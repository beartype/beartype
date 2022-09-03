# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide terminal **text colour** control utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import sys


def _is_stdout_terminal() -> bool:
    '''
    ``True`` only if standard output is currently attached
    to an interactive terminal.

    See also this StackOverflow thread:
        https://stackoverflow.com/questions/3818511/how-to-tell-if-python-script-is-being-run-in-a-terminal-or-via-gui
    '''

    # One-liners for great justice.
    #
    # Note that input streams are *NOT* guaranteed to define
    # the isatty() method. Defensively test for the existence of
    # that method before deferring to that method.
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def _is_stdout_terminal_colourized() -> bool:
    '''
    ``True`` only if standard output is attached to an
    interactive terminal that supports ANSII colour codes.
    '''

    # *BOOM.*
    return _is_stdout_terminal() and sys.platform != 'win32'


# ....................{ CONSTANTS ~ ANSI escape sequences  }....................
if _is_stdout_terminal_colourized():
    COLOUR_GREEN = '\033[92m'
    COLOUR_RED = '\033[31m'
    COLOUR_BLUE = '\033[34m'
    COLOUR_YELLOW = '\033[33m'
    COLOUR_RESET = '\033[0m'
    TEXT_BOLD = '\033[1m'
else:
    COLOUR_GREEN = ''
    COLOUR_RED = ''
    COLOUR_YELLOW = ''
    COLOUR_BLUE = ''
    COLOUR_RESET = ''
    TEXT_BOLD = ''


def user_value_colour(text: str) -> str:
    '''
    Colour user values.
    '''

    return f"{COLOUR_YELLOW}{text}{COLOUR_RESET}"


def matched_colour(text: str) -> str:
    '''
    Colour the matched / correct types.
    '''

    return f"{TEXT_BOLD}{COLOUR_GREEN}{text}{COLOUR_RESET}"


def error_colour(text: str) -> str:
    '''
    Colour the errors.
    '''

    return f"{COLOUR_RED}{text}{COLOUR_RESET}"


def truth_colour(text: str) -> str:
    '''
    Colour the information of the truth.
    '''

    return f"{TEXT_BOLD}{COLOUR_BLUE}{text}{COLOUR_RESET}"
