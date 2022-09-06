# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide terminal **text colour** control utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import sys

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_stdout_terminal() -> bool:
    '''
    ``True`` only if standard output is currently attached to an interactive
    terminal.

    See Also
    ----------
    https://stackoverflow.com/questions/3818511/how-to-tell-if-python-script-is-being-run-in-a-terminal-or-via-gui
        StackOverflow thread strongly inspiring this implementation.
    '''

    # One-liners for great justice.
    #
    # Note that:
    # * Input and output streams are *NOT* guaranteed to define the isatty()
    #   method. For safety, we defensively test for the existence of that method
    #   before deferring to that method.
    # * All popular terminals under Windows >= 10 -- including terminals bundled
    #   out-of-the-box with Windows -- now support ANSII escape sequences. Since
    #   older Windows versions are compelling security risks and thus ignorable
    #   for contemporary purposes, Windows no longer needs to be excluded from
    #   ANSII-based colourization. All praise Satya Nadella. \o/
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

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
def user_value_colour(text: str) -> str:
    '''
    Colour user values.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{COLOUR_YELLOW}{text}{COLOUR_RESET}'


def matched_colour(text: str) -> str:
    '''
    Colour the matched / correct types.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{TEXT_BOLD}{COLOUR_GREEN}{text}{COLOUR_RESET}'


def error_colour(text: str) -> str:
    '''
    Colour the errors.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{TEXT_BOLD}{COLOUR_RED}{text}{COLOUR_RESET}'


def truth_colour(text: str) -> str:
    '''
    Colour the information of the truth.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{TEXT_BOLD}{COLOUR_BLUE}{text}{COLOUR_RESET}'
