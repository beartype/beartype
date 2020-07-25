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

This private submodule implements `PEP 484`_ (i.e., "Type Hints") support by
transparently converting high-level objects and types defined by the
:mod:`typing` module into low-level code snippets independent of that module.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintValuePepException
from beartype._decor._code._pep._pepsnip import (
    PARAM_KIND_TO_PEP_CODE_GET,
    PEP_CODE_HINT,
    PEP_CODE_GET_RETURN,
    PEP_CODE_RETURN_CHECKED,
)
from beartype._decor._data import BeartypeData
from beartype._util.utilobj import get_object_name_qualified
from inspect import Parameter

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CODERS                            }....................
def pep_code_check_param(
    data: BeartypeData,
    func_arg: Parameter,
    func_arg_index: int,
) -> str:
    '''
    Python code type-checking the parameter with the passed signature and index
    annotated by a **PEP-compliant type hint** (e.g.,:mod:`beartype`-agnostic
    annotation compliant with annotation-centric PEPs) of the decorated
    callable.

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
        Python code type-checking this parameter against this hint.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_unless_hint_pep_supported()
    # function). By design, the caller already guarantees this to be the case.
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))
    assert isinstance(func_arg, Parameter), (
        '{!r} not parameter metadata.'.format(func_arg))
    assert isinstance(func_arg_index, int), (
        '{!r} not parameter index.'.format(func_arg_index))

    # Human-readable label describing this parameter.
    func_arg_hint_label = (
        '{} parameter "{}" PEP type hint'.format(
            data.func_name, func_arg.name))

    # Python code template localizing this parameter if this kind of parameter
    # is supported *OR* "None" otherwise.
    func_arg_code_template = PARAM_KIND_TO_PEP_CODE_GET.get(
        func_arg.kind, None)

    # If this kind of parameter is unsupported, raise an exception.
    #
    # Note this edge case should *NEVER* occur, as the parent function should
    # have simply ignored this parameter.
    if func_arg_code_template is None:
        raise BeartypeDecorHintValuePepException(
            '{} kind {!r} unsupported.'.format(
                func_arg_hint_label, func_arg.kind))
    # Else, this kind of parameter is supported. Ergo, this code is non-"None".

    # Return Python code to...
    return (
        # Localize this parameter.
        func_arg_code_template.format(
            arg_name=func_arg.name, arg_index=func_arg_index)

        # Type-check this parameter.
        _pep_code_check(
            hint=func_arg.annotation,
            hint_label=func_arg_hint_label,
        )
    )


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
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_unless_hint_pep_supported() function). By
    # design, the caller already guarantees this to be the case.
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))

    # Human-readable label describing this hint.
    func_return_hint_label = '{} return PEP type hint'.format(data.func_name)

    # Return Python code to...
    return (
        # Call the decorated callable and localizing its return value.
        PEP_CODE_GET_RETURN +

        #FIXME: Type-check this localized value here.

        # Return this value from this wrapper function.
        PEP_CODE_RETURN_CHECKED
    )

# ....................{ CODERS ~ check                    }....................
def _pep_code_check(
    hint: object,
    hint_label: str,
):
    '''
    Python code type-checking the previously localized parameter or return
    value annotated by the passed PEP-compliant type hint against this hint of
    the decorated callable.

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be type-checked.
    hint_label : str
        Human-readable label prefixing this type hint's representation in
        exception messages raised by this function.

    Returns
    ----------
    str
        Python code type-checking the previously localized parameter or return
        value against this hint.
    '''

    # Fully-qualified name of this hint.
    hint_name = get_object_name_qualified(hint)

    # Python expression evaluating to this hint.
    hint_expr = PEP_CODE_HINT.format(hint_name)
