#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint globals** (i.e., constant global variables
concerning PEP-agnostic type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.hint.data.pep.utilhintdatapep import (
    HINT_PEP_SIGNS_IGNORABLE,
)
from beartype._util.hint.data.pep.proposal.utilhintdatapep484 import (
    HINT_PEP484_TYPE_FORWARDREF,
)

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


HINTS_IGNORABLE_SHALLOW = HINT_PEP_SIGNS_IGNORABLE | {
    # The PEP-noncompliant builtin "object" type is the transitive superclass
    # of all classes, parameters and return values annotated as "object"
    # unconditionally match *ALL* objects under isinstance()-based type
    # covariance and thus semantically reduce to unannotated parameters and
    # return values. This is literally the "beartype.cave.AnyType" type.
    object,
}
'''
Frozen set of all **shallowly ignorable type hints** (i.e., annotations
unconditionally ignored by the :func:`beartype.beartype` decorator).

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
'''
