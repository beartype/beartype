#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **main codebase paths** (i.e., low-level callables creating and
returning :class:`pathlib.Path` objects encapsulating test-agnostic paths
applicable to the codebase being tested).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: Tests should ideally *ONLY* call the get_main_package_dir() and
# get_main_package_dir() getters defined below. All other getters defined below
# assume that this main package and test suite reside under the same parent
# directory. That assumption is *NOT* necessarily the case, especially for
# exotic testing environments like remote third-party continuous integration
# (CI) workflows *NOT* under our control. Tests calling those
# other getters are thus intrinsically non-portable, fragile, and failure-prone.
# This includes:
# * "conda-forge", whose release workflow for downstream feedstocks requires
#   that the test suite shipped with associated third-party packages in release
#   tarballs passes. For safety, that release workflow both strips and splits
#   the contents of those tarballs into distinct subdirectories strewn across
#   the CI-hosted filesystem. Since the main and test package subdirectories no
#   longer share the same parent directory, the crude directory discovery
#   heuristic employed by logic below fails to generalize to "conda-forge".
#   Anecdotally, the CI-hosted filesystem looks something like:
#       etc/
#         conda/
#           test-files/
#             beartype/
#               1/
#                 beartype_test
#                 pytest.ini
#       lib/
#         python3.11/
#           site-packages/
#             beartype
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._util.cache.func.utilcachefunc import callable_cached
from beartype_test._util.path.pytpathlib import (
    DirRelative,
    FileRelative,
)
from pathlib import Path

# ....................{ GETTERS ~ dir                      }....................
@callable_cached
def get_main_package_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **top-level project
    package** (i.e., directory providing this package's top-level package
    containing at least an ``__init__.py`` file) if found *or* raise an
    exception otherwise.
    '''

    # Defer function-specific imports.
    import beartype
    from beartype._util.module.utilmodget import get_module_dir

    # Path encapsulating the absolute dirname of our top-level package.
    #
    # Note that we intentionally avoid accessing this path by seemingly
    # equivalent test-specific logic resembling:
    #     main_package_dir = DirRelative(get_main_repo_dir(), PACKAGE_NAME)
    #
    # Why? Because doing so assumes that our top-level package resides in a
    # ".git" repository, which is *NOT* necessarily the case when this test
    # suite is run from exotic continuous integration (CI) environments (e.g.,
    # "conda-forge"). See also "WARNING:" comments above for gruesome details.
    main_package_dir = get_module_dir(beartype)

    # Return this path as is.
    return main_package_dir


@callable_cached
def get_main_package_parent_dir() -> Path:
    '''
    :mod:`Path` encapsulating the absolute dirname of the **top-level project
    package parent directory** (i.e., parent directory containing the child
    directory providing this package's top-level package containing at least an
    ``__init__.py`` file) if found *or* raise an exception otherwise.

    Note that:

    * Under *most* testing environments, this path is identical to that returned
      by the :func:`.get_main_repo_dir` getter.
    * Under exotic testing environments (e.g., ``conda-forge``), this path
      differs substantially from that returned by the :func:`.get_main_repo_dir`
      getter.
    '''

    # Return this path as is.
    return get_main_package_dir().parent

# ....................{ GETTERS ~ dir : repo               }....................
@callable_cached
def get_main_repo_dir() -> Path:
    '''
    :class:`.Path` encapsulating the absolute dirname of the **top-level project
    directory** (i.e., directory containing both a ``.git/`` subdirectory and a
    subdirectory providing this project's package) if found *or* raise an
    exception otherwise.
    '''
    # print(f'current module paths: {__package__} [{__file__}]')

    # Defer function-specific imports.
    from beartype.meta import PACKAGE_TEST_NAME

    # Path encapsulating the current module.
    MODULE_FILE = Path(__file__)

    # Path encapsulating the current module's package.
    MODULE_PACKAGE_DIR = MODULE_FILE.parent

    # Path encapsulating the relative dirname of this project's directory
    # relative to the dirname of the package defining the current module.
    MAIN_DIR = DirRelative(MODULE_PACKAGE_DIR, '../../..')

    # If this project's directory either does not contain a "beartype_test"
    # subdirectory *OR* does but this path is not a directory, raise an
    # exception. This basic sanity check improves the likelihood that this
    # project directory is what we assume it is.
    #
    # Note that we intentionally avoid testing paths *NOT* bundled with release
    # tarballs (e.g., a root ".git/" directory), as doing so would prevent
    # external users and tooling from running tests from release tarballs.
    DirRelative(MAIN_DIR, PACKAGE_TEST_NAME)

    # Return this path.
    return MAIN_DIR

# ....................{ GETTERS ~ file : repo              }....................
@callable_cached
def get_main_repo_mypy_config_file() -> Path:
    '''
    :mod:`Path` encapsulating the absolute filename of this project's **mypy
    configuration file** (i.e., top-level ``.mypy.ini`` file) if found *or*
    raise an exception otherwise.
    '''

    # Obverse obviation!
    return FileRelative(get_main_repo_dir(), 'mypy.ini')


@callable_cached
def get_main_repo_readme_file() -> Path:
    '''
    :mod:`Path` encapsulating the absolute filename of the **project readme
    file** (i.e., this project's front-facing ``README.rst`` file) if found *or*
    raise an exception otherwise.

    Note that the :meth:`.Path.read_text` method of this object trivially yields
    the decoded plaintext contents of this file as a string.
    '''

    # Perverse pomposity!
    return FileRelative(get_main_repo_dir(), 'README.rst')
