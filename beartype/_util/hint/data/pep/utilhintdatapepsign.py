#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype Python version-agnostic signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints in a safe, non-deprecated manner
regardless of the Python version targeted by the active Python interpreter).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_9,
)

# ....................{ SIGNS ~ declare                   }....................
# Initialized below.
HINT_PEP_SIGN_LIST = None
'''
**List sign** (i.e., arbitrary object uniquely identifying PEP-compliant list
type hints) appropriate to the current Python interpreter.
'''


# Initialized below.
HINT_PEP_SIGN_TUPLE = None
'''
**Tuple sign** (i.e., arbitrary object uniquely identifying PEP-compliant tuple
type hints) appropriate to the current Python interpreter.
'''

# ....................{ SIGNS ~ define                    }....................
# Signs conditionally dependent on the major version of Python targeted by
# the active Python interpreter.

# If the active Python interpreter targets at least Python >= 3.9 and thus
# supports PEP 584, prefer the standard types.
if IS_PYTHON_AT_LEAST_3_9:
    HINT_PEP_SIGN_LIST = list
    HINT_PEP_SIGN_TUPLE = tuple
# Else, defer to deprecated "typing" objects.
else:
    from typing import List, Tuple

    HINT_PEP_SIGN_LIST = List
    HINT_PEP_SIGN_TUPLE = Tuple
