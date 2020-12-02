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
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPep484Exception,
)
from beartype._decor._code._pep._pepsnip import (
    PARAM_KIND_TO_PEP_CODE_GET,
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
from beartype._decor._typistry import register_typistry_forwardref
from beartype._util.cache.utilcacheerror import reraise_exception_cached
from beartype._util.hint.utilhintget import (
    get_hint_forwardref_classname_relative_to_obj,
)
from beartype._util.hint.utilhinttest import die_unless_hint
from beartype._util.text.utiltextlabel import (
    label_callable_decorated_param,
    label_callable_decorated_return,
)
from collections.abc import Callable, Iterable
from inspect import Parameter
from typing import NoReturn, Union

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_RETURN_REPR = repr('return')
'''
Object representation of the magic string implying a return value in various
Python objects (e.g., the ``__annotations__`` dunder dictionary of annotated
callables).
'''

# ....................{ COERCERS                          }....................
def coerce_hint_pep(
    func: Callable,
    pith_name: str,
    hint: object,
    hint_label: str,
) -> object:
    '''
    Coerce the passed type hint annotating the parameter or return with the
    passed name of the passed callable into the corresponding PEP-compliant
    type hint if needed.

    Specifically, this function:

    * If this hint is a **PEP-noncompliant tuple union** (i.e., tuple of one or
      more standard classes and forward references to standard classes):

      * Coerces this tuple union into the equivalent `PEP 484`_-compliant
        union.
      * Replaces this tuple union in the ``__annotations__`` dunder tuple of
        this callable with this `PEP 484`_-compliant union.
      * Returns this `PEP 484`_-compliant union.

    * Else if this hint is already PEP-compliant, preserves and returns this
      hint unmodified as is.
    * Else (i.e., if this hint is neither PEP-compliant nor -noncompliant and
      thus invalid as a type hint), raise an exception.

    This getter is *not* memoized, due to being only called once per decorated
    callable parameter or return value.

    Parameters
    ----------
    func : Callable
        Callable
    pith_name : str
        Either:

        * If this hint annotates a parameter, the name of that parameter.
        * If this hint annotates the return, ``"return"``.
    hint : object
        Type hint to be rendered PEP-compliant.
    hint_label : str
        Human-readable label describing this hint.

    Returns
    ----------
    object
        Either:

        * If this hint is PEP-noncompliant, PEP-compliant type hint converted
          from this hint.
        * If this hint is PEP-compliant, hint unmodified as is.

    Raises
    ----------
    BeartypeDecorHintNonPepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # If this hint is a PEP-noncompliant tuple union, coerce this union into
    # the equivalent PEP-compliant union subscripted by the same child hints.
    # By definition, PEP-compliant unions are a strict superset of
    # PEP-noncompliant tuple unions and thus accept all child hints accepted by
    # the latter.
    if isinstance(hint, tuple):
        assert callable(func), f'{repr(func)} not callable.'
        assert isinstance(pith_name, str), f'{pith_name} not string.'

        hint = func.__annotations__[pith_name] = Union.__getitem__(hint)
    # Else, this hint is *NOT* a PEP-noncompliant tuple union.

    # If this object is neither a PEP-noncompliant type hint *NOR* supported
    # PEP-compliant type hint, raise an exception.
    die_unless_hint(hint=hint, hint_label=hint_label)
    # Else, this object is either a PEP-noncompliant type hint *OR* supported
    # PEP-compliant type hint.

    # Return this hint.
    return hint

# ....................{ CODERS                            }....................
def pep_code_check_param(
    data: BeartypeData,
    hint: object,
    param: Parameter,
    param_index: int,
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
    hint : object
        PEP-compliant type hint annotating this parameter.
    param : Parameter
        :mod:`inspect`-specific object describing this parameter.
    param_index : int
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
    assert isinstance(param, Parameter), (
        f'{repr(param)} not parameter metadata.')
    assert isinstance(param_index, int), (
        f'{repr(param_index)} not integer.')

    # Python code template localizing this parameter if this kind of parameter
    # is supported *OR* "None" otherwise.
    get_arg_code_template = PARAM_KIND_TO_PEP_CODE_GET.get(
        param.kind, None)

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
            func=data.func, param_name=param.name)

        # Raise an exception embedding this label.
        raise BeartypeDecorHintPepException(
            f'{hint_label} kind {repr(param.kind)} unsupported.')
    # Else, this kind of parameter is supported. Ergo, this code is non-"None".

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

    # Attempt to...
    try:
        # Generate memoized parameter-agnostic Python code type-checking a
        # parameter or return value with an arbitrary name.
        (
            func_code,
            is_func_code_needs_random_int,
            hints_forwardref_class_basename,
        ) = pep_code_check_hint(hint)

        # Generate unmemoized parameter-specific Python code type-checking this
        # exact parameter by globally replacing in this parameter-agnostic
        # code...
        func_code = func_code.replace(
            # This placeholder substring cached into this code with...
            PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER,
            # This object representation of this parameter's name.
            repr(param.name),
        )

        # If this code contains one or more relative forward reference
        # placeholder substrings memoized into this code, unmemoize this code
        # by globally resolving these placeholders relative to the currently
        # decorated callable.
        if hints_forwardref_class_basename:
            func_code = resolve_pep_code_hints_forwardref_class_basename(
                data=data,
                func_code=func_code,
                hints_forwardref_class_basename=(
                    hints_forwardref_class_basename),
            )
    # If the prior call to the memoized _pep_code_check() function raises a
    # cached exception...
    except Exception as exception:
        # Human-readable label describing this parameter.
        hint_label = label_callable_decorated_param(
            func=data.func, param_name=param.name) + ' PEP type hint'

        # Reraise this cached exception's memoized parameter-agnostic message
        # into an unmemoized parameter-specific message.
        reraise_exception_cached(exception=exception, target_str=hint_label)

    # Return all metadata required by higher-level callers, including...
    return (
        # Python code to....
        (
            # Localize this parameter *AND*...
            get_arg_code_template.format(
                arg_name=param.name, arg_index=param_index) +
            # Type-check this parameter.
            func_code
        ),
        # Boolean true only if type-checking this parameter requires first
        # localizing a pseudo-random integer.
        is_func_code_needs_random_int,
    )


def pep_code_check_return(
    data: BeartypeData,
    hint: object,
) -> 'Tuple[str, bool]':
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
    func_code = None

    # True only if type-checking for this return value requires a higher-level
    # caller to prefix the body of this wrapper function with code generating
    # and localizing a pseudo-random integer.
    is_func_code_needs_random_int = False

    # If this is the PEP 484-compliant "typing.NoReturn" type hint permitted
    # *ONLY* as a return annotation, prefer pregenerated code type-checking
    # this peculiar type hint against this hint.
    if hint is NoReturn:
        func_code = PEP484_CODE_CHECK_NORETURN
    # Else, this is a standard PEP-compliant type hint. In this case...
    else:
        # Attempt to generate memoized parameter-agnostic Python code
        # type-checking a parameter or return value with an arbitrary name.
        try:
            (
                func_code,
                is_func_code_needs_random_int,
                hints_forwardref_class_basename,
            ) = pep_code_check_hint(hint)

            # If this code contains one or more relative forward reference
            # placeholder substrings memoized into this code, unmemoize this
            # code by globally resolving these placeholders relative to the
            # currently decorated callable.
            if hints_forwardref_class_basename:
                func_code = resolve_pep_code_hints_forwardref_class_basename(
                    data=data,
                    func_code=func_code,
                    hints_forwardref_class_basename=(
                        hints_forwardref_class_basename),
                )

            # Python code to:
            # * Call the decorated callable and localize its return value
            #   *AND*...
            # * Type-check this return value *AND*...
            # * Return this value from this wrapper function.
            func_code = (
                f'{PEP_CODE_CHECK_RETURN_PREFIX}{func_code}'
                f'{PEP_CODE_CHECK_RETURN_SUFFIX}'
            )
        # If the prior call to the memoized _pep_code_check() function raises a
        # cached exception...
        except Exception as exception:
            # Human-readable label describing this return.
            hint_label = (
                f'{label_callable_decorated_return(data.func)} PEP type hint')

            # Reraise this cached exception's memoized return value-agnostic
            # message into an unmemoized return value-specific message.
            reraise_exception_cached(
                exception=exception, target_str=hint_label)

    # Return all metadata required by higher-level callers, including...
    return (
        # Generate unmemoized parameter-specific Python code type-checking this
        # exact return value by globally replacing in this return-agnostic
        # code...
        func_code.replace(
            # This placeholder substring cached into this code with...
            PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER,
            # This object representation of this return value,
            _RETURN_REPR,
        ),
        # Boolean true only if type-checking this return value requires first
        # localizing a pseudo-random integer.
        is_func_code_needs_random_int,
    )

# ....................{ CODERS                            }....................
def resolve_pep_code_hints_forwardref_class_basename(
    data: BeartypeData,
    func_code: str,
    hints_forwardref_class_basename: tuple,
) -> str:
    '''
    Passed memoized Python code type-checking a parameter or return value of
    the currently decorated callable unmemoized by globally replacing all
    relative forward reference placeholder substrings cached into this code
    with Python expressions evaluating to the classes referred to by these
    substrings relative to that callable when accessed via the private
    ``__beartypistry`` parameter.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.
    func_code : str
        Memoized Python code type-checking a parameter or return value of
        the currently decorated callable.
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
    assert isinstance(func_code, str), f'{repr(func_code)} not string.'
    assert isinstance(hints_forwardref_class_basename, Iterable), (
        f'{repr(hints_forwardref_class_basename)} not iterable.')

    # For each unqualified classname referred to by a relative forward
    # reference type hints visitable from the current root type hint...
    for hint_forwardref_class_basename in hints_forwardref_class_basename:
        # Generate unmemoized callable-specific Python code type-checking this
        # class by globally replacing in this callable-agnostic code...
        func_code = func_code.replace(
            # This placeholder substring cached into this code with...
            (
                f'{PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX}'
                f'{hint_forwardref_class_basename}'
                f'{PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX}'
            ),
            # Python expression evaluating to this class when accessed
            # via the private "__beartypistry" parameter.
            register_typistry_forwardref(
                # Fully-qualified classname referred to by this forward
                # reference relative to the decorated callable.
                get_hint_forwardref_classname_relative_to_obj(
                    obj=data.func,
                    hint=hint_forwardref_class_basename,
                )
            )
        )

    # Return this unmemoized callable-specific Python code.
    return func_code
