# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **ANSI utilities** (i.e., low-level callables handling ANSI escape
sequences colouring arbitrary strings).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from re import compile as re_compile

# ....................{ CONSTANTS                          }....................
ANSI_RESET = '\033[0m'
'''
ANSI escape sequence resetting the effect of all prior ANSI sequence sequences,
effectively "undoing" all colors and styles applied by those sequences.
'''

# ....................{ CONSTANTS ~ color                  }....................
COLOR_GREEN = '\033[92m'
'''
ANSI escape sequence colouring all subsequent characters as green.
'''


COLOR_RED = '\033[31m'
'''
ANSI escape sequence colouring all subsequent characters as red.
'''


COLOR_BLUE = '\033[34m'
'''
ANSI escape sequence colouring all subsequent characters as blue.
'''


COLOR_YELLOW = '\033[33m'
'''
ANSI escape sequence colouring all subsequent characters as yellow.
'''

# ....................{ CONSTANTS ~ style                  }....................
STYLE_BOLD = '\033[1m'
'''
ANSI escape sequence stylizing all subsequent characters as bold.
'''

# ....................{ TESTERS                            }....................
def is_str_ansi(text: str) -> bool:
    '''
    :data:`True` only if the passed text contains one or more ANSI escape
    sequences.

    Parameters
    ----------
    text : str
        Text to be tested.

    Returns
    -------
    bool
        :data:`True` only if this text contains one or more ANSI escape
        sequences.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Return true only this compiled regex matching ANSI escape sequences
    # returns a non-"None" match object when passed this text.
    return _ANSI_REGEX.search(text) is not None

# ....................{ COLOURIZERS                        }....................
def color_error(text: str) -> str:
    '''
    Colour the passed substring as an error.

    Parameters
    ----------
    text : str
        Text to be coloured as an error.

    Returns
    -------
    str
        This text coloured as an error.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Infinite one-liner. Infinite possibility.
    return f'{STYLE_BOLD}{COLOR_RED}{text}{ANSI_RESET}'


def color_hint(text: str) -> str:
    '''
    Colour the passed substring as a PEP-compliant type hint.

    Parameters
    ----------
    text : str
        Text to be coloured as a type hint.

    Returns
    -------
    str
        This text coloured as a type hint.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # To boldly go where no one-liner has gone before.
    return f'{STYLE_BOLD}{COLOR_BLUE}{text}{ANSI_RESET}'


def color_repr(text: str) -> str:
    '''
    Colour the passed substring as a **representation** (i.e., machine-readable
    string returned by the :func:`repr` builtin).

    Parameters
    ----------
    text : str
        Text to be coloured as a representation.

    Returns
    -------
    str
        This text coloured as a representation.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Victory fanfare! One-liner enters the chat.
    return f'{COLOR_YELLOW}{text}{ANSI_RESET}'


def color_type(text: str) -> str:
    '''
    Colour the passed substring as a simple class.

    Parameters
    ----------
    text : str
        Text to be coloured as a simple class.

    Returns
    -------
    str
        This text coloured as a simple class.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # One-liner gonna one-liner. Ya, it's been a long night.
    return f'{STYLE_BOLD}{COLOR_GREEN}{text}{ANSI_RESET}'

# ....................{ STRIPPERS                          }....................
def strip_str_ansi(text: str) -> str:
    '''
    Strip *all* ANSI escape sequences from the passed string.

    Parameters
    ----------
    text : str
        Text to be stripped.

    Returns
    -------
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
