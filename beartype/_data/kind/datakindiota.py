#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **sentinel singletons** (i.e., objects of arbitrary placeholder
value commonly required throughout this codebase, reducing space and time
consumption by preallocating widely used sentinel objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Add support for PEP 661 (i.e., the new sentinel() builtin) under Python
#>= 3.15. Specifically, refactor the code below to resemble:
#    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_15
#    if IS_PYTHON_AT_LEAST_3_15:
#        class Iota(object): ...
#        SENTINEL = Iota()
#    else:
#        SENTINEL = sentinel('SENTINEL')
#
#Pretty trivial, honestly. See also:
#    https://peps.python.org/pep-0661/

# ....................{ CLASSES                            }....................
class Iota(object):
    '''
    **Iota** (i.e., object minimizing space consumption by guaranteeably
    containing *no* attributes).
    '''

    __slots__ = ()


    def __repr__(self) -> str:
        '''
        Machine-readable representation of this iota.
        '''

        # Return the fully-qualified name of the sentinel placeholder defined
        # below. Since this is the *ONLY* meaningful instance of this type
        # instantiated throughout the codebase, this reduction improves the
        # readability of debugging messages and logging.
        return 'beartype._data.kind.datakindiota.SENTINEL'

# ....................{ CONSTANTS                          }....................
SENTINEL = Iota()
'''
**Sentinel singleton** (i.e., object of arbitrary placeholder value).

This object is internally leveraged by various utility functions to identify
erroneous and edge-case input (e.g., iterables of insufficient length).
'''
