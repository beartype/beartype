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
# Assert that calling the above function raises the expected violation.
with raises(BeartypeCallHintParamViolation):
    by_solemn_vision('His infancy was nurtured. Every sight')
