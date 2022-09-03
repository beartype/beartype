# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide terminal **text colour** control utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from sys import platform, stdout


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
    return hasattr(stdout, 'isatty') and stdout.isatty()


def _is_stdout_terminal_colourized() -> bool:
    '''
    ``True`` only if standard output is attached to an
    interactive terminal that supports ANSII colour codes.
    '''

    # *BOOM.*
    return _is_stdout_terminal() and platform != 'win32'


def error_colour(text: str) -> str:
    '''
    colour the errors.
    '''

    return COLOUR_RED + text + COLOUR_RESET

def truth_colour(text: str) -> str:
    '''
    colour the information of the truth.
    '''

    return COLOUR_BLUE + text + COLOUR_RESET
