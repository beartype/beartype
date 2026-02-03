#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type-check call metadata dataclass** unit tests.

This submodule unit tests the
:func:`beartype._check.metadata.call.callmetadecormin` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_callmetadecormin() -> None:
    '''
    Test the
    :func:`beartype._check.metadata.call.callmetadecormin.BeartypeCallDecorMinimalMeta`
    dataclass.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype._check.metadata.call.callmetadecor import (
        BeartypeCallDecorMeta)
    from beartype._check.metadata.call.callmetadecormin import (
        BeartypeCallDecorMinimalMeta)
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
    decor_meta = BeartypeCallDecorMeta()
    decor_meta.reinit(
        func=function_wrappee, conf=conf, cls_stack=cls_stack)

    # Minimal metadata reduced from this maximal metadata.
    decor_min_meta = decor_meta.minify()

    # ....................{ PASS                           }....................
    # Assert that this minimal metadata is an instance of the expected type.
    assert isinstance(decor_min_meta, BeartypeCallDecorMinimalMeta)

    # Assert that this minimal metadata exposes the expected fields.
    assert decor_min_meta.func is function_wrappee
    assert decor_min_meta.conf is conf
    assert decor_min_meta.cls_stack is cls_stack
    assert decor_min_meta.func_annotations is decor_meta.func_annotations
