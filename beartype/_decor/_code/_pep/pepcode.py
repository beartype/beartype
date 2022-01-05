#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type-checking code generators.**

This private submodule dynamically generates pure-Python code type-checking all
parameters and return values annotated with **PEP-compliant type hints**
(i.e., :mod:`beartype`-agnostic annotations compliant with
annotation-centric PEPs) of the decorated callable.

This private submodule implements :pep:`484` (i.e., "Type Hints") support by
transparently converting high-level objects and types defined by the
:mod:`typing` module into low-level code snippets independent of that module.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPepException
from beartype._decor._cache.cachetype import (
    bear_typistry,
    register_typistry_forwardref,
)
from beartype._decor._code.codemagic import (
    ARG_NAME_TYPISTRY,
    EXCEPTION_PREFIX,
)
from beartype._decor._code._pep._pephint import pep_code_check_hint
from beartype._decor._code._pep._pepsnip import (
    PARAM_KIND_TO_PEP_CODE_LOCALIZE,
    PEP_CODE_CHECK_RETURN_PREFIX,
    PEP_CODE_CHECK_RETURN_SUFFIX,
    PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX,
    PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX,
    PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER,
)
from beartype._decor._call import BeartypeCall
from beartype._util.func.arg.utilfuncargiter import ParameterMeta
from beartype._util.hint.pep.proposal.pep484585.utilpep484585ref import (
    get_hint_pep484585_forwardref_classname_relative_to_object)
from beartype._util.kind.utilkinddict import update_mapping
from beartype._util.text.utiltextmunge import replace_str_substrs
from collections.abc import Iterable

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_RETURN_REPR = repr('return')
'''
Object representation of the magic string implying a return value in various
Python objects (e.g., the ``__annotations__`` dunder dictionary of annotated
callables).
'''

# ....................{ CODERS                            }....................
def pep_code_check_arg(
    bear_call: BeartypeCall,
    hint: object,
    arg_meta: ParameterMeta,
) -> str:
    '''
    Generate a Python code snippet type-checking the parameter with the passed
    signature and index annotated by a **PEP-compliant type hint** (e.g.,
    :mod:`beartype`-agnostic annotation compliant with annotation-centric PEPs)
    of the decorated callable.

    Parameters
    ----------
    bear_call : BeartypeCall
        Decorated callable to be type-checked.
    hint : object
        PEP-compliant type hint annotating this parameter.
    arg_meta : ParameterMeta
        Metadata describing this parameter.

    Returns
    ----------
    str
        Code type-checking this parameter.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_if_hint_pep_unsupported()
    # function). By design, the caller already guarantees this to be the case.
    assert bear_call.__class__ is BeartypeCall, (
        f'{repr(bear_call)} not @beartype call.')
    assert arg_meta.__class__ is ParameterMeta, (
        f'{repr(arg_meta)} not parameter metadata.')

    # Python code template localizing this parameter.
    #
    # Since @beartype now supports *ALL* parameter kinds, we safely assume this
    # behaves as expected without additional validation.
    # PARAM_LOCALIZE_TEMPLATE = PARAM_KIND_TO_PEP_CODE_LOCALIZE[arg_meta.kind]

    #FIXME: Preserved in the event of a new future unsupported parameter kind.
    # Python code template localizing this parameter if this kind of parameter
    # is supported *OR* "None" otherwise.
    PARAM_LOCALIZE_TEMPLATE = PARAM_KIND_TO_PEP_CODE_LOCALIZE.get(  # type: ignore
        arg_meta.kind, None)

    # If this kind of parameter is unsupported, raise an exception.
    #
    # Note this edge case should *NEVER* occur, as the parent function should
    # have simply ignored this parameter.
    if PARAM_LOCALIZE_TEMPLATE is None:
        raise BeartypeDecorHintPepException(
            f'{EXCEPTION_PREFIX}kind {repr(arg_meta.kind)} '
            f'currently unsupported by @beartype.'
        )
    # Else, this kind of parameter is supported. Ergo, this code is non-"None".

    # Generate a memoized parameter-agnostic code snippet type-checking any
    # parameter or return value with an arbitrary name.
    (
        code_param_check_pith,
        func_wrapper_locals,
        hint_forwardrefs_class_basename,
    ) = pep_code_check_hint(hint)

    # Merge the local scope required to type-check this parameter into the
    # local scope currently required by the current wrapper function.
    update_mapping(bear_call.func_wrapper_locals, func_wrapper_locals)

    # Python code snippet localizing this parameter.
    code_param_localize = PARAM_LOCALIZE_TEMPLATE.format(
        arg_name=arg_meta.name, arg_index=arg_meta.index)

    # Unmemoize this snippet against the current parameter.
    code_param_check = _unmemoize_pep_code(
        bear_call=bear_call,
        func_wrapper_code=code_param_check_pith,
        pith_repr=repr(arg_meta.name),
        hint_forwardrefs_class_basename=hint_forwardrefs_class_basename,
    )

    # Return a Python code snippet localizing and type-checking this parameter.
    return f'{code_param_localize}{code_param_check}'


def pep_code_check_return(bear_call: BeartypeCall, hint: object) -> str:
    '''
    Generate a Python code type-checking the return value annotated by a
    **PEP-compliant type hint** (e.g., :mod:`beartype`-agnostic annotation
    compliant with annotation-centric PEPs) of the decorated callable.

    Parameters
    ----------
    bear_call : BeartypeCall
        Decorated callable to be type-checked.
    hint : object
        PEP-compliant type hint annotating this return.

    Returns
    ----------
    str
        Code type-checking this return.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_if_hint_pep_unsupported()
    # function). By design, the caller already guarantees this to be the case.
    assert bear_call.__class__ is BeartypeCall, (
        f'{repr(bear_call)} not @beartype call.')

    # Empty tuple, passed below to satisfy the _unmemoize_pep_code() API.
    hint_forwardrefs_class_basename = ()

    # Generate a memoized parameter-agnostic code snippet type-checking any
    # parameter or return value with an arbitrary name.
    (
        code_return_check_pith,
        func_wrapper_locals,
        hint_forwardrefs_class_basename,
    ) = pep_code_check_hint(hint)

    # Merge the local scope required to type-check this return into the
    # local scope currently required by the current wrapper function.
    update_mapping(bear_call.func_wrapper_locals, func_wrapper_locals)

    # Unmemoize this snippet against this return.
    code_return_check_pith_unmemoized = _unmemoize_pep_code(
        bear_call=bear_call,
        func_wrapper_code=code_return_check_pith,
        pith_repr=_RETURN_REPR,
        hint_forwardrefs_class_basename=hint_forwardrefs_class_basename,
    )

    # Python code snippet type-checking this return.
    code_return_check_prefix = PEP_CODE_CHECK_RETURN_PREFIX.format(
        func_call_prefix=bear_call.func_wrapper_code_call_prefix)

    # Return a Python code snippet:
    # * Calling the decorated callable and localize its return *AND*...
    # * Type-checking this return *AND*...
    # * Returning this return from this wrapper function.
    return (
        f'{code_return_check_prefix}'
        f'{code_return_check_pith_unmemoized}'
        f'{PEP_CODE_CHECK_RETURN_SUFFIX}'
    )

# ....................{ PRIVATE ~ unmemoize               }....................
def _unmemoize_pep_code(
    bear_call: BeartypeCall,
    func_wrapper_code: str,
    pith_repr: str,
    hint_forwardrefs_class_basename: tuple,
) -> str:
    '''
    Convert the passed memoized code snippet type-checking any parameter or
    return of the decorated callable into a memoized code snippet type-checking
    a specific parameter or return of that callable.

    Specifically, this function (in order):

    #. Globally replaces all references to the
       :data:`PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER` placeholder substring
       cached into this code with the passed ``pith_repr`` parameter.
    #. Unmemoizes this code by globally replacing all relative forward
       reference placeholder substrings cached into this code with Python
       expressions evaluating to the classes referred to by those substrings
       relative to that callable when accessed via the private
       ``__beartypistry`` parameter.

    Parameters
    ----------
    bear_call : BeartypeCall
        Decorated callable to be type-checked.
    func_wrapper_code : str
        Memoized callable-agnostic code snippet type-checking any parameter or
        return of the decorated callable.
    pith_repr : str
        Machine-readable representation of the name of this parameter or
        return.
    hint_forwardrefs_class_basename : tuple
        Tuple of the unqualified classnames referred to by all relative forward
        reference type hints visitable from the current root type hint.

    Returns
    ----------
    str
        This memoized code unmemoized by globally resolving all relative
        forward reference placeholder substrings cached into this code relative
        to the currently decorated callable.
    '''
    assert bear_call.__class__ is BeartypeCall, (
        f'{repr(bear_call)} not @beartype call.')
    assert isinstance(func_wrapper_code, str), (
        f'{repr(func_wrapper_code)} not string.')
    assert isinstance(pith_repr, str), f'{repr(pith_repr)} not string.'
    assert isinstance(hint_forwardrefs_class_basename, Iterable), (
        f'{repr(hint_forwardrefs_class_basename)} not iterable.')

    # Generate an unmemoized parameter-specific code snippet type-checking this
    # parameter by replacing in this parameter-agnostic code snippet...
    func_wrapper_code = replace_str_substrs(
        text=func_wrapper_code,
        # This placeholder substring cached into this code with...
        old=PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER,
        # This object representation of the name of this parameter or return.
        new=pith_repr,
    )

    # If this code contains one or more relative forward reference placeholder
    # substrings memoized into this code, unmemoize this code by globally
    # resolving these placeholders relative to the decorated callable.
    if hint_forwardrefs_class_basename:
        # Callable currently being decorated by @beartype.
        func = bear_call.func_wrappee

        # Pass the beartypistry singleton as a private "__beartypistry"
        # parameter to this wrapper function.
        bear_call.func_wrapper_locals[ARG_NAME_TYPISTRY] = bear_typistry

        # For each unqualified classname referred to by a relative forward
        # reference type hints visitable from the current root type hint...
        for hint_forwardref_class_basename in hint_forwardrefs_class_basename:
            # Generate an unmemoized callable-specific code snippet
            # type-checking this class by globally replacing in this
            # callable-agnostic code...
            func_wrapper_code = replace_str_substrs(
                text=func_wrapper_code,
                # This placeholder substring cached into this code with...
                old=(
                    f'{PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX}'
                    f'{hint_forwardref_class_basename}'
                    f'{PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX}'
                ),
                # Python expression evaluating to this class when accessed
                # via the private "__beartypistry" parameter.
                new=register_typistry_forwardref(
                    # Fully-qualified classname referred to by this forward
                    # reference relative to the decorated callable.
                    get_hint_pep484585_forwardref_classname_relative_to_object(
                        hint=hint_forwardref_class_basename, obj=func,)),
            )

    # Return this unmemoized callable-specific code snippet.
    return func_wrapper_code
