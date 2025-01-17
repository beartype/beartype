#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator exception unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to exceptions raised by the :mod:`beartype._check.error.errget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_violation_culprits() -> None:
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


def test_decor_violation_pickle() -> None:
    '''
    Test the :func:`beartype.beartype` decorator with respect to **type-checking
    violation pickling** (i.e., (de)serializing
    :exc:`beartype.roar.BeartypeCallHintViolation` exceptions raised by
    callables decorated by that decorator via the :mod:`pickle` module).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from pickle import dumps, loads
    from beartype.door import die_if_unbearable
    from beartype.roar import BeartypeDoorHintViolation

    # ....................{ CLASSES                        }....................
    class TheHorridTruth(object):
        '''
        Arbitrary user-defined type.

        Note that this unit test is deterministic *only* when the
        :func:`.die_if_unbearable` function is passed an instance of a
        user-defined types. When that function is instead passed a builtin
        scalar (e.g., string, integer), this unit test becomes
        non-deterministic. Why? Object interning, probably. For efficiency,
        Python **interns** (i.e., internalizes as globally cached objects)
        simple primitives like builtin scalars. How and when Python does so
        probably varies depending on contextual runtime features like the
        current platform, CPython compiler options and *whatevahs*.
        '''

        pass

    # Arbitrary instance of this type.
    the_awful_facts = TheHorridTruth()

    # ....................{ ASSERTS                        }....................
    # Trivially raise a type-checking violation.
    try:
        die_if_unbearable(the_awful_facts, int)
    except BeartypeDoorHintViolation as exception:
        # Pickled string embodying this exception's state.
        exception_dumped = dumps(exception)

        # Unpickled exception resembling the original exception.
        exception_loaded = loads(exception_dumped)

        # Assert that this unpickled exception is of the same type.
        assert isinstance(exception_loaded, BeartypeDoorHintViolation)

        # Assert that both the original *AND* unpickled exception provide the
        # expected number of culprits.
        assert len(exception.culprits) == 1
        assert len(exception_loaded.culprits) == 1

        # Assert that the unpickled exception stores *ONLY* the machine-readable 
        # representation of this culprit. Why? Because the weak reference to the
        # culprit stored by the original exception is *NOT* pickleable.
        assert repr(exception.culprits[0]) == exception_loaded.culprits[0]


def test_decor_violation_types() -> None:
    '''
    Test the
    :func:`beartype.beartype` decorator with respect to the
    :attr:`beartype.BeartypeConf.violation_param_type` and
    :attr:`beartype.BeartypeConf.violation_return_type` configuration
    parameters.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        beartype,
    )
    from beartype.typing import (
        List,
        Tuple,
        Union,
    )
    from pytest import (
        raises,
        warns,
    )

    # ..................{ CLASSES                            }..................
    class TheVacantWoods(Exception):
        '''
        Arbitrary exception subclass.
        '''

        pass


    class SpreadRoundHim(Exception):
        '''
        Arbitrary exception subclass.
        '''

        pass


    class LowInTheWest(UserWarning):
        '''
        Arbitrary warning subclass.
        '''

        pass


    class WhereHeStood(UserWarning):
        '''
        Arbitrary warning subclass.
        '''

        pass

    # ..................{ CALLABLES                          }..................
    def the_clear_and(
        garish_hills: List[str], the_distinct_valley) -> (
        Union[int, Tuple[str, ...]]):
        '''
        Arbitrary callable to be decorated by the :func:`beartype.beartype`
        decorator, configured in various ways below.
        '''

        return the_distinct_valley

    # Beartype decorator configured to raise different types of user-defined
    # exceptions on invalid parameters and returns.
    beartype_raise = beartype(conf=BeartypeConf(
        violation_param_type=TheVacantWoods,
        violation_return_type=SpreadRoundHim,
    ))

    # Beartype decorator configured to emit different types of user-defined
    # warnings on invalid parameters and returns.
    beartype_warn = beartype(conf=BeartypeConf(
        violation_param_type=LowInTheWest,
        violation_return_type=WhereHeStood,
        # is_debug=True,
    ))

    # Above callable decorated with type-checking raising custom exceptions.
    the_clear_and_raise = beartype_raise(the_clear_and)

    # Above callable decorated with type-checking emitting custom warnings.
    the_clear_and_warn = beartype_warn(the_clear_and)

    # ..................{ CONSTANTS                          }..................
    # Arbitrary list of strings to be passed to these callables.
    WHITHER_HAVE_FLED = [
        'Low in the west, the clear and garish hills,',
        'The distinct valley and the vacant woods,',
    ]

    # Arbitrary tuple of strings to be passed to these callables.
    THE_HUES_OF_HEAVEN = (
        'Spread round him where he stood. Whither have fled',
        'The hues of heaven that canopied his bower',
    )

    # ..................{ PASS                               }..................
    # Assert that these decorated callables neither raise exceptions nor emit
    # warnings when passed valid parameters.
    assert the_clear_and_raise(WHITHER_HAVE_FLED, THE_HUES_OF_HEAVEN) is (
        THE_HUES_OF_HEAVEN)
    assert the_clear_and_warn(WHITHER_HAVE_FLED, THE_HUES_OF_HEAVEN) is (
        THE_HUES_OF_HEAVEN)

    # Assert that this decorated callable raises the expected exception that
    # this callable was configured to raise on receiving an invalid parameter.
    with raises(TheVacantWoods):
        the_clear_and_raise(THE_HUES_OF_HEAVEN, WHITHER_HAVE_FLED)

    # Assert that this decorated callable raises the expected exception that
    # this callable was configured to raise on returning an invalid return.
    with raises(SpreadRoundHim):
        the_clear_and_raise(WHITHER_HAVE_FLED, WHITHER_HAVE_FLED)

    # Assert that this decorated callable emits the expected warning that
    # this callable was configured to emit on receiving an invalid parameter.
    with warns(LowInTheWest):
        the_clear_and_warn(THE_HUES_OF_HEAVEN, THE_HUES_OF_HEAVEN)

    # Assert that this decorated callable emits the expected warning that
    # this callable was configured to emit on returning an invalid return.
    with warns(WhereHeStood):
        the_clear_and_warn(WHITHER_HAVE_FLED, WHITHER_HAVE_FLED)
