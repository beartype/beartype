#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`557` **dataclasses data submodule.**

This submodule defines :pep:`557`-compliant **dataclasses** (i.e.,
:func:`dataclasses.dataclass`-decorated types) configured with varying
combinations of keyword parameters validating known edge cases in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
from dataclasses import dataclass

# ....................{ CLASSES                            }....................
@dataclass
class DataclassDefault(object):
    '''
    Arbitrary dataclass declared with default :func:`.dataclass` parameters.
    '''

    pass


@dataclass(frozen=True)
class DataclassFrozen(object):
    '''
    Arbitrary dataclass declared with non-default :func:`.dataclass` parameters
    configuring a **frozen** (i.e., immutable) dataclass.
    '''

    pass
