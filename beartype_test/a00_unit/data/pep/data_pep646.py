#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646` **data submodule.**

This submodule exercises :pep:`646` support for statement-level tuple and type
variable unpacking (e.g., ``*TypeVarTuple('Ts')``, ``*Tuple[int, str]``)
implemented in the :func:`beartype.beartype` decorator by declaring unit tests
exercising these aliases. For safety, these tests are intentionally isolated
from the main test suite. Notably, this low-level submodule implements the
higher-level ``test_decor_pep646()`` unit test in the main test suite.

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.11.0.** If this is *not* the case, importing this submodule raises an
:exc:`SyntaxError` exception.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import TypeVarTuple
from beartype._util.hint.pep.proposal.pep646692 import (
    make_hint_pep646_tuple_unpacked_prefix,
    make_hint_pep646_typevartuple_unpacked_prefix,
)

# ....................{ HINTS                              }....................
TUPLE_UNPACKED_EMPTY = make_hint_pep646_tuple_unpacked_prefix(())
'''
:pep:`646`-compliant unpacked child tuple hint subscripted by the empty tuple
(signifying zero child hints).
'''

# ....................{ TYPEARGS                           }....................
Ts = TypeVarTuple('Ts')
'''
Arbitrary :pep:`646`-compliant type variable tuple.
'''


Us = TypeVarTuple('Us')
'''
Arbitrary :pep:`646`-compliant type variable tuple.
'''

# ....................{ TYPEARGS ~ unpacked                }....................
Ts_unpacked = make_hint_pep646_typevartuple_unpacked_prefix(Ts)
'''
Arbitrary :pep:`646`-compliant unpacked type variable tuple of the form ``*Ts``.
'''


Us_unpacked = make_hint_pep646_typevartuple_unpacked_prefix(Us)
'''
Arbitrary :pep:`646`-compliant unpacked type variable tuple of the form ``*Ts``.
'''
