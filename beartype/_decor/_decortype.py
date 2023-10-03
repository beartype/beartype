#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Unmemoized beartype type decorators** (i.e., low-level decorators decorating
classes on behalf of the parent :mod:`beartype._decor.decorcore` submodule).

This private submodule is effectively the :func:`beartype.beartype` decorator
despite *not* actually being that decorator (due to being unmemoized).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Insufficient. We also want to set a beartype-specific dunder attribute
#-- say, "__beartyped" -- on this class. Additionally, if this class has already
#been @beartyped, we want to detect that here and avoid re-@beartype-ing this
#class. In short, we want to generalize our existing
#"beartype._util.func.mod.utilbeartypefunc" submodule to support classes as
#well. Let's shift that submodule somewhere more general, please. Perhaps:
#* Rename "beartype._util.func.mod.utilbeartypefunc" to
#  "beartype._util.check.utilcheckfunc".
#* Define a new "beartype._util.check.utilchecktype" submodule containing
#  similar class-specific functionality.
#FIXME: Actually... *NO.* We absolutely do *NOT* want to monkey-patch random
#@beartype-specific attributes into user-defined classes, because then the
#Python ecosystem will shudder, then sway, then crack, and finally tumble into
#the churning seas below. Instead, let's find something *ELSE* that is actually
#safe to monkey-patch. Method objects are the classic example. Nobody cares if
#we monkey-patch those. The most common method object would be the
#"cls.__init__" object. Of course, many types do *NOT* define that object -- but
#many types also do. We could simply:
#* Decide whether the "cls.__init__" method exists.
#* Decide whether the "cls.__init__.__beartyped_cls" attribute exists. Note that
#  this attribute is distinct from our existing "__beartyped" attribute, when
#  records a lower-level and less useful truth.
#
#For example:
#    is_type_beartyped = getattr(
#        getattr(cls, '__init__', None), '__beartyped_cls', False)
#
#Pretty sure that suffices. It's just a simple two-liner. This is only an
#optimization, so it doesn't particularly matter if it fails to apply to some
#classes. So, let's a-go!
#FIXME: Actually, we *DO* now want to make this mandatory across all classes.
#This is no longer merely an optimization. We really do want to be able to
#reliably detect when a class has been previously @beartyped to avoid doing so
#again. Let's avoid monkey-patching __init__(), for reasons that will become
#clear shortly. Instead, let's monkey-patch the little-used and now-obsolete
#__reduce__() dunder method -- which has been obsoleted by the newer
#__reduce_ex__() dunder method. Specifically:
#* Inside beartype_type():
#  * Before doing anything, test whether the passed class has already been
#    beartyped as follows:
#        is_type_beartyped = getattr(
#            getattr(cls, '__reduce__', None), '__beartyped_cls', False)
#  * If so, silently reduce to a noop. Else, continue.
#  * Define a new type_reduce_wrapper() closure resembling:
#        def type_reduce_wrapper(self) -> Union[str, tuple]:
#            return cls_reduce_old(self)
#  * Unconditionally wrap the __reduce__() method of the passed class with a new
#    placeholder __reduce__() method monkey-patched with the "__beartyped_cls"
#    boolean: e.g.,
#        cls_reduce_old = cls.__reduce__
#        cls.__reduce__ = type_reduce_wrapper
#        cls.__reduce__.__beartyped_cls = True
#
#__reduce__() is optimal for several reasons:
#* Wrapping a method with another method reduces efficiency.
#* But pickling is already extremely inefficient. Ergo, the minor overhead
#  introduced by wrapping a pickling method with another pickling method is
#  negligible with respect to the major overhead of pickling itself.
#* Moreover, the __reduce__() method is obsolete and *ONLY* called as a fallback
#  when the modern __reduce_ex__() method is undefined.
#FIXME: Actually, let's avoid messing about with pickling methods. Notably, the
#official docs for __reduce_ex__() contain this concerning clause:
#     In addition, __reduce__() automatically becomes a synonym for the extended
#     version __reduce_ex__() [when __reduce_ex__() is defined].
#
#Instead, let's leverage the __sizeof__() dunder method. Nothing of
#mission-critical interest ever calls that method. It's basically only ever
#called by the sys.getsizeof() utility function, which itself is only ever
#called in a REPL or by third-party object sizer packages. In short, *PERFECT*!
#Specifically:
#* Inside beartype_type():
#  * Before doing anything, test whether the passed class has already been
#    beartyped as follows:
#        is_type_beartyped = getattr(
#            getattr(cls, '__sizeof__', None), '__beartyped_cls', False)
#  * If so, silently reduce to a noop. Else, continue.
#  * Define a new type_reduce_wrapper() closure resembling:
#        def type_sizeof_wrapper(self) -> int:
#            return cls_sizeof_old(self)
#  * Unconditionally wrap the __sizeof__() method of the passed class with a new
#    placeholder __sizeof__() method monkey-patched with the "__beartyped_cls"
#    boolean: e.g.,
#        cls_sizeof_old = cls.__sizeof__
#        cls.__sizeof__ = type_sizeof_wrapper
#        cls.__sizeof__.__beartyped_cls = True

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Dict,
    Set,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.convert.convcoerce import clear_coerce_hint_caches
from beartype._conf.confcls import BeartypeConf
from beartype._data.cls.datacls import TYPES_BEARTYPEABLE
from beartype._data.hint.datahinttyping import (
    BeartypeableT,
    TypeStack,
)
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
from collections import defaultdict

# ....................{ DECORATORS ~ type                  }....................
def beartype_type(
    # Mandatory parameters.
    cls: BeartypeableT,
    conf: BeartypeConf,

    # Optional parameters.
    cls_stack: TypeStack = None,
) -> BeartypeableT:
    '''
    Decorate the passed class with dynamically generated type-checking.

    Parameters
    ----------
    cls : BeartypeableT
        Class to be decorated by :func:`beartype.beartype`.
    conf : BeartypeConf
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this class.
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.

    Returns
    ----------
    BeartypeableT
        This class decorated by :func:`beartype.beartype`.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'
    assert isinstance(cls_stack, NoneTypeOr[tuple]), (
        f'{repr(cls_stack)} neither tuple nor "None".')
    # assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'
    # print(f'Decorating type {repr(obj)}...')

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._decor.decorcore import beartype_object

    # ....................{ LOCALS                         }....................
    # Fully-qualified name of the module defining this class if this class is
    # defined by a module *OR* "None" otherwise (e.g., if this class is only
    # dynamically defined in-memory outside of any module structure).
    module_name = get_object_module_name_or_none(cls)

    # If this class is defined by a module...
    if module_name:
        # Unqualified basename of this class.
        type_name = cls.__name__

        # Set of the unqualified basenames of *ALL* classes in that module
        # previously decorated by this decorator.
        type_names_beartyped = _BEARTYPED_MODULE_TO_TYPE_NAME[module_name]

        #FIXME: Protect against redecoration, please. That is, this condition
        #should *NOT* be triggered under this common edge case:
        #    @beartype
        #    @beartype  # <-- or "beartype.claw", which implicitly does this
        #    def muh_class(...): ...
        #
        #Doing so will require that we begin marking classes as decorated by
        #beartype. See commentary above, please.

        # If a class with the same unqualified basename defined in a module with
        # the same fully-qualified name has already been marked as decorated by
        # this decorator, then either:
        # * That module has been externally reloaded. In this case, this class
        #   (along with the remainder of that module) has now been redefined.
        #   Common examples include:
        #   * Rerunning a Jupyter cell defining this class.
        #   * Refreshing a web app enabling hot reloading (i.e., automatic
        #     reloading of on-disk modules whose contents have been externally
        #     modified *AFTER* that app was initially run). Since most Python
        #     web app frameworks (e.g., Flask, Streamlit) support hot reloading,
        #     this is the common case.
        # * That module has internally redefined this class two or more times.
        #   This behaviour, while typically a bug, is also technically valid:
        #   e.g.,
        #       @beartype
        #       def MuhClass(object): ...
        #       @beartype
        #       def MuhClass(object): ...   # <-- this makes me squint
        #
        # In this case, clear *ALL* beartype-specific internal caches that have
        # been shown to fail when a class is redefined.
        if type_name in type_names_beartyped:
            #FIXME: Consider emitting a logging message instead, please.
            # print(f'@beartyped class "{module_name}.{type_name}" redefined!')

            # Clear *ALL* type hint coercion caches, which map from the
            # machine-readable representations of previously seen
            # non-self-cached type hints (e.g., "list[MuhClass]") to the first
            # seen instance of those hints (e.g., list[MuhClass]). Since this
            # class has been redefined, the first seen instance of those hints
            # could contain a reference to the first definition of this class;
            # if so, there now exists a discrepancy between the current
            # definition of this class and cached hints containing the prior
            # definition of this class. For safety, all caches possibly
            # containing those hints must now be assumed to be invalid. Failing
            # to clear these caches causes @beartype-decorated wrapper functions
            # to raise erroneous type-checking violations. See also:
            #     https://github.com/beartype/beartype/issues/288
            clear_coerce_hint_caches()
        # Else, this is the first decoration of this class by this decorator.
        # In this case...
        else:
            #FIXME: Delay until *AFTER* successfully decorating this class.
            # Necord that this class has now been decorated by this decorator.
            type_names_beartyped.add(type_name)
    # Else, this class is *NOT* defined by a module.

    # Replace the passed class stack with a new class stack appending this
    # decorated class to the top of this stack, reflecting the fact that this
    # decorated class is now the most deeply lexically nested class for the
    # currently recursive chain of @beartype-decorated classes.
    cls_stack = (
        # If the caller passed *NO* class stack, then this class is necessarily
        # the first decorated class being decorated directly by @beartype and
        # thus the root decorated class.
        #
        # Note this is the common case and thus tested first. Since nested
        # classes effectively do *NOT* exist in the wild, this comprises
        # 99.999% of all real-world cases.
        (cls,)
        if cls_stack is None else
        # Else, the caller passed a clack stack comprising at least a root
        # decorated class. Preserve that class as is to properly expose that
        # class elsewhere.
        cls_stack + (cls,)
    )

    # ....................{ DECORATION                     }....................
    # For the unqualified name and value of each direct (i.e., *NOT* indirectly
    # inherited) attribute of this class...
    for attr_name, attr_value in cls.__dict__.items():  # pyright: ignore[reportGeneralTypeIssues]
        # If this attribute is beartypeable...
        if isinstance(attr_value, TYPES_BEARTYPEABLE):
            # This attribute decorated with type-checking configured by this
            # configuration if *NOT* already decorated.
            attr_value_beartyped = beartype_object(
                obj=attr_value,
                conf=conf,
                cls_stack=cls_stack,
            )

            # Attempt to...
            try:
                # Replace this undecorated attribute with this decorated
                # attribute.
                #
                # Note that class attributes are *ONLY* settable by calling the
                # tragically slow setattr() builtin. Attempting to directly set
                # an attribute on the class dictionary raises an exception. Why?
                # Because class dictionaries are actually low-level
                # "mappingproxy" objects that intentionally override the
                # __setattr__() dunder method to unconditionally raise an
                # exception. Why? Because that constraint enables the
                # type.__setattr__() dunder method to enforce critical
                # efficiency constraints on class attributes -- including that
                # class attribute keys are *NOT* only strings but also valid
                # Python identifiers:
                #     >>> class OhGodHelpUs(object): pass
                #     >>> OhGodHelpUs.__dict__['even_god_cannot_help'] = 2
                #     TypeError: 'mappingproxy' object does not support item
                #     assignment
                #
                # See also this relevant StackOverflow answer by Python luminary
                # Raymond Hettinger:
                #     https://stackoverflow.com/a/32720603/2809027
                setattr(cls, attr_name, attr_value_beartyped)
            # If doing so raises a builtin "TypeError"...
            except TypeError as exception:
                #FIXME: Shift this detection logic into a new
                #is_typeerror_attr_immutable() tester, please.

                # Message raised with this "TypeError".
                exception_message = str(exception)

                # If this message satisfies a pattern , then this "TypeError" signifies this attribute
                # to be inherited from an immutable builtin type (e.g., "str")
                # subclassed by this user-defined subclass. In this case,
                # silently skip past this uncheckable attribute to the next.
                #
                # Note that this pattern depends on the current Python version.
                if (
                    # The active Python interpreter targets Python >= 3.10,
                    # match a message of the form "cannot set '{attr_name}'
                    # attribute of immutable type '{cls_name}'".
                    IS_PYTHON_AT_LEAST_3_10 and (
                        exception_message.startswith("cannot set '") and
                        "' attribute of immutable type " in exception_message
                    # Else, the active Python interpreter targets Python <= 3.9.
                    # In this case, match a message of the form "can't set
                    # attributes of built-in/extension type '{cls_name}'".
                    ) or exception_message.startswith(
                        "can't set attributes of built-in/extension type '")
                ):
                    continue
                # Else, this message does *NOT* satisfy that pattern.

                # Preserve this exception by re-raising this exception.
                raise
        # Else, this attribute is *NOT* beartypeable. In this case, silently
        # ignore this attribute.

    # Return this class as is.
    return cls  # type: ignore[return-value]

# ....................{ PRIVATE ~ globals                  }....................
_BEARTYPED_MODULE_TO_TYPE_NAME: Dict[str, Set[str]] = defaultdict(set)
'''
**Decorated classname registry (i.e., dictionary mapping from the
fully-qualified name of each module defining one or more classes decorated by
the :func:`beartype.beartype` decorator to the set of the unqualified basenames
of all classes in that module decorated by that decorator).
'''
