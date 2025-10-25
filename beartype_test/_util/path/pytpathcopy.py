#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-specific **path copy utilities** (i.e., low-level callables non-recursively
copying files and recursively copying directories from source to target paths).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ EXCEPTIONS ~ basename              }....................
#FIXME: Unit test us up, please.
def die_unless_basename(pathname: str) -> None:
    '''
    Raise an exception unless the passed pathname is a **pure basename** (i.e.,
    contains one or more directory separators).

    Parameters
    ----------
    pathname : str
        Pathname to be validated.

    Raises
    ------
    beartype_test._util.pytroar.BeartypeTestPathException
        If this pathname is *not* a pure basename.

    See Also
    --------
    :func:`.is_basename`
        Further details.
    '''

    # Defer test-specific imports.
    from beartype_test._util.pytroar import BeartypeTestPathException

    # If this pathname is *NOT* a pure basename, raise an exception.
    if not is_basename(pathname):
        raise BeartypeTestPathException(
            f'Pathname "{pathname}" not pure basename '
            f'(i.e., contains one or more "{DIRNAME_DELIMITER}" '
            f'directory separator characters).'
        )

# ....................{ TESTERS ~ basename                 }....................
#FIXME: Unit test us up, please.
def is_basename(pathname: str) -> bool:
    '''
    :data:`True` only if the passed pathname is a **pure basename** (i.e.,
    contains no directory separators and hence no directory components).

    Parameters
    ----------
    pathname : str
        Pathname to be tested.

    Returns
    ----------
    bool
        :data:`True` only if this pathname is a pure basename.
    '''
    assert isinstance(pathname, str), f'{repr(pathname)} not string.'

    # One-liners justify college education. *OR DO THEY*!?!?
    return DIRNAME_DELIMITER not in pathname
