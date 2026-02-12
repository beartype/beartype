#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-noncompliant** :mod:`nptyping` **type hint unit
tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP-noncompliant** :mod:`nptyping` **type hints** (i.e.,
:mod:`nptyping`-specific annotations *not* compliant with annotation-centric
PEPs).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import (
    skip,
    # skip_if_python_version_less_than,
    # skip_unless_package,
)

# ....................{ TESTS                              }....................
#FIXME: *WOAH.* Importing literally *ANYTHING* from "nptyping" now produces
#extreme breakage with respect to the "abc.ABC" superclass. We don't quite
#understand why and it probably doesn't particularly matter, since "nptyping" is
#quite dead. That said, enabling this test currently causes the
#test_door_is_bearable_warnings() test to fail with this unreadable exception:
#    beartype.roar.BeartypeDecorHintNonpepException: Is_bearable() <class
#    'abc.ABC'> uncheckable at runtime (i.e., not passable as second parameter
#    to isinstance(), due to raising "NPTypingError: Subclass checking is not
#    supported for nptyping.NDArray." from metaclass __instancecheck__()
#    method).
#
#Consequently, this test is now unconditionally disabled for safety. O_o
#FIXME: If "nptyping" ever revives itself, politely reconsider this.
@skip('"nptyping" harmfully breaks unrelated unit tests.')

#FIXME: We have to disable even package testing or everything breaks. *YIKES.*
# If the active Python interpreter targets Python < 3.10.0, this interpreter
# fails to support PEP 604-compliant new unions (e.g., "int | str") and thus the
# entire point of this unit test. In this case, skip this test.
# @skip_if_python_version_less_than('3.10.0')
# @skip_unless_package('nptyping')
def test_decor_nptyping() -> None:
    '''
    Test that the :func:`beartype.beartype` decorator rejects *all*
    :mod:`nptyping` type hints with the expected exception.

    :mod:`nptyping` type hints violate Python typing standards in various ways.
    Notably, :mod:`nptyping` type hint factories dynamically generate unique
    classes that nonetheless share the same fully-qualified names, complicating
    caching in the :func:`beartype.beartype` decorator.

    Whereas this test suite automates testing of PEP-compliant type hints via
    the :mod:`beartype_test.a00_unit.data` subpackage, :mod:`nptyping` type
    hints are fundamentally non-standard and thus *cannot* be automated in this
    standard manner. These hints can *only* be tested with a non-standard
    workflow implemented by this unit test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    #
    # Note that nptyping requires NumPy. Ergo, NumPy is safely importable here.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep604Exception
    from numpy import (
        # array,
        # float64,
        int64,
        sum as numpy_sum,
    )
    from nptyping import (
        Float64,
        Int64,
        NDArray,
        Shape,
    )
    from pytest import raises

    # ....................{ FUNCTIONS                      }....................
    with raises(BeartypeDecorHintPep604Exception):
        @beartype
        def suspended_he_that_task(
            but_ever_gazed: NDArray[Shape['N, N'], Float64] | None = None,
            and_gazed:      NDArray[Shape['*'   ], Int64] | None = None,
        ) -> int64 | None:
            '''
            Arbitrary callable annotated by two :pep:`604`-compliant new unions
            of distinct :mod:`nptyping` type hints and arbitrary other types.

            This callable exercises a `prominent edge case`_.

            .. _prominent edge case:
               https://github.com/beartype/beartype/issues/304
            '''

            # Bend it like Bender.
            return None if and_gazed is None else numpy_sum(and_gazed)

    #FIXME: Uncomment this if @ramonhagenaars ever resurrects "nptyping". Until
    #that utopia, this is optimistically preserved for posterity.
    # '''
    # Test that the :func:`beartype.beartype` decorator successfully type-checks
    # callables annotated by :mod:`nptyping` type hints.
    #
    # :mod:`nptyping` type hints violate Python typing standards in various ways.
    # Notably, :mod:`nptyping` type hint factories dynamically generate unique
    # classes that nonetheless share the same fully-qualified names, complicating
    # caching in the :func:`beartype.beartype` decorator.
    #
    # Whereas this test suite automates testing of PEP-compliant type hints via
    # the :mod:`beartype_test.a00_unit.data` subpackage, :mod:`nptyping` type
    # hints are fundamentally non-standard and thus *cannot* be automated in this
    # standard manner. These hints can *only* be tested with a non-standard
    # workflow implemented by this unit test.
    # '''
    #
    # # ....................{ IMPORTS                        }....................
    # # Defer test-specific imports.
    # #
    # # Note that nptyping requires NumPy. Ergo, NumPy is safely importable here.
    # from beartype import beartype
    # from beartype.roar import BeartypeCallHintParamViolation
    # from numpy import (
    #     array,
    #     float64,
    #     int64,
    #     sum as numpy_sum,
    # )
    # from nptyping import (
    #     Float64,
    #     Int64,
    #     NDArray,
    #     Shape,
    # )
    # from pytest import raises
    #
    # # ....................{ LOCALS                         }....................
    # # Arbitrary NumPy arrays satisfied by "nptyping" type hints defined below.
    # flashed_like_strong_inspiration = array(
    #     [[1., 2.], [3., 4.]], dtype=float64)
    # till_meaning_on_his_vacant_mind = array(
    #     [1, 2, 3, 4, 5, 6], dtype=int64)
    #
    # # ....................{ FUNCTIONS                      }....................
    # @beartype
    # def suspended_he_that_task(
    #     but_ever_gazed: NDArray[Shape['N, N'], Float64] | None = None,
    #     and_gazed:      NDArray[Shape['*'   ], Int64] | None = None,
    # ) -> int64 | None:
    #     '''
    #     Arbitrary callable annotated by two :pep:`604`-compliant new unions of
    #     distinct :mod:`nptyping` type hints and arbitrary other types.
    #
    #     This callable exercises a `prominent edge case`_.
    #
    #     .. _prominent edge case:
    #        https://github.com/beartype/beartype/issues/304
    #     '''
    #
    #     # Bend it like Bender.
    #     return None if and_gazed is None else numpy_sum(and_gazed)
    #
    # # ....................{ PASS                           }....................
    # # Assert that this callable returns the expected value when passed NumPy
    # # arrays satisfying the "nptyping" type hints annotating this callable.
    # assert suspended_he_that_task(
    #     but_ever_gazed=flashed_like_strong_inspiration,
    #     and_gazed=till_meaning_on_his_vacant_mind,
    # ) == 21
    #
    # # ....................{ FAIL                           }....................
    # # Assert that this callable raises the expected exception when passed NumPy
    # # arrays violating the "nptyping" type hints annotating this callable.
    # with raises(BeartypeCallHintParamViolation):
    #     suspended_he_that_task(till_meaning_on_his_vacant_mind)
