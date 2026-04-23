#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`696`-compliant **type hint test data.**
'''

# ....................{ FIXTURES                           }....................
def hints_pep696_meta() -> 'list[HintPepMetadata]':
    '''
    List of :pep:`696`-compliant **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.metadata.pith.data_hintpithmeta.HintPepMetadata`
    instances describing test-specific :pep:`696`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_13

    # List of all PEP-specific type hint metadata to be returned.
    hints_piths_pep_meta = []

    # If the active Python interpreter targets Python < 3.13, this interpreter
    # fails to support PEP 696. In this case, return the empty list.
    if not IS_PYTHON_AT_LEAST_3_13:
        return hints_piths_pep_meta
    # Else, the active Python interpreter targets Python >= 3.13 and thus
    # supports PEP 696.

    # ..................{ IMPORTS ~ version                  }..................
    # Defer version-specific imports.
    from beartype.door import TypeVarTypeHint
    from beartype._data.hint.sign.datahintsigns import HintSignTypeVar
    from beartype_test.a00_unit.data.hint.metadata.pith.data_hintmeta import (
        HintPepMetadata)
    from beartype_test.a00_unit.data.hint.metadata.pith.data_pithmeta import (
        PithSatisfiedMetadata,
        PithUnsatisfiedMetadata,
    )
    from typing import TypeVar

    # ..................{ LOCALS                             }..................
    T_list_str = TypeVar('T_list_str', default=list[str])
    '''
    '''

    # ..................{ LISTS                              }..................
    # Add PEP 696-specific test type hints to this list.
    hints_piths_pep_meta.extend((
        # ................{ PEP 484 ~ typevar                  }................
        # PEP 484-compliant user-defined defaulted type variable.
        HintPepMetadata(
            hint=T_list_str,
            pep_sign=HintSignTypeVar,
            typehint_cls=TypeVarTypeHint,
            is_typing=False,
            piths_meta=(
                # List of string constants.
                PithSatisfiedMetadata(
                    ["And touch'd", 'with shade of', 'bronzed obelisks,',]),
                # String constant.
                PithUnsatisfiedMetadata(
                    "Glar'd a blood-red through all its thousand courts,"),
            ),
        ),
    ))

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_piths_pep_meta
