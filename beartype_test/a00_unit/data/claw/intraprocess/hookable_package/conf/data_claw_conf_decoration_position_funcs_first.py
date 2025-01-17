#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hookable configuration first callable decorator position
submodule** (i.e., data module defining callables decorated by chains of one or
more decorators into which the :mod:`beartype.beartype` decorator will be
injected as the first decorator, mimicking real-world usage of the
:func:`beartype.claw.beartype_package` import hook from external callers).
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintReturnViolation
from beartype.typing import no_type_check
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
from pytest import raises

# ....................{ FUNCTIONS                          }....................
# Validate that the import hook presumably registered by the caller implicitly
# injects the @beartype decorator as the first decorator in *ALL* chains of
# callable decorations.

@no_type_check
def night_followed() -> int:
    '''
    Arbitrary function trivially violating its return type hint.
    '''

    return 'Night followed, clad with stars. On every side'

# Assert that the import hook registered by the caller ignored the
# @no_type_check decorator decorating the callable defined above by forcefully
# injecting the @beartype decorator as the first decorator on that callable.
with raises(BeartypeCallHintReturnViolation):
    night_followed()

# ....................{ CLASSES                            }....................
# Validate that the import hook presumably registered by the caller implicitly
# injects the @beartype decorator as the last decorator in *ALL* chains of
# class decorations.

# If the active Python interpreter targets Python >= 3.11, the standard
# @no_type_check decorator correctly applies itself to classes. In this case...
if IS_PYTHON_AT_LEAST_3_11:
    @no_type_check
    class MoreHorribly(object):
        '''
        Arbitrary class decorated by one or more decorators, which the import
        hook registered by the caller will then respect by continuing to inject
        the :func:`beartype.beartype` decorator as the last decorator.
        '''

        @staticmethod
        def the_multitudinous_streams() -> int:
            '''
            Arbitrary static method trivially violating its return type hint.
            '''

            return 'More horribly the multitudinous streams'

    # Assert that the import hook registered by the caller respected the
    # @no_type_check decorator decorating the class defined above by continuing
    # to inject the @beartype decorator as the last decorator on that class.
    assert MoreHorribly.the_multitudinous_streams() == (
        'More horribly the multitudinous streams')
# Else, the active Python interpreter targets Python <= 3.10. In this case, the
# standard @no_type_check decorator fails to correctly apply itself to classes.
# In this case, simply avoid performing the prior test for simplicity. *shrug*
