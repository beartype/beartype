#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **collections class globals** (i.e., global constants describing
various well-known abstract base classes (ABCs) published by the standard
:mod:`collections.abc` submodule).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    # AsyncGenerator,
    Iterable,
    Iterator,
    # Generator,
)

# ....................{ FROZEN SETS                        }....................
TYPES_ITERABLE_OR_ITERATOR_ASYNC = frozenset((AsyncIterable, AsyncIterator))
'''
Frozen set containing both the standard :class:`collections.abc.AsyncIterable`
*and* :class:`collections.abc.AsyncIterator` abstract base classes (ABCs).
'''


TYPES_ITERABLE_OR_ITERATOR_SYNC = frozenset((Iterable, Iterator))
'''
Frozen set containing both the standard :class:`collections.abc.Iterable` *and*
:class:`collections.abc.Iterator` abstract base classes (ABCs).
'''
