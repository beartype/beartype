#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`647`- or :pep:`742`-compliant **unit tests**.

This submodule unit tests both :pep:`647` and :pep:`742` support implemented in
the :func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.10.0')
def test_decor_pep647() -> None:
    '''
    Test :pep:`647` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.10 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintReturnViolation,
        BeartypeDecorHintPep647Exception,
    )
    from beartype.typing import (
        List,
        TypeGuard,
        Tuple,
    )
    from pytest import raises

    # ....................{ FUNCTIONS                      }....................
    @beartype
    def is_typeguard_slow(lst: List[object]) -> TypeGuard[List[str]]:
        '''
        :pep:`647`-compliant type guard returning :data:`True` only if the
        passed list contains only string items via the standard linear runtime
        type-check implemented manually.

        *leisurely barfs into adjacent bucket*
        '''

        return all(isinstance(item, str) for item in lst)


    @beartype
    def is_typeguard_bad(tup: Tuple[object, ...]) -> TypeGuard[Tuple[int, ...]]:
        '''
        :pep:`647`-compliant type guard erroneously (presumably, accidentally)
        violating :pep:`647` by returning a non-boolean object.
        '''

        return "Lull'd by the coil of his crystalline streams,"

    # ....................{ PASS                           }....................
    # Assert that the above function passed lists both satisfying and violating
    # this type guard returns the expected booleans.
    assert is_typeguard_slow(
        ['Thou', 'who', 'didst', 'waken', 'from', 'his', 'summer', 'dreams']
    ) is True
    assert is_typeguard_slow(
        ['Thou', 'who', 'didst', 'waken', 'from', 'his', 'summer', b'dreams']
    ) is False

    # ....................{ FAIL                           }....................
    # Assert that @beartype raises the expected exception when decorating a
    # callable accepting one or more parameters erroneously annotated by a PEP
    # 647-compliant type guard.
    with raises(BeartypeDecorHintPep647Exception):
        @beartype
        def the_blue_mediterranean(where_he_lay: TypeGuard[str]) -> bool:
            return where_he_lay

    # Assert that @beartype raises the expected violation when calling a
    # callable erroneously violating a PEP 647-compliant type guard.
    with raises(BeartypeCallHintReturnViolation):
        is_typeguard_bad(('Beside a', 'pumice isle', 'in', "Baiae's bay,",))


@skip_if_python_version_less_than('3.13.0')
def test_decor_pep742() -> None:
    '''
    Test :pep:`742` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.13 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintReturnViolation,
        BeartypeDecorHintPep742Exception,
    )
    from beartype.typing import (
        List,
        TypeIs,
        Tuple,
    )
    from pytest import raises

    # ....................{ FUNCTIONS                      }....................
    @beartype
    def is_typeguard_slow(lst: List[object]) -> TypeIs[List[str]]:
        '''
        :pep:`742`-compliant type guard returning :data:`True` only if the
        passed list contains only string items via the standard linear runtime
        type-check implemented manually.

        *leisurely barfs into adjacent bucket*
        '''

        return all(isinstance(item, str) for item in lst)


    @beartype
    def is_typeguard_bad(tup: Tuple[object, ...]) -> TypeIs[Tuple[int, ...]]:
        '''
        :pep:`742`-compliant type guard erroneously (presumably, accidentally)
        violating :pep:`742` by returning a non-boolean object.
        '''

        return 'He hath prepared, prowling around the world;'

    # ....................{ PASS                           }....................
    # Assert that the above function passed lists both satisfying and violating
    # this type guard returns the expected booleans.
    assert is_typeguard_slow(
        ['Glutted', 'with', 'which', 'thou', 'mayst', 'repose,', 'and', 'men']
    ) is True
    assert is_typeguard_slow(
        ['Glutted', 'with', 'which', 'thou', 'mayst', 'repose,', 'and', b'men']
    ) is False

    # ....................{ FAIL                           }....................
    # Assert that @beartype raises the expected exception when decorating a
    # callable accepting one or more parameters erroneously annotated by a PEP
    # 742-compliant type guard.
    with raises(BeartypeDecorHintPep742Exception):
        @beartype
        def he_hath_prepared(prowling_around_the_world: TypeIs[str]) -> bool:
            return prowling_around_the_world

    # Assert that @beartype raises the expected violation when calling a
    # callable erroneously violating a PEP 742-compliant type guard.
    with raises(BeartypeCallHintReturnViolation):
        is_typeguard_bad((
            'Go', 'to', 'their', 'graves', 'like', 'flowers',
            'or', 'creeping', 'worms,'
        ))
