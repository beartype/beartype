#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) unsubscripted type
hint factory classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing
support for :pep:`484`-compliant unsubscripted type hint factories (e.g.,
:obj:`typing.List`, :obj:`typing.Tuple`) *not* already matched by a more
fine-grained :class:`beartype.door.TypeHint` subclass).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsuper import TypeHint

# ....................{ SUBCLASSES                         }....................
#FIXME: Actually use in lieu of "ClassTypeHint", please. *sigh*
class UnsubscriptedTypeHint(TypeHint):
    '''
    **Unsubscripted type hint factory wrapper** (i.e., high-level object
    encapsulating a low-level :pep:`484`-compliant unsubscripted type hint
    factory (e.g., :obj:`typing.List`) originating from an isinstanceable class
    (e.g., :class:`list`) such that *all* objects satisfying this factory are
    instances of that class).
    '''

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _is_args_ignorable(self) -> bool:

        # Unconditionally return true, as unsubscripted type hint factories are
        # unsubscripted and could thus be said to only have ignorable arguments.
        return True

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_subhint_branch(self, branch: TypeHint) -> bool:
        # print(f'Entering ClassTypeHint._is_subhint_branch({self}, {branch})...')
        # print(f'{self}._hint: {self._hint}')
        # print(f'{branch}._hint: {branch._hint}')
        # print(f'{self}._origin_type: {self._origin_type}')
        # print(f'{branch}._origin_type: {branch._origin_type}')
        # print(f'{repr(self)}._is_args_ignorable: {self._is_args_ignorable}')
        # print(f'{repr(branch)}._is_args_ignorable: {branch._is_args_ignorable}')
        # # print(f'{repr(self)}._origin_type.__args__: {self._origin_type.__args__}')
        # print(f'{repr(self)}._origin_type.__parameters__: {self._origin_type.__parameters__}')
        # # print(f'{repr(branch)}._origin_type.__args__: {branch._origin_type.__args__}')
        # print(f'{repr(branch)}._origin_type.__parameters__: {branch._origin_type.__parameters__}')

        #FIXME: Actually, let's avoid the implicit numeric tower for now.
        #Explicit is better than implicit and we really strongly disagree with
        #this subsection of PEP 484, which does more real-world harm than good.
        # # Numeric tower:
        # # https://peps.python.org/pep-0484/#the-numeric-tower
        # if self._origin_type is float and branch._origin_type in {float, int}:
        #     return True
        # if self._origin_type is complex and branch._origin_type in {complex, float, int}:
        #     return True

        # Return true only if...
        return (
            # The passed branch is also unsubscripted *AND*...
            branch._is_args_ignorable and
            # The type originating this hint is a subclass of the
            # unsubscripted type originating that branch.
            issubclass(self._origin_type, branch._origin_type)
        )

    # ..................{ PRIVATE ~ getters                  }..................
    def _get_hash(self) -> int:

        # Low-level hashable object encapsulated by this high-level wrapper to
        # be hashed below as the hash for this wrapper, defined as either...
        wrapper_hashable = (
            # * If this hint originates from an origin type (e.g., "typing.List"
            #   originates from "list"), that origin type.
            # * Else if this hint is itself a type (e.g., "list"), that type.
            #
            # Note that this is the common case and thus tested first.
            self._origin_type
            if self._origin_type is not object else
            # Else, this hint neither originates from an origin type *OR* is
            # itself a type. In this case, our superclass defaulted this
            # "_origin_type" instance variable to the root "object" superclass!
            # Although trivial, hashing that superclass would invite hash
            # collisions by erroneously hashing unsubscripted hints to the same
            # hash. Avoid such nonsense by falling back to this hint as is. Ugh.
            self._hint
        )

        # Hash this wrapper by this hashable.
        return hash(wrapper_hashable)
