#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking cache utilities** (i.e., low-level callables
manipulating global dictionaries distributed throughout the
:mod:`beartype._check` subpackage).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.code.codescope import _tuple_union_to_tuple_union
from beartype._check.convert._convcoerce import _hint_repr_to_hint
from beartype._check.forward.reference.fwdrefmake import (
    _forwardref_args_to_forwardref)
from beartype._check.forward.reference.fwdrefmeta import (
    _forwardref_to_referent)

# ....................{ CLEARERS                           }....................
def clear_checker_caches() -> None:
    '''
    Clear (i.e., empty) *all* internal caches specifically leveraged by the
    :mod:`beartype._check` subpackage, enabling callers to reset this subpackage
    to its initial state.

    Notably, this function clears:

    * The **forward reference proxy cache** (i.e., private
      :data:`beartype._check.forward.reference.fwdrefmake._forwardref_args_to_forwardref`
      dictionary).
    * The **forward reference referee cache** (i.e., private
      :data:`beartype._check.forward.reference.fwdrefmeta._forwardref_to_referent`
      dictionary).
    * The **tuple union cache** (i.e., private
      :data:`beartype._check.code.codescope._tuple_union_to_tuple_union`
      dictionary).
    * The **type hint coercion cache** (i.e., private
      :data:`beartype._check.convert._convcoerce._hint_repr_to_hint`
      dictionary).
    '''
    # print('Clearing all \"beartype._check\" caches...')

    # Clear all relevant caches used throughout this subpackage.
    _forwardref_to_referent.clear()
    _forwardref_args_to_forwardref.clear()
    _hint_repr_to_hint.clear()
    _tuple_union_to_tuple_union.clear()
