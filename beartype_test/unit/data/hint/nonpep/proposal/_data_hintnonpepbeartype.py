#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype-specific PEP-noncompliant type hint** (i.e., type hint supported
*only* by the :mod:`beartype.beartype` decorator) test data.

Beartype-specific PEP-noncompliant type hints include:

* **Tuple unions** (i.e., tuples containing *only* standard classes and
  forward references to standard classes).
'''

# ....................{ IMPORTS                           }....................
from beartype_test.unit.data.hint.data_hintmeta import (
    NonPepHintMetadata,
    PepHintPithSatisfiedMetadata,
    PepHintPithUnsatisfiedMetadata,
)

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add beartype-specific PEP-noncompliant type hint test data to various
    global containers declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # ..................{ TUPLES                            }..................
    # Add beartype-specific PEP-noncompliant test type hints to this dictionary
    # global.
    data_module.HINTS_NONPEP_META.extend((
        # ................{ TUPLE UNION                       }................
        # Tuple union of one standard class.
        NonPepHintMetadata(
            hint=(str,),
            piths_satisfied_meta=(
                # String constant.
                PepHintPithSatisfiedMetadata('Pinioned coin tokens'),
            ),
            piths_unsatisfied_meta=(
                # Byte-string constant.
                PepHintPithUnsatisfiedMetadata(
                    pith=b'Murkily',
                    # Match that the exception message raised for this pith
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this pith
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # Tuple union of two or more standard classes.
        NonPepHintMetadata(
            hint=(int, str),
            piths_satisfied_meta=(
                # Integer constant.
                PepHintPithSatisfiedMetadata(12),
                # String constant.
                PepHintPithSatisfiedMetadata('Smirk‐opined — openly'),
            ),
            piths_unsatisfied_meta=(
                # Byte-string constant.
                PepHintPithUnsatisfiedMetadata(
                    pith=b'Betokening',
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bint\b',
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

        # ................{ TYPE                              }................
        # Builtin type.
        NonPepHintMetadata(
            hint=str,
            piths_satisfied_meta=(
                # String constant.
                PepHintPithSatisfiedMetadata('Glassily lassitudinal bȴood-'),
            ),
            piths_unsatisfied_meta=(
                # Byte-string constant.
                PepHintPithUnsatisfiedMetadata(
                    pith=b'Stains, disdain-fully ("...up-stairs!"),',
                    # Match that the exception message raised for this pith
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this pith
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),
    ))
