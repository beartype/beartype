#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`604`-compliant **type hint test data.**
'''

# ....................{ IMPORTS                            }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

# ....................{ ADDERS                             }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :pep:`604`-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # If the active Python interpreter targets Python < 3.11, this interpreter
    # fails to support PEP 675. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_11:
        return
    # Else, this interpreter supports PEP 675.

    # ..................{ IMPORTS                            }..................
    # Defer attribute-dependent imports.
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignLiteralString)
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from beartype.typing import LiteralString

    # ..................{ TUPLES                             }..................
    # Add PEP 675-specific test type hints to this tuple global.
    data_module.HINTS_PEP_META.extend((
        # ................{ PEP 675                            }................
        # Literal string type hint.
        HintPepMetadata(
            hint=LiteralString,
            pep_sign=HintSignLiteralString,
            piths_meta=(
                # Literal string statically defined from a literal string.
                HintPithSatisfiedMetadata(
                    'All overgrown with azure moss and flowers'),
                # Literal string dynamically defined from the concatenation of
                # multiple literal strings, inducing type inference in PEP 675.
                HintPithSatisfiedMetadata(
                    'So sweet, ' + 'the sense faints picturing them! ' + 'Thou'
                ),
                # Non-literal string dynamically defined from a literal integer.
                # Ideally, @beartype should reject this non-literal;
                # pragmatically, runtime type-checkers are incapable of doing
                # so in the general case. For example, str() could have been
                # shadowed by a user-defined function of the same name returning
                # a valid literal string.
                HintPithSatisfiedMetadata(str(0xFEEDFACE)),

                # Literal byte string.
                HintPithUnsatisfiedMetadata(
                    pith=b"For whose path the Atlantic's level powers",
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),
    ))
