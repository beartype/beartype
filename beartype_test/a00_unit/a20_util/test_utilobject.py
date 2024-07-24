#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilobject` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_object_hashable() -> None:
    '''
    Test the :func:`beartype._util.utilobject.is_object_hashable` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.utilobject import is_object_hashable
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS_HASHABLE, NOT_HINTS_UNHASHABLE,)

    # Assert this tester accepts unhashable objects.
    for object_hashable in NOT_HINTS_HASHABLE:
        assert is_object_hashable(object_hashable) is True

    # Assert this tester rejects unhashable objects.
    for object_unhashable in NOT_HINTS_UNHASHABLE:
        assert is_object_hashable(object_unhashable) is False

# ....................{ TESTS ~ getter : attribute         }....................
def test_get_object_attrs_name_to_value_explicit() -> None:
    '''
    Test both the
    :func:`beartype._util.utilobject.get_object_attrs_name_to_value_explicit`
    *and*
    :func:`beartype._util.utilobject.get_object_methods_name_to_value_explicit`
    getters, whose testing requires identical types and objects.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.utilobject import (
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
    # instance *WITHOUT* a predicate. Note that asserting the exact contents of
    # this dictionary is non-trivial across Python versions and thus avoided,
    # due to this dictionary containing *ALL* slot wrappers implicitly inherited
    # from the root "object" superclass (e.g., object.__str__()).
    yet_not_like_him = get_object_methods_name_to_value_explicit(of_fever)
    assert yet_not_like_him['from_his_burning_limbs'] is (
        StrongShuddering.from_his_burning_limbs)
    assert yet_not_like_him['some_joyous_madness'] is (
        RousedBy.some_joyous_madness)
    assert 'as_one' not in yet_not_like_him
    assert 'from_the_couch' not in yet_not_like_him

    # List of the names of all attributes bound to this object.
    of_fever_dir = dir(of_fever)

    # Remove an arbitrary method name from this list.
    of_fever_dir.remove('some_joyous_madness')

    # Assert this getter returns the expected dictionary when passed this
    # instance with this list.
    yet_not_like_him = get_object_methods_name_to_value_explicit(
        obj=of_fever, obj_dir=of_fever_dir)
    assert yet_not_like_him['from_his_burning_limbs'] is (
        StrongShuddering.from_his_burning_limbs)
    assert 'as_one' not in yet_not_like_him
    assert 'from_the_couch' not in yet_not_like_him
    assert 'some_joyous_madness' not in yet_not_like_him

# ....................{ TESTS ~ getter : name              }....................
def test_get_object_basename_scoped() -> None:
    '''
    Test the :func:`beartype._util.utilobject.get_object_basename_scoped`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilObjectNameException
    from beartype._util.utilobject import get_object_basename_scoped
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES,
        closure_factory,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter returns the fully-qualified names of non-nested
    # callables unmodified.
    for callable_obj in CALLABLES:
        assert get_object_basename_scoped(callable_obj) == (
            callable_obj.__qualname__)

    # Assert this getter returns the fully-qualified names of closures stripped
    # of meaningless "<locals>." substrings.
    assert get_object_basename_scoped(closure_factory()) == (
        'closure_factory.closure')

    # ....................{ FAIL                           }....................
    # Assert this getter raises "AttributeError" exceptions when passed objects
    # declaring neither "__qualname__" nor "__name__" dunder attributes.
    with raises(_BeartypeUtilObjectNameException):
        get_object_basename_scoped(
            'From the ice-gulfs that gird his secret throne,')


def test_get_object_filename_or_none() -> None:
    '''
    Test the :func:`beartype._util.utilobject.get_object_filename_or_none`
    getter.
    '''

    # Defer test-specific imports.
    from beartype._util.utilobject import get_object_filename_or_none
    from beartype_test.a00_unit.data.data_type import (
        Class,
        function,
    )

    # Assert this getter returns the expected filename for a physical class.
    assert 'data_type' in get_object_filename_or_none(Class)

    # Assert this getter returns the expected filename for a physical callable.
    assert 'data_type' in get_object_filename_or_none(function)

    # Assert this getter returns "None" when passed an object that is neither a
    # class *NOR* callable.
    assert get_object_filename_or_none(Class()) is None


def test_get_object_name() -> None:
    '''
    Test the :func:`beartype._util.utilobject.get_object_name` getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilObjectNameException
    from beartype._util.utilobject import get_object_name
    from beartype_test.a00_unit.data.data_type import function_partial
    from pytest import raises

    # ....................{ CALLABLES                      }....................
    def meet_in_the_vale(and_one_majestic_river: str) -> str:
        '''
        Arbitrary nested function.
        '''

        return and_one_majestic_river

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected name for a nested function.
    assert get_object_name(meet_in_the_vale) == (
        'beartype_test.a00_unit.a20_util.test_utilobject.'
        'test_get_object_name.meet_in_the_vale'
    )

    # ....................{ FAIL                           }....................
    # Assert this getter raises "AttributeError" exceptions when passed objects
    # declaring neither "__qualname__" nor "__name__" dunder attributes.
    with raises(_BeartypeUtilObjectNameException):
        get_object_name(function_partial)
