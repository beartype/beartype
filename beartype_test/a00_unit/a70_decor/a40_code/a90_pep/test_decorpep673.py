#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`673`-compliant :obj:`typing.Self` **unit tests**.

This submodule unit tests :pep:`673` support implemented in the
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
def test_decor_pep673() -> None:
    '''
    Test :pep:`673` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.11 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.door import (
        die_if_unbearable,
        is_bearable,
    )
    from beartype.roar import (
        BeartypeCallHintReturnViolation,
        BeartypeDecorHintPep673Exception,
    )
    from beartype.typing import (
        List,
        Self,
    )
    from pytest import raises

    # ....................{ CLASSES                        }....................
    @beartype
    class GoodClassIsGood(object):
        '''
        Arbitrary class decorated by :func:`.beartype`.
        '''

        def wonderful_method_is_wonderful(self: Self, count: int) -> List[Self]:
            '''
            Arbitrary method annotated by one or more :pep:`673`-compliant self
            type hints, guaranteed to *not* violate runtime type-checking.
            '''

            return [self] * count


        def horrible_method_is_horrible(self: Self) -> Self:
            '''
            Arbitrary method annotated by one or more :pep:`673`-compliant self
            type hints, guaranteed to violate runtime type-checking.
            '''

            return 'Cleave themselves into chasms, while far below'

    # Do not taunt Super Happy Fun Instance.
    super_happy_fun_instance = GoodClassIsGood()

    # ....................{ PASS                           }....................
    # Assert that a method of a @beartype-decorated class satisfying a PEP
    # 673-compliant self type hint returns the expected object.
    avoid_prolonged_exposure = (
        super_happy_fun_instance.wonderful_method_is_wonderful(count=42))
    assert len(avoid_prolonged_exposure) == 42
    assert avoid_prolonged_exposure[ 0] is super_happy_fun_instance
    assert avoid_prolonged_exposure[-1] is super_happy_fun_instance

    # Assert that @beartype raises the expected violation when calling a
    # method of a @beartype-decorated class erroneously violating a PEP
    # 673-compliant self type hint.
    with raises(BeartypeCallHintReturnViolation):
        super_happy_fun_instance.horrible_method_is_horrible()

    # ....................{ FAIL                           }....................
    # Assert that @beartype raises the expected exception when decorating
    # non-class objects accepting one or more parameters erroneously annotated
    # by a PEP 673-compliant self type hint. Self type hints are valid *ONLY*
    # inside classes decorated by @beartype.
    with raises(BeartypeDecorHintPep673Exception):
        @beartype
        def terribad_function_is_terribad(self: Self) -> Self:
            return self
    with raises(BeartypeDecorHintPep673Exception):
        class BadClassIsBad(object):
            @beartype
            def awful_method_is_awful(self: Self) -> Self:
                return self

    # Assert that statement-level runtime type-checkers raise the expected
    # exceptions when passed PEP 673-compliant self type hints.
    with raises(BeartypeDecorHintPep673Exception):
        die_if_unbearable(
            'So sweet, the sense faints picturing them! Thou', Self)
    with raises(BeartypeDecorHintPep673Exception):
        is_bearable(
            "For whose path the Atlantic's level powers", Self)
