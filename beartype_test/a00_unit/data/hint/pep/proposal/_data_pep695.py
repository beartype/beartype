#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant **type hint test data.**
'''

# ....................{ FIXTURES                           }....................
def hints_pep695_meta() -> 'List[HintPepMetadata]':
    '''
    Session-scoped fixture returning a list of :pep:`695`-compliant **type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific :pep:`695`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignList,
        HintSignUnion,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ..................{ LOCALS                             }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = []

    # ..................{ TUPLES                             }..................
    # If the active Python interpreter targets Python >= 3.12, this interpreter
    # supports PEP 695. In this case...
    if IS_PYTHON_AT_LEAST_3_12:
        #FIXME: Populate us up, please.
        # Add PEP 695-specific test type hints to this tuple global.
        hints_pep_meta.extend(())
    # Else, this interpreter supports PEP 695. In this case, return the empty
    # list.

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta
