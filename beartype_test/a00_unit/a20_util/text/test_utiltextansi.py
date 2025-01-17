#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

"""
**Beartype ANSI utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextansi` submodule.
"""


# ....................{ IMPORTS                            }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_text_ansi() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextansi.is_str_ansi` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextansi import is_str_ansi

    # Assert that this tester returns false for a string containing *NO* ANSI.
    assert is_str_ansi('The sea-blooms and the oozy woods which wear') is False

    # Assert that this tester returns true for a string containing ANSI.
    assert is_str_ansi('The sapless foliage of the ocean, know\033[92m') is (
        True)

# ....................{ TESTS ~ stripper                   }....................
def test_strip_str_ansi() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextansi.strip_str_ansi` stripper.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextansi import strip_str_ansi

    # String containing *NO* ANSI.
    THY_VOICE = 'and suddenly grow gray with fear,'

    # Assert that this stripper preserves strings containing *NO* ANSI as is.
    assert strip_str_ansi(THY_VOICE) == THY_VOICE

    # Assert that this stripper strips *ALL* ANSI from strings containing ANSI.
    assert strip_str_ansi(f'\033[31m{THY_VOICE}\033[92m') == THY_VOICE
