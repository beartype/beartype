#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **pathable utilities** (i.e., callables querying commands residing
in the current ``${PATH}`` and hence executable by specifying merely their
basename rather than either relative or absolute path).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from shutil import which

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_pathable(command_basename: str) -> bool:
    '''
    ``True`` only if a **pathable** (i.e., external command with the passed
    basename corresponding to an executable file in the current ``${PATH}``)
    exists.

    Caveats
    ----------
    For safety, avoid appending the passed basename by a platform-specific
    filetype -- especially, a Windows-specific filetype. On that platform, this
    function iteratively appends this basename by each filetype associated with
    executable files listed by the ``%PATHEXT%`` environment variable (e.g.,
    ``.bat``, ``.cmd``, ``.com``, ``.exe``) until the resulting basename is
    that of an executable file in the current ``%PATH%``.

    Parameters
    ----------
    command_basename : str
        Basename of the command to be searched for.

    Returns
    ----------
    bool
        ``True`` only if this pathable exists.

    Raises
    ----------
    BeartypeTestPathException
        If the passed string is *not* a basename (i.e., contains one or more
        directory separators).
    '''
    assert isinstance(command_basename, str), (
        f'{repr(command_basename)} not string.')

    # Defer test-specific imports.
    from beartype_test._util.path.pytpathname import die_unless_basename

    # If this string is *NOT* a pure basename, raise an exception.
    die_unless_basename(command_basename)

    # Return whether this command exists or not.
    return which(command_basename) is not None
