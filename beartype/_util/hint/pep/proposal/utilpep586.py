#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`586`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPep586Exception
from beartype._cave._cavefast import EnumMemberType, NoneType
from beartype._data.hint.pep.sign.datapepsigns import HintSignLiteral
from beartype._util.text.utiltextjoin import join_delimited_disjunction_classes
from typing import Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_LITERAL_ARG_TYPES = (bool, bytes, int, str, EnumMemberType, NoneType)
'''
Tuple of all types of objects permissible as arguments subscripting the
:pep:`586`-compliant :attr:`typing.Literal` singleton.

These types are explicitly listed by :pep:`586` as follows:

    Literal may be parameterized with literal ints, byte and unicode strings,
    bools, Enum values and None.
'''

# ....................{ VALIDATORS                        }....................
def die_unless_hint_pep586(hint: Any) -> None:
    '''
    Raise an exception unless the passed object is a :pep:`586`-compliant
    type hint (i.e., subscription of the :attr:`typing.Literal` singleton).

    Ideally, the :attr:`typing.Literal` singleton would internally validate the
    literal objects subscripting that singleton at subscription time (i.e., in
    the body of the ``__class_getitem__()`` dunder method). Whereas *all* other
    :mod:`typing` attributes do just that, :attr:`typing.Literal` permissively
    accepts all possible arguments like a post-modern philosopher hopped up on
    too much tenure. For inexplicable reasons, :pep:`586` explicitly requires
    third-party type checkers (that's us) to validate these hints rather than
    standardizing that validation in the :mod:`typing` module. Weep, Guido!

    Caveats
    ----------
    **This function is slow** and should thus be called only once per
    visitation of a :pep:`586`-compliant type hint. Specifically, this function
    is O(n) where n is the number of arguments subscripting this hint.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Raises
    ----------
    BeartypeDecorHintPep586Exception
        If this object either:

        * Is *not* a subscription of the :attr:`typing.Literal` singleton.
        * Subscripts :attr:`typing.Literal` with zero arguments via the empty
          tuple, which :attr:`typing.Literal` sadly fails to guard against.
        * Subscripts :attr:`typing.Literal` with one or more arguments that are
          *not* **valid literals**, defined as the set of all:

          * Booleans.
          * Byte strings.
          * Integers.
          * Unicode strings.
          * :class:`enum.Enum` members.
          * The ``None`` singleton.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign

    # If this hint is *NOT* PEP 586-compliant, raise an exception.
    if get_hint_pep_sign(hint) is not HintSignLiteral:
        raise BeartypeDecorHintPep586Exception(
            f'PEP 586 type hint {repr(hint)} not "typing.Literal".')
    # Else, this hint is PEP 586-compliant.

    # Tuple of zero or more literal objects subscripting this hint.
    hint_literals = hint.__args__

    # If the caller maliciously subscripted this hint by the empty tuple and
    # thus *NO* arguments, raise an exception. Ideally, the "typing.Literal"
    # singleton would guard against this itself. It does not; thus, we do.
    if not hint_literals:
        raise BeartypeDecorHintPep586Exception(
            f'PEP 586 type hint {repr(hint)} subscripted by empty tuple.')

    # If any argument subscripting this hint is *NOT* a valid literal...
    #
    # Sadly, despite PEP 586 imposing strict restrictions on the types of
    # objects permissible as arguments subscripting the "typing.Literal"
    # singleton, PEP 586 explicitly offloads the odious chore of enforcing
    # those restrictions onto third-party type checkers by intentionally
    # implementing that singleton to permissively accept all possible
    # objects when subscripted:
    #
    #     Although the set of parameters Literal[...] may contain at type
    #     check time is very small, the actual implementation of
    #     typing.Literal will not perform any checks at runtime.
    if any(
        not isinstance(hint_literal, _LITERAL_ARG_TYPES)
        for hint_literal in hint_literals
    # Then raise a human-readable exception describing this invalidity.
    ):
        # For each argument subscripting this hint...
        for hint_literal_index, hint_literal in enumerate(hint_literals):
            # If this argument is invalid as a literal argument...
            if not isinstance(hint_literal, _LITERAL_ARG_TYPES):
                # Human-readable concatenation of the types of all valid
                # literal arguments, delimited by commas and/or "or".
                hint_literal_types = join_delimited_disjunction_classes(
                    _LITERAL_ARG_TYPES)

                # Raise an exception.
                raise BeartypeDecorHintPep586Exception(
                    f'PEP 586 type hint {repr(hint)} '
                    f'argument {hint_literal_index} {repr(hint_literal)} '
                    f'not {hint_literal_types}.'
                )
