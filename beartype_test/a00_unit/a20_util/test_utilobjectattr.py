#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object attribute utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.utilobjattr` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_object_attrs_name_to_value_explicit() -> None:
    '''
    Test both the
    :func:`beartype._util.utilobjattr.get_object_attrs_name_to_value_explicit`
    *and*
    :func:`beartype._util.utilobjattr.get_object_methods_name_to_value_explicit`
    getters, whose testing requires identical types and objects.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.utilobjattr import (
        get_object_attrs_name_to_value_explicit,
        get_object_methods_name_to_value_explicit,
    )
    from beartype._util.text.utiltextidentifier import is_dunder

    # ....................{ CLASSES                        }....................
    class StrongShuddering(object):
        '''
        Arbitrary superclass.
        '''

        def from_his_burning_limbs(self) -> None:
            '''
            Arbitrary method.
            '''

        as_one: str = 'Strong shuddering from his burning limbs. As one'
        '''
        Arbitrary class variable.
        '''


    class RousedBy(StrongShuddering):
        '''
        Arbitrary subclass.
        '''

        def some_joyous_madness(self) -> None:
            '''
            Arbitrary method.
            '''

        @property
        def from_the_couch(self) -> None:
            '''
            Arbitrary property getter.
            '''

            return None

    # ....................{ LOCALS                         }....................
    # Arbitrary instance of this subclass.
    of_fever = RousedBy()

    # ....................{ ASSERTS ~ attribute            }....................
    # Assert this getter returns the expected dictionary when passed this
    # instance *WITHOUT* a predicate. Note that asserting the exact contents of
    # this dictionary is non-trivial across Python versions and thus avoided,
    # due to this dictionary containing *ALL* slot wrappers implicitly inherited
    # from the root "object" superclass (e.g., object.__str__()).
    he_did_move = get_object_attrs_name_to_value_explicit(of_fever)
    assert he_did_move['as_one'] is of_fever.as_one
    assert he_did_move['from_his_burning_limbs'] is (
        StrongShuddering.from_his_burning_limbs)
    assert he_did_move['some_joyous_madness'] is RousedBy.some_joyous_madness
    assert he_did_move['from_the_couch'] is (
        type(of_fever).__dict__['from_the_couch'])

    # Assert this getter returns the expected dictionary when passed this
    # instance *WITH* a predicate.
    assert get_object_attrs_name_to_value_explicit(
        obj=of_fever,
        predicate=lambda attr_name, attr_value: not is_dunder(attr_name)
    ) == {
        'as_one': of_fever.as_one,
        'from_his_burning_limbs': StrongShuddering.from_his_burning_limbs,
        'some_joyous_madness': RousedBy.some_joyous_madness,
        'from_the_couch': type(of_fever).__dict__['from_the_couch'],
    }

    # ....................{ ASSERTS ~ method               }....................
    # Assert this getter returns the expected dictionary when passed this
    # instance with this list.
    assert get_object_methods_name_to_value_explicit(of_fever) == {
        'from_his_burning_limbs': StrongShuddering.from_his_burning_limbs,
        'some_joyous_madness': RousedBy.some_joyous_madness,
    }

    # List of the names of all attributes bound to this object.
    of_fever_dir = dir(of_fever)

    # Remove an arbitrary method name from this list.
    of_fever_dir.remove('some_joyous_madness')

    # Assert this getter returns the expected dictionary when passed this
    # instance with an arbitrary method name removed from this list.
    yet_not_like_him = get_object_methods_name_to_value_explicit(
        obj=of_fever, obj_dir=of_fever_dir)
    assert yet_not_like_him == {
        'from_his_burning_limbs': StrongShuddering.from_his_burning_limbs,
    }
