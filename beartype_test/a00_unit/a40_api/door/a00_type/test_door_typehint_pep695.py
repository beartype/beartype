#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR)** :pep:`695`-compliant
**type alias unit tests.**

This submodule unit tests the :class:`beartype.door.Pep695TypeAliasTypeHint`
subclass of the :class:`beartype.door.TypeHint` superclass.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than
import pytest

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.12.0')
def test_door_pep695_alias_wrapper() -> None:
    '''
    Test that the :class:`beartype.door.TypeHint` factory wraps
    :pep:`695`-compliant type aliases with the expected subclass, preserving
    the alias itself.
    '''

    # Defer test-specific imports.
    from beartype.door import (
        Pep695TypeAliasTypeHint,
        TypeHint,
    )
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasDoorInt,
        AliasDoorListSetT,
    )

    # Assert this factory wraps both unsubscripted and subscripted aliases with
    # the expected subclass.
    assert isinstance(TypeHint(AliasDoorInt), Pep695TypeAliasTypeHint)
    assert isinstance(TypeHint(AliasDoorListSetT[int]), Pep695TypeAliasTypeHint)

    # Assert this wrapper preserves the alias itself.
    assert TypeHint(AliasDoorInt).hint is AliasDoorInt

    # Assert this wrapper is a singleton, as with all other wrappers.
    assert TypeHint(AliasDoorInt) is TypeHint(AliasDoorInt)


@skip_if_python_version_less_than('3.12.0')
def test_door_pep695_alias_hint_aliased() -> None:
    '''
    Test the :attr:`beartype.door.Pep695TypeAliasTypeHint.hint_aliased`
    property.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasDoorBareT,
        AliasDoorInt,
        AliasDoorIntNested,
        AliasDoorListSetT,
    )

    # Assert this property resolves an alias to the *SAME* singleton wrapper
    # wrapping the hint aliased by that alias.
    assert TypeHint(AliasDoorInt).hint_aliased is TypeHint(int)

    # Assert this property transitively resolves an alias of an alias.
    assert TypeHint(AliasDoorIntNested).hint_aliased is TypeHint(int)

    # Assert this property substitutes child hints for type parameters.
    assert TypeHint(AliasDoorListSetT[int]).hint_aliased is TypeHint(
        list[int] | set[int])

    # Assert this property substitutes an alias aliasing a bare type parameter,
    # which is *NOT* itself subscriptable.
    assert TypeHint(AliasDoorBareT[int]).hint_aliased is TypeHint(int)
    assert TypeHint(AliasDoorBareT[int]) == TypeHint(int)

    # Assert this property is specific to type alias wrappers.
    assert not hasattr(TypeHint(int), 'hint_aliased')


@skip_if_python_version_less_than('3.12.0')
def test_door_pep695_alias_hash() -> None:
    '''
    Test that type alias wrappers satisfy the equality-hash constraint.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasDoorInt,
        AliasDoorListSetT,
    )

    # Assert an alias hashes equal to the hint it aliases, and is usable as a
    # dictionary key interchangeably with that hint.
    assert hash(TypeHint(AliasDoorInt)) == hash(TypeHint(int))
    assert {TypeHint(int): 1}[TypeHint(AliasDoorInt)] == 1
    assert hash(TypeHint(AliasDoorListSetT[int])) == hash(
        TypeHint(list[int] | set[int]))


@skip_if_python_version_less_than('3.12.0')
def test_door_pep695_alias_recursive() -> None:
    '''
    Test that **recursive type aliases** (e.g., ``type Tree = int |
    list[Tree]``) are rejected at construction with the expected exception,
    rather than recursing infinitely later.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import (
        BeartypeDecorHintPep695Exception,
        BeartypeDoorPepUnsupportedException,
    )
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasCircularA,
        AliasDoorMutual1,
        AliasDoorMutual2,
        AliasDoorTree,
        AliasPep484604Recursive2T,
    )
    from pytest import raises

    # For each recursive alias...
    for hint_recursive in (
        AliasDoorTree,
        AliasDoorMutual1,
        AliasDoorMutual2,
        AliasPep484604Recursive2T[int],
    ):
        # Assert wrapping this alias raises the expected exception, twice. The
        # second attempt guards against the metaclass caching a wrapper whose
        # initialization failed.
        for _ in range(2):
            with raises(BeartypeDoorPepUnsupportedException) as exception_info:
                TypeHint(hint_recursive)
            assert 'recursive' in str(exception_info.value)

    # Assert a recursive alias nested beneath a non-alias parent raises the
    # same exception on first semantic use requiring that alias, rather than
    # "RecursionError". Parent wrappers wrap their child hints lazily, so
    # construction itself succeeds. Note that "list[int]" rather than
    # "list[object]" is intentional: the latter is decidable without
    # inspecting child hints and thus (correctly) never wraps this alias.
    hint_parent = TypeHint(list[AliasDoorTree])
    for _ in range(2):
        with raises(BeartypeDoorPepUnsupportedException):
            hash(hint_parent)
        with raises(BeartypeDoorPepUnsupportedException):
            hint_parent.is_subhint(TypeHint(list[int]))

    # Assert wrapping a circular chain of aliases raises the exception raised
    # by the underlying getter.
    with raises(BeartypeDecorHintPep695Exception):
        TypeHint(AliasCircularA)


@pytest.mark.xfail(
    strict=True,
    reason='repr-keyed TypeHint memoization collides: beartype/beartype#700',
)
@skip_if_python_version_less_than('3.12.0')
def test_door_pep695_alias_same_name() -> None:
    '''
    Test that distinct type aliases sharing the same name (and thus the same
    :func:`repr`) in different modules are *not* conflated.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from types import ModuleType

    def _make_module(name: str, source: str) -> ModuleType:
        module = ModuleType(name)
        exec(source, module.__dict__)
        return module

    # Two modules each defining same-named but distinct aliases. These names
    # are intentionally unique to this test, as the colliding cache is global.
    module_a = _make_module(
        'door_same_name_a',
        'type DoorSameName = int\ntype DoorSameNameG[T] = list[T]\n')
    module_b = _make_module(
        'door_same_name_b',
        'type DoorSameName = str\ntype DoorSameNameG[T] = set[T]\n')

    # Warm every cache with the first module's aliases.
    # Note that "not ==" rather than "!=" is intentional: __eq__() and
    # __ne__() are memoized by separate caches, and only __eq__() is asserted
    # against below.
    assert not (TypeHint(module_a.DoorSameName) == TypeHint(str))
    assert TypeHint(module_a.DoorSameName).is_subhint(TypeHint(int))
    assert not (TypeHint(module_a.DoorSameNameG[int]) == TypeHint(set[int]))

    # Assert the second module's aliases are answered on their own merits.
    assert TypeHint(module_b.DoorSameName) == TypeHint(str)
    assert not TypeHint(module_b.DoorSameName).is_subhint(TypeHint(int))
    assert TypeHint(module_b.DoorSameNameG[int]) == TypeHint(set[int])
