#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
    Integration test validating that the :mod:`beartype` package raises *no*
    unexpected exceptions when type-checking instances of the third-party
    :class:`xarray.Dataset` class known to be hostile to runtime type-checking.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises
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

    # ....................{ CALLABLES                      }....................
    @beartype
    def crunch_data(data: Dataset) -> Dataset:
        '''
        Arbitrary callable both accepting and returning a
        :class:`xarray.Dataset` object.
        '''

        # Do it, @beartype. Do it for @leycec!
        return data

    # ....................{ PASS                           }....................
    # Implicitly assert that a @beartype-decorated callable accepts this dataset
    # *WITHOUT* raising unexpected exceptions.
    crunch_data(xarray_dataset)

    # ....................{ FAIL                           }....................
    # Assert that a @beartype-decorated callable raises the expected exception
    # when passed a non-dataset.
    with raises(BeartypeCallHintParamViolation):
        crunch_data("It's 110°F and I can feel my face peeling off my face.")
