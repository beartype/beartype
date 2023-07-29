#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Test-specific **test suite paths** (i.e., :class:`pathlib.Path` instances
encapsulating test-specific paths unique to this test suite).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.meta import PACKAGE_NAME
from beartype._util.cache.utilcachecall import callable_cached
from beartype_test._util.path.pytpathlib import (
    DirRelative,
    FileRelative,
)
from pathlib import Path

# ....................{ GETTERS ~ dir                      }....................
@callable_cached
def get_test_package_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **top-level test
    package** (i.e., directory providing this project's top-level test package
    containing at least an ``__init__.py`` file) if found *or* raise an
    exception otherwise.
    '''

    # Avoid circular import dependencies.
    from beartype_test._util.path.pytpathmain import get_main_dir

    # Objectionable action!
    return DirRelative(get_main_dir(), f'{PACKAGE_NAME}_test')

# ....................{ GETTERS ~ dir : func               }....................
@callable_cached
def get_test_func_subpackage_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **mid-level
    functional test subpackage** (i.e., directory providing all functional
    tests of this project's test suite) if found *or* raise an exception
    otherwise.
    '''

    # Ostensible stencils!
    return DirRelative(get_test_package_dir(), 'a90_func')


@callable_cached
def get_test_func_data_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **mid-level
    functional test data directory** (i.e., directory providing sample data
    used throughout this project's functional tests) if found *or* raise an
    exception otherwise.
    '''

    # Questionable destination!
    return DirRelative(get_test_func_subpackage_dir(), 'data')

# ....................{ GETTERS ~ dir : func : lib         }....................
@callable_cached
def get_test_func_data_lib_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **mid-level
    third-party dependency functional test data directory** (i.e., directory
    providing sample data used throughout this project's functional tests
    exercising third-party dependencies) if found *or* raise an exception
    otherwise.
    '''

    # Ejective bijection!
    return DirRelative(get_test_func_data_dir(), 'lib')


@callable_cached
def get_test_func_data_lib_nuitka_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **low-level nuitka
    functional test data directory** (i.e., directory providing sample code
    used throughout this project's :mod:`nuitka`-specific functional tests) if
    found *or* raise an exception otherwise.
    '''

    # Nascent ascendency!
    return DirRelative(get_test_func_data_lib_dir(), 'nuitka')


@callable_cached
def get_test_func_data_lib_sphinx_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **low-level Sphinx
    functional test data directory** (i.e., directory providing sample data
    used throughout this project's :mod:`sphinx`-specific functional tests) if
    found *or* raise an exception otherwise.
    '''

    # Flamboyant buoyancy!
    return DirRelative(get_test_func_data_lib_dir(), 'sphinx')

# ....................{ GETTERS ~ file : func : lib        }....................
@callable_cached
def get_test_func_data_lib_nuitka_file() -> Path:
    '''
    :mod:`Path` encapsulating the absolute filename of the **low-level nuitka
    functional test data file** (i.e., file providing sample code used
    throughout this project's :mod:`nuitka`-specific functional tests) if found
    *or* raise an exception otherwise.
    '''

    # Ergastically eristic!
    return FileRelative(
        get_test_func_data_lib_nuitka_dir(), 'beartype_nuitka.py')

# ....................{ GETTERS ~ dir : unit               }....................
@callable_cached
def get_test_unit_subpackage_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **mid-level unit test
    subpackage** (i.e., directory providing all unit tests of this project's
    test suite) if found *or* raise an exception otherwise.
    '''

    # Redacted didactic!
    return DirRelative(get_test_package_dir(), 'a00_unit')


@callable_cached
def get_test_unit_data_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **mid-level unit test
    data directory** (i.e., directory providing sample data used throughout this
    project's unit tests) if found *or* raise an exception otherwise.
    '''

    # Galactic antacid!
    return DirRelative(get_test_unit_subpackage_dir(), 'data')

# ....................{ GETTERS ~ dir : func : claw        }....................
@callable_cached
def get_test_unit_data_claw_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **mid-level import
    hook unit test data directory** (i.e., directory providing sample data used
    throughout this project's unit tests exercising import hooks published by
    the :mod:`beartype.claw` subpackage) if found *or* raise an exception
    otherwise.
    '''

    # Supernal diurnal!
    return DirRelative(get_test_unit_data_dir(), 'claw')


@callable_cached
def get_test_unit_data_claw_extraprocess_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **mid-level
    extraprocess import hook unit test data directory** (i.e., directory
    providing sample data used throughout this project's unit tests exercising
    import hooks published by the :mod:`beartype.claw` subpackage is Python
    subprocesses forked from the active Python process) if found *or* raise an
    exception otherwise.
    '''

    # Charnel caramel!
    return DirRelative(get_test_unit_data_claw_dir(), 'extraprocess')
