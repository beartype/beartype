#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **executable main beartype import hook main package submodule**
(i.e., data module implicitly imported by Python when the fully-qualified name
of the package directly containing this module is passed as the argument to
Python's ``-m`` command-line option).
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintParamViolation
from executable_package.nonexecutable_submodule import by_solemn_vision
from pytest import raises

# ....................{ MAIN                               }....................
# Call the above function with a valid parameter, which then prints that
# parameter to standard output.
by_solemn_vision(len('And sound from the vast earth and ambient air,'))

# Assert that calling the above function with an invalid parameter raises
# the expected violation.
with raises(BeartypeCallHintParamViolation):
    by_solemn_vision('His infancy was nurtured. Every sight')
