#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) type variable
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant :attr:`typing.TypeVar` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.pep.doorpep484604 import UnionTypeHint
from beartype._data.hint.sign.datahintsigns import HintSignUnion
# from beartype._util.cache.func.utilcacheproperty import property_cached
from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
    get_hint_pep484_typevar_bounded_constraints_or_none)
from beartype._util.hint.pep.proposal.typearg.peptypeargrepr import (
    make_hint_typearg_unpacked_repr)
from beartype._util.hint.pep.utilpepget import get_hint_pep_childs
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none
from typing import (
    TYPE_CHECKING,
    TypeVar,
)

# ....................{ SUBCLASSES                         }....................
class TypeVarTypeHint(UnionTypeHint):
    '''
    **Type variable wrapper** (i.e., high-level object encapsulating a low-level
    :pep:`484`-compliant :attr:`typing.TypeVar` type hint).
    '''

    # ..................{ STATIC                             }..................
    # Squelch false negatives from static type checkers.
    if TYPE_CHECKING:
        _hint: TypeVar

    # ..................{ PROPERTIES                         }..................
    @property
    def is_ignorable(self) -> bool:

        # This type variable is ignorable only if this type variable is either:
        # * Unconstrained by any bounds or constraints (and thus effectively
        #   bound only by the "typing.Any" catch-all).
        # * Bound by an ignorable bound (e.g., "TypeVar('T', bound=object)").
        # * Constrained by one or more ignorable constraints. Since constraints
        #   effectively build a union over those constraints, even a single
        #   ignorable constraint suffices to render an entire type variable
        #   ignorable (e.g., "TypeVar('T', object)").
        return self._is_args_ignorable

    # ..................{ PRIVATE ~ getters                  }..................
    def _get_repr_unique(self) -> str:

        # Return a unique repr()-like string unambiguously encapsulating *ALL*
        # type variable fields (i.e., meaningful instance variables) rather than
        # the non-unique repr() strings known to be ambiguously returned for
        # otherwise distinct type variables.
        return make_hint_typearg_unpacked_repr(self._hint)

    # ..................{ PRIVATE ~ factories                }..................
    def _make_args(self) -> tuple:

        #FIXME: Support covariance and contravariance, please. We don't
        #particularly care about either at the moment. Moreover, runtime type
        #checkers were *NEVER* expected to support either -- although we
        #eventually intend to do so. For now, raising a fatal exception here
        #would seem to be extreme overkill. Doing nothing is (probably) better
        #than doing something reckless and wild.
        # # Human-readable string describing the variance of this type variable if
        # # any *OR* "None" otherwise (i.e., if this type variable is invariant).
        # variance_str = None
        # if self._hint.__covariant__:
        #     variance_str = 'covariant'
        # elif self._hint.__contravariant__:
        #     variance_str = 'contravariant'
        #
        # # If this type variable is variant, raise an exception.
        # if variance_str:
        #     raise BeartypeDoorPepUnsupportedException(
        #         f'Type hint {repr(self._hint)} '
        #         f'variance "{variance_str}" currently unsupported.'
        #     )
        # # Else, this type variable is invariant.

        # Note that type variables may only be bound or constrained, but *NOT*
        # both. The difference between the two has semantic meaning for static
        # type checkers but relatively little meaning for us. Ultimately, we're
        # only concerned with the set of compatible types present in either the
        # bound or the constraints. We thus treat a type variable as a union of
        # its constraints or bound. See also:
        #     https://docs.python.org/3/library/typing.html#typing.TypeVar

        # If this type variable was parametrized by:
        # * One or more constraints (i.e., positional arguments passed by the
        #   caller to the typing.TypeVar.__init__() call initializing this
        #   type variable), a new PEP-484 or 604-compliant union hint over those
        #   constraints.
        # * One upper bound (i.e., "bound" keyword argument passed by the caller
        #   to the typing.TypeVar.__init__() call initializing this type
        #   variable), that bound as is.
        #. Else, "None".
        hint_child = get_hint_pep484_typevar_bounded_constraints_or_none(
            self._hint)

        # Tuple of all child hints to be returned as the fake "arguments"
        # subscripting this type variable, defaulting to the 1-tuple containing
        # the root "object" superclass. Why? Because PEP 484 states that an
        # unconstrained and unbounded type variable has an implicit upper bound
        # of (waitforit) the root "object" superclass. *shrugs meaningfully*
        args = _TUPLE_OBJECT

        # If this type variable is either constrained *OR* bounded...
        if hint_child is not None:
            # Sign uniquely identifying the child hint synthesized by the above
            # call to get_hint_pep484_typevar_bounded_constraints_or_none().
            hint_child_sign = get_hint_pep_sign_or_none(hint_child)

            # If this child hint is a union, this type variable was constrained
            # by one or more constraints. In this case, return this existing
            # tuple of these constraints.
            if hint_child_sign is HintSignUnion:
                args = get_hint_pep_childs(hint_child)
            # Else, this child hint is *NOT* a union -- implying this type
            # variable was bounded by a single child hint. In this case, return
            # the 1-tuple containing only this child hint.
            else:
                args = (hint_child,)

        # Return this tuple of all child hints.
        return args

# ....................{ PRIVATE ~ constants                }....................
_TUPLE_OBJECT = (object,)
'''
1-tuple containing only the root :class:`object` superclass.
'''
