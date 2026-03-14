#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator code generator utilities** (i.e., low-level callables
assisting the parent :func:`beartype._decor._nontype._wrap.wrapmain` submodule).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.code.datacodename import CODE_PITH_ROOT_NAME_PLACEHOLDER
from beartype._util.text.utiltextmunge import replace_str_substrs

# ....................{ CACHERS                            }....................
def unmemoize_func_pith_check_expr(pith_check_expr: str, pith_repr: str) -> str:
    '''
    Convert the passed memoized code snippet type-checking any parameter or
    return of the decorated callable into an "unmemoized" code snippet
    type-checking a specific parameter or return of that callable.

    Specifically, this function (in order):

    #. Globally replaces all references to the
       :data:`.CODE_PITH_ROOT_NAME_PLACEHOLDER` placeholder substring
       cached into this code with the passed ``pith_repr`` parameter.
    #. Unmemoizes this code by globally replacing all relative forward
       reference placeholder substrings cached into this code with Python
       expressions evaluating to the classes referred to by those substrings
       relative to that callable when accessed via the private
       ``__beartypistry`` parameter.

    Parameters
    ----------
    pith_check_expr : str
        Memoized callable-agnostic code snippet type-checking either a parameter
        or the return of the decorated callable.
    pith_repr : str
        Machine-readable representation of the name of this parameter or return.

    Returns
    -------
    str
        This memoized code unmemoized by globally resolving all relative
        forward reference placeholder substrings cached into this code relative
        to the currently decorated callable.
    '''
    assert isinstance(pith_check_expr, str), (
        f'{repr(pith_check_expr)} not string.')
    assert isinstance(pith_repr, str), f'{repr(pith_repr)} not string.'

    # Generate an unmemoized parameter-specific code snippet type-checking this
    # parameter by replacing in this parameter-agnostic code snippet...
    pith_check_expr = replace_str_substrs(
        text=pith_check_expr,
        # This placeholder substring cached into this code with...
        old=CODE_PITH_ROOT_NAME_PLACEHOLDER,
        # This object representation of the name of this parameter or return.
        new=pith_repr,
    )

    # Return this unmemoized callable-specific code snippet.
    return pith_check_expr
