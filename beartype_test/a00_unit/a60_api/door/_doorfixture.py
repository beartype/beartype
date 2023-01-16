#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) API procedural
unit tests.**

This submodule unit tests the subset of the public API of the public
:mod:`beartype.door` subpackage that is procedural.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ FIXTURES ~ equality                }....................
@fixture(scope='session')
def door_cases_equality() -> 'Iterable[Tuple[object, object, bool]]':
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
    --------
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
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
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
        # ..................{ HINTS ~ argless : bare         }..................
        # PEP 484-compliant unsubscripted type hints, which are necessarily
        # equal to themselves.
        (tuple, Tuple, True),
        (list, list, True),
        (list, List, True),

        # ..................{ HINTS ~ arg : sequence         }..................
        # PEP 484-compliant sequence type hints.
        (list, List[Any], True),
        (tuple, Tuple[Any, ...], True),

        # ..................{ HINTS ~ arg : union            }..................
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
    ]

    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # both PEP 585 and 593...
    if IS_PYTHON_AT_LEAST_3_9:
        from beartype.typing import Annotated
        from collections.abc import (
            Awaitable as AwaitableABC,
            Sequence as SequenceABC,
        )

        # Append cases exercising version-specific relations.
        HINT_EQUALITY_CASES.extend((
            # PEP 585-compliant type hints.
            (tuple[str, ...], Tuple[str, ...], True),
            (list[str], List[str], True),
            (AwaitableABC[SequenceABC[int]], AwaitableABC[SequenceABC[int]], True),

            # PEP 593-compliant type hints.
            (Annotated[int, "hi"], Annotated[int, "hi"], True),
            (Annotated[int, "hi"], Annotated[int, "low"], False),
            (Annotated[int, "hi"], Annotated[int, "low"], False),
        ))

    # Return this mutable list coerced into an immutable tuple for safety.
    return tuple(HINT_EQUALITY_CASES)

# ....................{ FIXTURES ~ subhint                 }....................
@fixture(scope='session')
def door_cases_subhint() -> 'Iterable[Tuple[object, object, bool]]':
    '''
    Session-scoped fixture returning an iterable of **hint subhint cases**
    (i.e., 3-tuples ``(subhint, superhint, is_subhint)`` describing the subhint
    relations between two PEP-compliant type hints), efficiently cached across
    all tests requiring this fixture.

    This iterable is intentionally defined by the return of this fixture rather
    than as a global constant of this submodule. Why? Because the former safely
    defers all heavyweight imports required to define this iterable to the call
    of the first unit test requiring this fixture, whereas the latter unsafely
    performs those imports at pytest test collection time.

    Returns
    --------
    Iterable[Tuple[object, object, bool]]
        Iterable of one or more 3-tuples ``(subhint, superhint, is_subhint)``,
        where:

        * ``subhint`` is the PEP-compliant type hint to be passed as the first
          parameter to the :func:`beartype.door.is_subhint` tester.
        * ``superhint`` is the PEP-compliant type hint to be passed as the
          second parameter to the :func:`beartype.door.is_subhint` tester.
        * ``is_subhint`` is ``True`` only if that subhint is actually a subhint
          of that superhint according to that tester.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    import collections.abc
    import typing
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typevars
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_LEAST_3_9,
        IS_PYTHON_AT_LEAST_3_8,
    )
    from collections.abc import (
        Collection as CollectionABC,
        Sequence as SequenceABC,
    )

    # Intentionally import from "typing" rather than "beartype.typing" to
    # guarantee PEP 484-compliant type hints.
    from typing import (
        Any,
        Awaitable,
        ByteString,
        Callable,
        Collection,
        DefaultDict,
        Dict,
        Generic,
        Hashable,
        Iterable,
        List,
        Mapping,
        NamedTuple,
        NewType,
        Optional,
        Reversible,
        Sequence,
        Sized,
        Tuple,
        Type,
        TypeVar,
        Union,
    )

    # ..................{ NEWTYPES                           }..................
    NewStr = NewType("NewStr", str)

    # ..................{ TYPEVARS                           }..................
    T = TypeVar("T")
    SeqBoundTypeVar = TypeVar("SeqBoundTypeVar", bound=Sequence)
    IntStrConstrainedTypeVar = TypeVar("IntStrConstrainedTypeVar", int, str)

    # ..................{ CLASSES                            }..................
    class MuhThing:
        def muh_method(self):
            ...

    class MuhSubThing(MuhThing):
        ...

    class MuhNutherThing:
        def __len__(self) -> int:
            ...


    class MuhTuple(NamedTuple):
        thing_one: str
        thing_two: int


    class MuhGeneric(Generic[T]):
        ...

    # ..................{ LISTS                              }..................
    HINT_SUBHINT_CASES = [
        # ..................{ HINTS ~ argless : any          }..................
        # PEP 484-compliant catch-all type hint.
        (MuhThing, Any, True),
        (Tuple[object, ...], Any, True),
        (Union[int, MuhThing], Any, True),

        # Although *ALL* type hints are subhints of "Any", "Any" is only a
        # subhint of itself.
        (Any, Any, True),
        (Any, object, False),

        # ..................{ HINTS ~ argless : bare         }..................
        # PEP 484-compliant unsubscripted type hints, which are necessarily
        # subhints of themselves.
        (list, list, True),
        (list, List, True),

        # PEP 484-compliant unsubscripted sequence type hints.
        (Sequence, List, False),
        (Sequence, list, False),
        (List, Sequence, True),
        (list, Sequence, True),
        (list, SequenceABC, True),
        (list, CollectionABC, True),

        # ..................{ HINTS ~ argless : type         }..................
        # PEP 484-compliant argumentless abstract base classes (ABCs).
        (bytes, ByteString, True),
        (str, Hashable, True),
        (MuhNutherThing, Sized, True),
        (MuhTuple, tuple, True),  # not really types

        # PEP 484-compliant new type type hints.
        (NewStr, NewStr, True),
        (NewStr, int, False),
        (NewStr, str, True),
        (int, NewStr, False),
        (str, NewStr, False),  # NewType act like subtypes

        # ..................{ HINTS ~ argless : typevar      }..................
        # PEP 484-compliant type variables.
        (list, SeqBoundTypeVar, True),
        (SeqBoundTypeVar, list, False),
        (int, IntStrConstrainedTypeVar, True),
        (str, IntStrConstrainedTypeVar, True),
        (list, IntStrConstrainedTypeVar, False),
        (Union[int, str], IntStrConstrainedTypeVar, True),
        (Union[int, str, None], IntStrConstrainedTypeVar, False),
        (T, SeqBoundTypeVar, False),
        (SeqBoundTypeVar, T, True),
        (SeqBoundTypeVar, Any, True),
        (Any, T, True),  # Any is compatible with an unconstrained TypeVar
        (Any, SeqBoundTypeVar, False),  # but not vice versa

        # ..................{ HINTS ~ argless : number       }..................
        # Blame Guido.
        (bool, int, True),

        # PEP 484-compliant implicit numeric tower, which we explicitly and
        # intentionally do *NOT* comply with. Floats are not integers. Notably,
        # floats *CANNOT* losslessly represent many integers and are thus
        # incompatible in general.
        (float, int, False),
        (complex, int, False),
        (complex, float, False),
        (int, float, False),
        (float, complex, False),

        # ..................{ HINTS ~ arg : callable         }..................
        # PEP 484-compliant callable type hints.
        (Callable, Callable[..., Any], True),
        (Callable[[], int], Callable[..., Any], True),
        (Callable[[int, str], List[int]], Callable, True),
        (Callable[[int, str], List[int]], Callable, True),
        (
            Callable[[float, List[str]], int],
            Callable[[int, Sequence[str]], int],
            True,
        ),
        (Callable[[Sequence], int], Callable[[list], int], False),
        (Callable[[], int], Callable[..., None], False),
        (Callable[..., Any], Callable[..., None], False),
        (Callable[[float], None], Callable[[float, int], None], False),
        (Callable[[], int], Sequence[int], False),
        (Callable[[int, str], int], Callable[[int, str], Any], True),
        # (types.FunctionType, Callable, True),  # FIXME

        # ..................{ HINTS ~ arg : generic          }..................
        # PEP 484-compliant generics.
        (MuhGeneric[list], MuhGeneric[SeqBoundTypeVar], True),
        (MuhGeneric[str], MuhGeneric[SeqBoundTypeVar], True),
        (MuhGeneric[int], MuhGeneric[SeqBoundTypeVar], False),
        (MuhGeneric, MuhGeneric, True),
        (MuhGeneric[int], MuhGeneric, True),
        (MuhGeneric, MuhGeneric[int], False),
        (MuhGeneric[list], MuhGeneric[Sequence], True),
        (MuhGeneric[Sequence], MuhGeneric[list], False),
        (MuhGeneric[SeqBoundTypeVar], MuhGeneric, True),
        (MuhGeneric[int], MuhGeneric[SeqBoundTypeVar], False),

        # ..................{ HINTS ~ arg : mapping          }..................
        # PEP 484-compliant mapping type hints.
        (dict, Dict, True),
        (Dict[str, int], Dict, True),
        (dict, Dict[str, int], False),
        (
            DefaultDict[str, Sequence[int]],
            Mapping[Union[str, int], Iterable[Union[int, str]]],
            True,
        ),

        # ..................{ HINTS ~ arg : sequence         }..................
        # PEP 484-compliant sequence type hints.
        (List[int], List[int], True),
        (List[int], Sequence[int], True),
        (Sequence[int], Iterable[int], True),
        (Iterable[int], Sequence[int], False),
        (Sequence[int], Reversible[int], True),
        (Sequence[int], Reversible[str], False),
        (Collection[int], Sized, True),
        (List[int], List, True),  # if the super is un-subscripted, assume Any
        (List[int], List[Any], True),
        (Awaitable, Awaitable[str], False),
        (List[int], List[str], False),

        # PEP 484-compliant tuple type hints.
        (tuple, Tuple, True),
        (Tuple, Tuple, True),
        (tuple, Tuple[Any, ...], True),
        (tuple, Tuple[()], False),
        (Tuple[()], tuple, True),
        (Tuple[int, str], Tuple[int, str], True),
        (Tuple[int, str], Tuple[int, str, int], False),
        (Tuple[int, str], Tuple[int, Union[int, list]], False),
        (Tuple[Union[int, str], ...], Tuple[int, str], False),
        (Tuple[int, str], Tuple[str, ...], False),
        (Tuple[int, str], Tuple[Union[int, str], ...], True),
        (Tuple[Union[int, str], ...], Tuple[Union[int, str], ...], True),
        (Tuple[int], Dict[str, int], False),
        (Tuple[Any, ...], Tuple[str, int], False),

        # PEP 484-compliant nested sequence type hints.
        (List[int], Union[str, List[Union[int, str]]], True),

        # ..................{ HINTS ~ arg : subclass         }..................
        # PEP 484-compliant subclass type hints.
        (Type[int], Type[int], True),
        (Type[int], Type[str], False),
        (Type[MuhSubThing], Type[MuhThing], True),
        (Type[MuhThing], Type[MuhSubThing], False),
        (MuhThing, Type[MuhThing], False),

        # ..................{ HINTS ~ arg : union            }..................
        # PEP 484-compliant unions.
        (int, Union[int, str], True),
        (Union[int, str], Union[list, int, str], True),
        (Union[str, int], Union[int, str, list], True),  # order doesn't matter
        (Union[str, list], Union[str, int], False),
        (Union[int, str, list], list, False),
        (Union[int, str, list], Union[int, str], False),
        (int, Optional[int], True),
        (Optional[int], int, False),
        (list, Optional[Sequence], True),
    ]

    # ..................{ HINTS ~ abcs                       }..................
    # Smoke test for all "typing" ABCs. Smoke out those bugs, pytest!
    for cls_name in dir(collections.abc) + ['Deque']:
        if not cls_name.startswith("_"):
            typing_abc = getattr(typing, cls_name)

            #FIXME: This logic (probably) isn't behaving as expected under
            #Python >= 3.9, where unsubscripted "typing" factories (probably)
            #are *NOT* parametrized by type variables. Let's research this up!

            # Tuple of the zero or more type variables parametrizing this ABC.
            typing_abc_typevars = get_hint_pep_typevars(typing_abc)

            # Number of type variables parametrizing this ABC.
            nparams = len(typing_abc_typevars)

            if nparams:
                sub = typing_abc[(list,) * nparams]
                sup = typing_abc[(Sequence,) * nparams]
            else:
                sub = typing_abc
                sup = typing_abc

            HINT_SUBHINT_CASES.append((sub, sup, True))

    # ..................{ HINTS ~ version                    }..................
    # If the active Python interpreter targets Python >= 3.8 and thus supports
    # PEP 544 and 586...
    if IS_PYTHON_AT_LEAST_3_8:
        # Intentionally import from "beartype.typing" rather than "typing" to
        # guarantee PEP 544-compliant caching protocol type hints.
        from beartype.typing import (
            Literal,
            Protocol,
            TypedDict,
        )

        # Arbitrary caching @beartype protocol.
        class MuhThingP(Protocol):
            def muh_method(self):
                ...

        class MuhDict(TypedDict):
            thing_one: str
            thing_two: int

        # Append cases exercising version-specific relations.
        HINT_SUBHINT_CASES.extend((
            # PEP 544-compliant type hints.
            (MuhThing, MuhThingP, True),
            (MuhNutherThing, MuhThingP, False),
            (MuhThingP, MuhThing, False),

            # PEP 586-compliant type hints.
            (Literal[7], int, True),
            (Literal["a"], str, True),
            (Literal[7, 8, "3"], Union[int, str], True),
            (Literal[7, 8, "3"], Union[list, int], False),
            (int, Literal[7], False),
            (Literal[7, 8], Literal[7, 8, 9], True),

            # PEP 589-compliant type hints.
            (MuhDict, dict, True),
        ))

        # If the active Python interpreter targets Python >= 3.9 and thus
        # supports PEP 585 and 593...
        if IS_PYTHON_AT_LEAST_3_9:
            from beartype.typing import Annotated

            # Append cases exercising version-specific relations.
            HINT_SUBHINT_CASES.extend((
                # PEP 585-compliant type hints.
                (tuple, Tuple, True),
                (tuple[()], Tuple[()], True),

                # PEP 593-compliant type hints.
                (Annotated[int, "a note"], int, True),  # annotated is subtype of unannotated
                (int, Annotated[int, "a note"], False),  # but not vice versa
                (Annotated[list, True], Annotated[Sequence, True], True),
                (Annotated[list, False], Annotated[Sequence, True], False),
                (Annotated[list, 0, 0], Annotated[list, 0], False),  # must have same num args
                (Annotated[List[int], "metadata"], List[int], True),
            ))

    # Return this mutable list coerced into an immutable tuple for safety.
    return tuple(HINT_SUBHINT_CASES)
