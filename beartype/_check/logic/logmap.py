#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **hint sign logic mappings** (i.e., dictionary globals mapping from
signs uniquely identifying various kinds of type hints to corresponding
dataclasses encapsulating all low-level Python code snippets and associated
metadata required to dynamically generate high-level Python code snippets fully
type-checking those type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Dict
from beartype._check.logic.logcls import (
    HintSignLogicContainerArgs1,
    HintSignLogicReiterableArgs1,
    HintSignLogicSequenceArgs1,
)
from beartype._data.hint.pep.sign.datapepsigncls import HintSign

# ....................{ MAPPINGS                           }....................
# Initialized by the _init() function defined below.
HINT_SIGN_PEP484585_CONTAINER_ARGS_1_TO_LOGIC: (
    Dict[HintSign, HintSignLogicContainerArgs1]) = {}
'''
Dictionary mapping from the sign uniquely identifying each applicable kind of
**standard single-argument container type hint** (i.e., :pep:`484`- or
:pep:`585`-compliant type hint describing a standard container, subscripted by
exactly one child type hint constraining *all* items contained in that
container) to the hint sign logic dataclass dynamically generating Python code
snippets type-checking that kind of type hint.
'''

# ..................{ PRIVATE ~ main                         }..................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer function-specific imports.
    from beartype._data.hint.pep.sign.datapepsignset import (
        HINT_SIGNS_REITERABLE_ARGS_1,
        HINT_SIGNS_SEQUENCE_ARGS_1,
    )

    # ....................{ DEFINE                         }....................
    # Hint sign logic singletons.
    HINT_SIGN_LOGIC_REITERABLE_ARGS_1 = HintSignLogicReiterableArgs1()
    HINT_SIGN_LOGIC_SEQUENCE_ARGS_1 = HintSignLogicSequenceArgs1()

    # For each sign identifying a single-argument reiterable hint...
    for hint_sign in HINT_SIGNS_REITERABLE_ARGS_1:
        # Map this sign to this logic dataclass.
        HINT_SIGN_PEP484585_CONTAINER_ARGS_1_TO_LOGIC[hint_sign] = (
            HINT_SIGN_LOGIC_REITERABLE_ARGS_1)

    # For each sign identifying a single-argument sequence hint...
    for hint_sign in HINT_SIGNS_SEQUENCE_ARGS_1:
        # Map this sign to this logic dataclass.
        HINT_SIGN_PEP484585_CONTAINER_ARGS_1_TO_LOGIC[hint_sign] = (
            HINT_SIGN_LOGIC_SEQUENCE_ARGS_1)


# Initialize this submodule.
_init()
