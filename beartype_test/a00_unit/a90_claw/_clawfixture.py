#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook unit test fixtures** (i.e., :mod:`pytest`-specific
context managers passed as parameters to unit tests exercising the
:mod:`beartype.claw` subpackage).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ FIXTURES ~ equality                }....................
@fixture(autouse=True, scope='function')
def clean_claws_unit() -> None:  # <-- heh. get it... clean *CLAWS*? it is punny.
    '''
    Permanently, silently, and recursively remove all **bytecode files** (i.e.,
    pure-Python bytecode compiled to platform-dependent temporary files residing
    in temporary ``__pycache__/`` subdirectories) from the test-specific
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
    #
    # Note that we intentionally avoid importing any subsubpackages (e.g.,
    # "beartype_test.a00_unit.data.claw.intraprocess.hookable_package.beartype_this_package")
    # above. Why? Because doing so would implicitly install the exact beartype
    # import hook which calling unit tests are attempting to subsequently
    # exercise and which *MUST* be confined to a context manager for test
    # idempotency.
    from beartype_test.a00_unit.data import claw
    from beartype_test._util.data.pytdataclean import (
        data_claw_subpackage_cleaned)

    # Recursively remove all previously compiled bytecode files from both this
    # subpackage *AND* sub-subpackages of this subpackage.
    yield from data_claw_subpackage_cleaned(claw)
