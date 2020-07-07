#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant code snippets.**

This private submodule *only* defines **PEP-compliant code snippets** (i.e.,
triple-quoted pure-Python code constants formatted and concatenated together
into wrapper functions implementing type-checking for decorated callables
annotated with PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ CODE ~ hint                       }....................
# PEP_CODE_PARAM_HINT = '__beartype_hints[{!r}]'
PEP_CODE_PARAM_HINT = '__beartype_func.__annotations__[{!r}]'
'''
PEP-compliant code snippet accessing the annotation with an arbitrary name
formatted into this snippet by the caller.
'''


# PEP_CODE_RETURN_HINT = "__beartype_hints['return']"
PEP_CODE_RETURN_HINT = "__beartype_func.__annotations__['return']"
'''
PEP-compliant code snippet accessing the **return annotation** (i.e.,
annotation synopsizing the type hint for this callable's return value).
'''

# ....................{ CODE ~ return                     }....................
PEP_CODE_RETURN_CHECKED = '''
    __beartype_return_value = __beartype_func(*args, **kwargs)
    if not isinstance(__beartype_return_value, {return_type_expr}):
        raise __beartype_return_exception(
            '{func_name} return value {{}} not a {{!r}}, '
            'violating type-hinted {{!r}} constraints.'.format(
                __beartype_trim(__beartype_return_value),
                {return_type_expr},
                {return_hint_expr},
            ))
    return __beartype_return_value
'''
'''
PEP-compliant code snippet type-checking the return value if any.

Specifically, this snippet (in order):

#. Calls the decorated callable.
#. Localizes the value returned by that call.
#. Type-checks that value.
#. Returns that value as this wrapper function's value.
'''
