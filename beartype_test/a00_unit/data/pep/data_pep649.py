#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`649` **data submodule.**

This submodule exercises :pep:`649` support for unquoted forward references
inside type hinting contexts implemented in the :func:`beartype.beartype`
decorator by declaring unit tests exercising these references. For safety, these
tests are intentionally isolated from the main test suite.

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.14.0.** If this is *not* the case, importing this submodule raises
:exc:`NameError` exceptions.
'''

# ....................{ TESTS ~ iterator                   }....................
def unit_test_get_pep649_hintable_annotations() -> None:
    '''
    Test the :pep:`649`-compliant implementation of the private
    :mod:`beartype._util.hint.pep.proposal.pep649.get_pep649_hintable_annotations`
    getter under Python >= 3.14.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep649Exception
    # from beartype.typing import (
    #     Generic,
    #     Tuple,
    #     TypeVarTuple,
    #     Unpack,
    # )
    from beartype._util.hint.pep.proposal.pep649 import (
        get_pep649_hintable_annotations)
    from pytest import raises

    # # ....................{ CALLABLES                      }....................
    # @beartype
    # def of_all_the_grace(
    #     and_to_the_damp_leaves: ItsMotions,
    #     *and_beauty_that_endued: *Ts
    # # ) -> Tuple[ItsMotions, *Ts]:
    # ) -> object:
    #     '''
    #     Arbitrary callable simply returning the tuple of all passed variadic
    #     positional parameters prepended by the passed generic, decorated by
    #     :func:`beartype.beartype` and correctly annotated by:
    #
    #     * A variadic positional parameter typed as a :pep:`649`-compliant
    #       unpacked type variable tuple hint.
    #     * A return typed as a :pep:`484`-compliant tuple type hint subscripted
    #       by the same :pep:`649`-compliant unpacked type variable tuple hint.
    #     '''
    #
    #     # Return this variadic positional parameter prepended by this generic.
    #     return (and_to_the_damp_leaves,) + and_beauty_that_endued
    #
    # # ....................{ PASS                           }....................
    # # Assert that this callable returns a tuple of all passed positional
    # # parameters.
    # assert of_all_the_grace(
    #     render_up_its_majesty, 'Of all the grace', 'and beauty', 'that endued') == (
    #     render_up_its_majesty, 'Of all the grace', 'and beauty', 'that endued')
    #
    # # ....................{ FAIL                           }....................
    # # Assert that @beartype raises the expected exception when decorating a
    # # callable annotated by a hint unpacking a PEP 649-noncompliant object
    # # (i.e., *ANY* object other than a PEP 649-compliant type variable tuple).
    # with raises(BeartypeDecorHintPep649Exception):
    #     @beartype
    #     def scatter_its_music(
    #         *on_the_unfeeling_storm: Unpack[Tuple[str]]) -> str:
    #         return on_the_unfeeling_storm[0]
