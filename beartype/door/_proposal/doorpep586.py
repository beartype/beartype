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
class _TypeHintLiteral(_TypeHintSubscripted):
    '''
    **Literal type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`586`-compliant :attr:`typing.Literal` type hint).
    '''

    # ..................{ TESTERS                            }..................
    @callable_cached
    def is_subhint(self, other: TypeHint) -> bool:

        die_unless_typehint(other)

        # If the other hint is also a literal, check that our args are a subset
        # of theirs.
        if isinstance(other, _TypeHintLiteral):
            return all(arg in other._args for arg in self._args)

        # If the other hint is a just an origin, check that our args are *ALL*
        # instances of that origin.
        if other._is_args_ignorable:
            return all(isinstance(x, other._origin) for x in self._args)

        # Else... something, something. *waves hands madly*
        return all(TypeHint(type(arg)) <= other for arg in self._args)

    # ..................{ PRIVATE                            }..................
    def _wrap_children(self, _: tuple) -> Tuple[TypeHint, ...]:
        # The parameters of Literal aren't hints; they're arbitrary values.
        # Do *NOT* erroneously wrap those values with "TypeHint" instances.
        return ()

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _is_args_ignorable(self) -> bool:
        return False
