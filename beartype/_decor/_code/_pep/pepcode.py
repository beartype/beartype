#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type-checking code generators.**

This private submodule dynamically generates pure-Python code type-checking all
parameters and return values annotated with **PEP-compliant type hints**
(i.e., :mod:`beartype`-agnostic annotations compliant with
annotation-centric PEPs) of the decorated callable.

This private submodule also implements `PEP 484`_ (i.e., Type Hints) support by
transparently converting high-level special-purpose abstract types and methods
defined by the stdlib :mod:`typing` module into low-level general-use concrete
types and code snippets independent of that module.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
# from beartype.roar import BeartypeDecorHintValuePepException
from beartype._decor._code._pep._pepsnip import (
    PEP_CODE_PARAM_HINT,
    PEP_CODE_RETURN_HINT,
    PEP_CODE_RETURN_CHECKED,
    # PEP_CODE_RETURN_HINT,
    # PARAM_KIND_TO_PEP_CODE,
)
from beartype._decor._data import BeartypeData
from beartype._util.hint.utilhintpep import (
    die_unless_hint_pep_supported)
from inspect import Parameter

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CODERS                            }....................
#FIXME: Implement us up.
# def pep_code_check_param(
#     data: BeartypeData,
#     func_arg: Parameter,
#     func_arg_index: int,
# ) -> str:
#     '''
#     Python code type-checking the parameter with the passed signature and index
#     annotated with a **PEP-compliant type hint** (e.g.,:mod:`beartype`-agnostic
#     annotation compliant with annotation-centric PEPs) of the decorated
#     callable.
#
#     Parameters
#     ----------
#     data : BeartypeData
#         Decorated callable to be type-checked.
#     func_arg : Parameter
#         :mod:`inspect`-specific object describing this parameter.
#     func_arg_index : int
#         0-based index of this parameter in this callable's signature.
#
#     Returns
#     ----------
#     str
#         Python code type-checking this parameter against this hint.
#
#     Raises
#     ----------
#     BeartypeDecorHintValuePepException
#         If either this parameter or this hint is *not* PEP-compliant.
#     '''
#     # Note this hint need *NOT* be validated as a PEP-noncompliant type hint
#     # (e.g., by explicitly calling the die_unless_hint_pep_supported() function). By
#     # design, the caller already guarantees this to be the case.
#     #
#     assert isinstance(data, BeartypeData), (
#         '{!r} not @beartype data.'.format(data))
#     assert isinstance(func_arg, Parameter), (
#         '{!r} not parameter metadata.'.format(func_arg))
#     assert isinstance(func_arg_index, int), (
#         '{!r} not parameter index.'.format(func_arg_index))
#
#     # Human-readable label describing this parameter.
#     func_arg_hint_label = (
#         '{} parameter "{}" type hint'.format(
#             data.func_name, func_arg.name))
#
#     # Python code template type-checking this parameter if this type of
#     # parameter is supported *OR* "None" otherwise.
#     func_arg_code_template = PARAM_KIND_TO_PEP_CODE.get(func_arg.kind, None)
#
#     # If this type of parameter is unsupported, raise an exception.
#     #
#     # Note this edge case should *NEVER* occur, as the parent
#     # _code_check_params() function should have simply ignored this parameter.
#     if func_arg_code_template is None:
#         raise BeartypeDecorHintValuePepException(
#             '{} kind {!r} unsupported.'.format(
#                 func_arg_hint_label, func_arg.kind))
#     # Else, this type of parameter is supported. Ergo, this code is non-"None".
#
#     # Python code evaluating to this hint.
#     func_arg_type_expr = PEP_CODE_PARAM_HINT.format(func_arg.name)
#
#     # Python code evaluating to this parameter's current value when passed
#     # as a keyword.
#     func_arg_value_key_expr = 'kwargs[{!r}]'.format(func_arg.name)
#
#     # Python code evaluating to this parameter's current value when passed
#     # positionally.
#     func_arg_value_pos_expr = 'args[{!r}]'.format(func_arg_index)
#
#     # Return Python code type-checking this parameter against this hint.
#     return func_arg_code_template.format(
#         func_name=data.func_name,
#         arg_name=func_arg.name,
#         arg_index=func_arg_index,
#         arg_type_expr=func_arg_type_expr,
#         arg_value_key_expr=func_arg_value_key_expr,
#         arg_value_pos_expr=func_arg_value_pos_expr,
#     )


def pep_code_check_return(data: BeartypeData) -> str:
    '''
    Python code type-checking the return value annotated with a **PEP-compliant
    type hint** (e.g.,:mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs) of the decorated callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Python code type-checking this return value against this hint.

    Raises
    ----------
    BeartypeDecorHintValuePepException
        If this hint is *not* PEP-compliant.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_unless_hint_pep_supported() function). By
    # design, the caller already guarantees this to be the case.
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))

    # Human-readable label describing this hint.
    func_return_hint_label = '{} return typing annotation'.format(
        data.func_name)

    # String evaluating to this return value's annotated type.
    func_return_hint_expr = PEP_CODE_RETURN_HINT
    #print('Return annotation: {{}}'.format({func_return_type_expr}))

    # Return Python code, calling the decorated callable, type-checking the
    # returned value, and returning this value from this wrapper function.
    return PEP_CODE_RETURN_CHECKED.format(
        func_name=data.func_name,

        #FIXME: Define us up to access the corresponding low-level typistry
        #type with which we actually implement this type-checking.
        # return_type_expr=func_return_type_expr,
        return_hint_expr=func_return_hint_expr,
    )

# ....................{ CODERS                            }....................
def _pep_code_check(
    data: BeartypeData,
    hint: object,
    hint_expr: str,
    hint_label: str,
) -> str:
    '''
    Python code type-checking the parameter or return value accessed by the
    passed expression and annotated by the passed PEP-compliant type hint of
    the decorated callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.
    hint : object
        PEP-compliant type hint annotating this parameter or return value.
    hint_expr : str
        Python expression accessing this hint in the wrapper function
        type-checking the decorated callable.
    hint_label : str
        Human-readable label describing this hint.

    Returns
    ----------
    str
        Python code type-checking this parameter or return value against this
        hint.

    Raises
    ----------
    BeartypeDecorHintValuePepException
        If this hint is *not* PEP-compliant.
    '''
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))
    assert isinstance(hint_expr, str), (
        '{!r} not a Python expression.'.format(hint_expr))
    assert isinstance(hint_label, str), (
        '{!r} not a human-readable label.'.format(hint_label))

    # If this is *NOT* a supported PEP-compliant type hint, raise an exception.
    die_unless_hint_pep_supported(hint)
