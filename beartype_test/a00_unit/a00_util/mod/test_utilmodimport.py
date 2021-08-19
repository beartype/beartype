#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module importer** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.mod.utilmodimport` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises, warns

# ....................{ TESTS                             }....................
def test_import_module_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.mod.utilmodule.import_module_or_none` function.
    '''

    # Defer heavyweight imports.
    import beartype
    from beartype.roar import BeartypeModuleUnimportableWarning
    from beartype._util.mod.utilmodimport import import_module_or_none

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
    :func:`beartype._util.mod.utilmodule.import_module_attr` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.mod.utilmodimport import import_module_attr

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
    :func:`beartype._util.mod.utilmodule.import_module_attr_or_none` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeModuleUnimportableWarning
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.mod.utilmodimport import import_module_attr_or_none

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

# ....................{ TESTS ~ attr : typing             }....................
def test_import_module_typing_any_attr() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepattr.import_module_typing_any_attr`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.mod.utilmodimport import (
        import_module_attr_or_none,
        import_module_typing_any_attr,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from typing import Union

    # Assert that dynamically importing "typing.Union" attribute (guaranteed to
    # be importable under all supported Python versions) is that attribute.
    assert import_module_typing_any_attr('Union') is Union

    # Assert that attempting to dynamically import a ridiculous attribute
    # (guaranteed to be unimportable under all supported Python versions, we
    # swear) raises the expected exception.
    with raises(_BeartypeUtilModuleException):
        import_module_typing_any_attr('FromMyWingsAreShakenTheDewsThatWaken')

    #FIXME: On retiring Python 3.8, refactor everything below to import a newer
    #"typing" attribute introduced with a bleeding-edge Python version.
    # If the active Python interpreter targets Python >= 3.9, the
    # "typing.Annotated" attribute is guaranteed to exist. In this case...
    if IS_PYTHON_AT_LEAST_3_9:
        # Defer Python version-specific imports.
        from typing import Annotated

        # Assert that dynamically importing the "typing.Annotated" attribute
        # (guaranteed to be importable under this Python version) is that
        # attribute.
        assert import_module_typing_any_attr('Annotated') is Annotated
    # Else, the active Python interpreter targets Python < 3.9 and the
    # "typing.Annotated" attribute is guaranteed to *NOT* exist. In this
    # case...
    else:
        # The "typing_extensions.Annotated" attribute if the third-party
        # "typing_extensions" module is both installed and declares that
        # attribute *OR* "None" otherwise.
        typing_extensions_annotated = import_module_attr_or_none(
            'typing_extensions.Annotated')

        # If that attribute exists...
        if typing_extensions_annotated is not None:
            # Assert that dynamically importing the
            # "typing_extensions.Annotated" attribute (guaranteed to be
            # importable by this condition) is that attribute.
            assert import_module_typing_any_attr('Annotated') is (
                typing_extensions_annotated)
        # Else, safely reduce to a noop. This should typically *NEVER* happen,
        # as all sane versions of that module declare that attribute. *shrug*
