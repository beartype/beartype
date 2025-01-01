#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- or :pep:`585`-compliant **type hint ignorers** (i.e.,
low-level callables detecting whether :pep:`484`- or :pep:`585`-compliant type
hints are ignorable or not).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Generic
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    get_hint_or_sane_hint,
)

# ....................{ TESTERS                            }....................
def is_hint_pep484585_generic_subscripted_ignorable(
    hint_or_sane: HintOrHintSanifiedData) -> bool:
    '''
    :data:`True` only if the passed :pep:`484`- or :pep:`585`-compliant
    **subscripted generic** (i.e., unsubscripted generic type originally
    parametrized by one or more :pep:`484`-compliant type variables subscripted
    by a corresponding number of arbitrary child type hints) is ignorable.

    This tester ignores *all* parametrizations of the :class:`typing.Generic`
    abstract base class (ABC) by one or more type variables. As the name
    implies, this ABC is generic and thus fails to impose any meaningful
    constraints. Since a type variable in and of itself also fails to impose any
    meaningful constraints, these parametrizations are safely ignorable in all
    possible contexts: e.g.,

    .. code-block:: python

       from typing import Generic, TypeVar
       T = TypeVar('T')
       def noop(param_hint_ignorable: Generic[T]) -> T: pass

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only safely callable by
    the memoized parent
    :func:`beartype._check.convert._ignore.ignhint.is_hint_ignorable` tester.

    Caveats
    -------
    **Unsubscripted generics are unconditionally unignorable.** This tester thus
    considers *only* subscripted generics.

    Parameters
    ----------
    hint_or_sane : HintOrHintSanifiedData
        Either a type hint *or* **sanified type hint metadata** (i.e.,
        :data:`.HintSanifiedData` object) to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this :pep:`484`-compliant type hint is ignorable.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_origin_or_none
    # print(f'Testing generic hint {repr(hint)} deep ignorability...')

    # Hint encapsulated by this metadata.
    hint = get_hint_or_sane_hint(hint_or_sane)

    # If this generic is the "typing.Generic" superclass directly parametrized
    # by one or more type variables (e.g., "typing.Generic[T]"), return true.
    #
    # Note that we intentionally avoid calling the
    # get_hint_pep_origin_type_isinstanceable_or_none() function here, which has
    # been intentionally designed to exclude PEP-compliant type hints
    # originating from "typing" type origins for stability reasons.
    if get_hint_pep_origin_or_none(hint) is Generic:
        # print(f'Testing generic hint {repr(hint)} deep ignorability... True')
        return True
    # Else, this generic is *NOT* the "typing.Generic" superclass directly
    # parametrized by one or more type variables and thus *NOT* an ignorable
    # non-protocol.
    #
    # Note that this condition being false is *NOT* sufficient to declare this
    # hint to be unignorable. Notably, the origin type originating both
    # ignorable and unignorable protocols is "Protocol" rather than "Generic".
    # Ergo, this generic could still be an ignorable protocol.
    # print(f'Testing generic hint {repr(hint)} deep ignorability... False')

    #FIXME: Probably insufficient. *shrug*
    return False
