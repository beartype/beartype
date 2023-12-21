#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant **type alias** (i.e., objects created via the
``type`` statement under Python >= 3.12) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.meta import URL_ISSUES
from beartype.roar import BeartypeDecorHintPep695Exception
from beartype.typing import Optional
from beartype._cave._cavefast import HintPep695Type
from beartype._check.forward.fwdref import make_forwardref_indexable_subtype
from beartype._util.error.utilerrorget import get_name_error_attr_name
from beartype._util.module.utilmodget import get_module_imported_or_none

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

    # Unqualified basename of the previous undeclared attribute in this alias.
    hint_ref_name_prev: Optional[str] = None

    # While this type alias still contains one or more forward references to
    # attributes *NOT* defined by the module declaring this type alias...
    while True:
        # Attempt to...
        try:
            # Reduce this alias to the type hint it lazily refers to. If this
            # alias contains *NO* forward references to undeclared attributes,
            # this reduction *SHOULD* succeed. Let's pretend we mean that.
            hint_aliased = hint.__value__  # type: ignore[attr-defined]

            # This reduction raised *NO* exception and thus succeeded. In this
            # case, immediately halt iteration.
            break
        # If doing so raises a builtin "NameError" exception, this alias
        # contains one or more forward references to undeclared attributes. In
        # this case...
        except NameError as exception:
            # Unqualified basename of this alias (i.e., name of the global or
            # local variable assigned to by the left-hand side of this alias).
            hint_name = repr(hint)

            # Fully-qualified name of the external third-party module defining
            # this alias.
            hint_module_name = hint.__module__

            # That module as its previously imported object.
            hint_module = get_module_imported_or_none(hint_module_name)

            # Unqualified basename of the next remaining undeclared attribute
            # contained in this alias relative to that module.
            hint_ref_name = get_name_error_attr_name(exception)

            # If this attribute is the same as that of the prior iteration of
            # this "while" loop, then that iteration *MUST* have failed to
            # define this attribute as a global variable of that module. In this
            # case, raise an exception.
            #
            # Note that this should *NEVER* happen. Of course, this will happen.
            if hint_ref_name == hint_ref_name_prev:
                raise BeartypeDecorHintPep695Exception(  # pragma: no cover
                    f'{exception_prefix}PEP 695 type alias "{hint_name}" '
                    f'unquoted relative forward reference "{hint_ref_name}" '
                    f'still undefined in module "{hint_module_name}", '
                    f'despite purportedly being defined there. '
                    f'In theory, this should never happen. '
                    f'Of course, this happened. You suddenly feel the '
                    f'horrifying urge to report this grievous failure to the '
                    f'beartype issue tracker:\n\t{URL_ISSUES}'
                ) from exception
            # Else, this attribute differs from that of the prior iteration of
            # this "while" loop.
            #
            # If that module paradoxically claims to already define this
            # attribute as a global variable, raise an exception.
            #
            # Note that this should *NEVER* happen. Of course, this will happen.
            elif hasattr(hint_module, hint_ref_name):
                raise BeartypeDecorHintPep695Exception(  # pragma: no cover
                    f'{exception_prefix}PEP 695 type alias "{hint_name}" '
                    f'unquoted relative forward reference "{hint_ref_name}" '
                    f'already defined in module "{hint_module_name}", '
                    f'despite purportedly being undefined. '
                    f'In theory, this should never happen. '
                    f'Of course, this happened. You suddenly feel the '
                    f'horrifying urge to report this grievous failure to the '
                    f'beartype issue tracker:\n\t{URL_ISSUES}'
                ) from exception
            # Else, that module does *NOT* yet define this attribute.

            # Forward reference proxy to this undeclared attribute.
            hint_ref = make_forwardref_indexable_subtype(
                scope_name=hint_module_name, hint_name=hint_ref_name)

            # Define this attribute as a global variable of that module whose
            # value is this forward reference proxy.
            setattr(hint_module, hint_ref_name, hint_ref)

            # Store the unqualified basename of this previously undeclared
            # attribute for detection by the next iteration of this "while" loop.
            hint_ref_name_prev = hint_ref_name

    # Return this underlying type hint.
    return hint_aliased
