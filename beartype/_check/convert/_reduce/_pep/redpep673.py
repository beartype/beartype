#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`673`-compliant **self string type hint reducers** (i.e.,
low-level callables converting higher-level type hints created by subscripting
the :obj:`typing.Self` type hint factory to lower-level type hints more readily
consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep673Exception
from beartype._check.cls.call.callmetaabc import BeartypeCallMetaABC
from beartype._check.cls.hint.hintsane import (
    HintSane,
    make_hint_sane,
)
from beartype._data.typing.datatypingport import Hint
from typing import Optional

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep673(
    call_meta: BeartypeCallMetaABC,
    hint: Hint,
    hint_parent_sane: Optional[HintSane],
    exception_prefix: str,
    **kwargs
) -> HintSane:
    '''
    Reduce the passed :pep:`673`-compliant **self type hint** (i.e.,
    the :obj:`typing.Self` type hint singleton) to the **currently decorated
    class** (i.e., the most deeply nested class on the passed type stack,
    signifying the class currently being decorated by :func:`beartype.beartype`)
    if any *or* raise an exception otherwise (i.e., if *no* class is currently
    being decorated).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    call_meta : BeartypeCallMetaABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    hint : object
        Self type hint to be reduced.
    hint_parent_sane : Optional[HintSane]
        Either:

        * If the passed hint is a **root** (i.e., top-most parent hint of a tree
          of child hints), :data:`None`.
        * Else, the passed hint is a **child** of some parent hint. In this
          case, the **sanified parent type hint metadata** (i.e., immutable and
          thus hashable object encapsulating *all* metadata previously returned
          by :mod:`beartype._check.convert.convmain` sanifiers after sanitizing
          the possibly PEP-noncompliant parent hint of this child hint into a
          fully PEP-compliant parent hint).
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed keyword-only parameters are silently ignored.

    Returns
    -------
    HintSane
        Sanified hint metadata encapsulating most deeply nested class on this
        type stack.

    Raises
    ------
    BeartypeDecorHintPep673Exception
        If either:

        * ``cls_stack`` is :data:`None`.
        * ``cls_stack`` is non-:data:`None` but empty.
    '''

    # Currently decorated type stack, localized for negligible efficiency.
    cls_stack = call_meta.cls_stack

    # If either no type stack *OR* an empty type stack was passed, *NO* class is
    # currently being decorated by @beartype. It follows that either:
    # * @beartype is currently decorating a function or method directly.
    # * A statement-level runtime type-checker (e.g.,
    #   beartype.door.is_bearable()) is currently being called.
    #
    # However, the "typing.Self" type hint *CANNOT* be reliably resolved outside
    # of a class context. Although @beartype could attempt to heuristically
    # differentiate functions from methods via the first passed argument, Python
    # itself does *NOT* require that argument of a method to be named "self";
    # such a heuristic would catastrophically fail in common edge cases. Our
    # only recourse is to raise an exception encouraging the user to refactor
    # their code to decorate classes rather than methods.
    if not cls_stack:
        # We didn't make crazy. We only document it.
        raise BeartypeDecorHintPep673Exception(
            f'{exception_prefix}PEP 673 type hint "{repr(hint)}" '
            f'invalid outside @beartype-decorated class. '
            f'PEP 673 type hints are valid only inside classes decorated by '
            f'@beartype. If this hint annotates a method decorated by '
            f'@beartype, instead decorate the class declaring this method by '
            f'@beartype: e.g.,\n'
            f'\n'
            f'    # Instead of decorating methods by @beartype like this...\n'
            f'    class BadClassIsBad(object):\n'
            f'        @beartype\n'
            f'        def awful_method_is_awful(self: Self) -> Self:\n'
            f'            return self\n'
            f'\n'
            f'    # ...decorate classes by @beartype instead - like this!\n'
            f'    @beartype\n'
            f'    class GoodClassIsGood(object):\n'
            f'        def wonderful_method_is_wonderful(self: Self) -> Self:\n'
            f'            return self\n'
            f'\n'
            f"This has been a message of the Bearhugger Broadcasting Service."
        )
    # Else, a non-empty type stack was passed.

    # Sanified hint metadata encapsulating the currently decorated class (i.e.,
    # the most deeply nested class on this type stack, signifying the class
    # currently being decorated by @beartype.beartype).
    hint_sane = make_hint_sane(  # type: ignore[assignment]
        hint=cls_stack[-1],
        hint_parent_sane=hint_parent_sane,
        # Type-checking code dynamically generated for each "typing.Self" type
        # hint is contextually relative to the currently decorated class and
        # thus *CANNOT* be cached across all "typing.Self" type hints.
        is_check_expr_cacheable=False,
    )

    # Reduce this hint to this metadata.
    return hint_sane
