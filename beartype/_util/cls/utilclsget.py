#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class getters** (i.e., low-level callables introspecting
general-purpose properties of arbitrary classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
# from beartype.roar._roarexc import _BeartypeUtilTypeException
from beartype._data.typing.datatyping import (
    LexicalScope,
    # TypeException,
)
from beartype._util.kind.maplike.utilmapfrozen import FrozenDict
# from beartype._util.cache.func.utilcachefunc import callable_cached
from typing import Optional

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up.
def get_type_filename_or_none(cls: type) -> Optional[str]:
    '''
    Absolute filename of the file on the local filesystem containing the
    pure-Python source code for the script or module defining the passed class
    if that class is defined on-disk *or* :data:`None` otherwise (i.e., if that
    class is dynamically defined in-memory by a prior call to the :func:`exec`
    or :func:`eval` builtins).

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    -------
    Optional[str]
        Either:

        * If this class was physically declared by a file, the absolute filename
          of that file.
        * If this class was dynamically declared in-memory, :data:`None`.
    '''

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodget import (
        get_module_filename_or_none,
        get_object_module_name_or_none,
    )
    from beartype._util.module.utilmodget import get_module_imported_or_none

    # Fully-qualified name of the module declaring this type if any *OR* "None".
    #
    # Note that *ALL* types should be declared by *SOME* modules. Nonetheless,
    # this is Python. It's best to assume the worst.
    type_module_name = get_object_module_name_or_none(cls)

    # If a module declares this type...
    if type_module_name:
        # This module if previously imported *OR* "None".
        #
        # Note that this module *SHOULD* necessarily already have been imported,
        # as this type obviously exists. Nonetheless, this module will be
        # unimportable for types dynamically declared in-memory rather than
        # on-disk, in which case the name of this module will have been a lie.
        type_module = get_module_imported_or_none(type_module_name)

        # If this module was previously imported...
        if type_module:
            # Return the filename defining this module if any *OR* "None".
            return get_module_filename_or_none(type_module)
    # Else, *NO* modules defines this type.

    # If all else fails, this type was probably declared in-memory rather than
    # on-disk. In this case, fallback to merely returning "None".
    return None

# ....................{ GETTERS ~ scope                    }....................
#FIXME: Define a new get_type_globals() getter with a similar one-liner to that
#suggested by PEP 563 (lol):
#      cls_globals = vars(sys.modules[cls_stack[-1].__module__])
#
#Of course, note that "__module__" may be either "None" *OR* an imaginary
#in-memory string that has no relation to "sys.modules". Care is thus warranted.

#FIXME: Unit test us up, please.
#FIXME: Memoize this getter. Doing so, however, could prove non-trivial. It's
#unsafe to memoize an arbitrarily large number of decorated classes. Ergo, we
#instead want to:
#* Define a new @callable_cached_lru decorator bounding the number of memoized
#  entries to some sane threshold.
#* Decorator this getter by that decorator. *sigh*
# @callable_cached_lru
def get_type_locals(cls: type) -> LexicalScope:
    '''
    **Local scope** (i.e., dictionary mapping from the name to value of each
    attribute directly declared by that class) for the passed class.

    Design
    ------
    This getter currently reduces to a (mostly) trivial one-liner returning
    ``cls.__dict__`` and has thus been defined mostly just for orthogonality
    with the comparable
    :func:`beartype._util.func.utilfuncscope.find_func_locals_frame` getter.
    That said, :pep:`563` suggests this non-trivial heuristic for computing the
    local scope of a given class:

        For classes, localns can be composed by chaining vars of the given class
        and its base classes (in the method resolution order). Since slots can
        only be filled after the class was defined, we don’t need to consult
        them for this purpose.

    We fail to grok that suggestion, because we lack a galactic brain. A
    minimal-length example (MLE) refutes all of the above by demonstrating that
    superclass attributes are *not* local to subclasses:

    .. code-block:: pycon

       >>> class Superclass(object):
       ...     my_int = int
       >>> class Subclass(Superclass):
       ...     def get_str(self) -> my_int:
       ...         return 'Oh, Gods.'
       NameError: name 'my_int' is not defined

    We are almost certainly confused about what :pep:`563` is talking about, but
    we are almost certain that :pep:`536` is also confused about what :pep:`563`
    is talking about. That said, the standard :func:`typing.get_type_hints`
    getter implements that suggestion with iteration over the method-resolution
    order (MRO) of the passed class resembling:

    .. code-block:: python

       for base in reversed(obj.__mro__):
           ...
           base_locals = dict(vars(base)) if localns is None else localns

    The standard :func:`typing.get_type_hints` getter appears to recursively
    retrieve all type hints annotating both the passed class and all
    superclasses of that class. Why? We have no idea, frankly. We're unconvinced
    that is useful in practice. We prefer a trivial one-liner, which behaves
    exactly as advertised and efficiently at decoration-time.

    Caveats
    -------
    **This getter returns an immutable rather than mutable mapping.** Callers
    requiring the latter are encouraged to manually coerce the immutable mapping
    returned by this getter into a mutable mapping (e.g., by passing the former
    to the :class:`dict` constructor as is).

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    -------
    LexicalScope
        Local scope for this class.

    Raises
    ------
    exception_cls
        If the next non-ignored frame following the last ignored frame is *not*
        the parent callable or module directly declaring the passed callable.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'

    #FIXME: Report this issue to the CPython issue tracker when time permits.
    #So, probably never. Convincing anyone that this isn't a @beartype issue is
    #likely to be an exercise in QA futility. *sigh*
    # Unsafe frozen dictionary of attributes directly defined by this class.
    #
    # Note that this dictionary:
    # * Is actually an instance of the builtin C-based "mappingproxy" type,
    #   which explicitly prohibits attribute assignment and is thus effectively
    #   frozen: e.g.,
    #       >>> class MuhClass: ...
    #       >>> MuhClass.__dict__['ugh'] = 3
    #       TypeError: 'mappingproxy' object does not support item assignment
    # * Unsafely contains the __new__() dunder method for classes explicitly
    #   defining that method. Ideally, including that method in the returned
    #   dictionary would be safe. Unfortunately, it isn't. Even recent versions
    #   of CPython appear to suffer an extremely subtle issue with respect to
    #   PEP 435-compliant "enum.Enum" subclasses nested inside other arbitrary
    #   classes when those subclasses define one or more methods annotated by
    #   PEP 484-compliant stringified forward references: e.g.,
    #       from beartype import beartype
    #       import enum
    #
    #       class Outer:
    #           @beartype
    #           class Inner(enum.Enum):
    #               ONE = 3
    #
    #               def muh_method(self, muh_str: 'str') -> str:
    #                   return 'Guh! ' + muh_str
    #
    #       print(Outer.__new__)
    #       Outer()
    #
    #   ...which first prints and then raises:
    #       <function Enum.__new__ at 0x7f1466536090>
    #       Traceback (most recent call last):
    #         File "/home/leycec/tmp/mopy.py", line 51, in <module>
    #           Outer()
    #           ~~~~~^^
    #       TypeError: Enum.__new__() missing 1 required positional argument:
    #       'value'
    #
    #   In other words, @beartype somehow magically replaces the Outer.__new__()
    #   dunder method by the Outer.Inner.__new__() dunder method! Except...
    #   @beartype *IS NEVER DOING THAT*. CPython itself is doing that. Why?
    #   Unclear. The low-level issue appears to concern the eval() builtin,
    #   which @beartype calls to resolve the PEP 484-compliant stringified
    #   forward reference annotating the Outer.Inner.muh_method() method. By
    #   default, this low-level getter naively returns a dictionary containing
    #   a key-value pair encapsulating the Outer.Inner.__new__() dunder method,
    #   which the higher-level make_scope_forward_decor_curr() factory then
    #   folds into the local scope it dynamically computes for the
    #   Outer.Inner.muh_method() method, like so:
    #       type_locals = get_type_locals(cls_curr)
    #       func_locals.update(type_locals)
    #
    #   The even higher-level _resolve_hint_pep484_ref_str() resolver then
    #   passes that scope to the eval() function, like so:
    #       hint_resolved = eval(hint, scope_forward)
    #
    #   That eval() call then appears to dangerously perform the Outer.__new__()
    #   dunder method replacement described above. Why? No idea. Filtering out
    #   *ALL* "__new__" attributes from the dictionary returned by this getter
    #   suffices to resolve this issue. That is thus what we do -- despite no
    #   one actually understanding this issue.
    #
    #   Good luck convincing anyone that that is an issue outside @beartype.
    #   It's *NOT* @beartype's fault. It just looks like it. A *LOT* like it.
    type_locals_unsafe = cls.__dict__

    # Safe frozen dictionary of attributes directly defined by this class,
    # filtering out *ALL* unsafe "__new__" dunder attributes as detailed above.
    type_locals_safe: LexicalScope = FrozenDict({
        key: value
        for key, value in type_locals_unsafe.items()
        if key != '__new__'
    })

    # Return this frozen dictionary.
    return type_locals_safe
