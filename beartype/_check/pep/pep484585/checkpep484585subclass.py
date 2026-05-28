#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **subclass type hint
type-checking utilities** (i.e., low-level callables generically applicable to
type-checking both :pep:`484`-compliant ``typing.Type[...]`` type hints and
:pep:`585`-compliant ``type[...]`` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.hint.hintsane import (
    # HINT_IGNORABLE,
    HINT_SANE_IGNORABLE,
)
from beartype._check.cls.hint.tree.hinttreeabc import HintTreeABC
from beartype._data.hint.sign.datahintsigns import HintSignUnion
from beartype._data.typing.datatyping import TypeOrTupleTypes
from beartype._util.cls.pep.clspep3119 import (
    die_unless_object_issubclassable,
    is_object_issubclassable,
)
from beartype._util.hint.pep.proposal.pep484585.pep484585args import (
    get_hint_pep484585_arg)
from beartype._util.hint.pep.utilpepget import get_hint_pep_args
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please. *sigh*
def get_hint_pep484585_subclass_hint_child_sanified(
    hint_tree: HintTreeABC) -> TypeOrTupleTypes:
    '''
    :pep:`3119`-compliant **issubclassable child type(s)** (i.e., type or tuple
    of types valid as the second parameter to the :func:`issubclass` builtin)
    sanified from the **subclass type hint** (i.e., of the :pep:`484`-compliant
    form ``typing.Type[...]`` *or* :pep:`585`-compliant form ``type[...]``)
    rooting the passed type hint tree if these child type(s) are unignorable
    *or* the root :class:`object` superclass otherwise (i.e., if these child
    type(s) are all ignorable).

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as the ``hint_tree`` parameter is
    **context-sensitive** (i.e., contextually depends on context unique to the
    code being generated for the currently decorated callable).

    Parameters
    ----------
    hint_tree : HintTreeABC
        **Subclass type hint tree** (i.e., object describing the tree of all
        type hints rooted at the desired subclass type hint).

    Returns
    -------
    TypeOrTupleTypes
        Either:

        * If these child type(s) are unignorable, the type or tuple of types
          sanified from the subclass type hint rooting this type hint tree.
        * If these child type(s) are all ignorable, the root :class:`object`
          superclass.
    '''
    assert isinstance(hint_tree, HintTreeABC), (
        f'{repr(hint_tree)} not "HintTreeABC" object.')
    # print(f'Visiting generic type {repr(hint_curr)}...')

    # ....................{ LOCALS                         }....................
    # Metadata encapsulating the sanification of this hint, localized for both
    # usability and efficiency.
    hint_sane = hint_tree.hint_curr.hint_sane

    # This sanified subclass hint.
    hint = hint_sane.hint

    # ....................{ SANIFY                         }....................
    # Possibly ignorable insane child hint subscripting this parent sanified
    # subclass hint, guaranteed to be the *ONLY* child hint subscripting this
    # subclass hint.
    hint_child_insane = get_hint_pep484585_arg(
        hint=hint, exception_prefix=hint_tree.exception_prefix)

    # Metadata encapsulating the sanification of this child hint.
    #
    # Note that, if this possibly insane child hint was a PEP 484-compliant
    # forward reference, that this sanified child hint is now guaranteed to be
    # a normal isinstanceable type instead. Ergo, forward references need *NOT*
    # be explicitly handled below.
    hint_child_sane = hint_tree.sanify_hint_child(hint_child_insane)

    #FIXME: Additionally, if "hint_child_sane.hint is type", then this sanified
    #child hint is *ALSO* ignorable. Why? Because *ALL* types necessarily
    #subclass the root "type" superclass. Ergo, the type hint "type[type]" is
    #semantically equivalent to "type[Any]" and thus ignorable.
    #
    #Uncomment that reducer logic elsewhere we currently disabled, please! Ugh.

    # If this sanified child hint is ignorable, this parent subclass hint is
    # trivially type-checkable as an instance of the root "type" superclass. In
    # this case, notify the caller by returning the root "object" superclass.
    if hint_child_sane is HINT_SANE_IGNORABLE:
        return object
    # Else, this child hint is unignorable.

    # ....................{ SANIFY                         }....................
    # Sanified child hint encapsulated by this metadata.
    hint_child = hint_child_sane.hint

    # Sign identifying this child hint.
    hint_child_sign = get_hint_pep_sign_or_none(hint_child)

    # If this child hint is a union of superclasses, reduce this union to a
    # tuple of superclasses. Only the latter is safely passable as the second
    # parameter to the issubclass() builtin under all supported Python versions.
    if hint_child_sign is HintSignUnion:
        hint_child = get_hint_pep_args(hint_child)
    # Else, this child hint is *NOT* a union.

    # If this child hint is *NOT* an issubclassable object, raise an exception.
    # Note that:
    # * The is_object_issubclassable() tester is faster and thus called before
    #   the slower die_unless_object_issubclassable() raiser.
    # * This tester is memoized and thus requires that all parameters be passed
    #   only positionally. It is what it is.
    if not is_object_issubclassable(
        hint_child,  # type: ignore[arg-type]
        # Permit this hint to be a beartype-specific forward reference proxy
        # (i.e., "_BeartypeForwardRefABC" subtype). Although prohibiting such
        # proxies from consideration as supported hints is usually desirable,
        # this lower-level getter called by higher-level reducers that are
        # themselves passed such proxies produced by the even higher-level
        # reduce_hint_pep484_ref() reducer. Such proxies are thus valid for this
        # specific use case.
        True,  # <-- "is_ref_proxy_valid=True", effectively *sigh*
    ):
        die_unless_object_issubclassable(
            obj=hint_child,  # type: ignore[arg-type]
            is_ref_proxy_valid=True,
            exception_prefix=(
                f'{hint_tree.exception_prefix}'
                f'PEP 484 or 585 subclass type hint {repr(hint)} '
                f'child type hint '
            ),
        )
    # Else, this child hint is an issubclassable object.

    # ....................{ RETURN                         }....................
    # Return this child hint.
    return hint_child  # pyright: ignore
