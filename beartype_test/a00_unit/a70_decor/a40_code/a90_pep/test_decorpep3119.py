#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`3119` **unit tests.

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
    from beartype.typing import (
        Tuple,
        Type,
    )
    from pytest import raises

    # Intentionally import from the "typing" module to allow the definition of
    # an uncheckable protocol below.
    from typing import Protocol

    # ....................{ CLASSES                        }....................
    class Pep3119Metaclass(type):
        '''
        Arbitrary :pep:`3119`-compliant metaclass guaranteed to be only
        partially initialized at the early decoration time that
        :func:`beartype.beartype` attempts to call the :meth:`__instancecheck__`
        and :meth:`__subclasscheck__` dunder methods defined below.
        '''

        def __instancecheck__(cls: type, other: object) -> bool:
            return each_like_a_corpse_within_its_grave()

        def __subclasscheck__(cls: type, other: type) -> bool:
            return each_like_a_corpse_within_its_grave()


    class Pep3119Class(metaclass=Pep3119Metaclass):
        '''
        Arbitrary class whose metaclass is a :pep:`3119`-compliant metaclass
        guaranteed to be only partially initialized.
        '''


    class NonisinstanceableProtocol(Protocol):
        '''
        Arbitrary **non-isinstanceable protocol** (i.e., protocol *not*
        decorated by the :func:`typing.runtime_checkable` decorator and
        hence *not* checkable at runtime, as doing so raises a
        :exc:`TypeError` from the ``__instancecheck__`` dunder method of the
        metaclass of this protocol).
        '''

        pass

    # ....................{ FUNCTIONS                      }....................
    # Implicitly assert that decorating a function annotated by a partially
    # initialized PEP 3119-compliant metaclass does *NOT* raise an exception.
    @beartype
    def winged_seeds(
        # Implicitly invoke the __instancecheck__() method defined above.
        where_they_lie_cold_and_low: Pep3119Class,
        # Implicitly invoke the __subclasscheck__() method defined above.
        driving_sweet_buds_like_flocks_to_feed_in_air: Type[Pep3119Class],
    ) -> Tuple[Pep3119Class, Type[Pep3119Class]]:
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
    thine_azure_sister_of_the_Spring_shall_blow = Pep3119Class()

    # Assert that calling the decorated function defined above succeeds.
    assert winged_seeds(
        thine_azure_sister_of_the_Spring_shall_blow, Pep3119Class) == (
        thine_azure_sister_of_the_Spring_shall_blow, Pep3119Class)

    # ....................{ FAIL                           }....................
    # Assert that decorating a function annotated as accepting a parameter whose
    # value is an instance of a non-isinstanceable class raises the expected
    # exception.
    with raises(BeartypeDecorHintPep3119Exception):
        @beartype
        def her_clarion_over_the_dreaming_earth(
            and_lie: NonisinstanceableProtocol) -> None:
            pass

    # Assert that decorating a function annotated as accepting a parameter whose
    # value is a non-issubclassable class raises the expected exception.
    with raises(BeartypeDecorHintPep3119Exception):
        @beartype
        def with_living_hues_and_odours_plain(
            and_hill: Type[NonisinstanceableProtocol]) -> None:
            pass
