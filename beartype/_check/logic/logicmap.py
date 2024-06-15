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
from beartype._check.checkmagic import VAR_NAME_RANDOM_INT
from beartype._check.logic.logiccls import HintSignLogic
from beartype._data.hint.pep.sign.datapepsigncls import HintSign

# ....................{ MAPPINGS                           }....................
# Initialized by the _init() function defined below.
HINT_SIGN_PEP484585_CONTAINER_ARGS_1_TO_LOGIC: (
    Dict[HintSign, HintSignLogic]) = {}
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
        HINT_SIGNS_CONTAINER_ARGS_1,
        HINT_SIGNS_REITERABLE_ARGS_1,
        HINT_SIGNS_SEQUENCE_ARGS_1,
    )

    # ....................{ SNIPPETS                       }....................
    # PEP 484- and 585-compliant code snippet generically type-checking the
    # current pith against *any* arbitrary kind of single-argument standard
    # container type hint.
    _CODE_PEP484585_CONTAINER_ARGS_1 = '''(
    _{indent_curr}    # True only if this pith is of this container type *AND*...
    _{indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
    _{indent_curr}    # True only if either this container is empty *OR* this container
    _{indent_curr}    # is both non-empty and the first item satisfies this hint.
    _{indent_curr}    (not {pith_curr_var_name} or {hint_child_placeholder})
    _{indent_curr})'''

    # PEP 484- and 585-compliant Python expression yielding the first item of
    # the current reiterable pith.
    _CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR = (
        '''next(iter({pith_curr_var_name}))''')

    # PEP 484- and 585-compliant Python expression yielding a randomly indexed
    # item of the current sequence pith.
    _CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR = (
        f'''{{pith_curr_var_name}}[{VAR_NAME_RANDOM_INT} % len({{pith_curr_var_name}})]''')

    # ....................{ LOCALS                         }....................
    # str.format() methods bound to string locals defined above.
    _CODE_PEP484585_CONTAINER_ARGS_1_format = (
        _CODE_PEP484585_CONTAINER_ARGS_1.format)
    _CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR_format = (
        _CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR.format)
    _CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR_format = (
        _CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR.format)

    # ....................{ DEFINE                         }....................
    # For each sign identifying some kind of single-argument container hint...
    for hint_sign in HINT_SIGNS_CONTAINER_ARGS_1:
        # Map this sign to this logic dataclass.
        HINT_SIGN_PEP484585_CONTAINER_ARGS_1_TO_LOGIC[hint_sign] = (
            HintSignLogic(code_format=_CODE_PEP484585_CONTAINER_ARGS_1_format))

    # For each sign identifying a single-argument reiterable hint...
    for hint_sign in HINT_SIGNS_REITERABLE_ARGS_1:
        # Logic dataclass type-checking this sign.
        hint_sign_logic = HINT_SIGN_PEP484585_CONTAINER_ARGS_1_TO_LOGIC[
            hint_sign]

        # Classify this str.format() method.
        hint_sign_logic.pith_child_expr_format = (
            _CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR_format)

    # For each sign identifying a single-argument sequence hint...
    for hint_sign in HINT_SIGNS_SEQUENCE_ARGS_1:
        # Logic dataclass type-checking this sign.
        hint_sign_logic = HINT_SIGN_PEP484585_CONTAINER_ARGS_1_TO_LOGIC[
            hint_sign]

        # Classify this str.format() method.
        hint_sign_logic.pith_child_expr_format = (
            _CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR_format)

        # Classify that code snippets dynamically generated by this logic
        # require pseudo-random integers (to type-check random sequence items).
        hint_sign_logic.is_var_random_int_needed = True


# Initialize this submodule.
_init()
