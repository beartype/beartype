# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **ANSI utilities** (i.e., low-level callables handling ANSI escape
sequences colouring arbitrary strings).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from re import compile as re_compile

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_text_ansi(text: str) -> bool:
    '''
    ``True`` if the passed text contains one or more ANSI escape sequences.

    Parameters
    ----------
    text : str
        Text to be tested for ANSI.

    Returns
    ----------
    bool
        ``True`` only if this text contains one or more ANSI escape sequences.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Return true only this compiled regex matching ANSI escape sequences
    # returns a non-"None" match object when passed this text.
    return _ANSI_REGEX.search(text) is not None

# ....................{ STRIPPERS                          }....................
#FIXME: Unit test us up, please.
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
