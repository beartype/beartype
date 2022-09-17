#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) literal type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`586`-compliant :attr:`typing.Literal` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._doorcls import (
    TypeHint,
    _TypeHintSubscripted,
)
from beartype.door._doortest import die_unless_typehint
from beartype.typing import Tuple
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ SUBCLASSES                         }....................
#FIXME: Insufficient. We also need to override __eq__(), because Literal hints
#do *NOT* provide a sane _args_wrapped_tuple() required by the default __eq__().
class LiteralTypeHint(_TypeHintSubscripted):
    '''
    **Literal type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`586`-compliant :attr:`typing.Literal` type hint).
    '''

    # ..................{ TESTERS                            }..................
    @callable_cached
    def is_subhint(self, other: TypeHint) -> bool:

        # If the other hint is *NOT* also a wrapper, raise an exception.
        die_unless_typehint(other)
        # Else, the other hint is also a wrapper.

        # If the other hint is also a Literal, check that our args are a subset
        # of theirs.
        if isinstance(other, LiteralTypeHint):
            return all(arg in other._args for arg in self._args)
        # Else, the other hint is *NOT* also a Literal.
        #
        # If the other hint is just an origin, check that our args are *ALL*
        # instances of that origin.
        elif other._is_args_ignorable:
            return all(isinstance(x, other._origin) for x in self._args)
        # Else, the other hint is *NOT* just an origin.

        # Return true only if the type of each child hint subscripting this
        # parent hint is a subhint and thus inclusive subclass of the other
        # hint.
        return all(
            TypeHint(type(hint_child)) <= other for hint_child in self._args)

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _args_wrapped_tuple(self) -> Tuple[TypeHint, ...]:

        # Return the empty tuple, thus presenting Literal type hints as having
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
