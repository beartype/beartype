#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator** `PEP 484`_-agnostic **code constants.**

This private submodule *only* defines **code constants** (i.e., global
triple-quoted strings containing pure-Python code snippets required at
decorate time by the :func:`beartype.beartype` decorator to dynamically
generate a new callable wrapping the decorated callable with runtime type
checking).

This private submodule is the `PEP 484`_-agnostic analogue to the `PEP
484_`-specific :mod:`beartype._decor.pep484.p484snippet` submodule.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ CODE                              }....................
CODE_SIGNATURE = '''
def {func_wrapper_name}(
    *args,
    __beartype_func=__beartype_func,
    __beartypistry=__beartypistry,
    **kwargs
):
'''
#FIXME: Add above if desired:
#     __beartype_hints=__beartype_hints,

# ....................{ CODE ~ annotations                }....................
#FIXME: Refactor type and forward reference annotations access to access
#fully-qualified classnames on the "__beartypistry". That said, note that tuple
#annotations will probably continue to require accessing this function-specific
#dictionary. So it goes.

CODE_PARAM_HINT = '__beartype_func.__annotations__[{!r}]'
# CODE_PARAM_HINT = '__beartype_hints[{!r}]'
'''
Code snippet accessing the annotation with an arbitrary name formatted into
this snippet by the caller.
'''


CODE_RETURN_HINT = "__beartype_func.__annotations__['return']"
# CODE_RETURN_HINT = "__beartype_hints['return']"
'''
Code snippet accessing the **return annotation** (i.e., annotation synopsizing
the type hint for this callable's return value).
'''

# ....................{ CODE ~ param                      }....................
CODE_PARAM_VARIADIC_POSITIONAL = '''
    for __beartype_arg in args[{arg_index!r}:]:
        if not isinstance(__beartype_arg, {arg_type_expr}):
            raise __beartype_param_exception(
                '{func_name} positional variadic parameter '
                '{arg_index} {{}} not a {{!r}}.'.format(
                    __beartype_trim(__beartype_arg), {arg_type_expr}))
'''


CODE_PARAM_KEYWORD_ONLY = '''
    if {arg_name!r} in kwargs and not isinstance(
        {arg_value_key_expr}, {arg_type_expr}):
        raise __beartype_param_exception(
            '{func_name} keyword-only parameter '
            '{arg_name}={{}} not a {{!r}}.'.format(
                __beartype_trim({arg_value_key_expr}), {arg_type_expr}))
'''


CODE_PARAM_POSITIONAL_OR_KEYWORD = '''
    if not (
        isinstance({arg_value_pos_expr}, {arg_type_expr})
        if len(args) > {arg_index} else
        isinstance({arg_value_key_expr}, {arg_type_expr})
        if {arg_name!r} in kwargs else True):
            raise __beartype_param_exception(
                '{func_name} parameter {arg_name}={{}} not a {{!r}}.'.format(
                __beartype_trim({arg_value_pos_expr} if len(args) > {arg_index} else {arg_value_key_expr}),
                {arg_type_expr}))
'''

# ....................{ CODE ~ return                     }....................
CODE_RETURN_CHECKED = '''
    __beartype_return_value = __beartype_func(*args, **kwargs)
    if not isinstance(__beartype_return_value, {return_type_expr}):
        raise __beartype_return_exception(
            '{func_name} return value {{}} not a {{!r}}.'.format(
                __beartype_trim(__beartype_return_value), {return_type_expr}))
    return __beartype_return_value
'''


CODE_RETURN_UNCHECKED = '''
    return __beartype_func(*args, **kwargs)
'''

# ....................{ CODE ~ reference : str            }....................
CODE_STR_REPLACE = '''
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


CODE_STR_IMPORT = '''
        # Attempt to import this attribute from this module, implicitly
        # raising a human-readable "ImportError" or "ModuleNotFoundError"
        # exception on failure.
        from {hint_type_module_name} import {hint_type_basename}
'''

# ....................{ CODE ~ reference : tuple          }....................
CODE_TUPLE_STR_TEST = '''
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


CODE_TUPLE_STR_IMPORT = '''
        # Attempt to import this attribute from this module, implicitly
        # raising a human-readable "ImportError" exception on failure.
        from {subhint_type_module_name} import {subhint_type_basename}
'''


CODE_TUPLE_STR_APPEND = '''
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


CODE_TUPLE_CLASS_APPEND = '''
        # Append this class copied from the original tuple to this list.
        __beartype_func_hint_list.append({subhint_expr})
'''


CODE_TUPLE_REPLACE = '''
        # Replace the external copy of this annotation stored in this
        # function's signature by this list coerced back into a tuple for
        # conformance with isinstance() constraints -- guaranteeing that
        # subsequent access of this annotation via "__beartype_hints" accesses
        # this class rather than this classname.
        {hint_expr} = tuple(__beartype_func_hint_list)

        # Nullify this list for safety.
        __beartype_func_hint_list = None
'''
