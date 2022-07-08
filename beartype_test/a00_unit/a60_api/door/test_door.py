#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Orientedly Recursive (DOOR) API unit tests.**

This submodule unit tests the public API of the public
:mod:`beartype.door` subpackage.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TODO                               }....................

# ....................{ IMPORTS                            }....................
from beartype_test.util.mark.pytskip import skip
from pytest import fixture

#FIXME: Isolate to tests below, please.
# from beartype.door._doorcls import (
#     _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1,
#     _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2,
#     _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3,
#     TypeHint,
#     is_subhint,
# )
# from beartype.roar import BeartypeMathException

# ....................{ FIXTURES                           }....................
#FIXME: Consider shifting into a new "conftest" plugin of this subpackage.
@fixture(scope='session')
def subhint_superhint_is_cases() -> 'Iterable[Tuple[object, object, bool]]':
    '''
    Session-scoped fixture returning an iterable efficiently cached across *all*
    tests requiring this fixture.

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
    from beartype import typing as bt
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_LEAST_3_9,
        IS_PYTHON_AT_LEAST_3_8,
    )
    from collections import abc
    import typing as t

    # # ..................{ TYPEVARS                           }..................
    # T = t.TypeVar('T')
    # P = t.ParamSpec('P')

    # ..................{ CLASSES                            }..................
    class MuhThing:
        def muh_method(self):
            ...


    class MuhNutherThing:
        def __len__(self) -> int:
            ...


    class MuhDict(t.TypedDict):
        thing_one: str
        thing_two: int


    class MuhTuple(t.NamedTuple):
        thing_one: str
        thing_two: int

    # ..................{ LISTS                              }..................
    SUBHINT_SUPERHINT_IS_CASES = [
        # things are subclasses of themselves
        (list, list, True),
        (list, t.List, True),
        # a few standard, ordered types
        (t.Sequence, t.List, False),
        (t.Sequence, list, False),
        (t.List, t.Sequence, True),
        (list, t.Sequence, True),
        (list, abc.Sequence, True),
        (list, abc.Collection, True),
        # a few types that take no params
        (str, t.Hashable, True),
        (MuhNutherThing, t.Sized, True),
        (bytes, t.ByteString, True),
        # everything is a subtype of Any
        (t.Any, t.Any, True),
        (MuhThing, t.Any, True),
        (t.Union[int, MuhThing], t.Any, True),
        # numeric tower
        (float, int, True),
        (complex, int, True),
        (complex, float, True),
        (int, float, False),
        (float, complex, False),
        # subscripted types
        # lists,
        (t.List[int], t.List[int], True),
        (t.List[int], t.Sequence[int], True),
        (t.Sequence[int], t.Iterable[int], True),
        (t.Iterable[int], t.Sequence[int], False),
        (t.Sequence[int], t.Reversible[int], True),
        (t.Sequence[int], t.Reversible[str], False),
        (t.Collection[int], t.Sized, True),
        (t.List[int], t.List, True),  # if the super is un-subscripted, assume t.Any
        (t.List[int], t.List[t.Any], True),
        (t.Awaitable, t.Awaitable[str], False),
        (t.List[int], t.List[str], False),
        # maps
        (dict, t.Dict, True),
        (t.Dict[str, int], t.Dict, True),
        (dict, t.Dict[str, int], False),
        (
            t.DefaultDict[str, t.Sequence[int]],
            t.Mapping[t.Union[str, int], t.Iterable[t.Union[int, str]]],
            True,
        ),
        # callable
        (t.Callable, t.Callable[..., t.Any], True),
        (t.Callable[[], int], t.Callable[..., t.Any], True),
        (t.Callable[[int, str], t.List[int]], t.Callable, True),
        (t.Callable[[int, str], t.List[int]], t.Callable, True),
        (
            t.Callable[[float, t.List[str]], int],
            t.Callable[[int, t.Sequence[str]], int],
            True,
        ),
        (t.Callable[[t.Sequence], int], t.Callable[[list], int], False),
        (t.Callable[[], int], t.Callable[..., None], False),
        (t.Callable[..., t.Any], t.Callable[..., None], False),
        (t.Callable[[float], None], t.Callable[[float, int], None], False),
        (t.Callable[[], int], t.Sequence[int], False),
        (t.Callable[[int, str], int], t.Callable[[int, str], t.Any], True),
        # (types.FunctionType, t.Callable, True),  # FIXME
        # tuples
        (tuple, t.Tuple, True),
        (t.Tuple, t.Tuple, True),
        (bt.Tuple, t.Tuple, True),
        (tuple, t.Tuple[t.Any, ...], True),
        (tuple, t.Tuple[()], False),
        (bt.Tuple[()], t.Tuple[()], True),
        (t.Tuple[()], tuple, True),
        (t.Tuple[int, str], t.Tuple[int, str], True),
        (t.Tuple[int, str], t.Tuple[int, str, int], False),
        (t.Tuple[int, str], t.Tuple[int, t.Union[int, list]], False),
        (t.Tuple[t.Union[int, str], ...], t.Tuple[int, str], False),
        (t.Tuple[int, str], t.Tuple[str, ...], False),
        (t.Tuple[int, str], t.Tuple[t.Union[int, str], ...], True),
        (t.Tuple[t.Union[int, str], ...], t.Tuple[t.Union[int, str], ...], True),
        (t.Tuple[int], t.Dict[str, int], False),
        (t.Tuple[t.Any, ...], t.Tuple[str, int], False),
        # unions
        (int, t.Union[int, str], True),
        (t.Union[int, str], t.Union[list, int, str], True),
        (t.Union[str, int], t.Union[int, str, list], True),  # order doesn't matter
        (t.Union[str, list], t.Union[str, int], False),
        (t.Union[int, str, list], list, False),
        (t.Union[int, str, list], t.Union[int, str], False),
        (int, t.Optional[int], True),
        (t.Optional[int], int, False),
        (list, t.Optional[t.Sequence], True),
        # literals
        (t.Literal[1], int, True),
        (t.Literal["a"], str, True),
        (t.Literal[1, 2, "3"], t.Union[int, str], True),
        (t.Literal[1, 2, "3"], t.Union[list, int], False),
        (int, t.Literal[1], False),
        (t.Literal[1, 2], t.Literal[1, 2, 3], True),
        # moar nestz
        (t.List[int], t.Union[str, t.List[t.Union[int, str]]], True),
        # not really types:
        (MuhDict, dict, True),
        (MuhTuple, tuple, True),
    ]

    # If the active Python interpreter targets Python >= 3.8 and thus supports
    # PEP 544...
    if IS_PYTHON_AT_LEAST_3_8:
        # Arbitrary caching @beartype protocol.
        class MuhThingP(bt.Protocol):
            def muh_method(self):
                ...

        # Append cases exercising subhint protocol relations.
        SUBHINT_SUPERHINT_IS_CASES.extend((
            (MuhThing, MuhThingP, True),
            (MuhNutherThing, MuhThingP, False),
            (MuhThingP, MuhThing, False),
        ))

        # If the active Python interpreter targets Python >= 3.9 and thus
        # supports PEP 593...
        if IS_PYTHON_AT_LEAST_3_9:
            # Append cases exercising subhint annotated relations.
            SUBHINT_SUPERHINT_IS_CASES.extend((
                (t.Annotated[int, "a note"], int, True),  # annotated is subtype of unannotated
                (int, t.Annotated[int, "a note"], False),  # but not vice versa
                (t.Annotated[list, True], t.Annotated[t.Sequence, True], True),
                (t.Annotated[list, False], t.Annotated[t.Sequence, True], False),
                (t.Annotated[list, 0, 0], t.Annotated[list, 0], False),  # must have same num args
                (t.Annotated[t.List[int], "metadata"], t.List[int], True),
            ))

    # Return this mutable list coerced into an immutable tuple for safety.
    return tuple(SUBHINT_SUPERHINT_IS_CASES)

# ....................{ TESTS ~ testers                    }....................
#FIXME: Resolve, please. It looks like Python 3.7 and 3.8 are failing hard.
@skip('Currently known to be broken. *sigh*')
def test_is_subhint(
    subhint_superhint_is_cases: 'Iterable[Tuple[object, object, bool]]'):
    '''
    Test the :func:`beartype.door.is_subhint` tester.

    Parameters
    ----------
    subhint_superhint_is_cases : Iterable[Tuple[object, object, bool]]
        Iterable of one or more 3-tuples ``(subhint, superhint,
        is_subhint)`` as defined by :func:`subhint_superhint_is_cases`.
    '''

    # Defer heavyweight imports.
    from beartype.door import is_subhint

    # For each subhint relation to be tested...
    for subhint, superhint, IS_SUBHINT in subhint_superhint_is_cases:
        # Assert this tester returns the expected boolean.
        assert is_subhint(subhint, superhint) is IS_SUBHINT


#FIXME: Currently disabled due to failing tests under at least Python 3.7 and
#3.8. See also relevant commentary at:
#    https://github.com/beartype/beartype/pull/136#issuecomment-1175841494
# EQUALITY_CASES = [
#     (tuple, t.Tuple, True),
#     (list, list, True),
#     (list, t.List, True),
#     (list, t.List[t.Any], True),
#     (t.Union[int, str], t.Union[str, int], True),
#     (t.Union[int, str], t.Union[str, list], False),
#     (tuple, t.Tuple[t.Any, ...], True),
#     (t.Annotated[int, "hi"], t.Annotated[int, "hi"], True),
#     (t.Annotated[int, "hi"], t.Annotated[int, "low"], False),
#     (t.Annotated[int, "hi"], t.Annotated[int, "low"], False),
#     (abc.Awaitable[abc.Sequence[int]], t.Awaitable[t.Sequence[int]], True),
# ]
# if IS_PYTHON_AT_LEAST_3_9:
#     EQUALITY_CASES.extend(
#         [
#             (tuple[str, ...], t.Tuple[str, ...], True),
#             (list[str], t.List[str], True),
#         ]
#     )
#
#
# @pytest.mark.parametrize("type_a, type_b, expected", EQUALITY_CASES)
# def test_type_equality(type_a, type_b, expected):
#     """test that things with the same sign and arguments are equal."""
#     hint_a = TypeHint(type_a)
#     hint_b = TypeHint(type_b)
#     assert (hint_a == hint_b) is expected
#
#     # smoke test
#     assert hint_a != TypeHint(t.Generator[t.Union[list, str], str, None])
#
#     assert hint_a != "notahint"
#     with pytest.raises(TypeError, match="not supported between"):
#         hint_a <= "notahint"
#
#
# def test_type_hint_singleton():
#     """Recreating a type hint with the same input should yield the same type hint."""
#     assert TypeHint(t.List[t.Any]) is TypeHint(t.List[t.Any])
#     assert TypeHint(int) is TypeHint(int)
#     assert TypeHint(TypeHint(int)) is TypeHint(int)
#
#     # alas, this is not true:
#     assert TypeHint(t.List) is not TypeHint(list)
#     # leaving here for future reference, and so we know if we've fixed it.
#
#
# def test_typehint_fail():
#     with pytest.raises(BeartypeMathException):
#         TypeHint(1)
#
#
# @pytest.mark.parametrize(
#     "nparams, sign_group",
#     [
#         (1, _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1),
#         (2, _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2),
#         (3, _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3),
#     ],
# )
# def test_arg_nparams(nparams, sign_group):
#     """Make sure that our hint sign groups are consistent with the typing module."""
#     for sign in sign_group:
#         actual = getattr(t, sign.name)._nparams
#         assert (
#             actual == nparams
#         ), f"{sign.name} has {actual} params, should have {nparams}"
#
#
# def test_callable_takes_args():
#     assert TypeHint(t.Callable[[], t.Any]).takes_no_args is True
#     assert TypeHint(t.Callable[[int], t.Any]).takes_no_args is False
#     assert TypeHint(t.Callable[..., t.Any]).takes_no_args is False
#
#     assert TypeHint(t.Callable[..., t.Any]).takes_any_args is True
#     assert TypeHint(t.Callable[[int], t.Any]).takes_any_args is False
#     assert TypeHint(t.Callable[[], t.Any]).takes_any_args is False
#
#
# def test_empty_tuple():
#     assert TypeHint(t.Tuple[()]).is_empty_tuple
#
#
# def test_hint_iterable():
#     assert list(TypeHint(t.Union[int, str])) == [TypeHint(int), TypeHint(str)]
#     assert not list(TypeHint(int))
#
#
# def test_hint_ordered_comparison():
#     a = TypeHint(t.Callable[[], list])
#     b = TypeHint(t.Callable[..., t.Sequence[t.Any]])
#
#     assert a <= b
#     assert a < b
#     assert a != b
#     assert not a > b
#     assert not a >= b
#
#     with pytest.raises(TypeError, match="not supported between"):
#         a <= 1
#     with pytest.raises(TypeError, match="not supported between"):
#         a < 1
#     with pytest.raises(TypeError, match="not supported between"):
#         a >= 1
#     with pytest.raises(TypeError, match="not supported between"):
#         a > 1
#
#
# def test_hint_repr():
#     annotation = t.Callable[[], list]
#     hint = TypeHint(annotation)
#     assert repr(annotation) in repr(hint)
#
#
# def test_types_that_are_just_origins():
#     assert TypeHint(t.Callable)._is_just_an_origin
#     assert TypeHint(t.Callable[..., t.Any])._is_just_an_origin
#     assert TypeHint(t.Tuple)._is_just_an_origin
#     assert TypeHint(t.Tuple[t.Any, ...])._is_just_an_origin
#     assert TypeHint(int)._is_just_an_origin
#
#
# def test_invalid_subtype_comparison():
#     hint = TypeHint(t.Callable[[], list])
#     with pytest.raises(
#         BeartypeMathException, match="not a 'beartype.door.TypeHint' instance"
#     ):
#         hint.is_subhint(int)
#
#
# def test_callable_param_spec():
#     # TODO
#     with pytest.raises(NotImplementedError):
#         TypeHint(t.Callable[t.ParamSpec("P"), t.TypeVar("T")])
#
#
# def test_generic():
#     # TODO
#     class MyGeneric(t.Generic[T]):
#         ...
#
#     with pytest.raises(BeartypeMathException, match="currently unsupported by class"):
#         TypeHint(MyGeneric[int])
