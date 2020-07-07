#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator general-purpose code snippets.**

This private submodule *only* defines **code snippets** (i.e., triple-quoted
pure-Python code constants formatted and concatenated together into wrapper
functions implementing type-checking for decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ CODE                              }....................
#FIXME: Add below if desired:
#     __beartype_hints=__beartype_hints,
CODE_SIGNATURE = '''
def {func_wrapper_name}(
    *args,
    __beartype_func=__beartype_func,
    __beartypistry=__beartypistry,
    **kwargs
):
'''
'''
PEP-agnostic code snippet declaring the signature of the wrapper function
type-checking the decorated callable.
'''


CODE_RETURN_UNCHECKED = '''
    return __beartype_func(*args, **kwargs)
'''
'''
PEP-agnostic code snippet calling the decorated callable *without*
type-checking the value returned by that call (if any).
'''
