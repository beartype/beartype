#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Unmemoized beartype decorator.**

This private submodule defines all core high-level logic underlying the
:func:`beartype.beartype` decorator, whose implementation in the parent
:mod:`beartype._decor._cache.cachedecor` submodule is a thin wrapper
efficiently memoizing closures internally created and returned by that
decorator. In turn, those closures directly defer to this submodule.

This private submodule is effectively the :func:`beartype.beartype` decorator
despite *not* actually being that decorator (due to being unmemoized).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeException,
    BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException,
    # BeartypeWarning,
)
from beartype._cave._cavefast import (
    # MethodBoundInstanceOrClassType,
    MethodDecoratorBuiltinTypes,
    MethodDecoratorClassType,
    MethodDecoratorPropertyType,
    MethodDecoratorStaticType,
    # MethodDescriptorTypes,
)
from beartype._data.datatyping import (
    BeartypeableT,
    TypeWarning,
)
from beartype._conf import BeartypeConf
from beartype._decor._code.codemain import generate_code
from beartype._decor._decorcall import BeartypeCall
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed,
    release_object_typed,
)
from beartype._util.cls.pep.utilpep557 import is_type_pep557
from beartype._util.func.lib.utilbeartypefunc import (
    is_func_unbeartypeable,
    set_func_beartyped,
)
from beartype._util.func.utilfuncmake import make_func
from beartype._util.mod.utilmodget import get_object_module_line_number_begin
from beartype._util.utilobject import get_object_name
from traceback import format_exc
from warnings import warn

# ....................{ DECORATORS                         }....................
def beartype_object(
    obj: BeartypeableT, conf: BeartypeConf) -> BeartypeableT:
    '''
    Decorate the passed **beartypeable** (i.e., pure-Python callable or class)
    with optimal type-checking dynamically generated unique to that
    beartypeable.

    Parameters
    ----------
    obj : BeartypeableT
        **Beartypeable** (i.e., pure-Python callable or class) to be decorated.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable or class).

    Returns
    ----------
    BeartypeableT
        Either:

        * If the passed object is a class, this existing class embellished with
          dynamically generated type-checking.
        * If the passed object is a callable, a new callable wrapping that
          callable with dynamically generated type-checking.

    See Also
    ----------
    :func:`beartype._decor.decormain.beartype`
        Memoized parent decorator wrapping this unmemoized child decorator.
    '''

    # If this object is a class, return this class decorated with type-checking.
    if isinstance(obj, type):
        #FIXME: Mypy currently erroneously emits a false negative resembling
        #the following if the "# type: ignore..." pragma is omitted below:
        #    beartype/_decor/main.py:246: error: Incompatible return value type
        #    (got "type", expected "BeartypeableT")  [return-value]
        #This is almost certainly a mypy issue, as _beartype_type() is
        #explicitly annotated as both accepting and returning "BeartypeableT".
        #Until upstream resolves this, we squelch mypy with regret in our
        #hearts.
        return _beartype_type(cls=obj, conf=conf)  # type: ignore[return-value]
    # Else, this object is a non-class.

    # Type of this object.
    obj_type = type(obj)

    # If this object is an uncallable builtin method descriptor (i.e., either a
    # property, class method, instance method, or static method object),
    # @beartype was listed above rather than below the builtin decorator
    # generating this descriptor in the chain of decorators decorating this
    # decorated callable. Although @beartype typically *MUST* decorate a
    # callable directly, this edge case is sufficiently common *AND* trivial to
    # resolve to warrant doing so. To do so, this conditional branch effectively
    # reorders @beartype to be the first decorator decorating the pure-Python
    # function underlying this method descriptor: e.g.,
    #
    #     # This branch detects and reorders this edge case...
    #     class MuhClass(object):
    #         @beartype
    #         @classmethod
    #         def muh_classmethod(cls) -> None: pass
    #
    #     # ...to resemble this direct decoration instead.
    #     class MuhClass(object):
    #         @classmethod
    #         @beartype
    #         def muh_classmethod(cls) -> None: pass
    #
    # Note that most but *NOT* all of these objects are uncallable. Regardless,
    # *ALL* of these objects are unsuitable for direct decoration. Specifically:
    # * Under Python < 3.10, *ALL* of these objects are uncallable.
    # * Under Python >= 3.10:
    #   * Descriptors created by @classmethod and @property are uncallable.
    #   * Descriptors created by @staticmethod are technically callable but
    #     C-based and thus unsuitable for decoration.
    if obj_type in MethodDecoratorBuiltinTypes:
        return _beartype_descriptor(descriptor=obj, conf=conf)
    # Else, this object is *NOT* an uncallable builtin method descriptor.
    #
    # If this object is uncallable, raise an exception.
    elif not callable(obj):
        # Raise an exception.
        raise BeartypeDecorWrappeeException(
            f'Uncallable {repr(obj)} not decoratable by @beartype.')
    # Else, this object is callable.

    # Return a new callable decorating that callable with type-checking.
    return _beartype_func(func=obj, conf=conf)  # type: ignore[return-value]


#FIXME: Unit test us up, please.
def beartype_object_nonfatal(
    obj: BeartypeableT,
    conf: BeartypeConf,
    warning_category: TypeWarning,
) -> BeartypeableT:
    '''
    Decorate the passed **beartypeable** (i.e., pure-Python callable or class)
    with optimal type-checking dynamically generated unique to that
    beartypeable and any otherwise uncaught exception raised by doing so safely
    coerced into a warning instead.

    Motivation
    ----------
    This decorator is principally intended to be called by our **all-at-once
    API** (i.e., the import hooks defined by the :mod:`beartype.claw`
    subpackage). Raising detailed exception tracebacks on unexpected error
    conditions is:

    * The right thing to do for callables and classes manually type-checked with
      the :func:`beartype.beartype` decorator.
    * The wrong thing to do for callables and classes automatically type-checked
      by import hooks installed by public functions exported by the
      :mod:`beartype.claw` subpackage. Why? Because doing so would render those
      import hooks fragile to the point of being practically useless on
      real-world packages and codebases by unexpectedly failing on the first
      callable or class defined *anywhere* under a package that is not
      type-checkable by :func:`beartype.beartype` (whether through our fault or
      that package's). Instead, the right thing to do is to:

      * Emit a warning for each callable or class that :func:`beartype.beartype`
        fails to generate a type-checking wrapper for.
      * Proceed to the next callable or class.

    Parameters
    ----------
    obj : BeartypeableT
        **Beartypeable** (i.e., pure-Python callable or class) to be decorated.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable or class).
    warning_category : TypeWarning
        Category of the non-fatal warning to emit if :func:`beartype.beartype`
        fails to generate a type-checking wrapper for this callable or class.

    Returns
    ----------
    BeartypeableT
        Either:

        * If the passed object is a class, this existing class embellished with
          dynamically generated type-checking.
        * If the passed object is a callable, a new callable wrapping that
          callable with dynamically generated type-checking.

    Warns
    ----------
    warning_category
        If :func:`beartype.beartype` fails to generate a type-checking wrapper
        for this callable or class by raising a fatal exception, this function
        coerces that exception into a non-fatal warning describing that error.

    See Also
    ----------
    :func:`beartype._decor.decormain.beartype`
        Memoized parent decorator wrapping this unmemoized child decorator.
    '''

    # Attempt to decorate the passed beartypeable.
    try:
        return beartype_object(obj, conf)
    # If doing so unexpectedly raises an exception, coerce that fatal exception
    # into a non-fatal warning for nebulous safety.
    except Exception as exception:
        assert isinstance(warning_category, Warning), (
            f'{repr(warning_category)} not warning category.')

        # Original error message to be embedded in the warning message to be
        # emitted, defined as either...
        error_message = (
            # If this exception is beartype-specific, this exception's message
            # is probably human-readable as is. In this case, coerce only that
            # message directly into a warning for brevity and readability.
            str(exception)
            if isinstance(exception, BeartypeException) else
            # Else, this exception is *NOT* beartype-specific. In this case,
            # this exception's message is probably *NOT* human-readable as is.
            # Prepend that non-human-readable message by this exception's
            # traceback to for disambiguity and debuggability. Note that the
            # format_exc() function appends this exception's message to this
            # traceback and thus suffices as is.
            format_exc()
        )

        #FIXME: Unconditionally parse this warning message by globally replacing
        #*EACH* newline (i.e., "\n" substring) in this message with a newline
        #followed by four spaces (i.e., "\n    ").

        #FIXME: Inadequate, really. Instead defer to the:
        #* "label_callable(func=obj, is_contextualized=True)" function if this
        #  object is *NOT* a class.
        #* "label_class(cls=obj, is_contextualized=True)" function if this
        #  object is a class. Of course, that function currently accepts no such
        #  "is_contextualized" parameter. Make it so, please. *sigh*
        #
        #This suggests we probably just want to define a new higher-level
        #label_object() function with signature resembling:
        #    label_object(obj: object, is_contextualized: Optional[bool] = None)
        #FIXME: Note that we'll want to capitalize the first character of the
        #string returned by the label_object() function, please.

        # Fully-qualified name of this beartypeable.
        obj_name = get_object_name(obj)

        # Line number of the first line declaring this beartypeable in its
        # underlying source code module file.
        obj_lineno = get_object_module_line_number_begin(obj)

        # Warning message to be emitted.
        warning_message = (
            error_message
        )

        # Emit this message under this category.
        warn(warning_message, warning_category)

    # Return this object unmodified, as @beartype failed to successfully wrap
    # this object with a type-checking class or callable. So it goes, fam.
    return obj

# ....................{ PRIVATE ~ beartypers : func        }....................
def _beartype_descriptor(
    descriptor: BeartypeableT, conf: BeartypeConf) -> BeartypeableT:
    '''
    Decorate the passed C-based unbound method descriptor with dynamically
    generated type-checking.

    Parameters
    ----------
    descriptor : BeartypeableT
        Descriptor to be decorated by :func:`beartype.beartype`.
    conf : BeartypeConf
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this descriptor.

    Returns
    ----------
    BeartypeableT
        New pure-Python callable wrapping this descriptor with type-checking.
    '''
    assert isinstance(descriptor, MethodDecoratorBuiltinTypes), (
        f'{repr(descriptor)} not builtin method descriptor.')
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    # Type of this descriptor.
    descriptor_type = type(descriptor)

    # If this descriptor is a property method...
    #
    # Note that property method descriptors are intentionally tested next, due
    # to their ubiquity "in the wild." Class and static method descriptors are
    # comparatively rarefied by comparison.
    if descriptor_type is MethodDecoratorPropertyType:
        # Pure-Python unbound getter, setter, and deleter functions wrapped by
        # this descriptor if any *OR* "None" otherwise (i.e., for each such
        # function currently unwrapped by this descriptor).
        descriptor_getter  = descriptor.fget  # type: ignore[union-attr]
        descriptor_setter  = descriptor.fset  # type: ignore[union-attr]
        descriptor_deleter = descriptor.fdel  # type: ignore[union-attr]

        # Decorate this getter function with type-checking.
        #
        # Note that *ALL* property method descriptors wrap at least a getter
        # function (but *NOT* necessarily a setter or deleter function). This
        # function is thus guaranteed to be non-"None".
        descriptor_getter = _beartype_func(func=descriptor_getter, conf=conf)  # type: ignore[type-var]

        # If this property method descriptor additionally wraps a setter and/or
        # deleter function, type-check those functions as well.
        if descriptor_setter is not None:
            descriptor_setter = _beartype_func(
                func=descriptor_setter, conf=conf)
        if descriptor_deleter is not None:
            descriptor_deleter = _beartype_func(
                func=descriptor_deleter, conf=conf)

        # Return a new property method descriptor decorating all of these
        # functions, implicitly destroying the prior descriptor.
        #
        # Note that the "property" class interestingly has this signature:
        #     class property(fget=None, fset=None, fdel=None, doc=None): ...
        return property(  # type: ignore[return-value]
            fget=descriptor_getter,
            fset=descriptor_setter,
            fdel=descriptor_deleter,
            doc=descriptor.__doc__,
        )
    # Else, this descriptor is *NOT* a property method.
    #
    # If this descriptor is a class method...
    elif descriptor_type is MethodDecoratorClassType:
        # Return a new class method descriptor decorating the pure-Python
        # unbound function wrapped by this descriptor with type-checking,
        # implicitly destroying the prior descriptor.
        return classmethod(_beartype_func(func=descriptor.__func__, conf=conf))  # type: ignore[return-value,union-attr]
    # Else, this descriptor is *NOT* a class method.
    #
    # If this descriptor is a static method...
    elif descriptor_type is MethodDecoratorStaticType:
        # Return a new static method descriptor decorating the pure-Python
        # unbound function wrapped by this descriptor with type-checking,
        # implicitly destroying the prior descriptor.
        return staticmethod(_beartype_func(func=descriptor.__func__, conf=conf))  # type: ignore[return-value,union-attr]
    # Else, this descriptor is *NOT* a static method.

    #FIXME: Unconvinced this edge case is required or desired. Does @beartype
    #actually need to decorate instance method descriptors? Nonetheless, this
    #is sufficiently useful to warrant preservation... probably.
    #FIXME: Unit test us up, please.
    # # If this descriptor is an instance method...
    # #
    # # Note that instance method descriptors are intentionally tested first, as
    # # most methods are instance methods.
    # if descriptor_type is MethodBoundInstanceOrClassType:
    #     # Pure-Python unbound function decorating the similarly pure-Python
    #     # unbound function wrapped by this descriptor with type-checking.
    #     descriptor_func = _beartype_func(func=descriptor.__func__, conf=conf)
    #
    #     # New instance method descriptor rebinding this function to the
    #     # instance of the class bound to the prior descriptor.
    #     descriptor_new = MethodBoundInstanceOrClassType(
    #         descriptor_func, descriptor.__self__)  # type: ignore[return-value]
    #
    #     # Propagate the docstring from the prior to new descriptor.
    #     descriptor_new.__doc__ = descriptor.__doc__
    #
    #     # Return this new descriptor, implicitly destroying the prior
    #     # descriptor.
    #     return descriptor_new
    # Else, this descriptor is *NOT* an instance method.

    # Raise a fallback exception. This should *NEVER happen. This *WILL* happen.
    raise BeartypeDecorWrappeeException(
        f'Builtin method descriptor {repr(descriptor)} '
        f'not decoratable by @beartype '
        f'(i.e., neither property, class method, nor static method descriptor).'
    )


def _beartype_func(func: BeartypeableT, conf: BeartypeConf) -> BeartypeableT:
    '''
    Decorate the passed callable with dynamically generated type-checking.

    Parameters
    ----------
    func : BeartypeableT
        Callable to be decorated by :func:`beartype.beartype`.
    conf : BeartypeConf
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this callable.

    Returns
    ----------
    BeartypeableT
        New pure-Python callable wrapping this callable with type-checking.
    '''
    assert callable(func), f'{repr(func)} uncallable.'
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    # If that callable is unbeartypeable (i.e., if this decorator should
    # preserve that callable as is rather than wrap that callable with
    # constant-time type-checking), silently reduce to the identity decorator.
    if is_func_unbeartypeable(func):
        return func  # type: ignore[return-value]
    # Else, that callable is beartypeable. Let's do this, folks.

    #FIXME: Uncomment to display all annotations in "pytest" tracebacks.
    # func_hints = func.__annotations__

    # Previously cached callable metadata reinitialized from this callable.
    func_data = acquire_object_typed(BeartypeCall)
    func_data.reinit(func, conf)

    # Generate the raw string of Python statements implementing this wrapper.
    func_wrapper_code = generate_code(func_data)

    # If this callable requires *NO* type-checking, silently reduce to a noop
    # and thus the identity decorator by returning this callable as is.
    if not func_wrapper_code:
        return func  # type: ignore[return-value]

    # Function wrapping this callable with type-checking to be returned.
    #
    # For efficiency, this wrapper accesses *ONLY* local rather than global
    # attributes. The latter incur a minor performance penalty, since local
    # attributes take precedence over global attributes, implying all global
    # attributes are *ALWAYS* first looked up as local attributes before falling
    # back to being looked up as global attributes.
    func_wrapper = make_func(
        func_name=func_data.func_wrapper_name,
        func_code=func_wrapper_code,
        func_locals=func_data.func_wrapper_locals,
        func_label=f'@beartyped {func.__name__}() wrapper',
        func_wrapped=func,
        is_debug=conf.is_debug,
        exception_cls=BeartypeDecorWrapperException,
    )

    # Declare this wrapper to be generated by @beartype, which tests for the
    # existence of this attribute above to avoid re-decorating callables
    # already decorated by @beartype by efficiently reducing to a noop.
    set_func_beartyped(func_wrapper)

    # Release this callable metadata back to its object pool.
    release_object_typed(func_data)

    # Return this wrapper.
    return func_wrapper  # type: ignore[return-value]

# ....................{ PRIVATE ~ beartypers : type        }....................
def _beartype_type(cls: BeartypeableT, conf: BeartypeConf) -> BeartypeableT:
    '''
    Decorate the passed class with dynamically generated type-checking.

    Parameters
    ----------
    cls : BeartypeableT
        Class to be decorated by :func:`beartype.beartype`.
    conf : BeartypeConf
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this class.

    Returns
    ----------
    BeartypeableT
        This class decorated by :func:`beartype.beartype`.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    #FIXME: *REMOVE THIS CONDITIONAL* after implementing full-blown support for
    #class decoration, please.
    #FIXME: Unit test us up, please.
    # If this class is a dataclass...
    if is_type_pep557(cls):  # type: ignore[arg-type]
        # Wrap the implicit __init__() method generated by the @dataclass
        # decorator with a wrapper function type-checking all dataclass fields
        # annotated by PEP-compliant type hints implicitly passed as parameters
        # of the same name to this method by that decorator. Phew!
        cls.__init__ = _beartype_func(  # type: ignore[misc]
            func=cls.__init__, conf=conf)  # type: ignore[misc]
        return cls  # type: ignore[return-value]

    #FIXME: Generalize to support non-dataclass classes, please.
    # Else, this class is *NOT* a dataclass. In this case, raise an
    # exception.
    raise BeartypeDecorWrappeeException(
        f'{repr(cls)} not decoratable by @beartype, as '
        f'non-dataclasses (i.e., types not decorated by '
        f'@dataclasses.dataclass) currently unsupported by @beartype.'
    )
