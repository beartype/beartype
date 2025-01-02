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

# ....................{ TESTS ~ tester                     }....................
def unit_test_is_hint_pep695_subscripted() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695.is_hint_pep695_subscripted`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep695 import (
        is_hint_pep695_subscripted)

    # ....................{ LOCALS                         }....................
    # Unsubscripted type alias.
    type and_thou = int | float

    # Subscriptable type alias yet to be subscripted by a concrete type.
    #
    # Note that, although subscriptable type aliases superficially appear to be
    # "pre-subscripted" by PEP 484-compliant type variables, this
    # "pre-subscription" is simply syntactic sugar; subscriptable type aliases
    # remain unsubscripted until explicitly subscripted by concrete types.
    type colossal_skeleton[T] = complex | T

    # ....................{ PASS                           }....................
    # Assert this tester accepts PEP 695-compliant subscripted type aliases
    # (i.e., subscriptable type aliases subscripted by concrete types).
    assert is_hint_pep695_subscripted(colossal_skeleton[int]) is True

    # ....................{ FAIL                           }....................
    # Assert this tester rejects objects that are *NOT* PEP 585-compliant
    # subscripted builtins.
    assert is_hint_pep695_subscripted(
        'And thou, colossal Skeleton, that, still') is False

    # Assert this tester rejects PEP 585-compliant subscripted builtins that are
    # *NOT* PEP 695-compliant subscripted type aliases.
    assert is_hint_pep695_subscripted(list[str]) is False

    # Assert this tester rejects PEP 695-compliant unsubscripted type aliases.
    assert is_hint_pep695_subscripted(and_thou) is False

    # Assert this tester accepts PEP 695-compliant subscriptable type aliases
    # yet to be subscripted by a concrete type.
    assert is_hint_pep695_subscripted(colossal_skeleton) is False

# ....................{ TESTS ~ iterator                   }....................
def unit_test_iter_hint_pep695_forwardrefs() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695.iter_hint_pep695_unsubscripted_forwardrefs`
    iterator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._check.forward.reference.fwdrefmeta import (
        BeartypeForwardRefMeta)
    from beartype._util.hint.pep.proposal.pep695 import (
        iter_hint_pep695_unsubscripted_forwardrefs)
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
    their_own_life = list(iter_hint_pep695_unsubscripted_forwardrefs(of_intermitted_song))
    assert not their_own_life

    # ....................{ ASSERTS ~ single               }....................
    # Assert that this iterator yields a single forward reference proxy
    # referring to the single unquoted forward reference embedded in a
    # passed type alias containing only that reference.
    and_saw_by = iter_hint_pep695_unsubscripted_forwardrefs(sudden_she_rose)
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
    # Assert that this iterator first yields a forward reference proxy referring
    # to the first unquoted forward reference embedded in a passed type alias
    # containing only that reference.
    her_glowing_limbs = iter_hint_pep695_unsubscripted_forwardrefs(
        as_if_her_heart)
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
def unit_test_reduce_hint_pep695_unsubscripted() -> None:
    '''
    Test the private
    :mod:`beartype._check.convert._reduce._pep.redpep695.reduce_hint_pep695_unsubscripted`
    reducer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._check.convert._reduce._pep.redpep695 import (
        reduce_hint_pep695_unsubscripted)
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Type alias containing *NO* unquoted forward references.
    type her_dark_locks = str | int

    # Type alias containing one unquoted forward reference.
    type floating_in = TheBreathOfNight | bool

    # ....................{ PASS                           }....................
    # Assert that this reducer returns the type hint underlying the passed type
    # alias containing *NO* unquoted forward references.
    assert reduce_hint_pep695_unsubscripted(
        hint=her_dark_locks, exception_prefix='') == str | int

    # ....................{ FAIL                           }....................
    # Assert that this reducer raises the expected exception when passed a type
    # alias containing one unquoted forward reference.
    with raises(BeartypeDecorHintPep695Exception):
        reduce_hint_pep695_unsubscripted(hint=floating_in, exception_prefix='')


def unit_test_reduce_hint_pep484_subscripted_typevar_to_hint() -> None:
    '''
    Test the public
    :mod:`beartype._util.hint.pep.proposal.pep484.pep484typevar.reduce_hint_pep484_subscripted_typevar_to_hint`
    getter with respect to :pep:`695`-compliant subscripted type aliases.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484TypeVarException
    from beartype._check.metadata.metasane import HintSanifiedData
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typevars
    from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
        reduce_hint_pep484_subscripted_typevar_to_hint)
    from beartype._util.kind.map.utilmapfrozen import FrozenDict
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Unsubscripted type alias.
    type guiding_its = int | float

    # Subscriptable type alias correctly parametrized by a single type variable.
    type irresistible_career[T] = complex | T

    # Subscriptable type alias correctly parametrized by multiple type
    # variables.
    type in_thy[S, T] = list[S] | dict[S, T]

    # Tuples of all type variables parametrizing these type aliases.
    irresistible_career_typevars = get_hint_pep_typevars(irresistible_career)
    in_thy_typevars = get_hint_pep_typevars(in_thy)

    # ....................{ PASS                           }....................
    # Assert this getter passed PEP 695-compliant subscripted type aliases
    # returns the expected tuple of all type variables parametrizing the
    # unsubscripted type aliases underlying these subscripted type aliases.
    #
    # Note that these type variables are literally scoped (i.e., isolated) to
    # these aliases and thus accessible *ONLY* by directly accessing the
    # "__parameters__" dunder attribute on these aliases. It is what it is.
    assert reduce_hint_pep484_subscripted_typevar_to_hint(
        irresistible_career[int]) == HintSanifiedData(
            irresistible_career,
            FrozenDict({irresistible_career_typevars[0]: int,}),
        )
    assert reduce_hint_pep484_subscripted_typevar_to_hint(
        in_thy[bool, complex]) == HintSanifiedData(
            in_thy,
            FrozenDict({
                in_thy_typevars[0]: bool,
                in_thy_typevars[1]: complex,
            }),
        )

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a PEP 695-compliant subscripted type alias.
    with raises(BeartypeDecorHintPep484TypeVarException):
        reduce_hint_pep484_subscripted_typevar_to_hint(
            'In thy devastating omnipotence,')

    # Assert this getter raises the expected exception when passed a PEP
    # 695-compliant unsubscripted type alias.
    with raises(BeartypeDecorHintPep484TypeVarException):
        reduce_hint_pep484_subscripted_typevar_to_hint(guiding_its)
    with raises(BeartypeDecorHintPep484TypeVarException):
        reduce_hint_pep484_subscripted_typevar_to_hint(irresistible_career)
