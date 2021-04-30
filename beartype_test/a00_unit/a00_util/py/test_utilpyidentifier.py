#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python identifier** utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.py.utilpyidentifier` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_is_identifier_qualified() -> None:
    '''
    Test the :func:`beartype._util.py.utilpyidentifier.is_identifier_qualified`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.py.utilpyidentifier import is_identifier_qualified

    # Assert this tester accepts an unqualified Python identifier prefixed by
    # an underscore and suffixed by a digit.
    assert is_identifier_qualified('_the_lucy_poems_5') is True

    # Assert this tester accepts a fully-qualified Python identifier containing
    # underscores and digits.
    assert is_identifier_qualified('She_dwelt.among_the.untrodden.ways_2') is (
        True)

    # Assert this tester rejects the empty string.
    assert is_identifier_qualified('') is False

    # Assert this tester rejects a non-empty string prefixed by a digit.
    assert is_identifier_qualified('42147') is False

    # Assert this tester rejects an unqualified Python identifier suffixed by a
    # non-empty string prefixed by a digit.
    assert is_identifier_qualified('Sentient.6') is False
