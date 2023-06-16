#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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

# ....................{ TESTS ~ raisers                    }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by this test. Urgh!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
def test_door_die_if_unbearable() -> None:
    '''
    Test the :class:`beartype.door.die_if_unbearable` raiser function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import die_if_unbearable
    from beartype.roar import (
        BeartypeConfException,
        BeartypeDecorHintNonpepException,
        BeartypeDoorHintViolation,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPithUnsatisfiedMetadata)
    from beartype_test.a00_unit.data.hint.util.data_hintmetautil import (
        iter_hints_piths_meta)
    from pytest import raises

    # ....................{ PASS                           }....................
    # For each predefined type hint and associated metadata...
    for hint_pith_meta in iter_hints_piths_meta():
        # Type hint to be type-checked.
        hint = hint_pith_meta.hint_meta.hint

        # Beartype dataclass configuring this type-check.
        conf = hint_pith_meta.hint_meta.conf

        # Object to type-check against this type hint.
        pith = hint_pith_meta.pith

        # If this pith violates this hint...
        if isinstance(hint_pith_meta.pith_meta, HintPithUnsatisfiedMetadata):
            # Assert this raiser raises the expected exception when passed this
            # pith and hint.
            with raises(BeartypeDoorHintViolation) as exception_info:
                die_if_unbearable(pith, hint, conf=conf)

            # Exception message raised by this wrapper function.
            exception_str = str(exception_info.value)

            # Assert this raiser successfully replaced the irrelevant substring
            # previously prefixing this message.
            assert exception_str.startswith('Object ')
            assert ' violates type hint ' in exception_str
        # Else, this raiser satisfies this hint. In this case...
        else:
            # Assert this validator raises *NO* exception when passed this pith
            # and hint.
            die_if_unbearable(pith, hint, conf=conf)

    # ....................{ FAIL                           }....................
    # Assert this tester raises the expected exception when passed an invalid
    # object as the type hint.
    with raises(BeartypeDecorHintNonpepException):
        die_if_unbearable(
            obj='Holds every future leaf and flower; the bound',
            hint=b'With which from that detested trance they leap;',
        )

    # Assert this tester raises the expected exception when passed an invalid
    # object as the beartype configuration.
    with raises(BeartypeConfException):
        die_if_unbearable(
            obj='The torpor of the year when feeble dreams',
            hint=str,
            conf='Visit the hidden buds, or dreamless sleep',
        )


# See above for @ignore_warnings() discussion.
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
def test_door_typehint_die_if_unbearable() -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.die_if_unbearable` raiser method.

    This test intentionally tests only the core functionality of this tester to
    avoid violating Don't Repeat Yourself (DRY). This tester internally defers
    to the procedural :class:`beartype.door.die_if_unbearable` tester, already
    exhaustively tested by preceding unit tests.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
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

    # ....................{ PASS                           }....................
    # For each predefined unignorable type hint and associated metadata...
    for hint_pith_meta in iter_hints_piths_meta():
        # Type hint to be type-checked.
        hint = hint_pith_meta.hint_meta.hint

        # Beartype dataclass configuring this type-check.
        conf = hint_pith_meta.hint_meta.conf

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
                    typehint.die_if_unbearable(pith, conf=conf)
            # Else, this pith satisfies this hint. In this case, assert this
            # raiser raises *NO* exception when passed this pith and hint.
            else:
                typehint.die_if_unbearable(pith, conf=conf)

# ....................{ TESTS ~ testers                    }....................
# See above for @ignore_warnings() discussion.
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
def test_door_is_bearable() -> None:
    '''
    Test the :class:`beartype.door.is_bearable` tester function.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.door import is_bearable
    from beartype.roar import (
        BeartypeConfException,
        BeartypeDecorHintForwardRefException,
        BeartypeDecorHintNonpepException,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPithUnsatisfiedMetadata)
    from beartype_test.a00_unit.data.hint.util.data_hintmetautil import (
        iter_hints_piths_meta)
    from beartype_test.a00_unit.data.hint.data_hint import HINTS_IGNORABLE
    from pytest import raises

    # ..................{ PASS ~ ignorable                   }..................
    # Arbitrary object to be tested below.
    pith = 'The breath and blood of distant lands, for ever'

    # For each predefined ignorable type hint...
    for hint_ignorable in HINTS_IGNORABLE:
        # Assert this tester returns true when passed this object and this hint.
        assert is_bearable(pith, hint_ignorable) is True

    # ..................{ PASS ~ unignorable                 }..................
    # For each predefined unignorable type hint and associated metadata...
    for hint_pith_meta in iter_hints_piths_meta():
        # Type hint to be type-checked.
        hint = hint_pith_meta.hint_meta.hint

        # Beartype dataclass configuring this type-check.
        conf = hint_pith_meta.hint_meta.conf

        # Object to type-check against this type hint.
        pith = hint_pith_meta.pith

        # True only if this pith satisfies this hint.
        is_bearable_expected = not isinstance(
            hint_pith_meta.pith_meta, HintPithUnsatisfiedMetadata)

        # Assert this tester returns the expected boolean when passed this pith
        # and hint.
        assert is_bearable(pith, hint, conf=conf) is is_bearable_expected

    # ..................{ FAIL ~ args                        }..................
    # Assert this tester raises the expected exception when passed an invalid
    # object as the type hint.
    with raises(BeartypeDecorHintNonpepException):
        is_bearable(
            obj='Holds every future leaf and flower; the bound',
            hint=b'With which from that detested trance they leap;',
        )

    # Assert this tester raises the expected exception when passed an invalid
    # object as the beartype configuration.
    with raises(BeartypeConfException):
        is_bearable(
            obj='The torpor of the year when feeble dreams',
            hint=str,
            conf='Visit the hidden buds, or dreamless sleep',
        )

    # ..................{ FAIL ~ refs                        }..................
    class RollsItsLoudWatersToTheOceanWaves(object):
        '''
        Arbitrary class with which to test relative forward references below.
        '''

        pass

    # Assert this tester raises the expected exception when passed a relative
    # forward reference as the type hint, which this tester explicitly prohibits
    # to promote both robustness and efficiency.
    with raises(BeartypeDecorHintForwardRefException):
        is_bearable(
            obj='Breathes its swift vapours to the circling air.',
            hint='RollsItsLoudWatersToTheOceanWaves',
        )


# See above for @ignore_warnings() discussion.
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
def test_door_typehint_is_bearable() -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.is_bearable` tester method.

    This test intentionally tests only the core functionality of this tester to
    avoid violating Don't Repeat Yourself (DRY). This tester internally defers
    to the procedural :class:`beartype.door.is_bearable` tester, already
    exhaustively tested by preceding unit tests.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import BeartypeDoorNonpepException
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPithUnsatisfiedMetadata)
    from beartype_test.a00_unit.data.hint.util.data_hintmetautil import (
        iter_hints_piths_meta)
    from contextlib import suppress

    # ....................{ PASS                           }....................
    # For each predefined unignorable type hint and associated metadata...
    for hint_pith_meta in iter_hints_piths_meta():
        # Type hint to be type-checked.
        hint = hint_pith_meta.hint_meta.hint

        # Beartype dataclass configuring this type-check.
        conf = hint_pith_meta.hint_meta.conf

        # Object to type-check against this type hint.
        pith = hint_pith_meta.pith

        # True only if this pith satisfies this hint.
        is_bearable_expected = not isinstance(
            hint_pith_meta.pith_meta, HintPithUnsatisfiedMetadata)

        #FIXME: Remove this suppression *AFTER* improving "TypeHint" to support
        #all currently unsupported type hints.
        with suppress(BeartypeDoorNonpepException):
            # Assert this tester returns the expected boolean when passed this
            # pith and hint.
            assert TypeHint(hint).is_bearable(pith, conf=conf) is (
                is_bearable_expected)
