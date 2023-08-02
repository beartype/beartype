#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **string munging** utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextmunge` submodule.
'''

# ....................{ IMPORTS                            }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ case                       }....................
def test_uppercase_str_char_first():
    '''
    Test the :func:`beartype._util.text.utiltextmunge.uppercase_str_char_first`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextmunge import uppercase_str_char_first
    from pytest import raises

    # Assert this munger returns the expected string when passed a string.
    assert uppercase_str_char_first(text='beArTyPe') == "BeArTyPe"
    assert uppercase_str_char_first(text="<bear>") == "<bear>"
    assert uppercase_str_char_first(text="") == ""

    # Assert this munger raises the expected exception when passed a non-string.
    with raises(AssertionError):
        uppercase_str_char_first(7)

# ....................{ TESTS ~ number                     }....................
def test_number_str_lines():
    '''
    Test the :func:`beartype._util.text.utiltextmunge.number_str_lines`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextmunge import number_str_lines
    from pytest import raises
    from re import search

    with raises(AssertionError):
        number_str_lines(7)

    # No lines to split.
    assert number_str_lines(text="") == ""

    NEWLINE_COUNT = 20
    base_string = 'bears, beats, battlestar galactica'
    total_string = f'{base_string}\n' * NEWLINE_COUNT

    numbered_lines_string = number_str_lines(total_string)
    numbered_lines_string = numbered_lines_string.splitlines()

    # Confirm the function preserves newlines as is.
    assert len(numbered_lines_string) == NEWLINE_COUNT

    # Confirm the base string is prefixed with something.
    for line_number in range(NEWLINE_COUNT):
        assert search(
            pattern=fr'(?<!^){base_string}$',
            string=numbered_lines_string[line_number],
        ) is not None

# ....................{ TESTS ~ replace                    }....................
def test_replace_str_substrs():
    '''
    Test the :func:`beartype._util.text.utiltextmunge.replace_str_substrs`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextmunge import replace_str_substrs
    from beartype.roar._roarexc import _BeartypeUtilTextException
    from pytest import raises

    with raises(AssertionError):
        replace_str_substrs(text=7, old='Oh No!', new='A non-str value')

    with raises(AssertionError):
        replace_str_substrs(text='Oh No!', old=7.0, new='is a non-str value')

    with raises(AssertionError):
        replace_str_substrs(text='Oh No!', old='A non-str value of ', new=7)

    with raises(_BeartypeUtilTextException):
        replace_str_substrs(
            text="OG Beartype",
            old="I DON'T EXIST!",
            new="Therefore I do not think.",
        )

    assert replace_str_substrs(
        text="I do not think, therefore I am.",
        old="do not think",
        new="think",
    ) == "I think, therefore I am."

# ....................{ TESTS ~ [pre|suf]fix               }....................
def test_suffix_str_unless_suffixed():
    '''
    Test the
    :func:`beartype._util.text.utiltextmunge.suffix_str_unless_suffixed`
    function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.text.utiltextmunge import suffix_str_unless_suffixed
    from pytest import raises

    # ....................{ LOCALS                         }....................
    not_suffixed_text = "somefile"
    suffix = ".py"

    # ....................{ PASS                           }....................
    suffixed_text = suffix_str_unless_suffixed(
        text=not_suffixed_text, suffix=suffix)

    # Confirm text is suffixed
    assert suffixed_text == "somefile.py"

    # Attempt to reapply the suffix
    suffix_str_unless_suffixed(text=suffixed_text, suffix=suffix)

    # Confirm the text is unchanged
    assert suffixed_text == "somefile.py"

    # ....................{ FAIL                           }....................
    with raises(AssertionError):
        suffix_str_unless_suffixed(text=7, suffix="That's not a string!")

    with raises(AssertionError):
        suffix_str_unless_suffixed(text="HEY! You're not a string!", suffix=7)

# ....................{ TESTS ~ truncate                   }....................
def test_truncate_str():
    '''
    Test the :func:`beartype._util.text.utiltextmunge.truncate_str` function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextmunge import truncate_str

    # Assert that truncating the empty string returns the empty string.
    assert truncate_str(text='') == ''
    assert truncate_str(text='', max_len=0) == ''

    # Assert that truncating extremely short strings (i.e., less than four
    # characters in length) truncates those strings to the desired maximum
    # length *WITHOUT* injecting an ellipsis into that truncation.
    assert truncate_str(text='Se',   max_len=1) == 'S'
    assert truncate_str(text='Sen',  max_len=2) == 'Se'
    assert truncate_str(text='Sent', max_len=3) == 'Sen'

    # Assert that truncating fairly short strings (i.e., less than seven
    # characters in length but more than four characters in length) containing
    # *NO* punctuation truncates those strings to the desired maximum length by
    # replacing all trailing characters in those strings with an ellipsis.
    assert truncate_str(text='Sent ',   max_len=4) == 'S...'
    assert truncate_str(text='Sent t',  max_len=5) == 'Se...'
    assert truncate_str(text='Sent to', max_len=6) == 'Sen...'

    # Assert that truncating fairly short strings containing one non-period
    # punctuation character truncates those strings to the desired maximum
    # length by replacing all trailing characters in those strings up to but
    # *NOT* including that non-period punctuation character with an ellipsis.
    assert truncate_str(text='Sent>',   max_len=4) == '...>'
    assert truncate_str(text='Sent >',  max_len=5) == 'S...>'
    assert truncate_str(text='Sent t>', max_len=6) == 'Se...>'

    # Assert that truncating a fairly short string containing two or more
    # non-period punctuation characters to a length larger than the length of
    # an ellipsis (i.e., 3 characters) plus the length of those non-period
    # punctuation characters (e.g., 2 in this case) truncates that string in a
    # reasonable but complex manner too complex to detail here. *sigh* 
    assert truncate_str(text='Sent/>', max_len=4) == '...>'

    # Assert that truncating fairly short strings containing two or more
    # non-period punctuation characters truncates those strings to the desired
    # maximum length by replacing all trailing characters in those strings up to
    # but *NOT* including those non-period punctuation characters with an
    # ellipsis.
    assert truncate_str(text='Sent />',   max_len=5) == '.../>'
    assert truncate_str(text='Sent t/>',  max_len=6) == 'S.../>'
    assert truncate_str(text='Sent to/>', max_len=7) == 'Se.../>'

    # Assert that truncating fairly short strings suffixed by one period
    # followed by two or more non-period punctuation characters truncates those
    # strings to the desired maximum length by replacing all trailing characters
    # in those strings up to and including those periods but *NOT* those
    # non-period punctuation characters with an ellipsis.
    assert truncate_str(text='Sen."?',    max_len=5) == '..."?'
    assert truncate_str(text='Sent."?',   max_len=6) == 'S..."?'
    assert truncate_str(text='Sent ."?',  max_len=7) == 'Se..."?'
    assert truncate_str(text='Sent t."?', max_len=8) == 'Sen..."?'

    # Assert that truncating fairly short strings suffixed by an ellipsis
    # truncates those strings to the desired maximum length while preserving
    # that ellipsis as is.
    assert truncate_str(text='Se...',   max_len=4) == 'S...'
    assert truncate_str(text='Se....',  max_len=4) == 'S...'
    assert truncate_str(text='Sen...',  max_len=4) == 'S...'
    assert truncate_str(text='Sent...', max_len=4) == 'S...'
