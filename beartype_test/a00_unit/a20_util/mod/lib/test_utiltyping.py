#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **typing module** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.module.lib.utiltyping` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ attr : typing             }....................
def test_import_typing_attr() -> None:
    '''
    Test the :func:`beartype._util.module.lib.utiltyping.import_typing_attr`
    importer.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.module.lib.utiltyping import import_typing_attr
    from beartype._util.module.utilmodimport import import_module_attr_or_none
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from pytest import raises
    from typing import Union

    # Assert that dynamically importing "typing.Union" attribute (guaranteed to
    # be importable under all supported Python versions) is that attribute.
    assert import_typing_attr('Union') is Union

    # Assert that attempting to dynamically import a ridiculous attribute
    # (guaranteed to be unimportable under all supported Python versions, we
    # swear) raises the expected exception.
    with raises(_BeartypeUtilModuleException):
        import_typing_attr('FromMyWingsAreShakenTheDewsThatWaken')

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
        assert import_typing_attr('Annotated') is Annotated
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
            assert import_typing_attr('Annotated') is (
                typing_extensions_annotated)
        # Else, safely reduce to a noop. This should typically *NEVER* happen,
        # as all sane versions of that module declare that attribute. *shrug*
