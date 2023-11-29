#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module deprecation** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.module.utilmoddeprecate` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_deprecate_module_attr() -> None:
    '''
    Test the
    :func:`beartype._util.module.utilmoddeprecate.deprecate_module_attr` function.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype._util.module.utilmoddeprecate import deprecate_module_attr
    from pytest import raises, warns

    # ..................{ LOCALS                             }..................
    # Dictionary mapping from the deprecated to non-deprecated name of
    # arbitrary objects masquerading as deprecated and non-deprecated
    # attributes (respectively) of an arbitrary submodule.
    ATTR_DEPRECATED_NAME_TO_NONDEPRECATED_NAME = {
        # Deprecated names originating from public non-deprecated names in the
        # "ATTR_NONDEPRECATED_NAME_TO_VALUE" dictionary defined below.
        'Robes_some_unsculptured_image': 'Thine_earthly_rainbows',

        # Deprecated names originating from private non-deprecated names in
        # that dictionary, exercising an edge case.
        'The_strange_sleep': '_Of_the_aethereal_waterfall',

        # Deprecated names originating from non-deprecated names *NOT* in that
        # dictionary, exercising an edge case.
        'Wraps_all_in': 'its_own_deep_eternity',
    }

    # Dictionary mapping from the name to value of arbitrary objects
    # masquerading as non-deprecated attributes of an arbitrary submodule.
    ATTR_NONDEPRECATED_NAME_TO_VALUE = {
        'Thine_earthly_rainbows': "stretch'd across the sweep",
        '_Of_the_aethereal_waterfall': 'whose veil',

        # Globally scoped attribute required by deprecate_module_attr().
        '__name__': 'Lines.Written_in_the.Vale_of.Chamouni',
    }

    # ..................{ WARNS                              }..................
    # Assert this function both emits the expected warning and returns the
    # expected value of a deprecated attribute originating from a public
    # non-deprecated attribute of an arbitrary submodule.
    with warns(DeprecationWarning):
        assert deprecate_module_attr(
            attr_deprecated_name='Robes_some_unsculptured_image',
            attr_deprecated_name_to_nondeprecated_name=(
                ATTR_DEPRECATED_NAME_TO_NONDEPRECATED_NAME),
            attr_nondeprecated_name_to_value=ATTR_NONDEPRECATED_NAME_TO_VALUE,
        ) == "stretch'd across the sweep"

    # Assert this function both emits the expected warning and returns the
    # expected value of a deprecated attribute originating from a private
    # non-deprecated attribute of an arbitrary submodule.
    with warns(DeprecationWarning):
        assert deprecate_module_attr(
            attr_deprecated_name='The_strange_sleep',
            attr_deprecated_name_to_nondeprecated_name=(
                ATTR_DEPRECATED_NAME_TO_NONDEPRECATED_NAME),
            attr_nondeprecated_name_to_value=ATTR_NONDEPRECATED_NAME_TO_VALUE,
        ) == 'whose veil'

    # ..................{ RAISES                             }..................
    # Assert this function raises the expected exception when passed any name
    # other than that of a deprecated attribute.
    with raises(AttributeError):
        assert deprecate_module_attr(
            attr_deprecated_name='Which when the voices of the desert fail',
            attr_deprecated_name_to_nondeprecated_name=(
                ATTR_DEPRECATED_NAME_TO_NONDEPRECATED_NAME),
            attr_nondeprecated_name_to_value=ATTR_NONDEPRECATED_NAME_TO_VALUE,
        )

    # Assert this function raises the expected exception when passed the name
    # of a deprecated attribute whose corresponding non-deprecated attribute is
    # *NOT* defined by this submodule.
    with raises(ImportError):
        assert deprecate_module_attr(
            attr_deprecated_name='Wraps_all_in',
            attr_deprecated_name_to_nondeprecated_name=(
                ATTR_DEPRECATED_NAME_TO_NONDEPRECATED_NAME),
            attr_nondeprecated_name_to_value=ATTR_NONDEPRECATED_NAME_TO_VALUE,
        )
