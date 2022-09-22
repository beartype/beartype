# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **text colour utilities** (i.e., low-level callables conditionally
accenting caller-defined strings with ANSI escape sequences colourizing those
strings when printed to an ANSI-capable terminal).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.os.utilostty import is_stdout_terminal
from re import (
    compile as re_compile,
    sub as re_sub,
)

# ....................{ CONSTANTS ~ ANSI                   }....................
if is_stdout_terminal():
    COLOUR_GREEN = '\033[92m'
    COLOUR_RED = '\033[31m'
    COLOUR_BLUE = '\033[34m'
    COLOUR_YELLOW = '\033[33m'
    COLOUR_RESET = '\033[0m'
    TEXT_BOLD = '\033[1m'
else:
    COLOUR_GREEN = ''
    COLOUR_RED = ''
    COLOUR_BLUE = ''
    COLOUR_YELLOW = ''
    COLOUR_RESET = ''
    TEXT_BOLD = ''

# ....................{ COLOURIZERS                        }....................
def error_colour(text: str) -> str:
    '''
    Colour the errors.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{TEXT_BOLD}{COLOUR_RED}{text}{COLOUR_RESET}'


def matched_colour(text: str) -> str:
    '''
    Colour the matched / correct types.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{TEXT_BOLD}{COLOUR_GREEN}{text}{COLOUR_RESET}'


def truth_colour(text: str) -> str:
    '''
    Colour the information of the truth.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{TEXT_BOLD}{COLOUR_BLUE}{text}{COLOUR_RESET}'


def user_value_colour(text: str) -> str:
    '''
    Colour user values.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{COLOUR_YELLOW}{text}{COLOUR_RESET}'

# ....................{ STRIPPERS                          }....................
def strip_text_ansi(text: str) -> str:
    '''
    Strip all ANSI escape sequences from the passed string.

    Parameters
    ----------
    text : str
        Text to be stripped of ANSI.

    Returns
    ----------
    str
        This text stripped of ANSI.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Glory be to the one liner that you are about to read.
    return _ANSI_REGEX.sub('', text)

# ....................{ PRIVATE ~ constants                }....................
_ANSI_REGEX = re_compile(r'\033\[[0-9;?]*[A-Za-z]')
'''
Compiled regular expression matching a single ANSI escape sequence.
'''
