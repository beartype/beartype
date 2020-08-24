#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-noncompliant code snippets.**

This private submodule *only* defines **PEP-noncompliant code snippets** (i.e.,
triple-quoted pure-Python code constants formatted and concatenated together
into wrapper functions implementing type-checking for decorated callables
annotated by PEP-noncompliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._decor._code.codemain import (
    PARAM_NAME_FUNC,
    # PARAM_NAME_TYPISTRY,
)
from inspect import Parameter

# ....................{ CODE ~ hint                       }....................
#FIXME: Refactor type and forward reference annotations access to access
#fully-qualified classnames on the "__beartypistry", as doing so is more
#efficient and simpler than the existing forward reference resolution
#mechanism. Moreover, doing so avoids implicit dictionary lookups on
#"__beartype_func.__annotations__" for standard types and is thus more
#efficient for the common case as well.
#
#That said, note that tuple annotations will probably continue to require
#accessing this function-specific dictionary. So it goes. Ergo, we'll probably
#want to:
#
#* Rename:
#  * "NONPEP_CODE_PARAM_HINT" to "NONPEP_CODE_PARAM_HINT_TUPLE".
#  * "NONPEP_CODE_RETURN_HINT" to "NONPEP_CODE_RETURN_HINT_TUPLE".
#* Define a new:
#  * "NONPEP_CODE_PARAM_HINT_NONTUPLE" global string constant.
#  * "NONPEP_CODE_RETURN_HINT_NONTUPLE" global string constant.

NONPEP_CODE_PARAM_HINT = PARAM_NAME_FUNC + '.__annotations__[{!r}]'
'''
PEP-noncompliant code snippet accessing the annotation with an arbitrary name
formatted into this snippet by the caller.
'''


NONPEP_CODE_RETURN_HINT = PARAM_NAME_FUNC + ".__annotations__['return']"
'''
PEP-noncompliant code snippet accessing the **return annotation** (i.e.,
annotation synopsizing the type hint for this callable's return value).
'''

# ....................{ CODE ~ param                      }....................
PARAM_KIND_TO_NONPEP_CODE = {
    # Snippet type-checking any standard positional or keyword parameter both
    # by lookup in the wrapper function's variadic "**kwargs" dictionary *AND*
    # by index into the wrapper function's variadic "*args" tuple.
    Parameter.POSITIONAL_OR_KEYWORD: '''
    # If this positional or keyword parameter was passed, type-check this
    # parameter against this PEP-noncompliant type hint.
    if not (
        isinstance(args[{arg_index}], {hint_expr})
        if __beartype_args_len > {arg_index} else
        isinstance(kwargs[{arg_name!r}], {hint_expr})
        if {arg_name!r} in kwargs else True
    ):
        raise __beartype_nonpep_param_exception(
            '{func_name} parameter {arg_name}={{}} not a {{!r}}.'.format(
            __beartype_trim(
                args[{arg_index}] if __beartype_args_len > {arg_index} else
                kwargs[{arg_name!r}]
            ),
            {hint_expr})
        )
''',

    # Snippet type-checking any keyword-only parameter (e.g., "*, kwarg") by
    # lookup in the wrapper function's variadic "**kwargs" dictionary.
    Parameter.KEYWORD_ONLY: '''
    # If this keyword-only parameter was passed, type-check this parameter
    # against this PEP-noncompliant type hint.
    if {arg_name!r} in kwargs and not isinstance(
        kwargs[{arg_name!r}], {hint_expr}):
        raise __beartype_nonpep_param_exception(
            '{func_name} keyword-only parameter '
            '{arg_name}={{}} not a {{!r}}.'.format(
                __beartype_trim(kwargs[{arg_name!r}]), {hint_expr}))
''',

    # Snippet type-checking any variadic positional pseudo-parameter (e.g.,
    # "*args") by iteratively checking all relevant parameters.
    Parameter.VAR_POSITIONAL: '''
    # Type-check all passed positional variadic parameters against this
    # PEP-noncompliant type hint.
    for __beartype_arg in args[{arg_index!r}:]:
        if not isinstance(__beartype_arg, {hint_expr}):
            raise __beartype_nonpep_param_exception(
                '{func_name} positional variadic parameter '
                '{{}} not a {{!r}}.'.format(
                    __beartype_trim(__beartype_arg), {hint_expr}))
''',
}
'''
Dictionary mapping from the type of each callable parameter supported by the
:func:`beartype.beartype` decorator to a PEP-noncompliant code snippet
type-checking that type.
'''

# ....................{ CODE ~ return                     }....................
NONPEP_CODE_RETURN_CHECKED = '''
    # Call this function with all passed parameters, type-check the value
    # returned from this call against this PEP-noncompliant type hint, and
    # return this value only if this check succeeds.
    __beartype_return_value = {param_name_func}(*args, **kwargs)
    if not isinstance(__beartype_return_value, {{hint_expr}}):
        raise __beartype_nonpep_return_exception(
            '{{func_name}} return value {{{{}}}} not a {{{{!r}}}}.'.format(
                __beartype_trim(__beartype_return_value), {{hint_expr}}))
    return __beartype_return_value'''.format(
        param_name_func=PARAM_NAME_FUNC)
'''
PEP-noncompliant code snippet type-checking the return value if any.

Specifically, this snippet (in order):

#. Calls the decorated callable.
#. Localizes the value returned by that call.
#. Type-checks that value.
#. Returns that value as this wrapper function's value.
'''

# ....................{ CODE ~ reference : str            }....................
NONPEP_CODE_STR_REPLACE = '''
    # If this annotation is still a classname, this annotation has yet to be
    # replaced by the corresponding class, implying this to be the first call
    # to this callable. Perform this replacement in this call, preventing
    # subsequent calls to this callable from repeatedly doing so.
    if isinstance({hint_expr}, str):
        {hint_type_import_code}

        # Validate this class to be either a class or tuple of classes,
        # preventing this attribute from being yet another classname. (The
        # recursion definitively ends here, folks.)
        __beartype_die_unless_hint_nonpep(
            hint={hint_type_basename},
            hint_label={hint_label!r},
            is_str_valid=False,
        )

        # Replace the external copy of this annotation stored in this
        # function's signature by this class -- guaranteeing that subsequent
        # access of this annotation via "__beartype_hints" access this class
        # rather than this classname.
        {hint_expr} = {hint_type_basename}
'''


NONPEP_CODE_STR_IMPORT = '''
        # Attempt to import this attribute from this module, implicitly
        # raising a human-readable "ImportError" or "ModuleNotFoundError"
        # exception on failure.
        from {hint_type_module_name} import {hint_type_basename}
'''

# ....................{ CODE ~ reference : tuple          }....................
NONPEP_CODE_TUPLE_STR_TEST = '''
    # If the first classname in this annotation is still a classname, this
    # annotation has yet to be replaced by a tuple containing classes rather
    # than classnames, implying this to be the first call to this callable.
    # Perform this replacement in this call, preventing subsequent calls to
    # this callable from repeatedly doing so.
    if isinstance({subhint_type_name_expr}, str):
        # List replacing all classnames in this tuple with the classes with
        # these classnames with which this tuple will be subsequently replaced.
        __beartype_func_hint_list = []
'''


NONPEP_CODE_TUPLE_STR_IMPORT = '''
        # Attempt to import this attribute from this module, implicitly
        # raising a human-readable "ImportError" exception on failure.
        from {subhint_type_module_name} import {subhint_type_basename}
'''


NONPEP_CODE_TUPLE_STR_APPEND = '''
        # Validate this member to be a class, preventing this member from being
        # yet another classname or tuple of classes and/or classnames. (The
        # recursion definitively ends here, folks.)
        if not isinstance({subhint_type_basename}, type):
            raise BeartypeException(
                '{hint_label} tuple member {{}} not a class.'.format(
                    {subhint_type_basename}))

        # Append this class to this list.
        __beartype_func_hint_list.append({subhint_type_basename})
'''


NONPEP_CODE_TUPLE_CLASS_APPEND = '''
        # Append this class copied from the original tuple to this list.
        __beartype_func_hint_list.append({subhint_expr})
'''


NONPEP_CODE_TUPLE_REPLACE = '''
        # Replace the external copy of this annotation stored in this
        # function's signature by this list coerced back into a tuple for
        # conformance with isinstance() constraints -- guaranteeing that
        # subsequent access of this annotation via "__beartype_hints" accesses
        # this class rather than this classname.
        {hint_expr} = tuple(__beartype_func_hint_list)

        # Nullify this list for safety.
        __beartype_func_hint_list = None
'''
