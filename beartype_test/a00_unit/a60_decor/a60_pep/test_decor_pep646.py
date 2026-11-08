#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`646`-compliant :obj:`typing.Unpack` **unit tests**.

This submodule unit tests :pep:`646` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.11.0')
def test_decor_pep646() -> None:
    '''
    Test :pep:`646` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.11 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep646692Exception
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        Ts_unpacked_prefix,
        Ts_unpacked_subbed,
    )
    from pytest import raises
    from typing import (
        Generic,
        Unpack,
    )

    # ....................{ CLASSES                        }....................
    @beartype
    class ItsMotions(Generic[Ts_unpacked_subbed]):
        '''
        Generic over an arbitrary number of type variables, decorated by
        :func:`beartype.beartype` and defined by subclassing the
        :class:`.Generic` superclass subscripted by the :pep:`646`-compliant
        :obj:`typing.Unpack` type hint factory subscripted by a
        :pep:`646`-compliant type variable tuple.

        Note that this is semantically equivalent to:

        .. code-block:: python

           class ItsMotions(Generic[*Ts]):
        '''

        pass


    # Arbitrary instance of this class.
    render_up_its_majesty = ItsMotions()

    # ....................{ CALLABLES                      }....................
    @beartype
    def of_all_the_grace(
        and_to_the_damp_leaves: ItsMotions,
        *and_beauty_that_endued: Ts_unpacked_prefix
    ) -> tuple[ItsMotions, Ts_unpacked_prefix]:
        '''
        Arbitrary callable simply returning the tuple of all passed variadic
        positional parameters prepended by the passed generic, decorated by
        :func:`beartype.beartype` and correctly annotated by:

        * A variadic positional parameter typed as a :pep:`646`-compliant
          unpacked type variable tuple hint.
        * A return typed as a :pep:`585`-compliant tuple type hint subscripted
          by the same :pep:`646`-compliant unpacked type variable tuple hint.
        '''

        # Return this variadic positional parameter prepended by this generic.
        return (and_to_the_damp_leaves,) + and_beauty_that_endued


    @beartype
    def shall_scare(rebel_jove: int) -> tuple[int, Unpack[tuple[int, ...]]]:
        '''
        Arbitrary callable returning the tuple consisting of the passed integer
        followed by as many integers as the passed integer, decorated by
        :func:`beartype.beartype` and correctly annotated by a return typed as a
        :pep:`585`-compliant tuple type hint subscripted by a
        :pep:`646`-compliant unpacked tuple type hint subscripted by another
        :pep:`585`-compliant tuple type hint.
        '''
        assert rebel_jove >= 0

        # Tuple of all non-negative integers in the range [0, rebel_jove).
        ints_nonnegative = tuple(
            int_nonnegative for int_nonnegative in range(rebel_jove))

        # Return the tuple of this integer and all items in that tuple unpacked.
        return rebel_jove, *ints_nonnegative

    # ....................{ PASS                           }....................
    # Assert that this callable returns a tuple of all passed positional
    # parameters.
    assert of_all_the_grace(
        render_up_its_majesty, 'Of all the grace', 'and beauty', 'that endued') == (
        render_up_its_majesty, 'Of all the grace', 'and beauty', 'that endued')

    # Assert that this callable returns a tuple of the passed integer followed
    # by as many integers as the passed integer.
    assert shall_scare(4) == (4, 0, 1, 2, 3)

    # ....................{ FAIL                           }....................
    # Assert that @beartype raises the expected exception when decorating a
    # callable annotated by a hint unpacking a PEP 646-noncompliant object
    # (i.e., other than a PEP 646-compliant type variable tuple or tuple hint).
    with raises(BeartypeDecorHintPep646692Exception):
        @beartype
        def scatter_its_music(
            *on_the_unfeeling_storm: Unpack[list[str]]) -> str:
            return on_the_unfeeling_storm[0]


@skip_if_python_version_less_than('3.11.0')
def test_decor_pep646_tuple_fixed_variadic() -> None:
    '''
    Test that the :func:`beartype.beartype` decorator deeply type-checks a
    pseudo-random variadic item of tuples annotated by :pep:`646`-compliant
    fixed-variadic tuple hints *and* that violations describe that same item
    (including when nested in other hints with an ignorable variadic child hint)
    if the active Python interpreter targets Python >= 3.11 *or* skip otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        tuple_variadic_strs_unpacked_prefix)
    from pytest import raises
    from re import search
    from typing import Unpack

    # ....................{ LOCALS                         }....................
    # PEP 646-compliant fixed-variadic tuple hint.
    Hint = tuple[int, tuple_variadic_strs_unpacked_prefix, bytes]

    # Tuple whose variadic items (i.e., at indices 1 through 4) *ALL* satisfy
    # this hint excluding the item at index 3.
    with_hooded_brows = (0, 'And with', 'hooded', 0xBADBEEF, 'brows', b'and')

    # ....................{ CALLABLES                      }....................
    @beartype
    def like_lightning(on_the_unfeeling_storm: Hint) -> None: pass

    @beartype
    def with_daedal(
        the_steep: tuple[tuple[int, Unpack[tuple[object, ...]]], int]) -> None: pass

    # ....................{ PASS                           }....................
    # Number of calls in which a valid and the invalid variadic item were
    # pseudo-randomly type-checked, respectively.
    calls_passed = calls_failed = 0

    # For a sufficiently large number of calls that both valid and invalid
    # variadic items are effectively guaranteed to be type-checked...
    for _ in range(64):
        try:
            like_lightning(with_hooded_brows)
            calls_passed += 1
        # If the invalid variadic item was type-checked, assert that this
        # violation describes that item. If this violation were to describe a
        # different item, @beartype would instead raise a private
        # desynchronization exception that this test fails to catch.
        except BeartypeCallHintParamViolation as exception:
            assert search(r'\btuple index 3 item int\b', str(exception))
            calls_failed += 1

    # Assert that both valid and invalid variadic items were type-checked.
    assert calls_passed
    assert calls_failed

    # ....................{ FAIL ~ nested                  }....................
    # Assert that a callable annotated by a fixed-variadic tuple hint with an
    # ignorable variadic child hint nested in another hint describes violations
    # *WITHOUT* requiring a pseudo-random integer.
    with raises(BeartypeCallHintParamViolation, match=r'\btuple index 1 item str\b'):
        with_daedal(((1, 2), 'the steep'))
    with raises(BeartypeCallHintParamViolation, match=r'\blength 0 < 1\b'):
        with_daedal(((), 0))
