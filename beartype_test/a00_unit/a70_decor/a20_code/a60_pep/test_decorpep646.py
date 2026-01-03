#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`646`-compliant :obj:`typing.Self` **unit tests**.

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

    #FIXME: Uncomment once worky, please.
    # # Assert that this callable returns a tuple of the passed integer followed
    # # by as many integers as the passed integer.
    # assert shall_scare(4) == (4, 0, 1, 2, 3)

    # ....................{ FAIL                           }....................
    # Assert that @beartype raises the expected exception when decorating a
    # callable annotated by a hint unpacking a PEP 646-noncompliant object
    # (i.e., other than a PEP 646-compliant type variable tuple or tuple hint).
    with raises(BeartypeDecorHintPep646692Exception):
        @beartype
        def scatter_its_music(
            *on_the_unfeeling_storm: Unpack[list[str]]) -> str:
            return on_the_unfeeling_storm[0]
