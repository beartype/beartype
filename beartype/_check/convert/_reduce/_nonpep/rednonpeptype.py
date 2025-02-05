#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-noncompliant type hint reducers** (i.e., low-level callables
converting higher-level type hints that do *not* comply with any specific PEP
but are nonetheless shallowly supported by :mod:`beartype` to lower-level type
hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Super-silly. The reduce_hint_nonpep_type() reducer doesn't actually do
#anything except validate the passed hint to be a valid hint. Surely, there is a
#better place for that sort of validation than in a "fake reducer" that doesn't
#actually reduce anything? *sigh*

# ....................{ IMPORTS                            }....................
# from beartype._data.hint.datahinttyping import (
#     Pep484TowerComplex,
#     Pep484TowerFloat,
# )
from beartype._conf.confcls import BeartypeConf
from beartype._data.hint.datahintpep import Hint
from beartype._util.hint.utilhinttest import die_unless_hint

# ....................{ REDUCERS                           }....................
def reduce_hint_nonpep_type(
    hint: Hint,
    conf: BeartypeConf,
    exception_prefix: str,
    **kwargs
) -> Hint:
    '''
    Reduce the passed **PEP-noncompliant type** (i.e., type hint identified
    by *no* sign, implying this hint to almost certainly be an isinstanceable
    type) if this hint satisfies various conditions to another (possibly signed)
    PEP-compliant type hint.

    Specifically:

    * If the passed hint is **shallowly ignorable**
    * If the passed configuration enables support for the :pep:`484`-compliant
      implicit numeric tower *and* this hint is:

      * The builtin :class:`float` type, this reducer expands this type to the
        ``float | int`` union of types.
      * The builtin :class:`complex` type, this reducer expands this type to the
        ``complex | float | int`` union of types.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        PEP-noncompliant hint to be reduced.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    Hint
        PEP-compliant hint reduced from this PEP-noncompliant hint.
    '''

    # FIXME: Preserved in perpetuity. Although currently unused, this logic will
    # probably be desired again at some point. *shrug*
    # assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'
    #
    # # If...
    # if (
    #     # This configuration enables support for the PEP 484-compliant
    #     # implicit numeric tower *AND*...
    #     conf.is_pep484_tower and
    #     # This hint is either the builtin "float" or "complex" classes
    #     # governed by this tower...
    #     (hint is float or hint is complex)
    # # Then expand this hint to the corresponding numeric tower.
    # ):
    #     # Expand this hint to match...
    #     hint = (
    #         # If this hint is the builtin "float" class, both the builtin
    #         # "float" and "int" classes;
    #         Pep484TowerFloat
    #         if hint is float else
    #         # Else, this hint is the builtin "complex" class by the above
    #         # condition; in this case, the builtin "complex", "float", and
    #         # "int" classes.
    #         Pep484TowerComplex
    #     )
    # # Else, this hint is truly unidentifiable.
    # else:

    # If this hint is *NOT* a valid type hint, raise an exception.
    #
    # Note this function call is effectively memoized and thus fast.
    die_unless_hint(hint=hint, exception_prefix=exception_prefix)
    # Else, this hint is a valid type hint.

    # Return this hint as is unmodified.
    return hint
