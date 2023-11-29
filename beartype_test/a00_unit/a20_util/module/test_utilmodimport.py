#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module importer** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.module.utilmodimport` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
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

# ....................{ TESTS ~ attr                      }....................
def test_import_module_attr() -> None:
    '''
    Test the
    :func:`beartype._util.module.utilmodget.import_module_attr` function.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.module.utilmodimport import import_module_attr
    from pytest import raises

    # Attribute dynamically imported from a module.
    module_attr = import_module_attr(
        'beartype_test.a00_unit.data.util.mod.data_utilmodule_good.attrgood')

    # Assert this to be the expected attribute.
    assert isinstance(module_attr, str)
    assert module_attr.startswith('I started to see human beings as little')

    # Assert this function raises the expected exception when passed the
    # syntactically valid fully-qualified name of a non-existent attribute of
    # an importable module.
    with raises(_BeartypeUtilModuleException):
        import_module_attr(
            'beartype_test.a00_unit.data.util.mod.data_utilmodule_good.attrbad')


def test_import_module_attr_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.module.utilmodget.import_module_attr_or_none` function.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeModuleUnimportableWarning
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.module.utilmodimport import import_module_attr_or_none
    from pytest import raises, warns

    # Attribute declared by an importable module.
    module_attr_good = import_module_attr_or_none(
        'beartype_test.a00_unit.data.util.mod.data_utilmodule_good.attrgood')

    # Attribute *NOT* declared by an importable module.
    module_attr_bad = import_module_attr_or_none(
        'beartype_test.a00_unit.data.util.mod.data_utilmodule_good.attrbad')

    # Assert this to be the expected attribute.
    assert isinstance(module_attr_good, str)
    assert module_attr_good.startswith(
        'I started to see human beings as little')

    # Assert this function returns "None" when passed the syntactically valid
    # fully-qualified name of a non-existent attribute of an importable module.
    assert module_attr_bad is None

    # Assert this function emits the expected warning when passed the
    # syntactically valid fully-qualified name of a non-existent attribute of
    # an unimportable module.
    with warns(BeartypeModuleUnimportableWarning):
        bad_module_attr = import_module_attr_or_none(
            'beartype_test.a00_unit.data.util.mod.data_utilmodule_bad.attrbad')
        assert bad_module_attr is None

    # Assert this function raises the expected exception when passed a
    # non-string.
    with raises(_BeartypeUtilModuleException):
        import_module_attr_or_none(
            b'In far countries little men have closely studied your longing '
            b'to be an indiscriminate slave.'
        )

    # Assert this function raises the expected exception when passed a
    # string containing no "." characters.
    with raises(_BeartypeUtilModuleException):
        import_module_attr_or_none(
            'These little men were not born in mansions, '
            'they rose from your ranks'
        )

    # Assert this function raises the expected exception when passed a
    # string containing one or more "." characters but syntactically invalid as
    # a fully-qualified module attribute name.
    with raises(_BeartypeUtilModuleException):
        import_module_attr_or_none(
            'They have gone hungry like you, suffered like you. And they have '
            'found a quicker way of changing masters.'
        )
