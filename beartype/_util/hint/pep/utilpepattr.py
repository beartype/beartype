#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint attribute** (i.e., attribute usable for creating
PEP-compliant type hints in a safe, non-deprecated manner regardless of the
Python version targeted by the active Python interpreter) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.utilobject import SENTINEL
from typing import Any

# ....................{ ATTRS                             }....................
# Signs conditionally dependent on the major version of Python targeted by
# the active Python interpreter, initialized to a sentinel guaranteed to
# *NEVER* match.

# Initialized below.
HINT_ATTR_LIST: Any = SENTINEL
'''
**List sign** (i.e., arbitrary object uniquely identifying PEP-compliant list
type hints) importable under the active Python interpreter.
'''


# Initialized below.
HINT_ATTR_TUPLE: Any = SENTINEL
'''
**Tuple sign** (i.e., arbitrary object uniquely identifying PEP-compliant tuple
type hints) importable under the active Python interpreter.
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Permit redefinition of these globals below.
    global HINT_ATTR_LIST, HINT_ATTR_TUPLE

    # Defer initialization-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

    # If the active Python interpreter targets at least Python >= 3.9...
    if IS_PYTHON_AT_LEAST_3_9:
        # Initialize PEP 585-compliant types.
        HINT_ATTR_LIST = list
        HINT_ATTR_TUPLE = tuple
    # Else...
    else:
        from typing import List, Tuple

        # Default PEP 585-compliant types unavailable under this interpreter to
        # corresponding albeit deprecated "typing" singletons.
        HINT_ATTR_LIST = List
        HINT_ATTR_TUPLE = Tuple

# Initialize this submodule.
_init()
