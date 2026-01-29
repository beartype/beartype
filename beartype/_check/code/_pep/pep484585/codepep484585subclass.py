#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`- or :pep:`585`-compliant **subclass type-checking code
factories** (i.e., low-level callables dynamically generating pure-Python code
snippets type-checking arbitrary objects against ``type[...]`` and
``typing.Type[...]`` type hints, which warrant special handling).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.code.codescope import add_hints_meta_scope_type_or_types
from beartype._check.metadata.hint.hintsane import HINT_SANE_IGNORABLE
from beartype._check.metadata.hint.hintsmeta import HintsMeta
from beartype._data.code.pep.datacodepep484585 import (
    CODE_PEP484585_SUBCLASS_format)
from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.hint.sign.datahintsigns import HintSignUnion
from beartype._util.cls.pep.clspep3119 import (
    die_unless_object_issubclassable,
    is_object_issubclassable,
)
from beartype._util.hint.pep.proposal.pep484585.pep484585args import (
    get_hint_pep484585_arg)
from beartype._util.hint.pep.utilpepget import get_hint_pep_args
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

# ....................{ FACTORIES                          }....................
def make_hint_pep484585_subclass_check_expr(
    hints_meta: HintsMeta) -> None:
    '''
    Python code snippet type-checking the current pith against the
    passed :pep:`484`- or :pep:`585`-compliant **subclass type hint** of the
    form ``type[...]`` or ``typing.Type[...]``.

    This factory is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the ``hints_meta`` parameter is
    **context-sensitive** (i.e., contextually depends on context unique to the
    code being generated for the currently decorated callable).

    Parameters
    ----------
    hints_meta : HintsMeta
        Stack of metadata describing all visitable hints previously discovered
        by this breadth-first search (BFS).
    '''
    assert isinstance(hints_meta, HintsMeta), (
        f'{repr(hints_meta)} not "HintsMeta" object.')
    # print(f'Visiting generic type {repr(hint_curr)}...')

    # ....................{ PARENT                         }....................
    # Metadata encapsulating the sanification of this hint, localized for both
    # usability and efficiency.
    hint_sane = hints_meta.hint_curr_meta.hint_sane

    # This sanified subclass hint.
    hint = hint_sane.hint

    # ....................{ CHILD                          }....................
    # Possibly ignorable insane child hint subscripting this parent sanified
    # subclass hint, guaranteed to be the *ONLY* child hint subscripting this
    # subclass hint.
    hint_child_insane = get_hint_pep484585_arg(
        hint=hint, exception_prefix=hints_meta.exception_prefix)

    # Metadata encapsulating the sanification of this child hint.
    #
    # Note that, if this possibly insane child hint was a PEP 484-compliant
    # forward reference, that this sanified child hint is now guaranteed to be
    # a normal isinstanceable type instead. Ergo, forward references need *NOT*
    # be explicitly handled below.
    hint_child_sane = hints_meta.sanify_hint_child(hint_child_insane)

    # If this sanified child hint is ignorable...
    if hint_child_sane is HINT_SANE_IGNORABLE:
        # Python expression evaluating to the origin type of this hint (i.e.,
        # the "type" root superclass by definition). Since this superclass is a
        # builtin (i.e., universally accessible object), microoptimize this edge
        # case by hardcoding direct (and thus efficient) access of this builtin
        # rather than injecting a hidden beartype-specific parameter into the
        # signature of this wrapper function as we usually do.
        hints_meta.hint_curr_expr = 'type'

        # Fallback to trivial code shallowly type-checking this pith as an
        # instance of this origin type.
        return
    # Else, this child hint is unignorable.

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
    #
    # Note that the is_object_issubclassable() tester is considerably faster and
    # thus called before the considerably slower
    # die_unless_object_issubclassable() raiser.
    if not is_object_issubclassable(hint_child):  # type: ignore[arg-type]
        die_unless_object_issubclassable(
            obj=hint_child,  # type: ignore[arg-type]
            exception_prefix=(
                f'{EXCEPTION_PLACEHOLDER}'
                f'PEP 484 or 585 subclass type hint {repr(hint)} '
                f'child type hint '
            ),
        )
    # Else, this child hint is an issubclassable object.

    # ....................{ CHECK                          }....................
    # Python expression evaluating to this child hint passed to this wrapper
    # function.
    hint_curr_expr = add_hints_meta_scope_type_or_types(
        hints_meta=hints_meta, type_or_types=hint_child)  # type: ignore[arg-type]

    # Code type-checking this pith against this superclass.
    hints_meta.func_curr_code = CODE_PEP484585_SUBCLASS_format(
        pith_curr_assign_expr=hints_meta.pith_curr_assign_expr,
        pith_curr_var_name=hints_meta.pith_curr_var_name,
        hint_curr_expr=hint_curr_expr,
        indent_curr=hints_meta.indent_curr,
    )
