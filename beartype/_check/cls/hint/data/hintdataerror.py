#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **exception-generating type hint dataclasses** (i.e., low-level classes
fabricating human-readable strings and associated metadata detailing why the
currently type-checked objects violate the type hints annotating those objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.hint.data.hintdataabc import HintDataABC

# ....................{ SUBCLASSES                         }....................
#FIXME: Unit test us up, please.
class HintDataError(HintDataABC):
    '''
    **Exception-generating type hint dataclass** (i.e., low-level class
    fabricating human-readable strings and associated metadata detailing why the
    currently type-checked object violates the type hint annotating that
    object).

    Instances of this lower-level dataclass are bound to the
    :attr:`beartype._check.cls.hint.tree.hinttreeerror.HintTreeError.hint_data`
    instance variable of the higher-level parent
    :class:`beartype._check.cls.hint.tree.hinttreeerror.HintTreeError` dataclass
    iterating over all such instances for a given type hint tree.
    '''

    pass
