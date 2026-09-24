#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep695` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep695_unsubbed_alias_circular() -> None:
    '''
    Test that the
    :func:`beartype._util.hint.pep.proposal.pep695.get_hint_pep695_unsubbed_alias`
    getter raises the expected exception when passed a **circular chain of type
    aliases** (i.e., one or more type aliases each aliasing only the next, the
    last of which aliases the first).

    Such a chain never reduces to a type hint conveying any semantics. Absent
    detection, unwrapping such a chain silently iterates forever.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._util.hint.pep.proposal.pep695 import (
        get_hint_pep695_unsubbed_alias)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from pytest import raises

    # If the active Python interpreter targets Python < 3.12, this interpreter
    # fails to support PEP 695. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_12:
        return
    # Else, this interpreter supports PEP 695.

    # ....................{ IMPORTS ~ version              }....................
    # Defer version-specific imports.
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasCircularA,
        AliasCircularB,
        AliasCircularSelf,
    )

    # ....................{ FAIL                           }....................
    # For each circular type alias...
    for hint_circular in (
        AliasCircularSelf, AliasCircularA, AliasCircularB):
        # Assert that this getter raises the expected exception when passed
        # this alias rather than silently iterating forever.
        with raises(BeartypeDecorHintPep695Exception) as exception_info:
            get_hint_pep695_unsubbed_alias(hint_circular)

        # Assert that this exception message is helpful.
        assert 'circularly aliases itself' in str(exception_info.value)


def test_get_hint_pep695_alias() -> None:
    '''
    Test the private
    :func:`beartype._util.hint.pep.proposal.pep695.get_hint_pep695_alias`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._util.hint.pep.proposal.pep695 import get_hint_pep695_alias
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from pytest import raises

    # ....................{ FAIL                           }....................
    # Assert this getter rejects objects that are *NOT* type aliases.
    with raises(BeartypeDecorHintPep695Exception):
        get_hint_pep695_alias(int)

    # If the active Python interpreter targets Python < 3.12, this interpreter
    # fails to support PEP 695. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_12:
        return
    # Else, this interpreter supports PEP 695.

    # ....................{ IMPORTS ~ version              }....................
    # Defer version-specific imports.
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasCircularA,
        AliasDoorInt,
        AliasDoorIntNested,
        AliasDoorListSetT,
    )

    # ....................{ PASS                           }....................
    # Assert this getter reduces an unsubscripted alias to its aliased hint.
    assert get_hint_pep695_alias(AliasDoorInt) is int

    # Assert this getter transitively unwraps an alias of an alias.
    assert get_hint_pep695_alias(AliasDoorIntNested) is int

    # Assert this getter reduces a subscripted alias to the hint aliased by the
    # unsubscripted alias originating that alias, *BEFORE* substituting type
    # parameters (i.e., still parametrized by "T").
    assert get_hint_pep695_alias(AliasDoorListSetT[int]) == (
        AliasDoorListSetT.__value__)

    # ....................{ FAIL ~ circular                }....................
    # Assert this getter propagates circular-chain detection.
    with raises(BeartypeDecorHintPep695Exception):
        get_hint_pep695_alias(AliasCircularA)

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep695_subbed() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695.is_hint_pep695_subbed`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep695 import is_hint_pep695_subbed
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12

    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695util import (
            unit_test_is_hint_pep695_subbed)

        # Perform this test.
        unit_test_is_hint_pep695_subbed()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.

    # ....................{ FAIL                           }....................
    # Assert this tester rejects objects that are *NOT* PEP 585-compliant
    # subscripted builtins.
    assert is_hint_pep695_subbed(
        'And thou, colossal Skeleton, that, still') is False


def test_is_hint_pep695_recursive() -> None:
    '''
    Test the private
    :func:`beartype._util.hint.pep.proposal.pep695.is_hint_pep695_recursive`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._util.hint.pep.proposal.pep695 import (
        is_hint_pep695_recursive)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from pytest import raises

    # If the active Python interpreter targets Python < 3.12, this interpreter
    # fails to support PEP 695. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_12:
        return
    # Else, this interpreter supports PEP 695.

    # ....................{ IMPORTS ~ version              }....................
    # Defer version-specific imports.
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasCircularA,
        AliasCircularSelf,
        AliasDoorAnnotated,
        AliasDoorBareT,
        AliasDoorCallable,
        AliasDoorInt,
        AliasDoorIntNested,
        AliasDoorListSetT,
        AliasDoorMutual1,
        AliasDoorMutual2,
        AliasDoorShared,
        AliasDoorTree,
        AliasDoorUnion,
        AliasPep484604Recursive2T,
    )

    # ....................{ PASS ~ recursive               }....................
    # Assert this tester detects direct, generic, and mutual recursion from
    # every entry point.
    for hint_recursive in (
        AliasDoorTree,
        AliasPep484604Recursive2T,
        AliasPep484604Recursive2T[int],
        AliasDoorMutual1,
        AliasDoorMutual2,
    ):
        assert is_hint_pep695_recursive(hint_recursive) is True

    # ....................{ PASS ~ non-recursive           }....................
    # Assert this tester rejects non-recursive aliases, including aliases
    # reusing the same child alias more than once *WITHOUT* recursion.
    for hint_nonrecursive in (
        AliasDoorInt,
        AliasDoorIntNested,
        AliasDoorUnion,
        AliasDoorListSetT,
        AliasDoorListSetT[int],
        AliasDoorShared,
        AliasDoorAnnotated,
        AliasDoorCallable,
        AliasDoorBareT[int],
    ):
        assert is_hint_pep695_recursive(hint_nonrecursive) is False

    # ....................{ FAIL                           }....................
    # Assert this tester propagates circular-chain detection.
    for hint_circular in (AliasCircularSelf, AliasCircularA):
        with raises(BeartypeDecorHintPep695Exception):
            is_hint_pep695_recursive(hint_circular)

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep695_parameterizable_typeparams() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695._get_hint_pep695_parameterizable_typeparams`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._util.hint.pep.proposal.pep695 import (
        _get_hint_pep695_parameterizable_typeparams)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from beartype_test.a00_unit.data.data_type import (
        Class,
        function,
    )
    from pytest import raises

    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695util import (
            unit_test_get_hint_pep695_parameterizable_typeparams)

        # Perform this test.
        unit_test_get_hint_pep695_parameterizable_typeparams()

        # Assert this getter returns the empty tuple for pure-Python classes and
        # functions that are *NOT* PEP 695-parametrized.
        assert _get_hint_pep695_parameterizable_typeparams(Class) == ()
        assert _get_hint_pep695_parameterizable_typeparams(function) == ()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an arbitrary
    # object that is *NOT* parameterizable under PEP 695.
    with raises(BeartypeDecorHintPep695Exception):
        _get_hint_pep695_parameterizable_typeparams(
            'And all the gloom and sorrow of the place,')

# ....................{ TESTS ~ iterator                   }....................
def test_iter_hint_pep695_forwardrefs() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695.iter_hint_pep695_unsubbed_forwardrefs`
    iterator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._util.hint.pep.proposal.pep695 import (
        iter_hint_pep695_unsubbed_forwardrefs)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from pytest import raises

    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695util import (
            unit_test_iter_hint_pep695_forwardrefs)

        # Perform this test.
        unit_test_iter_hint_pep695_forwardrefs()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.

    # ....................{ FAIL                           }....................
    # Assert this iterator raises the expected exception when passed an
    # arbitrary PEP 695-noncompliant object.
    with raises(BeartypeDecorHintPep695Exception):
        next(iter_hint_pep695_unsubbed_forwardrefs(
            'Tumultuously accorded with those fits'))
