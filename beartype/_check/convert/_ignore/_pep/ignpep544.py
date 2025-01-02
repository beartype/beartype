#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant **type hint ignorers** (i.e., low-level
callables detecting whether :pep:`544`-compliant type hints are ignorable or
not).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    get_hint_or_sane_hint,
)
from beartype._data.api.standard.datamodtyping import TYPING_MODULE_NAMES
from beartype._util.hint.utilhintget import get_hint_repr

# ....................{ TESTERS                            }....................
def is_hint_pep544_ignorable(hint_or_sane: HintOrHintSanifiedData) -> bool:
    '''
    :data:`True` only if the passed :pep:`544`-compliant type hint is ignorable.

    Specifically, this tester returns :data:`True` only if this hint is a
    parametrization of the :class:`typing.Protocol` abstract base class (ABC) by
    one or more type variables. As the name implies, this ABC is generic and
    thus fails to impose any meaningful constraints. Since a type variable in
    and of itself also fails to impose any meaningful constraints, these
    parametrizations are safely ignorable in all possible contexts: e.g.,

    .. code-block:: python

       from typing import Protocol, TypeVar
       T = TypeVar('T')
       def noop(param_hint_ignorable: Protocol[T]) -> T: pass

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only safely callable by
    the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint_or_sane : HintOrHintSanifiedData
        Either a type hint *or* **sanified type hint metadata** (i.e.,
        :data:`.HintSanifiedData` object) to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this :pep:`544`-compliant type hint is ignorable.
    '''

    # Hint encapsulated by this metadata.
    hint = get_hint_or_sane_hint(hint_or_sane)

    # Machine-readable representation of this hint.
    hint_repr = get_hint_repr(hint)

    # If this representation contains a relevant substring suggesting that this
    # hint might be the "Protocol" superclass directly parametrized by type
    # variables (e.g., "typing.Protocol[S, T]")...
    if 'Protocol[' in hint_repr:
        # For the fully-qualified name of each typing module...
        for typing_module_name in TYPING_MODULE_NAMES:
            # If this hint is the "Protocol" superclass defined by this module
            # directly parametrized by one or more type variables (e.g.,
            # "typing.Protocol[S, T]"), ignore this superclass by returning
            # true. This superclass can *ONLY* be parametrized by type
            # variables; a string test thus suffices.
            #
            # For unknown and uninteresting reasons, *ALL* possible objects
            # satisfy the "Protocol" superclass. Ergo, this superclass and *ALL*
            # parametrizations of this superclass are synonymous with the
            # "object" root superclass.
            if hint_repr.startswith(f'{typing_module_name}.Protocol['):
                return True
            # Else, this hint is *NOT* such a "Protocol" superclass. In this
            # case, continue to the next typing module.
        # Else, this hint is *NOT* the "Protocol" superclass directly
        # parametrized by one or more type variables.
    # Else, this representation contains such *NO* such substring.

    # Return false, as *ALL* other "Protocol" subclasses are unignorable.
    return False
