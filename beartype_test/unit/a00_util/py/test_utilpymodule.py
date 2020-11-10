#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype module utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.py.utilpymodule` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                             }....................
def test_import_module_attr_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.py.utilpymodule.import_module_attr` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.py.utilpymodule import import_module_attr

    # Attribute dynamically imported from a module.
    module_attr = import_module_attr(
        'beartype_test.unit.data.module.data_modulegood.attrgood')

    # Assert this to be the expected attribute.
    assert isinstance(module_attr, str)
    assert module_attr.startswith('I started to see human beings as little')


def test_import_module_attr_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.py.utilpymodule.import_module_attr` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import _BeartypeUtilModuleException
    from beartype._util.py.utilpymodule import import_module_attr

    # Assert this function raises the expected exception when passed a
    # non-string.
    with raises(_BeartypeUtilModuleException):
        import_module_attr(
            b'In far countries little men have closely studied your longing '
            b'to be an indiscriminate slave.'
        )

    # Assert this function raises the expected exception when passed a
    # string containing no "." characters.
    with raises(_BeartypeUtilModuleException):
        import_module_attr(
            'These little men were not born in mansions, they rose from your '
            'ranks'
        )

    # Assert this function raises the expected exception when passed a
    # string containing one or more "." characters but syntactically invalid as
    # a fully-qualified module attribute name..
    with raises(_BeartypeUtilModuleException):
        import_module_attr(
            'They have gone hungry like you, suffered like you. And they have '
            'found a quicker way of changing masters.'
        )

    # Assert this function raises the expected exception when passed the
    # syntactically valid fully-qualified name of a non-existent attribute of
    # an importable module.
    with raises(_BeartypeUtilModuleException):
        import_module_attr(
            'beartype_test.unit.data.module.data_modulegood.attrbad')

    # Assert this function raises the expected exception when passed the
    # syntactically valid fully-qualified name of a non-existent attribute of
    # an unimportable module.
    with raises(ValueError):
        import_module_attr(
            'beartype_test.unit.data.module.data_modulebad.attrbad')

