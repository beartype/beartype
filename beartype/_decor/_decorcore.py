#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
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

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException,
)
from beartype._data.cls.datacls import (
    TYPES_BUILTIN_DECORATOR_DESCRIPTOR_FACTORY)
from beartype._data.datatyping import BeartypeableT
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

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ DECORATORS                        }....................
def beartype_args_mandatory(
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

    # Validate the type of the decorated object *BEFORE* performing any work
    # assuming this object to define attributes (e.g., "func.__name__").
    #
    # If this object is an unusable descriptor created by a builtin type
    # masquerading as a decorator (e.g., @property), @beartype was erroneously
    # listed above rather than below this decorator in the chain of decorators
    # decorating an underlying callable. @beartype typically *MUST* decorate a
    # callable directly. In this case, raise a human-readable exception
    # instructing the end user to reverse the order of decoration.
    #
    # Note that most but *NOT* all of these objects are uncallable. Regardless,
    # *ALL* of these objects are unsuitable for decoration. Specifically:
    # * Under Python < 3.10, *ALL* of these objects are uncallable.
    # * Under Python >= 3.10:
    #   * Descriptors created by @classmethod and @property are uncallable.
    #   * Descriptors created by @staticmethod are technically callable but
    #     C-based and thus unsuitable for decoration.
    if isinstance(obj, TYPES_BUILTIN_DECORATOR_DESCRIPTOR_FACTORY):
        # Human-readable name of this type masquerading as a decorator.
        DECORATOR_NAME = f'@{obj.__class__.__name__}'

        # Raise an exception embedding this name.
        raise BeartypeDecorWrappeeException(
            f'Uncallable descriptor created by builtin decorator '
            f'{DECORATOR_NAME} not decoratable by @beartype. '
            f'Consider listing @beartype below rather than above '
            f'{DECORATOR_NAME} in the decorator chain for this method: '
            f'e.g.,\n'
            f'\t{DECORATOR_NAME}\n'
            f'\t@beartype      # <-- this is the Way of the Bear\n'
            f'\tdef ...'
        )
    # Else, this is object is *NOT* such an unusable descriptor.
    #
    # If this object is a class, return this class decorated with
    # type-checking.
    elif isinstance(obj, type):
        #FIXME: Mypy currently erroneously emits a false negative resembling
        #the following if the "# type: ignore..." pragma is omitted below:
        #    beartype/_decor/main.py:246: error: Incompatible return value type
        #    (got "type", expected "BeartypeableT")  [return-value]
        #This is almost certainly a mypy issue, as _beartype_type() is
        #explicitly annotated as both accepting and returning "BeartypeableT". Until
        #upstream resolves this, we squelch mypy with regret in our hearts.
        return _beartype_type(cls=obj, conf=conf)  # type: ignore[return-value]
    # Else, this object is a non-class.
    #
    # If this object is uncallable, raise an exception.
    elif not callable(obj):
        raise BeartypeDecorWrappeeException(
            f'Uncallable {repr(obj)} not decoratable by @beartype.')
    # Else, this object is callable.
    #
    # If that callable is unbeartypeable (i.e., if this decorator should
    # preserve that callable as is rather than wrap that callable with
    # constant-time type-checking), silently reduce to the identity decorator.
    elif is_func_unbeartypeable(obj):
        return obj
    # Else, that callable is beartypeable. Let's do this, folks.

    # Return a new callable decorating that callable with type-checking.
    return _beartype_func(func=obj, conf=conf)

# ....................{ PRIVATE ~ beartypers              }....................
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
        return func

    # Function wrapping this callable with type-checking to be returned.
    #
    # For efficiency, this wrapper accesses *ONLY* local rather than global
    # attributes. The latter incur a minor performance penalty, since local
    # attributes take precedence over global attributes, implying all global
    # attributes are *ALWAYS* first looked up as local attributes before
    # falling back to being looked up as global attributes.
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
