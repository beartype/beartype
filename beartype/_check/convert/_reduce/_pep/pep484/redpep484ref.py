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

# ....................{ TODO                               }....................
#FIXME: As needed or desired, the reduce_hint_pep484_ref() reducer defined below
#can be additionally generalized to perform further reductions of relative
#forward references to the objects those references refer to. To do so in a
#reasonably sane and algorithmic way:
#* Generalize the existing find_hint_pep484_ref_on_cls_stack_or_none() finder
#  into a new full-blown find_hint_pep484_ref_or_none() finder. Internally,
#  find_hint_pep484_ref_or_none() should perform a "while" loop over lower-level
#  finders like find_hint_pep484_ref_on_cls_stack_or_none(). The comparable
#  canonicalize_hint_pep484_ref() canonicalizer performs a "while" loop over
#  lower-level private canonicalizers should serve as a useful reference.
#* Call find_hint_pep484_ref_or_none() rather than
#  find_hint_pep484_ref_on_cls_stack_or_none() below.
#* Externally privatize find_hint_pep484_ref_on_cls_stack_or_none().
#FIXME: Other useful private finders to have find_hint_pep484_ref_or_none()
#iteratively call should attempt to reduce forward references as follows:
#* Of an absolute unqualified forward reference referring to a builtin type.
#  This one's super-trivial. Use the existing "from beartype._data.cls.datacls
#  import TYPE_BUILTIN_NAME_TO_TYPE" dictionary to map strings like "int" to the
#  corresponding builtin types.
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

# ....................{ IMPORTS                            }....................
from beartype._data.typing.datatyping import (
    HintPep484Ref,
    TypeStack,
)
from beartype._data.typing.datatypingport import Hint
from beartype._util.hint.pep.proposal.pep484.forward.pep484refcanonic import (
    find_hint_pep484_ref_on_cls_stack_or_none)

# ....................{ REDUCERS ~ forwardref              }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep484_ref(
    hint: HintPep484Ref,
    cls_stack: TypeStack,
    exception_prefix: str,
    **kwargs
) -> Hint:
    '''
    Reduce the passed :pep:`484`-compliant **forward reference hint** (i.e.,
    object indirectly referring to a user-defined type that typically has yet to
    be defined) to the object this reference refers to if that object is
    efficiently accessible at this early decoration time without unsafe dynamic
    importation of third-party packages or modules *or* preserve this reference
    as is otherwise.

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

    #FIXME: *INSUFFICIENT,* obviously. Refactor as follows:
    #* First, fully unit test the is_hint_needs_cls_stack() tester.
    #* Next, we need to finally attend to the dangling "FIXME: DRY violation..."
    #  comment in both the "_wrapreturn" and "_wrapargs" submodules. *sigh*
    #* Once we've done that, we then need to utilize this generalized logic for
    #  detecting whether the "cls_stack" is required in that dangling comment:
    #      cls_stack = (
    #          decor_meta.cls_stack
    #          if is_hint_needs_cls_stack(
    #              hint=hint_insane, cls_stack=decor_meta.cls_stack) else
    #          None
    #      )

    # If this forward reference annotates a method of a possibly nested type
    # currently being decorated by the @beartype decorator...
    if cls_stack:
        # Either:
        # * If this is a relative forward reference referring to the possibly
        #   nested and thus partially-qualified name of that type (e.g.,
        #   "OuterType.InnerType"), that type.
        # * Else, "None".
        hint_type = find_hint_pep484_ref_on_cls_stack_or_none(
            hint=hint, cls_stack=cls_stack, exception_prefix=exception_prefix)

        # If this is such a reference, reduce this reference to this type. The
        # type to which this reference refers is directly available, implying
        # that a forward reference is neither needed nor desired anymore.
        if hint_type:
            hint = hint_type  # type: ignore[assignment]
        # Else, this is *NOT* such a reference. In this case, silently preserve
        # this reference as is.
    # Else, this forward reference does *NOT* annotate such a method. In this
    # case, silently preserve this reference as is.

    # Return this possibly reduced forward reference.
    return hint  # pyright: ignore
