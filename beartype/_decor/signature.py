#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator signature introspection.**

This private submodule introspects the signatures of callables to be decorated
by the :func:`beartype.beartype` decorator. Notably, this submodule implements:

* `PEP 563`_ (i.e., Postponed Evaluation of Annotations) support by safely
  resolving all postponed annotations on this callable to their referents.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
'''

# ....................{ IMPORTS                           }....................
import __future__, inspect, sys
from beartype.cave import CallableTypes
from beartype.roar import BeartypeDecorPep563Exception
from beartype._util import (
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_AT_LEAST_4_0,
)
from inspect import Signature

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_func_signature(func: CallableTypes, func_name: str) -> Signature:
    '''
    :class:`Signature` instance encapsulating the passed callable's signature.

    If `PEP 563`_ is conditionally active for this callable, this function
    additionally resolves all postponed annotations on this callable to their
    referents (i.e., the intended annotations to which those postponed
    annotations refer).

    Parameters
    ----------
    func : CallableTypes
        Non-class callable to parse the signature of.
    func_name : str
        Human-readable name of this callable.

    Returns
    ----------
    Signature
        :class:`Signature` instance encapsulating this callable's signature,
        dynamically parsed by the :mod:`inspect` module from this callable.

    Raises
    ----------
    BeartypeDecorPep563Exception
        If evaluating a postponed annotation on this callable raises an
        exception (e.g., due to that annotation referring to local state no
        longer accessible from this deferred evaluation).

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert callable(func), '{!r} uncallable.'.format(func)
    assert isinstance(func_name, str), '{!r} not a string.'.format(func_name)

    # If this callable's annotations are postponed under PEP 563, resolve these
    # annotations to their intended objects *BEFORE* parsing the actual
    # annotations these postponed annotations evaluate to.
    if _is_func_pep_563(func):
        _resolve_func_pep_563(func=func, func_name=func_name)

    # "Signature" instance encapsulating this callable's signature, dynamically
    # parsed by the stdlib "inspect" module from this callable.
    return inspect.signature(func)

# ....................{ PRIVATE ~ PEP 563                 }....................
def _is_func_pep_563(func: CallableTypes) -> bool:
    '''
    ``True`` only if `PEP 563`_ is conditionally active for the passed
    callable, in which case this callable's annotations are initially
    **postponed** (i.e., strings dynamically evaluating to Python expressions
    yielding the desired annotations).

    `PEP 563`_ is conditionally active for this callable if the active Python
    interpreter targets at least:

    * Python 3.7.0 *and* the module declaring this callable explicitly enables
      `PEP 563`_ support with a leading dunder importation of the form ``from
      __future__ import annotations``.
    * Python 4.0.0, where `PEP 563`_ is expected to be mandatory.

    Parameters
    ----------
    func : CallableTypes
        Non-class callable to be introspected.

    Returns
    ----------
    bool
        ``True`` only if `PEP 563`_ is conditionally active for this callable.

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert callable(func), '{!r} uncallable.'.format(func)

    # True only if PEP 563 is active for this callable.
    #
    # If the active Python interpreter targets at least Python 4.0.x, PEP 563
    # is unconditionally active. Ergo, *ALL* annotations including this
    # callable's annotations are necessarily postponed.
    is_func_pep_563 = IS_PYTHON_AT_LEAST_4_0

    # If the active Python interpreter targets at least Python 3.7.x, PEP 563
    # is conditionally active only if...
    if not is_func_pep_563 and IS_PYTHON_AT_LEAST_3_7:
        # Module declaring this callable.
        func_module = sys.modules[func.__module__]

        # "annotations" attribute declared by this module if any *OR* None
        # otherwise.
        func_module_annotations_attr = getattr(
            func_module, 'annotations', None)

        # If this attribute is the "__future__.annotations" object, then the
        # module declaring this callable *MUST* necessarily have enabled PEP
        # 563 support with a leading statement resembling:
        #     from __future__ import annotations
        is_func_pep_563 = (
             func_module_annotations_attr is __future__.annotations)

    # Return True only if PEP 563 is active for this callable.
    return is_func_pep_563


def _resolve_func_pep_563(func: CallableTypes, func_name: str) -> None:
    '''
    Resolve the passed callable with respect to `PEP 563`_.

    This function resolves all postponed annotations on this callable to their
    **referents** (i.e., the intended annotations to which those postponed
    annotations refer). Specifically, for each annotation on this callable:

    * If this annotation is postponed (i.e., is a string), this function:

      #. Dynamically evaluates that string within this callable's globals
         context (i.e., set of all global variables defined by the module
         declaring this callable).
      #. Replaces this annotation's string value with the expression produced
         by this dynamic evaluation.

    * Else, this function preserves this annotation as is.

    Parameters
    ----------
    func : CallableTypes
        Non-class callable to be resolved.
    func_name : str
        Human-readable name of this callable.

    Raises
    ----------
    BeartypeDecorPep563Exception
        If evaluating a postponed annotation on this callable raises an
        exception (e.g., due to that annotation referring to local state no
        longer accessible from this deferred evaluation).

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert callable(func), '{!r} uncallable.'.format(func)
    assert isinstance(func_name, str), '{!r} not a string.'.format(func_name)
    # print('annotations: {!r}'.format(func.__annotations__))

    # Dictionary mapping from parameter name to resolved annotation for
    # each annotated parameter of this callable.
    func_annotations_resolved = {}

    # For the parameter name (or "return" for the return value) and
    # corresponding annotation of each of this callable's annotations...
    #
    # Note that refactoring this iteration into a dictionary comprehension
    # would be largely infeasible (e.g., due to the need to raise
    # human-readable exceptions on evaluating unevaluatable annotations) as
    # well as largely pointless (e.g., due to dictionary comprehensions being
    # either no faster or even slower than explicit iteration for small
    # dictionary sizes, as "func.__annotations__" usually is).
    for param_name, param_hint in func.__annotations__.items():
        # If this annotation is postponed (i.e., is a string), resolve this
        # annotation to its referent against the global variables (if any)
        # defined by the module defining this callable. Note that any local
        # variables referenced by this annotation are now inaccessible and
        # *MUST* be ignored, thus raising an exception here on attempting to
        # evaluate this annotation against a non-inaccessible local.
        #
        # Yes, this is absurd. Yes, this is unavoidable. To quote PEP 563:
        #
        # "When running eval(), the value of globals can be gathered in the
        #  following way:
        #  * function objects hold a reference to their respective globals in
        #    an attribute called __globals__;
        #  ...
        #  The value of localns cannot be reliably retrieved for functions
        #  because in all likelihood the stack frame at the time of the call no
        #  longer exists."
        if isinstance(param_hint, str):
            # Attempt to resolve this postponed annotation to its referent.
            try:
                func_annotations_resolved[param_name] = eval(
                    param_hint, func.__globals__)
            # If this fails (as it commonly does), wrap the low-level (and
            # usually non-human-readable) exception raised by eval() with a
            # higher-level human-readable beartype-specific exception.
            except Exception as exception:
                raise BeartypeDecorPep563Exception(
                    '{} parameter "{}" postponed annotation "{}" '
                    'not evaluable.'.format(func_name, param_name, param_hint)
                ) from exception
        # Else, this annotation is *NOT* postponed (i.e., *NOT* a string). In
        # this case, silently preserve this annotation as is. Since PEP
        # 563 provides no means of distinguishing expected from unexpected
        # evaluation of postponed annotations, either emitting a non-fatal
        # warning *OR* raising a fatal exception here would be overly violent.
        # Instead, we conservatively assume that this annotation was previously
        # postponed but has already been properly resolved to its referent by
        # external logic elsewhere (e.g., yet another runtime type checker).
        #
        # Did we mention that PEP 563 is a shambolic cesspit of inelegant
        # language design and thus an indictment of Guido himself, who approved
        # this festering mess that:
        #
        # * Critically breaks backward compatibility throughout the
        #   well-established Python 3 ecosystem.
        # * Unhelpfully provides no general-purpose API for either:
        #   * Detecting postponed annotations on arbitrary objects.
        #   * Resolving those annotations.
        # * Dramatically reduces the efficiency of annotation-based decorators
        #   for no particularly good reason.
        # * Non-orthogonally prohibits annotations from accessing local state.
        #
        # Because we should probably mention those complaints here.
        else:
            func_annotations_resolved[param_name] = param_hint

    # Replace this callable's postponed annotations with these resolved
    # annotations all at once for both safety and efficiency.
    func.__annotations__ = func_annotations_resolved
