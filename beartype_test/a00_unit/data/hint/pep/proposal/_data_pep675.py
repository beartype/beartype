#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`675`-compliant **type hint test data.**
'''

# ....................{ FIXTURES                           }....................
def hints_pep675_meta() -> 'List[HintPepMetadata]':
    '''
    Session-scoped fixture returning a list of :pep:`675`-compliant **type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific :pep:`675`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignLiteralString)
    from beartype._util.api.standard.utiltyping import get_typing_attrs
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ..................{ LOCALS                             }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = []

    # ..................{ FACTORIES                          }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module...
    for LiteralString in get_typing_attrs('LiteralString'):
        # ..................{ LISTS                          }..................
        # Add PEP-specific type hint metadata to this list.
        hints_pep_meta.extend((
            # ................{ PEP 675                        }................
            # Literal string type hint.
            HintPepMetadata(
                hint=LiteralString,
                pep_sign=HintSignLiteralString,
                piths_meta=(
                    # Literal string statically defined from a literal string.
                    HintPithSatisfiedMetadata(
                        'All overgrown with azure moss and flowers'),
                    # Literal string dynamically defined from the concatenation
                    # of multiple literal strings, inducing type inference in
                    # PEP 675.
                    HintPithSatisfiedMetadata(
                        'So sweet, ' + 'the sense faints picturing them! ' + 'Thou'
                    ),
                    # Non-literal string dynamically defined from a literal
                    # integer. Ideally, @beartype should reject this
                    # non-literal; pragmatically, runtime type-checkers are
                    # incapable of doing so in the general case. For example,
                    # str() could have been shadowed by a user-defined function
                    # of the same name returning a valid literal string.
                    HintPithSatisfiedMetadata(str(0xFEEDFACE)),

                    # Literal byte string.
                    HintPithUnsatisfiedMetadata(
                        pith=b"For whose path the Atlantic's level powers",
                        # Match that the exception message raised for this
                        # object declares the types *NOT* satisfied by this
                        # object.
                        exception_str_match_regexes=(
                            r'\bstr\b',
                        ),
                        # Match that the exception message raised for this
                        # object does *NOT* contain a newline or bullet
                        # delimiter.
                        exception_str_not_match_regexes=(
                            r'\n',
                            r'\*',
                        ),
                    ),
                ),
            ),
        ))

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta
