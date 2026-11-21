#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`646`-compliant **tuple type-checking code factories** (i.e.,
low-level callables dynamically generating pure-Python code snippets
type-checking arbitrary objects against :pep:`646`-compliant fixed-variadic
tuple type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.hint.hintsane import HINT_SANE_IGNORABLE
from beartype._check.cls.hint.tree.hinttreecode import HintTreeCode
from beartype._data.check.code.datacodelen import LINE_RSTRIP_INDEX_AND
from beartype._data.check.code.pep.datacodepep484585 import (
    CODE_PEP484585_TUPLE_FIXED_PREFIX,
    CODE_PEP484585_TUPLE_FIXED_SUFFIX,
    CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD_format,
    CODE_PEP484585_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR_format,
)
from beartype._data.check.code.pep.datacodepep646 import (
    CODE_PEP646_TUPLE_FIXED_VARIADIC_CHILD_VARIADIC_format,
    CODE_PEP646_TUPLE_FIXED_VARIADIC_LEN_MIN_format,
    CODE_PEP646_TUPLE_FIXED_VARIADIC_RANDOM_PITH_CHILD_EXPR_format,
)
from beartype._util.hint.pep.proposal.pep646.pep484585646tuple import (
    get_hint_pep646_tuple_fixed_variadic_args,
)
from itertools import chain

# ....................{ FACTORIES                          }....................
def make_hint_pep646_tuple_check_expr(hint_tree: HintTreeCode) -> None:
    '''
    Python code snippet type-checking the current pith against the passed
    :pep:`646`-compliant **fixed-variadic tuple hint** of the form
    ``tuple[{prefix_1}, ..., {prefix_M}, *tuple[{variadic}, ...], {suffix_1},
    ..., {suffix_N}]``.

    The generated code type-checks in :math:`O(1)` time that the current pith is
    a tuple of at least ``M + N`` items whose first ``M`` items satisfy the
    prefix child hints, whose last ``N`` items satisfy the suffix child hints,
    and whose remaining items (if any) are represented by one item satisfying
    the variadic child hint. That item is pseudo-random if the
    :attr:`beartype.BeartypeConf.is_random` option is enabled *or* the first
    such item otherwise.

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

    # ....................{ LOCALS                         }....................
    # Name of the local variable yielding the current pith.
    pith_curr_var_name = hint_tree.hint_curr.pith_var_name

    # Prefix, variadic, and suffix child hints subscripting this tuple hint.
    hints_prefix, hint_variadic, hints_suffix = (
        get_hint_pep646_tuple_fixed_variadic_args(
            hint_tree.hint_curr.hint_sane.hint,
        )
    )

    # Number of prefix and fixed (i.e., prefix and suffix) child hints. The
    # latter is the minimum length of tuples satisfying this hint.
    hints_prefix_len = len(hints_prefix)
    hints_fixed_len = hints_prefix_len + len(hints_suffix)

    # Code type-checking this pith to be a tuple of at least this length.
    func_curr_code = (
        CODE_PEP484585_TUPLE_FIXED_PREFIX +
        CODE_PEP646_TUPLE_FIXED_VARIADIC_LEN_MIN_format(
            pith_curr_var_name=pith_curr_var_name,
            hints_fixed_len=hints_fixed_len,
        )
    )

    # ....................{ FIXED                          }....................
    # For each fixed child hint and the index of the item of this tuple
    # type-checked by that hint (i.e., non-negative indices relative to the
    # start of this tuple for prefix child hints *AND* negative indices
    # relative to the end of this tuple for suffix child hints)...
    for pith_child_index, hint_child in chain(
        enumerate(hints_prefix), enumerate(hints_suffix, -len(hints_suffix))):
        # Unignorable sane child hint sanified from this possibly ignorable
        # insane child hint *OR* "HINT_SANE_IGNORABLE" otherwise.
        hint_child_sane = hint_tree.sanify_hint_child(hint_child)

        # If this child hint is unignorable, deeply type-check this item.
        if hint_child_sane is not HINT_SANE_IGNORABLE:
            func_curr_code += CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD_format(
                hint_child_placeholder=hint_tree.enqueue_hint_child_sane(
                    hint_sane=hint_child_sane,
                    pith_expr=(
                        CODE_PEP484585_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR_format(
                            pith_curr_var_name=pith_curr_var_name,
                            pith_child_index=pith_child_index,
                        )
                    ),
                ),
            )
        # Else, this child hint is ignorable.

    # ....................{ VARIADIC                       }....................
    # Unignorable sane variadic child hint sanified from this possibly
    # ignorable insane child hint *OR* "HINT_SANE_IGNORABLE" otherwise.
    hint_variadic_sane = hint_tree.sanify_hint_child(hint_variadic)

    # If this variadic child hint is unignorable...
    if hint_variadic_sane is not HINT_SANE_IGNORABLE:
        # Python expression yielding either a pseudo-random variadic item of
        # this tuple if randomized type-checking is enabled *OR* the first
        # variadic item of this tuple otherwise.
        pith_child_expr = (
            CODE_PEP646_TUPLE_FIXED_VARIADIC_RANDOM_PITH_CHILD_EXPR_format(
                pith_curr_var_name=pith_curr_var_name,
                hints_prefix_len=hints_prefix_len,
                hints_fixed_len=hints_fixed_len,
            )
            if hint_tree.conf.is_random else
            CODE_PEP484585_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR_format(
                pith_curr_var_name=pith_curr_var_name,
                pith_child_index=hints_prefix_len,
            )
        )

        # Deeply type-check this item if this tuple has variadic items.
        func_curr_code += CODE_PEP646_TUPLE_FIXED_VARIADIC_CHILD_VARIADIC_format(
            pith_curr_var_name=pith_curr_var_name,
            hints_fixed_len=hints_fixed_len,
            hint_child_placeholder=hint_tree.enqueue_hint_child_sane(
                hint_sane=hint_variadic_sane, pith_expr=pith_child_expr),
        )

        # This code requires a pseudo-random integer if and only if randomized
        # type-checking is enabled.
        hint_tree.is_var_random_int_needed |= hint_tree.conf.is_random
    # Else, this variadic child hint is ignorable.

    # ....................{ FORMAT                         }....................
    # Strip the erroneous " and" suffix appended by the last child hint, suffix
    # this code by the substring suffixing all such code, and format this code.
    hint_tree.func_curr_code = (
        f'{func_curr_code[:LINE_RSTRIP_INDEX_AND]}'
        f'{CODE_PEP484585_TUPLE_FIXED_SUFFIX}'
    ).format(
        indent_curr=hint_tree.indent_curr,
        pith_curr_assign_expr=hint_tree.pith_curr_assign_expr,
    )
