#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) type alias
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`695`-compliant type aliases).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorabc import (
    CollectionTypeHints,
    TypeHint,
)
from beartype._util.cache.func.utilcacheproperty import (
    get_property_var_name,
    property_cached,
)
from beartype._util.hint.pep.proposal.pep695 import (
    get_hint_pep695_unsubbed_alias)
from beartype._util.hint.pep.utilpepget import get_hint_pep_childs
from beartype._data.typing.datatypingport import Hint
from collections.abc import Callable
from threading import local

# ....................{ SUBCLASSES                         }....................
class Pep695TypeAliasTypeHint(TypeHint):
    '''
    **Type alias wrapper** (i.e., high-level object encapsulating a low-level
    :pep:`695`-compliant type alias created by a statement of the form ``type
    {alias_name} = {alias_value}``, possibly subscripted by one or more child
    hints replacing the type parameters parametrizing that alias).

    :pep:`695` explicitly defines type aliases to be **transparent** to type
    checkers: an alias conveys exactly the semantics of the hint aliased by that
    alias. This wrapper thus preserves the alias itself (e.g., for the
    :attr:`hint` property and machine-readable representations) while deferring
    *all* semantic decisions (e.g., equality, subhint testing) to the wrapper
    wrapping the hint aliased by that alias.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    __slots__ = (
        get_property_var_name('_hint_aliased_wrapper'),
    )

    # ..................{ PRIVATE ~ properties               }..................
    @property  # type: ignore
    @property_cached
    def _hint_aliased_wrapper(self) -> TypeHint:
        '''
        Wrapper wrapping the hint aliased by the type alias wrapped by this
        wrapper.

        This property is intentionally deferred rather than decided by the
        :meth:`__init__` method. Why? Because :pep:`695` type aliases are
        lazily evaluated and thus commonly recursive (e.g., ``type Tree = int |
        list[Tree]``). Deferring this decision until required guarantees that
        merely instantiating this wrapper is guaranteed to halt.
        '''

        # Unsubscripted type alias underlying this possibly subscripted type
        # alias, defined as either this alias itself if unsubscripted *OR* the
        # origin of this alias otherwise.
        hint_unsubbed = getattr(self._hint, '__origin__', self._hint)

        # Hint aliased by this alias. Note that this getter is memoized and thus
        # intentionally called with positional arguments.
        hint_aliased = get_hint_pep695_unsubbed_alias(hint_unsubbed, '')  # type: ignore[arg-type]

        # Child hints subscripting this alias if any *OR* the empty tuple.
        hint_childs = get_hint_pep_childs(self._hint)

        # If this alias is subscripted, replace the type parameters
        # parametrizing this alias by these child hints. Note that CPython
        # itself performs this replacement, which is thus guaranteed to comply
        # with PEP 695 in a version-specific manner.
        if hint_childs:
            hint_aliased = hint_aliased[hint_childs]  # type: ignore[index]
        # Else, this alias is unsubscripted. Preserve this hint as is.

        # Wrap this hint.
        return TypeHint(hint_aliased)


    @property
    def unaliased(self) -> TypeHint:

        # Wrapper wrapping the hint aliased by this alias, which the caching
        # "_TypeHintMetaclass" metaclass guarantees to be the same singleton
        # wrapper returned by passing that hint to the "TypeHint" superclass.
        return self._hint_aliased_wrapper


    @property
    def _branches(self) -> CollectionTypeHints:

        # Defer to the branches of the hint aliased by this alias, guaranteeing
        # that this alias is transparent when passed as the "other" operand of
        # the is_subhint() tester.
        return self._hint_aliased_wrapper._branches


    @property
    def _is_args_ignorable(self) -> bool:
        return self._hint_aliased_wrapper._is_args_ignorable

    # ..................{ PRIVATE ~ factories                }..................
    def _make_args(self) -> tuple:

        # Preserve the child hints subscripting this alias (if any), enabling
        # the len(), iter(), and [] APIs to behave as expected.
        return get_hint_pep_childs(self._hint)

    # ..................{ PRIVATE ~ getters                  }..................
    def _get_hash(self) -> int:

        # Set of the IDs of all type aliases currently being hashed by the
        # current thread. PEP 695 type aliases are commonly recursive (e.g.,
        # "type Tree = int | list[Tree]"). Since hashing a recursive alias as
        # the hint aliased by that alias would provoke infinite recursion,
        # detect and halt that recursion here.
        hint_ids = _hint_ids_hashing.ids

        # If this alias is already being hashed, this alias is recursive. In
        # this case, fallback to hashing this alias as itself.
        if id(self._hint) in hint_ids:
            return _HASH_RECURSIVE
        # Else, this alias is *NOT* already being hashed.

        # Note that this alias is now being hashed.
        hint_ids.add(id(self._hint))

        # Attempt to hash this alias as the hint aliased by this alias,
        # preserving consistency between equality and hashing.
        try:
            return hash(self._hint_aliased_wrapper)
        # Note that this alias is no longer being hashed.
        finally:
            hint_ids.discard(id(self._hint))

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_equal(self, other: TypeHint) -> bool:
        return self._hint_aliased_wrapper._is_equal(other)


    def _is_subhint(self, other: TypeHint) -> bool:
        return self._defer_guarded(
            self._hint_aliased_wrapper._is_subhint, other)


    def _is_subhint_branch(self, branch: TypeHint) -> bool:
        return self._defer_guarded(
            self._hint_aliased_wrapper._is_subhint_branch, branch)

    # ..................{ PRIVATE ~ deferrers                }..................
    def _defer_guarded(self, tester: Callable, other: TypeHint) -> bool:
        '''
        Result of passing the passed wrapper to the passed bound tester method
        of the wrapper wrapping the hint aliased by this alias, guarding
        recursive aliases against infinite recursion.

        :pep:`695` type aliases are commonly recursive (e.g., ``type Tree = int
        | list[Tree]``), whose wrappers thus form a cyclic object graph. Naively
        deferring to that graph would recurse infinitely. Detect that here.
        '''

        # Set of the keys of all comparisons currently being performed by the
        # current thread.
        hint_ids = _hint_ids_comparing.ids

        # Unique key identifying this comparison.
        hint_id = (id(self._hint), id(other), id(tester.__func__))

        # If this comparison is already underway, this alias is recursive. In
        # this case, ignore this recursion by returning true. @beartype
        # currently embraces the easiest, fastest, and laziest approach to
        # recursive hints everywhere: just ignore all recursion!
        if hint_id in hint_ids:
            return True
        # Else, this comparison is *NOT* already underway.

        # Note that this comparison is now underway.
        hint_ids.add(hint_id)

        # Attempt to defer to this tester.
        try:
            return tester(other)
        # Note that this comparison is no longer underway.
        finally:
            hint_ids.discard(hint_id)


# ....................{ PRIVATE ~ globals                  }....................
class _HintIdsThreadLocal(local):
    '''
    Thread-local set of the IDs of all :pep:`695`-compliant type aliases
    currently being hashed by the current thread.
    '''

    def __init__(self) -> None:
        self.ids: set = set()


_HASH_RECURSIVE = hash('beartype.door recursive PEP 695 type alias')

_hint_ids_hashing = _HintIdsThreadLocal()
_hint_ids_comparing = _HintIdsThreadLocal()
