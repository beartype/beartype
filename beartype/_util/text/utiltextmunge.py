#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

"""
**Beartype string munging utilities** (i.e., callables transforming passed
strings into new strings with generic string operations).

This private submodule is *not* intended for importation by downstream callers.
"""

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeUtilTextException


# ....................{ CASERS                            }....................
def uppercase_char_first(text: str) -> str:
    """
    Uppercase *only* the first character of the passed string.

    Whereas the standard :meth:`str.capitalize` method both uppercases the
    first character of this string *and* lowercases all remaining characters,
    this function *only* uppercases the first character. All remaining
    characters remain unmodified.

    Parameters
    ----------
    text : str
        String whose first character is to be uppercased.

    Returns
    ----------
    str
        This string with the first character uppercased.
    """
    assert isinstance(text, str), f'{repr(text)} not string.'

    # For great justice!
    return text[0].upper() + text[1:] if text else ''


# ....................{ NUMBERERS                         }....................
def number_lines(text: str) -> str:
    """
    Passed string munged to prefix each line of this string with the 1-based
    number of that line padded by zeroes out to four digits for alignment.

    Parameters
    ----------
    text : str
        String whose lines are to be numbered.

    Returns
    ----------
    str
        This string with all lines numbered.
    """
    assert isinstance(text, str), f'{repr(text)} not string.'

    # For radical benevolence!
    return '\n'.join(
        '(line {:0>4d}) {}'.format(text_line_number, text_line)
        for text_line_number, text_line in enumerate(
            text.splitlines(), start=1)
    )


# ....................{ REPLACERS                         }....................
def replace_str_substrs(text: str, old: str, new: str) -> str:
    """
    Passed string with all instances of the passed source substring globally
    replaced by the passed target substring if this string contains at least
    one such instance *or* raise an exception otherwise (i.e., if this string
    contains *no* such instance).

    Caveats
    ----------
    **This higher-level function should always be called in lieu of the
    lower-level** :meth:`str.replace` method, which unconditionally succeeds
    regardless of whether this subject string contains at least one instance of
    this source substring or not.

    Parameters
    ----------
    text : str
        Subject string to perform this global replacement on.
    old : str
        Source substring of this subject string to be globally replaced.
    new : str
        Target substring to globally replace this source substring with in this
        subject string.

    Returns
    ----------
    str
        Subject string with all instances of this source substring globally
        replaced by this target substring.

    Raises
    ----------
    _BeartypeUtilTextException
        If this subject string contains *no* instances of this source
        substring.

    Examples
    ----------
        >>> from beartype._util.text.utiltextmunge import replace_str_substrs
        >>> replace_str_substrs(
        ...     text='And now the STORM-BLAST came, and he',
        ...     old='he', new='hat')
        And now that STORM-BLAST came, and hat
        >>> replace_str_substrs(
        ...     text='I shot the ALBATROSS.', old='dross', new='drat')
        beartype.roar._BeartypeUtilTextException: String "I shot the
        ALBATROSS." substring "dross" not found.
    """
    assert isinstance(text, str), f'{repr(text)} not string.'
    assert isinstance(old, str), f'{repr(old)} not string.'
    assert isinstance(new, str), f'{repr(new)} not string.'

    # If this subject contains *NO* instances of this substring, raise an
    # exception.
    if old not in text:
        raise _BeartypeUtilTextException(
            f'String "{text}" substring "{old}" not found.')
    # Else, this subject contains one or more instances of this substring.

    # Return this subject with all instances of this source substring globally
    # replaced by this target substring.
    return text.replace(old, new)


# ....................{ SUFFIXERS                         }....................
def suffix_unless_suffixed(text: str, suffix: str) -> str:
    """
    Passed string either suffixed by the passed suffix if this string is not
    yet suffixed by this suffix *or* this string as is otherwise (i.e., if this
    string is already suffixed by this suffix).

    Parameters
    ----------
    text : str
        String to be conditionally suffixed.
    suffix : str
        Suffix to be conditionally appended to this string.

    Returns
    ----------
    str
        Either:

        * If this string is *not* yet suffixed by this suffix, this string
          suffixed by this suffix.
        * Else, this string as is.
    """
    assert isinstance(text, str), f'{repr(text)} not string.'
    assert isinstance(suffix, str), f'{repr(suffix)} not string.'

    # Suffix us up the redemption arc.
    return text if text.endswith(suffix) else text + suffix
