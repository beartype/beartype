#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant PEP-noncompliant type hint test data.

:pep:`695`-compliant type hints *mostly* indistinguishable from
PEP-noncompliant type hints include:

* :func:`typing.TypeAliasType`, the C-based type of all :pep:`695`-compliant
  type aliases and itself a valid type hint.
'''

# ....................{ FIXTURES                           }....................
def hints_nonpep695_meta() -> 'List[HintNonpepMetadata]':
    '''
    List of :pep:`695`-sorta-compliant **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintNonpepMetadata`
    instances describing test-specific :pep:`695`-sorta-compliant sample type
    hints with metadata generically leveraged by various PEP-agnostic unit
    tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta import (
        HintNonpepMetadata,
        PithSatisfiedMetadata,
        PithUnsatisfiedMetadata,
    )

    # List of all PEP-noncompliant type hint metadata to be returned.
    hints_nonpep_meta = []

    # If the active Python interpreter targets Python < 3.12, this interpreter
    # fails to support PEP 695. In this case, return the empty list.
    if not IS_PYTHON_AT_LEAST_3_12:
        return hints_nonpep_meta
    # Else, the active Python interpreter targets Python >= 3.12 and thus
    # supports PEP 695.

    # ..................{ LISTS                              }..................
    # Defer version-specific imports.
    from beartype._cave._cavefast import HintPep695TypeAlias
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasSimple)

    # Add PEP 695-specific (albeit technically PEP-noncompliant from the
    # beartype perspective) test type hints to this list.
    hints_nonpep_meta.extend((
        # Unsubscripted "typing.TypeAliasType" type of *ALL* PEP 695-compliant
        # type aliases. This type is a valid type and thus a valid hint, despite
        # defining a PEP-noncompliant "__parameters__" dunder attribute.
        HintNonpepMetadata(
            hint=HintPep695TypeAlias,
            piths_meta=(
                # Arbitrary PEP 695-compliant type alias.
                PithSatisfiedMetadata(AliasSimple),
                # String constant.
                PithUnsatisfiedMetadata(
                    pith='And diamond-paved lustrous long arcades,',
                    # Match that the exception message raised for this pith
                    # contains...
                    exception_str_match_regexes=(
                        # The type *NOT* satisfied by this object.
                        r'\btyping\.TypeAliasType\b',
                    ),
                    # Match that the exception message raised for this pith does
                    # *NOT* contain...
                    exception_str_not_match_regexes=(
                        # A newline.
                        r'\n',
                        # A bullet delimiter.
                        r'\*',
                    ),
                ),
            ),
        ),
    ))

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-noncompliant type hint metadata.
    return hints_nonpep_meta
