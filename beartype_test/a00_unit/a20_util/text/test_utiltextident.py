#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python identifier** utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextident` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_die_unless_identifier() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextident.die_unless_identifier`
    exception-raiser.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilTextIdentifierException
    from beartype._util.text.utiltextident import die_unless_identifier
    from pytest import raises

    # Assert this raiser accepts an unqualified Python identifier prefixed by
    # an underscore and suffixed by a digit.
    die_unless_identifier('_the_lucy_poems_5')

    # Assert this raiser accepts a fully-qualified Python identifier containing
    # underscores and digits.
    die_unless_identifier('She_dwelt.among_the.untrodden.ways_2')

    # Assert this raiser rejects the empty string.
    with raises(_BeartypeUtilTextIdentifierException):
        die_unless_identifier('')

    # Assert this raiser rejects a non-empty string prefixed by a digit.
    with raises(_BeartypeUtilTextIdentifierException):
        die_unless_identifier('42147')

    # Assert this raiser rejects an unqualified Python identifier suffixed by a
    # non-empty string prefixed by a digit.
    with raises(_BeartypeUtilTextIdentifierException):
        die_unless_identifier('Sentient.6')


def test_is_identifier() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextident.is_identifier` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextident import is_identifier

    # Assert this tester accepts an unqualified Python identifier prefixed by
    # an underscore and suffixed by a digit.
    assert is_identifier('_the_lucy_poems_5') is True

    # Assert this tester accepts a fully-qualified Python identifier containing
    # underscores and digits.
    assert is_identifier('She_dwelt.among_the.untrodden.ways_2') is (
        True)

    # Assert this tester rejects the empty string.
    assert is_identifier('') is False

    # Assert this tester rejects a non-empty string prefixed by a digit.
    assert is_identifier('42147') is False

    # Assert this tester rejects an unqualified Python identifier suffixed by a
    # non-empty string prefixed by a digit.
    assert is_identifier('Sentient.6') is False
