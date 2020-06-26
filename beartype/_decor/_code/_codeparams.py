#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator annotation introspection.**

This private submodule introspects the annotations of callables to be decorated
by the :func:`beartype.beartype` decorator in a general-purpose manner. For
genericity, this relatively high-level submodule implements *no* support for
annotation-based PEPs (e.g., `PEP 484`_, `PEP 563`_); other lower-level
submodules in this subpackage do so instead.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorParamNameException
from beartype._decor._code import _codehint
from beartype._decor._code._codehint import HINTS_IGNORABLE
from beartype._decor._code._snippet import (
    CODE_PARAM_VARIADIC_POSITIONAL,
    CODE_PARAM_KEYWORD_ONLY,
    CODE_PARAM_POSITIONAL_OR_KEYWORD,
    CODE_PARAM_HINT,
)
from beartype._decor._data import BeartypeData
from inspect import Parameter, Signature

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_PARAM_HINTS_IGNORABLE = {Parameter.empty,} | HINTS_IGNORABLE
'''
Set of all parameter annotation types to be ignored during annotation-based
type checking in the :func:`beartype` decorator.

This includes:

* The :class:`Parameter.empty` type, denoting **unannotated parameters** (i.e.,
  parameters *not* annotated with a type hint).
* All context-agnostic types listed in the
  :attr:`beartype._decor.annotation.HINTS_IGNORABLE` set global constant.
'''


_PARAM_KINDS_IGNORABLE = {Parameter.POSITIONAL_ONLY, Parameter.VAR_KEYWORD}
'''
Set of all :attr:`Parameter.kind` constants to be ignored during
annotation-based type checking in the :func:`beartype` decorator.

This includes:

* Constants specific to variadic keyword parameters (e.g., ``**kwargs``), which
  are currently unsupported by :func:`beartype`.
* Constants specific to positional-only parameters, which apply only to
  non-pure-Python callables (e.g., defined by C extensions). The
  :func:`beartype` decorator applies *only* to pure-Python callables, which
  provide no syntactic means for specifying positional-only parameters.
'''

# ....................{ CODERS                            }....................
def code_check_params(data: BeartypeData) -> str:
    '''
    Python code snippet type-checking all annotated parameters declared by the
    the decorated callable if any *or* the empty string otherwise (i.e., if
    these parameters are unannotated).

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Python code snippet type-checking all annotated parameters declared by
        the decorated callable if any *or* the empty string otherwise.

    Raises
    ----------
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__beartype_``.
    BeartypeDecorHintTupleItemException
        If any item of any **type-hinted tuple** (i.e., tuple applied as a
        parameter or return value annotation) is of an unsupported type.
        Supported types include:

        * :class:`type` (i.e., classes).
        * :class:`str` (i.e., strings).
    '''
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))

    # Python code snippet to be returned.
    func_body = ''

    # For the name of each parameter accepted by this callable and the
    # "Parameter" instance encapsulating this parameter (in declaration
    # order)...
    for func_arg_index, func_arg in enumerate(
        data.func_sig.parameters.values()):
        # If this callable redefines a parameter initialized to a default value
        # by this wrapper, raise an exception. Permitting this unlikely edge
        # case would permit unsuspecting users to accidentally override these
        # defaults.
        if func_arg.name.startswith('__beartype_'):
            raise BeartypeDecorParamNameException(
                '{} parameter "{}" reserved by @beartype.'.format(
                    data.func_name, func_arg.name))

        # Annotation for this parameter if any *OR* "Parameter.empty" otherwise
        # (i.e., if this parameter is unannotated).
        func_arg_hint = func_arg.annotation

        # Attempt to...
        try:
            # If the type of either this parameter or annotation is silently
            # ignorable, continue to the next parameter.
            #
            # Note the "in" operator when applied to a set() object requires
            # that the first operand (i.e., "func_arg_hint" and
            # "func_arg_kind") to be hashable. Since:
            #
            # * "func_arg_kind" derives from the stdlib "inspect" module, this
            #   should *ALWAYS* be the case for that object.
            # * "func_arg_hint" is an arbitrary user-defined object, this is
            #   *NOT* necessarily the case for that object. However, since most
            #   annotations are types (including those generated by the stdlib
            #   "typing" module) *AND* since types are hashable, this is
            #   generally the case for that object. Nonetheless, exception
            #   handling is still warranted to catch edge cases.
            if (func_arg_hint in _PARAM_HINTS_IGNORABLE or
                func_arg.kind in _PARAM_KINDS_IGNORABLE):
                continue
        # If this annotation is unhashable and hence *NOT* a beartype-supported
        # type (e.g., class, string, tuple of classes and/or strings), the
        # above code raises a "TypeError".
        except TypeError as type_error:
            # If this exception does *NOT* denote unhashability, this exception
            # is unexpected. Raise this exception as is. Note that:
            #     >>> [] in {,}
            #     TypeError: unhashable type: 'list'
            if not str(type_error).startswith("unhashable type: '"):
                raise
            # Else, this exception denotes unhashability. In this case, simply
            # ignore this low-level non-human-readable exception. The
            # subsequent call to annotation._verify_hint() will raise a
            # high-level human-readable exception describing this failure.

        # Human-readable label describing this annotation.
        func_arg_hint_label = (
            '{} parameter "{}" type hint'.format(
                data.func_name, func_arg.name))

        # Validate this annotation.
        _codehint.verify_hint(
            hint=func_arg_hint, hint_label=func_arg_hint_label)

        # String evaluating to this parameter's annotated type.
        func_arg_type_expr = CODE_PARAM_HINT.format(func_arg.name)

        # String evaluating to this parameter's current value when passed
        # as a keyword.
        func_arg_value_key_expr = 'kwargs[{!r}]'.format(func_arg.name)

        # Replace all classnames in this annotation by the corresponding
        # classes.
        func_body += _codehint.code_resolve_forward_refs(
            hint=func_arg_hint,
            hint_expr=func_arg_type_expr,
            hint_label=func_arg_hint_label,
        )

        # If this parameter is a tuple of positional variadic parameters
        # (e.g., "*args"), iteratively check these parameters.
        if func_arg.kind is Parameter.VAR_POSITIONAL:
            func_body += CODE_PARAM_VARIADIC_POSITIONAL.format(
                func_name=data.func_name,
                arg_name=func_arg.name,
                arg_index=func_arg_index,
                arg_type_expr=func_arg_type_expr,
            )
        # Else if this parameter is keyword-only, check this parameter only
        # by lookup in the variadic "**kwargs" dictionary.
        elif func_arg.kind is Parameter.KEYWORD_ONLY:
            func_body += CODE_PARAM_KEYWORD_ONLY.format(
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
            func_body += CODE_PARAM_POSITIONAL_OR_KEYWORD.format(
                func_name=data.func_name,
                arg_name=func_arg.name,
                arg_index=func_arg_index,
                arg_type_expr=func_arg_type_expr,
                arg_value_key_expr=func_arg_value_key_expr,
                arg_value_pos_expr=func_arg_value_pos_expr,
            )

    # Return this Python code snippet.
    return func_body
