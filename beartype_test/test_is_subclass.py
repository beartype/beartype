from typing import Union, Any, List, Sequence
from collections import abc
from beartype.math._mathcls import _is_subtype
from beartype.typing import Protocol

import pytest


class MuhThingP(Protocol):
    def muh_method(self):
        ...


class MuhThing:
    def muh_method(self):
        ...


class MuhNutherThing:
    def yo(self):
        ...


CASES = [
    # things are subclasses of themselves
    (list, list, True),
    (list, List, True),
    # a few standard, ordered types
    (Sequence, List, False),
    (Sequence, list, False),
    (List, Sequence, True),
    (list, Sequence, True),
    (list, abc.Sequence, True),
    (list, abc.Collection, True),
    # everything is a subtype of Any
    (Any, Any, True),
    (MuhThing, Any, True),
    (Union[int, MuhThing], Any, True),
    # numeric tower
    (float, int, True),
    (complex, int, True),
    (complex, float, True),
    (int, float, False),
    (float, complex, False),
    # subscripted types
    (List[int], List[int], True),
    (List[int], List, True),  # if the super is un-subscripted, assume Any
    (List[int], List[Any], True),
    (List, List[str], False),
    (List[int], List[str], False),
    # unions
    (int, Union[int, str], True),
    (Union[int, str], Union[list, int, str], True),
    (Union[str, int], Union[int, str, list], True),  # order doesn't matter
    (Union[str, list], Union[str, int], False),
    (Union[int, str, list], list, False),
    (Union[int, str, list], Union[int, str], False),
    # protocols
    (MuhThing, MuhThingP, True),
    (MuhNutherThing, MuhThingP, False),
    (MuhThingP, MuhThing, False),
    # moar nestz
    (List[int], Union[str, List[Union[int, str]]], True),
]


@pytest.mark.parametrize("subt, supert, expected_result", CASES)
def test_is_subtype(subt, supert, expected_result):
    assert _is_subtype(subt, supert) == expected_result
