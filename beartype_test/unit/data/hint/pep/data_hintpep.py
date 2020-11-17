#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hints test data.**

This submodule predefines low-level global constants whose values are
PEP-compliant type hints, exercising known edge cases on behalf of higher-level
unit test submodules.
'''

# ....................{ IMPORTS                           }....................
import sys
from beartype_test.unit.data.hint.pep.proposal import (
    data_hintpep484,
    _data_hintpep544,
    _data_hintpep593,
)

# ....................{ METADATA ~ dict : attr            }....................
# Initialized by the _init() function below.
HINT_PEP_TO_META = {}
'''
Dictionary mapping various PEP-compliant type hints to :class:`PepHintMetadata`
instances describing those hints with metadata applicable to testing scenarios.
'''


# Initialized by the _init() function below.
HINT_PEP_CLASSED_TO_META = {}
'''
Dictionary mapping various PEP-compliant type hints implemented by the
:mod:`typing` module as standard classes indistinguishable from
non-:mod:`typing` classes to :class:`PepHintNonsignedMetadata` instances
describing those hints with metadata applicable to testing scenarios.

These hints do *not* conform to standard expectations for PEP-compliant type
hints and must thus be segregated from those that do conform (which is most of
them) to avoid spurious issues throughout downstream unit tests. In particular,
these hints are *not* uniquely identified by unsubscripted :mod:`typing`
attributes.
'''

# ....................{ SETS                              }....................
# Initialized by the _init() function below.
HINTS_PEP = None
'''
Frozen set of PEP-compliant type hints exercising well-known edge cases.
'''


# Initialized by the _init() function below.
HINTS_PEP_IGNORABLE_DEEP = set()
'''
Frozen set of **deeply ignorable PEP-compliant type hints** (i.e.,
PEP-compliant type hints that are *not* shallowly ignorable and thus *not* in
the low-level
:attr:`beartype._util.hint.data.utilhintdata.HINTS_IGNORABLE_SHALLOW` set, but
which are nonetheless ignorable and thus require dynamic testing by the
high-level :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester
function to demonstrate this fact).
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Submodule globals to be redefined below.
    global \
        HINTS_PEP, \
        HINTS_PEP_IGNORABLE_DEEP

    # Current submodule, obtained via the standard idiom. See also:
    #     https://stackoverflow.com/a/1676860/2809027
    CURRENT_SUBMODULE = sys.modules[__name__]

    # Tuple of all private submodules of this subpackage to be initialized.
    DATA_HINT_PEP_SUBMODULES = (
        data_hintpep484,
        _data_hintpep544,
        _data_hintpep593,
    )

    # Initialize all private submodules of this subpackage.
    for data_hint_pep_submodule in DATA_HINT_PEP_SUBMODULES:
        data_hint_pep_submodule.add_data(CURRENT_SUBMODULE)

    # Assert these global to have been initialized by these private submodules.
    assert HINT_PEP_TO_META, 'Dictionary global "HINT_PEP_TO_META" empty.'
    assert HINTS_PEP_IGNORABLE_DEEP, (
        'Set global "HINTS_PEP_IGNORABLE_DEEP" empty.')

    # Frozen sets defined *AFTER* initializing these private submodules and
    # thus the lower-level globals required by these sets.
    HINTS_PEP = frozenset(HINT_PEP_TO_META.keys())
    HINTS_PEP_IGNORABLE_DEEP = frozenset(HINTS_PEP_IGNORABLE_DEEP)


# Initialize this submodule.
_init()
