#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant **data factories** (i.e., low-level callables
creating and returning lists of :pep:`557`-compliant type hints, exercising edge
cases in unit tests requiring these fixtures).
'''

# ....................{ FIXTURES ~ meta                    }....................
def hints_pep557_reduction_meta() -> (
    'list[beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta.HintReductionABC]'):
    '''
    List of :pep:`557`-compliant **type hint reduction metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta.HintReductionABC`
    instances describing test-specific :pep:`557`-compliant sample type hints
    with metadata generically leveraged by PEP-agnostic unit tests validating
    the :func:`beartype._check.convert.reduce.redmain.reduce_hint` function).
    '''

    # Defer fixture-specific imports.
    from beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta import (
        HintReductionValid)
    from dataclasses import InitVar

    # List of all PEP-specific type hint reduction metadata to be returned.
    hints_pep_reduction_meta = [
        # ..................{ INITVAR                        }..................
        # A PEP 557-compliant "InitVar" is reduced to its child hint.
        HintReductionValid(hint_unreduced=InitVar[str], hint_reduced=str),
    ]

    # Return this list.
    return hints_pep_reduction_meta
