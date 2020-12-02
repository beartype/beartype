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
from beartype_test.unit.data.hint.data_hintmeta import NonPepHintMetadata
from beartype_test.unit.data.hint.nonpep.proposal import (
    _data_hintnonpep484,
)

# ....................{ TUPLES                            }....................
# Initialized by the _init() function below.
HINTS_NONPEP_META = []
'''
Tuple of **PEP-noncompliant type hint metadata** (i.e.,
:class:`NonPepHintMetadata` instances describing test-specific PEP-noncompliant
type hints with metadata leveraged by various testing scenarios).
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Submodule globals to be redefined below.
    global HINTS_NONPEP_META

    # Current submodule, obtained via the standard idiom. See also:
    #     https://stackoverflow.com/a/1676860/2809027
    CURRENT_SUBMODULE = sys.modules[__name__]

    # Tuple of all private submodules of this subpackage to be initialized.
    DATA_HINT_NONPEP_SUBMODULES = (
        _data_hintnonpep484,
    )

    # Initialize all private submodules of this subpackage.
    for data_hint_nonpep_submodule in DATA_HINT_NONPEP_SUBMODULES:
        data_hint_nonpep_submodule.add_data(CURRENT_SUBMODULE)

    # Assert these global to have been initialized by these private submodules.
    assert HINTS_NONPEP_META, 'Tuple global "HINTS_NONPEP_META" empty.'

    # Assert this global to contain only instances of its expected dataclass.
    assert (
        isinstance(hint_nonpep_meta, NonPepHintMetadata)
        for hint_nonpep_meta in HINTS_NONPEP_META
    ), (f'{repr(HINTS_NONPEP_META)} not iterable of '
        f'"NonPepHintMetadata" instances.')

    # Frozen sets defined *AFTER* initializing these private submodules and
    # thus the lower-level globals required by these sets.
    HINTS_NONPEP_META = tuple(HINTS_NONPEP_META)


# Initialize this submodule.
_init()
