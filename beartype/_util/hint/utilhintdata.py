#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint globals** (i.e., constant global variables
concerning PEP-agnostic type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from typing import Any, Union

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
HINTS_IGNORABLE = frozenset((
    # Ignorable non-"typing" types.
    object,

    # Ignorable "typing" singletons.
    Any,

    # Ignorable "typing" unions.
    Union,
    Union[Any, object],
    Union[object, Any],
))
'''
Frozen set of all annotation objects to be unconditionally ignored during
annotation-based type checking in the :func:`beartype` decorator regardless of
callable context (e.g., parameter, return value).

This includes:

* The PEP-noncompliant builtin :class:`object` type, syntactically synonymous
  with the :class:`beartype.cave.AnyType` type. Since :class:`object` is the
  transitive superclass of all classes, parameters and return values annotated
  as :class:`object` unconditionally match *all* objects under
  :func:`isinstance`-based type covariance and thus semantically reduce to
  unannotated parameters and return values.
* The PEP-compliant:

  * :data:`Any` singleton object, semantically synonymous with the
    :class:`AnyType` and hence :class:`object` types.
  * :data:`Union` singleton object. Since `PEP 484`_ stipulates that an
    unsubscripted subscriptable PEP-compliant object (e.g., ``Generic``,
    ``Iterable``) semantically expands to that object subscripted by an
    implicit :data:`Any` argument, :data:`Union` semantically expands to the
    implicit :data:`Union[Any]` singleton object. Since `PEP 484`_ also
    stipulates that a union of one type semantically reduces to merely that
    type, :data:`Union[Any]` semantically reduces to merely :data:`Any`.
    Despite their semantic equivalency, however, note that these objects remain
    syntactically distinct with respect to object identification. Notably:

    * ``Union is not Union[Any]``.
    * ``Union is not Any``.

  * :data:`Union[Any, object]` and :data:`Union[object, Any]` singleton
    objects. Since both :data:`Union[Any]` and :data:`Union[object]`
    semantically reduce to a noop, so too do all permutations of those unions.
    Ideally, :data:`Union[Any, object]` and :data:`Union[object, Any]` would be
    cached as the same singleton object. For unknown reasons (presumably,
    unintentional bugs), they currently are *not* under *all* current revisions
    of the :mod:`typing` module (namely, Python 3.5 through 3.8). Why? Because
    order is significant rather than insignificant in :data:`Union` arguments.
    Naturally, this is ludicrous -- but so is most of both `PEP 484`_ and its
    implementation in the :mod:`typing` module. A :data:`Union` is merely a set
    of PEP-compliant objects; sets are unordered; ergo, so should
    :data:`Union`. Since we have no say in the matter, we strenuously object in
    the only meaningful way we can: with a docstring rant no one will ever
    read. (This is that docstring rant, by the way.)

This intentionally does *not* include:

* The PEP-compliant:

  * :data:`Union[Any]` and :data:`Union[object]` singleton objects, since the
    :mod:`typing` module physically reduces:

    * :data:`Union[Any]` to merely :data:`Any` (i.e., ``Union[Any] is Any``),
      which this frozen set already contains.
    * :data:`Union[object]` to merely :data:`object` (i.e., ``Union[object] is
      object``), which this frozen set already contains.

Although PEP-specific logic should typically be isolated to private
PEP-specific submodules for maintainability, defining this set here *improves*
maintainability by centralizing similar logic across the codebase.

Examples
----------
The :mod:`typing` module aggressively caches subscripted objects produced by
that module. Conveniently, this guarantees that subscripting the same objects
declared by that module by the same arguments again produces the same objects,
which also guarantees that external set membership tests against this set with
subscripted objects produced by that module behave as expected: e.g.,

    >>> from typing import Any, Union
    >>> Union is Union
    True
    >>> Union is Union[Any, object]
    False
    >>> Union[Any, object] is Union[Any, object]
    True
    >>> Union[Any, object] is Union[object, Any]
    False
    >>> Union in HINTS_IGNORABLE
    True
    >>> Union[Any, object] in HINTS_IGNORABLE
    True

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''
