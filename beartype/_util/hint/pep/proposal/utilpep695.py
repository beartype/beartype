#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant **type alias** (i.e., objects created via the
``type`` statement under Python >= 3.12) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: PEP 695 is fundamentally broken for forward references. To sanely handle
#forward references in a way that preserves working behaviour for both trivial
#recursive type aliases *AND* non-trivial recursive type aliases, a significant
#rethink is required. This is that rethink.
#
#Basically, Python itself needs to recursively compose larger type aliases from
#smaller type aliases that it synthetically instantiates on-demand. Since Python
#currently fails to do that, @beartype must do that. Thankfully, this is
#feasible -- albeit non-trivial, as always.
#
#Specifically, the "beartype.claw" API should statically and unconditionally
#transform *EVERY* single type alias as follows:
#    # "beartype.claw" should transform this...
#    type alias = UndeclaredClass | UndeclaredType
#
#    # ...into this.
#    type alias = UndeclaredClass | UndeclaredType
#    while True:
#        try:
#            alias.__value__
#            break
#        except NameError as exception:
#            undeclared_attr_name = get_name_error_attr_name(exception)
#            exec(f'type {undeclared_attr_name} = {undeclared_attr_name}')
#            type alias = UndeclaredClass | UndeclaredType
#
#The above approach transparently supports non-trivial recursive type aliases
#resembling:
#    type circular_foo = list[circular_bar]
#    type circular_bar = int | circular_foo
#
#Given the above transformation, supporting forward references embedded within
#PEP 695-style "type" aliases is now trivial. How? Simply:
#FIXME: Horrifying. Our above idea of performing this transformation:
#    # "beartype.claw" should transform this...
#    type alias = UndeclaredClass | UndeclaredType
#
#    # ...into this.
#    type alias = UndeclaredClass | UndeclaredType
#    while True:
#        try:
#            alias.__value__
#            break
#        except NameError as exception:
#            undeclared_attr_name = get_name_error_attr_name(exception)
#            exec(f'type {undeclared_attr_name} = {undeclared_attr_name}')
#            type alias = UndeclaredClass | UndeclaredType
#
#...fundamentally fails, as each type loop f'type {undeclared_attr_name} =
#{undeclared_attr_name}' is simply a self-recursive tautology that fails to
#correctly update itself when that undeclared attribute becomes declared.
#
#We now have *NO* recourse but to fall back to our age-old standby, the
#beartype._check.forward.fwdref.make_forwardref_indexable_subtype() factory. In
#short, perform the following transformation instead:
#    # "beartype.claw" should transform this...
#    type alias = UndeclaredClass | UndeclaredType
#
#    # ...into this.
#    from beartype._check.forward.fwdref import (
#        make_forwardref_indexable_subtype as
#        __beartype_make_forwardref_indexable_subtype
#    )
#    from beartype._util.error.utilerrorget import (
#        get_name_error_attr_name as __beartype_get_name_error_attr_name)
#
#    type alias = UndeclaredClass | UndeclaredType
#    while True:
#        try:
#            alias.__value__
#            break
#        except NameError as __beartype_exception:
#            __beartype_hint_name = __beartype_get_name_error_attr_name(
#                __beartype_exception)
#            __beartype_forwardref = __beartype_make_forwardref_indexable_subtype(
#                # Fully-qualified name of the current module.
#                __name__,
#                # Unqualified basename of this unresolved type hint.
#                __beartype_hint_name,
#            )
#
#            # If the current scope is module scope, prefer an efficient
#            # non-exec()-based solution. Note that this optimization does *NOT*
#            # generalize to other scopes, for obscure reasons delineated here:
#            #     https://stackoverflow.com/a/8028772/2809027
#            if globals() is locals():
#                globals()[__beartype_hint_name] = __beartype_forwardref
#            # Else, the current scope is *NOT* module scope. In this case,
#            # fallback to an inefficient exec()-based solution.
#            else:
#                exec(f'{__beartype_hint_name} = __beartype_forwardref')
#
#            # Delete the above local variables to avoid polluting namespaces.
#            del (
#                __beartype_exception,
#                __beartype_forwardref,
#                __beartype_hint_name,
#            )

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep695Exception
from beartype._cave._cavefast import HintPep695Type
from beartype._util.error.utilerrorget import get_name_error_attr_name

# ....................{ REDUCERS                           }....................
def reduce_hint_pep695(
    hint: HintPep695Type,
    exception_prefix: str,
    *args, **kwargs
) -> object:
    '''
    Reduce the passed :pep:`695`-compliant **type alias** (i.e., objects created
    by statements of the form ``type {alias_name} = {alias_value}``) to the
    underlying type hint lazily referred to by this type alias.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : object
        Self type hint to be reduced.
    exception_prefix : str, optional
        Human-readable substring prefixing exception messages raised by this
        reducer.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    object
        Underlying type hint lazily referred to by this type alias.
    '''

    # Underlying type hint to be returned.
    hint_aliased: object = None

    # Attempt to reduce this type alias to the type hint it lazily refers to. If
    # this alias contains *NO* forward references to undeclared attributes, this
    # reduction is mostly guaranteed to succeed. So, not at all guaranteed.
    try:
        hint_aliased = hint.__value__  # type: ignore[attr-defined]
    # If doing so raises a builtin "NameError" exception, this alias contains
    # one or more forward references to undeclared attributes. In this case...
    except NameError as exception:
        # Unqualified basename of this type alias (i.e., the name of the global
        # or local variable assigned to by the left-hand side of this alias).
        hint_name = repr(hint)

        # Unqualified basename of the first relative forward reference embedded
        # within this alias.
        hint_ref_name = get_name_error_attr_name(exception)

        # Raise a human-readable exception embedding these names.
        raise BeartypeDecorHintPep695Exception(
            f'{exception_prefix}PEP 695 type alias "{hint_name}" '
            f'unquoted relative forward reference "{hint_ref_name}" '
            f'unsupported outside "beartype.claw" import hooks, '
            f'due to inadequacies in the runtime implementation of '
            f'type aliases beyond the purview of @beartype '
            f'(i.e., PEP 695 is dumb and CPython devs should feel bad). '
            f'Consider either:\n'
            f'* Applying "beartype.claw" import hooks to the '
            f'module defining this type alias: e.g.,\n'
            f'     # In the "{{your_package}}.__init__" submodule:\n'
            f'     from beartype.claw import beartype_this_package\n'
            f'     beartype_this_package()\n'
            f'* Quoting this forward reference in this type alias: e.g.,\n'
            f'     # Instead of this...\n'
            f'     type {hint_name} = ... {hint_ref_name} ...\n'
            f'\n'
            f'     # Do this.\n'
            f'     type {hint_name} = ... "{hint_ref_name}" ...'
        ) from exception

    # Return this underlying type hint.
    return hint_aliased
