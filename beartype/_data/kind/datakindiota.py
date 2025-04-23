#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **sentinel singletons** (i.e., objects of arbitrary placeholder
value commonly required throughout this codebase, reducing space and time
consumption by preallocating widely used sentinel objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ CLASSES                            }....................
class Iota(object):
    '''
    **Iota** (i.e., object minimizing space consumption by guaranteeably
    containing *no* attributes).
    '''

    __slots__ = ()

# ....................{ CONSTANTS                          }....................
SENTINEL = Iota()
'''
**Sentinel singleton** (i.e., object of arbitrary placeholder value).

This object is internally leveraged by various utility functions to identify
erroneous and edge-case input (e.g., iterables of insufficient length).
'''
