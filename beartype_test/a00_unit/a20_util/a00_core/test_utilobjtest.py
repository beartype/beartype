#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object getter utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.utilobjget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_object_hashable() -> None:
    '''
    Test the :func:`beartype._util.utilobjtest.is_object_hashable` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.utilobjtest import is_object_hashable
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS_HASHABLE,
        NOT_HINTS_UNHASHABLE,
    )

    # Assert that this tester accepts unhashable objects.
    for object_hashable in NOT_HINTS_HASHABLE:
        assert is_object_hashable(object_hashable) is True

    # Assert that this tester rejects unhashable objects.
    for object_unhashable in NOT_HINTS_UNHASHABLE:
        assert is_object_hashable(object_unhashable) is False

# ....................{ TESTS ~ tester : descriptor        }....................
def test_is_object_descriptor_instance() -> None:
    '''
    Test both the :func:`beartype._util.utilobjtest.is_object_descriptor_data`
    *and* :func:`beartype._util.utilobjtest.is_object_descriptor_nondata`
    testers, whose validation is similar enough to warrant centralization into
    this single unit test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.utilobjtest import (
        is_object_descriptor_data_instance,
        is_object_descriptor_nondata_instance,
    )
    from beartype_test.a00_unit.data.data_type import (
        DataAndNondataDescriptorStore,
        DataDescriptor,
        NondataDescriptor,
    )

    # ....................{ LOCALS                         }....................
    # Tuple of this pair of testers to be tested.
    object_descriptor_instance_testers = (
        is_object_descriptor_data_instance,
        is_object_descriptor_nondata_instance,
    )

    # Data and non-data descriptor instances, intentionally accessed directly on
    # the class dictionary underlying the descriptor store defining class
    # variables bound to these instances. Attempting to trivially access these
    # instances on this descriptor store would implicitly call the __get__()
    # dunder method and thus raise an exception. Look. It's complicated. *sigh*
    descriptor_data_instance = DataAndNondataDescriptorStore.__dict__[
        'var_writable']
    descriptor_nondata_instance = DataAndNondataDescriptorStore.__dict__[
        'var_readonly']

    # ....................{ PASS                           }....................
    # Assert that this tester accepts a data descriptor instance.
    assert is_object_descriptor_data_instance(
        descriptor_data_instance) is True

    # Assert that this tester accepts a non-data descriptor instance.
    assert is_object_descriptor_nondata_instance(
        descriptor_nondata_instance) is True

    # ....................{ FAIL                           }....................
    # Assert that this tester rejects a data descriptor instance.
    assert is_object_descriptor_nondata_instance(
        descriptor_data_instance) is False

    # Assert that this tester rejects a non-data descriptor instance.
    assert is_object_descriptor_data_instance(
        descriptor_nondata_instance) is False

    # Assert that both of these testers...
    for object_descriptor_instance_tester in object_descriptor_instance_testers:
        # Reject unrelated objects.
        assert object_descriptor_instance_tester(
            'I saw my first-born tumbled from his throne!') is False

        # Reject arbitrary types, including the types of both data and non-data
        # descriptors.
        assert object_descriptor_instance_tester(str) is False
        assert object_descriptor_instance_tester(DataDescriptor) is False
        assert object_descriptor_instance_tester(NondataDescriptor) is False
