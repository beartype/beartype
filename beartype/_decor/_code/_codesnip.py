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
CODE_SIGNATURE = '''
def {func_wrapper_name}(
    *args,
    __beartype_func=__beartype_func,
    __beartypistry=__beartypistry,
    **kwargs
):
    # Localize the number of passed positional arguments for efficiency.
    __beartype_args_len = len(args)
'''
'''
PEP-agnostic code snippet declaring the signature of the wrapper function
type-checking the decorated callable.
'''


CODE_RETURN_UNCHECKED = '''
    # Call this function with all passed parameters and return the value
    # returned from this call.
    return __beartype_func(*args, **kwargs)'''
'''
PEP-agnostic code snippet calling the decorated callable *without*
type-checking the value returned by that call (if any).
'''

# ....................{ CODE ~ indent                     }....................
CODE_INDENT_1 = '    '
'''
PEP-agnostic code snippet expanding to a single level of indentation.
'''


CODE_INDENT_2 = CODE_INDENT_1*2
'''
PEP-agnostic code snippet expanding to two levels of indentation.
'''


CODE_INDENT_3 = CODE_INDENT_2 + CODE_INDENT_1
'''
PEP-agnostic code snippet expanding to three levels of indentation.
'''
