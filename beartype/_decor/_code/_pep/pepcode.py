#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
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
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPep484Exception,
)
from beartype._decor._code._pep._pepsnip import (
    PARAM_KIND_TO_PEP_CODE_LOCALIZE,
    PEP_CODE_CHECK_RETURN_PREFIX,
    PEP_CODE_CHECK_RETURN_SUFFIX,
    PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX,
    PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX,
    PEP484_CODE_CHECK_NORETURN,
)
from beartype._decor._code._pep._pephint import pep_code_check_hint
from beartype._decor._code._pep._pepsnip import (
    PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER)
from beartype._decor._data import BeartypeData
from beartype._decor._cache.cachetype import register_typistry_forwardref
from beartype._util.cache.utilcacheerror import reraise_exception_cached
from beartype._util.func.utilfuncscope import CallableScope
from beartype._util.hint.utilhintget import (
    get_hint_forwardref_classname_relative_to_obj,
)
from beartype._util.text.utiltextlabel import (
    label_callable_decorated_param,
    label_callable_decorated_return,
)
from beartype._util.text.utiltextmunge import replace_str_substrs
from collections.abc import Iterable
from inspect import Parameter
from typing import NoReturn, Tuple

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_RETURN_REPR = repr('return')
'''
Object representation of the magic string implying a return value in various
Python objects (e.g., the ``__annotations__`` dunder dictionary of annotated
callables).
'''

# ....................{ HINTS                             }....................
FuncWrapperData = Tuple[str, CallableScope]
'''
PEP-compliant type hint matching **function wrapper data.**

Specifically, this hint matches 2-tuples
``(func_wrapper_code, func_wrapper_locals)`` where:

* ``func_wrapper_code`` is either:

    * If the decorated callable requires *no* type-checking (e.g., due to all
      type hints annotating this callable being ignorable), the empty string.
      Note this edge case is distinct from a related edge case at the head of
      the :func:`beartype.beartype` decorator reducing to a noop for
      unannotated callables. By compare, this boolean is ``True`` only for
      callables annotated with **ignorable type hints** (i.e., :class:`object`,
      :class:`beartype.cave.AnyType`, :class:`typing.Any`): e.g.,

      .. _code-block:: python

          >>> from beartype.cave import AnyType
          >>> from typing import Any
          >>> def muh_func(muh_param1: AnyType, muh_param2: object) -> Any: pass
          >>> muh_func is beartype(muh_func)
          True

      * Else, a code snippet defining the wrapper function type-checking the
        decorated callable, including (in order):

        * A signature declaring this wrapper, accepting both beartype-agnostic
          and -specific parameters. The latter include:

          * A private ``__beartype_func`` parameter initialized to the
            decorated callable. In theory, this callable should be accessible
            as a closure-style local in this wrapper. For unknown reasons
            (presumably, a subtle bug in the exec() builtin), this is *not* the
            case. Instead, a closure-style local must be simulated by passing
            this callable at function definition time as the default value of
            an arbitrary parameter. To ensure this default is *not* overwritten
            by a function accepting a parameter of the same name, this unlikely
            edge case is guarded against elsewhere.

        * Statements type checking parameters passed to the decorated callable.
        * A call to the decorated callable.
        * A statement type checking the value returned by the decorated
          callable.

* ``func_wrapper_locals`` is the **local scope** (i.e., dictionary mapping from
  the name to value of each attribute referenced in the signature) of this
  wrapper function required by this code snippet.
'''

# ....................{ CODERS                            }....................
def pep_code_check_param(
    data: BeartypeData,
    hint: object,
    param: Parameter,
    param_index: int,
) -> FuncWrapperData:
    '''
    Python code type-checking the parameter with the passed signature and index
    annotated by a **PEP-compliant type hint** (e.g., :mod:`beartype`-agnostic
    annotation compliant with annotation-centric PEPs) of the decorated
    callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.
    hint : object
        PEP-compliant type hint annotating this parameter.
    param : Parameter
        :mod:`inspect`-specific object describing this parameter.
    param_index : int
        0-based index of this parameter in this callable's signature.

    Returns
    ----------
    FuncWrapperData
        Generated function wrapper data. See :data:`FuncWrapperData`.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_if_hint_pep_unsupported()
    # function). By design, the caller already guarantees this to be the case.
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'
    assert isinstance(param, Parameter), (
        f'{repr(param)} not parameter metadata.')
    assert isinstance(param_index, int), (
        f'{repr(param_index)} not integer.')

    # If this is the PEP 484-compliant "typing.NoReturn" type hint permitted
    # *ONLY* as a return annotation...
    if hint is NoReturn:
        # Human-readable label describing this parameter.
        hint_label = label_callable_decorated_param(
            func=data.func, param_name=param.name)

        # Raise an exception embedding this label.
        raise BeartypeDecorHintPep484Exception(
            f'{hint_label} PEP return hint '
            f'{repr(hint)} invalid as parameter annotation.'
        )
    # Else, this is a standard PEP-compliant type hint.

    # Python code template localizing this parameter if this kind of parameter
    # is supported *OR* "None" otherwise.
    PARAM_LOCALIZE_TEMPLATE = PARAM_KIND_TO_PEP_CODE_LOCALIZE.get(
        param.kind, None)

    # If this kind of parameter is unsupported...
    #
    # Note this edge case should *NEVER* occur, as the parent function should
    # have simply ignored this parameter.
    if PARAM_LOCALIZE_TEMPLATE is None:
        #FIXME: Generalize this label to embed the kind of parameter as well
        #(e.g., "positional-only", "keyword-only", "variadic positional"),
        #probably by defining a new label_callable_decorated_param_kind().

        # Human-readable label describing this parameter.
        hint_label = label_callable_decorated_param(
            func=data.func, param_name=param.name)

        # Raise an exception embedding this label.
        raise BeartypeDecorHintPepException(
            f'{hint_label} kind {repr(param.kind)} unsupported.')
    # Else, this kind of parameter is supported. Ergo, this code is non-"None".

    # Python code snippet localizing this parameter.
    func_wrapper_code_param_localize = PARAM_LOCALIZE_TEMPLATE.format(
        arg_name=param.name, arg_index=param_index)

    # Attempt to...
    try:
        # Generate a memoized parameter-agnostic code snippet type-checking any
        # parameter or return value with an arbitrary name.
        (
            func_wrapper_code,
            func_wrapper_locals,
            hints_forwardref_class_basename,
        ) = pep_code_check_hint(hint)

        # Unmemoize this snippet against the current parameter.
        func_wrapper_code = _unmemoize_pep_code(
            data=data,
            func_wrapper_code=func_wrapper_code,
            pith_repr=repr(param.name),
            hints_forwardref_class_basename=hints_forwardref_class_basename,
        )
    # If the prior call to the memoized pep_code_check_hint() function raised a
    # cached exception...
    except Exception as exception:
        # Human-readable label describing this parameter.
        hint_label = label_callable_decorated_param(
            func=data.func, param_name=param.name)

        # Reraise this cached exception's memoized parameter-agnostic message
        # into an unmemoized parameter-specific message.
        reraise_exception_cached(
            exception=exception, target_str=f'{hint_label} PEP type hint')

    # Return all metadata required by higher-level callers, including...
    return (
        # Python code snippet localizing and type-checking this parameter.
        f'{func_wrapper_code_param_localize}{func_wrapper_code}',
        func_wrapper_locals,
    )


def pep_code_check_return(data: BeartypeData, hint: object) -> FuncWrapperData:
    '''
    Python code type-checking the return value annotated with a **PEP-compliant
    type hint** (e.g., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs) of the decorated callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.
    hint : object
        PEP-compliant type hint annotating this return.

    Returns
    ----------
    FuncWrapperData
        Generated function wrapper data. See :data:`FuncWrapperData`.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_if_hint_pep_unsupported()
    # function). By design, the caller already guarantees this to be the case.
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'

    # Memoized parameter-agnostic code snippet type-checking any parameter or
    # return with an arbitrary name.
    func_wrapper_code: str = None  # type: ignore[assignment]

    # Local scope of this wrapper function required by this code snippet.
    func_wrapper_locals: CallableScope = {}

    # If this is the PEP 484-compliant "typing.NoReturn" type hint permitted
    # *ONLY* as a return annotation...
    if hint is NoReturn:
        # Default this snippet to a pre-generated snippet validating this
        # callable to *NEVER* successfully return. Yes, this is absurd.
        func_wrapper_code = PEP484_CODE_CHECK_NORETURN

        # Empty tuple, passed below to satisfy the _unmemoize_pep_code() API.
        hints_forwardref_class_basename = ()
    # Else, this is a standard PEP-compliant type hint. In this case...
    else:
        # Attempt to...
        try:
            # Generate a memoized parameter-agnostic code snippet type-checking
            # any parameter or return value with an arbitrary name.
            (
                func_wrapper_code,
                func_wrapper_locals,
                hints_forwardref_class_basename,
            ) = pep_code_check_hint(hint)

            # Extend this snippet to:
            # * Call the decorated callable and localize its return *AND*...
            # * Type-check this return *AND*...
            # * Return this return from this wrapper function.
            func_wrapper_code = (
                f'{PEP_CODE_CHECK_RETURN_PREFIX}{func_wrapper_code}'
                f'{PEP_CODE_CHECK_RETURN_SUFFIX}'
            )
        # If the prior call to the memoized pep_code_check_hint() function
        # raised a cached exception...
        except Exception as exception:
            # Human-readable label describing this return.
            hint_label = (
                f'{label_callable_decorated_return(data.func)} PEP type hint')

            # Reraise this cached exception's memoized return value-agnostic
            # message into an unmemoized return value-specific message.
            reraise_exception_cached(
                exception=exception, target_str=hint_label)

    # Unmemoize this snippet against this return.
    func_wrapper_code = _unmemoize_pep_code(
        data=data,
        func_wrapper_code=func_wrapper_code,
        pith_repr=_RETURN_REPR,
        hints_forwardref_class_basename=(
            hints_forwardref_class_basename),
    )

    # Return all metadata required by higher-level callers.
    return (func_wrapper_code, func_wrapper_locals)

# ....................{ PRIVATE ~ unmemoize               }....................
def _unmemoize_pep_code(
    data: BeartypeData,
    func_wrapper_code: str,
    pith_repr: str,
    hints_forwardref_class_basename: tuple,
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
    data : BeartypeData
        Decorated callable to be type-checked.
    func_wrapper_code : str
        Memoized callable-agnostic code snippet type-checking any parameter or
        return of the decorated callable.
    pith_repr : str
        Machine-readable representation of the name of this parameter or
        return.
    hints_forwardref_class_basename : tuple
        Tuple of the unqualified classnames referred to by all relative forward
        reference type hints visitable from the current root type hint.

    Returns
    ----------
    str
        This memoized code unmemoized by globally resolving all relative
        forward reference placeholder substrings cached into this code relative
        to the currently decorated callable.
    '''
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'
    assert isinstance(func_wrapper_code, str), (
        f'{repr(func_wrapper_code)} not string.')
    assert isinstance(pith_repr, str), f'{repr(pith_repr)} not string.'
    assert isinstance(hints_forwardref_class_basename, Iterable), (
        f'{repr(hints_forwardref_class_basename)} not iterable.')

    # Generate an unmemoized parameter-specific code snippet type-checking
    # this parameter by globally replacing in this parameter-agnostic
    # code snippet...
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
    if hints_forwardref_class_basename:
        # For each unqualified classname referred to by a relative forward
        # reference type hints visitable from the current root type hint...
        for hint_forwardref_class_basename in hints_forwardref_class_basename:
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
                    get_hint_forwardref_classname_relative_to_obj(
                        obj=data.func,
                        hint=hint_forwardref_class_basename,
                    )
                )
            )

    # Return this unmemoized callable-specific code snippet.
    return func_wrapper_code
