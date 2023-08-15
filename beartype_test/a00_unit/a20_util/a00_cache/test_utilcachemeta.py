#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype caching metaclass unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.utilcachemeta` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_caching_metaclass() -> None:
    '''
    Test the
    :func:`beartype._util.cache.utilcachemeta.BeartypeCachingMeta` metaclass.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableCachedException
    from beartype._util.cache.utilcachemeta import BeartypeCachingMeta
    from pytest import raises

    # ..................{ CALLABLES                          }..................
    class FledNotHisThirstingLips(object, metaclass=BeartypeCachingMeta):
        '''
        Arbitrary class whose metaclass is this metaclass.
        '''

        def __init__(self, and_all_of_great, or_good, or_lovely):
            '''
            Arbitrary callable memoized by this decorator.
            '''

            # If an arbitrary condition, raise an exception whose value depends
            # on these parameters to exercise this metaclass' exception caching.
            if len(or_lovely) == 6:
                raise ValueError(or_lovely)

            # Else, set an instance variable depending on these parameters to
            # exercise this metaclass' instance caching.
            self.which_the_sacred_past = and_all_of_great + or_good + or_lovely

    # ..................{ LOCALS                             }..................
    # Hashable objects to be passed as parameters below.
    and_all_of_great = ('In', 'truth', 'or', 'fable', 'consecrates,', 'he', 'felt',)
    or_good          = ('And', 'knew.', 'When', 'early', 'youth', 'had', 'past,', 'he', 'left',)
    or_lovely        = ('To', 'seek', 'strange', 'truths', 'in', 'undiscovered', 'lands.',)
    he_left          = ('His', 'cold', 'fireside', 'and', 'alienated', 'home',)

    # ..................{ ASSERTS ~ pass                     }..................
    # Assert that memoizing two instances passed the same positional arguments
    # caches and returns the same instance.
    assert (
        FledNotHisThirstingLips(and_all_of_great, or_good, or_lovely) is
        FledNotHisThirstingLips(and_all_of_great, or_good, or_lovely))

    # Assert that memoizing an instance expected to raise an exception does so.
    with raises(ValueError) as exception_first_info:
        FledNotHisThirstingLips(and_all_of_great, or_good, he_left)

    # Assert that repeating that instantiation reraises the same exception.
    with raises(ValueError) as exception_next_info:
        FledNotHisThirstingLips(and_all_of_great, or_good, he_left)
    assert exception_first_info.value is exception_next_info.value

    # Assert that initializing this class with one or more unhashable parameters
    # succeeds with the expected instance.
    and_he_has_bought = FledNotHisThirstingLips(
        ['Many', 'a', 'wide', 'waste',],
        ['and', 'tangled', 'wilderness',],
        ['Has lured his fearless steps;',],
    )
    assert and_he_has_bought.which_the_sacred_past == [
        'Many', 'a', 'wide', 'waste',
        'and', 'tangled', 'wilderness',
        'Has lured his fearless steps;',
    ]
