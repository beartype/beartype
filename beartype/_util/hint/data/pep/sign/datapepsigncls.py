#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **sign classes** (i.e., classes whose instances uniquely
identifying PEP-compliant type hints in a safe, non-deprecated manner
regardless of the Python version targeted by the active Python interpreter).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from typing import Union

# ....................{ CLASSES                           }....................
class HintSign(object):
    '''
    **Sign** (i.e., object uniquely identifying PEP-compliant type hints in a
    safe, non-deprecated manner regardless of the Python version targeted by
    the active Python interpreter).
    '''

    __slots__ = ()

# ....................{ HINTS                             }....................
HintSignOrType = Union[HintSign, type]
'''
PEP-compliant type hint matching either a **sign** (i.e., object uniquely
identifying PEP-compliant type hints in a safe, non-deprecated manner
regardless of the Python version targeted by the active Python interpreter) or
**isinstanceable class** (i.e., class safely passable as the second argument to
the :func:`isinstance` builtin).
'''
