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

    # ..................{ PRIVATE ~ methods                  }..................
    def _is_subhint_branch(self, branch: TypeHint) -> bool:
        # print(f'Entering ClassTypeHint._is_subhint_branch({self}, {branch})...')
        # print(f'{branch}._is_args_ignorable: {branch._is_args_ignorable}')
        # print(f'{self}._origin: {self._origin}')
        # print(f'{branch}._origin: {branch._origin}')

        # print(f'{self}._hint: {self._hint}')
        # print(f'{branch}._hint: {branch._hint}')
        # # print(f'{repr(self)}._origin.__args__: {self._origin.__args__}')
        # print(f'{repr(self)}._origin.__parameters__: {self._origin.__parameters__}')
        # # print(f'{repr(branch)}._origin.__args__: {branch._origin.__args__}')
        # print(f'{repr(branch)}._origin.__parameters__: {branch._origin.__parameters__}')
        # print(f'{repr(self)}._is_args_ignorable: {self._is_args_ignorable}')

        #FIXME: Actually, let's avoid the implicit numeric tower for now.
        #Explicit is better than implicit and we really strongly disagree with
        #this subsection of PEP 484, which does more real-world harm than good.
        # # Numeric tower:
        # # https://peps.python.org/pep-0484/#the-numeric-tower
        # if self._origin is float and branch._origin in {float, int}:
        #     return True
        # if self._origin is complex and branch._origin in {complex, float, int}:
        #     return True

        # Return true only if...
        return (
            # That class is unsubscripted (and thus *NOT* a subscripted generic)
            # *AND*...
            branch._is_args_ignorable and
            # The unsubscripted type originating this class is a subclass of the
            # unsubscripted type originating that class.
            issubclass(self._origin, branch._origin)
        )
