#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hookable configuration first class decorator position
submodule** (i.e., data module defining classes decorated by chains of one or
more decorators into which the :mod:`beartype.beartype` decorator will be
injected as the first decorator, mimicking real-world usage of the
:func:`beartype.claw.beartype_package` import hook from external callers).
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintReturnViolation
from beartype.typing import no_type_check
from pytest import raises

# ....................{ CLASSES                            }....................
# Validate that the import hook presumably registered by the caller implicitly
# injects the @beartype decorator as the first decorator in *ALL* chains of
# class decorations.

@no_type_check
class EntwinedInDuskierWreaths(object):
    '''
    Arbitrary class decorated by one or more decorators, which the import hook
    registered by the caller will then ignore by forcefully injecting the
    :func:`beartype.beartype` decorator as the first decorator.
    '''

    @staticmethod
    def her_braided_locks() -> int:
        '''
        Arbitrary static method trivially violating its return type hint.
        '''

        return 'Entwined in duskier wreaths her braided locks'

# Assert that the import hook registered by the caller ignored the
# @no_type_check decorator decorating the class defined above by forcefully
# injecting the @beartype decorator as the first decorator on that class.
with raises(BeartypeCallHintReturnViolation):
    EntwinedInDuskierWreaths.her_braided_locks()

# ....................{ FUNCTIONS                          }....................
# Validate that the import hook presumably registered by the caller implicitly
# injects the @beartype decorator as the last decorator in *ALL* chains of
# callable decorations.

@no_type_check
def over_the_fair_front() -> int:
    '''
    Arbitrary function trivially violating its return type hint.
    '''

    return "O'er the fair front and radiant eyes of day;"

# Assert that the import hook registered by the caller respected the
# @no_type_check decorator decorating the function defined above by continuing
# to inject the @beartype decorator as the last decorator on that function.
assert over_the_fair_front() == "O'er the fair front and radiant eyes of day;"
