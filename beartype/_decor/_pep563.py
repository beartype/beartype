#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator** `PEP 563`_ **support.**

This private submodule this submodule implements `PEP 563`_ (i.e., "Postponed
Evaluation of Annotations") support on behalf of the :func:`beartype.beartype`
decorator.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
'''

# ....................{ TODO                              }....................
#FIXME: Refactor to support typing types (i.e., "typing" objects and classes).
#Naturally, typing types are *NOT* safely resolvable simply by passing to the
#eval() builtin. Why? Because typing-specific forward references (both explicit
#ala "List[_ForwardRef('C')]" and implicit ala "List['C']") require
#surprisingly non-trivial special handling that we're frankly *NOT* equipped to
#deal with.
#
#Fortunately, the "typing" API actually provides a public function that sort-of
#gets us where we need to go: the public typing.get_type_hints() function,
#which accepts a callable or class and resolves all postponed "typing" hints on
#that callable or class -- forward references and all. Of course, @beartype
#explicitly permits callers to freely mingle PEP-compliant and PEP-noncompliant
#annotations on the same callable. So, simply calling that getter as is is
#guaranteed to explode on us.
#
#Of course, there's a clever alternative (in order):
#
#* Detect whether or not the decorated callable is annotated by one or more
#  PEP-noncompliant type hints.
#* If so:
#  * Shallow-copy the "__annotations__" dictionary of this callable into a new
#    local dictionary -- or perhaps only the PEP-noncompliant type hints from
#    "__annotations__" into that local dictionary. Whatevah's easier, clearly.
#  * Strip all PEP-noncompliant type hints from the original "__annotations__"
#    dictionary of this callable.
#  * Pass this callable to typing.get_type_hints() as is to conveniently
#    resolve all PEP-compliant type hints on that callable.
#  * Resolve all PEP-noncompliant type hints in that shallow copy.
#  * Add those resolved PEP-noncompliant type hints back to the original
#    "__annotations__" dictionary. Voila! Insta-workaround, PEP suckers.
#* If not, simply pass this callable to typing.get_type_hints() as is to
#  conveniently resolve all PEP-compliant type hints on that callable.
#
#Suck it, typing. Suck it.
#FIXME: The most efficient way I've come up with yet to implement this is:
#
#    # ...at the head of _resolve_hints_postponed():
#
#    # If one or more postponed annotations on this callable contain one or
#    # more PEP-compliant unqualified forward references, safely resolve these
#    # annotations in a PEP-compliant manner.
#    #
#    # Note that this test correctly detects both:
#    #
#    #     def muh_func(
#    #         # Top-level PEP-compliant unqualified forward references *AND*...
#    #         muh_bare_ref: 'MuhTypingType',
#    #         # Parametrized PEP-compliant unqualified forward references.
#    #         muh_nest_ref: typing.Tuple['MuhTypingType', ...],
#    #     ): pass
#    if any(
#        "'" in hint_str and '.' not in hint_str
#        for hint_str in data.func.__annotations__.values()
#    ):
#        _resolve_hints_postponed_pep_refs(data)
#    # Else, no annotations on this callable contain PEP-compliant unqualified
#    # forward references. In this case, efficiently resolve these annotations
#    # in a PEP-noncompliant manner.
#    else:
#        _resolve_hints_postponed_fast(data)
#
#The idea here is that the _resolve_hints_postponed_pep_refs() function will be
#considerably less efficient than the _resolve_hints_postponed_fast()
#function, so we only want to call the former when we absolutely must --
#namely, when we need to resolve a PEP-compliant unqualified forward reference.
#In all other cases (including the common case in which one or more annotations
#are PEP-compliant but do *NOT* contain unqualified forward references), the
#more efficient
#
#Then, given the above:
#
#* Define a new _resolve_hints_postponed_fast() function whose implementation
#  resembles that of the current _resolve_hints_postponed() function.
#* Define a new _resolve_hints_postponed_pep_refs() function whose
#  implementation resembles that of the algorithm initially documented above.
#
#Voila! Insta PEP-compliant forward reference resolution for (mostly) free.

# ....................{ IMPORTS                           }....................
import __future__
from beartype.roar import BeartypeDecorPep563Exception
from beartype._decor._data import BeartypeData
from beartype._util.utilpy import (
    IS_PYTHON_AT_LEAST_4_0,
    IS_PYTHON_AT_LEAST_3_7,
)
from sys import modules as sys_modules

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ RESOLVERS                         }....................
def resolve_hints_postponed_if_needed(data: BeartypeData) -> None:
    '''
    Resolve all `PEP 563`_-based **postponed annotations** (i.e., strings that
    when dynamically evaluated as Python expressions yield actual annotations)
    on the currently decorated callable to their **referents** (i.e., the
    actual annotations to which those postponed annotations evaluate) if `PEP
    563`_ is active for this callable *or* silently reduce to a noop otherwise
    (i.e., if `PEP 563`_ is *not* active for this callable).

    Conditions
    ----------
    `PEP 563`_ is active for this callable if the active Python interpreter
    targets at least:

    * Python 3.7.0 *and* the module declaring this callable explicitly enables
      `PEP 563`_ support with a leading dunder importation of the form ``from
      __future__ import annotations``.
    * Python 4.0.0, where `PEP 563`_ is expected to be mandatory.

    Resolution
    ----------
    If the above conditions applies, then for each annotation on this callable:

    * If this annotation is postponed (i.e., is a string), this function:

      #. Dynamically evaluates that string within this callable's globals
         context (i.e., set of all global variables defined by the module
         declaring this callable).
      #. Replaces this annotation's string value with the expression produced
         by this dynamic evaluation.

    * Else, this function preserves this annotation as is.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be resolved.

    Raises
    ----------
    BeartypeDecorPep563Exception
        If evaluating a postponed annotation on this callable raises an
        exception (e.g., due to that annotation referring to local state
        inaccessible in this deferred context).

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''

    # If this callable's annotations are postponed under PEP 563, resolve these
    # annotations to their referents.
    if _is_hints_postponed(data):
        _resolve_hints_postponed(data)

    #FIXME: We currently no longer require this, but nonetheless preserve this
    #for both posterity and the unknowable future to come.
    # Else, this callable's annotations are *NOT* postponed under PEP 563. In
    # this case, shallowly copy the originating annotations dictionary to a
    # beartype-specific annotations dictionary to enable other functions
    # elsewhere to safely modify these annotations.
    # else:
    #     data.func_hints = data.func.__annotations__.copy()

# ....................{ PRIVATE                           }....................
def _is_hints_postponed(data: BeartypeData) -> bool:
    '''
    ``True`` only if `PEP 563`_ is active for the currently decorated callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be inspected.

    Returns
    ----------
    bool
        ``True`` only if `PEP 563`_ is active for this callable.

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert data.__class__ is BeartypeData, (
        '{!r} not @beartype data.'.format(data))

    # True only if PEP 563 is active for this callable.
    #
    # If the active Python interpreter targets at least Python 4.0.x, PEP 563
    # is unconditionally active. Ergo, *ALL* annotations including this
    # callable's annotations are necessarily postponed.
    is_hints_postponed = IS_PYTHON_AT_LEAST_4_0

    # If the active Python interpreter targets at least Python 3.7.x, PEP 563
    # is conditionally active only if...
    if not is_hints_postponed and IS_PYTHON_AT_LEAST_3_7:
        # Module declaring this callable.
        func_module = sys_modules[data.func.__module__]

        # "annotations" attribute declared by this module if any *OR* None.
        func_module_annotations_attr = getattr(
            func_module, 'annotations', None)

        # If this attribute is the "__future__.annotations" object, then the
        # module declaring this callable *MUST* necessarily have enabled PEP
        # 563 support with a leading statement resembling:
        #     from __future__ import annotations
        is_hints_postponed = (
             func_module_annotations_attr is __future__.annotations)

    # Return true only if PEP 563 is active for this callable.
    return is_hints_postponed


def _resolve_hints_postponed(data: BeartypeData) -> None:
    '''
    Resolve all `PEP 563`_-based postponed annotations on the currently
    decorated callable to their referents.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be resolved.

    Raises
    ----------
    BeartypeDecorPep563Exception
        If evaluating a postponed annotation on this callable raises an
        exception (e.g., due to that annotation referring to local state no
        longer accessible from this deferred evaluation).

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert data.__class__ is BeartypeData, (
        '{!r} not @beartype data.'.format(data))
    # print('annotations: {!r}'.format(func.__annotations__))

    # Localize attributes of this metadata for negligible efficiency gains.
    func = data.func
    func_globals = func.__globals__

    # Dictionary mapping from parameter name to resolved annotation for each
    # annotated parameter and return value of this callable.
    func_hints = {}

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
                func_hints[param_name] = eval(param_hint, func_globals)
            # If this fails (as it commonly does), wrap the low-level (and
            # usually non-human-readable) exception raised by eval() with a
            # higher-level human-readable beartype-specific exception.
            except Exception as exception:
                raise BeartypeDecorPep563Exception(
                    '{} parameter "{}" postponed annotation "{}" '
                    'not evaluable.'.format(
                        data.func_name,
                        param_name,
                        param_hint,
                    )
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
            func_hints[param_name] = param_hint

    # Atomically (i.e., all-at-once) replace this callable's postponed
    # annotations with these resolved annotations for safety and efficiency.
    #
    # While the @beartype decorator goes to great lengths to preserve the
    # originating "__annotations__" dictionary as is, PEP 563 is sufficiently
    # expensive, non-trivial, and general-purpose to implement that generally
    # resolving postponed annotations for downstream third-party callers is
    # justified. Everyone benefits from replacing useless postponed annotations
    # with useful real annotations; so, we do.
    func.__annotations__ = func_hints
