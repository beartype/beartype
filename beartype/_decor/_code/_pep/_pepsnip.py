#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant code snippets.**

This private submodule *only* defines **PEP-compliant code snippets** (i.e.,
triple-quoted pure-Python code constants formatted and concatenated together
into wrapper functions implementing type-checking for decorated callables
annotated by PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ PARAMETERS                        }....................
from inspect import Parameter

# ....................{ CODE ~ hint                       }....................
PEP_CODE_HINT = '__beartypistry[{!r}]'
'''
PEP-compliant code snippet accessing the object whose fully-qualified name is
formatted into this snippet by the caller.
'''

# ....................{ CODE ~ param                      }....................
PARAM_KIND_TO_PEP_CODE_GET = {
    # Snippet localizing any positional or keyword parameter as follows:
    #
    # * If this parameter's 0-based index (in the parameter list of the
    #   decorated callable's signature) does *NOT* exceed the number of
    #   positional parameters passed to the wrapper function, localize this
    #   positional parameter from the wrapper's variadic "*args" tuple.
    # * Else if this parameter's name is in the dictionary of keyword
    #   parameters passed to the wrapper function, localize this keyword
    #   parameter from the wrapper's variadic "*kwargs" tuple.
    # * Else, this parameter is unpassed. In this case, localize this parameter
    #   as a placeholder value guaranteed to *NEVER* be passed to any wrapper
    #   function: the private "__beartypistry" singleton passed to this wrapper
    #   function as a hidden default parameter and thus accessible here.
    Parameter.POSITIONAL_OR_KEYWORD: '''
    __beartype_got = (
        args[{arg_index} if {arg_index} < len(args) else
        kwargs.get({arg_name!r}, __beartypistry)
    )
    if __beartype_got is not __beartypistry:
''',

    # Snippet localizing any keyword-only parameter (e.g., "*, kwarg") by
    # lookup in the wrapper's variadic "**kwargs" dictionary. (See above.)
    Parameter.KEYWORD_ONLY: '''
    __beartype_got = kwargs.get({arg_name!r}, __beartypistry)
    if __beartype_got is not __beartypistry:
''',

    # Snippet iteratively localizing all variadic positional parameters.
    Parameter.VAR_POSITIONAL: '''
    for __beartype_got in args[{arg_index!r}:]:
''',
}
'''
Dictionary mapping from the type of each callable parameter supported by the
:func:`beartype.beartype` decorator to a PEP-compliant code snippet localizing
that callable's next parameter to be type-checked.
'''

# ....................{ CODE ~ return                     }....................
PEP_CODE_GET_RETURN = '''
    __beartype_got = __beartype_func(*args, **kwargs)
    (
'''
'''
PEP-compliant code snippet calling the decorated callable and localizing the
value returned by that call.

Note that this snippet intentionally terminates on a line containing only the
``(`` character, enabling subsequent type-checking code to effectively ignore
indentation level and thus uniformly operate on both:

* Parameters localized via values of the :data:`PARAM_KIND_TO_PEP_CODE_GET`
  dictionary.
* Return values localized via this sippet.
'''


PEP_CODE_RETURN_CHECKED = '''
    )
    return __beartype_got
'''
'''
PEP-compliant code snippet returning from the wrapper function the successfully
type-checked value returned from the decorated callable.

Note that this snippet intentionally terminates on a line containing only the
``)`` character, which closes the corresponding character terminating the
:data:`PEP_CODE_GET_RETURN` snippet.
'''
