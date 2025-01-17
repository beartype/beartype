#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Python expression indentation substring unit tests.**

This submodule unit tests the public API of the public
:mod:`beartype._data.hint.pep.sign.datapepsignset` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_data_indent_level_to_code() -> None:
    '''
    Test the :obj:`beartype._data.code.datacodeindent.INDENT_LEVEL_TO_CODE`
    dictionary singleton.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._data.code.datacodeindent import INDENT_LEVEL_TO_CODE
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this dictionary indexed by various indentation levels creates and
    # returns the expected indentation string constants.
    assert INDENT_LEVEL_TO_CODE[1] == '    '
    assert INDENT_LEVEL_TO_CODE[2] == '        '
    assert INDENT_LEVEL_TO_CODE[3] == '            '

    # Assert this dictionary internally caches these constants.
    assert INDENT_LEVEL_TO_CODE[1] is INDENT_LEVEL_TO_CODE[1]
    assert INDENT_LEVEL_TO_CODE[2] is INDENT_LEVEL_TO_CODE[2]
    assert INDENT_LEVEL_TO_CODE[3] is INDENT_LEVEL_TO_CODE[3]

    # ....................{ FAIL                           }....................
    # Assert that attempting to index this dictionary by non-integer
    # indentation levels raises the expected exception.
    with raises(AssertionError):
        INDENT_LEVEL_TO_CODE[2.34]

    # Assert that attempting to index this dictionary by non-positive
    # indentation levels raises the expected exception.
    with raises(AssertionError):
        INDENT_LEVEL_TO_CODE[0]
    with raises(AssertionError):
        INDENT_LEVEL_TO_CODE[-1]
