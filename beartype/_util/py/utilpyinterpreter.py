#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python interpreter** utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from platform import python_implementation

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
#FIXME: Inefficient. Just wrap this in a cached function call instead: e.g.,
#    @callable_cached
#    def is_pypy() -> bool:
#        return python_implementation() == 'PyPy'
IS_PYPY = python_implementation() == 'PyPy'
'''
``True`` only if the current Python interpreter is PyPy.
'''
