import types
import typing as t
from collections import abc

import beartype.typing as bt
import pytest
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype.math._mathcls import (
    _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1,
    _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2,
    _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3,
    TypeHint,
    is_subtype,
)
from beartype.roar import BeartypeMathException


class MuhThingP(bt.Protocol):
    def muh_method(self):
        ...


class MuhThing:
    def muh_method(self):
        ...


class MuhNutherThing:
    def __len__(self) -> int:
        ...


class MuhDict(t.TypedDict):
    thing_one: str
    thing_two: int


SUBTYPE_CASES = [
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
    # unions
    (int, t.Union[int, str], True),
    (t.Union[int, str], t.Union[list, int, str], True),
    (t.Union[str, int], t.Union[int, str, list], True),  # order doesn't matter
    (t.Union[str, list], t.Union[str, int], False),
    (t.Union[int, str, list], list, False),
    (t.Union[int, str, list], t.Union[int, str], False),
    # literals
    (t.Literal[1], int, True),
    (t.Literal["a"], str, True),
    (t.Literal[1, 2, "3"], t.Union[int, str], True),
    (t.Literal[1, 2, "3"], t.Union[list, int], False),
    (int, t.Literal[1], False),
    (t.Literal[1, 2], t.Literal[1, 2, 3], True),
    # protocols
    (MuhThing, MuhThingP, True),
    (MuhNutherThing, MuhThingP, False),
    (MuhThingP, MuhThing, False),
    # moar nestz
    (t.List[int], t.Union[str, t.List[t.Union[int, str]]], True),
    # not really types:
    (MuhDict, dict, True),
    # annotated:
    (
        t.Annotated[int, "a note"],
        int,
        True,
    ),  # annotated is subtype of unannotated origin
    (int, t.Annotated[int, "a note"], False),  # but not vice versa
    (t.Annotated[list, True], t.Annotated[t.Sequence, True], True),
    (t.Annotated[list, False], t.Annotated[t.Sequence, True], False),
    (t.Annotated[list, 0, 0], t.Annotated[list, 0], False),  # must have same num args
]


@pytest.mark.parametrize("subt, supert, expected_result", SUBTYPE_CASES)
def test_is_subtype(subt, supert, expected_result):
    """Test all the subtype cases."""
    assert is_subtype(subt, supert) is expected_result


EQUALITY_CASES = [
    (tuple, t.Tuple, True),
    (list, list, True),
    (list, t.List, True),
    (list, t.List[t.Any], True),
    (t.Union[int, str], t.Union[str, int], True),
    (t.Union[int, str], t.Union[str, list], False),
    (tuple, t.Tuple[t.Any, ...], True),
    (t.Annotated[int, "hi"], t.Annotated[int, "hi"], True),
    (t.Annotated[int, "hi"], t.Annotated[int, "low"], False),
    (abc.Awaitable[abc.Sequence[int]], t.Awaitable[t.Sequence[int]], True),
]
if IS_PYTHON_AT_LEAST_3_9:
    EQUALITY_CASES.extend(
        [
            (tuple[str, ...], t.Tuple[str, ...], True),
            (list[str], t.List[str], True),
        ]
    )


@pytest.mark.parametrize("type_a, type_b, expected", EQUALITY_CASES)
def test_type_equality(type_a, type_b, expected):
    """test that things with the same sign and arguments are equal."""
    hint_a = TypeHint(type_a)
    hint_b = TypeHint(type_b)
    assert (hint_a == hint_b) is expected

    # smoke test
    assert hint_a != TypeHint(t.Generator[t.Union[list, str], str, None])


def test_type_hint_singleton():
    """Recreating a type hint with the same input should yield the same type hint."""
    assert TypeHint(t.List[t.Any]) is TypeHint(t.List[t.Any])
    assert TypeHint(int) is TypeHint(int)

    # assert TypeHint(t.List) is TypeHint(list)  # alas


def test_typehint_fail():
    with pytest.raises(BeartypeMathException):
        TypeHint(1)


@pytest.mark.parametrize(
    "nparams, sign_group",
    [
        (1, _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1),
        (2, _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2),
        (3, _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3),
    ],
)
def test_arg_nparams(nparams, sign_group):
    """Make sure that our hint sign groups are consistent with the typing module."""
    for sign in sign_group:
        actual = getattr(t, sign.name)._nparams
        assert (
            actual == nparams
        ), f"{sign.name} has {actual} params, should have {nparams}"
