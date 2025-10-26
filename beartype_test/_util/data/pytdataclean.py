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

# ....................{ FIXTURES                           }....................
def data_claw_subpackage_cleaned(
    data_claw_subpackage: 'types.ModuleType') -> None:
    '''
    Context manager guaranteeably reverting *all* beartype import hooks
    transitively installed in the body of this context manager by the parent
    unit test implicitly invoking this fixture.

    Before doing so, this context manager permanently, silently, and recursively
    removes all **bytecode files** (i.e., pure-Python bytecode compiled to
    platform-dependent temporary files residing in temporary ``__pycache__/``
    subdirectories) of the passed test-specific subpackage and all
    subsubpackages of that subpackage regardless of depth.

    Parameters
    ----------
    data_claw_subpackage : types.ModuleType
        Previously imported subpackage containing one or more submodules
        expected to be hooked by :mod:`beartype.claw` import hooks. This
        subpackage should typically either be:

        * The :mod:`beartype_test.a00_unit.data.claw` subpackage.
        * The :mod:`beartype_test.a90_func.data.claw` subpackage.

    Raises
    ------
    beartype.roar.BeartypeClawHookException
        If one or more packages have been registered by a prior call to the
        :func:`beartype.claw._package.clawpkghook.hook_packages` function.
    '''

    # Defer fixture-specific imports.
    from beartype.claw._package.clawpkgcontext import packages_trie_reverted

    # Recursively remove *ALL* previously compiled bytecode files from both this
    # subpackage *and* *ALL* subsubpackages of this subpackage.
    clean_data_subpackage(data_claw_subpackage)

    # With a context manager guaranteeably reverting *ALL* beartype import hooks
    # transitively installed in the body of this context manager, defer to the
    # parent unit test implicitly invoking this fixture.
    #
    # Note that it is no longer safe to unconditionally clear *ALL* beartype
    # import hooks. Previously, when beartype was less popular, it was. That is
    # exactly what we did. At some point, however, it would seem that one or
    # more third-party packages of unknown provenance imported at an unknown
    # time by our test suite began registering beartype import hooks against
    # Microsoft's ambiguously named "key_value" Python package: the official API
    # for their Azure cloud-hosting services. Since GitHub Actions literally run
    # on Azure, that package now appears to be type-checked by beartype *BEFORE*
    # the beartype test suite is even started under GitHub Actions-based
    # continuous integration (CI) workflows. Crazy, yet true.
    with packages_trie_reverted():
        yield

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
    from beartype._util.path.utilpathremove import remove_package_bytecode_files

    # ....................{ PATHS                          }....................
    # Path encapsulating the absolute dirname of this data claw subpackage.
    data_subpackage_dir = get_module_dir(data_subpackage)
    # print(f'Clearing "{data_subpackage_dir}/" bytecode files...')

    # Recursively remove *ALL* previously compiled bytecode files from both this
    # subdirectory *and* *ALL* subsubdirectories of this subdirectory.
    remove_package_bytecode_files(data_subpackage_dir)
