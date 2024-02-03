#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695` **utility data submodule.**

This submodule exercises :pep:`695` support for statement-level type aliases
implemented in the :func:`beartype.beartype` decorator by declaring unit tests
exercising these aliases. For safety, these tests are intentionally isolated
from the main test suite. Notably, this low-level submodule implements the
higher-level ``test_decor_pep695()`` unit test in the main test suite.

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.12.0.** If this is *not* the case, importing this submodule raises an
:exc:`SyntaxError` exception.
'''
# ....................{ TESTS ~ iterator                   }....................
def unit_test_iter_hint_pep695_forwardrefs() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.utilpep695.iter_hint_pep695_forwardrefs`
    iterator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._check.forward.reference.fwdrefmeta import (
        BeartypeForwardRefMeta)
    from beartype._util.hint.pep.proposal.utilpep695 import (
        iter_hint_pep695_forwardrefs)
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Type alias containing *NO* unquoted forward references.
    type of_intermitted_song = str | int

    # Type alias containing one unquoted forward reference.
    type sudden_she_rose = ItsBurstingBurthen | bool

    # Type alias containing two or more unquoted forward reference.
    type as_if_her_heart = ImpatientlyEndured | complex | AtTheSoundHeTurned

    # ....................{ ASSERTS ~ null                 }....................
    # Assert that this iterator yields nothing when passed a type alias
    # containing *NO* unquoted forward references.
    their_own_life = list(iter_hint_pep695_forwardrefs(of_intermitted_song))
    assert not their_own_life

    # ....................{ ASSERTS ~ single               }....................
    # Assert that this iterator yields a single forward reference proxy
    # referring to the single unquoted forward reference embedded in a
    # passed type alias containing only that reference.
    and_saw_by = iter_hint_pep695_forwardrefs(sudden_she_rose)
    the_warm_light_of = next(and_saw_by)
    assert isinstance(the_warm_light_of, BeartypeForwardRefMeta)
    assert the_warm_light_of.__name__ == 'ItsBurstingBurthen'

    # Assert this iterator raises the expected exception when attempting to
    # erroneously iterate past an unquoted forward reference referring to an
    # undefined attribute.
    with raises(BeartypeDecorHintPep695Exception):
        next(and_saw_by)

    class ItsBurstingBurthen(object):
        '''
        Class to which this unquoted forward reference refers, intentionally
        declared while iterating this iterator.
        '''

        pass

    # Assert that this iterator is now exhausted.
    with raises(StopIteration):
        next(and_saw_by)

    # ....................{ ASSERTS ~ multiple             }....................
    # Assert that this iterator first yields a forward reference proxy
    # referring to the first unquoted forward reference embedded in a
    # passed type alias containing only that reference.
    her_glowing_limbs = iter_hint_pep695_forwardrefs(as_if_her_heart)
    beneath_the_sinuous_veil = next(her_glowing_limbs)
    assert isinstance(beneath_the_sinuous_veil, BeartypeForwardRefMeta)
    assert beneath_the_sinuous_veil.__name__ == 'ImpatientlyEndured'

    class ImpatientlyEndured(object):
        '''
        Class to which this unquoted forward reference refers, intentionally
        declared while iterating this iterator.
        '''

        pass

    # Assert that this iterator lastly yields a forward reference proxy
    # referring to the last unquoted forward reference in this type alias.
    of_woven_wind = next(her_glowing_limbs)
    assert isinstance(of_woven_wind, BeartypeForwardRefMeta)
    assert of_woven_wind.__name__ == 'AtTheSoundHeTurned'

    class AtTheSoundHeTurned(object):
        '''
        Class to which this unquoted forward reference refers, intentionally
        declared while iterating this iterator.
        '''

        pass

    # Assert this iterator raises the expected exception when attempting to
    # erroneously iterate past an unquoted forward reference referring to an
    # undefined attribute.
    with raises(StopIteration):
        next(her_glowing_limbs)

# ....................{ TESTS ~ reducer                    }....................
def unit_test_reduce_hint_pep695() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.utilpep695.reduce_hint_pep695`
    reducer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._util.hint.pep.proposal.utilpep695 import reduce_hint_pep695
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Type alias containing *NO* unquoted forward references.
    type her_dark_locks = str | int

    # Type alias containing one unquoted forward reference.
    type floating_in = TheBreathOfNight | bool

    # ....................{ PASS                           }....................
    # Assert that this reducer returns the type hint underlying the passed type
    # alias containing *NO* unquoted forward references.
    assert reduce_hint_pep695(
        hint=her_dark_locks, exception_prefix='') == str | int

    # ....................{ FAIL                           }....................
    # Assert that this reducer raises the expected exception when passed a type
    # alias containing one unquoted forward reference.
    with raises(BeartypeDecorHintPep695Exception):
        reduce_hint_pep695(hint=floating_in, exception_prefix='')
