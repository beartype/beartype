#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant **type alias reducers** (i.e., low-level
callables converting higher-level objects created via the ``type`` statement
under Python >= 3.12 to lower-level type hints more readily consumable by
:mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep695Exception
from beartype._cave._cavefast import HintPep695TypeAlias
from beartype._data.hint.datahintpep import Hint
from beartype._util.error.utilerrget import get_name_error_attr_name
from beartype._util.hint.pep.proposal.pep695 import (
    get_hint_pep695_unsubscripted_alias)

# ....................{ REDUCERS                           }....................
# Note that PEP 695-compliant subscripted type aliases are generically reduced
# by the reduce_hint_pep484_subscripted_typevars_to_hints() reducer, which also
# applies to PEP 484- and 585-compliant subscripted generics.

def reduce_hint_pep695_unsubscripted(
    hint: HintPep695TypeAlias, exception_prefix: str, **kwargs) -> Hint:
    '''
    Reduce the passed :pep:`695`-compliant **unsubscripted type alias** (i.e.,
    object created by a statement of the form ``type {alias_name} =
    {alias_value}``) to the underlying type hint referred to by this alias.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : HintPep695TypeAlias
        Unsubscripted type alias to be reduced.
    exception_prefix : str
        Human-readable substring prefixing exception messages raised by this
        reducer.

    All remaining passed keyword parameters are silently ignored.

    Returns
    -------
    Hint
        Underlying type hint referred to by this unsubscripted type alias.

    Raises
    ------
    BeartypeDecorHintPep695Exception
        If this alias contains one or more unquoted relative forward references
        to undefined attributes. Note that this *only* occurs when callers avoid
        beartype import hooks in favour of manually decorating callables and
        classes with the :func:`beartype.beartype` decorator.
    '''

    # Underlying type hint to be returned.
    hint_aliased: Hint = None  # pyright: ignore

    # Attempt to...
    try:
        # Reduce this alias to the type hint it lazily refers to. If this alias
        # contains *NO* forward references to undeclared attributes, this
        # reduction *SHOULD* succeed. Let's pretend we mean that.
        #
        # Note that this getter is memoized and thus intentionally called with
        # positional arguments.
        hint_aliased = get_hint_pep695_unsubscripted_alias(
            hint, exception_prefix)
    # If doing so raises a builtin "NameError" exception, this alias contains
    # one or more forward references to undeclared attributes. In this case...
    except NameError as exception:
        # Unqualified basename of this alias (i.e., name of the global or local
        # variable assigned to by the left-hand side of this alias).
        hint_name = repr(hint)

        # Fully-qualified name of the third-party module defining this alias.
        hint_module_name = hint.__module__
        # print(f'hint_module_name: {hint_module_name}')

        # Unqualified basename of the next remaining undeclared attribute
        # contained in this alias relative to that module.
        hint_ref_name = get_name_error_attr_name(exception)
        # print(f'hint: {hint}; hint_ref_name: {hint_ref_name}')

        # Raise a human-readable exception describing this issue.
        raise BeartypeDecorHintPep695Exception(
            f'{exception_prefix}PEP 695 type alias "{hint_name}" '
            f'unquoted relative forward reference {repr(hint_ref_name)} in '
            f'module "{hint_module_name}" unsupported outside '
            f'"beartype.claw" import hooks. Consider either:\n'
            f'* Quoting this forward reference in this type alias: e.g.,\n'
            f'      # Instead of an unquoted forward reference...\n'
            f'      type {hint_name} = ... {hint_ref_name} ...\n'
            f'\n'
            f'      # Prefer a quoted forward reference.\n'
            f'      type {hint_name} = ... "{hint_ref_name}" ...\n'
            f'* Applying "beartype.claw" import hooks to '
            f'module "{hint_module_name}": e.g.,\n'
            f'      # In your "this_package.__init__" submodule:\n'
            f'      from beartype.claw import beartype_this_package\n'
            f'      beartype_this_package()'
        ) from exception
    # Else, doing so raised *NO* exceptions, implying this alias contains *NO*
    # forward references to undeclared attributes.

    # Return this underlying type hint.
    return hint_aliased
