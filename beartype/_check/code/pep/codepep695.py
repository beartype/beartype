#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`695`-compliant **type alias type-checking code factories** (i.e.,
low-level callables dynamically generating pure-Python code snippets
type-checking arbitrary objects against type aliases).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Optional
from beartype._check.code.codecls import HintMeta
from beartype._util.hint.pep.proposal.pep695 import (
    get_hint_pep695_subscripted_typevar_to_hint)

# ....................{ FACTORIES                          }....................
def make_hint_pep695_type_alias_subscripted_check_expr(
    # Mandatory parameters.
    hint_meta: HintMeta,
    pith_curr_assign_expr: str,
    pith_curr_var_name_index: int,

    # Optional parameters.
    exception_prefix: str = '',
) -> None:
    '''
    Reduce the mostly semantically useless passed :pep:`695`-compliant
    **subscripted type alias** (i.e., object created by subscripting an object
    created by a statement of the form ``type {alias_name}[{type_var}] =
    {alias_value}`` by one or more child type hints) to the more semantically
    useful :pep:`695`-compliant subscripted type alias underlying this
    unsubscripted type alias.

    This factory is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), due to accepting **context-sensitive
    parameters** (i.e., whose values contextually depend on context unique to
    the code being generated for the currently decorated callable) such as
    ``pith_curr_assign_expr``.

    Parameters
    ----------
    hint_meta : HintMeta
        Metadata describing the currently visited hint, appended by the
        previously visited parent hint to the ``hints_meta`` stack.
    pith_curr_assign_expr : str
        Assignment expression assigning this full Python expression to the
        unique local variable assigned the value of this expression.
    pith_curr_var_name_index : int
        Integer suffixing the name of each local variable assigned the value of
        the current pith in a assignment expression, thus uniquifying this
        variable in the body of the current wrapper function.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.
    '''
    assert isinstance(hint_meta, HintMeta), (
        f'{repr(hint_meta)} not "HintMeta" object.')

    # Reduce this subscripted type alias to:
    # * The semantically useful unsubscripted type alias originating this
    #   semantically useless subscripted type alias.
    # * The type variable lookup table mapping all type variables parametrizing
    #   this alias to all non-type variable hints subscripting this alias.
    hint_child, typevar_to_hint_child = (
        get_hint_pep695_subscripted_typevar_to_hint(
            hint=hint_meta.hint, exception_prefix=exception_prefix))  # pyright: ignore

    # Full type variable lookup table uniting...
    typevar_to_hint_curr = (
        # The type variable lookup table describing all transitive parent hints
        # of this alias *AND*...
        hint_meta.typevar_to_hint |  # type: ignore[operator]
        # The type variable lookup table describing this alias.
        #
        # Note that this table is intentionally the second rather than first
        # operand of this "|" operation, efficiently ensuring that type
        # variables mapped by this alias take precedence over type variables
        # mapped by transitive parent hints of this alias.
        typevar_to_hint_child
    )

    # Silently ignore this semantically useless subscripted type alias in favour
    # of this semantically useful unsubscripted type alias by trivially
    # replacing *ALL* hint metadata describing the former with the latter.
    hint_meta.reinit(
        hint=hint_child,  # pyright: ignore
        indent_level=hint_meta.indent_level + 1,
        pith_expr=pith_curr_assign_expr,
        pith_var_name_index=pith_curr_var_name_index,
        typevar_to_hint=typevar_to_hint_curr,
    )
