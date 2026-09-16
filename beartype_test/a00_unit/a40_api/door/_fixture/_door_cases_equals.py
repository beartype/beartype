#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) equality fixtures**
(i.e., :mod:`pytest`-specific context managers passed as parameters to unit
tests validating the :mod:`beartype.door.TypeHint.__eq__` dunder method).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ FIXTURES ~ equality                }....................
@fixture(scope='session')
def door_cases_equals() -> 'tuple[tuple[object, object, bool]]':
    '''
    Session-scoped fixture returning an iterable of **hint equality cases**
    (i.e., 3-tuples ``(hint_a, hint_b, is_equal)`` describing the equality
    relations between two PEP-compliant type hints), efficiently cached across
    all tests requiring this fixture.

    This iterable is intentionally defined by the return of this fixture rather
    than as a global constant of this submodule. Why? Because the former safely
    defers all heavyweight imports required to define this iterable to the call
    of the first unit test requiring this fixture, whereas the latter unsafely
    performs those imports at pytest test collection time.

    Returns
    -------
    Iterable[Tuple[object, object, bool]]
        Iterable of one or more 3-tuples ``(hint_a, hint_b, is_equal)``,
        where:

        * ``hint_a`` is the PEP-compliant type hint to be passed as the first
          parameter to the :meth:`beartype.door.TypeHint.__equals__` tester.
        * ``hint_b`` is the PEP-compliant type hint to be passed as the second
          parameter to the :meth:`beartype.door.TypeHint.__equals__` tester.
        * ``is_equal`` is ``True`` only if these hints are equal according to
          that tester.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype.typing import Annotated
    from collections.abc import (
        Awaitable as AwaitableABC,
        Callable as CallableABC,
        Sequence as SequenceABC,
    )
    from numbers import Number

    # Intentionally import from "typing" rather than "beartype.typing" to
    # guarantee PEP 484-compliant type hints.
    from typing import (
        Any,
        List,
        Tuple,
        Union,
    )

    # ..................{ LISTS                              }..................
    HINT_EQUALITY_CASES = [
        # ..................{ NON-PEP                        }..................
        # PEP-noncompliant types are obviously equal to themselves. They better!
        (list, list, True),

        # ..................{ PEP 484 ~ any                  }..................
        # PEP 484-compliant "Any" singleton is equal to itself. We swear.
        (Any, Any, True),

        # PEP 484-compliant "Any" singleton is technically unequal (despite
        # being semantically equal) to *ANY* other valid type hint. See the
        # AnyTypeHint._is_equal() implementation for further commentary.
        (Any, str, False),
        (Any, list[str], False),

        # ..................{ PEP 484 ~ argless              }..................
        # PEP 484-compliant unsubscripted type hint factories are equal to the
        # PEP-noncompliant types underlying those factories.
        (Tuple, tuple, True),
        (List, list, True),

        # ..................{ PEP 484 ~ arg : sequence       }..................
        # PEP 484-compliant sequence type hints.
        (list, List[Any], True),
        (tuple, Tuple[Any, ...], True),

        # ..................{ PEP 484 ~ arg : union          }..................
        # PEP 484-compliant union type hints.
        (Union[int, str], Union[str, list], False),
        (Union[Number, int], Union[Number, float], True),

        # Test that union equality ignores order.
        (Union[int, str], Union[str, int], True),

        # Test that union equality compares child type hints collectively rather
        # than individually.
        #
        # Note that this pair of cases tests numerous edge cases, including:
        # * Equality comparison of non-unions against unions. Although
        #   "Union[int]" superficially appears to be a union, Python reduces
        #   "Union[int]" to simply "int" at runtime.
        (Union[bool, int], Union[int], True),
        (Union[int], Union[bool, int], True),

        # ..................{ PEP 585 ~ arg                  }..................
        # PEP 585-compliant type hints.
        (list[str], List[str], True),
        (tuple[str, ...], Tuple[str, ...], True),
        (tuple[int, Any], tuple[int, str], False),
        (AwaitableABC[SequenceABC[int]], AwaitableABC[SequenceABC[int]], True),
        (CallableABC, CallableABC[..., Any], True),

        # ..................{ PEP 593                        }..................
        # PEP 593-compliant type hints.
        (
            Annotated[int, 'For simple sheep'],
            Annotated[int, 'For simple sheep'],
            True,
        ),
        (
            Annotated[int, 'and such'],
            Annotated[int, 'are daffodils'],
            False,
        ),

        # ..................{ PEP 604                        }..................
        # PEP 604-compliant union type hints.

        # Any union subscripted by "Any" semantically reduces to simply "Any"
        # and is thus technically unequal (despite being semantically equal) to
        # *ANY* other union *NOT* also subscripted by "Any". See the
        # AnyTypeHint._is_equal() implementation for further commentary.
        (Any | int, Any, False),
        (int | Any, Any, False),  # <-- intentionally exercises an edge case!
        (Any | int, int, False),
        (Any | int, Any | int, True),
        (Any | int, str | int, False),
    ]

    # ..................{ RETURN                             }..................
    # Return this mutable list coerced into an immutable tuple for safety.
    return tuple(HINT_EQUALITY_CASES)
