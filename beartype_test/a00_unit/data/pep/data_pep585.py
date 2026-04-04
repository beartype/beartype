#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`585` **type hints data submodule.**

This submodule mostly exists just to define arbitrary non-deprecated type hints
from module global scope. Since :pep:`585` itself deprecated most of :pep:`484`,
:pep:`585` type hints are likely to remain non-deprecated. Since they are also
the *only* type hints capable of subscripting builtin types, they require *no*
fragile imports. So, they serve as suitable arbitrary non-deprecated type hints.

Other higher-level data modules (e.g.,
:mod:`beartype_test.a00_unit.data.pep.pep484.forward.data_pep484ref_proxy`) then
create:

* :pep:`484`-compliant stringified forward reference type hints referring to the
  arbitrary non-deprecated type hints defined by this submodule.
* :mod:`beartype`-specific forward reference proxies encapsulating those
  :pep:`484`-compliant stringified forward reference type hints.

In short, madness. Layers of madness upon layers of madness.
'''

# ....................{ HINTS                              }....................
Pep585Hint = list[str]  # <-- *YOLO*
'''
Arbitrary :pep:`585`-compliant type hint.
'''
