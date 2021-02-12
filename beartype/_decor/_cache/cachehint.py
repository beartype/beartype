#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Cecil Curry.
# See "LICENSE" for further details.

'''
**Type hint cache** (i.e., singleton dictionary mapping from the
machine-readable representations of all non-self-cached type hints to those
hints).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CACHES                            }....................
HINT_REPR_TO_HINT = {}
'''
**Type hint cache** (i.e., singleton dictionary mapping from the
machine-readable representations of all non-self-cached type hints to those
hints).**

This dictionary caches:

* `PEP 585`_-compliant type hints, which do *not* cache themselves.
* `PEP 563`_-compliant **deferred type hints** (i.e., type hints persisted as
  evaluatable strings rather than actual type hints), enabled if the active
  Python interpreter targets either:

  * Python 3.7.0 *and* the module declaring this callable explicitly enables
    `PEP 563`_ support with a leading dunder importation of the form ``from
    __future__ import annotations``.
  * Python 4.0.0, where `PEP 563`_ is expected to be mandatory.

This dictionary does *not* cache:

* Type hints declared by the :mod:`typing` module, which implicitly cache
  themselves on subscription thanks to inscrutable metaclass magic.

Design
------
This dictionary does *not* bother caching **self-cached type hints** (i.e.,
type hints that externally cache themselves), as these hints are already cached
elsewhere. Self-cached type hints include most `PEP 484`_-compliant type hints
declared by the :mod:`typing` module, which means that subscripting type hints
declared by the :mod:`typing` module with the same child type hints reuses the
exact same internally cached objects rather than creating new uncached objects:
e.g.,

.. code-block:: python

   >>> import typing
   >>> typing.List[int] is typing.List[int]
   True

Equivalently, this dictionary *only* caches **non-self-cached type hints**
(i.e., type hints that do *not* externally cache themselves), as these hints
are *not* already cached elsewhere. Non-self-cached type hints include *all*
`PEP 585`_-compliant type hints produced by subscripting builtin container
types, which means that subscripting builtin container types with the same
child type hints creates new uncached objects rather than reusing the same
internally cached objects: e.g.,

.. code-block:: python

   >>> list[int] is list[int]
   False

Implementation
--------------
This dictionary is intentionally designed as a naive dictionary rather than
robust LRU cache, for the same reasons that callables accepting hints are
memoized by the :func:`beartype._util.cache.utilcachecall.callable_cached`
rather than the :func:`functools.lru_cache` decorator. Why? Because:

* The number of different type hints instantiated across even worst-case
  codebases is negligible in comparison to the space consumed by those hints.
* The :attr:`sys.modules` dictionary persists strong references to all
  callables declared by previously imported modules. In turn, the
  ``func.__annotations__`` dunder dictionary of each such callable persists
  strong references to all type hints annotating that callable. In turn, these
  two statements imply that type hints are *never* garbage collected but
  instead persisted for the lifetime of the active Python process. Ergo,
  temporarily caching hints in an LRU cache is pointless, as there are *no*
  space savings in dropping stale references to unused hints.

Motivation
----------
This dictionary enables callers to coerce non-self-cached type hints into
:mod:`beartype`-cached type hints. :mod:`beartype` effectively requires *all*
type hints to be cached somewhere! :mod:`beartype` does *not* care who, what,
or how is caching those type hints -- only that they are cached before being
passed to utility functions in the :mod:`beartype` codebase. Why? Because
most such utility functions are memoized for efficiency by the
:func:`beartype._util.cache.utilcachecall.callable_cached` decorator, which
maps passed parameters (typically including the standard ``hint`` parameter
accepting a type hint) based on object identity to previously cached return
values. You see the problem, we trust.

Non-self-cached type hints that are otherwise semantically equal are
nonetheless distinct objects and will thus be treated as distinct parameters by
memoization decorators. If this dictionary did *not* exist, non-self-cached
type hints could *not* be coerced into :mod:`beartype`-cached type hints and
thus could *not* be memoized, dramatically reducing the efficiency of
:mod:`beartype` for common type hints.

.. _PEP 484:
    https://www.python.org/dev/peps/pep-0484
.. _PEP 563:
    https://www.python.org/dev/peps/pep-0563
.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''
