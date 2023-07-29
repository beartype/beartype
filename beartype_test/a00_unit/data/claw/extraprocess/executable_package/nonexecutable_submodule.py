#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **executable main beartype import hook non-executable submodule**
(i.e., data module *only* intended to be imported from other submodules of this
data package rather than directly executed as a script).
'''

# ....................{ CALLABLES                          }....................
def by_solemn_vision(and_bright_silver_dream: int) -> None:
    '''
    Arbitrary callable annotated by trivial PEP-compliant type hints.

    To enable the parent Python process to validate that this callable actually
    *was* successfully called, this callable prints the passed parameter as is
    to standard output.
    '''

    print(and_bright_silver_dream)
