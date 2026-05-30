#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
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
def test_get_object_attr_name_to_value() -> None:
    '''
    Test the family of public attribute getters defined by the
    :func:`beartype._util.utilobjattr` submodule, whose testing requires
    identical types and objects and is thus centralized in this single test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
    from beartype._util.utilobjattr import (
        get_object_attr_name_to_value,
        get_object_method_name_to_value,
        get_object_nonmethod_name_to_value,
    )
    from beartype._util.text.utiltextidentifier import is_dunder
    from pytest import raises

    # ....................{ CLASSES                        }....................
    class StrongShuddering(object):
        '''
        Arbitrary superclass.
        '''

        as_one: str = 'Strong shuddering from his burning limbs. As one'
        '''
        Arbitrary class variable.
        '''

        def from_his_burning_limbs(self) -> None:
            '''
            Arbitrary method.
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

    # ....................{ CALLABLES                      }....................
    def is_object_attr_nondunder(attr_name: str, attr_value: object) -> bool:
        '''
        :data:`True` only if the arbitrary object attribute with the passed name
        and value is *not* a **dunder** (i.e., attribute whose name is both
        prefixed and suffixed by double underscores).

        This function is intended to be passed as the ``predicate`` parameter of
        the :func:`.get_object_attr_name_to_value` getter.
        '''

        return not is_dunder(attr_name)

    # ....................{ LOCALS                         }....................
    # Arbitrary instance of this subclass.
    of_fever = RousedBy()

    # ....................{ CONSTANTS                      }....................
    # List of the names of all attributes bound to this object.
    OF_FEVER_DIR = dir(of_fever)

    # Dictionary mapping from the names to values of all non-dunder methods
    # bound to this object.
    OF_FEVER_METHOD_NAME_TO_VALUE = {
        'from_his_burning_limbs': StrongShuddering.from_his_burning_limbs,
        'some_joyous_madness': RousedBy.some_joyous_madness,
    }

    # Dictionary mapping from the names to values of all non-dunder non-method
    # attributes bound to this object.
    OF_FEVER_NONMETHOD_NAME_TO_VALUE = {
        'as_one': of_fever.as_one,
        'from_the_couch': type(of_fever).__dict__['from_the_couch'],
    }

    # Dictionary mapping from the names to values of all non-dunder attributes
    # bound to this object, defined by manually merging the lesser dictionaries
    # defined above.
    OF_FEVER_ATTR_NONDUNDER_NAME_TO_VALUE = dict(OF_FEVER_METHOD_NAME_TO_VALUE)
    OF_FEVER_ATTR_NONDUNDER_NAME_TO_VALUE.update(
        OF_FEVER_NONMETHOD_NAME_TO_VALUE)

    # Frozen set of the names of *ALL* non-dunder attributes bound to this
    # object.
    OF_FEVER_ATTR_NONDUNDER_NAMES_ALL = frozenset(
        OF_FEVER_ATTR_NONDUNDER_NAME_TO_VALUE.keys())

    # ....................{ PASS ~ attr                    }....................
    # Assert that this getter returns the expected dictionary when passed this
    # object *WITHOUT* a predicate. Note that asserting the exact contents of
    # this dictionary is non-trivial across Python versions and thus avoided,
    # due to this dictionary containing *ALL* slot wrappers implicitly inherited
    # from the root "object" superclass (e.g., object.__str__()).
    of_fever_attrs_actual = get_object_attr_name_to_value(of_fever)
    assert (
        OF_FEVER_ATTR_NONDUNDER_NAME_TO_VALUE.items() <=
        of_fever_attrs_actual.items()
    )

    # Assert that this getter returns the expected dictionary when passed this
    # object *WITH* a functional predicate but *NO* precomputed predicate (i.e.,
    # "predicate_attr_names_*" parameter).
    assert get_object_attr_name_to_value(
        obj=of_fever, predicate=is_object_attr_nondunder,
    ) == OF_FEVER_ATTR_NONDUNDER_NAME_TO_VALUE

    # ....................{ PASS ~ attr : any              }....................
    # Assert that this getter returns the expected dictionary when passed this
    # object *WITH* both a functional predicate and the precomputed predicate
    # "predicate_attr_names_any" containing the names of one or attributes also
    # bound to this object.
    assert get_object_attr_name_to_value(
        obj=of_fever,
        predicate=is_object_attr_nondunder,
        predicate_attr_names_any=frozenset(('from_his_burning_limbs',))
    ) == OF_FEVER_ATTR_NONDUNDER_NAME_TO_VALUE

    # Assert that this getter returns the empty frozen dictionary singleton when
    # passed this object *WITH* both a functional predicate and the precomputed
    # predicate "predicate_attr_names_any" containing the names of *NO*
    # attributes also bound to this object.
    assert get_object_attr_name_to_value(
        obj=of_fever,
        predicate=is_object_attr_nondunder,
        predicate_attr_names_any=frozenset(('and_at_the_fruits_thereof',))
    ) is FROZENDICT_EMPTY

    # ....................{ PASS ~ attr : all              }....................
    # Assert that this getter returns the expected dictionary when passed this
    # object *WITH* both a functional predicate and the precomputed predicate
    # "predicate_attr_names_all" containing the names of *ALL* non-dunder
    # attributes also bound to this object.
    assert get_object_attr_name_to_value(
        obj=of_fever,
        predicate=is_object_attr_nondunder,
        predicate_attr_names_all=OF_FEVER_ATTR_NONDUNDER_NAMES_ALL,
    ) == OF_FEVER_ATTR_NONDUNDER_NAME_TO_VALUE

    # Assert that this getter returns the empty frozen dictionary singleton when
    # passed this object *WITH* both a functional predicate and the precomputed
    # predicate "predicate_attr_names_all" containing both the names of *ALL*
    # non-dunder attributes also bound to this object as well as the name of
    # one attribute *NOT* bound to this object.
    assert get_object_attr_name_to_value(
        obj=of_fever,
        predicate=is_object_attr_nondunder,
        predicate_attr_names_all=(
            OF_FEVER_ATTR_NONDUNDER_NAMES_ALL |
            frozenset(('what_shapes_they_be',))
        ),
    ) is FROZENDICT_EMPTY

    # ....................{ PASS ~ method                  }....................
    # Assert that this getter returns the expected dictionary of methods when
    # passed this object *WITHOUT* a predicate. Note that asserting the exact
    # contents of this dictionary is non-trivial across Python versions and thus
    # avoided. Although asserting the contents of this dictionary was trivial
    # under Python <= 3.13, Python >= 3.14 complicates comparisons by
    # introducing dynamically instantiated bound methods for certain contexts,
    # including:
    # * The __annotate_func__() dunder method, which CPython now implicitly
    #   defines for *ALL* types declaring one or more class variables annotated
    #   by type hints.
    of_fever_methods_actual = get_object_method_name_to_value(of_fever)
    assert (
        OF_FEVER_METHOD_NAME_TO_VALUE.items() <=
        of_fever_methods_actual.items()
    )

    # ....................{ PASS ~ method : dir            }....................
    # Remove an arbitrary method name from this list.
    OF_FEVER_DIR.remove('some_joyous_madness')
    OF_FEVER_METHOD_NAME_TO_VALUE.pop('some_joyous_madness')

    # Assert that this getter returns the expected dictionary when passed this
    # instance with an arbitrary method name removed from this list.
    of_fever_methods_actual = get_object_method_name_to_value(
        obj=of_fever, obj_dir=OF_FEVER_DIR)
    assert (
        OF_FEVER_METHOD_NAME_TO_VALUE.items() <=
        of_fever_methods_actual.items()
    )

    # ....................{ PASS ~ method                  }....................
    # Assert that this getter returns the expected dictionary of non-method
    # attributes when passed this object *WITHOUT* a predicate. Note that
    # similar caveats apply as above.
    of_fever_nonmethods_actual = get_object_nonmethod_name_to_value(of_fever)
    assert (
        OF_FEVER_NONMETHOD_NAME_TO_VALUE.items() <=
        of_fever_nonmethods_actual.items()
    )

    # ....................{ FAIL                           }....................
    # Assert that this getter raises the expected exception when passed invalid
    # one or more parameters.
    with raises(AssertionError):
        get_object_attr_name_to_value(
            obj=of_fever, obj_dir='All unrevealed even to the powers')
    with raises(AssertionError):
        get_object_attr_name_to_value(
            obj=of_fever, predicate='Which met at thy creating; at whose joys')
    with raises(AssertionError):
        get_object_attr_name_to_value(
            obj=of_fever,
            predicate_attr_names_all=(
                'And palpitations sweet, and pleasures soft,'),
        )
    with raises(AssertionError):
        get_object_attr_name_to_value(
            obj=of_fever,
            predicate_attr_names_any=(
                'I, Coelus, wonder, how they came and whence;'),
        )
