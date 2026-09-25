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
    Iterable[Pep484Tuple[object, object, bool]]
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
    from beartype._cave._cavefast import NoneType
    from beartype_test.a00_unit.data.pep.generic.data_pep484generic import (
        Pep484GenericT)
    from collections.abc import (
        Awaitable as Pep585Awaitable,
        Callable as Pep585Callable,
        Sequence as Pep585Sequence,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from numbers import Number

    # Intentionally import from "typing" rather than "beartype.typing" to
    # guarantee PEP 484-compliant type hints.
    from typing import (
        Annotated,
        Any,
        Literal,
        Union,
        List as Pep484List,
        Tuple as Pep484Tuple,
    )

    # ..................{ LISTS                              }..................
    HINT_EQUALITY_CASES = [
        # ..................{ NON-PEP                        }..................
        # PEP-noncompliant types are obviously equal to themselves. They better!
        (list, list, True),

        # ..................{ PEP 484                        }..................
        # PEP 484-compliant unsubscripted type hint factories are equal to the
        # PEP-noncompliant types underlying those factories.
        (Pep484List, list, True),
        (Pep484Tuple, tuple, True),

        # ..................{ PEP 484 ~ any                  }..................
        # PEP 484-compliant "Any" singleton is equal to itself. We swear.
        (Any, Any, True),

        # PEP 484-compliant "Any" singleton is technically unequal (despite
        # being semantically equal) to *ANY* other valid type hint. See the
        # AnyTypeHint._is_equal() implementation for further commentary.
        (Any, str, False),
        (Any, list[str], False),

        # ..................{ PEP 484 ~ none                 }..................
        # PEP 484-compliant "None" singleton is equal to itself, of course.
        (None, None, True),

        # PEP 484-compliant "None" singleton is equal to its type, as the former
        # trivially reduces to the latter under PEP 484 semantics.
        (None, NoneType, True),

        # ..................{ PEP (484|585)                  }..................
        # PEP 585-compliant unsubscripted hint factories are equal to equivalent
        # PEP 484-compliant hint factories subscripted by the PEP 484-compliant
        # "Any" singleton.
        (list, Pep484List[Any], True),
        (tuple, Pep484Tuple[Any, ...], True),

        # PEP 585-compliant hints subscripted by the PEP 484-compliant "Any"
        # singleton are unequal to to other such hints *NOT* also subscripted by
        # "Any" (in the same exact child hint position).
        (tuple[int, Any], tuple[int, Any], True),
        (tuple[int, Any], tuple[int, str], False),

        # PEP 484- and 585-compliant hints that differ only in their factory are
        # equal.
        (list[str], Pep484List[str], True),
        (tuple[str, ...], Pep484Tuple[str, ...], True),

        # PEP 585-compliant deeply nested hints are equal to themselves. *sigh*
        (
            Pep585Awaitable[Pep585Sequence[int]],
            Pep585Awaitable[Pep585Sequence[int]],
            True,
        ),

        # PEP 585-compliant unsubscripted callable hint is equal to a
        # PEP 585-compliant callable hint subscripted by ignorable child hints.
        (Pep585Callable, Pep585Callable[..., Any], True),

        # ..................{ PEP (484|585) ~ generic        }..................
        # PEP 484-compliant unsubscripted generics parametrized by one
        # PEP 484-compliant type variable are equal to those same generics
        # subscripted by the PEP 484-compliant "Any" singleton.
        (Pep484GenericT, Pep484GenericT[Any], True),

        # ..................{ PEP (484|604) ~ union          }..................
        # PEP 484-compliant union type hints.
        (Union[int, str], Union[str, list], False),
        (Union[Number, int], Union[Number, float], True),

        # Unions (and thus equality between unions) ignores order.
        (Union[int, str], Union[str, int], True),

        # Unions (and thus equality between unions) ignore subhint-redundant
        # child hints (i.e., child hints that are subhints of other child hints
        # subscripting a union).
        #
        # Note that this pair of cases tests numerous edge cases, including:
        # * Equality comparison of non-unions against unions. Although
        #   "Union[int]" superficially appears to be a union, Python reduces
        #   "Union[int]" to simply "int" at runtime.
        (Union[bool, int], Union[int], True),
        (Union[int], Union[bool, int], True),

        # PEP 604-compliant union type hints.
        #
        # Unions subscripted by PEP 484-compliant "Any" singleton semantically
        # reduce to simply "Any" and are thus technically unequal (despite being
        # semantically equal) to other unions *NOT* also subscripted by "Any".
        # See the AnyTypeHint._is_equal() implementation for further commentary.
        (Any | int, Any, False),
        (int | Any, Any, False),  # <-- intentionally exercises awful edge case
        (Any | int, int, False),
        (Any | int, Any | int, True),
        (Any | int, str | int, False),

        # ..................{ PEP 586                        }..................
        # PEP 586-compliant "typing.Literal" hints.

        # PEP 586-compliant hints are equal to themselves. *sigh*
        (Literal[1, 2], Literal[1, 2], True,),

        # PEP 586-compliant hints subscripted by two or more child hints are
        # equal to PEP 604-compliant unions subscripted by PEP 586-compliant
        # hints subscripted by each of those child hints individually. Brutal!
        (Literal[1, 2], Literal[1] | Literal[2], True,),

        # ..................{ PEP 593                        }..................
        # PEP 593-compliant "typing.Annotated" hints.

        # PEP 593-compliant hints are equal to themselves. *sigh*
        (
            Annotated[int, 'For simple sheep'],
            Annotated[int, 'For simple sheep'],
            True,
        ),

        # PEP 593-compliant hints subscripted by the same metahint but differing
        # metadata are unequal.
        (
            Annotated[int, 'and such'],
            Annotated[int, 'are daffodils'],
            False,
        ),

    ]

    # ..................{ PEP 695                            }..................
    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695-compliant type aliases...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
            AliasDoorInt,
            AliasDoorIntNested,
            AliasDoorListInt,
            AliasDoorListSetT,
            AliasDoorStr,
            AliasDoorUnion,
        )

        # Append PEP 695-specific equality cases. PEP 695 defines type aliases
        # to be *TRANSPARENT*: an alias conveys exactly the semantics of the
        # hint aliased by that alias and *NO* semantics of its own.
        HINT_EQUALITY_CASES.extend((
            # An alias is equal to the hint aliased by that alias...
            (AliasDoorInt, int, True),
            # ...in either direction.
            (int, AliasDoorInt, True),

            # An alias of an alias transitively reduces to the same hint.
            (AliasDoorIntNested, int, True),
            (AliasDoorIntNested, AliasDoorInt, True),

            # Aliases of differing hints are unequal.
            (AliasDoorInt, AliasDoorStr, False),
            (AliasDoorInt, str, False),

            # An alias of a union is equal to that union.
            (AliasDoorUnion, int | float, True),
            (AliasDoorUnion, int | str, False),

            # A subscripted alias is equal to the hint aliased by that alias
            # with its type parameters replaced by those child hints.
            (AliasDoorListSetT[int], list[int] | set[int], True),

            # Subscripting an alias by differing child hints differs.
            (AliasDoorListSetT[int], AliasDoorListSetT[str], False),

            # Aliases nested as child hints of parent hints are transparent.
            (list[AliasDoorInt], list[int], True),
            (dict[AliasDoorInt, AliasDoorStr], dict[int, str], True),
            (AliasDoorInt | bytes, int | bytes, True),

            # An alias is equal to the non-union subscripted hint it aliases,
            # regardless of which operand the alias is.
            (list[int], AliasDoorListInt, True),

            # Aliases subscripting unions are transparent as union branches.
            (AliasDoorListInt | str, list[int] | str, True),

            # An alias of a union subscripting another union is flattened.
            (AliasDoorUnion | bytes, int | float | bytes, True),
        ))
    # Else, this interpreter fails to support PEP 695.

    # ..................{ RETURN                             }..................
    # Return this mutable list coerced into an immutable tuple for safety.
    return tuple(HINT_EQUALITY_CASES)
