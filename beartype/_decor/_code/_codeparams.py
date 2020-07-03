#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator parameter type checking.**

This private submodule dynamically generates pure-Python code type-checking all
annotated parameters of the callable currently being decorated by the
:func:`beartype.beartype` decorator.

This private submodule is *not* intended for importation by downstream callers.
'''

#FIXME: Unify this submodule with the "_codehint" and "_codereturn" submodules.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorParamNameException
from beartype._decor._code._codehint import HINTS_IGNORABLE
from beartype._decor._code._nonpep.nonpepparam import nonpep_code_check_param
from beartype._decor._data import BeartypeData
from beartype._util.hint.utilhint import die_unless_hint
from beartype._util.hint.utilhintnonpep import die_unless_hint_nonpep
from beartype._util.hint.utilhintpep import is_hint_typing
from inspect import Parameter

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
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
    Python code type-checking all annotated parameters of the decorated
    callable if any *or* the empty string otherwise (i.e., if these parameters
    are unannotated).

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Python code snippet type-checking all annotated parameters of the
        decorated callable if any *or* the empty string otherwise.

    Raises
    ----------
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__beartyp``.
    BeartypeDecorHintValueNonPepException
        If any type hint annotating any parameter of this callable is *not*
        **PEP-noncompliant** (i.e., fails to comply with
        :mod:`beartype`-specific semantics, including tuple unions and
        fully-qualified forward references).
    BeartypeDecorHintValueUnhashableException
        If any type hint annotating any parameter of this callable is
        **unhashable** (i.e., *not* hashable by the builtin :func:`hash`
        function and thus unusable in hash-based containers like dictionaries).
    '''
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))

    # Python code snippet to be returned.
    func_code = ''

    # For the name of each parameter accepted by this callable and the
    # "Parameter" instance encapsulating this parameter (in declaration
    # order)...
    for func_arg_index, func_arg in enumerate(
        data.func_sig.parameters.values()):
        # If this parameter is unannotated, continue to the next parameter.
        if func_arg.annotation is Parameter.empty:
            continue
        # Else, this parameter is annotated.

        # If this annotation is unsupported, raise an exception; else, this
        # annotation is guaranteed to be supported and thus hashable.
        die_unless_hint(func_arg.annotation)

        # If this callable redefines a parameter initialized to a default value
        # by this wrapper, raise an exception. Permitting this unlikely edge
        # case would permit unsuspecting users to accidentally override these
        # defaults.
        if func_arg.name.startswith('__beartyp'):
            raise BeartypeDecorParamNameException(
                '{} parameter "{}" reserved by @beartype.'.format(
                    data.func_name, func_arg.name))

        # If the type of either this parameter or annotation is silently
        # ignorable, continue to the next parameter.
        #
        # Note the "in" operator when applied to a set() object requires that
        # the first operand (i.e., "func_arg_hint" and "func_arg_kind") to be
        # hashable. Since:
        #
        # * "func_arg.annotation" is guaranteed to be hashable by the prior
        #   call to the die_unless_hint() validator.
        # * "func_arg_kind" derives from the stdlib "inspect" module, this
        #   should *ALWAYS* be the case for that object.
        if (func_arg.annotation in HINTS_IGNORABLE or
            func_arg.kind in _PARAM_KINDS_IGNORABLE):
            continue

        # If this is a PEP-compliant annotation...
        if is_hint_typing(func_arg.annotation):
            #FIXME: Implement us up. Raise a placeholder exception for now.
            die_unless_hint_nonpep(
                hint=func_arg.annotation,
                hint_label=('{} parameter "{}" type hint'.format(
                    data.func_name, func_arg.name)))
        # Else, this is a PEP-noncompliant annotation. In this case...
        else:
            # Append Python statements to the body of this wrapper function
            # type-checking this parameter against this annotation.
            func_code += nonpep_code_check_param(
                data=data,
                func_arg=func_arg,
                func_arg_index=func_arg_index,
            )

    # Return this Python code.
    return func_code
