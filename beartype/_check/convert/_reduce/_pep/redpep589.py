#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`589`-compliant **type alias reducers** (i.e., low-level
callables converting higher-level objects created via the ``type`` statement
under Python >= 3.12 to lower-level type hints more readily consumable by
:mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.datahinttyping import MappingStrToAny

# ....................{ REDUCERS                           }....................
#FIXME: Remove *AFTER* deeply type-checking typed dictionaries. For now,
#shallowly type-checking such hints by reduction to untyped dictionaries
#remains the sanest temporary work-around.
def reduce_hint_pep589(**kwargs) -> Hint:
    '''
    Reduce the passed :pep:`589`-compliant **typed dictionary** (i.e.,
    :class:`typing.TypedDict` subclass) to a lower-level type hint currently
    supported by :mod:`beartype`.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    All passed keyword arguments are silently ignored. So it goes.

    Returns
    -------
    Hint
        Lower-level type hint currently supported by :mod:`beartype`.
    '''

    # Silently ignore all child type hints annotating this dictionary by
    # reducing this hint to the "Mapping" type hint. Yes, "Mapping" rather than
    # "dict". By PEP 589 edict:
    #     First, any TypedDict type is consistent with Mapping[str, object].
    return MappingStrToAny  # pyright: ignore
