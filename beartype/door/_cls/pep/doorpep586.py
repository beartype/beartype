#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) literal type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`586`-compliant :attr:`typing.Literal` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsub import _TypeHintSubscripted
from beartype.door._cls.doorsuper import TypeHint
from beartype.typing import Tuple

# ....................{ SUBCLASSES                         }....................
class LiteralTypeHint(_TypeHintSubscripted):
    '''
    **Literal type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`586`-compliant :attr:`typing.Literal` type hint).
    '''

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _args_wrapped_tuple(self) -> Tuple[TypeHint, ...]:

        # Return the empty tuple, thus presenting "Literal" type hints as having
        # *NO* child type hints. Why? Because the arguments subscripting a
        # Literal type hint are *NOT* generally PEP-compliant type hints and
        # thus *CANNOT* be safely wrapped by "TypeHint" instances. These
        # arguments are merely arbitrary values.
        #
        # Note that this property getter is intentionally *NOT* memoized with
        # @property_cached, as Python already efficiently guarantees the empty
        # tuple to be a singleton.
        return ()


    @property
    def _is_args_ignorable(self) -> bool:
        return False

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_subhint(self, other: TypeHint) -> bool:

        # If the other hint is also a literal, return true only if the set of
        # all child hints subscripting this literal is a subset of the set of
        # all child hints subscripting that literal.
        if isinstance(other, LiteralTypeHint):
            return all(
                this_hint_child in other._args
                for this_hint_child in self._args
            )
        # Else, the other hint is *NOT* also a literal.
        #
        # If the other hint is just an origin, check that *ALL* child hints
        # subscripting this literal are instances of that origin.
        elif other._is_args_ignorable:
            return all(
                isinstance(this_hint_child, other._origin)
                for this_hint_child in self._args
            )
        # Else, the other hint is *NOT* just an origin.

        # Return true only if the type of each child hint subscripting this
        # literal is a subhint of the other hint.
        return all(
            TypeHint(type(this_hint_child)).is_subhint(other)
            for this_hint_child in self._args
        )
