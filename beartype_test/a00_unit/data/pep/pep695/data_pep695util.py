#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
def unit_test_is_hint_pep695_subbed() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695.is_hint_pep695_subbed`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep695 import (
        is_hint_pep695_subbed)

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
    assert is_hint_pep695_subbed(colossal_skeleton[int]) is True

    # ....................{ FAIL                           }....................
    # Assert this tester rejects objects that are *NOT* PEP 585-compliant
    # subscripted builtins.
    assert is_hint_pep695_subbed(
        'And thou, colossal Skeleton, that, still') is False

    # Assert this tester rejects PEP 585-compliant subscripted builtins that are
    # *NOT* PEP 695-compliant subscripted type aliases.
    assert is_hint_pep695_subbed(list[str]) is False

    # Assert this tester rejects PEP 695-compliant unsubscripted type aliases.
    assert is_hint_pep695_subbed(and_thou) is False

    # Assert this tester accepts PEP 695-compliant subscriptable type aliases
    # yet to be subscripted by a concrete type.
    assert is_hint_pep695_subbed(colossal_skeleton) is False

# ....................{ TESTS ~ getter                     }....................
def unit_test_get_hint_pep695_parameterizable_typeparams() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695._get_hint_pep695_parameterizable_typeparams`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.typing import (
        ParamSpec,
        TypeVar,
        TypeVarTuple,
    )
    from beartype._util.hint.pep.proposal.pep695 import (
        _get_hint_pep695_parameterizable_typeparams)

    # ....................{ CLASSES                        }....................
    class AndThenSpake[S]:  # <-- this is madness. this is PEP 695.
        '''
        Class parametrized by *only* a :pep:`484`-compliant type variable.

        Note that this class intentionally avoids subclassing *any* superclass,
        including:

        * The root :class:`object` superclass, as doing so raises unreadable
          low-level Python exceptions resembling:

          TypeError: Cannot create a consistent method resolution order (MRO)
          for bases object, Generic

        * The :pep:`484`-compliant :class:`typing.Generic` superclass, as doing
          so raises unreadable low-level Python exceptions resembling:

          TypeError: Cannot inherit from Generic[...] multiple times.

        This is nonsensical and actively obstructs the declaration of generics.
        Explicit is better than implicit -- especially when implicit stopped
        making sense 50 PEP standards and 4 CPython minor versions ago.
        '''

        pass

    # ....................{ CALLABLES                      }....................
    def as_with_a_palsied_tongue[*Ss, **Q]():
        '''
        Function parametrized by *only* a :pep:`612`-compliant parameter
        specifications and :pep:`646`-compliant tuple type variable.
        '''

        pass

    # ....................{ LOCALS                         }....................
    # Type alias parametrized by one of each possible type parameter.
    type and_that_fair_kneeling_goddess[T, *Ts, **P] = int

    # ....................{ ASSERTS                        }....................
    # Assert this getter passed a pure-Python class returns the expected tuple.
    AndThenSpake_typevars = _get_hint_pep695_parameterizable_typeparams(
        AndThenSpake)
    assert len(AndThenSpake_typevars) == 1
    assert isinstance(AndThenSpake_typevars[0], TypeVar)

    # Assert this getter passed a pure-Python function returns the expected
    # tuple.
    as_with_a_palsied_tongue_typevars = (
        _get_hint_pep695_parameterizable_typeparams(as_with_a_palsied_tongue))
    assert len(as_with_a_palsied_tongue_typevars) == 2
    assert isinstance(as_with_a_palsied_tongue_typevars[0], TypeVarTuple)
    assert isinstance(as_with_a_palsied_tongue_typevars[1], ParamSpec)

    # Assert this getter passed a PEP 695-compliant type alias returns the
    # expected tuple.
    and_that_fair_kneeling_goddess_typevars = (
        _get_hint_pep695_parameterizable_typeparams(
            and_that_fair_kneeling_goddess))
    assert len(and_that_fair_kneeling_goddess_typevars) == 3
    assert isinstance(and_that_fair_kneeling_goddess_typevars[0], TypeVar)
    assert isinstance(and_that_fair_kneeling_goddess_typevars[1], TypeVarTuple)
    assert isinstance(and_that_fair_kneeling_goddess_typevars[2], ParamSpec)

# ....................{ TESTS ~ iterator                   }....................
def unit_test_iter_hint_pep695_forwardrefs() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695.iter_hint_pep695_unsubbed_forwardrefs`
    iterator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._check.forward.reference.fwdrefmeta import (
        BeartypeForwardRefMeta)
    from beartype._util.hint.pep.proposal.pep695 import (
        iter_hint_pep695_unsubbed_forwardrefs)
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
    their_own_life = list(
        iter_hint_pep695_unsubbed_forwardrefs(of_intermitted_song))
    assert not their_own_life

    # ....................{ ASSERTS ~ single               }....................
    # Assert that this iterator yields a single forward reference proxy
    # referring to the single unquoted forward reference embedded in a
    # passed type alias containing only that reference.
    and_saw_by = iter_hint_pep695_unsubbed_forwardrefs(sudden_she_rose)
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
    her_glowing_limbs = iter_hint_pep695_unsubbed_forwardrefs(
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
def unit_test_reduce_hint_pep695_unsubbed() -> None:
    '''
    Test the public
    :mod:`beartype._check.convert._reduce._pep.redpep695.reduce_hint_pep695_unsubbed`
    reducer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._check.convert._reduce._pep.redpep695 import (
        reduce_hint_pep695_unsubbed)
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Type alias containing *NO* unquoted forward references.
    type her_dark_locks = str | int

    # Type alias containing one unquoted forward reference.
    type floating_in = TheBreathOfNight | bool

    # ....................{ PASS                           }....................
    # Assert that this reducer returns the type hint underlying the passed type
    # alias containing *NO* unquoted forward references.
    hint_sane = reduce_hint_pep695_unsubbed(
        hint=her_dark_locks,
        hint_parent_sane=None,
        exception_prefix='',
    )
    assert hint_sane.hint == str | int

    # ....................{ FAIL                           }....................
    # Assert that this reducer raises the expected exception when passed a type
    # alias containing one unquoted forward reference.
    with raises(BeartypeDecorHintPep695Exception):
        reduce_hint_pep695_unsubbed(
            hint=floating_in,
            hint_parent_sane=None,
            exception_prefix='',
        )


def unit_test_reduce_hint_pep484612646_subbed_typeargs_to_hints_for_pep695() -> (
    None):
    '''
    Test the public ``reduce_hint_pep484612646_subbed_typeargs_to_hints()`` getter
    with respect to :pep:`695`-compliant subscripted type aliases.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484612646Exception
    from beartype._check.convert._reduce._pep.redpep484612646 import (
        reduce_hint_pep484612646_subbed_typeargs_to_hints)
    from beartype._check.metadata.hint.hintsane import HintSane
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typeargs_packed
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
    irresistible_career_typevars = get_hint_pep_typeargs_packed(irresistible_career)
    in_thy_typevars = get_hint_pep_typeargs_packed(in_thy)

    # ....................{ PASS                           }....................
    # Assert this getter passed PEP 695-compliant subscripted type aliases
    # returns the expected tuple of all type variables parametrizing the
    # unsubscripted type aliases underlying these subscripted type aliases.
    #
    # Note that these type variables are literally scoped (i.e., isolated) to
    # these aliases and thus accessible *ONLY* by directly accessing the
    # "__parameters__" dunder attribute on these aliases. It is what it is.
    hint_sane = reduce_hint_pep484612646_subbed_typeargs_to_hints(
        irresistible_career[int])
    assert hint_sane == HintSane(
        hint=irresistible_career,
        typearg_to_hint=FrozenDict({irresistible_career_typevars[0]: int,}),
    )

    hint_sane = reduce_hint_pep484612646_subbed_typeargs_to_hints(
        in_thy[bool, complex])
    assert hint_sane == HintSane(
        hint=in_thy,
        typearg_to_hint=FrozenDict({
            in_thy_typevars[0]: bool,
            in_thy_typevars[1]: complex,
        }),
    )

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a PEP 695-compliant subscripted type alias.
    with raises(BeartypeDecorHintPep484612646Exception):
        reduce_hint_pep484612646_subbed_typeargs_to_hints(
            'In thy devastating omnipotence,')

    # Assert this getter raises the expected exception when passed a PEP
    # 695-compliant unsubscripted type alias.
    with raises(BeartypeDecorHintPep484612646Exception):
        reduce_hint_pep484612646_subbed_typeargs_to_hints(guiding_its)
    with raises(BeartypeDecorHintPep484612646Exception):
        reduce_hint_pep484612646_subbed_typeargs_to_hints(irresistible_career)

# ....................{ TESTS ~ decorator                  }....................
#FIXME: Actually call this unit test!
def unit_test_decor_hint_pep695_type_recursive_indirect() -> None:
    '''
    Test :pep:`695`-compliant type aliases with respect to a
    :func:`beartype.beartype`-decorated class parametrized by a
    :pep:`484`-compliant type variable bound to an unsubscripted type alias such
    that that class defines a method accepting a parameter annotated as that
    same type alias subscripted by that same type variable, indirectly inducing
    recursion between that type alias and type variable.

    This unit test exercises a non-trivial `edge case`_ that actually arose.

    .. _edge case:
       https://github.com/beartype/beartype/issues/510
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Type alias aliasing a PEP 585-compliant fixed-length tuple type hint
    # subscripted by one type variable and an arbitrary builtin type.
    type WithStr[T] = tuple[T, str]

    # ....................{ CALLABLES                      }....................
    @beartype
    class ToOverbear[T: WithStr]:
        '''
        Arbitrary :func:`beartype.beartype`-decorated class parametrized by a
        :pep:`484`-compliant type variable bound to an unsubscripted type alias.
        '''

        @staticmethod
        def and_crumble_this(to_naught: WithStr[T]) -> str:
            '''
            Arbitrary method accepting a parameter annotated as that same type
            alias subscripted by that same type variable, indirectly inducing
            recursion between that type alias and type variable.
            '''

            (_, inner_item_second), outer_item_second = to_naught
            return inner_item_second + outer_item_second

    # ....................{ LOCALS                         }....................
    # Arbitrary tuple satisfying the "to_naught" parameter defined above with
    # respect to O(1) type-checking generated by @beartype.
    #
    # Note that this tuple is intentionally *NOT* infinitely recursive. For
    # efficiency, O(1) type-checking generated by @beartype only type-checks
    # PEP 695-compliant recursive type aliases to one layer of nesting. Ergo, a
    # tuple of tuple of strings suffices to exercise this functionality.
    where_is_another_chaos = (
        (
            # Technically, this should be an infinitely recursive tuple
            # exhibiting the same internal structure to satisfy this hint.
            # Pragmatically, @beartype only type-checks PEP 695-compliant
            # recursive type aliases to one layer of nesting as detailed above.
            # Since this is that layer of nesting, *ANY* object suffices.
            0xFEEDFACE,
            'Where is another chaos? Where?"—That word',
        ),
        'Found way unto Olympus, and made quake',
    )

    # Arbitrary tuple violating the "to_naught" parameter defined above with
    # respect to O(1) type-checking generated by @beartype.
    found_way_unto_olympus = (
        (
            0xCAFEBABE,  # See above.
            b'The rebel three.--Thea was startled up,',
        ),
        'Found way unto Olympus, and made quake',
    )

    # ....................{ PASS                           }....................
    # Assert that this method passed a valid parameter returns the expected
    # value.
    assert ToOverbear.and_crumble_this(where_is_another_chaos) == (
        'Where is another chaos? Where?"—That word'
        'Found way unto Olympus, and made quake'
    )

    # ....................{ FAIL                           }....................
    # Assert that this method passed an valid parameter raises the expected
    # exception.
    with raises(BeartypeCallHintParamViolation):
        ToOverbear.and_crumble_this(found_way_unto_olympus)
