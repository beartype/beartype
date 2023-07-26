#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`435`- and :pep:`663`-compliant **enumeration unit
tests**.

This submodule unit tests :pep:`435` and :pep:`663` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
def test_decor_pep435() -> None:
    '''
    Test :pep:`435` (i.e., :class:`enum.Enum`) support implemented in the
    :func:`beartype.beartype` decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from enum import (
        Enum,
        auto,
    )

    # ....................{ ENUMERATIONS                   }....................
    # Assert that @beartype properly decorates PEP 435-compliant enumerations.

    @beartype
    class BreathedOverHisDarkFate(Enum):
        '''
        Arbitrary :obj:`enum.auto`-based enumeration decorated by the
        :func:`beartype.beartype` decorator.
        '''

        one_melodious_sigh = auto()
        he_lived_he_died_he_sung_in_solitude = auto()


    @beartype
    class StrangersHaveWeptToHear(str, Enum):
        '''
        Arbitrary string-based enumeration decorated by the
        :func:`beartype.beartype` decorator.

        Note that this type intentionally subclasses the immutable :class:`str`
        type -- exercising an edge case in decoration of immutable types.
        '''

        his_passionate_notes = 'And virgins'
        as_unknown_he_passed = 'have pined'


@skip_if_python_version_less_than('3.11.0')
def test_decor_pep663() -> None:
    '''
    Test :pep:`663` (i.e., :class:`enum.StrEnum`) support implemented in the
    :func:`beartype.beartype` decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from enum import StrEnum

    # ....................{ ENUMERATIONS                   }....................
    # Assert that @beartype properly decorates PEP 663-compliant enumerations.

    @beartype
    class AndWastedForFondLove(StrEnum):
        '''
        Arbitrary string-based enumeration decorated by the
        :func:`beartype.beartype` decorator.

        Note that this enumeration intentionally subclasses the immutable
        :class:`.StrEnum` superclass -- exercising an edge case in decoration of
        immutable types.
        '''

        of_his_wild_eyes = 'The fire of'
        those_soft_orbs = 'has ceased to burn,'
