#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :pep:`484`-compliant **type variable** (i.e.,
:class:`typing.TypeVar`) unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to :pep:`484`-compliant type variables.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ hint : typevar             }....................
def test_decor_pep484_hint_typevar_cacheunworthy() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on distinct callables annotated
    by **ambiguous type variables** (i.e., distinct type variables bound to
    different types that nonetheless ambiguously share the same names and thus
    the same machine-readable representations), validating that
    :func:`beartype.beartype` correctly preserves type variables as is rather
    than attempting to deduplicate type variables.

    See Also
    --------
    https://github.com/beartype/beartype/issues/458
        Issue exercised by this unit test.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype.typing import (
        Tuple,
        TypeVar,
    )
    from pytest import raises

    # ..................{ CLASSES ~ 1                        }..................
    # First arbitrary class hierarchy.
    class TheDimAndHornedMoonHungLow(object):
        '''
        Arbitrary superclass.
        '''

        pass


    class AndPoured(TheDimAndHornedMoonHungLow):
        '''
        Arbitrary subclass.
        '''

        pass

    # ..................{ CLASSES ~ 2                        }..................
    # Second arbitrary class hierarchy.
    class ASeaOfLustre(object):
        '''
        Arbitrary superclass.
        '''

        pass


    class OnTheHorizonsVerge(ASeaOfLustre):
        '''
        Arbitrary subclass.
        '''

        pass

    # ..................{ LOCALS                             }..................
    # Type variables bound to the above superclasses, intentionally given
    # ambiguous names so as to possibly provoke worst-case behaviour from the
    # @beartype decorator.
    T_TheDimAndHornedMoonHungLow = TypeVar('T', bound=TheDimAndHornedMoonHungLow)
    U_TheDimAndHornedMoonHungLow = TypeVar('U', bound=TheDimAndHornedMoonHungLow)
    T_ASeaOfLustre = TypeVar('T', bound=ASeaOfLustre)
    U_ASeaOfLustre = TypeVar('U', bound=ASeaOfLustre)

    # Type hints parametrized by these type variables.
    Tuple_TheDimAndHornedMoonHungLow = Tuple[
        T_TheDimAndHornedMoonHungLow,
        U_TheDimAndHornedMoonHungLow
    ]
    Tuple_ASeaOfLustre = Tuple[
        T_ASeaOfLustre,
        U_ASeaOfLustre
    ]

    # Arbitrary instances of the above subclasses.
    and_poured = AndPoured()
    on_the_horizons_verge = OnTheHorizonsVerge()

    # 2-tuples intentionally referencing these instances twice.
    tuple_and_poured = (and_poured, and_poured)
    tuple_on_the_horizons_verge = (on_the_horizons_verge, on_the_horizons_verge)

    # ..................{ CALLABLES                          }..................
    @beartype
    def that_overflowed_its_mountains(
        yellow_mist: Tuple_TheDimAndHornedMoonHungLow) -> (
        Tuple_TheDimAndHornedMoonHungLow):
        '''
        Arbitrary callable annotated by type hints defined above.
        '''

        return yellow_mist


    @beartype
    def filled_the_unbounded_atmosphere(
        and_drank: Tuple_ASeaOfLustre) -> (
        Tuple_ASeaOfLustre):
        '''
        Arbitrary callable annotated by type hints defined above.
        '''

        return and_drank

    # ..................{ PASS                               }..................
    # Assert these callables succeed when passed objects satisfying the bounds
    # of the type variables annotating these callables.
    assert that_overflowed_its_mountains(tuple_and_poured) is tuple_and_poured
    assert filled_the_unbounded_atmosphere(tuple_on_the_horizons_verge) is (
        tuple_on_the_horizons_verge)

    # ..................{ FAIL                               }..................
    # Assert these callables fail when passed objects violating the bounds
    # of the type variables annotating these callables.
    with raises(BeartypeCallHintParamViolation):
        that_overflowed_its_mountains(tuple_on_the_horizons_verge)
    with raises(BeartypeCallHintParamViolation):
        filled_the_unbounded_atmosphere(tuple_and_poured)
