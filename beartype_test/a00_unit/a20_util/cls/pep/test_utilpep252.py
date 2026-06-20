#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`252`-compliant **dataclass utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cls.pep.clspep252` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester : type              }....................
def test_is_type_pep252_descriptor_data() -> None:
    '''
    Test the :func:`beartype._util.cls.pep.clspep252.is_type_pep252_descriptor_data`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.cls.pep.clspep252 import is_type_pep252_descriptor_data
    from beartype_test.a00_unit.data.pep.data_pep252 import (
        DataDescriptor,
        NondataDescriptor,
    )

    # ....................{ PASS                           }....................
    # Assert that this tester accepts a data descriptor type.
    assert is_type_pep252_descriptor_data(DataDescriptor) is True

    # ....................{ FAIL                           }....................
    # Assert that this tester rejects an unrelated type.
    assert is_type_pep252_descriptor_data(str) is False

    # Assert that this tester rejects a non-data descriptor type.
    assert is_type_pep252_descriptor_data(NondataDescriptor) is False


def test_is_type_pep252_descriptor_nondata() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.clspep252.is_type_pep252_descriptor_nondata`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.cls.pep.clspep252 import (
        is_type_pep252_descriptor_nondata)
    from beartype_test.a00_unit.data.pep.data_pep252 import (
        DataDescriptor,
        NondataDescriptor,
    )

    # ....................{ PASS                           }....................
    # Assert that this tester accepts a non-data descriptor type.
    assert is_type_pep252_descriptor_nondata(NondataDescriptor) is True

    # ....................{ FAIL                           }....................
    # Assert that this tester rejects an unrelated type.
    assert is_type_pep252_descriptor_nondata(str) is False

    # Assert that this tester rejects a data descriptor type.
    assert is_type_pep252_descriptor_nondata(DataDescriptor) is False

# ....................{ TESTS ~ tester : instance          }....................
def test_is_object_pep252_descriptor_instance_all() -> None:
    '''
    Test both the
    :func:`beartype._util.cls.pep.clspep252.is_object_pep252_descriptor_data`
    *and*
    :func:`beartype._util.cls.pep.clspep252.is_object_pep252_descriptor_nondata`
    testers, whose validation is similar enough to warrant centralization into
    this single unit test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.cls.pep.clspep252 import (
        is_object_pep252_descriptor_data_instance,
        is_object_pep252_descriptor_nondata_instance,
    )
    from beartype_test.a00_unit.data.pep.data_pep252 import (
        DataAndNondataDescriptorStore,
        DataDescriptor,
        NondataDescriptor,
    )

    # ....................{ LOCALS                         }....................
    # Tuple of this pair of testers to be tested.
    object_descriptor_instance_testers = (
        is_object_pep252_descriptor_data_instance,
        is_object_pep252_descriptor_nondata_instance,
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
    assert is_object_pep252_descriptor_data_instance(
        descriptor_data_instance) is True

    # Assert that this tester accepts a non-data descriptor instance.
    assert is_object_pep252_descriptor_nondata_instance(
        descriptor_nondata_instance) is True

    # ....................{ FAIL                           }....................
    # Assert that this tester rejects a data descriptor instance.
    assert is_object_pep252_descriptor_nondata_instance(
        descriptor_data_instance) is False

    # Assert that this tester rejects a non-data descriptor instance.
    assert is_object_pep252_descriptor_data_instance(
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
