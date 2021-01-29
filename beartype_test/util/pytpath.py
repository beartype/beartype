#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2021 by Cecil Curry.
# See "LICENSE" for further details.

'''
**:mod:`pytest` **path** (i.e., directory and file) utilities.**
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pathlib import Path
from beartype_test.util.pytroar import BeartypeTestPathException

# ....................{ GETTERS                           }....................
def get_repo_dir() -> Path:
    '''
    Concrete platform-agnostic :mod:`Path` object encapsulating this absolute
    dirname of this project's **repository directory** (i.e., directory
    containing both a ``.git/`` subdirectory and a subdirectory providing this
    project's package) if found *or* raise an exception otherwise.

    Returns
    ----------
    Path
        Concrete platform-agnostic object encapsulating the absolute dirname of
        this project's repository directory.

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
    # print(f'current module paths: {__package__} [{__file__}]')

    # Concrete platform-agnostic path encapsulating the absolute filename of
    # current module.
    MODULE_FILE = Path(__file__)

    # Concrete platform-agnostic path encapsulating the absolute dirname of the
    # package defining the current module.
    MODULE_PACKAGE_DIR = MODULE_FILE.parent

    # Concrete platform-agnostic path encapsulating the relative dirname of
    # this project's repository directory relative to the dirname of the
    # package defining the current module.
    #
    # Note that this path has *NOT* been validated to exist yet.
    REPO_DIR_UNRESOLVED = MODULE_PACKAGE_DIR.joinpath('../..')

    # Canonicalize this relative dirname into an absolute dirname if this path
    # exists *OR* raise a "FileNotFoundError" or "RuntimeError" exception
    # otherwise.
    REPO_DIR = REPO_DIR_UNRESOLVED.resolve()

    # If this path is *NOT* a directory, raise an exception.
    if not REPO_DIR.is_dir():
        raise BeartypeTestPathException(
            f'Project repository path {REPO_DIR} not directory.')
    # Else, this path is a directory.

    # Concrete platform-agnostic path encapsulating the absolute dirname
    # of the ".git/" subdirectory of this project's repository directory.
    REPO_GIT_DIR = REPO_DIR.joinpath('.git')

    # If this subdirectory either does *NOT* exist or is *NOT* a directory,
    # raise an exception.
    if not REPO_GIT_DIR.is_dir():
        raise BeartypeTestPathException(
            f'Project repository git subdirectory {REPO_GIT_DIR} not found.')
    # Else, this subdirectory exists.

    # Return this path.
    return REPO_DIR


def get_repo_readme_file() -> Path:
    '''
    Concrete platform-agnostic :mod:`Path` object encapsulating the absolute
    filename of this project's **readme file** (i.e., this project's
    front-facing ``README.rst`` file) if found *or* raise an exception
    otherwise.

    Note that the :meth:`Path.read_text` method of this object trivially yields
    the decoded plaintext contents of this file as a string.

    Returns
    ----------
    Path
        Concrete platform-agnostic object encapsulating the absolute filename
        of this project's readme file.

    Raises
    ----------
    BeartypeTestPathException
        If this path exists but is *NOT* a file.
    FileNotFoundError
        If this path does *not* exist.
    RuntimeError
        If this path exists but whose resolution to a physical path requires
        resolving one or more cyclic symbolic links inducing an infinite loop.
    '''

    # Concrete platform-agnostic path encapsulating this project's
    # repository directory.
    REPO_DIR = get_repo_dir()

    # Concrete platform-agnostic path encapsulating the absolute filename of
    # this project's readme file.
    REPO_README_FILE = REPO_DIR.joinpath('README.rst')

    # If this file either does *NOT* exist or is *NOT* a file, raise an
    # exception.
    if not REPO_README_FILE.is_file():
        raise BeartypeTestPathException(
            f'Project repository readme file {REPO_README_FILE} not found.')
    # Else, this file exists.

    # Return this path.
    return REPO_README_FILE
