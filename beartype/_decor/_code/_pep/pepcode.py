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

# ....................{ TODO                              }....................
#FIXME: Resolve PEP-compliant forward references as well. Note that doing so is
#highly non-trivial -- sufficiently so, in fact, that we probably want to do so
#as cleverly documented in the "_pep563" submodule.

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPep484Exception,
)
from beartype._decor._code._pep._pepsnip import (
    PARAM_KIND_TO_PEP_CODE_GET,
    PEP_CODE_CHECK_RETURN_PREFIX,
    PEP_CODE_CHECK_RETURN_SUFFIX,
    PEP484_CODE_CHECK_NORETURN,
)
from beartype._decor._code._pep._pephint import pep_code_check_hint
from beartype._decor._code._pep._pepsnip import (
    PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER)
from beartype._decor._data import BeartypeData
from beartype._util.cache.utilcacheerror import reraise_exception_cached
from beartype._util.text.utiltextlabel import (
    label_callable_decorated_param,
    label_callable_decorated_return,
)
from inspect import Parameter
from typing import NoReturn

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_RETURN_REPR = repr('return')
'''
Object representation of the magic string implying a return value in various
Python objects (e.g., the ``__annotations__`` dunder dictionary of annotated
callables).
'''

# ....................{ CODERS                            }....................
def pep_code_check_param(
    data: BeartypeData,
    func_arg: Parameter,
    func_arg_index: int,
) -> 'Tuple[str, bool]':
    '''
    Python code type-checking the parameter with the passed signature and index
    annotated by a **PEP-compliant type hint** (e.g., :mod:`beartype`-agnostic
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
    Tuple[str, bool]
        2-tuple ``(func_code, is_func_code_needs_random_int)``, where:

        * ``func_code`` is Python code type-checking this parameter against
          this hint.
        * ``is_func_code_needs_random_int`` is a boolean that is ``True`` only
          if type-checking for this parameter requires a higher-level caller to
          prefix the body of this wrapper function with code generating and
          localizing a pseudo-random integer.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_if_hint_pep_unsupported()
    # function). By design, the caller already guarantees this to be the case.
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'
    assert isinstance(func_arg, Parameter), (
        f'{repr(func_arg)} not parameter metadata.')
    assert func_arg_index.__class__ is int, (
        f'{repr(func_arg_index)} not parameter index.')

    # Python code template localizing this parameter if this kind of parameter
    # is supported *OR* "None" otherwise.
    get_arg_code_template = PARAM_KIND_TO_PEP_CODE_GET.get(func_arg.kind, None)

    # If this kind of parameter is unsupported...
    #
    # Note this edge case should *NEVER* occur, as the parent function should
    # have simply ignored this parameter.
    if get_arg_code_template is None:
        #FIXME: Generalize this label to embed the kind of parameter as well
        #(e.g., "positional-only", "keyword-only", "variadic positional"),
        #probably by defining a new label_callable_decorated_param_kind().

        # Human-readable label describing this parameter.
        hint_label = label_callable_decorated_param(
            func=data.func, param_name=func_arg.name)

        # Raise an exception embedding this label.
        raise BeartypeDecorHintPepException(
            f'{hint_label} kind {repr(func_arg.kind)} unsupported.')
    # Else, this kind of parameter is supported. Ergo, this code is non-"None".

    # PEP-compliant type hint annotating this parameter.
    param_hint = func_arg.annotation

    # If this is the PEP 484-compliant "typing.NoReturn" type hint permitted
    # *ONLY* as a return annotation...
    if param_hint is NoReturn:
        # Human-readable label describing this parameter.
        hint_label = label_callable_decorated_param(
            func=data.func, param_name=func_arg.name)

        # Raise an exception embedding this label.
        raise BeartypeDecorHintPep484Exception(
            f'{hint_label} PEP return hint '
            f'{repr(param_hint)} invalid as parameter annotation.'
        )
    # Else, this is a standard PEP-compliant type hint.

    # Attempt to...
    try:
        # Generate memoized parameter-agnostic Python code type-checking a
        # parameter or return value with an arbitrary name.
        (
            param_code_check,
            is_func_code_needs_random_int,

            #FIXME: Actually use this, please. To minimize DRY with the
            #function below, we probably want to define a new private helper of
            #this submodule to do so.
            hint_forwardrefs_unqualified,
        ) = pep_code_check_hint(param_hint)

        # Generate unmemoized parameter-specific Python code type-checking this
        # exact parameter by globally replacing in this parameter-agnostic
        # code...
        param_code_check = param_code_check.replace(
            # This placeholder substring cached into this code with...
            PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER,
            # This object representation of this parameter's name.
            repr(func_arg.name),
        )
    # If the prior call to the memoized _pep_code_check() function raises a
    # cached exception...
    except Exception as exception:
        # Human-readable label describing this parameter.
        hint_label = label_callable_decorated_param(
            func=data.func, param_name=func_arg.name) + ' PEP hint'

        # Reraise this cached exception's memoized parameter-agnostic message
        # into an unmemoized parameter-specific message.
        reraise_exception_cached(exception=exception, target_str=hint_label)

    # Return all metadata required by higher-level callers, including...
    return (
        # Python code to....
        (
            # Localize this parameter *AND*...
            get_arg_code_template.format(
                arg_name=func_arg.name, arg_index=func_arg_index) +
            # Type-check this parameter.
            param_code_check
        ),
        # Boolean true only if type-checking this parameter requires first
        # localizing a pseudo-random integer.
        is_func_code_needs_random_int,
    )


def pep_code_check_return(data: BeartypeData) -> 'Tuple[str, bool]':
    '''
    Python code type-checking the return value annotated with a **PEP-compliant
    type hint** (e.g., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs) of the decorated callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    Tuple[str, bool]
        2-tuple ``(func_code, is_func_code_needs_random_int)``, where:

        * ``func_code`` is Python code type-checking this return value against
          this hint.
        * ``is_func_code_needs_random_int`` is a boolean that is ``True`` only
          if type-checking for this return value requires a higher-level caller
          to prefix the body of this wrapper function with code generating and
          localizing a pseudo-random integer.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_if_hint_pep_unsupported()
    # function). By design, the caller already guarantees this to be the case.
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'

    # Memoized parameter-agnostic Python code type-checking either a parameter
    # or return value with an arbitrary name.
    return_code_check = None

    # True only if type-checking for this return value requires a higher-level
    # caller to prefix the body of this wrapper function with code generating
    # and localizing a pseudo-random integer.
    is_func_code_needs_random_int = False

    # PEP-compliant type hint annotating this parameter.
    param_hint = data.func_sig.return_annotation

    # If this is the PEP 484-compliant "typing.NoReturn" type hint permitted
    # *ONLY* as a return annotation, prefer pregenerated code type-checking
    # this peculiar type hint against this hint.
    if param_hint is NoReturn:
        return_code_check = PEP484_CODE_CHECK_NORETURN
    # Else, this is a standard PEP-compliant type hint. In this case...
    else:
        # Attempt to generate memoized parameter-agnostic Python code
        # type-checking a parameter or return value with an arbitrary name.
        try:
            (
                return_code_check,
                is_func_code_needs_random_int,

                #FIXME: Actually use this, please. To minimize DRY with the
                #function below, we probably want to define a new private
                #helper of this submodule to do so.
                hint_forwardrefs_unqualified,
            ) = pep_code_check_hint(param_hint)

            # Python code to:
            # * Call the decorated callable and localize its return value
            #   *AND*...
            # * Type-check this return value *AND*...
            # * Return this value from this wrapper function.
            return_code_check = (
                f'{PEP_CODE_CHECK_RETURN_PREFIX}{return_code_check}'
                f'{PEP_CODE_CHECK_RETURN_SUFFIX}'
            )
        # If the prior call to the memoized _pep_code_check() function raises a
        # cached exception...
        except Exception as exception:
            # Human-readable label describing this return.
            hint_label = (
                f'{label_callable_decorated_return(data.func)} PEP hint')

            # Reraise this cached exception's memoized return value-agnostic
            # message into an unmemoized return value-specific message.
            reraise_exception_cached(
                exception=exception, target_str=hint_label)

    # Return all metadata required by higher-level callers, including...
    return (
        # Generate unmemoized parameter-specific Python code type-checking this
        # exact return value by globally replacing in this return-agnostic code...
        return_code_check.replace(
            # This placeholder substring cached into this code with...
            PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER,
            # This object representation of this return value,
            _RETURN_REPR,
        ),
        # Boolean true only if type-checking this return value requires first
        # localizing a pseudo-random integer.
        is_func_code_needs_random_int,
    )
