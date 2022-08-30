#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) type variable classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant :attr:`typing.TypeVar` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._doorcls import TypeHint
from beartype.door._proposal.doorpep484604 import UnionTypeHint
from beartype.roar import BeartypeDoorPepUnsupportedException
from beartype.typing import (
    Any,
    Tuple,
    TypeVar,
)

# ....................{ SUBCLASSES                         }....................
#FIXME: Document all public and private attributes of this class, please.
class TypeVarTypeHint(UnionTypeHint):
    '''
    **Type variable wrapper** (i.e., high-level object encapsulating a low-level
    :pep:`484`-compliant :attr:`typing.TypeVar` type hint).

    Attributes (Private)
    --------
    '''

    # ..................{ VARIABLES                          }..................
    _hint: TypeVar

    # ..................{ PRIVATE                            }..................
    def _wrap_children(
        self, unordered_children: tuple) -> Tuple[TypeHint, ...]:

        # Human-readable string describing the variance of this type variable if
        # any *OR* "None" otherwise (i.e., if this type variable is invariant).
        variance_str = None
        if self._hint.__covariant__:
            variance_str = 'covariant'
        elif self._hint.__contravariant__:
            variance_str = 'contravariant'

        # If this type variable is variant, raise an exception.
        if variance_str:
            raise BeartypeDoorPepUnsupportedException(
                f'Type hint {repr(self._hint)} '
                f'variance "{variance_str}" currently unsupported.'
            )
        # Else, this type variable is invariant.

        # TypeVars may only be bound or constrained, but not both. The
        # difference between the two has semantic meaning for static type
        # checkers, but relatively little meaning for us here. Ultimately, we're
        # only concerned with the set of compatible types present in either the
        # bound or the constraints, so we treat a TypeVar as a Union of its
        # constraints or bound. See also:
        #     https://docs.python.org/3/library/typing.html#typing.TypeVar
        if self._hint.__bound__ is not None:
            return (TypeHint(self._hint.__bound__),)
        elif self._hint.__constraints__:
            return tuple(TypeHint(t) for t in self._hint.__constraints__)

        return (TypeHint(Any),)
