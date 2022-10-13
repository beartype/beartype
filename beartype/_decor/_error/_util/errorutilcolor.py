# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype exception message color utilities** (i.e., low-level callables
conditionally accenting type-checking violation messages with ANSI escape
sequences colouring those strings when configured to do so by the
:func:`beartype.beartype`-decorated callables raising those violations).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.os.utilostty import is_stdout_terminal
from re import compile as re_compile

# ....................{ CONSTANTS ~ ANSI                   }....................
if is_stdout_terminal():
    _COLOR_GREEN = '\033[92m'
    _COLOR_RED = '\033[31m'
    _COLOR_BLUE = '\033[34m'
    _COLOR_YELLOW = '\033[33m'
    _COLOR_RESET = '\033[0m'
    _STYLE_BOLD = '\033[1m'
else:
    _COLOR_GREEN = ''
    _COLOR_RED = ''
    _COLOR_BLUE = ''
    _COLOR_YELLOW = ''
    _COLOR_RESET = ''
    _STYLE_BOLD = ''

# ....................{ COLOURIZERS                        }....................
def color_error(text: str) -> str:
    '''
    Colour the passed substring as an error.

    Parameters
    ----------
    text : str
        Text to be coloured as an error.

    Returns
    ----------
    str
        This text coloured as an error.
    '''

    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{_STYLE_BOLD}{_COLOR_RED}{text}{_COLOR_RESET}'


def color_hint(text: str) -> str:
    '''
    Colour the passed substring as a PEP-compliant type hint.

    Parameters
    ----------
    text : str
        Text to be coloured as a type hint.

    Returns
    ----------
    str
        This text coloured as a type hint.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{_STYLE_BOLD}{_COLOR_BLUE}{text}{_COLOR_RESET}'


def color_repr(text: str) -> str:
    '''
    Colour the passed substring as a **representation** (i.e., machine-readable
    string returned by the :func:`repr` builtin).

    Parameters
    ----------
    text : str
        Text to be coloured as a representation.

    Returns
    ----------
    str
        This text coloured as a representation.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{_COLOR_YELLOW}{text}{_COLOR_RESET}'


def color_type(text: str) -> str:
    '''
    Colour the passed substring as a simple class.

    Parameters
    ----------
    text : str
        Text to be coloured as a simple class.

    Returns
    ----------
    str
        This text coloured as a simple class.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{_STYLE_BOLD}{_COLOR_GREEN}{text}{_COLOR_RESET}'
