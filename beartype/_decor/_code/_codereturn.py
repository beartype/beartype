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
from beartype._decor._code._codehint import (
    HINTS_IGNORABLE,
    code_resolve_forward_refs,
)
from beartype._decor._code._snippet import (
    CODE_RETURN_CHECKED,
    CODE_RETURN_UNCHECKED,
    CODE_RETURN_HINT,
)
from beartype._decor._data import BeartypeData
from beartype._util.hint.utilhintnonpep import die_unless_hint_nonpep
from inspect import Signature

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_RETURN_HINTS_IGNORABLE = {Signature.empty,} | HINTS_IGNORABLE
'''
Set of all return value annotation types to be ignored during annotation-based
type checking in the :func:`beartype` decorator.

This includes:

* The :class:`Signature.empty` type, denoting **unannotated return values**
  (i.e., return values *not* annotated with a type hint).
* All context-agnostic types listed in the
  :attr:`beartype._decor.annotation.HINTS_IGNORABLE` set global constant.
'''

# ....................{ CODERS                            }....................
def code_check_return(data: BeartypeData) -> str:
    '''
    Python code snippet type-checking the annotated return value declared by
    the decorated callable if any *or* the empty string otherwise (i.e., if
    this value is unannotated).

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Python code snippet type-checking the annotated return value declared
         by this callable if any *or* the empty string otherwise.
    '''
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))

    # Value of the annotation for this callable's return value.
    func_return_hint = data.func_sig.return_annotation

    # Attempt to...
    #
    # See similar logic in the comparable
    # beartype._decor.parameter._get_code_checking_params() function.
    try:
        # If this annotation is silently ignorable, return code calling this
        # callable unchecked and returning this value from this wrapper.
        if func_return_hint in _RETURN_HINTS_IGNORABLE:
            return CODE_RETURN_UNCHECKED
    # If this annotation is unhashable, the above code raises a "TypeError".
    except TypeError as type_error:
        # If this exception does *NOT* denote unhashability, this exception is
        # unexpected. Raise this exception as is.
        if not str(type_error).startswith("unhashable type: '"):
            raise

    # Human-readable label describing this annotation.
    func_return_hint_label = '{} return type annotation'.format(data.func_name)

    # Validate this annotation.
    die_unless_hint_nonpep(
        hint=func_return_hint, hint_label=func_return_hint_label)

    # String evaluating to this return value's annotated type.
    func_return_type_expr = CODE_RETURN_HINT
    #print('Return annotation: {{}}'.format({func_return_type_expr}))

    # Python code snippet to be returned.
    func_body = '{}{}'.format(
        # Replace all classnames in this annotation with those classes.
        code_resolve_forward_refs(
            hint=func_return_hint,
            hint_expr=func_return_type_expr,
            hint_label=func_return_hint_label,
        ),
        # Call this callable, type check the returned value, and return this
        # value from this wrapper.
        CODE_RETURN_CHECKED.format(
            func_name=data.func_name, return_type_expr=func_return_type_expr),
    )

    # Return this Python code snippet.
    return func_body
