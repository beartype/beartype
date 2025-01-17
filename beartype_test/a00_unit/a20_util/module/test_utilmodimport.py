#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module importer** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.module.utilmodimport` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_import_module_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.module.utilmodget.import_module_or_none` function.
    '''

    # Defer test-specific imports.
    import beartype
    from beartype.roar import BeartypeModuleUnimportableWarning
    from beartype._util.module.utilmodimport import import_module_or_none
    from pytest import warns

    # Assert this function returns the expected module when passed the
    # fully-qualified name of a previously imported module.
    assert import_module_or_none('beartype') is beartype

    # Assert this function returns the expected module when passed the
    # fully-qualified name of a module effectively guaranteed to *NOT* have
    # been previously imported by virtue of its irrelevance.
    xmlrpc_client_dynamic = import_module_or_none('xmlrpc.client')
    from xmlrpc import client as xmlrpc_client_static
    assert xmlrpc_client_dynamic is xmlrpc_client_static

    # Assert this function returns "None" when passed the fully-qualified name
    # of a module effectively guaranteed to *NEVER* exist by virtue of the
    # excess inscrutability, stupidity, and verbosity of its name.
    assert import_module_or_none(
        'phnglui_mglwnafh_Cthulhu_Rlyeh_wgahnagl_fhtagn') is None

    # Assert this function emits the expected warning when passed the
    # fully-qualified name of an unimportable module.
    with warns(BeartypeModuleUnimportableWarning):
        assert import_module_or_none(
            'beartype_test.a00_unit.data.util.mod.data_utilmodule_bad') is (
                None)

# ....................{ TESTS ~ attr                       }....................
def test_import_module_attr() -> None:
    '''
    Test the :func:`beartype._util.module.utilmodget.import_module_attr`
    importer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.module.utilmodimport import import_module_attr
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Fully-qualified name of an importable module defining attributes intended
    # to be dynamically imported below.
    MODULE_IMPORTABLE_NAME = (
        'beartype_test.a00_unit.data.util.mod.data_utilmodule_good')

    # Fully-qualified name of an unimportable module.
    MODULE_UNIMPORTABLE_NAME = 'to.thy_delightful.realms'

    # ....................{ PASS                           }....................
    # Assert that passing this importer the fully-qualified name of an
    # existing attribute of an importable module returns that attribute as is.
    attr_good = import_module_attr(f'{MODULE_IMPORTABLE_NAME}.attrgood')
    assert isinstance(attr_good, str)
    assert attr_good.startswith('I started to see human beings as little')

    # ....................{ FAIL                           }....................
    # Assert that passing this importer the unqualified basename of a
    # non-existent attribute and *NO* module raises the expected exception.
    with raises(_BeartypeUtilModuleException):
        import_module_attr('Conduct_O_Sleep')

    # Assert that passing this importer the unqualified basename of a
    # non-existent attribute of an importable module raises the expected
    # exception.
    with raises(_BeartypeUtilModuleException):
        import_module_attr('This_doubt', module_name=MODULE_IMPORTABLE_NAME)

    # Assert that passing this importer the unqualified basename of a
    # non-existent attribute of an unimportable module raises the expected
    # exception.
    with raises(_BeartypeUtilModuleException):
        import_module_attr(
            'with_sudden_tide', module_name=MODULE_UNIMPORTABLE_NAME)

    # Assert that passing this importer the fully-qualified basename of a
    # non-existent attribute of an importable module raises the expected
    # exception.
    with raises(_BeartypeUtilModuleException):
        import_module_attr(
            'flowed_on_his_heart', module_name=MODULE_IMPORTABLE_NAME)

    # Assert that passing this importer the fully-qualified basename of a
    # non-existent attribute of an unimportable module raises the expected
    # exception.
    with raises(_BeartypeUtilModuleException):
        import_module_attr(
            'The_insatiate_hope', module_name=MODULE_UNIMPORTABLE_NAME)


def test_import_module_attr_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.module.utilmodget.import_module_attr_or_none`
    importer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.module.utilmodimport import import_module_attr_or_none

    # ....................{ LOCALS                         }....................
    # Fully-qualified name of an importable module defining attributes intended
    # to be dynamically imported below.
    MODULE_NAME = 'beartype_test.a00_unit.data.util.mod.data_utilmodule_good'

    # ....................{ PASS                           }....................
    # Assert that passing this importer the fully-qualified name of an
    # existing attribute of an importable module returns that attribute as is.
    attr_good = import_module_attr_or_none(f'{MODULE_NAME}.attrgood')
    assert isinstance(attr_good, str)
    assert attr_good.startswith('I started to see human beings as little')

    # Assert that passing this importer the fully-qualified name of a
    # non-existent attribute of an importable module returns "None".
    assert import_module_attr_or_none(f'{MODULE_NAME}.attrbad') is None


def test_import_module_attr_or_sentinel() -> None:
    '''
    Test the
    :func:`beartype._util.module.utilmodget.import_module_attr_or_sentinel`
    importer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeModuleUnimportableWarning
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.module.utilmodimport import (
        import_module_attr_or_sentinel)
    from beartype._util.utilobject import SENTINEL
    from pytest import (
        raises,
        warns,
    )

    # ....................{ LOCALS                         }....................
    # Fully-qualified name of a test-specific module defining attributes
    # intended to be dynamically imported below.
    MODULE_NAME = 'beartype_test.a00_unit.data.util.mod.data_utilmodule_good'

    # ....................{ PASS                           }....................
    # Assert that passing this importer an arbitrary attribute name of an
    # unimportable module returns the sentinel.
    assert import_module_attr_or_sentinel(
        attr_name='Hides_its_dead_eye', module_name='from.the_detested.day',
    ) is SENTINEL

    # Assert that passing this importer the unqualified name of an existing
    # builtin type returns that type as is.
    assert import_module_attr_or_sentinel('int') is int

    # Assert that passing this importer the unqualified name of a non-existent
    # builtin type returns the sentinel.
    assert import_module_attr_or_sentinel(
        'Where_every_shade_which_the_foul_grave_exhales') is SENTINEL

    # Assert that passing this importer the fully-qualified name of an
    # existing attribute of an importable module returns that attribute as is.
    attr_good = import_module_attr_or_sentinel(f'{MODULE_NAME}.attrgood')
    assert isinstance(attr_good, str)
    assert attr_good.startswith(
        'I started to see human beings as little')

    # Assert that passing this importer the fully-qualified name of a
    # non-existent attribute of an importable module which is also the
    # unqualified name of a builtin type returns that type.
    assert import_module_attr_or_sentinel(
        'str', module_name=MODULE_NAME) is str

    # Assert that passing this importer the fully-qualified name of a
    # non-existent attribute of an importable module which is *NOT* also the
    # unqualified name of a builtin type returns the sentinel.
    assert import_module_attr_or_sentinel(
        'attrbad', module_name=MODULE_NAME) is SENTINEL

    # ....................{ FAIL                           }....................
    # Assert this function emits the expected warning when passed the
    # syntactically valid fully-qualified name of a non-existent attribute of an
    # unimportable module.
    with warns(BeartypeModuleUnimportableWarning):
        bad_module_attr = import_module_attr_or_sentinel(
            'beartype_test.a00_unit.data.util.mod.data_utilmodule_bad.attrbad')
        assert bad_module_attr is SENTINEL

    # Assert this function raises the expected exception when passed a
    # non-string.
    with raises(_BeartypeUtilModuleException):
        import_module_attr_or_sentinel(
            b'In far countries little men have closely studied your longing '
            b'to be an indiscriminate slave.'
        )

    # Assert this function raises the expected exception when passed a
    # string containing no "." characters.
    with raises(_BeartypeUtilModuleException):
        import_module_attr_or_sentinel(
            'These little men were not born in mansions, '
            'they rose from your ranks'
        )

    # Assert this function raises the expected exception when passed a
    # string containing one or more "." characters but syntactically invalid as
    # a fully-qualified module attribute name.
    with raises(_BeartypeUtilModuleException):
        import_module_attr_or_sentinel(
            'They have gone hungry like you, suffered like you. And they have '
            'found a quicker way of changing masters.'
        )
