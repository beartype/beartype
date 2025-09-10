#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **data subpackage cleaners** (i.e., low-level functions internally
called by higher-level tests and fixtures to recursively remove all bytecode
files from imported test-specific data subpackages).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ CLEANERS                           }....................
def clean_data_subpackage(data_subpackage: 'types.ModuleType') -> None:
    '''
    Permanently, silently, and recursively remove all **bytecode files** (i.e.,
    pure-Python bytecode compiled to platform-dependent temporary files residing
    in temporary ``__pycache__/`` subdirectories) of the passed test-specific
    subpackage and all subsubpackages of that subpackage regardless of depth.

    Parameters
    ----------
    datasubpackage : types.ModuleType
        Previously imported subpackage containing one or more data submodules.

    See Also
    --------
    :func:`beartype._util.path.utilpathremove.remove_package_bytecode_files`
        Further details.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.module.utilmodget import get_module_dir
    from beartype._util.path.utilpathremove import (
        remove_package_bytecode_files)

    # ....................{ PATHS                          }....................
    # Path encapsulating the absolute dirname of this data claw subpackage.
    data_subpackage_dir = get_module_dir(data_subpackage)
    # print(f'Clearing "{data_subpackage_dir}/" bytecode files...')

    # Recursively remove *ALL* previously compiled bytecode files from both this
    # subdirectory *and* *ALL* subsubdirectories of this subdirectory.
    remove_package_bytecode_files(data_subpackage_dir)


def clean_data_claw_subpackage(
    data_claw_subpackage: 'types.ModuleType') -> None:
    '''
    Permanently, silently, and recursively remove all **bytecode files** (i.e.,
    pure-Python bytecode compiled to platform-dependent temporary files residing
    in temporary ``__pycache__/`` subdirectories) of the passed test-specific
    subpackage and all subsubpackages of that subpackage regardless of depth.

    Parameters
    ----------
    data_claw_subpackage : types.ModuleType
        Previously imported subpackage containing one or more submodules
        expected to be hooked by :mod:`beartype.claw` import hooks. This
        subpackage should typically either be:

        * The :mod:`beartype_test.a00_unit.data.claw` subpackage.
        * The :mod:`beartype_test.a90_func.data.claw` subpackage.

    See Also
    --------
    :func:`beartype._util.path.utilpathremove.remove_package_bytecode_files`
        Further details.
    '''

    # Defer fixture-specific imports.
    from beartype.claw._package.clawpkgcontext import packages_trie_cleared

    # Recursively remove *ALL* previously compiled bytecode files from both this
    # subpackage *and* *ALL* subsubpackages of this subpackage.
    clean_data_subpackage(data_claw_subpackage)

    # With a context manager guaranteeably reverting *ALL* beartype import hooks
    # transitively installed in the body of this context manager, defer to the
    # parent unit test implicitly invoking this fixture.
    with packages_trie_cleared():
        yield
