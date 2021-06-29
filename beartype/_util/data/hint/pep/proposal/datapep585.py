#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype :pep:`585`**-compliant type hint data.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype._util.utilobject import Iota

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                             }....................
HINT_PEP585_TUPLE_EMPTY = (
    tuple[()] if IS_PYTHON_AT_LEAST_3_9 else Iota())  # type: ignore[misc]
'''
:pep:`585`-compliant empty fixed-length tuple type hint if the active Python
interpreter supports at least Python 3.9 and thus :pep:`585` *or* a unique
placeholder object otherwise to guarantee failure when comparing arbitrary
objects against this object via equality tests.
'''
