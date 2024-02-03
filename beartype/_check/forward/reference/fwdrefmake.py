#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference factories** (i.e.,  low-level callables creating
and returning forward reference proxy subclasses deferring the resolution of a
stringified type hint referencing an attribute that has yet to be defined and
annotating a class or callable decorated by the :func:`beartype.beartype`
decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import (
    Type,
)
from beartype._data.hint.datahinttyping import (
    TupleTypes,
)
from beartype._check.forward.reference.fwdrefabc import (
    BeartypeForwardRefABC,
    _BeartypeForwardRefIndexableABC,
    _BeartypeForwardRefIndexableABC_BASES,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.utilclsmake import make_type

# ....................{ FACTORIES                          }....................
@callable_cached
def make_forwardref_indexable_subtype(
    scope_name: str, hint_name: str) -> Type[_BeartypeForwardRefIndexableABC]:
    '''
    Create and return a new **subscriptable forward reference subclass** (i.e.,
    concrete subclass of the :class:`._BeartypeForwardRefIndexableABC` abstract
    base class (ABC) deferring the resolution of the unresolved type hint with
    the passed name, transparently permitting this type hint to be subscripted
    by any arbitrary positional and keyword parameters).

    Parameters
    ----------
    scope_name : str
        Possibly ignored lexical scope name. Specifically:

        * If ``hint_name`` is absolute (i.e., contains one or more ``.``
          delimiters), this parameter is silently ignored in favour of the
          fully-qualified name of the module prefixing ``hint_name``.
        * If ``hint_name`` is relative (i.e., contains *no* ``.`` delimiters),
          this parameter declares the absolute (i.e., fully-qualified) name of
          the lexical scope to which this unresolved type hint is relative.

        The fully-qualified name of the module prefixing ``hint_name`` (if any)
        thus *always* takes precedence over this lexical scope name, which only
        provides a fallback to resolve relative forward references. While
        unintuitive, this is needed to resolve absolute forward references.
    hint_name : str
        Relative (i.e., unqualified) or absolute (i.e., fully-qualified) name of
        this unresolved type hint to be referenced.

    This factory is memoized for efficiency.

    Returns
    -------
    Type[_BeartypeForwardRefIndexableABC]
        Subscriptable forward reference subclass referencing this type hint.
    '''

    # Subscriptable forward reference to be returned.
    #
    # Note that parameters *MUST* be passed positionally to the memoized
    # _make_forwardref_subtype() factory function.
    return _make_forwardref_subtype(  # type: ignore[return-value]
        scope_name=scope_name,
        hint_name=hint_name,
        type_bases=_BeartypeForwardRefIndexableABC_BASES,
    )

# ....................{ PRIVATE ~ factories                }....................
def _make_forwardref_subtype(
    scope_name: str,
    hint_name: str,
    type_bases: TupleTypes,
) -> Type[BeartypeForwardRefABC]:
    '''
    Create and return a new **forward reference subclass** (i.e., concrete
    subclass of the passed abstract base class (ABC) deferring the resolution of
    the type hint with the passed name transparently).

    This factory is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as *all* higher-level public factories
    calling this private factory are themselves already memoized.

    Parameters
    ----------
    scope_name : str
        Possibly ignored lexical scope name. See
        :func:`.make_forwardref_indexable_subtype` for further details.
    hint_name : str
        Absolute (i.e., fully-qualified) or relative (i.e., unqualified) name of
        the type hint referenced by this forward reference subclass.
    type_bases : Tuple[type, ...]
        Tuple of all base classes to be inherited by this forward reference
        subclass. For simplicity, this *must* be a 1-tuple
        ``(type_base,)`` where ``type_base`` is a
        :class:`._BeartypeForwardRefIndexableABC` subclass.

    Returns
    -------
    Type[_BeartypeForwardRefIndexableABC]
        Forward reference subclass referencing this type hint.

    Raises
    ------
    BeartypeDecorHintForwardRefException
        If this is a **relative forward reference** (i.e., ``hint_name``
        contains *no* ``.`` delimiters) *and* ``scope_name`` is :data:`None`,
        preventing this reference from being canonicalized into an absolute
        forward reference.
    '''
    assert isinstance(hint_name, str), f'{repr(hint_name)} not string.'
    assert isinstance(scope_name, str), f'{repr(scope_name)} not string.'
    assert len(type_bases) == 1, (
        f'{repr(type_bases)} not 1-tuple of a single superclass.')

    # Fully-qualified module name *AND* unqualified basename of the type hint
    # referenced by this forward reference subclass. Specifically, if the name
    # of this type hint is:
    # * Fully-qualified:
    #   * This module name is the substring of this name preceding the last "."
    #     delimiter in this name.
    #   * This basename is the substring of this name following the last "."
    #     delimiter in this name.
    # * Unqualified:
    #   * This module name is the empty string and thus ignorable.
    #   * This basename is this name as is.
    type_module_name, _, type_name = hint_name.rpartition('.')
    # _, _, type_name = hint_name.rpartition('.')

    # If this module name is the empty string *AND* no lexical scope name was
    # passed, this type hint is a relative forward reference relative to *NO*
    # lexical scope. In this case, raise an exception.
    if not (scope_name or type_module_name):
        type_module_name = scope_name
    # Else, either this module name is non-empty *OR* a lexical scope name was
    # passed. This type hint is thus either already an absolute forward
    # reference or a relative forward reference relative to a lexical scope that
    # can be canonicalized into an absolute forward reference.

    # Forward reference subclass to be returned.
    forwardref_subtype: Type[_BeartypeForwardRefIndexableABC] = make_type(
        type_name=type_name,
        type_module_name=scope_name,
        type_bases=type_bases,
    )

    # Classify passed parameters with this subclass.
    forwardref_subtype.__name_beartype__ = hint_name  # pyright: ignore[reportGeneralTypeIssues]
    forwardref_subtype.__scope_name_beartype__ = scope_name  # pyright: ignore[reportGeneralTypeIssues]

    # Nullify all remaining class variables of this subclass for safety.
    # forwardref_subtype.__type_beartype__ = None  # pyright: ignore[reportGeneralTypeIssues]

    # Return this subclass.
    return forwardref_subtype
