#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator parameter PEP-noncompliant type checking.**

This private submodule dynamically generates pure-Python code type-checking all
parameters annotated with **PEP-noncompliant type hints** (e.g., tuple unions,
fully-qualified forward references) of the callable currently being decorated
by the :func:`beartype.beartype` decorator.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._decor._code._codehint import code_resolve_forward_refs
from beartype._decor._code._snippet import (
    CODE_PARAM_VARIADIC_POSITIONAL,
    CODE_PARAM_KEYWORD_ONLY,
    CODE_PARAM_POSITIONAL_OR_KEYWORD,
    CODE_PARAM_HINT,
)
from beartype._decor._data import BeartypeData
from inspect import Parameter

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CODERS                            }....................
def nonpep_code_check_param(
    data: BeartypeData,
    func_arg : Parameter,
    func_arg_index : int,
) -> str:
    '''
    Python code type-checking the parameter with the passed signature and index
    annotated with a **PEP-noncompliant type hint** (e.g., type hint complying
    with :mod:`beartype`-specific semantics, including tuple unions and
    fully-qualified forward references) of the decorated callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.
    func_arg : Parameter
        :mod:`inspect`-specific object describing this parameter.
    func_arg_index : int
        0-based index of this parameter in this callable's signature.

    Returns
    ----------
    str
        Python code type-checking all parameters annotated with
        PEP-noncompliant type hints of the decorated callable if any *or* the
        empty string otherwise.

    Raises
    ----------
    BeartypeDecorHintValueNonPepException
        If any type hint annotating any parameter of this callable is *not*
        **PEP-noncompliant** (i.e., fails to comply with
        :mod:`beartype`-specific semantics, including tuple unions and
        fully-qualified forward references).
    '''
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))
    assert isinstance(func_arg, Parameter), (
        '{!r} not parameter metadata.'.format(func_arg))
    assert isinstance(func_arg_index, int), (
        '{!r} not parameter index.'.format(func_arg_index))

    # Note that this annotation need *NOT* be validated as a PEP-noncompliant
    # annotation (e.g., by explicitly calling the die_unless_hint_nonpep()
    # function). By design, the caller already guarantees this to be the case.

    # Human-readable label describing this annotation.
    func_arg_hint_label = (
        '{} parameter "{}" type hint'.format(
            data.func_name, func_arg.name))

    # Python code evaluating to this annotation.
    func_arg_type_expr = CODE_PARAM_HINT.format(func_arg.name)

    # Python code evaluating to this parameter's current value when passed
    # as a keyword.
    func_arg_value_key_expr = 'kwargs[{!r}]'.format(func_arg.name)

    # Python code to be returned, initialized with one or more Python
    # statements resolving forward references in this annotation.
    func_code = code_resolve_forward_refs(
        hint=func_arg.annotation,
        hint_expr=func_arg_type_expr,
        hint_label=func_arg_hint_label,
    )

    # If this parameter is a tuple of positional variadic parameters
    # (e.g., "*args"), iteratively check these parameters.
    if func_arg.kind is Parameter.VAR_POSITIONAL:
        func_code += CODE_PARAM_VARIADIC_POSITIONAL.format(
            func_name=data.func_name,
            arg_name=func_arg.name,
            arg_index=func_arg_index,
            arg_type_expr=func_arg_type_expr,
        )
    # Else if this parameter is keyword-only, check this parameter only
    # by lookup in the variadic "**kwargs" dictionary.
    elif func_arg.kind is Parameter.KEYWORD_ONLY:
        func_code += CODE_PARAM_KEYWORD_ONLY.format(
            func_name=data.func_name,
            arg_name=func_arg.name,
            arg_type_expr=func_arg_type_expr,
            arg_value_key_expr=func_arg_value_key_expr,
        )
    # Else, this parameter may be passed either positionally or as a
    # keyword. Check this parameter both by lookup in the variadic
    # "**kwargs" dictionary *AND* by index into the variadic "*args"
    # tuple.
    else:
        # String evaluating to this parameter's current value when
        # passed positionally.
        func_arg_value_pos_expr = 'args[{!r}]'.format(func_arg_index)
        func_code += CODE_PARAM_POSITIONAL_OR_KEYWORD.format(
            func_name=data.func_name,
            arg_name=func_arg.name,
            arg_index=func_arg_index,
            arg_type_expr=func_arg_type_expr,
            arg_value_key_expr=func_arg_value_key_expr,
            arg_value_pos_expr=func_arg_value_pos_expr,
        )

    # Return this Python code.
    return func_code
