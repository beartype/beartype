#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator **forward reference utility** unit tests.

This submodule unit tests the :func:`beartype._check.forward._fwdref` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_make_forwardref_indexable_subtype() -> None:
    '''
    Test the
    :func:`beartype._check.forward._fwdref.make_forwardref_indexable_subtype`
    factory.
    '''

    # ....................{ LOCALS                         }....................
    # Defer test-specific imports.
    from beartype._check.forward._fwdref import (
        make_forwardref_indexable_subtype)
    from beartype_test.a00_unit.data.data_type import Subclass
    # from pytest import raises

    # ....................{ LOCALS                         }....................
    # Fully-qualified name of a module containing an arbitrary class.
    MODULE_NAME = 'beartype_test.a00_unit.data.data_type'

    # Unqualified basename of that class in that module.
    CLASS_NAME = 'Class'

    # Arbitrary instance of a subclass of that class.
    instance = Subclass()

    # Forward reference proxy to an unsubscripted class referenced with an
    # absolute (i.e., fully-qualified) name.
    forwardref_absolute = make_forwardref_indexable_subtype(
        # Ignorable fully-qualified name of the current test module.
        __name__,
        f'{MODULE_NAME}.{CLASS_NAME}',
    )

    # Forward reference proxy to an unsubscripted class referenced with an
    # relative (i.e., unqualified) name.
    forwardref_relative = make_forwardref_indexable_subtype(
        MODULE_NAME, CLASS_NAME)

    # ....................{ PASS                           }....................
    # Assert that these proxies have the expected class names.
    assert forwardref_absolute.__name__ == CLASS_NAME
    assert forwardref_relative.__name__ == CLASS_NAME

    # Assert that these proxies have the expected module names.
    assert forwardref_absolute.__module__ == MODULE_NAME
    assert forwardref_relative.__module__ == MODULE_NAME

    # Assert that these proxies have the expected hint names.
    assert forwardref_absolute.__beartype_name__ == (
        f'{MODULE_NAME}.{CLASS_NAME}')
    assert forwardref_relative.__beartype_name__ == CLASS_NAME

    # Assert that these proxies have the expected scope names.
    assert forwardref_absolute.__beartype_scope_name__ == __name__
    assert forwardref_relative.__beartype_scope_name__ == MODULE_NAME

    # Assert that an arbitrary instance of a subclass of that class is also an
    # instance of both of these proxies.
    assert isinstance(instance, forwardref_absolute)
    assert isinstance(instance, forwardref_relative)

    # Assert that subclass is also a subclass of both of these proxies.
    assert issubclass(Subclass, forwardref_absolute)
    assert issubclass(Subclass, forwardref_relative)
