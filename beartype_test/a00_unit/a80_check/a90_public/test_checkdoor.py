#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) type-checking unit
tests.**

This submodule unit tests the subset of the public API of the public
:mod:`beartype.door` subpackage that pertains to type-checking.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from beartype_test._util.mark.pytmark import ignore_warnings

# ....................{ TESTS ~ testers                    }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by this test. Urgh!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
def test_door_die_if_unbearable() -> None:
    '''
    Test successful usage of the :meth:`beartype.door.TypeHint.die_if_unbearable`
    tester.

    This test intentionally tests only the core functionality of this tester to
    avoid violating Don't Repeat Yourself (DRY). This tester internally defers
    to the :class:`beartype.abby.die_if_unbearable` tester, whose test in the
    companion :mod:`test_checkabby` submodule already exercises all
    functionality of that tester.
    '''

    # Defer heavyweight imports.
    from beartype.door import TypeHint
    from beartype.roar import (
        BeartypeDoorHintViolation,
        BeartypeDoorNonpepException,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPithUnsatisfiedMetadata)
    from beartype_test.a00_unit.data.hint.util.data_hintmetautil import (
        iter_hints_piths_meta)
    from contextlib import suppress
    from pytest import raises

    # For each predefined unignorable type hint and associated metadata...
    for hint_pith_meta in iter_hints_piths_meta():
        # Type hint to be type-checked.
        hint = hint_pith_meta.hint_meta.hint

        # Object to type-check against this type hint.
        pith = hint_pith_meta.pith

        #FIXME: Remove this suppression *AFTER* improving "TypeHint" to support
        #all currently unsupported type hints.
        with suppress(BeartypeDoorNonpepException):
            # Wrapper wrapping this type hint.
            typehint = TypeHint(hint)

            # If this pith violates this hint, assert this raiser raises the
            # expected exception when passed this pith and hint.
            if isinstance(
                hint_pith_meta.pith_meta, HintPithUnsatisfiedMetadata):
                with raises(BeartypeDoorHintViolation):
                    typehint.die_if_unbearable(pith)
            # Else, this pith satisfies this hint. In this case, assert this
            # raiser raises *NO* exception when passed this pith and hint.
            else:
                typehint.die_if_unbearable(pith)


# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by this test. Urgh!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
def test_door_is_bearable() -> None:
    '''
    Test successful usage of the :meth:`beartype.door.TypeHint.is_bearable`
    tester.

    This test intentionally tests only the core functionality of this tester to
    avoid violating Don't Repeat Yourself (DRY). This tester internally defers
    to the :class:`beartype.abby.is_bearable` tester, whose test in the
    companion :mod:`test_checkabby` submodule already exercises all
    functionality of that tester.
    '''

    # Defer heavyweight imports.
    from beartype.door import TypeHint
    from beartype.roar import BeartypeDoorNonpepException
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPithUnsatisfiedMetadata)
    from beartype_test.a00_unit.data.hint.util.data_hintmetautil import (
        iter_hints_piths_meta)
    from contextlib import suppress

    # For each predefined unignorable type hint and associated metadata...
    for hint_pith_meta in iter_hints_piths_meta():
        # Type hint to be type-checked.
        hint = hint_pith_meta.hint_meta.hint

        # Object to type-check against this type hint.
        pith = hint_pith_meta.pith

        # True only if this pith satisfies this hint.
        is_bearable_expected = not isinstance(
            hint_pith_meta.pith_meta, HintPithUnsatisfiedMetadata)

        #FIXME: Remove this suppression *AFTER* improving "TypeHint" to support
        #all currently unsupported type hints.
        with suppress(BeartypeDoorNonpepException):
            # Assert this tester returns false when passed this pith and hint.
            assert TypeHint(hint).is_bearable(pith) is is_bearable_expected
