#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype `PEP 593`_**-compliant type hint data.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 593:
    https://www.python.org/dev/peps/pep-0593
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SETS ~ sign : supported           }....................
HINT_PEP593_SIGNS_SUPPORTED_DEEP = frozenset(
    (typing.Annotated,)  # type: ignore[attr-defined]
    if IS_PYTHON_AT_LEAST_3_9 else
    ()
)
'''
Frozen set of all `PEP 593`_-compliant **deeply supported signs** (i.e.,
arbitrary objects uniquely identifying `PEP 593`_-compliant type hints for
which the :func:`beartype.beartype` decorator generates deep type-checking
code).

.. _PEP 593:
    https://www.python.org/dev/peps/pep-0593
'''
