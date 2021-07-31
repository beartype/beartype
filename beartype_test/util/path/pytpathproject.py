#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Test-specific **path** (e.g., directory, file) utilities.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pathlib import Path
from beartype._util.cache.utilcachecall import callable_cached
from beartype_test.util.pytroar import BeartypeTestPathException

# ....................{ GETTERS ~ dir                     }....................
@callable_cached
def get_project_dir() -> Path:
    '''
    Concrete platform-agnostic :mod:`Path` object encapsulating the absolute
    dirname of this project's **top-level directory** (i.e., directory
    containing both a ``.git/`` subdirectory and a subdirectory providing this
    project's package) if found *or* raise an exception otherwise.

    Returns
    ----------
    Path
        Concrete platform-agnostic object encapsulating the absolute dirname of
        this project's top-level directory.

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
    # this project's project directory relative to the dirname of the
    # package defining the current module.
    #
    # Note that this path has *NOT* been validated to exist yet.
    PROJECT_DIR_UNRESOLVED = MODULE_PACKAGE_DIR.joinpath('../../..')

    # Canonicalize this relative dirname into an absolute dirname if this path
    # exists *OR* raise a "FileNotFoundError" or "RuntimeError" exception
    # otherwise.
    PROJECT_DIR = PROJECT_DIR_UNRESOLVED.resolve()

    # If this path is *NOT* a directory, raise an exception.
    if not PROJECT_DIR.is_dir():
        raise BeartypeTestPathException(
            f'Project root {PROJECT_DIR} not directory.')
    # Else, this path is a directory.

    # Concrete platform-agnostic path encapsulating the absolute dirname
    # of the ".git/" subdirectory of this project's project directory.
    PROJECT_GIT_DIR = PROJECT_DIR.joinpath('.git')

    # If this subdirectory either does *NOT* exist or is *NOT* a directory,
    # raise an exception.
    if not PROJECT_GIT_DIR.is_dir():
        raise BeartypeTestPathException(
            f'Project git subdirectory {PROJECT_GIT_DIR} not found.')
    # Else, this subdirectory exists.

    # Return this path.
    return PROJECT_DIR


@callable_cached
def get_project_package_dir() -> Path:
    '''
    Concrete platform-agnostic :mod:`Path` object encapsulating the absolute
    dirname of this project's **top-level package** (i.e., directory providing
    this package's top-level package containing at least an ``__init__.py``
    file) if found *or* raise an exception otherwise.

    Returns
    ----------
    Path
        Concrete platform-agnostic object encapsulating the absolute dirname of
        this project's top-level package.

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

    # Concrete platform-agnostic path encapsulating this project's
    # project directory.
    PROJECT_DIR = get_project_dir()

    # Concrete platform-agnostic path encapsulating the absolute dirname of
    # this project's package.
    PROJECT_PACKAGE_DIR = PROJECT_DIR.joinpath('beartype')

    # If this directory either does *NOT* exist or is *NOT* a directory, raise
    # an exception.
    if not PROJECT_PACKAGE_DIR.is_dir():
        raise BeartypeTestPathException(
            f'Project package {PROJECT_PACKAGE_DIR} not found.')
    # Else, this file exists.

    # Return this path.
    return PROJECT_PACKAGE_DIR


@callable_cached
def get_project_test_package_dir() -> Path:
    '''
    Concrete platform-agnostic :mod:`Path` object encapsulating the absolute
    dirname of this project's **top-level test package** (i.e., directory
    providing this package's top-level test package containing at least an
    ``__init__.py`` file) if found *or* raise an exception otherwise.

    Returns
    ----------
    Path
        Concrete platform-agnostic object encapsulating the absolute dirname of
        this project's top-level test package.

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

    # Concrete platform-agnostic path encapsulating this project's
    # project directory.
    PROJECT_DIR = get_project_dir()

    # Concrete platform-agnostic path encapsulating the absolute dirname of
    # this project's package.
    PROJECT_TEST_PACKAGE_DIR = PROJECT_DIR.joinpath('beartype_test')

    # If this directory either does *NOT* exist or is *NOT* a directory, raise
    # an exception.
    if not PROJECT_TEST_PACKAGE_DIR.is_dir():
        raise BeartypeTestPathException(
            f'Project test package {PROJECT_TEST_PACKAGE_DIR} not found.')
    # Else, this file exists.

    # Return this path.
    return PROJECT_TEST_PACKAGE_DIR

# ....................{ GETTERS ~ file                    }....................
@callable_cached
def get_project_mypy_config_file() -> Path:
    '''
    Concrete platform-agnostic :mod:`Path` object encapsulating the absolute
    filename of this project's **mypy configuration file** (i.e., top-level
    ``.mypy.ini`` file) if found *or* raise an exception otherwise.

    Returns
    ----------
    Path
        Concrete platform-agnostic object encapsulating the absolute filename
        of this project's mypy configuration file.

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
    # project directory.
    PROJECT_DIR = get_project_dir()

    # Concrete platform-agnostic path encapsulating the absolute filename of
    # this project's mypy configuration file.
    PROJECT_MYPY_CONFIG_FILE = PROJECT_DIR.joinpath('.mypy.ini')

    # If this file either does *NOT* exist or is *NOT* a file, raise an
    # exception.
    if not PROJECT_MYPY_CONFIG_FILE.is_file():
        raise BeartypeTestPathException(
            f'Project mypy configuration file '
            f'{PROJECT_MYPY_CONFIG_FILE} not found.'
        )
    # Else, this file exists.

    # Return this path.
    return PROJECT_MYPY_CONFIG_FILE


@callable_cached
def get_project_readme_file() -> Path:
    '''
    Concrete platform-agnostic :mod:`Path` object encapsulating the absolute
    filename of this project's **readme file** (i.e., front-facing
    ``README.rst`` file) if found *or* raise an exception otherwise.

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
    # project directory.
    PROJECT_DIR = get_project_dir()

    # Concrete platform-agnostic path encapsulating the absolute filename of
    # this project's readme file.
    PROJECT_README_FILE = PROJECT_DIR.joinpath('README.rst')

    # If this file either does *NOT* exist or is *NOT* a file, raise an
    # exception.
    if not PROJECT_README_FILE.is_file():
        raise BeartypeTestPathException(
            f'Project readme file {PROJECT_README_FILE} not found.')
    # Else, this file exists.

    # Return this path.
    return PROJECT_README_FILE
