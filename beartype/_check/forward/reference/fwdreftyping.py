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
from beartype._check.forward.reference._fwdrefabc import BeartypeForwardRefABC
# from beartype._check.forward.reference._fwdrefmeta import BeartypeForwardRefMeta

# ....................{ TESTERS                            }....................
#FIXME: Replace all unsafe external references to the private
#"BeartypeForwardRefMeta" type with safe references to this type hint instead.
BeartypeForwardRef = type[BeartypeForwardRefABC]
'''
:pep:`585`-compliant type hint matching a :mod:`beartype`-specific **forward
reference proxy** (i.e., class whose metaclass defers the resolution of a
forward reference type hint referencing a type hint that has yet to be defined
in the lexical scope of the external caller).
'''


TupleBeartypeForwardRefs = tuple[BeartypeForwardRef, ...]
'''
:pep:`585`-compliant type hint matching a tuple of zero or more
:mod:`beartype`-specific forward reference proxies.
'''
