#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) type-checking**
unit tests.

This submodule unit tests the subset of the public API of the public
:mod:`beartype.door` subpackage that pertains to type-checking.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytmark import ignore_warnings

# ....................{ TESTS ~ raisers                    }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by this test. Urgh!
@ignore_warnings(DeprecationWarning)
def test_door_die_if_unbearable(iter_hints_piths_meta) -> None:
    '''
    Test the :class:`beartype.door.die_if_unbearable` raiser function.

    Parameters
    ----------
    iter_hints_piths_meta : Callable[[], Iterable[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPithMetadata]]
        Factory function creating and returning a generator iteratively yielding
        ``HintPithMetadata`` instances, each describing a sample type hint
        exercising an edge case in the :mod:`beartype` codebase paired with a
        related object either satisfying or violating that hint.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import die_if_unbearable
    from beartype.roar import (
        BeartypeConfException,
        BeartypeDecorHintNonpepException,
        BeartypeDoorHintViolation,
    )
    from beartype._util.text.utiltextrepr import represent_object
    from beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta import (
        PithUnsatisfiedMetadata)
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
        if isinstance(hint_pith_meta.pith_meta, PithUnsatisfiedMetadata):
            # print(f'hint_pith_meta: {hint_pith_meta}\n')

            # Assert this raiser raises the expected exception when passed this
            # pith and hint.
            with raises(BeartypeDoorHintViolation) as exception_info:
                die_if_unbearable(pith, hint, conf=conf)

            # Exception message raised by this wrapper function.
            exception_message = str(exception_info.value)

            # Truncated representation of this pith.
            pith_repr = represent_object(pith)

            # Assert that this message contains a truncated representation of
            # this pith.
            assert pith_repr in exception_message

            # Assert that this raiser successfully replaced the temporary
            # placeholder previously prefixing this message.
            assert 'die_if_unbearable() value ' in exception_message.lower()
            assert ' violates type hint ' in exception_message
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
@ignore_warnings(DeprecationWarning)
def test_door_typehint_die_if_unbearable(iter_hints_piths_meta) -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.die_if_unbearable` raiser method.

    This test intentionally tests only the core functionality of this tester to
    preserve  Don't Repeat Yourself (DRY). This tester internally defers to the
    procedural :class:`beartype.door.die_if_unbearable` tester, already
    exhaustively tested by preceding unit tests.

    Parameters
    ----------
    iter_hints_piths_meta : Callable[[], Iterable[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPithMetadata]]
        Factory function creating and returning a generator iteratively yielding
        ``HintPithMetadata`` instances, each describing a sample type hint
        exercising an edge case in the :mod:`beartype` codebase paired with a
        related object either satisfying or violating that hint.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import (
        BeartypeDoorHintViolation,
        BeartypeDoorNonpepException,
    )
    from beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta import (
        PithUnsatisfiedMetadata)
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
                hint_pith_meta.pith_meta, PithUnsatisfiedMetadata):
                with raises(BeartypeDoorHintViolation):
                    typehint.die_if_unbearable(pith, conf=conf)
            # Else, this pith satisfies this hint. In this case, assert this
            # raiser raises *NO* exception when passed this pith and hint.
            else:
                typehint.die_if_unbearable(pith, conf=conf)

# ....................{ TESTS ~ testers                    }....................
def test_door_is_bearable(iter_hints_piths_meta, hints_ignorable) -> None:
    '''
    Test the :class:`beartype.door.is_bearable` tester function.

    This test also validates that this tester issues expected non-fatal warnings
    when passed various problematic (e.g., deprecated) type hints.

    Parameters
    ----------
    iter_hints_piths_meta : Callable[[], Iterable[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPithMetadata]]
        Factory function creating and returning a generator iteratively yielding
        ``HintPithMetadata`` instances, each describing a sample type hint
        exercising an edge case in the :mod:`beartype` codebase paired with a
        related object either satisfying or violating that hint.
    hints_ignorable : frozenset
        Frozen set of ignorable PEP-agnostic type hints.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.door import is_bearable
    from beartype._util.cache.utilcacheclear import clear_caches
    from beartype.roar import (
        BeartypeConfException,
        BeartypeDecorHintNonpepException,
    )
    from beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta import (
        PithUnsatisfiedMetadata)
    from beartype_test._util.error.pyterrraise import raises_uncached
    from beartype_test._util.error.pyterrwarn import warns_uncached
    from warnings import (
        catch_warnings,
        simplefilter,
    )

    # ....................{ SETUP                          }....................
    # Force pytest to temporarily allow deprecation warnings to be caught by the
    # warns() context manager for the duration of this test. By default, pytest
    # simply "passes through" all deprecation warnings for subsequent reporting
    # if tests otherwise successfully pass. Deprecation warnings include:
    # * "DeprecationWarning".
    # * "FutureWarning".
    # * "PendingDeprecationWarning".
    simplefilter('always')

    # ....................{ PASS ~ ignorable               }....................
    # Arbitrary object to be tested below.
    pith = 'The breath and blood of distant lands, for ever'

    # For each predefined ignorable type hint...
    for hint_ignorable in hints_ignorable:
        # Assert this tester returns true when passed this object and this hint.
        assert is_bearable(pith, hint_ignorable) is True

    # ....................{ PASS ~ unignorable             }....................
    # For each predefined unignorable type hint and associated metadata...
    for hint_pith_meta in iter_hints_piths_meta():
        # Preserve test idempotence by explicitly clearing *ALL* internal caches
        # leveraged throughout the main @beartype codebase. Doing so effectively
        # resets this codebase back to its initial state.
        clear_caches()

        # Metadata describing this hint.
        hint_meta = hint_pith_meta.hint_meta

        # Type hint to be type-checked.
        hint = hint_meta.hint

        # Beartype dataclass configuring this type-check.
        conf = hint_meta.conf

        # Object to type-check against this type hint.
        pith = hint_pith_meta.pith

        # True only if this pith is expected to satisfy this hint.
        is_bearable_expected = not isinstance(
            hint_pith_meta.pith_meta, PithUnsatisfiedMetadata)

        # True only if this pith actually did satisfy this hint.
        is_bearable_returned: bool = None  # type: ignore[assignment]

        # If this tester is expected to emit a warning for this hint...
        if hint_meta.warning_type is not None:
            # Assert this tester to emit the expected warning when...
            with warns_uncached(hint_meta.warning_type):
                # Boolean returned by this tester when passed these parameters.
                is_bearable_returned = is_bearable(pith, hint, conf=conf)
        # Else, this tester is expected to emit *NO* warning for this hint. In
        # this case...
        else:
            # With a context manager "catching" *ALL* non-fatal warnings emitted
            # during this logic for subsequent "playback" below...
            with catch_warnings(record=True) as warnings_issued:
                # Boolean returned by this tester when passed these parameters.
                is_bearable_returned = is_bearable(pith, hint, conf=conf)

            # Assert that *NO* warnings were issued by this tester above.
            assert not warnings_issued

        # Assert that this tester returns the expected boolean when passed these
        # parameters.
        assert is_bearable_returned is is_bearable_expected

    # ....................{ FAIL ~ args                    }....................
    # Assert this tester raises the expected exception when passed an invalid
    # object as the type hint.
    with raises_uncached(BeartypeDecorHintNonpepException):
        is_bearable(
            obj='Holds every future leaf and flower; the bound',
            hint=b'With which from that detested trance they leap;',
        )

    # Assert this tester raises the expected exception when passed an invalid
    # object as the beartype configuration.
    with raises_uncached(BeartypeConfException):
        is_bearable(
            obj='The torpor of the year when feeble dreams',
            hint=str,
            conf='Visit the hidden buds, or dreamless sleep',
        )


# See above for @ignore_warnings() discussion.
@ignore_warnings(DeprecationWarning)
def test_door_typehint_is_bearable(iter_hints_piths_meta) -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.is_bearable` tester method.

    This test intentionally tests only the core functionality of this tester to
    preserve Don't Repeat Yourself (DRY). This tester internally defers most of
    its work to the procedural :class:`beartype.door.is_bearable` tester,
    already exhaustively tested by preceding unit tests.

    Parameters
    ----------
    iter_hints_piths_meta : Callable[[], Iterable[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPithMetadata]]
        Factory function creating and returning a generator iteratively yielding
        ``HintPithMetadata`` instances, each describing a sample type hint
        exercising an edge case in the :mod:`beartype` codebase paired with a
        related object either satisfying or violating that hint.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import BeartypeDoorNonpepException
    from beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta import (
        PithUnsatisfiedMetadata)
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
            hint_pith_meta.pith_meta, PithUnsatisfiedMetadata)

        #FIXME: Remove this suppression *AFTER* improving "TypeHint" to support
        #all currently unsupported type hints.
        with suppress(BeartypeDoorNonpepException):
            # Assert this tester returns the expected boolean when passed this
            # pith and hint.
            assert TypeHint(hint).is_bearable(pith, conf=conf) is (
                is_bearable_expected)
