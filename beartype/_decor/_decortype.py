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
from functools import wraps

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

    # ....................{ NOOP                           }....................
    # Original C-based __sizeof__() dunder method defined by this class, which
    # this decorator subsequently wraps with a pure-Python __sizeof__() dunder
    # method. Why? Tangential reasons that are obscure, profane, and have
    # absolutely *NOTHING* to do with the __sizeof__() dunder method itself.
    # Succinctly, @beartype needs a reasonably safe place to persist
    # @beartype-specific attributes pertaining to this class.
    #
    # Clearly, the obvious place would be this class itself. However, doing so
    # would fundamentally modify this class and thus *ALL* instances of this
    # class in an unexpected and thus possibly unsafe manner. Consider common
    # use cases like slots, introspection, pickling, and sizing. Clearly,
    # monkey-patching attributes into class dictionaries without the explicit
    # consent of class designers is an ill-advised approach.
    #
    # A less obvious but safer place is required. A method of this class would
    # be the ideal candidate; whereas everybody cares about object attributes
    # and thus class dictionaries, nobody cares about method attributes. This is
    # why @beartype safely monkey-patches attributes into @beartype-decorated
    # methods. However, which method? Most methods are *NOT* guaranteed to exist
    # across all possible classes. Adding a new method to this class would be no
    # better than adding a new attribute to this class; both modify class
    # dictionaries. Fortunately, Python currently guarantees *ALL* classes to
    # define at least 24 dunder methods as of Python 3.11. How? Via the root
    # "object" superclass. Unfortunately, *ALL* of these methods are C-based and
    # thus do *NOT* directly support monkey-patching: e.g.,
    #     >>> class AhMahGoddess(object): pass
    #     >>> AhMahGoddess.__init__.__beartyped_cls = True
    #     AttributeError: 'wrapper_descriptor' object has no attribute
    #     '__beartyped_cls'
    #
    # Fortunately, *ALL* of these methods may be wrapped by pure-Python
    # equivalents whose implementations defer to their original C-based methods.
    # Unfortunately, doing so slightly reduces the efficiency of calling these
    # methods. Fortunately, a subset of these methods are rarely called under
    # production workloads; slightly reducing the efficiency of calling these
    # methods is irrelevant to almost all use cases. Of these, the most obscure,
    # largely useless, poorly documented, and single-use is the __sizeof__()
    # dunder method -- which is only ever called by the sys.getsizeof() utility
    # function, which itself is only ever called manually in a REPL or by
    # third-party object sizing packages. In short, __sizeof__() is perfect.
    cls_sizeof_old = cls.__sizeof__

    # True only if this decorator has already decorated this class, as indicated
    # by the @beartype-specific instance variable "__beartyped_cls"
    # monkey-patched into a pure-Python __sizeof__() dunder method wrapper by a
    # prior call to this decorator passed this class.
    is_cls_beartyped = getattr(cls_sizeof_old, '__beartyped_cls', False)

    # If this decorator has already decorated this class, silently reduce to a
    # noop by returning this class as is.
    if is_cls_beartyped:
        # print(f'Ignoring repeat decoration of {repr(cls)}...')
        return cls  # type: ignore[return-value]
    # Else, this decorator has yet to decorate this class.

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
            #FIXME: Consider emitting a logging message instead if this branch
            #ever becomes computationally intensive, please.
            # print(f'@beartyped class "{module_name}.{type_name}" redefined!')

            # Clear the previously accessed set of the unqualified basenames of
            # *ALL* classes in that module previously decorated by this
            # decorator. Technically, this is optional. Pragmatically, this
            # *SHOULD* significantly improve the space and time constraints
            # associated with this class redefinition. Why? Because this class
            # being redefined implies that the module defining this class is
            # being redefined, which implies that all classes in that module are
            # being redefined as well. If we did *NOT* clear this set here, then
            # this set would continue to contain the unqualified basenames of
            # those other classes in that module; each @beartype-decorated
            # redefinition of those other classes would then unnecessarily clear
            # the same caches already cleared by the first @beartype-decorated
            # redefinition of a class in that module. Since doing so would be
            # overly aggressive and thus inefficient, avoiding doing so improves
            # efficiency in the common case of module redefinition.
            _BEARTYPED_MODULE_TO_TYPE_NAME.clear()

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
            # Record that this class has now been decorated by this decorator.
            # Technically, this should (probably) be performed *AFTER* this
            # decorator has actually successfully decorated this class.
            # Pragmatically, doing so here is simply faster and... simpler.
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

            # Replace this undecorated attribute with this decorated attribute.
            _set_type_attr(cls, attr_name, attr_value_beartyped)
        # Else, this attribute is *NOT* beartypeable. In this case, silently
        # ignore this attribute.

    # ....................{ MONKEY-PATCH                   }....................
    # Pure-Python __sizeof__() dunder method wrapping the original C-based
    # __sizeof__() dunder method declared by this class.
    @wraps(cls_sizeof_old)
    def cls_sizeof_new(self) -> int:
        return cls_sizeof_old(self)  # type: ignore[call-arg]

    # Monkey-patch a @beartype-specific instance variable into this wrapper,
    # recording that this decorator has now decorated this class. For safety,
    # leverage our high-level _set_type_attr() setter rather than attempting to
    # set this low-level attribute directly. Although doing so efficiently
    # succeeds for standard mutable classes, doing so fails catastrophically
    # for edge-case immutable classes (e.g., "enum.Enum" subclasses).
    cls_sizeof_new.__beartyped_cls = True  # type: ignore[attr-defined]

    # Replace the original C-based __sizeof__() dunder method with this wrapper.
    _set_type_attr(cls, '__sizeof__', cls_sizeof_new)

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

# ....................{ PRIVATE ~ setters                  }....................
def _set_type_attr(cls: type, attr_name: str, attr_value: object) -> None:
    '''
    Dynamically set the class attribute with the passed name to the passed value
    on the dictionary of the passed class.

    Parameters
    ----------
    cls : type
        Class to set this attribute on.
    attr_name : str
        Name of the class attribute to be set.
    attr_value : object
        Value to set this class attribute to.

    Caveats
    -------
    **This function is unavoidably slow.** Class attributes are *only* settable
    by calling the tragically slow :func:`setattr` builtin. Attempting to
    directly set an attribute on the class dictionary raises an exception. Why?
    Because class dictionaries are actually low-level :class:`mappingproxy`
    objects that intentionally override the ``__setattr__()`` dunder method to
    unconditionally raise an exception. Why? Because that constraint enables the
    :meth:`type.__setattr__` dunder method to enforce critical efficiency
    constraints on class attributes -- including that class attribute keys are
    *not* only strings but also valid Python identifiers:

    .. code-block:: pycon

       >>> class OhGodHelpUs(object): pass
       >>> OhGodHelpUs.__dict__['even_god_cannot_help'] = 2
       TypeError: 'mappingproxy' object does not support item
       assignment

    See also this `relevant StackOverflow answer by Python luminary
    Raymond Hettinger <answer_>`__.

    .. _answer:
       https://stackoverflow.com/a/32720603/2809027
    '''

    # Attempt to set the class attribute with this name to this value.
    try:
        setattr(cls, attr_name, attr_value)
    # If doing so raises a builtin "TypeError"...
    except TypeError as exception:
        # Message raised with this "TypeError".
        exception_message = str(exception)

        # If this message satisfies a well-known pattern unique to the current
        # Python version, then this exception signifies this attribute to be
        # inherited from an immutable builtin type (e.g., "str") subclassed by
        # this user-defined subclass. In this case, silently skip past this
        # uncheckable attribute to the next.
        if (
            # The active Python interpreter targets Python >= 3.10, match a
            # message of the form "cannot set '{attr_name}' attribute of
            # immutable type '{cls_name}'".
            IS_PYTHON_AT_LEAST_3_10 and (
                exception_message.startswith("cannot set '") and
                "' attribute of immutable type " in exception_message
            # Else, the active Python interpreter targets Python <= 3.9. In this
                # case, match a message of the form "can't set attributes of
                # built-in/extension type '{cls_name}'".
            ) or exception_message.startswith(
                "can't set attributes of built-in/extension type '")
        ):
            return
        # Else, this message does *NOT* satisfy that pattern.

        # Preserve this exception by re-raising this exception.
        raise
