#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`649`-compliant **data factories** (i.e., low-level callables
creating and returning lists of :pep:`649`-compliant type hints, exercising edge
cases in unit tests requiring these fixtures).
'''

# ....................{ FIXTURES                           }....................
def hints_pep649_meta() -> 'List[HintPepMetadata]':
    '''
    List of :pep:`649`-compliant **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific :pep:`649`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype.typing import ForwardRef
    from beartype._data.hint.pep.sign.datapepsigns import HintSignForwardRef
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_MOST_3_13
    from beartype_test.a00_unit.data.data_type import Subclass
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ....................{ CONSTANTS ~ forwardref         }....................
    # Fully-qualified classname of an arbitrary class guaranteed to be
    # importable.
    _FORWARDREF_CLASSNAME = 'beartype_test.a00_unit.data.data_type.Subclass'

    # Arbitrary class referred to by "FORWARDREF_CLASSNAME".
    _FORWARDREF_CLASSNAME_TYPE = Subclass

    # ..................{ LISTS                              }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = [
        # ................{ FORWARDREF                         }................
        # Forward references defined below are *ONLY* intended to shallowly
        # exercise support for types of forward references across the codebase;
        # they are *NOT* intended to deeply exercise resolution of forward
        # references to undeclared classes, which requires more finesse.
        #
        # See the "data_hintref" submodule for the latter.

        # PEP 484-compliant forward reference specified as a fully-qualified
        # classname.
        HintPepMetadata(
            hint=_FORWARDREF_CLASSNAME,
            pep_sign=HintSignForwardRef,
            is_type_typing=False,
            piths_meta=(
                # Instance of the class referred to by this reference.
                HintPithSatisfiedMetadata(_FORWARDREF_CLASSNAME_TYPE()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Empirical Ṗath after‐mathematically harvesting agro‐'),
            ),
        ),

        # PEP 649-compliant forward reference encapsulated by a forward
        # reference proxy published by the "annotationlib" module.
        HintPepMetadata(
            hint=ForwardRef(_FORWARDREF_CLASSNAME),
            pep_sign=HintSignForwardRef,
            # The module defining the "ForwardRef" type differs depending on
            # Python version. Specifically:
            # * If the active Python interpreter targets Python >= 3.14, the
            #   canonical definition resides at "annotationlib.ForwardRef".
            # * If the active Python interpreter targets Python <= 3.13, the
            #   canonical definition resides at "typing.ForwardRef".
            is_type_typing=IS_PYTHON_AT_MOST_3_13,
            piths_meta=(
                # Instance of the class referred to by this reference.
                HintPithSatisfiedMetadata(_FORWARDREF_CLASSNAME_TYPE()),
                # String constant.
                HintPithUnsatisfiedMetadata('Silvicultures of'),
            ),
        ),
    ]

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta
