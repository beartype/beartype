#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **forward reference reducers** (i.e.,
low-level callables converting :pep:`484`-compliant forward references to
lower-level type hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.typing.datatyping import TypeStack
from beartype._data.typing.datatypingport import Hint
from beartype._util.hint.pep.proposal.pep484.pep484ref import (
    get_hint_pep484_ref_names_absolute)

# ....................{ REDUCERS ~ forwardref              }....................
#FIXME: Add to the "_redmap" submodule, please.
#FIXME: Unit test us up, please.
#FIXME: Finalize implementation, please. Useful reductions for this reducer to
#eventually perform include:
#* Of an absolute unqualified forward reference referring to a builtin type.
#  Pretty sure we have similar functionality elsewhere. Our PEP 563 resolver,
#  perhaps? *shrug*
#* Of a relative unqualified forward reference referring to a *GLOBAL* attribute
#  of the module defining this *METHOD* if this reduction is being performed
#  against a *METHOD*, as is the case when the "cls_stack" parameter is
#  non-"None". In this case, we can trivially obtain these globals with a
#  similar one-liner to that suggested by PEP 563 (lol):
#      cls_globals = vars(sys.modules[cls_stack[-1].__module__])
#
#  Of course, note that "__module__" may be either "None" *OR* an imaginary
#  in-memory string that has no relation to "sys.modules". Some care is thus
#  warranted.
#
#  Note that the above one-liner should be expanded into a more general-purpose
#  get_type_globals() getter. We currently define get_type_locals() but *NOT*
#  get_type_globals(), interestingly. *shrug*
#* Of a relative unqualified forward reference referring to a *CLASS* attribute
#  of the type currently being decorated. Note that all class attributes are
#  efficiently accessible via the existing get_type_locals() getter. Call it!
#* Of a relative forward reference referring to a *GLOBAL* attribute of the
#  module defining this callable if this reduction is being performed against a
#  callable, as is the case when the "decor_meta" parameter is non-"None".
#  Recall that "decor_meta.func_wrappee_wrappee.__globals__" efficiently
#  provides the dictionary mapping from the names to values of all global
#  attributes accessible to the unwrapped decorated callable.
#
#  Note that:
#  * We intentionally do *NOT* bother attempting to resolve relative forward
#    reference referring to a *LOCAL*, as resolving local attributes against an
#    arbitrary callable is extremely inefficient in the general case.
#  * This reduction is currently pointless to attempt, despite being both
#    intelligent and useful. Why? Because higher-level callers calling the
#    parent reduce_hint() function currently *ONLY* pass the requisite
#    "decor_meta" parameter when the root type hint is being sanified by the
#    sanify_hint_root_func() sanifier. Two refactorings thus need to happen to
#    make this proposed reduction here useful:
#    * But a totally different code path in the coerce_func_hint_root() function
#      already reduces root type hints that are forward references! Ideally, the
#      coerce_func_hint_root() function should stop performing that reduction.
#    * Other sanifiers need to both receive and pass "decor_meta". The issue
#      is... maybe it's not even feasible! In all likelihood, "decor_meta" isn't
#      even accessible in those lower-level contexts, because that would destroy
#      memoization.
#  * In other words, this is probably impossible. Oh, well.
#
#Initially focus *ONLY* on the "cls_stack" use case, please. Those are the ones
#we absolutely *MUST* implement. They're *NOT* optimizations; they're critical
#reductions supporting edge-case type hints that *CANNOT* be readily supported
#any other way. The remainder of the above reductions are merely optimizations
#(albeit useful optimizations at that).
def reduce_hint_pep484_ref(
    hint: Hint,
    cls_stack: TypeStack,
    exception_prefix: str,
    **kwargs
) -> Hint:
    '''
    Reduce the passed :pep:`484`-compliant **forward reference hint** (i.e.,
    object indirectly referring to a user-defined type that typically has yet to
    be defined) to the object this reference refers to if that object is
    efficiently accessible at this early decoration time *or* preserve this
    reference as is otherwise.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), due to requiring contextual parameters and
    thus being fundamentally unmemoizable.

    Parameters
    ----------
    hint : Hint
        Type hint to be reduced.
    cls_stack : TypeStack
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    Hint
        Either:

        * If the object this hint refers to is efficiently accessible at this
          early decoration time, that object.
        * Else, this hint unmodified.
    '''

    #* Of a relative unqualified forward reference referring to a non-nested class
    #  to that class if the "cls_stack" contains *ONLY* that class.
    #* Of a relative qualified forward reference referring to a nested class to that
    #  class if the "cls_stack" contains two or more classes.

    # Fully-qualified module name and unqualified classname referred to by this
    # forward reference, canonicalized relative to the module declaring the
    # passed type stack.
    hint_module_name, hint_type_name = get_hint_pep484_ref_names_absolute(
        hint=hint,  # pyright: ignore
        cls_stack=cls_stack,
        exception_prefix=exception_prefix,
    )

    # Return this forward reference unmodified as a fallback.
    return hint
