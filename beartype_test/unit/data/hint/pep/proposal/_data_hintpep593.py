#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 593`_**-compliant type hint test data.**

.. _PEP 593:
    https://www.python.org/dev/peps/pep-0593
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype_test.unit.data.hint.data_hintmeta import (
    PepHintMetadata,
    PepHintPithSatisfiedMetadata,
    PepHintPithUnsatisfiedMetadata,
)
from typing import (
    Any,
    List,
    Optional,
    Union,
)

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 593`_**-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 593:
        https://www.python.org/dev/peps/pep-0593
    '''

    # If the active Python interpreter targets less than Python < 3.9, this
    # interpreter fails to support PEP 593. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_9:
        return
    # Else, the active Python interpreter targets at least Python >= 3.9 and
    # thus supports PEP 593.

    # Defer Python >= 3.9-specific imports.
    from typing import Annotated

    # ..................{ SETS                              }..................
    # Add PEP 593-specific deeply ignorable test type hints to that set global.
    data_module.HINTS_PEP_IGNORABLE_DEEP.update((
        # Annotated of shallowly ignorable type hints.
        Annotated[Any, int],
        Annotated[object, int],

        # Annotated of ignorable unions and optionals.
        Annotated[Union[Any, float, str,], int],
        Annotated[Optional[Any], int],

        # Unions and optionals of ignorable annotateds.
        Union[complex, int, Annotated[Any, int]],
        Optional[Annotated[object, int]],
    ))

    # Add PEP 593-specific invalid non-generic types to that set global.
    data_module.HINTS_PEP_INVALID_CLASS_NONGENERIC.update((
        # The "Annotated" class as is does *NOT* constitute a valid type hint.
        Annotated,
    ))

    # ..................{ TUPLES                            }..................
    # Add PEP 593-specific test type hints to this dictionary global.
    data_module.HINTS_PEP_META.extend((
        # ................{ ANNOTATED                         }................
        # Hashable annotated of a non-"typing" type annotated by an arbitrary
        # hashable object.
        PepHintMetadata(
            hint=Annotated[str, int],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # String constant.
                PepHintPithSatisfiedMetadata(
                    'Towards a timely, wines‐enticing gate'),
            ),
            piths_unsatisfied_meta=(
                # List of string constants.
                PepHintPithUnsatisfiedMetadata([
                    'Of languished anger’s sap‐spated rushings',]),
            ),
        ),

        # Unhashable annotated of a non-"typing" type annotated by an
        # unhashable mutable container.
        PepHintMetadata(
            hint=Annotated[str, []],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # String constant.
                PepHintPithSatisfiedMetadata(
                    'Papally Ľust‐besmirched Merchet laws'),
            ),
            piths_unsatisfied_meta=(
                # List of string constants.
                PepHintPithUnsatisfiedMetadata([
                    "Of our ôver‐crowdedly cowed crowd's opinion‐",]),
            ),
        ),

        # Annotated of a "typing" type.
        PepHintMetadata(
            hint=Annotated[List[str], int],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # List of string constants.
                PepHintPithSatisfiedMetadata([
                    'MINERVA‐unnerving, verve‐sapping enervations',
                    'Of a magik-stoned Shinto rivery',
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Of a Spicily sated',),
            ),
        ),
    ))
