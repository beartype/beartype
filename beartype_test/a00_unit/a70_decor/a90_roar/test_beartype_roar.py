#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator exception unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to exceptions raised by the :mod:`beartype._decor.error.errormain` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ decorator                  }....................
def test_beartypecallhintviolation() -> None:
    '''
    Test the :func:`beartype.beartype` decorator with respect to **type-checking
    violations** (i.e., :exc:`beartype.roar.BeartypeCallHintViolation`
    exceptions raised by callables decorated by that decorator).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintViolation
    from beartype.typing import List
    from pytest import raises

    # ....................{ ASSERTS ~ strong ref           }....................
    class SpiritBearIGiveYouSalmonToGoAway(object):
        '''
        Arbitrary user-defined class.
        '''

        pass

    class SpiritBearIGiftYouHoneyNotToStay(object):
        '''
        Arbitrary user-defined class.
        '''

        pass

    # Arbitrary object guaranteed to *NOT* be an instance of this class.
    #
    # Since CPython permits weak references to almost all instances of
    # user-defined classes (including both the above class and the "object"
    # superclass), this object exhibits the expected behaviour from the
    # "culprits" API exercised below that depends upon weak references.
    SPIRIT_BEAR_REFUSE_TO_GO_AWAY = SpiritBearIGiftYouHoneyNotToStay()

    @beartype
    def when_spirit_bear_hibernates_in_your_bed(
        best_bear_den: SpiritBearIGiveYouSalmonToGoAway) -> None:
        '''
        Arbitrary function decorated by :func:`beartype.beartype` annotated by a
        type hint inducing edge-case behaviour in type-checking violations
        raised by this callable.
        '''

        pass

    # Assert that calling this function with a parameter violating its type hint
    # raises the expected exception.
    with raises(BeartypeCallHintViolation) as exception_info:
        when_spirit_bear_hibernates_in_your_bed(SPIRIT_BEAR_REFUSE_TO_GO_AWAY)

    # Exception captured by the prior call to this wrapper function.
    exception = exception_info.value

    # Assert that exactly one culprit was responsible for this exception.
    assert len(exception.culprits) == 1

    # Culprit of this exception.
    culprit = exception.culprits[0]

    # Assert that this culprit is the same object passed to this function.
    assert culprit is SPIRIT_BEAR_REFUSE_TO_GO_AWAY

    # ....................{ ASSERTS ~ weak ref             }....................
    # List of lists of byte strings violating type hints annotating the
    # we_are_all_spirit_bear() function defined below.
    #
    # Since CPython prohibits weak references to both lists *AND* byte strings,
    # this data structure exhibits known flaws in the "culprits" API exercised
    # below that depends upon weak references.
    YOU_WENT_THERE_SPIRIT_BEAR = (
        b'Why do you sleep in my pinball room, Spirit Bear?')
    DO_NOT_GO_THERE_SPIRIT_BEAR = [[YOU_WENT_THERE_SPIRIT_BEAR]]

    @beartype
    def we_are_all_spirit_bear(
        best_bear_dens: List[List[str]]) -> None:
        '''
        Arbitrary function decorated by :func:`beartype.beartype` annotated by a
        type hint inducing edge-case behaviour in type-checking violations
        raised by this callable.
        '''

        pass

    # Assert that calling this function with a parameter violating its type hint
    # raises the expected exception.
    with raises(BeartypeCallHintViolation) as exception_info:
        we_are_all_spirit_bear(DO_NOT_GO_THERE_SPIRIT_BEAR)

    # Exception captured by the prior call to this wrapper function.
    exception = exception_info.value

    # Assert that exactly two culprits were responsible for this exception.
    assert len(exception.culprits) == 2

    # Root and leaf culprits of this exception.
    root_culprit = exception.culprits[0]
    leaf_culprit = exception.culprits[1]

    # Assert that both of these culprits are the machine-readable
    # representations of their underlying objects rather than those objects.
    # Why? Because CPython prohibits weak references to those objects. *sigh*
    assert isinstance(root_culprit, str)
    assert isinstance(leaf_culprit, str)
    assert root_culprit == repr(DO_NOT_GO_THERE_SPIRIT_BEAR)
    assert leaf_culprit == repr(YOU_WENT_THERE_SPIRIT_BEAR)
