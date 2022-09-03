# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide terminal **text colour** control utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import functools
import sys

# ....................{ CONSTANTS ~                        }....................
# Windows command prompt does not support ANSI escape sequences, but the Windows
# terminal does and it is becoming the default terminal for Windows. So we add
# colour control strings to all platforms.
COLOUR_RED = '\033[31m'
COLOUR_BLUE = '\033[34m'
COLOUR_RESET = '\033[0m'


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


def _plain_if_not_stdout(func):
    '''
    Decorator that returns the plain text if standard output is not attached to
    an interactive terminal.
    '''
    @functools.wraps(func)
    def wrapper(text: str) -> str:
        if _is_stdout_terminal_colourized():
            return func(text)
        return text

    return wrapper


@_plain_if_not_stdout
def error_colour(text: str) -> str:
    '''
    colour the errors.
    '''

    return COLOUR_RED + text + COLOUR_RESET


@_plain_if_not_stdout
def truth_colour(text: str) -> str:
    '''
    colour the information of the truth.
    '''

    return COLOUR_BLUE + text + COLOUR_RESET
