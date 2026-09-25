#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) subhint fixtures**
(i.e., :mod:`pytest`-specific context managers passed as parameters to unit
tests validating the :func:`beartype.door.is_subhint` function and equivalent
:meth:`beartype.door.TypeHint.is_subhint` method).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def door_cases_subhint() -> 'tuple[tuple[object, object, bool]]':
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
    from abc import ABCMeta
    from beartype._cave._cavefast import HintPep604Type
    from beartype._util.cls.utilclstest import is_type_subclass_proper
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_LEAST_3_12,
        IS_PYTHON_AT_MOST_3_13,
        IS_PYTHON_AT_LEAST_3_14,
    )
    from beartype_test.a00_unit.data.pep.generic.data_pep484generic import (
        Pep484GenericIntUT,
        Pep484GenericSInt,
        Pep484GenericST,
        Pep484GenericSTToUU,
        # Pep484GenericTSubclass,
        Pep484GenericT,
        Pep484GenericTSubclass,
        Pep484GenericTSubclassSubclass,
        Pep484GenericTS,
    )
    from beartype_test.a00_unit.data.pep.generic.data_pep585generic import (
        Pep585SequenceTSubbed,
    )
    from beartype_test.a00_unit.data.pep.pep484.data_pep484 import (
        S,
        T,
        T_bound_sequence,
        T_constraint_int_or_str,
    )
    from collections.abc import (
        Collection as CollectionABC,
        Sequence as SequenceABC,
    )

    # Intentionally import from "beartype.typing" rather than "typing" to
    # guarantee PEP 544-compliant caching protocol type hints.
    from beartype.typing import (
        Annotated,
        Any,
        Awaitable,
        Callable,
        Collection,
        DefaultDict,
        Dict,
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
        Union,
    )

    # ..................{ NEWTYPES                           }..................
    NewStr = NewType('NewStr', str)

    # ..................{ CLASSES                            }..................
    #FIXME: Redundant type definitions. Just import the equivalent types we
    #already define from relevant submodules of the
    #"beartype_test.a00_util.data" subpackage (e.g., "data_type").

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

    # ..................{ LISTS ~ cases                      }..................
    # List of all hint subhint cases (i.e., 3-tuples "(subhint, superhint,
    # is_subhint)" describing the subhint relations between two PEP-compliant
    # type hints) to be returned by this fixture.
    HINT_SUBHINT_CASES = [
        # ..................{ NON-PEP ~ tuple                }..................
        #FIXME: Uncomment when we decide to try properly resolving the following
        #long-standing feature request:
        #    https://github.com/beartype/beartype/issues/369
        # # PEP-noncompliant tuple type union.
        # (str, (int, str, list), True),
        # (MuhTuple, (int, tuple), True),
        # (bytes, (int,), False),
        # (str, (), False),

        # ..................{ PEP 484 ~ argless : any        }..................
        # PEP 484-compliant catch-all type hint.
        (MuhThing, Any, True),
        (Tuple[object, ...], Any, True),
        (Union[int, MuhThing], Any, True),

        # "Any" is itself a subhint of *ALL* possible hints. Why? Because what
        # "Any" semantically means is "some type hint exists that satisfies this
        # relation." In the case of the subhint relation, some type hint
        # "some_hint" satisfying the relation "is_subhint(Any, hint)" for all
        # possible types "hint" is guaranteed to *ALWAYS* exist. Which
        # "some_hint" is that? Easy: "some_hint = hint". Any type is a trivial
        # subhint of itself.
        #
        # Look. Something can be both dumb and true. This is like that.
        (Any, Any, True),
        (Any, object, True),
        (Any, str, True),
        (Any, str | None, True),

        # "Any" is itself also a superhint of *ALL* possible hints for the same
        # exact reason as above. Why? Because some type hint "some_hint"
        # satisfying the relation "is_subhint(cls, Any)" for all possible types
        # "hints" is guaranteed to *ALWAYS* exist. Which "some_hint" is that?
        # Easy: "some_hint = hint". Any type is a trivial subhint of itself.
        (object, Any, True),
        (str, Any, True),
        (str | None, Any, True),

        # "Any" nested inside subscripted hints is assignable to concrete types.
        (List[Any], List[int], True),
        (List[Any], List[str], True),

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

        # ..................{ PEP 484 ~ argless : type       }..................
        # PEP 484-compliant argumentless abstract base classes (ABCs).
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

        # "Any" is a subhint of any type variable, including both unbound and
        # bound type variables.
        (Any, T, True),
        (Any, T_bound_sequence, True),

        # Any type variable is also a subhint of "Any", including both unbound
        # and bound type variables.
        (T, Any, True),
        (T_bound_sequence, Any, True),

        # Any type is a subhint of any unbound type variable. The converse is
        # *NOT* the case, of course.
        (list, T, True),
        (T, list, False),

        # Any type is a subhint of any type variable bound to any superclass of
        # that type. The converse is *NOT* the case.
        (list, T_bound_sequence, True),
        (T_bound_sequence, list, False),

        # Any type is a subhint of any type variable constrained to any
        # superclass of that type. The converse is *NOT* the case.
        (int, T_constraint_int_or_str, True),
        (T_constraint_int_or_str, int, False),
        (str, T_constraint_int_or_str, True),
        (T_constraint_int_or_str, str, False),

        # Any type is *NOT* a subhint of any type variable constrained to other
        # types unrelated to that first type.
        (list, T_constraint_int_or_str, False),

        # Any union comprising the same types to which a type variable is
        # constrained is a subhint of that type variable.
        (Union[int, str], T_constraint_int_or_str, True),

        # Any union comprising the same types to which a type variable is
        # constrained as well as one or more unrelated types is *NOT* a subhint
        # of that type variable.
        (Union[int, str, None], T_constraint_int_or_str, False),

        # An arbitrary bound type variable is a subhint of an arbitrary unbound
        # type variable. The converse is *NOT* the case.
        (T_bound_sequence, T, True),
        (T, T_bound_sequence, False),

        # ..................{ PEP 484 ~ generic              }..................
        # "typing.Generic"-centric tests.

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize changes below by replacing all references in
        # the first tuple item to "Pep484GenericT" with "Pep484GenericTSubclass".
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # PEP 484-compliant generic superclasses parametrized by one
        # unconstrained type variable.
        (Pep484GenericT, Pep484GenericT, True),
        (Pep484GenericT, Pep484GenericT[int], False),
        (Pep484GenericT[int], Pep484GenericT, True),
        (Pep484GenericT[int], Pep484GenericT[T_bound_sequence], False),
        (Pep484GenericT[list], Pep484GenericT[T_bound_sequence], True),
        (Pep484GenericT[list], Pep484GenericT[Sequence], True),
        (Pep484GenericT[str], Pep484GenericT[T_bound_sequence], True),
        (Pep484GenericT[Sequence], Pep484GenericT[list], False),
        (Pep484GenericT[T_bound_sequence], Pep484GenericT, True),

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize changes above.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # PEP 484-compliant generic subclasses parametrized by one unconstrained
        # type variable.
        (Pep484GenericTSubclass, Pep484GenericT, True),
        (Pep484GenericTSubclass, Pep484GenericT[int], False),
        (Pep484GenericTSubclass[int], Pep484GenericT, True),
        (Pep484GenericTSubclass[int], Pep484GenericT[T_bound_sequence], False),
        (Pep484GenericTSubclass[list], Pep484GenericT[T_bound_sequence], True),
        (Pep484GenericTSubclass[list], Pep484GenericT[Sequence], True),
        (Pep484GenericTSubclass[str], Pep484GenericT[T_bound_sequence], True),
        (Pep484GenericTSubclass[Sequence], Pep484GenericT[list], False),
        (Pep484GenericTSubclass[T_bound_sequence], Pep484GenericT, True),
        (Pep484GenericTSubclassSubclass[T], Pep484GenericT[str], False),
        (Pep484GenericTSubclassSubclass[str], Pep484GenericT[str], True),
        (
            Pep484GenericTSubclassSubclass[str],
            Pep484GenericTSubclass[str],
            True,
        ),

        # PEP 484-compliant generic subclasses parametrized by one unconstrained
        # type variables and one concrete type.
        (Pep484GenericSInt, Pep484GenericST, True),
        (Pep484GenericSInt, Pep484GenericST[int, int], False),
        (Pep484GenericSInt[int], Pep484GenericST, True),
        (Pep484GenericSInt[int], Pep484GenericST[S, T_bound_sequence], False),
        (Pep484GenericSInt[list], Pep484GenericST[T_bound_sequence, object], True),
        (Pep484GenericSInt[list], Pep484GenericST[Sequence, Any], True),
        (Pep484GenericSInt[str], Pep484GenericST[T_bound_sequence, S], True),
        (Pep484GenericSInt[Sequence], Pep484GenericST[list, object], False),
        (Pep484GenericSInt[T_bound_sequence], Pep484GenericST, True),

        # PEP 484-compliant generic subclasses subclassing exactly two generic
        # superclasses such that:
        # * The first such generic superclass is subscripted by a subset of the
        #   type variables subscripting the second such generic superclass.
        # * Type variables are specified in a differing order between those two
        #   generic superclass subscriptions.
        (Pep484GenericTS, Pep484GenericST, True),
        (Pep484GenericTS[str, int], Pep484GenericST, True),
        (Pep484GenericTS[str, int], Pep484GenericST[int, str], True),
        (Pep484GenericTS[str, int], Pep484GenericST[str, int], False),
        (Pep484GenericIntUT, Pep484GenericST, True),
        (Pep484GenericIntUT[str, int], Pep484GenericST, True),
        (Pep484GenericIntUT[str, float], Pep484GenericST[int, float], True),
        (Pep484GenericIntUT[str, float], Pep484GenericST[float, int], False),
        (Pep484GenericSTToUU, Pep484GenericST, True),
        (Pep484GenericSTToUU[str, int, float], Pep484GenericST, True),
        (
            Pep484GenericSTToUU[str, int, float],
            Pep484GenericST[str, float],
            True,
        ),
        (
            Pep484GenericSTToUU[str, int, float],
            Pep484GenericST[str, int],
            False,
        ),
        (
            Pep484GenericSTToUU[str, int, float],
            Pep484GenericST[str, str],
            False,
        ),

        # ..................{ PEP 484 ~ optional             }..................
        # "typing.Optional"-centric tests.

        # PEP 484-compliant optionals.
        (int, Optional[int], True),
        (Optional[int], int, False),
        (list, Optional[Sequence], True),

        # ..................{ PEP (484|585) ~ bare           }..................
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
        (Pep585SequenceTSubbed, Sequence[T], True),
        (Pep585SequenceTSubbed, Sequence[int], False),
        (Pep585SequenceTSubbed[int], Sequence[T], True),
        (Pep585SequenceTSubbed[int], Sequence[T_bound_sequence], False),
        (Pep585SequenceTSubbed[list], Sequence[T_bound_sequence], True),
        (Pep585SequenceTSubbed[list], Sequence[Sequence], True),
        (Pep585SequenceTSubbed[str], Sequence[T_bound_sequence], True),
        (Pep585SequenceTSubbed[Sequence], Sequence[list], False),
        (Pep585SequenceTSubbed[T_bound_sequence], Sequence[T], True),

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

        # ..................{ PEP (484|604) ~ union          }..................
        # PEP 484- and 604-compliant union type hints.

        # PEP 484-compliant unions.
        (int, Union[int, str], True),
        (Union[int, str], Union[list, int, str], True),
        (Union[str, int], Union[int, str, list], True),  # order doesn't matter
        (Union[str, list], Union[str, int], False),
        (Union[int, str, list], list, False),
        (Union[int, str, list], Union[int, str], False),

        # PEP 604-compliant unions.
        (int | str, int | Any, True),
        (int | Any, int | str, True),

        # Types of PEP 484- and 604-compliant unsubscripted union factories
        # (i.e., "typing.Union" and "types.UnionType"). These cases implicitly
        # validate that these factories are accepted as valid types, guarding
        # against regressions. Previously, both of these factories erroneously
        # induced non-human-readable exceptions.
        #
        # Note that both cases conditionally evaluate to:
        # * If the active Python interpreter targets Python <= 3.13, false. Why?
        #   Python <= 3.13 differentiated the types of PEP 484-compliant old
        #   unions from the types of PEP 604-compliant new unions.
        # * If the active Python interpreter targets Python >= 3.14, true. Why?
        #   Python >= 3.14 unified union types such that the type of *ALL*
        #   unions is merely "Union" and "Union is HintPep604Type".
        (type(int | str), type[Union], IS_PYTHON_AT_LEAST_3_14),
        (type[int | str], type[HintPep604Type], IS_PYTHON_AT_LEAST_3_14),

        # ..................{ PEP 544                        }..................
        # PEP 544-compliant type hints.
        (MuhThing, MuhThingP, True),
        (MuhNutherThing, MuhThingP, False),
        (MuhThingP, MuhThing, False),

        # ..................{ PEP 585                        }..................
        # PEP 585-compliant type hints.
        (tuple, Tuple, True),
        (tuple[()], Tuple[()], True),

        # ..................{ PEP 586                        }..................
        # PEP 586-compliant type hints.

        # PEP 586-compliant literal hints are subhints of larger PEP
        # 586-compliant literal hints subscripted by a superset of the same
        # child hints subscripting the former. The converse is *NOT* true.
        (Literal[7, 8], Literal[7, 8, 9], True),
        (Literal[7, 8, 9], Literal[7, 8], False),

        # PEP 586-compliant literal hints are subhints of the types of the child
        # hints subscripting those literal hints. The converse is *NOT* true.
        # See the LiteralTypeHint._is_subhint() method for further discussion.
        (Literal[7], int, True),
        (int, Literal[7], False),
        (Literal['Gainst the hot season'], str, True),
        (str, Literal['Gainst the hot season'], False),

        (Literal[7, 8, '3'], Union[int, str], True),
        (Literal[7, 8, '3'], Union[list, int], False),

        # PEP 586-compliant hints subscripted by one child hint are subhints of
        # PEP 484-compliant unions subscripted by that some PEP 586-compliant
        # hints and arbitrary other child hints. The converse is *NOT* true.
        (Literal[True], Union[Literal[True], Literal[False]], True),
        (Union[Literal[True], Literal[False]], Literal[True], False),

        # PEP 586-compliant hints subscripted by two or more child hints are
        # subhints of PEP 604-compliant unions subscripted by PEP 586-compliant
        # hints subscripted by each of those child hints individually (and
        # arbitrary other child hints). Again, the converse is *NOT* true.
        (Literal[1, 2], Literal[1] | Literal[2] | Literal[3], True,),
        (Literal[1] | Literal[2] | Literal[3], Literal[1, 2], False,),

        # ..................{ PEP 589                        }..................
        # PEP 589-compliant type hints.
        (MuhDict, dict, True),

        # ..................{ PEP 593                        }..................
        # PEP 593-compliant type hints.

        # Annotated[{type}, ...] <= {type}.
        (Annotated[int, 'a note'], int, True),

        # {type} > Annotated[{type}, ...].
        (int, Annotated[int, 'a note'], False),

        (Annotated[list, True], Annotated[Sequence, True], True),
        (Annotated[list, False], Annotated[Sequence, True], False),
        (Annotated[list, 0, 0], Annotated[list, 0], False),  # must have same num args
        (Annotated[List[int], 'metadata'], List[int], True),
    ]

    # ..................{ LISTS ~ cases : version            }..................
    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 612-compliant type parameter declaration syntax (which raises a
    # "SyntaxError" under older Python interpreters)...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.generic.data_pep695generic import (
            Pep695GenericST,
            Pep695GenericSTToUU,
        )

        # Extend this list with...
        HINT_SUBHINT_CASES.extend((
            # ..................{ PEP 695 ~ generic          }..................
            # "typing.Generic"-centric tests.

            # PEP 695-compliant generic subclasses subclassing exactly two
            # generic superclasses such that:
            # * The first such generic superclass is subscripted by a subset of
            #   the type variables subscripting the second such generic
            #   superclass.
            # * Type variables are specified in a differing order between those
            #   two generic superclass subscriptions.
            (Pep695GenericSTToUU, Pep695GenericST, True),
            (Pep695GenericSTToUU[str, int, float], Pep695GenericST, True),
            (
                Pep695GenericSTToUU[str, int, float],
                Pep695GenericST[str, float],
                True,
            ),
            (
                Pep695GenericSTToUU[str, int, float],
                Pep695GenericST[str, int],
                False,
            ),
            (
                Pep695GenericSTToUU[str, int, float],
                Pep695GenericST[str, str],
                False,
            ),
        ))
    # Else, the active Python interpreter targets Python < 3.12 and thus fails
    # to support PEP 612-compliant type parameter declaration syntax.

    # If the active Python interpreter targets Python <= 3.13...
    if IS_PYTHON_AT_MOST_3_13:
        # "collections.abc.ByteString", "typing.ByteString", and therefore
        # "beartype.typing.ByteString" itself no longer exist under Python 3.14.
        from beartype.typing import ByteString

        # Extend this list with...
        HINT_SUBHINT_CASES.extend((
            # ..................{ PEP 484 ~ argless : type   }..................
            # PEP 484-compliant argumentless abstract base classes (ABCs).
            (bytes, ByteString, True),
        ))

    # ..................{ LISTS ~ typing                     }..................
    # List of the unqualified basenames of all standard ABCs published by
    # the standard "collections.abc" module, initialized to the empty list.
    COLLECTIONS_ABC_BASENAMES = []

    #FIXME: Call the higher-level and *SIGNIFICANTLY* safer
    #get_object_attr_name_to_value() getter instead of manually
    #iterating over "__dict__.items()", please. *sigh*
    # For the unqualified basename of each attribute and that attribute defined
    # by the standard "collections.abc" submodule...
    for collections_abc_basename, collections_abc in (
        collections.abc.__dict__.items()):
        # If this attribute is a public ABC, include this ABC, where public ABCs
        # are detected as...
        if (
            # The unqualified basename of this attribute is not prefixed by an
            # underscore (and is thus public) *AND*...
            not collections_abc_basename.startswith('_') and
            # This attribute is an ABC but *NOT* the semantically meaningless
            # "abc.ABCMeta" superclass itself.
            is_type_subclass_proper(collections_abc, ABCMeta)
        ):
            COLLECTIONS_ABC_BASENAMES.append(collections_abc_basename)
        # Else, this is an unrelated attribute. In this case, silently ignore
        # this attribute and continue to the next.

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
        ['Deque',]
    )
    # print(f'TYPING_ABC_BASENAMES: {TYPING_ABC_BASENAMES}')

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
        typing_abc = getattr(typing, TYPING_ABC_BASENAME, None)

        # If "typing" publishes *NO* such type hint factory, silently ignore
        # this ABC and continue to the next.
        if typing_abc is None:
            continue
        # Else, "typing" publishes this type hint factory.

        # Number of type variables parametrizing this ABC, defined as a private
        # instance variable of this type hint factory yielding this metadata.
        # Under Python >= 3.9, unsubscripted type hint factories are *NOT*
        # parametrized by type variables.
        typing_abc_typevars_len = typing_abc._nparams

        # If this ABC is parametrized by one or more type variables, exercise
        # that this ABC subscripted by one or more arbitrary concrete types is a
        # non-trivial subhint of this same ABC subscripted by one or more
        # arbitrary different ABCs of those concrete types.
        if typing_abc_typevars_len:
            subhint =   typing_abc[(list,)     * typing_abc_typevars_len]
            superhint = typing_abc[(Sequence,) * typing_abc_typevars_len]
        # Else, this ABC is parametrized by *NO* type variables. In this case,
        # fallback to exercising that this ABC is a trivial subhint of itself.
        else:
            subhint =   typing_abc
            superhint = typing_abc

        # Append a new hint subhint case exercising that this subhint is
        # actually a subhint of this superhint.
        HINT_SUBHINT_CASES.append((subhint, superhint, True))

    # ..................{ PEP 695                            }..................
    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695-compliant type aliases...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
            AliasDoorInt,
            AliasDoorListInt,
            AliasDoorListSetT,
            AliasDoorStr,
            AliasDoorUnion,
        )

        # Append PEP 695-specific subhint cases. Since PEP 695 defines type
        # aliases to be *TRANSPARENT*, an alias is a subhint of exactly those
        # hints the aliased hint is a subhint of -- and vice versa.
        HINT_SUBHINT_CASES.extend((
            # An alias is a subhint of the hint aliased by that alias...
            (AliasDoorInt, int, True),
            # ...and a superhint of it, too.
            (int, AliasDoorInt, True),

            # Subhint relations propagate through an alias in both directions.
            (bool, AliasDoorInt, True),
            (AliasDoorInt, object, True),
            (AliasDoorInt, AliasDoorUnion, True),
            (AliasDoorUnion, AliasDoorInt, False),

            # Aliases of unrelated hints are unrelated.
            (AliasDoorInt, AliasDoorStr, False),

            # Subscripted aliases obey the variance of the aliased hint.
            (list[int], AliasDoorListSetT[int], True),
            (AliasDoorListSetT[int], list[int] | set[int], True),

            # Aliases nested as child hints of parent hints are transparent.
            (list[AliasDoorInt], list[object], True),

            # Aliases subscripting unions are transparent as union branches.
            (list[int], AliasDoorListInt | str, True),
            (AliasDoorListInt, list[int] | str, True),
        ))
    # Else, this interpreter fails to support PEP 695.

    # ..................{ RETURN                             }..................
    # Return this mutable list coerced into an immutable tuple for safety.
    return tuple(HINT_SUBHINT_CASES)
