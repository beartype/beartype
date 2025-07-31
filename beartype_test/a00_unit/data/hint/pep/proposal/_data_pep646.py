#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646`-compliant **type hint test data.**
'''

# ....................{ FIXTURES                           }....................
def hints_pep646_meta() -> 'List[HintPepMetadata]':
    '''
    List of :pep:`646`-compliant **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific :pep:`646`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = []

    # If the active Python interpreter targets Python < 3.11, this interpreter
    # fails to support PEP 646. In this case, return the empty list.
    if not IS_PYTHON_AT_LEAST_3_11:
        return hints_pep_meta
    # Else, the active Python interpreter targets Python >= 3.11 and thus
    # supports PEP 646.

    # ..................{ IMPORTS ~ version                  }..................
    # Defer version-specific imports.
    from beartype.typing import NewType
    from beartype._data.hint.sign.datahintsigns import (
        HintSignPep484585GenericSubbed,
    )
    from beartype_test.a00_unit.data.hint.pep.generic.data_pep646generic import (
        Array,
        DType,
        Shape,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ..................{ LOCALS                             }..................
    # PEP 484-compliant aliases defined by PEP 646's "Summary Examples" section.
    Height = NewType('Height', int)
    Width = NewType('Width', int)

    # ..................{ LISTS                              }..................
    # Add PEP 646-specific test type hints to this list.
    hints_pep_meta.extend((
        # ................{ GENERICS ~ multiple                }................
        # PEP 646-compliant generic subclassing the standard PEP 484-compliant
        # "typing.Generic" superclass parametrized by a PEP 484-compliant type
        # variable followed by a PEP 646-compliant unpacked type variable tuple
        # subscripted by one builtin type and two PEP 484-compliant aliases.
        #
        # This example derives from PEP 646's "Summary Examples" section.
        HintPepMetadata(
            hint=Array[float, Height, Width],
            pep_sign=HintSignPep484585GenericSubbed,
            generic_type=Array,
            is_type_typing=True,
            is_typing=False,
            piths_meta=(
                # Generic instance.
                HintPithSatisfiedMetadata(Array()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Or the familiar visiting of one'),
            ),
        ),
    ))

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta
