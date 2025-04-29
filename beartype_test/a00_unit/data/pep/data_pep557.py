#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557` **dataclasses data submodule.**

This submodule exercises support for **dataclasses** (i.e., :pep:`557`-compliant
:func:`dataclasses.dataclass`-decorated classes) implemented in the
:func:`beartype.beartype` decorator. To do so, this submodule defines
dataclasses configured with varying combinations of keyword parameters.
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
