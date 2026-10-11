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
from beartype.roar import BeartypeDoorNonpepException
from beartype._cave._cavefast import HintPep646TypeVarTuplePackedType
from beartype._data.typing.datatypingport import Hint
from beartype._util.cache.func.utilcacheproperty import (
    get_property_var_name,
    property_cached,
)
from beartype._util.hint.pep.proposal.pep695 import (
    _get_hint_pep695_parameterizable_typeparams,
    get_hint_pep695_alias,
    is_hint_pep695_recursive,
)
from beartype._util.hint.pep.utilpepget import get_hint_pep_origin

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
    *all* semantic decisions (e.g., equality, hashing, subhint testing) to the
    :attr:`hint_aliased` wrapper wrapping the hint aliased by that alias. The
    :class:`TypeHint` superclass unwraps aliases at its public testers, so this
    subclass need only defer hashing, branches, and memoization keys.

    Caveats
    -------
    **Recursive type aliases** (e.g., ``type Tree = int | list[Tree]``) are
    currently unsupported, raising the same
    :exc:`beartype.roar.BeartypeDoorNonpepException` raised by *all* other type
    hints unsupported by this API. See also:
        https://github.com/beartype/beartype/issues/701
    '''

    # ..................{ CLASS VARIABLES                    }..................
    __slots__ = (
        get_property_var_name('hint_aliased'),
    )

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint: Hint) -> None:

        # Attempt to decide whether this alias is recursive. Since the hint
        # aliased by this alias is lazily evaluated by arbitrary user-defined
        # code, doing so may raise an arbitrary exception (e.g., "NameError" for
        # forward references to undefined attributes). In this case, raise the
        # same exception raised by "TypeHint" for all unsupported hints.
        try:
            is_recursive = is_hint_pep695_recursive(hint)
        except Exception as exception:
            raise BeartypeDoorNonpepException(
                f'PEP 695 type alias {repr(hint)} unevaluable and thus '
                f'unsupported by "beartype.door.TypeHint".'
            ) from exception

        # If this alias is recursive, raise an exception. Hashing and comparing
        # recursive aliases requires recursion guards throughout DOOR.
        if is_recursive:
            raise BeartypeDoorNonpepException(
                f'PEP 695 type alias {repr(hint)} recursive (i.e., '
                f'transitively refers to itself) and thus currently '
                f'unsupported by "beartype.door.TypeHint". See also:\n'
                f'    https://github.com/beartype/beartype/issues/701'
            )
        # Else, this alias is non-recursive.

        # Initialize our superclass.
        super().__init__(hint)

    # ..................{ PROPERTIES                         }..................
    @property  # type: ignore
    @property_cached
    def hint_aliased(self) -> TypeHint:
        '''
        Wrapper wrapping the hint aliased by the type alias wrapped by this
        wrapper, with the type parameters parametrizing that alias replaced by
        the child hints subscripting that alias (if any): e.g.,

        .. code-block:: pycon

           >>> from beartype.door import TypeHint
           >>> type MuhAlias = int

           # This wrapper preserves the alias...
           >>> TypeHint(MuhAlias).hint
           MuhAlias

           # ...while this property resolves it, returning the *SAME* singleton
           # wrapper as the hint aliased by that alias.
           >>> TypeHint(MuhAlias).hint_aliased is TypeHint(int)
           True
        '''

        # Hint aliased by this alias, still parametrized by type parameters if
        # this alias is subscripted. This getter is memoized and thus called
        # with positional arguments.
        hint_aliased = get_hint_pep695_alias(self._hint, '')

        # If this alias is subscripted, replace the type parameters
        # parametrizing this alias by the child hints subscripting this alias.
        if self._args:
            # Type parameters parametrizing the unsubscripted alias originating
            # this subscripted alias.
            hint_typeparams = _get_hint_pep695_parameterizable_typeparams(
                get_hint_pep_origin(self._hint))

            # If the aliased hint is itself one of those type parameters (e.g.,
            # "type Alias[T] = T"), that hint is *NOT* subscriptable. Replace
            # that hint by the corresponding child hint directly.
            if hint_aliased in hint_typeparams:
                # 0-based index of this type parameter.
                hint_typeparam_index = hint_typeparams.index(hint_aliased)

                # If a type variable tuple precedes this type parameter, that
                # tuple consumes a variable number of child hints. In this case,
                # this type parameter is the child hint at the same offset from
                # the end.
                if any(
                    isinstance(hint_typeparam, HintPep646TypeVarTuplePackedType)
                    for hint_typeparam in hint_typeparams[:hint_typeparam_index]
                ):
                    hint_typeparam_index += len(self._args) - len(hint_typeparams)

                # Replace this hint by the corresponding child hint.
                hint_aliased = self._args[hint_typeparam_index]
            # Else, defer to CPython's own type parameter substitution, which
            # is thus guaranteed to comply with PEP 695.
            else:
                hint_aliased = hint_aliased[self._args]  # type: ignore[index]
        # Else, this alias is unsubscripted. Preserve this hint as is.

        # Wrap this hint.
        return TypeHint(hint_aliased)

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _branches(self) -> CollectionTypeHints:

        # Defer to the branches of the hint aliased by this alias, guaranteeing
        # that this alias is transparent when subscripting a union. All other
        # semantic decisions (e.g., equality, subhint testing) are deferred by
        # the TypeHint superclass unwrapping aliases at its public entry points.
        return self.hint_aliased._branches

    # ..................{ PRIVATE ~ getters                  }..................
    def _get_hash(self) -> int:

        # Hash this alias as the hint aliased by this alias, preserving
        # consistency between equality and hashing.
        return hash(self.hint_aliased)


    def _get_repr_unique(self) -> str:

        # Key memoization on the hint aliased by this alias rather than this
        # alias, whose repr() is merely its non-unique name (e.g., "type X =
        # int" and "type X = str" in different modules). Since this alias
        # conveys exactly the semantics of that hint, sharing memoized results
        # with that hint is correct.
        return self.hint_aliased._get_repr_unique()
