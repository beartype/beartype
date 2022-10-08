# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **text colour utilities** (i.e., low-level callables conditionally
accenting caller-defined strings with ANSI escape sequences colourizing those
strings when printed to an ANSI-capable terminal).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: The structure of this submodule is fundamentally *DANGEROUS.* Why?
#Because the *ONLY* things @beartype should be colourizing are type-checking
#violations. Even that is a bit of a big ask for users, but it's largely worth
#it for the improved readability from tooling that supports ANSI in exceptions.
#@beartype absolutely should *NOT* be colourizing anything else. Ergo, the
#subset of this submodule that colourizes (e.g., the "colour_"-prefixed
#functions) should be shifted into an error handling-specific submodule to
#prevent general-purpose logic in the @beartype codebase from erroneously
#colourizing general-purpose strings -- say:
#* A new "beartype._decor._error._util._utilerrorcolour" submodule.
#
#Note that general-purpose ANSI functionality (e.g., the strip_text_ansi()
#function) should remain preserved as is in this submodule for usability.

# ....................{ IMPORTS                            }....................
from beartype._util.os.utilostty import is_stdout_terminal
from re import compile as re_compile

# ....................{ CONSTANTS ~ ANSI                   }....................
if is_stdout_terminal():
    _COLOUR_GREEN = '\033[92m'
    _COLOUR_RED = '\033[31m'
    _COLOUR_BLUE = '\033[34m'
    _COLOUR_YELLOW = '\033[33m'
    _COLOUR_RESET = '\033[0m'
    _STYLE_BOLD = '\033[1m'
else:
    _COLOUR_GREEN = ''
    _COLOUR_RED = ''
    _COLOUR_BLUE = ''
    _COLOUR_YELLOW = ''
    _COLOUR_RESET = ''
    _STYLE_BOLD = ''

# ....................{ COLOURIZERS                        }....................
def error_colour(text: str) -> str:
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

    return f'{_STYLE_BOLD}{_COLOUR_RED}{text}{_COLOUR_RESET}'


def matched_colour(text: str) -> str:
    '''
    Colour the passed substring as a matched (i.e., correct) type.

    Parameters
    ----------
    text : str
        Text to be coloured as matched.

    Returns
    ----------
    str
        This text coloured as matched.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{_STYLE_BOLD}{_COLOUR_GREEN}{text}{_COLOUR_RESET}'


def colour_hint(text: str) -> str:
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

    return f'{_STYLE_BOLD}{_COLOUR_BLUE}{text}{_COLOUR_RESET}'


def colour_repr(text: str) -> str:
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

    return f'{_COLOUR_YELLOW}{text}{_COLOUR_RESET}'

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
