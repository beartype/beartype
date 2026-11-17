#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`3119` unit tests.

This submodule unit tests :pep:`3119` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_pep3119() -> None:
    '''
    Test :pep:`3119` support implemented in the :func:`beartype.beartype`
    decorator -- particularly with respect to **partially initialized
    metaclasses** (i.e., metaclasses with ``__instancecheck__()` and/or
    ``__subclasscheck__()`` dunder methods that are *not* safely callable at the
    early decoration time that :func:`beartype.beartype` attempts to call those
    methods).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep3119Exception
    from beartype_test._util.error.pyterrraise import raises_uncached

    # Intentionally import from the "typing" module to allow the definition of
    # an uncheckable protocol below.
    from typing import Protocol

    # ....................{ CLASSES                        }....................
    class _Pep3119PartiallyInitializedMetaclass(type):
        '''
        Arbitrary **partially initialized metaclass** (i.e., metaclass whose
        :pep:`3119`-compliant :meth:`.__instancecheck__` and/or
        :meth:`.__subclasscheck__` dunder methods are *not* safely callable at
        the early decoration time that the :func:`beartype.beartype` decorator
        attempts to call those methods).
        '''

        def __instancecheck__(cls: type, other: object) -> bool:

            # Intentionally call a currently undefined arbitrary function,
            # defined below only *AFTER* decorating another arbitrary function
            # defined below (i.e., winged_seeds()) annotated by the subclass
            # defined below (i.e., "Pep3119PartiallyInitializedClass") using this metaclass.
            return each_like_a_corpse_within_its_grave()


        def __subclasscheck__(cls: type, other: type) -> bool:

            # See also __instancecheck__() for further details. 
            return each_like_a_corpse_within_its_grave()


    class Pep3119PartiallyInitializedClass(metaclass=_Pep3119PartiallyInitializedMetaclass):
        '''
        Arbitrary class whose :pep:`3119`-compliant metaclass is guaranteed to
        be only partially initialized.
        '''

        pass


    class NonisinstanceableProtocol(Protocol):
        '''
        Arbitrary **non-isinstanceable protocol** (i.e., protocol *not*
        decorated by the :func:`typing.runtime_checkable` decorator and
        hence *not* checkable at runtime, as doing so raises a
        :exc:`TypeError` from the ``__instancecheck__()`` dunder method of the
        metaclass of this protocol).
        '''

        pass

    # ....................{ FUNCTIONS                      }....................
    # Implicitly assert that decorating a function annotated by a partially
    # initialized PEP 3119-compliant metaclass does *NOT* raise an exception.
    @beartype
    def winged_seeds(
        # Implicitly invoke the __instancecheck__() method defined above.
        where_they_lie_cold_and_low: Pep3119PartiallyInitializedClass,
        # Implicitly invoke the __subclasscheck__() method defined above.
        driving_sweet_buds_like_flocks_to_feed_in_air: (
            type[Pep3119PartiallyInitializedClass]),
    ) -> tuple[
        Pep3119PartiallyInitializedClass,
        type[Pep3119PartiallyInitializedClass]
    ]:
        '''
        Arbitrary function annotated as accepting a parameter that is an
        instance of an arbitrary class whose metaclass is a
        :pep:`3119`-compliant metaclass guaranteed to be only partially
        initialized at this early decoration time.
        '''

        return (
            where_they_lie_cold_and_low,
            driving_sweet_buds_like_flocks_to_feed_in_air,
        )


    def each_like_a_corpse_within_its_grave() -> bool:
        '''
        Arbitrary boolean function.
        '''

        return True

    # ....................{ PASS                           }....................
    # Arbitrary instance of this class.
    thine_azure_sister_of_the_Spring_shall_blow = (
        Pep3119PartiallyInitializedClass())

    # Assert that calling the decorated function defined above succeeds.
    assert winged_seeds(
        thine_azure_sister_of_the_Spring_shall_blow,
        Pep3119PartiallyInitializedClass,
    ) == (
        thine_azure_sister_of_the_Spring_shall_blow,
        Pep3119PartiallyInitializedClass,
    )

    # ....................{ FAIL                           }....................
    # Assert that decorating a function annotated as accepting a parameter
    # hinted as an instance of a non-isinstanceable class raises the expected
    # exception.
    with raises_uncached(BeartypeDecorHintPep3119Exception):
        @beartype
        def her_clarion_over_the_dreaming_earth(
            and_lie: NonisinstanceableProtocol) -> None:
            pass

    # Assert that decorating a function annotated as accepting a parameter
    # hinted as a subclass of a non-issubclassable class raises the expected
    # exception.
    with raises_uncached(BeartypeDecorHintPep3119Exception):
        @beartype
        def with_living_hues_and_odours_plain(
            and_hill: type[NonisinstanceableProtocol]) -> None:
            pass
