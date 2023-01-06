#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype protocol hierarchy** (i.e., public :pep:`544`-compliant protocols
enabling users to extend :mod:`beartype` with custom runtime behaviours).

Most of the public attributes defined by this private submodule are explicitly
exported to external users in our top-level :mod:`beartype.__init__` submodule.
This private submodule is *not* intended for direct importation by downstream
callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    Protocol,
)

# ....................{ PROTOCOLS                          }....................
#FIXME: Docstring us up, please.
#FIXME: Unit test us up, please.
def BeartypeHintable(Protocol):
    '''
    '''

    @classmethod
    def __beartype_hint__(cls) -> Any:
        '''
        **Beartype type hint transform** (i.e., :mod:`beartype-specific
        dunder class method returning a new PEP-compliant type hint
        constraining this class with additional runtime type-checking).
        '''

        pass
