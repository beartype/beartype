#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hints test data.**

This submodule predefines low-level global constants whose values are
PEP-noncompliant type hints, exercising known edge cases on behalf of
higher-level unit test submodules.
'''

# ....................{ TUPLES                            }....................
# Initialized by the _init() function below.
HINTS_NONPEP_META = []
'''
Tuple of **PEP-noncompliant type hint metadata** (i.e.,
:class:`HintNonpepMetadata` instances describing test-specific PEP-noncompliant
type hints with metadata leveraged by various testing scenarios).
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer function-specific imports.
    import sys
    from beartype_test.a00_unit.data.hint.nonpep.beartype import (
        _data_nonpepbeartype,
    )
    from beartype_test.a00_unit.data.hint.nonpep.proposal import (
        _data_nonpep484,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintNonpepMetadata)

    # Submodule globals to be redefined below.
    global HINTS_NONPEP_META

    # Current submodule, obtained via the standard idiom. See also:
    #     https://stackoverflow.com/a/1676860/2809027
    CURRENT_SUBMODULE = sys.modules[__name__]

    # Tuple of all private submodules of this subpackage to be initialized.
    DATA_HINT_NONPEP_SUBMODULES = (
        _data_nonpep484,
        _data_nonpepbeartype,
    )

    # Initialize all private submodules of this subpackage.
    for data_hint_nonpep_submodule in DATA_HINT_NONPEP_SUBMODULES:
        data_hint_nonpep_submodule.add_data(CURRENT_SUBMODULE)

    # Assert these global to have been initialized by these private submodules.
    assert HINTS_NONPEP_META, 'Tuple global "HINTS_NONPEP_META" empty.'

    # Assert this global to contain only instances of its expected dataclass.
    assert (
        isinstance(hint_nonpep_meta, HintNonpepMetadata)
        for hint_nonpep_meta in HINTS_NONPEP_META
    ), (f'{repr(HINTS_NONPEP_META)} not iterable of '
        f'"HintNonpepMetadata" instances.')

    # Frozen sets defined *AFTER* initializing these private submodules and
    # thus the lower-level globals required by these sets.
    HINTS_NONPEP_META = tuple(HINTS_NONPEP_META)


# Initialize this submodule.
_init()
