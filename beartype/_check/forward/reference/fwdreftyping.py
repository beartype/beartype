#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype forward reference type hints** (i.e., PEP-compliant type hints
matching :mod:`beartype`-specific forward reference proxies).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.forward.reference._cls.fwdrefabc import (
    BeartypeForwardRefABC)
from beartype._check.forward.reference._cls.fwdreffake import (
    BeartypeForwardRefFakeABC)
from collections.abc import Set

# ....................{ HINTS ~ type                       }....................
#FIXME: Replace all unsafe external references to the private
#"BeartypeForwardRefMetaclass" type with safe references to this type hint instead.
BeartypeForwardRef = type[BeartypeForwardRefABC]
'''
:pep:`585`-compliant type hint matching any :mod:`beartype`-specific **forward
reference proxy** (i.e., class whose metaclass defers the resolution of a
forward reference type hint referencing a type hint that has yet to be defined
in the lexical scope of the external caller).
'''


BeartypeForwardRefFake = type[BeartypeForwardRefFakeABC]
'''
:pep:`585`-compliant type hint matching any :mod:`beartype`-specific **forward
reference fake proxy** (i.e., class whose metaclass pretends to proxy calls to
the :func:`isinstance` and :func:`issubclass` builtins against some externally
defined type when passed that proxy as their second parameters, typically due to
the inaccessibility of that type in the lexical scope in which that proxy is
accessed).
'''

# ....................{ HINTS ~ container                  }....................
AbstractSetBeartypeForwardRefs = Set[BeartypeForwardRef]
'''
:pep:`585`-compliant type hint matching any abstract set of zero or more
:mod:`beartype`-specific forward reference proxies.
'''


FrozenSetBeartypeForwardRefs = frozenset[BeartypeForwardRef]
'''
:pep:`585`-compliant type hint matching any frozen set of zero or more
:mod:`beartype`-specific forward reference proxies.
'''


SetBeartypeForwardRefs = set[BeartypeForwardRef]
'''
:pep:`585`-compliant type hint matching any **set** (i.e., :class:`set`
instance) of zero or more :mod:`beartype`-specific forward reference proxies.
'''
