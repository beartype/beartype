#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Testable path factories** (i.e., callables creating and returning
:class:`pathlib.Path` instances encapsulating testing-specific paths).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.pytroar import BeartypeTestPathException
from pathlib import Path

# ....................{ RELATIVIZERS                       }....................
# These functions are explicitly camelcased to enable their future refactoring
# into actual classes.

def DirRelative(parent_dir: Path, relative_dirname: str) -> Path:
    '''
    Concrete platform-agnostic :mod:`Path` object encapsulating the absolute
    dirname of a directory relative to the passed :mod:`Path` object
    encapsulating an arbitrary directory if found *or* raise an exception
    otherwise.

    Parameters
    ----------
    parent_dir : Path
        :mod:`Path` encapsulating an arbitrary **parent directory** (i.e.,
        directory containing the subdirectory to be returned).
    relative_dirname : str
        Relative dirname of this subdirectory relative to this parent
        directory.

    Returns
    ----------
    Path
        :mod:`Path` directory relative to the passed :mod:`Path` directory.

    Raises
    ----------
    BeartypeTestPathException
        If this path exists but is either:

        * *Not* a directory.
        * A directory *not* satisfying the expected filesystem structure.
    FileNotFoundError
        If this path does *not* exist.
    RuntimeError
        If this path exists but whose resolution to a physical path requires
        resolving one or more cyclic symbolic links inducing an infinite loop.
    '''
    assert isinstance(parent_dir, Path), (
        f'{repr(parent_dir)} not "pathlib.Path" object.')
    assert isinstance(relative_dirname, str), (
        f'{repr(relative_dirname)} not string.')

    # Path encapsulating the relative dirname of this subdirectory relative to
    # this parent directory, which has yet to be validated.
    subdir_unresolved = parent_dir / relative_dirname

    # Canonicalize this relative dirname into an absolute dirname if this path
    # exists *OR* raise a "FileNotFoundError" or "RuntimeError" exception
    # otherwise.
    subdir = subdir_unresolved.resolve()

    # If this path is *NOT* a directory, raise an exception.
    if not subdir.is_dir():
        raise BeartypeTestPathException(f'Directory "{subdir}" not found.')
    # Else, this path is a directory.

    # Return this directory.
    return subdir


def FileRelative(parent_dir: Path, relative_filename: str) -> Path:
    '''
    Concrete platform-agnostic :mod:`Path` object encapsulating the absolute
    filename of a file relative to the passed :mod:`Path` object encapsulating
    an arbitrary directory if found *or* raise an exception otherwise.

    Parameters
    ----------
    parent_dir : Path
        :mod:`Path` encapsulating an arbitrary **parent directory** (i.e.,
        directory containing the file to be returned).
    relative_filename : str
        Relative filename of this file relative to this parent directory.

    Returns
    ----------
    Path
        :mod:`Path` file relative to the passed :mod:`Path` directory.

    Raises
    ----------
    BeartypeTestPathException
        If this path exists but is either:

        * *Not* a directory.
        * A directory *not* satisfying the expected filesystem structure.
    FileNotFoundError
        If this path does *not* exist.
    RuntimeError
        If this path exists but whose resolution to a physical path requires
        resolving one or more cyclic symbolic links inducing an infinite loop.
    '''
    assert isinstance(parent_dir, Path), (
        f'{repr(parent_dir)} not "pathlib.Path" object.')
    assert isinstance(relative_filename, str), (
        f'{repr(relative_filename)} not string.')

    # Path encapsulating the relative filename of this file relative to this
    # parent directory, which has yet to be validated.
    file_unresolved = parent_dir / relative_filename

    # Canonicalize this relative filename into an absolute filename if this
    # path exists *OR* raise a "FileNotFoundError" or "RuntimeError" exception
    # otherwise.
    file = file_unresolved.resolve()

    # If this path is *NOT* a file, raise an exception.
    if not file.is_file():
        raise BeartypeTestPathException(f'File "{file}" not found.')
    # Else, this path is a file.

    # Return this file.
    return file
