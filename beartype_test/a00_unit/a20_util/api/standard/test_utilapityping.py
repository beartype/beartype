#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **typing module** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.api.standard.utiltyping` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_import_typing_attr() -> None:
    '''
    Test the :func:`beartype._util.api.standard.utiltyping.import_typing_attr`
    importer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.api.standard.utiltyping import import_typing_attr
    from beartype._util.module.utilmodimport import (
        import_module_attr_or_sentinel)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_13
    from beartype._util.utilobject import SENTINEL
    from pytest import raises
    from typing import Union

    # ....................{ PASS                           }....................
    # Assert that dynamically importing "typing.Union" attribute (guaranteed to
    # be importable under all supported Python versions) is that attribute.
    assert import_typing_attr('Union') is Union

    # ....................{ FAIL                           }....................
    # Assert that attempting to dynamically import a ridiculous attribute
    # (guaranteed to be unimportable under all supported Python versions, we
    # swear) raises the expected exception.
    with raises(_BeartypeUtilModuleException):
        import_typing_attr('FromMyWingsAreShakenTheDewsThatWaken')

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.13, the
    # "typing.TypeIs" attribute is guaranteed to exist. In this case...
    if IS_PYTHON_AT_LEAST_3_13:
        # Defer Python version-specific imports.
        from typing import TypeIs

        # Assert that dynamically importing the "typing.Annotated" attribute
        # (guaranteed to be importable under this Python version) is that
        # attribute.
        assert import_typing_attr('TypeIs') is TypeIs
    # Else, the active Python interpreter targets Python < 3.13 and the
    # "typing.TypeIs" attribute is guaranteed to *NOT* exist. In this case...
    else:
        # The "typing_extensions.TypeIs" attribute if the third-party
        # "typing_extensions" module is both installed and declares that
        # attribute *OR* "None" otherwise.
        typing_extensions_factory = import_module_attr_or_sentinel(
            'typing_extensions.TypeIs')

        # If that attribute exists...
        if typing_extensions_factory is not SENTINEL:
            # Assert that dynamically importing the
            # "typing_extensions.TypeIs" attribute (guaranteed to be
            # importable by this condition) is that attribute.
            assert import_typing_attr('TypeIs') is typing_extensions_factory
        # Else, safely reduce to a noop. This should typically *NEVER* happen,
        # as all sane versions of that module declare that attribute. *shrug*
