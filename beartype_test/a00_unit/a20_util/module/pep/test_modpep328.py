#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`328`-compliant **relative module name utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.module.pep.modpep328` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_canonicalize_pep328_module_name_relative() -> None:
    '''
    Test the :func:`beartype._util.module.pep.modpep328.canonicalize_pep328_module_name_relative`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilModulePep328Exception
    from beartype._util.module.pep.modpep328 import (
        canonicalize_pep328_module_name_relative)
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # List of the unqualified basenames comprising the fully-qualified name of
    # the originating module to which the relative module tested below is
    # relative.
    MODULE_BASENAMES_ABSOLUTE = [
        'package_name', 'subpackage_name', 'submodule_name']

    # ....................{ PASS                           }....................
    # Assert this canonicalizer returns the expected string when passed a
    # PEP 328-compliant relative module name relative to a single package level.
    assert canonicalize_pep328_module_name_relative(
        module_name_relative='.submodule_sibling_name',
        module_basenames_absolute=MODULE_BASENAMES_ABSOLUTE,
    ) == 'package_name.subpackage_name.submodule_sibling_name'

    # Assert this canonicalizer returns the expected string when passed a
    # PEP 328-compliant relative module name relative to two or more package
    # levels.
    assert canonicalize_pep328_module_name_relative(
        module_name_relative='..submodule_nephew_name',
        module_basenames_absolute=MODULE_BASENAMES_ABSOLUTE,
    ) == 'package_name.submodule_nephew_name'

    # ....................{ FAIL                           }....................
    # Assert this canonicalizer passed a PEP 328-noncompliant absolute module
    # name raises the expected exception.
    with raises(_BeartypeUtilModulePep328Exception):
        canonicalize_pep328_module_name_relative(
            module_name_relative='package_name.subpackage_name.submodule_name',
            module_basenames_absolute=MODULE_BASENAMES_ABSOLUTE,
        )
