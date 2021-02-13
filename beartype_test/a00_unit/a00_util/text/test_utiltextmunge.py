#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2021 by Cecil Curry.
# See "LICENSE" for further details.

"""
**Beartype replace utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextmunge.py` submodule.
"""


# ....................{ IMPORTS                           }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# from pytest import raises

# ....................{ TESTS                             }....................
def test_uppercase_char_first():
    # Defer heavyweight imports.
    from pytest import raises

    from beartype._util.text.utiltextmunge import uppercase_char_first

    # Not a string
    with raises(AssertionError):
        uppercase_char_first(7)

    assert uppercase_char_first(text='beArTyPe') == "BeArTyPe"
    assert uppercase_char_first(text="<bear>") == "<bear>"
    assert uppercase_char_first(text="") == ""


def test_number_lines():
    # Defer heavyweight imports.
    from pytest import raises

    from beartype._util.text.utiltextmunge import number_lines

    with raises(AssertionError):
        number_lines(7)

    # No lines to split
    assert number_lines(text="") == ""

    # This is in essence "x == x" - I don't know if this adds
    # anything substantive...
    text = "bears, beats, battlestar galactica\n" * 20
    expected_result = "\n".join(
        '(line {:0>4d}) {}'.format(line_no, line_text)
        for line_no, line_text in enumerate(text.splitlines(), start=1))

    assert number_lines(text) == expected_result


def test_replace_str_substrs():
    # Defer heavyweight imports.
    from pytest import raises

    from beartype._util.text.utiltextmunge import replace_str_substrs
    from beartype.roar import _BeartypeUtilTextException

    with raises(AssertionError):
        replace_str_substrs(text=7, old='Oh No!', new='A non-str value')
        replace_str_substrs(text='Oh No!', old=7.0, new='is a non-str value')
        replace_str_substrs(text='Oh No!', old='A non-str value of ', new=7)

    with raises(_BeartypeUtilTextException):
        replace_str_substrs(text="OG Beartype",
                            old="I DON'T EXIST!",
                            new="Therefore I do not think.")

    assert replace_str_substrs(text="I do not think, therefore I am.",
                               old="do not think",
                               new="think") == "I think, therefore I am."


def test_suffix_unless_suffixed():
    # Defer heavyweight imports.
    from pytest import raises

    from beartype._util.text.utiltextmunge import suffix_unless_suffixed

    with raises(AssertionError):
        suffix_unless_suffixed(text=7, suffix="That's not a string!")
        suffix_unless_suffixed(text="HEY! You're not a string!", suffix=7)

    not_suffixed_text = "somefile"
    suffix = ".py"
    suffixed_text = suffix_unless_suffixed(text=not_suffixed_text, suffix=suffix)

    # Confirm text is suffixed
    assert suffixed_text == "somefile.py"

    # Attempt to reapply the suffix
    suffix_unless_suffixed(text=suffixed_text, suffix=suffix)

    # Confirm the text is unchanged
    assert suffixed_text == "somefile.py"
