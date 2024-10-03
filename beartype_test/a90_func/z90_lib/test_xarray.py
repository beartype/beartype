#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`xarray` integration tests.

This submodule functionally tests the :mod:`beartype` package against the
third-party :mod:`xarray` package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('xarray')
def test_xarray_dataset() -> None:
    '''
    Functional test validating that the :mod:`beartype` package raises *no*
    unexpected exceptions when type-checking instances of the third-party
    :class:`xarray.Dataset` class known to be hostile to runtime type-checking.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import die_if_unbearable
    from xarray import Dataset

    # ....................{ LOCALS                         }....................
    # Arbitrary xarray dataset.
    xarray_dataset = Dataset({
        'temperature': (
            ['x', 'y'], [
                [20, 25],
                [30, 35],
            ],
        ),
    })

    # ....................{ ASSERTS                        }....................
    # Implicitly assert that @beartype accepts this dataset *WITHOUT* raising
    # unexpected exceptions.
    die_if_unbearable(xarray_dataset, Dataset)
