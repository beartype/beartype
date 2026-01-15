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
def hints_nonpep_api_threading_meta() -> (
    'list[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintNonpepMetadata]'):
    '''
    List of PEP-noncompliant :mod:`threading` **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintNonpepMetadata`
    instances describing test-specific sample type hints originating in the
    standard :mod:`threading` module with metadata generically leveraged by
    various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta import (
        HintNonpepMetadata,
        PithSatisfiedMetadata,
        PithUnsatisfiedMetadata,
    )
    from threading import (
        Lock,
        RLock,
    )

    # ..................{ LISTS                              }..................
    # List of all PEP-noncompliant type hint metadata to be returned.
    hints_nonpep_meta = [
        # "threading.Lock" attribute, which:
        # * Under Python >= 3.13 is a valid type and thus valid type hint.
        # * Under Python <= 3.12 is a factory function and thus invalid type
        #   hint. Since this attribute is conditionally valid as a hint under
        #   Python >= 3.13, @beartype unconditionally supports this attribute as
        #   a valid hint under *ALL* Python versions for generality.
        HintNonpepMetadata(
            hint=Lock,
            piths_meta=(
                # Arbitrary non-reentrant lock.
                PithSatisfiedMetadata(pith=Lock(), is_context_manager=True),
                # String constant.
                PithUnsatisfiedMetadata(
                    pith='Hubbub increases more they call out "Hush!"'),
            ),
        ),

        # "threading.RLock" attribute, which behaves similarly to the comparable
        # "threading.Lock" attribute documented above.
        HintNonpepMetadata(
            hint=RLock,
            piths_meta=(
                # Arbitrary reentrant lock.
                PithSatisfiedMetadata(pith=RLock(), is_context_manager=True),
                # String constant.
                PithUnsatisfiedMetadata(
                    pith="So at Hyperion's words the Phantoms pale"),
            ),
        ),
    ]

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-noncompliant type hint metadata.
    return hints_nonpep_meta
