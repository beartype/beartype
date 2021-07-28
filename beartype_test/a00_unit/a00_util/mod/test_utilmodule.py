#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.mod.utilmodule` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS ~ importer                  }....................
def test_import_module_attr() -> None:
    '''
    Test the
    :func:`beartype._util.mod.utilmodule.import_module_attr` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.mod.utilmodule import import_module_attr

    # Attribute dynamically imported from a module.
    module_attr = import_module_attr(
        'beartype_test.a00_unit.data.util.py.data_utilpymodule_good.attrgood')

    # Assert this to be the expected attribute.
    assert isinstance(module_attr, str)
    assert module_attr.startswith('I started to see human beings as little')

    # Assert this function raises the expected exception when passed the
    # syntactically valid fully-qualified name of a non-existent attribute of
    # an importable module.
    with raises(_BeartypeUtilModuleException):
        import_module_attr(
            'beartype_test.a00_unit.data.util.py.data_utilpymodule_good.attrbad')


def test_import_module_attr_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.mod.utilmodule.import_module_attr_or_none` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.mod.utilmodule import import_module_attr_or_none

    # Attribute declared by an importable module.
    module_attr_good = import_module_attr_or_none(
        'beartype_test.a00_unit.data.util.py.data_utilpymodule_good.attrgood')

    # Attribute *NOT* declared by an importable module.
    module_attr_bad = import_module_attr_or_none(
        'beartype_test.a00_unit.data.util.py.data_utilpymodule_good.attrbad')

    # Assert this to be the expected attribute.
    assert isinstance(module_attr_good, str)
    assert module_attr_good.startswith(
        'I started to see human beings as little')

    # Assert this function returns "None" when passed the syntactically valid
    # fully-qualified name of a non-existent attribute of an importable module.
    assert module_attr_bad is None

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

    # Assert this function raises the expected exception when passed the
    # syntactically valid fully-qualified name of a non-existent attribute of
    # an unimportable module.
    with raises(ValueError):
        import_module_attr_or_none(
            'beartype_test.a00_unit.data.util.py.data_utilpymodule_bad.attrbad')
