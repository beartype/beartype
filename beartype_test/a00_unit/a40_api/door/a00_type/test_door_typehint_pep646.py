#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR)** :pep:`646`-compliant
**fixed-variadic tuple hint unit tests.**

This submodule unit tests the reduction of :pep:`646`-compliant fixed-variadic
tuple hints performed by the :class:`beartype.door.TypeHint` superclass.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS ~ exact                      }....................
@skip_if_python_version_less_than('3.11.0')
def test_door_pep646_tuple_unpacked_fixed() -> None:
    '''
    Test that a :pep:`646`-compliant tuple hint subscripted by an unpacked
    *fixed-length* child tuple hint is wrapped by the same wrapper singleton as
    the :pep:`585`-compliant tuple hint it is longhand notation for.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        tuple_fixed_str_bytes_unpacked_prefix,
        tuple_fixed_str_bytes_unpacked_subbed,
    )

    # Wrapper wrapping the PEP 585-compliant tuple hint these PEP 646-compliant
    # tuple hints are merely longhand notation for.
    hint_wrapper = TypeHint(tuple[str, bytes])

    # Assert that both the "*tuple[str, bytes]" and
    # "typing.Unpack[tuple[str, bytes]]" spellings reduce to that same wrapper.
    assert TypeHint(
        tuple[tuple_fixed_str_bytes_unpacked_prefix]) is hint_wrapper
    assert TypeHint(
        tuple[tuple_fixed_str_bytes_unpacked_subbed]) is hint_wrapper


@skip_if_python_version_less_than('3.11.0')
def test_door_pep646_tuple_unpacked_variadic() -> None:
    '''
    Test that a :pep:`646`-compliant tuple hint subscripted by an unpacked
    *variadic* child tuple hint is wrapped by the same wrapper singleton as the
    :pep:`585`-compliant variadic tuple hint it is longhand notation for.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        tuple_variadic_strs_unpacked_prefix,
        tuple_variadic_strs_unpacked_subbed,
    )

    # Wrapper wrapping the PEP 585-compliant variadic tuple hint these PEP
    # 646-compliant tuple hints are merely longhand notation for.
    hint_wrapper = TypeHint(tuple[str, ...])

    assert TypeHint(
        tuple[tuple_variadic_strs_unpacked_prefix]) is hint_wrapper
    assert TypeHint(
        tuple[tuple_variadic_strs_unpacked_subbed]) is hint_wrapper


@skip_if_python_version_less_than('3.11.0')
def test_door_pep646_tuple_typevartuple() -> None:
    '''
    Test that a :pep:`646`-compliant tuple hint subscripted by *only* an
    unpacked type variable tuple (e.g., ``tuple[*Ts]``) is wrapped by the same
    wrapper singleton as the builtin :class:`tuple` type, which matches exactly
    the same tuples.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        Ts_unpacked_prefix,
        Ts_unpacked_subbed,
    )

    assert TypeHint(tuple[Ts_unpacked_prefix]) is TypeHint(tuple)
    assert TypeHint(tuple[Ts_unpacked_subbed]) is TypeHint(tuple)

# ....................{ TESTS ~ lossy                      }....................
@skip_if_python_version_less_than('3.11.0')
def test_door_pep646_tuple_mixed_unsupported() -> None:
    '''
    Test that a :pep:`646`-compliant tuple hint subscripted by *both* an
    unpacked variadic child hint *and* one or more other child hints raises the
    expected exception.

    :mod:`beartype` currently type-checks such hints only shallowly (i.e., as
    merely :class:`tuple`). Silently reducing such a hint would thus publish a
    semantics-eroding reduction through this API.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import BeartypeDoorPepUnsupportedException
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        Ts_unpacked_prefix,
        tuple_variadic_strs_unpacked_prefix,
    )
    from pytest import raises

    # For each mixed fixed-variadic tuple hint...
    for hint in (
        # A prefix of one or more child hints followed by an unpacked variadic
        # child tuple hint.
        tuple[int, tuple_variadic_strs_unpacked_prefix],
        # An unpacked variadic child tuple hint followed by a suffix.
        tuple[tuple_variadic_strs_unpacked_prefix, int],
        # A prefix followed by an unpacked type variable tuple.
        tuple[int, Ts_unpacked_prefix],
    ):
        # Assert that this factory raises the expected exception.
        with raises(BeartypeDoorPepUnsupportedException) as exception_info:
            TypeHint(hint)

        # Assert that this exception message is helpful.
        assert 'shallowly' in str(exception_info.value)


@skip_if_python_version_less_than('3.11.0')
def test_door_pep646_tuple_equality() -> None:
    '''
    Test that reduced :pep:`646`-compliant tuple hints preserve the equality and
    subhint relations of the tuple hints they reduce to.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        tuple_fixed_str_bytes_unpacked_prefix)

    # PEP 646-compliant longhand notation for "tuple[str, bytes]".
    hint = tuple[tuple_fixed_str_bytes_unpacked_prefix]

    # Assert that this hint compares equal to that shorthand notation.
    assert TypeHint(hint) == TypeHint(tuple[str, bytes])

    # Assert that this hint is a subhint of a variadic tuple of supertypes.
    assert TypeHint(hint) <= TypeHint(tuple[object, ...])

    # Assert that this hint is *NOT* a subhint of an unrelated tuple hint.
    assert not (TypeHint(hint) <= TypeHint(tuple[int, int]))


# ....................{ TESTS ~ unwrappable                }....................
@skip_if_python_version_less_than('3.11.0')
def test_door_pep646_unwrappable() -> None:
    '''
    Test that :pep:`646`-compliant objects that merely modify the child hints
    subscripting a parent hint -- rather than conveying meaning in their own
    right -- raise the expected exception when wrapped in isolation.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import BeartypeDoorPepUnsupportedException
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        Ts,
        Ts_unpacked_prefix,
        Ts_unpacked_subbed,
        tuple_fixed_str_bytes_unpacked_prefix,
        tuple_fixed_str_bytes_unpacked_subbed,
    )
    from pytest import raises

    # For each unwrappable object...
    for hint in (
        # Both spellings of an unpacked child tuple hint. Note that these two
        # spellings previously disagreed: the "typing.Unpack[...]" spelling was
        # silently misidentified as an unsubscripted hint, as that spelling
        # alone is published by the "typing" submodule.
        tuple_fixed_str_bytes_unpacked_prefix,
        tuple_fixed_str_bytes_unpacked_subbed,

        # Both spellings of an unpacked type variable tuple.
        Ts_unpacked_prefix,
        Ts_unpacked_subbed,

        # A type variable tuple, which is *ONLY* valid unpacked in a parent
        # hint (e.g., "def f(*args: *Ts)").
        Ts,
    ):
        with raises(BeartypeDoorPepUnsupportedException):
            TypeHint(hint)


@skip_if_python_version_less_than('3.11.0')
def test_door_pep646_unwrappable_parents_unaffected() -> None:
    '''
    Test that wrapping the *parent* hints subscripted by unwrappable objects
    continues to behave as expected.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        tuple_fixed_str_bytes_unpacked_prefix)
    from typing import TypeVar

    # Assert that the parent tuple hint subscripted by an unwrappable object
    # remains wrappable.
    assert TypeHint(
        tuple[tuple_fixed_str_bytes_unpacked_prefix]) is TypeHint(
        tuple[str, bytes])

    # Assert that PEP 484-compliant type variables remain wrappable. Unlike a
    # type variable tuple, a type variable *IS* a valid standalone hint.
    assert TypeHint(TypeVar('T')) is not None
