#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint globals** (i.e., global constants
describing PEP-agnostic type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.hint.pep.proposal.utilpep484 import (
    HINT_PEP484_TYPE_FORWARDREF)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SETS                              }....................
HINT_BASES_FORWARDREF = (
    # Technically, the builtin "str" type is the superclass of *ONLY*
    # PEP-noncompliant fully-qualified forward references (e.g.,
    # "muh_submodule.MuhType") and PEP 585-compliant nested forward references
    # (e.g., "list['Typo']") since PEP 484-compliant nested forward references
    # (e.g., "List['Typo']") are instead internally coerced by the "typing"
    # module into instances of the "typing.ForwardRef" superclass. Nonetheless,
    # including "str" here unconditionally does no harm *AND* should improve
    # robustness and forward compatibility with spurious "typing" edge cases
    # (of which we currently unaware but which probably exist, because
    # "typing").
    str,

    # PEP 484-compliant forward reference superclass.
    HINT_PEP484_TYPE_FORWARDREF,
)
'''
Tuple of all **forward reference type hint superclasses** (i.e., superclasses
such that all type hints forward referencing user-defined types are instances
of these superclasses).
'''
