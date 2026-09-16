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

    # Assert this wrapper preserves the alias itself rather than silently
    # replacing that alias by the hint aliased by that alias.
    assert TypeHint(AliasDoorInt).hint is AliasDoorInt

    # Assert this wrapper is a singleton, as with all other wrappers.
    assert TypeHint(AliasDoorInt) is TypeHint(AliasDoorInt)


@skip_if_python_version_less_than('3.12.0')
def test_door_pep695_alias_unaliased() -> None:
    '''
    Test the :attr:`beartype.door.TypeHint.unaliased` property.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasDoorInt,
        AliasDoorIntNested,
        AliasDoorListSetT,
    )

    # Assert this property resolves an alias to the *SAME* singleton wrapper
    # wrapping the hint aliased by that alias.
    assert TypeHint(AliasDoorInt).unaliased is TypeHint(int)

    # Assert this property transitively resolves an alias of an alias.
    assert TypeHint(AliasDoorIntNested).unaliased is TypeHint(int)

    # Assert this property replaces the type parameters parametrizing a
    # subscripted alias by the child hints subscripting that alias.
    assert TypeHint(AliasDoorListSetT[int]).unaliased is TypeHint(
        list[int] | set[int])

    # Assert this property is the identity for hints that are *NOT* aliases,
    # enabling callers to unconditionally access this property.
    assert TypeHint(int).unaliased is TypeHint(int)

    # Assert this property is idempotent.
    assert TypeHint(AliasDoorInt).unaliased.unaliased is TypeHint(int)


@skip_if_python_version_less_than('3.12.0')
def test_door_pep695_alias_recursive() -> None:
    '''
    Test that **recursive type aliases** (e.g., ``type Tree = int |
    list[Tree]``) are hashable and comparable without infinite recursion,
    preserving the equality-hash constraint.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasPep484604Recursive1T,
        AliasPep484604Recursive2T,
    )

    # Wrappers wrapping two distinct recursive aliases.
    hint_a = TypeHint(AliasPep484604Recursive1T[int])
    hint_b = TypeHint(AliasPep484604Recursive2T[int])

    # Assert that hashing these wrappers halts.
    assert isinstance(hash(hint_a), int)
    assert isinstance(hash(hint_b), int)

    # Assert that comparing these wrappers halts.
    assert hint_a == hint_a
    assert hint_a.is_subhint(hint_a)
    assert hint_a.is_subhint(TypeHint(object))
    assert isinstance(hint_a == hint_b, bool)

    # Assert that these wrappers preserve the equality-hash constraint: if two
    # wrappers compare equal, then those wrappers *MUST* share the same hash.
    # Violating this silently breaks hashable containers keyed on wrappers.
    if hint_a == hint_b:
        assert hash(hint_a) == hash(hint_b)
