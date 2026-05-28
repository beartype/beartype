#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
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
from beartype._check.cls.hint.tree.hinttreecode import HintTreeCode
from beartype._check.pep.pep484585.checkpep484585subclass import (
    get_hint_pep484585_subclass_hint_child_sanified)
from beartype._data.check.code.pep.datacodepep484585 import (
    CODE_PEP484585_SUBCLASS_format)

# ....................{ FACTORIES                          }....................
def make_hint_pep484585_subclass_check_expr(
    hint_tree: HintTreeCode) -> None:
    '''
    Python code snippet type-checking the current pith against the
    passed :pep:`484`- or :pep:`585`-compliant **subclass type hint** of the
    form ``type[...]`` or ``typing.Type[...]``.

    This factory is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the ``hint_tree`` parameter is
    **context-sensitive** (i.e., contextually depends on context unique to the
    code being generated for the currently decorated callable).

    Parameters
    ----------
    hint_tree : HintTreeCode
        Stack of metadata describing all visitable hints previously discovered
        by this breadth-first search (BFS).
    '''
    assert isinstance(hint_tree, HintTreeCode), (
        f'{repr(hint_tree)} not "HintTreeCode" object.')
    # print(f'Visiting generic type {repr(hint_curr)}...')

    # ....................{ IGNORABLE                      }....................
    # Sanified child hint subscripting the subclass hint rooting this tree.
    hint_child = get_hint_pep484585_subclass_hint_child_sanified(hint_tree)

    # If this sanified child hint is the root "object" superclass intentionally
    # returned by the above getter to connote ignorability, this sanified child
    # hint is ignorable. In this case...
    if hint_child is object:
        # Python expression evaluating to the origin type of this hint (i.e.,
        # the "type" root superclass by definition). Since this superclass is a
        # builtin (i.e., universally accessible object), microoptimize this edge
        # case by hardcoding direct (and thus efficient) access of this builtin
        # rather than injecting a hidden beartype-specific parameter into the
        # signature of this wrapper function as we usually do.
        hint_tree.hint_curr_expr = 'type'

        # Fallback to trivial code shallowly type-checking this pith as an
        # instance of this origin type.
        return
    # Else, this sanified child hint is unignorable.

    # ....................{ CHECK                          }....................
    # Python expression evaluating to this child hint passed to this wrapper
    # function.
    hint_curr_expr = add_hints_meta_scope_type_or_types(
        hint_tree=hint_tree, type_or_types=hint_child)  # type: ignore[arg-type]

    # Code type-checking this pith against this superclass.
    hint_tree.func_curr_code = CODE_PEP484585_SUBCLASS_format(
        pith_curr_assign_expr=hint_tree.pith_curr_assign_expr,
        pith_curr_var_name=hint_tree.hint_curr.pith_var_name,
        hint_curr_expr=hint_curr_expr,
        indent_curr=hint_tree.indent_curr,
    )
