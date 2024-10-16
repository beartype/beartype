#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) fixtures** (i.e.,
:mod:`pytest`-specific context managers passed as parameters to unit tests
exercising the :mod:`beartype.door.is_subhint` function).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def door_cases_is_subhint() -> 'Iterable[Tuple[object, object, bool]]':
    '''
    Session-scoped fixture returning an iterable of **type subhint cases**
    (i.e., 3-tuples ``(subhint, superhint, is_subhint)`` describing the subhint
    relations between two type hints), efficiently cached across all tests
    requiring this fixture.

    This iterable is intentionally defined by the return of this fixture rather
    than as a global constant of this submodule. Why? Because the former safely
    defers all heavyweight imports required to define this iterable to the call
    of the first unit test requiring this fixture, whereas the latter unsafely
    performs those imports at pytest test collection time.

    Returns
    -------
    Iterable[Tuple[object, object, bool]]
        Iterable of one or more 3-tuples ``(subhint, superhint, is_subhint)``,
        where:

        * ``subhint`` is the type hint to be passed as the first parameter to
          the :func:`beartype.door.is_subhint` tester.
        * ``superhint`` is the type hint to be passed as the second parameter to
          the :func:`beartype.door.is_subhint` tester.
        * ``is_subhint`` is :data:`True` only if that subhint is actually a
          subhint of that superhint according to that tester.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    import collections.abc
    import typing
    from beartype._data.hint.datahinttyping import S, T
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typevars
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from collections.abc import (
        Collection as CollectionABC,
        Sequence as SequenceABC,
    )

    # Intentionally import from "beartype.typing" rather than "typing" to
    # guarantee PEP 544-compliant caching protocol type hints.
    from beartype.typing import (
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
        Literal,
        Mapping,
        NamedTuple,
        NewType,
        Optional,
        Protocol,
        Reversible,
        Sequence,
        Sized,
        Tuple,
        Type,
        TypedDict,
        TypeVar,
        Union,
    )

    # ..................{ NEWTYPES                           }..................
    NewStr = NewType('NewStr', str)

    # ..................{ TYPEVARS                           }..................
    # Arbitrary constrained type variables.
    T_sequence = TypeVar('T_sequence', bound=SequenceABC)
    T_int_or_str = TypeVar('T_int_or_str', int, str)

    # ..................{ CLASSES                            }..................
    class MuhThing:
        def muh_method(self):
            pass

    class MuhSubThing(MuhThing):
        pass

    class MuhNutherThing:
        def __len__(self) -> int:
            pass


    class MuhDict(TypedDict):
        '''
        Arbitrary typed dictionary.
        '''

        thing_one: str
        thing_two: int


    class MuhThingP(Protocol):
        '''
        Arbitrary caching @beartype protocol.
        '''

        def muh_method(self):
            ...


    class MuhTuple(NamedTuple):
        '''
        Arbitrary named tuple.
        '''

        thing_one: str
        thing_two: int

    # ..................{ CLASSES ~ pep 484 : generic : one  }..................
    class GenericSuperT(Generic[T]):
        '''
        :pep:`484`-compliant generic superclass parametrized by one
        unconstrained type variable.
        '''

        pass


    class GenericSubT(GenericSuperT[T]):
        '''
        :pep:`484`-compliant generic subclass inheriting a :pep:`484`-compliant
        generic parametrized by one unconstrained type variable.
        '''

        pass

    # ..................{ CLASSES ~ pep 484 : generic : two  }..................
    class GenericSuperST(Generic[S, T]):
        '''
        :pep:`484`-compliant generic superclass parametrized by two
        unconstrained type variables.
        '''

        pass


    class GenericSubTInt(GenericSuperST[S, int]):
        '''
        :pep:`484`-compliant partially concrete generic subclass inheriting a
        :pep:`484`-compliant generic superclass subscripted first by an
        unconstrained type variable and then by the builtin :class:`int` type.
        '''

        pass


    class GenericSubIntInt(GenericSuperST[int, int]):
        '''
        :pep:`484`-compliant concrete generic subclass inheriting a
        :pep:`484`-compliant generic superclass subscripted twice by the
        builtin :class:`int` type.
        '''

        pass

    # ..................{ CLASSES ~ pep (484|585) : generic  }..................
    class SequenceSubT(Sequence[T]):
        '''
        :pep:`484`- or :pep:`585`-compliant generic subclass inheriting a
        :pep:`484`- or :pep:`585`-compliant ``Sequence[...]` type hint
        parametrized by one unconstrained type variable.
        '''

        pass

    # ..................{ LISTS ~ cases                      }..................
    # List of all hint subhint cases (i.e., 3-tuples "(subhint, superhint,
    # is_subhint)" describing the subhint relations between two PEP-compliant
    # type hints) to be returned by this fixture.
    HINT_SUBHINT_CASES = [
        # ..................{ PEP 484 ~ argless : any        }..................
        # PEP 484-compliant catch-all type hint.
        (MuhThing, Any, True),
        (Tuple[object, ...], Any, True),
        (Union[int, MuhThing], Any, True),

        # Although *ALL* type hints are subhints of "Any", "Any" is *ONLY* a
        # subhint of itself.
        (Any, Any, True),
        (Any, object, False),

        # ..................{ PEP 484 ~ argless : bare       }..................
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

        # ..................{ PEP 484 ~ argless : type       }..................
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

        # ..................{ PEP 484 ~ argless : typevar    }..................
        # PEP 484-compliant type variables.
        (list, T_sequence, True),
        (T_sequence, list, False),
        (int, T_int_or_str, True),
        (str, T_int_or_str, True),
        (list, T_int_or_str, False),
        (Union[int, str], T_int_or_str, True),
        (Union[int, str, None], T_int_or_str, False),
        (T, T_sequence, False),
        (T_sequence, T, True),
        (T_sequence, Any, True),
        (Any, T, True),  # Any is compatible with an unconstrained TypeVar
        (Any, T_sequence, False),  # but not vice versa

        # ..................{ PEP 484 ~ argless : number     }..................
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

        # ..................{ PEP 484 ~ generic              }..................
        # "typing.Generic"-centric tests.

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize changes below by replacing all references in
        # the first tuple item to "GenericSuperT" with "GenericSubT".
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # PEP 484-compliant generic superclasses parametrized by one
        # unconstrained type variables.
        (GenericSuperT, GenericSuperT, True),
        (GenericSuperT, GenericSuperT[int], False),
        (GenericSuperT[int], GenericSuperT, True),
        (GenericSuperT[int], GenericSuperT[T_sequence], False),
        (GenericSuperT[list], GenericSuperT[T_sequence], True),
        (GenericSuperT[list], GenericSuperT[Sequence], True),
        (GenericSuperT[str], GenericSuperT[T_sequence], True),
        (GenericSuperT[Sequence], GenericSuperT[list], False),
        (GenericSuperT[T_sequence], GenericSuperT, True),

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize changes above.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # PEP 484-compliant generic subclasses parametrized by one unconstrained
        # type variables.
        (GenericSubT, GenericSuperT, True),
        (GenericSubT, GenericSuperT[int], False),
        (GenericSubT[int], GenericSuperT, True),
        (GenericSubT[int], GenericSuperT[T_sequence], False),
        (GenericSubT[list], GenericSuperT[T_sequence], True),
        (GenericSubT[list], GenericSuperT[Sequence], True),
        (GenericSubT[str], GenericSuperT[T_sequence], True),
        (GenericSubT[Sequence], GenericSuperT[list], False),
        (GenericSubT[T_sequence], GenericSuperT, True),

        #FIXME: Uncomment after resolving open issue #271, please.
        # PEP 484-compliant generic subclasses parametrized by one unconstrained
        # type variables and one concrete type.
        (GenericSubTInt, GenericSuperST, True),
        (GenericSubTInt, GenericSuperST[int, int], False),
        (GenericSubTInt[int], GenericSuperST, True),

        #FIXME: Pickup here tomorrow, please. *sigh*
        # (GenericSubTInt[int], GenericSuperST[T_sequence], False),
        # (GenericSubTInt[list], GenericSuperST[T_sequence], True),
        # (GenericSubTInt[list], GenericSuperST[Sequence], True),
        # (GenericSubTInt[str], GenericSuperST[T_sequence], True),
        # (GenericSubTInt[Sequence], GenericSuperST[list], False),
        # (GenericSubTInt[T_sequence], GenericSuperST, True),

        # ..................{ PEP 484 ~ optional             }..................
        # "typing.Optional"-centric tests.

        # PEP 484-compliant optionals.
        (int, Optional[int], True),
        (Optional[int], int, False),
        (list, Optional[Sequence], True),

        # ..................{ PEP 484 ~ union                }..................
        # "typing.Union"-centric tests.

        # PEP 484-compliant unions.
        (int, Union[int, str], True),
        (Union[int, str], Union[list, int, str], True),
        (Union[str, int], Union[int, str, list], True),  # order doesn't matter
        (Union[str, list], Union[str, int], False),
        (Union[int, str, list], list, False),
        (Union[int, str, list], Union[int, str], False),

        # ..................{ PEP (484|585) ~ callable       }..................
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

        # ..................{ PEP (484|585) ~ generic        }..................
        # PEP 484- or 585-compliant generic subclasses inheriting PEP 484- or
        # 585-compliant type hints parametrized by one unconstrained type
        # variables.
        (SequenceSubT, Sequence[T], True),
        (SequenceSubT, Sequence[int], False),
        (SequenceSubT[int], Sequence[T], True),
        (SequenceSubT[int], Sequence[T_sequence], False),
        (SequenceSubT[list], Sequence[T_sequence], True),
        (SequenceSubT[list], Sequence[Sequence], True),
        (SequenceSubT[str], Sequence[T_sequence], True),
        (SequenceSubT[Sequence], Sequence[list], False),
        (SequenceSubT[T_sequence], Sequence[T], True),

        # ..................{ PEP (484|585) ~ mapping        }..................
        # PEP 484-compliant mapping type hints.
        (dict, Dict, True),
        (Dict[str, int], Dict, True),
        (dict, Dict[str, int], False),
        (
            DefaultDict[str, Sequence[int]],
            Mapping[Union[str, int], Iterable[Union[int, str]]],
            True,
        ),

        # ..................{ PEP (484|585) ~ sequence       }..................
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

        # ..................{ PEP (484|585) ~ subclass       }..................
        # PEP 484-compliant subclass type hints.
        (Type[int], Type[int], True),
        (Type[int], Type[str], False),
        (Type[MuhSubThing], Type[MuhThing], True),
        (Type[MuhThing], Type[MuhSubThing], False),
        (MuhThing, Type[MuhThing], False),

        # ..................{ PEP 544                        }..................
        # PEP 544-compliant type hints.
        (MuhThing, MuhThingP, True),
        (MuhNutherThing, MuhThingP, False),
        (MuhThingP, MuhThing, False),

        # ..................{ PEP 586                        }..................
        # PEP 586-compliant type hints.
        (Literal[7], int, True),
        (Literal["a"], str, True),
        (Literal[7, 8, "3"], Union[int, str], True),
        (Literal[7, 8, "3"], Union[list, int], False),
        (Literal[True], Union[Literal[True], Literal[False]], True),
        (Literal[7, 8], Literal[7, 8, 9], True),
        (int, Literal[7], False),
        (Union[Literal[True], Literal[False]], Literal[True], False),

        # ..................{ PEP 589                        }..................
        # PEP 589-compliant type hints.
        (MuhDict, dict, True),
    ]

    # ..................{ LISTS ~ typing                     }..................
    # List of the unqualified basenames of all standard ABCs published by
    # the standard "collections.abc" module, defined as...
    COLLECTIONS_ABC_BASENAMES = [
        # For the unqualified basename of each attribute defined by the standard
        # "collections.abc" module...
        COLLECTIONS_ABC_BASENAME
        for COLLECTIONS_ABC_BASENAME in dir(collections.abc)
        # If this basename is *NOT* prefixed by an underscore, this attribute is
        # public and thus an actual ABC. In this case, include this ABC.
        if not COLLECTIONS_ABC_BASENAME.startswith('_')
        # Else, this is an unrelated private attribute. In this case, silently
        # ignore this attribute and continue to the next.
    ]

    # List of the unqualified basenames of all standard abstract base classes
    # (ABCs) supported by the standard "typing" module, defined as the
    # concatenation of...
    TYPING_ABC_BASENAMES = (
        # List of the unqualified basenames of all standard ABCs published by
        # the standard "collections.abc" module *PLUS*...
        COLLECTIONS_ABC_BASENAMES +
        # List of the unqualified basenames of all ancillary ABCs *NOT*
        # published by the standard "collections.abc" module but nonetheless
        # supported by the standard "typing" module.
        ['Deque']
    )

    # ..................{ HINTS ~ abcs                       }..................
    # For the unqualified basename of each standard ABCs supported by the
    # standard "typing" module...
    #
    # Note this also constitutes a smoke test (i.e., high-level test validating
    # core functionality) for whether the DOOR API supports standard abstract
    # base classes (ABCs). Smoke out those API inconsistencies, pytest!
    for TYPING_ABC_BASENAME in TYPING_ABC_BASENAMES:
        #FIXME: This logic is likely to fail under a future Python release.
        # Type hint factory published by the "typing" module corresponding to
        # this ABC if any *OR* "None" otherwise (i.e., if "typing" publishes
        # *NO* such type hint factory).
        TypingABC = getattr(typing, TYPING_ABC_BASENAME, None)

        # If "typing" publishes *NO* such type hint factory, silently ignore
        # this ABC and continue to the next.
        if TypingABC is None:
            continue
        # Else, "typing" publishes this type hint factory.

        # Number of type variables parametrizing this ABC, defined as either...
        TYPING_ABC_TYPEVARS_LEN = (
            # If the active Python interpreter targets Python >= 3.9, a private
            # instance variable of this type hint factory yielding this
            # metadata. Under Python >= 3.9, unsubscripted type hint factories
            # are *NOT* parametrized by type variables.
            TypingABC._nparams
            if IS_PYTHON_AT_LEAST_3_9 else
            # Else, the active Python interpreter targets Python < 3.9. In this
            # case, the number of type variables directly parametrizing this
            # ABC.
            len(get_hint_pep_typevars(TypingABC))
        )

        # If this ABC is parametrized by one or more type variables, exercise
        # that this ABC subscripted by one or more arbitrary concrete types is a
        # non-trivial subhint of this same ABC subscripted by one or more
        # arbitrary different ABCs of those concrete types.
        if TYPING_ABC_TYPEVARS_LEN:
            subhint =   TypingABC[(list,)     * TYPING_ABC_TYPEVARS_LEN]
            superhint = TypingABC[(Sequence,) * TYPING_ABC_TYPEVARS_LEN]
        # Else, this ABC is parametrized by *NO* type variables. In this case,
        # fallback to exercising that this ABC is a trivial subhint of itself.
        else:
            subhint =   TypingABC
            superhint = TypingABC

        # Append a new hint subhint case exercising that this subhint is
        # actually a subhint of this superhint.
        HINT_SUBHINT_CASES.append((subhint, superhint, True))

    # ..................{ HINTS ~ version                    }..................
    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # both PEP 585 and 593...
    if IS_PYTHON_AT_LEAST_3_9:
        # Defer version-specific imports.
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
