#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook fixture utilities** (i.e., low-level functions internally
called by higher-level :mod:`pytest`-specific context managers passed as
parameters to unit tests exercising the :mod:`beartype.claw` subpackage).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ CLEANERS                           }....................
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

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype.claw._package.clawpkgcontext import packages_trie_cleared
    from beartype._util.module.utilmodget import get_module_dir
    from beartype._util.path.utilpathremove import (
        remove_package_bytecode_files)

    # ....................{ PATHS                          }....................
    # Path encapsulating the absolute dirname of this data claw subpackage.
    #
    # Note that we intentionally avoid importing any subsubpackages (e.g.,
    # "beartype_test.a00_unit.data.claw.intraprocess.hookable_package.beartype_this_package")
    # above. Why? Because doing so would implicitly install the exact beartype
    # import hook which calling unit tests are attempting to subsequently
    # exercise and which *MUST* be confined to a context manager for test
    # idempotency.
    data_claw_subpackage_dir = get_module_dir(data_claw_subpackage)

    # Recursively remove *ALL* previously compiled bytecode files from both this
    # subdirectory *and* *ALL* subsubdirectories of this subdirectory.
    remove_package_bytecode_files(data_claw_subpackage_dir)

    # ....................{ HOOKS                          }....................
    # With a context manager guaranteeably reverting *ALL* beartype import hooks
    # transitively installed in the body of this context manager, defer to the
    # parent unit test implicitly invoking this fixture.
    with packages_trie_cleared():
        yield
