#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type hint data.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
from typing import Tuple

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                             }....................
HINT_PEP484_TUPLE_EMPTY = Tuple[()]
'''
:pep:`484`-compliant empty fixed-length tuple type hint.
'''

# ....................{ BASES                             }....................
# Conditionally add the "typing.ForwardRef" superclass depending on the
# current Python version, as this superclass was thankfully publicized
# under Python >= 3.7 after its initial privatization under Python <= 3.6.
HINT_PEP484_TYPE_FORWARDREF = (
    typing.ForwardRef if IS_PYTHON_AT_LEAST_3_7 else
    typing._ForwardRef  # type: ignore [attr-defined]
)
'''
**Forward reference sign** (i.e., arbitrary objects uniquely identifying a
:pep:`484`-compliant type hint unifying one or more subscripted type hint
arguments into a disjunctive set union of these arguments).
'''
