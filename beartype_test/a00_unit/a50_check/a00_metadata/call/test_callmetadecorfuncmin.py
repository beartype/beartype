#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable decorator call minimal metadata dataclass** unit tests.

This submodule unit tests the
:func:`beartype._check.cls.call.calldatadecorabc` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_callmetadecorfuncmin() -> None:
    '''
    Test the
    :func:`beartype._check.cls.call.calldatadecorfuncmin.BeartypeCallDecorFuncMinimalData`
    dataclass.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype._check.cls.call.calldatadecorfuncmin import (
        BeartypeCallDecorFuncMinimalData)
    from beartype._check.cls.call.calldatadecorfunc import (
        BeartypeCallDecorFuncData)
    from beartype_test.a00_unit.data.data_type import (
        Class,
        function_wrappee,
    )

    # ....................{ LOCALS                         }....................
    # Arbitrary beartype configuration.
    conf = BeartypeConf(is_debug=True)

    # Arbitrary class stack.
    cls_stack = (Class,)

    # Arbitrary beartype decorator call metadata.
    decor_func = BeartypeCallDecorFuncData()
    decor_func.reinit(
        func_wrappee=function_wrappee, conf=conf, cls_stack=cls_stack)

    # Minimal metadata reduced from this maximal metadata.
    decor_min_meta = decor_func.minify()

    # ....................{ PASS                           }....................
    # Assert that this minimal metadata is an instance of the expected type.
    assert isinstance(decor_min_meta, BeartypeCallDecorFuncMinimalData)

    # Assert that this minimal metadata exposes the expected fields.
    assert decor_min_meta.conf is conf
    assert decor_min_meta.cls_stack is cls_stack
    assert decor_min_meta.decoratee is function_wrappee
    assert decor_min_meta.decoratee_annotations is (
        decor_func.decoratee_annotations)
