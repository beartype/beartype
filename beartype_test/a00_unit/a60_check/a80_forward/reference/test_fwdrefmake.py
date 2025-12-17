#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator **forward reference factory** unit tests.

This submodule unit tests the
:func:`beartype._check.forward.reference.fwdrefmake` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# NOTE: This module-scope import is required for the nested class forward
# reference test below (see "PASS ~ nested" section). Frame inspection in
# _make_forwardref_subtype() uses hasattr(module, 'Class') to find modules that
# define a class. Function-local imports do NOT make the class a module
# attribute, so we must import at module scope for the test to work.
# See: https://github.com/beartype/beartype/issues/603
from beartype_test.a00_unit.data.data_type import Class

# ....................{ TESTS                              }....................
def test_make_forwardref_indexable_subtype() -> None:
    '''
    Test the
    :func:`beartype._check.forward.reference.fwdrefmake.make_forwardref_indexable_subtype`
    factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import (
        BeartypeCallHintForwardRefException,
        BeartypeDecorHintForwardRefException,
    )
    from beartype._check.forward.reference.fwdrefmake import (
        make_forwardref_indexable_subtype,
    )
    from beartype_test.a00_unit.data.check.forward.data_fwdref import (
        CLASS_BASENAME,
        CLASS_NAME,
        FORWARDREF_ABSOLUTE,
        FORWARDREF_MODULE_ABSOLUTE,
        FORWARDREF_MODULE_CLASS,
        FORWARDREF_RELATIVE,
        FORWARDREF_RELATIVE_CIRCULAR,
        MODULE_BASENAME,
        MODULE_NAME,
        PACKAGE_NAME,
        SCOPE_NAME,
    )
    from beartype_test.a00_unit.data.data_type import (
        Class,
        Subclass,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Arbitrary instance of a subclass of that class.
    obj_subclass = Subclass()

    # ....................{ PASS ~ attr                    }....................
    # Assert that these proxies have the expected class names.
    assert FORWARDREF_ABSOLUTE.__name__ == CLASS_BASENAME
    assert FORWARDREF_RELATIVE.__name__ == CLASS_BASENAME
    assert FORWARDREF_MODULE_ABSOLUTE.__name__ == MODULE_BASENAME
    assert FORWARDREF_MODULE_CLASS.__name__ == CLASS_BASENAME

    # Assert that these proxies have the expected module names.
    assert FORWARDREF_ABSOLUTE.__module__ == MODULE_NAME
    assert FORWARDREF_RELATIVE.__module__ == MODULE_NAME
    assert FORWARDREF_MODULE_ABSOLUTE.__module__ == PACKAGE_NAME
    assert FORWARDREF_MODULE_CLASS.__module__ == (
        f'{PACKAGE_NAME}.{MODULE_BASENAME}')

    # Assert that these proxies have the expected hint names.
    assert FORWARDREF_ABSOLUTE.__name_beartype__ == CLASS_NAME
    assert FORWARDREF_RELATIVE.__name_beartype__ == CLASS_BASENAME
    assert FORWARDREF_MODULE_ABSOLUTE.__name_beartype__ == MODULE_NAME
    assert FORWARDREF_MODULE_CLASS.__name_beartype__ == CLASS_NAME

    # Assert that these proxies have the expected scope names.
    assert FORWARDREF_ABSOLUTE.__scope_name_beartype__ == SCOPE_NAME
    assert FORWARDREF_RELATIVE.__scope_name_beartype__ == MODULE_NAME
    assert FORWARDREF_MODULE_ABSOLUTE.__scope_name_beartype__ == SCOPE_NAME
    assert FORWARDREF_MODULE_CLASS.__scope_name_beartype__ == SCOPE_NAME

    # ....................{ PASS ~ check                   }....................
    # Assert that an instance of a subclass of that class is also an instance of
    # these proxies.
    assert isinstance(obj_subclass, FORWARDREF_ABSOLUTE)
    assert isinstance(obj_subclass, FORWARDREF_RELATIVE)
    assert isinstance(obj_subclass, FORWARDREF_MODULE_CLASS)

    # Assert that that subclass is also a subclass of both of these proxies.
    assert issubclass(Subclass, FORWARDREF_ABSOLUTE)
    assert issubclass(Subclass, FORWARDREF_RELATIVE)
    assert issubclass(Subclass, FORWARDREF_MODULE_CLASS)

    # ....................{ PASS ~ property                }....................
    # Assert that this property of these forward reference proxies has the
    # expected values.
    assert FORWARDREF_ABSOLUTE.__type_beartype__ is Class
    assert FORWARDREF_RELATIVE.__type_beartype__ is Class
    assert FORWARDREF_MODULE_CLASS.__type_beartype__ is Class

    # ....................{ PASS ~ repr                    }....................
    # Machine-readable representation of a forward reference proxy.
    FORWARDREF_REPR = repr(FORWARDREF_ABSOLUTE)

    # Tuple of one or more substrings expected to be in this representation.
    FORWARDREF_REPR_SUBSTRS = (
        # Unqualified basename of the type this forward reference proxies.
        FORWARDREF_ABSOLUTE.__name__,
        # Machine-readable representations of all class variables of all
        # unsubscripted forward reference proxies.
        repr(FORWARDREF_ABSOLUTE.__scope_name_beartype__),
        repr(FORWARDREF_ABSOLUTE.__name_beartype__),
    )

    # Assert that this representation contains the expected substrings.
    for fwdref_repr_substr in FORWARDREF_REPR_SUBSTRS:
        assert fwdref_repr_substr in FORWARDREF_REPR

    # ....................{ PASS ~ nested                  }....................
    # Test nested class forward references where the first component is a class
    # rather than a module. This exercises the frame inspection fallback in
    # _make_forwardref_subtype.
    #
    # To trigger frame inspection, we pass a scope_name that CANNOT resolve
    # "Class". The frame inspection code will iterate through the call stack
    # and find this test module, which has "Class" imported above. It will then
    # use this test module as the scope for resolving the nested class.

    # A scope that does NOT define "Class", forcing frame inspection fallback.
    UNRELATED_SCOPE = 'beartype._util.module.utilmodimport'

    # Create a forward reference proxy to a nested class. Since UNRELATED_SCOPE
    # cannot resolve "Class", the code must use frame inspection to find that
    # this test module has "Class" imported.
    forwardref_nested = make_forwardref_indexable_subtype(
        scope_name=UNRELATED_SCOPE,
        hint_name='Class.NestedClass',
    )

    # Assert the forward reference proxy has the expected attributes.
    # The scope_name should have been updated to this test module's name
    # by the frame inspection logic.
    assert forwardref_nested.__name__ == 'NestedClass'
    assert forwardref_nested.__name_beartype__ == 'Class.NestedClass'

    # Assert the forward reference proxy resolves to the correct type.
    assert forwardref_nested.__type_beartype__ is Class.NestedClass

    # Assert isinstance checks work with the nested class forward reference.
    nested_instance = Class.NestedClass()
    assert isinstance(nested_instance, forwardref_nested)

    # ....................{ FAIL                           }....................
    # Assert that attempting to access an undefined dunder attribute of a
    # forward reference proxy raises the expected exception.
    with raises(AttributeError):
        FORWARDREF_ABSOLUTE.__the_beating_of_her_heart_was_heard_to_fill__

    # Assert that attempting to instantiate a forward reference proxy raises the
    # expected exception.
    with raises(BeartypeDecorHintForwardRefException):
        FORWARDREF_ABSOLUTE()

    # Assert that attempting to validate a forward reference proxy to a module
    # as either an instance or subclass of a type raises the expected exception.
    with raises(BeartypeCallHintForwardRefException):
        isinstance(obj_subclass, FORWARDREF_MODULE_ABSOLUTE)
    with raises(BeartypeCallHintForwardRefException):
        issubclass(Subclass, FORWARDREF_MODULE_ABSOLUTE)

    # Assert that attempting to test an arbitrary object as an instance of a
    # circular forward reference proxy raises the expected exception.
    with raises(BeartypeCallHintForwardRefException):
        isinstance(obj_subclass, FORWARDREF_RELATIVE_CIRCULAR)

    # Assert that attempting to test an arbitrary type as a subclass of a
    # circular forward reference proxy raises the expected exception.
    with raises(BeartypeCallHintForwardRefException):
        issubclass(Subclass, FORWARDREF_RELATIVE_CIRCULAR)

    # Assert that attempting to test an undefined *NON-DUNDER* attribute of a
    # forward reference proxy raises the expected exception *AFTER* that same
    # forward reference proxy has already resolved its referent due to a prior
    # call to the isinstance() or issubclass() builtins against this proxy.
    with raises(AttributeError):
        FORWARDREF_MODULE_CLASS.and_buried_from_all_godlike_exercise
