# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide terminal **text color** control utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ CONSTANTS ~                        }....................
# Windows command prompt does not support ANSI escape sequences, but the Windows
# terminal does and it is becoming the default terminal for Windows. So we add
# color control strings to all platforms.
COLOR_RED = '\033[31m'
COLOR_BLUE = '\033[34m'
COLOR_RESET = '\033[0m'


def error_color(text: str) -> str:
    '''
    Color the errors.
    '''

    return COLOR_RED + text + COLOR_RESET

def truth_color(text: str) -> str:
    '''
    Color the information of the truth.
    '''

    return COLOR_BLUE + text + COLOR_RESET
