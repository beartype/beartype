#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`593` unit tests.

This submodule unit tests :pep:`593` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_pep593() -> None:
    '''
    Test :pep:`593` support implemented in the :func:`beartype.beartype`
    decorator.

    Notably, this test exercises unsuccessful usage of the public
    :mod:`beartype.vale.Is` class when used to type hint callables decorated by
    the :func:`beartype.beartype` decorator.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype.vale import Is
    from beartype._util.api.standard.utiltyping import get_typing_attrs
    from pytest import raises

    # ..................{ FAIL                               }..................
    # For the "Annotated" type hint factory exported by each typing module...
    for Annotated in get_typing_attrs('Annotated'):
        # Assert that @beartype raises the expected exception when decorating a
        # callable annotated by a type metahint whose first argument is a
        # beartype-specific data validator and whose second argument is a
        # beartype-agnostic object.
        with raises(BeartypeDecorHintPep593Exception):
            @beartype
            def volleyed_and_thundered(
                flashed_all_their_sabres_bare: Annotated[
                    str,
                    Is[lambda text: bool('Flashed as they turned in air')],
                    'Sabring the gunners there,',
                ]
            ) -> str:
                return flashed_all_their_sabres_bare + 'Charging an army, while'
