#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.module.utilmodtest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ raiser                     }....................
def test_die_unless_module_attr_name() -> None:
    '''
    Test the
    :func:`beartype._util.module.utilmodtest.die_unless_module_attr_name`
    raiser.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.module.utilmodtest import die_unless_module_attr_name
    from pytest import raises

    # Assert this validator raises *NO* exception when passed a syntactically
    # valid Python identifier.
    die_unless_module_attr_name('She_dwelt.among_the.untrodden.ways_2')

    # Assert this validator raises the expected exception when passed:
    # * A non-string.
    # * The empty string.
    # * A non-empty string containing *NO* "." delimiters.
    # * A non-empty string syntactically invalid as a Python identifier.
    with raises(_BeartypeUtilModuleException):
        die_unless_module_attr_name(b'Sentient.No6')
    with raises(_BeartypeUtilModuleException):
        die_unless_module_attr_name('')
    with raises(_BeartypeUtilModuleException):
        die_unless_module_attr_name('typing')
    with raises(_BeartypeUtilModuleException):
        die_unless_module_attr_name('Sentient.6')

# ....................{ TESTS ~ tester                     }....................
def test_is_module() -> None:
    '''
    Test the :func:`beartype._util.module.utilmodtest.is_module` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeModuleUnimportableWarning
    from beartype._util.module.utilmodtest import is_module
    from pytest import warns

    # ....................{ PASS                           }....................
    # Assert that this tester accepts the name of a (possibly unimported)
    # existing importable module.
    assert is_module(
        'beartype_test.a00_unit.data.util.module.data_utilmodule_good') is True

    # Assert that this tester accepts the name of that same module, which is now
    # guaranteed to have already been imported as a side effect of the prior
    # call.
    assert is_module(
        'beartype_test.a00_unit.data.util.module.data_utilmodule_good') is True

    # Assert that this tester accepts the name of a module whose global scope
    # intentionally circularly imports from another module whose global scope
    # intentionally circularly imports from that first module, which induces
    # Python to raise an "ImportError" exception at importation time claiming
    # these modules to only be partially initialized. Although these modules
    # have been maliciously implemented so as to *ALWAYS* raise this exception,
    # almost all real-world partially initialized modules of interest are only
    # temporarily and accidentally partially initialized. Still, this suffices.
    assert is_module(
        'beartype_test.a00_unit.data.util.module.circular.data_utilmodcircular_gates'
    ) is True
    assert is_module(
        'beartype_test.a00_unit.data.util.module.circular.data_utilmodcircular_hours'
    ) is True

    # ....................{ FAIL                           }....................
    # Assert that this tester rejects the name of a module guaranteed *NOT* to
    # exist, because we fully control the "beartype_test" package.
    assert is_module(
        'beartype_test.a00_unit.data.util.module.data_utilmodule_nonexistent'
    ) is False

    # Assert that this tester emits the expected warning when passed the name of
    # an existing unimportable module.
    with warns(BeartypeModuleUnimportableWarning):
        assert is_module(
            'beartype_test.a00_unit.data.util.module.data_utilmodule_bad') is (
            False)
