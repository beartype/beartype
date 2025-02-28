#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-noncompliant** :mod:`numpy` **type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP-noncompliant** :mod:`numpy` **type hints** (i.e., :mod:`numpy`-specific
annotations *not* compliant with annotation-centric PEPs).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@pytest.mark.run_in_subprocess
@skip_unless_package('numpy')
def test_decor_numpy_register() -> None:
    '''
    Test that the :func:`beartype.beartype` decorator preserves the ordering of
    child hints subscripting :pep:`484`-compliant union type hints against a
    `prior issue`_ involving :mod:`numpy` if :mod:`numpy` is importable *or*
    silently skip this test otherwise (i.e., if :mod:`numpy` is unimportable).

    This issue proceeded as follows:

    #. A caller erroneously (albeit intentionally) registers the NumPy array
       type as a valid sequence subclass. However, the NumPy array type is *not*
       a valid sequence subclass. Notably, NumPy arrays fail to support the
       ``__bool__()`` dunder method testing whether those arrays are empty
       sequences or not. Attempting to test a NumPy array as a bool causes NumPy
       to raise an exception, which then prevents :mod:`beartype` from
       type-checking NumPy arrays as sequences: e.g.,

       .. code-block:: python

          ValueError: The truth value of an array with more than one element is
          ambiguous. Use a.any() or a.all()

    #. A :func:`beartype.beartype`-decorated callable accepting a parameter
       annotated as the :pep:`484`-compliant union of a sequence and a NumPy
       array (in that order) is defined.
    #. A NumPy array is then passed to this callable, which then raises the
       aforementioned :exc:`ValueError` due to NumPy arrays *not* being valid
       sequences.

    .. _prior issue:
       https://github.com/beartype/beartype/issues/499#issuecomment-2683400721

    Caveats
    -------
    This test is intentionally isolated to its own subprocess. Why? Because this
    test erroneously (albeit intentionally) registers the NumPy array type as a
    valid sequence subclass. Subclass registration is **permanent** and cannot
    currently be undone. As this subclass registration is erroneous, this
    registration *must* be isolated to a subprocess to avoid contaminating this
    parent `pytest` process (and thus all subsequently run tests).

    This test intentionally avoids accepting the ``numpy_arrays`` fixture. Why?
    Because the ``@pytest.mark.run_in_subprocess`` mark appears to prohibit
    fixture use in subprocesses. Clearly, this is a bug on our part. Clearly, we
    have no temporal bandwidth to debug this with. For the moment, we simply
    default to defining sample NumPy arrays inside this test. We shrug!
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.typing import Union
    from collections.abc import Sequence
    from numpy import (
        array,
        ndarray,
    )
    from numpy.typing import NDArray
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Arbitrary tuple of integers.
    search_thea_search = (42, 27, 88, 10)

    # Arbitrary NumPy array of integers.
    here_on_this_spot_of_earth = array(search_thea_search)

    # ....................{ PHASE 1 ~ failure              }....................
    # In the first phase, we intentionally:
    # * Define *ONLY* a @beartype-decorated function accepting a parameter
    #   annotated by a union of a sequence and NumPy array (in that order).
    # * Fully exercise that function with test data.
    #
    # Ideally, we'd simply define both of the functions tested below at once.
    # However, the two type hints "NDArray[int] | Sequence[int]" and
    # "Sequence[int] | NDArray[int]" compare as equal. Since @beartype memoizes
    # the code it dynamically generates on the usually sensible basis of type
    # hint equality, the fact that these two type hints compare as equal implies
    # that @beartype generates identical code for these two type hints. If this
    # code was *NOT* memoized, then @beartype would generate different code for
    # these two type hints. Why? Because @beartype's internal code generator for
    # unions preserves the ordering of union members.

    @beartype
    def somewhere_between_the_throne(
        and_where_i_sit: Union[Sequence[int], NDArray[int]]) -> int:
        '''
        Arbitrary function decorated by :func:`beartype.`beartype` accepting a
        parameter annotated by a :pep:`604`-compliant union of a sequence and a
        NumPy array (in that order).
        '''

        return len(and_where_i_sit)


    # Accept that this function accepts both sequences and NumPy arrays *BEFORE*
    # erroneously registering NumPy arrays as sequences.
    assert somewhere_between_the_throne(search_thea_search) == 4
    assert somewhere_between_the_throne(here_on_this_spot_of_earth) == 4

    # Erroneously register NumPy arrays as sequences. Since NumPy arrays
    # prohibit boolean tests by unconditionally raising exceptions when the
    # ndarray.__bool__() dunder method is called, NumPy arrays are *NOT*
    # sequences.
    Sequence.register(ndarray)

    # Accept that this function now accepts sequences but *NOT* NumPy arrays
    # *AFTER* erroneously registering NumPy arrays as sequences.
    assert somewhere_between_the_throne(search_thea_search) == 4
    with raises(ValueError):
        somewhere_between_the_throne(here_on_this_spot_of_earth)

    # ....................{ PHASE 2 ~ success              }....................
    #FIXME: Ugh. Due to memoization, this doesn't actually work. We'd need some
    #means of clearing the make_check_expr() cache, which we don't currently.
    # @beartype
    # def my_strong_identity(my_real_self: NDArray[int] | Sequence[int]) -> int:
    #     '''
    #     Arbitrary function decorated by :func:`beartype.`beartype` accepting a
    #     parameter annotated by a :pep:`604`-compliant union of a NumPy array and
    #     a sequence (in that order).
    #     '''
    #
    #     return len(my_real_self)
    #
    #
    # # Accept that this function still accepts both sequences and NumPy arrays
    # # even *AFTER* erroneously registering NumPy arrays as sequences.
    # assert my_strong_identity(search_thea_search) == 4
    # assert my_strong_identity(here_on_this_spot_of_earth) == 4
