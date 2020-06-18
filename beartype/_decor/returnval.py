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
from beartype._decor import annotation
from beartype._decor.snippet import (
    CODE_RETURN_CHECKED,
    CODE_RETURN_UNCHECKED,
    CODE_RETURN_HINT,
)
# from beartype.cave import ()
# from beartype.roar import ()
from inspect import Signature

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_RETURN_HINT_IGNORABLE = {Signature.empty, None}
'''
Set of all return value annotation types to be ignored during annotation-based
type checking in the :func:`beartype` decorator.

This includes:

* The :class:`Signature.empty` type, denoting **unannotated return values**
  (i.e., return values *not* annotated with a type hint).
* ``None``, signifying a callable returning no value. By convention, callables
  returning no value are typically annotated to return ``None``. Technically,
  callables whose return values are annotated as ``None`` *could* be explicitly
  checked to return ``None`` rather than a none-``None`` value. Since return
  values are safely ignorable by callers, however, there appears to be little
  real-world utility in enforcing this constraint.
'''

# ....................{ GETTERS                           }....................
def get_code_checking_return(func_name: str, func_sig: Signature) -> str:
    '''
    Python code snippet type-checking the annotated return value declared by
    the passed signature of the passed callable name if any *or* reduce to a
    noop otherwise (i.e., if this value is unannotated).

    Parameters
    ----------
    func_name : str
        Human-readable name of this callable.
    func_sig : Signature
        :class:`Signature` instance encapsulating this callable's signature,
        dynamically parsed by the :mod:`inspect` module from this callable.

    Returns
    ----------
    str
        Python code snippet type-checking the annotated return value declared
        by this signature of this callable name if any *or* reduce to a noop
        otherwise (i.e., if this value is unannotated).
    '''
    assert isinstance(func_name, str), '{!r} not a string.'.format(func_name)
    assert isinstance(func_sig, Signature), (
        '{!r} not a signature.'.format(func_sig))

    # Value of the annotation for this callable's return value.
    func_return_hint = func_sig.return_annotation

    # Attempt to...
    #
    # See similar logic in the comparable
    # beartype._decor.parameter._get_code_checking_params() function.
    try:
        # If this annotation is silently ignorable, return code calling this
        # callable unchecked and returning this value from this wrapper.
        if func_return_hint in _RETURN_HINT_IGNORABLE:
            return CODE_RETURN_UNCHECKED
    # If this annotation is unhashable, the above code raises a "TypeError".
    except TypeError as type_error:
        # If this exception does *NOT* denote unhashability, this exception is
        # unexpected. Raise this exception as is.
        if not str(type_error).startswith("unhashable type: '"):
            raise

    # Human-readable label describing this annotation.
    func_return_hint_label = '{} return type annotation'.format(func_name)

    # Validate this annotation.
    annotation.verify_hint(
        hint=func_return_hint, hint_label=func_return_hint_label)

    # String evaluating to this return value's annotated type.
    func_return_type_expr = CODE_RETURN_HINT
    #print('Return annotation: {{}}'.format({func_return_type_expr}))

    # Python code snippet to be returned.
    func_body = '{}{}'.format(
        # Replace all classnames in this annotation with those classes.
        annotation.get_code_resolving_forward_refs(
            hint=func_return_hint,
            hint_expr=func_return_type_expr,
            hint_label=func_return_hint_label,
        ),
        # Call this callable, type check the returned value, and return this
        # value from this wrapper.
        CODE_RETURN_CHECKED.format(
            func_name=func_name, return_type_expr=func_return_type_expr),
    )

    # Return this Python code snippet.
    return func_body
