#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint factory** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.utilhintfactory` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_typehinttypefactory() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhintfactory.TypeHintTypeFactory`
    class.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.utilhintfactory import TypeHintTypeFactory

    # Arbitrary instance of this factory.
    bool_factory = TypeHintTypeFactory(bool)

    # Assert that this class memoizes this factory on the passed type.
    assert bool_factory is TypeHintTypeFactory(bool)

    # Assert that this factory unconditionally returns this type when
    # subscripted by any arbitrary object.
    assert bool_factory['The still and solemn power of many sights,'] is bool
