#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-noncompliant PyTorch type hint** unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP-noncompliant PyTorch type hints** (i.e., :mod:`torch`-specific types).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('torch')
def test_decor_torch() -> None:
    '''
    Test that the :func:`beartype.beartype` decorator correctly decorates
    callables annotated by PyTorch-centric type hints.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from collections.abc import Iterable
    from pytest import raises
    from torch import (
        Tensor,
        ones,
    )

    # ....................{ CALLABLES                      }....................
    @beartype
    def open_thine_eyes_eterne(
        and_sphere_them_round: Iterable[Tensor]) -> Iterable[Tensor]:
        '''
        Arbitrary callable both accepting and returning an iterable of PyTorch
        tensors.

        Surprisingly, this callable exercises an edge case unique to PyTorch
        tensors. Why? Because PyTorch tensors satisfy the standard
        :class:`collections.abc.Collection` protocol *but* override the
        ``__bool__()`` dunder method with non-standard behaviour that
        conditionally raises a :exc:`RuntimeError` when the current PyTorch
        tensor contains two or more items. Since *most* PyTorch tensors contain
        two or more items, effectively all PyTorch tensors raise exceptions when
        evaluated in a boolean context.

        This matters, because :mod:`beartype` previously generated optimally
        efficient type-checking code for :obj:`typing.Iterable` type hints.
        How? :mod:`beartype` detected whether the current pith is a non-empty
        collection by testing that pith in a boolean context. Cue destruction
        when the current pith is a PyTorch tensor.

        See Also
        --------
        https://github.com/beartype/beartype/issues/512
            Issue strongly inspiring this unit test.
        '''

        return and_sphere_them_round


    @beartype
    def a_certain_shape_or_shadow(making_way: Iterable[float]) -> None:
        '''
        Arbitrary callable accepting and returning an iterable of simple scalars
        rather than PyTorch tensors.

        This callable exercises a similar (but ultimately distinct) edge case to
        that of the :func:`.open_thine_eyes_eterne` function defined above.

        See Also
        --------
        https://github.com/beartype/beartype/issues/514
            Issue strongly inspiring this unit test.
        '''

        pass

    # ....................{ LOCALS                         }....................
    # Arbitrary non-trivial PyTorch tensor. In this case, this is a
    # one-dimensional tensor of 3 items that are all the floating-point number
    # "1.0".
    with_wings_or_chariot = ones(3)

    # Arbitrary non-trivial PyTorch tensor. In this case, this is a
    # two-dimensional tensor of standard shape 3x3 whose items are all the
    # floating-point number "1.0".
    upon_all_space = ones(3, 3)

    # ....................{ PASS                           }....................
    # Assert that this callable accepts this two-dimensional tensor -- which,
    # interestingly satisfies the definition of "an iterable of one-dimensional
    # tensors" from a certain mathematical perspective that is boring.
    assert open_thine_eyes_eterne(upon_all_space) is upon_all_space

    # ....................{ FAIL                           }....................
    # Assert that this callable raises the expected exception when passed an
    # iterable of non-tensors.
    with raises(BeartypeCallHintParamViolation):
        open_thine_eyes_eterne(
            "Upon all space: space starr'd, and lorn of light;")

    # Assert that this callable raises the expected exception when passed a
    # one-dimensional iterable of tensors.
    with raises(BeartypeCallHintParamViolation):
        a_certain_shape_or_shadow(with_wings_or_chariot)

    # Assert that this callable raises the expected exception when passed an
    # iterable of non-tensors.
    with raises(BeartypeCallHintParamViolation):
        a_certain_shape_or_shadow(
            'With wings or chariot fierce to repossess')
