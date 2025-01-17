#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant **type alias reducers** (i.e., low-level
callables converting higher-level objects created via the ``type`` statement
under Python >= 3.12 to lower-level type hints more readily consumable by
:mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Any
from beartype._data.api.standard.datamodtyping import TYPING_MODULE_NAMES
from beartype._data.hint.datahintpep import Hint
from beartype._util.hint.utilhintget import get_hint_repr

# ....................{ REDUCERS                           }....................
def reduce_hint_pep544(hint: Hint, exception_prefix: str, **kwargs) -> Hint:
    '''
    Reduce the passed :pep:`544`-compliant **protocol** (i.e., user-defined
    subclass of the :class:`typing.Protocol` abstract base class (ABC)) to the
    ignorable :obj:`typing.Any` singleton if this protocol is a parametrization
    of this ABC by one or more :pep:`484`-compliant **type variables** (i.e.,
    :class:`typing.TypeVar` objects).

    As the name implies, this ABC is generic and thus fails to impose any
    meaningful constraints. Since a type variable in and of itself also fails to
    impose any meaningful constraints, these parametrizations are safely
    ignorable in all possible runtime contexts: e.g.,

    .. code-block:: python

       from typing import Protocol, TypeVar
       T = TypeVar('T')
       def noop(param_hint_ignorable: Protocol[T]) -> T: pass

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Type hint to be reduced.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed keyword parameters are silently ignored.

    Returns
    -------
    Hint
        Lower-level type hint currently supported by :mod:`beartype`.
    '''

    # Machine-readable representation of this hint.
    hint_repr = get_hint_repr(hint)

    # If this representation contains a relevant substring suggesting that this
    # hint *MIGHT* be the "Protocol" superclass directly parametrized by type
    # variables (e.g., "typing.Protocol[S, T]")...
    if 'Protocol[' in hint_repr:
        # For the fully-qualified name of each typing module...
        for typing_module_name in TYPING_MODULE_NAMES:
            # If this hint is the "Protocol" superclass defined by this module
            # directly parametrized by one or more type variables (e.g.,
            # "typing.Protocol[S, T]"), ignore this superclass by returning the
            # ignorable "typing.Any" singleton. This superclass can *ONLY* be
            # parametrized by type variables; a string test thus suffices.
            #
            # For unknown and uninteresting reasons, *ALL* possible objects
            # satisfy the "Protocol" superclass. Ergo, this superclass and *ALL*
            # parametrizations of this superclass are synonymous with the
            # "object" root superclass.
            if hint_repr.startswith(f'{typing_module_name}.Protocol['):
                return Any  # pyright: ignore
            # Else, this hint is *NOT* such a "Protocol" superclass. In this
            # case, continue to the next typing module.
        # Else, this hint is *NOT* the "Protocol" superclass directly
        # parametrized by one or more type variables.
    # Else, this representation contains such *NO* such substring.

    # Return this protocol unmodified, as *ALL* other "Protocol" subclasses are
    # unignorable by definition.
    return hint
