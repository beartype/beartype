#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
DOOR comparisons between named tuples and positional tuple type hints.
'''

from pytest import mark
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than


@mark.parametrize('functional', (False, True))
def test_door_namedtuple_matching_fields(functional: bool) -> None:
    '''Class and functional named tuples retain their positional field types.'''

    from beartype.door import TypeHint, is_subhint
    from typing import NamedTuple, Tuple

    class NamedFields(NamedTuple):
        name: str
        kind: str
        velocity: float

    hint = (
        NamedTuple('FunctionalFields', [
            ('name', str), ('kind', str), ('velocity', float)])
        if functional else NamedFields
    )
    wrapper = TypeHint(hint)

    assert wrapper <= TypeHint(tuple[str, str, float])
    assert TypeHint(Tuple[str, str, float]) >= wrapper
    assert is_subhint(hint, tuple[str, str, float])
    assert wrapper.hint is hint


@mark.parametrize('superhint, expected', (
    (tuple[object, str, object], True),
    (tuple[object, ...], True),
    (tuple[str, ...], False),
    (tuple[str, str, int], False),
    (tuple[float, str, str], False),
    (tuple[str, str], False),
    (tuple[str, str, float, str], False),
    (tuple[()], False),
))
def test_door_namedtuple_field_comparison(superhint, expected: bool) -> None:
    '''Field covariance, order and length agree with tuple comparisons.'''

    from beartype.door import TypeHint
    from typing import NamedTuple

    class ComparedFields(NamedTuple):
        name: str
        kind: str
        velocity: float

    assert (TypeHint(ComparedFields) <= TypeHint(superhint)) is expected


def test_door_namedtuple_nested_fields() -> None:
    '''Existing supported nested field hints keep their comparison semantics.'''

    from beartype.door import TypeHint
    from typing import NamedTuple

    class NestedFields(NamedTuple):
        labels: list[str]
        count: int | None

    assert TypeHint(NestedFields) <= TypeHint(tuple[list[str], int | None])
    assert not TypeHint(NestedFields) <= TypeHint(tuple[list[int], int | None])
    assert TypeHint(NestedFields) <= TypeHint(tuple[list[str], object] | str)


@mark.parametrize('functional', (False, True))
def test_door_namedtuple_empty(functional: bool) -> None:
    '''An empty named tuple has zero positional fields, not an unknown length.'''

    from beartype.door import TypeHint
    from typing import NamedTuple

    class EmptyFields(NamedTuple):
        pass

    hint = NamedTuple('FunctionalEmptyFields', []) if functional else EmptyFields
    assert TypeHint(hint) <= TypeHint(tuple[()])
    assert TypeHint(hint) <= TypeHint(tuple[int, ...])
    assert not TypeHint(hint) <= TypeHint(tuple[int])


def test_door_namedtuple_subclass_fields() -> None:
    '''Subclass annotations and default values do not change tuple fields.'''

    from beartype.door import TypeHint
    from typing import NamedTuple

    class InheritedFields(NamedTuple):
        name: str
        count: int = 1

    class ExtraAttribute(InheritedFields):
        label: bytes

    assert TypeHint(ExtraAttribute) <= TypeHint(tuple[str, int])
    assert not TypeHint(ExtraAttribute) <= TypeHint(tuple[str, int, bytes])
    assert TypeHint(ExtraAttribute) <= TypeHint(InheritedFields)
    assert not TypeHint(InheritedFields) <= TypeHint(ExtraAttribute)


def test_door_namedtuple_nominal_identity() -> None:
    '''Tuple comparison must not erase the identity of a named tuple class.'''

    from beartype.door import TypeHint
    from typing import Any, NamedTuple

    class FirstRecord(NamedTuple):
        value: int

    class SecondRecord(NamedTuple):
        value: int

    first = TypeHint(FirstRecord)
    second = TypeHint(SecondRecord)
    original_hash = hash(first)
    assert first <= TypeHint(tuple)
    assert first <= TypeHint(object)
    assert first <= TypeHint(Any)
    assert not first <= second
    assert not second <= first
    assert first != second
    assert not TypeHint(tuple[int]) <= first
    assert first != TypeHint(tuple[int])
    assert TypeHint(tuple[int]) != first
    assert first.hint is FirstRecord
    assert hash(first) == original_hash
    assert {first: 'first', second: 'second'}[TypeHint(FirstRecord)] == 'first'


def test_door_namedtuple_untyped_fields() -> None:
    '''The fields of collections.namedtuple are Any, with a fixed length.'''

    from beartype.door import TypeHint
    from collections import namedtuple

    UntypedFields = namedtuple('UntypedFields', ('name', 'count'))
    wrapper = TypeHint(UntypedFields)
    assert wrapper <= TypeHint(tuple[str, int])
    assert wrapper <= TypeHint(tuple[object, ...])
    assert not wrapper <= TypeHint(tuple[str])
    assert not TypeHint(tuple[str, int]) <= wrapper
    assert wrapper.hint is UntypedFields


def test_door_namedtuple_plain_tuple_subclass() -> None:
    '''Ordinary tuple subclasses do not acquire positional annotation meaning.'''

    from beartype.door import TypeHint

    class AnnotatedTuple(tuple):
        value: int

    class TupleWithFields(tuple):
        _fields = ('value',)
        value: int

    assert not TypeHint(AnnotatedTuple) <= TypeHint(tuple[int])
    assert not TypeHint(TupleWithFields) <= TypeHint(tuple[int])
    assert TypeHint(AnnotatedTuple) <= TypeHint(tuple)
    assert TypeHint(TupleWithFields) <= TypeHint(tuple)


@mark.parametrize('field_kind', ('direct', 'nested', 'callable', 'typevar'))
def test_door_namedtuple_unresolved_fields(field_kind: str) -> None:
    '''Comparisons do not resolve field names in an unrelated caller scope.'''

    from beartype.door import TypeHint
    from typing import Callable, ForwardRef, NamedTuple, TypeVar

    field_hints = {
        'direct': ForwardRef('UnresolvedNamedTupleField'),
        'nested': list['UnresolvedNamedTupleField'],
        'callable': Callable[[list['UnresolvedNamedTupleField']], int],
        'typevar': TypeVar('UnresolvedField', bound='UnresolvedNamedTupleField'),
    }
    UnresolvedFields = NamedTuple(
        'UnresolvedFields', [('value', field_hints[field_kind])])

    assert not TypeHint(UnresolvedFields) <= TypeHint(tuple[object])
    assert TypeHint(UnresolvedFields) <= TypeHint(tuple)


def test_door_namedtuple_literal_metadata_and_any_fields() -> None:
    '''Literal strings and Annotated metadata are not forward references.'''

    from beartype.door import TypeHint
    from typing import Annotated, Any, Literal, NamedTuple

    class LiteralFields(NamedTuple):
        kind: Literal['red']
        count: Annotated[int, 'metadata']
        value: Any

    assert TypeHint(LiteralFields) <= TypeHint(tuple[str, int, bytes])
    assert not TypeHint(LiteralFields) <= TypeHint(
        tuple[Literal['blue'], int, bytes])


@skip_if_python_version_less_than('3.12.0')
@mark.parametrize('alias_kind', (
    'resolved', 'unresolved', 'nested', 'subscribed'))
def test_door_namedtuple_alias_fields(alias_kind: str) -> None:
    '''Unsupported alias fields retain nominal comparisons without resolution.'''

    from beartype.door import TypeHint
    from typing import NamedTuple

    namespace = {'__name__': __name__}
    exec(
        'type Alias = int' if alias_kind == 'resolved' else
        'type Alias[T] = T' if alias_kind == 'subscribed' else
        'type Alias = UnresolvedNamedTupleField', namespace)
    alias = namespace['Alias']
    field = (
        list[alias] if alias_kind == 'nested' else
        alias[int] if alias_kind == 'subscribed' else alias
    )
    AliasFields = NamedTuple('AliasFields', [('value', field)])

    assert not TypeHint(AliasFields) <= TypeHint(tuple[object])
    assert TypeHint(AliasFields) <= TypeHint(tuple)
