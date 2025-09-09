#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook fixtures** (i.e., :mod:`pytest`-specific context managers
passed as parameters to unit tests exercising the :mod:`beartype.claw`
subpackage).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ FIXTURES ~ equality                }....................
@fixture(autouse=True, scope='function')
def clean_claws() -> None:  # <-- heh. get it... clean *CLAWS*? it is punny.
    '''
    Permanently, silently, and recursively remove all **bytecode files** (i.e.,
    pure-Python bytecode compiled to platform-dependent temporary files residing
    in temporary ``__pycache__/`` subdirectories) of the test-specific
    :mod:`beartype_test.a00_unit.data` subpackage and all subsubpackages of that
    subpackage regardless of depth.

    Note that this unit test-scoped fixture is implicitly performed *before*
    each unit test transitively defined in sibling and child submodules of the
    subpackage directly containing this submodule. Why? Because failing to do so
    would invite subtle but easily reproducible desynchronization woes between
    those files and more recent changes to the implementation of the
    :mod:`beartype.claw` subpackage in the main codebase.

    See Also
    --------
    :func:`beartype._util.path.utilpathremove.remove_package_bytecode_files`
        Further details.
    '''

    # Defer fixture-specific imports.
    from beartype_test.a00_unit.data import claw
    from beartype_test._util.fixture.pytfixclaw import (
        clean_data_claw_subpackage)

    # Recursively remove *ALL* previously compiled bytecode files from both this
    # subpackage *and* *ALL* subsubpackages of this subpackage.
    clean_data_claw_subpackage(claw)
