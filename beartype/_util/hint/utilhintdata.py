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
from typing import Any, Optional, Union

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
HINTS_SHALLOW_IGNORABLE = frozenset((
    # Ignorable non-"typing" types.
    object,

    # Ignorable "typing" singletons.
    Any,

    # Ignorable "typing.Optional" objects.
    Optional,
    Optional[object],
    Optional[Any],

    # Ignorable "typing.Union" objects.
    Union,
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

  * :data:`Any` singleton, semantically synonymous with the
    :class:`AnyType` and hence :class:`object` types.
  * :data:`Optional` singleton. Since `PEP 484`_ stipulates that *any*
    unsubscripted subscriptable PEP-compliant object (e.g.,
    :attr:`typing.Generic`, :attr:`Iterable`) semantically expands to that
    object subscripted by an implicit :data:`Any` argument, :data:`Optional`
    semantically expands to the implicit :data:`Optional[Any]` singleton
    object. Since `PEP 484`_ also stipulates that all :data:`Optional[t]`
    objects semantically expand to :data:`Union[t, type(None)]` objects for
    arbitrary arguments ``t``, :data:`Optional[Any]` semantically expands to
    merely :data:`Union[Any, type(None)]`. Since all unions subscripted by
    :data:`Any` semantically reduces to merely :data:`Any`, the
    :data:`Optional` singleton also reduces to merely :data:`Any`.
  * :data:`Union` singleton. For similar reasons, :data:`Union` semantically
    expands to the implicit :data:`Union[Any]` singleton. Since `PEP 484`_
    stipulates that a union of one type semantically reduces to merely that
    type, :data:`Union[Any]` semantically reduces to merely :data:`Any`.
    Despite their semantic equivalency, however, these objects remain
    syntactically distinct with respect to object identification. Notably:

    * ``Union is not Union[Any]``.
    * ``Union is not Any``.

This intentionally intentionally excludes:

* The PEP-compliant:

  * :data:`Optional[type(None)]`, which the :mod:`typing` module physically
    reduces to merely ``type(None)``. (Don't ask, don't tell.)
  * :data:`Union[Any]` and :data:`Union[object]` singletons, since the
    :mod:`typing` module physically reduces:

    * :data:`Union[Any]` to merely :data:`Any` (i.e., ``Union[Any] is Any``),
      which this frozen set already contains.
    * :data:`Union[object]` to merely :data:`object` (i.e., ``Union[object] is
      object``), which this frozen set already contains.

  * :data:`Union` singleton subscripted by one or more ignorable type hints
    contained in this set (e.g., :data:`Union[Any, bool, str]`). Since there
    exist a countably infinite number of these subscriptions, these
    subscriptions *cannot* be explicitly listed in this set. Instead, these
    subscriptions are dynamically detected by the high-level
    :func:`beartype._util.hint.pep.utilhinttest.is_hint_ignorable` tester
    function and thus referred to as deeply ignorable type hints.

Although PEP-specific logic should typically be isolated to private
PEP-specific submodules for maintainability, defining this set here *improves*
maintainability by centralizing similar logic across the codebase.

Caveats
----------
**The high-level**
:func:`beartype._util.hint.pep.utilhinttest.is_hint_ignorable` **tester
function should always be called in lieu of testing type hints against this
low-level set.** This set is merely shallow and thus excludes **deeply
ignorable type hints** (e.g., :data:`Union[Any, bool, str]`). Since there exist
a countably infinite number of deeply ignorable type hints, this set is
necessarily constrained to the substantially smaller finite subset of only
shallowly ignorable type hints.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''
