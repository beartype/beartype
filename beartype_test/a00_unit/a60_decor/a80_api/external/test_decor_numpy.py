#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-noncompliant NumPy type hint** unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP-noncompliant NumPy type hints** (i.e., :mod:`numpy.typing`-specific
annotations *not* compliant with annotation-centric PEPs).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('numpy')
def test_decor_numpy() -> None:
    '''
    Test that the :func:`beartype.beartype` decorator correctly decorates
    callables annotated by NumPy-centric type hints.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from collections.abc import Iterable
    from numpy import (
        ndarray,
        ones,
    )
    from pytest import raises

    # ....................{ CALLABLES                      }....................
    @beartype
    def search_thea_search(
        here_on_this_spot_of_earth: Iterable[ndarray]) -> Iterable[ndarray]:
        '''
        Arbitrary callable both accepting and returning an iterable of NumPy
        arrays.

        Surprisingly, this callable exercises an edge case unique to NumPy
        arrays. Why? Because NumPy arrays satisfy the standard
        :class:`collections.abc.Collection` protocol *but* override the
        ``__bool__()`` dunder method with non-standard behaviour that
        conditionally raises a :exc:`RuntimeError` when the current NumPy
        array contains two or more items. Since *most* NumPy arrays contain
        two or more items, effectively all NumPy arrays raise exceptions when
        evaluated in a boolean context.

        This matters, because :mod:`beartype` previously generated optimally
        efficient type-checking code for :obj:`typing.Iterable` type hints.
        How? :mod:`beartype` detected whether the current pith is a non-empty
        collection by testing that pith in a boolean context. Cue destruction
        when the current pith is a NumPy array.

        See Also
        --------
        https://github.com/beartype/beartype/issues/514
            Issue strongly inspiring this unit test.
        '''

        return here_on_this_spot_of_earth

    # ....................{ LOCALS                         }....................
    # Arbitrary non-trivial NumPy array. In this case, this is a two-dimensional
    # array of standard shape 3x3 whose items are all the floating-point number
    # "1.0".
    somewhere_between_the_throne = ones((3, 3))

    # ....................{ PASS                           }....................
    # Assert that this callable accepts this array.
    assert search_thea_search(somewhere_between_the_throne) is (
        somewhere_between_the_throne)

    # ....................{ FAIL                           }....................
    # Assert that this callable raises the expected exception when passed an
    # iterable of non-arrays.
    with raises(BeartypeCallHintParamViolation):
        search_thea_search(
            "Upon all space: space starr'd, and lorn of light;")


@skip_unless_package('numpy')
def test_decor_numpy_dtype_union() -> None:
    '''
    Test :func:`beartype.door.is_bearable` against NumPy arrays subscripted by
    unions of scalar types and unions of dtypes.
    '''

    # Defer test-specific imports.
    from beartype.door import is_bearable
    from numpy import (
        dtype,
        float32,
        float64,
        floating,
        int64,
        ndarray,
        zeros,
    )
    from numpy.typing import NDArray

    array_f32 = zeros(2, dtype=float32)
    array_f64 = zeros(2, dtype=float64)
    array_i64 = zeros(2, dtype=int64)

    for hint in (
        NDArray[float32 | float64],
        ndarray[tuple[int], dtype[float32 | float64]],
        ndarray[tuple[int], dtype[float32] | dtype[float64]],
    ):
        assert is_bearable(array_f32, hint) is True
        assert is_bearable(array_f64, hint) is True
        assert is_bearable(array_i64, hint) is False

    hint_abc = NDArray[floating | int64]
    assert is_bearable(array_f32, hint_abc) is True
    assert is_bearable(array_i64, hint_abc) is True
    assert is_bearable(zeros(2, dtype=bool), hint_abc) is False
