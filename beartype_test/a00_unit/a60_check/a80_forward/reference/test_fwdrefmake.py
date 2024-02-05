#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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

# ....................{ TESTS                              }....................
def test_make_forwardref_indexable_subtype() -> None:
    '''
    Test the
    :func:`beartype._check.forward.reference.fwdrefmake.make_forwardref_indexable_subtype`
    factory.
    '''

    # ....................{ LOCALS                         }....................
    # Defer test-specific imports.
    from beartype.roar import (
        BeartypeCallHintForwardRefException,
        BeartypeDecorHintForwardRefException,
    )
    from beartype._check.forward.reference.fwdrefmake import (
        make_forwardref_indexable_subtype)
    from beartype_test.a00_unit.data._check.forward.data_fwdref import (
        FORWARDREF_RELATIVE_CIRCULAR)
    from beartype_test.a00_unit.data.data_type import (
        Class,
        Subclass,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Fully-qualified name of a subpackage defining an arbitrary submodule.
    PACKAGE_NAME = 'beartype_test.a00_unit.data'

    # Unqualified basename of a submodule in that subpackage defining an
    # arbitrary class.
    MODULE_BASENAME = 'data_type'

    # Fully-qualified name of the same submodule.
    MODULE_NAME = f'{PACKAGE_NAME}.{MODULE_BASENAME}'

    # Unqualified basename of that class in that module.
    CLASS_BASENAME = 'Class'

    # Fully-qualified name of that class.
    CLASS_NAME = f'{MODULE_NAME}.{CLASS_BASENAME}'

    # Arbitrary instance of a subclass of that class.
    obj_subclass = Subclass()

    # Forward reference proxy to an unsubscripted class referenced with an
    # absolute (i.e., fully-qualified) name.
    fwdref_absolute = make_forwardref_indexable_subtype(
        # Intentionally ignored fully-qualified name of this test submodule.
        __name__,
        f'{MODULE_NAME}.{CLASS_BASENAME}',
    )

    # Forward reference proxy to an unsubscripted class referenced with a
    # relative (i.e., unqualified) name.
    fwdref_relative = make_forwardref_indexable_subtype(
        MODULE_NAME, CLASS_BASENAME)

    # Forward reference proxy to a submodule of a subpackage referenced with an
    # absolute (i.e., fully-qualified) name.
    fwdref_module_absolute = make_forwardref_indexable_subtype(
        # Intentionally ignored fully-qualified name of this test submodule.
        __name__,
        f'{PACKAGE_NAME}.{MODULE_BASENAME}',
    )

    # Forward reference proxy to an unsubscripted class of that submodule
    # referenced with "."-delimited attribute syntax from an existing forward
    # reference proxy.
    fwdref_module_class = fwdref_module_absolute.Class

    # ....................{ PASS ~ attr                    }....................
    # Assert that these proxies have the expected class names.
    assert fwdref_absolute.__name__ == CLASS_BASENAME
    assert fwdref_relative.__name__ == CLASS_BASENAME
    assert fwdref_module_absolute.__name__ == MODULE_BASENAME
    assert fwdref_module_class.__name__ == CLASS_BASENAME

    # Assert that these proxies have the expected module names.
    assert fwdref_absolute.__module__ == MODULE_NAME
    assert fwdref_relative.__module__ == MODULE_NAME
    assert fwdref_module_absolute.__module__ == PACKAGE_NAME
    assert fwdref_module_class.__module__ == f'{PACKAGE_NAME}.{MODULE_BASENAME}'

    # Assert that these proxies have the expected hint names.
    assert fwdref_absolute.__name_beartype__ == CLASS_NAME
    assert fwdref_relative.__name_beartype__ == CLASS_BASENAME
    assert fwdref_module_absolute.__name_beartype__ == MODULE_NAME
    assert fwdref_module_class.__name_beartype__ == CLASS_NAME

    # Assert that these proxies have the expected scope names.
    assert fwdref_absolute.__scope_name_beartype__ == __name__
    assert fwdref_relative.__scope_name_beartype__ == MODULE_NAME
    assert fwdref_module_absolute.__scope_name_beartype__ == __name__
    assert fwdref_module_class.__scope_name_beartype__ == __name__

    # ....................{ PASS ~ check                   }....................
    # Assert that an arbitrary instance of a subclass of that class is also an
    # instance of both of these proxies.
    assert isinstance(obj_subclass, fwdref_absolute)
    assert isinstance(obj_subclass, fwdref_relative)
    assert isinstance(obj_subclass, fwdref_module_class)

    # Assert that subclass is also a subclass of both of these proxies.
    assert issubclass(Subclass, fwdref_absolute)
    assert issubclass(Subclass, fwdref_relative)
    assert issubclass(Subclass, fwdref_module_class)

    # ....................{ PASS ~ property                }....................
    # Assert that this property of these forward reference proxies has the
    # expected values.
    assert fwdref_absolute.__type_beartype__ is Class
    assert fwdref_relative.__type_beartype__ is Class
    assert fwdref_module_class.__type_beartype__ is Class

    # ....................{ PASS ~ repr                    }....................
    # Machine-readable representation of a forward reference proxy.
    FORWARDREF_REPR = repr(fwdref_absolute)

    # Tuple of one or more substrings expected to be in this representation.
    FORWARDREF_REPR_SUBSTRS = (
        # Unqualified basename of the type this forward reference proxies.
        fwdref_absolute.__name__,
        # Machine-readable representations of all class variables of all
        # unsubscripted forward reference proxies.
        repr(fwdref_absolute.__scope_name_beartype__),
        repr(fwdref_absolute.__name_beartype__),
    )

    # Assert that this representation contains the expected substrings.
    for fwdref_repr_substr in FORWARDREF_REPR_SUBSTRS:
        assert fwdref_repr_substr in FORWARDREF_REPR

    # ....................{ FAIL                           }....................
    # Assert that attempting to access an undefined dunder attribute of a
    # forward reference proxy raises the expected exception.
    with raises(AttributeError):
        fwdref_absolute.__the_beating_of_her_heart_was_heard_to_fill__

    # Assert that attempting to instantiate a forward reference proxy raises the
    # expected exception.
    with raises(BeartypeDecorHintForwardRefException):
        fwdref_absolute()

    # Assert that attempting to validate a forward reference proxy to a module
    # as either an instance or subclass of a type raises the expected exception.
    with raises(BeartypeCallHintForwardRefException):
        isinstance(obj_subclass, fwdref_module_absolute)
    with raises(BeartypeCallHintForwardRefException):
        issubclass(Subclass, fwdref_module_absolute)

    # Assert that attempting to test an arbitrary object as an instance of a
    # circular forward reference proxy raises the expected exception.
    with raises(BeartypeCallHintForwardRefException):
        isinstance(obj_subclass, FORWARDREF_RELATIVE_CIRCULAR)

    # Assert that attempting to test an arbitrary type as a subclass of a
    # circular forward reference proxy raises the expected exception.
    with raises(BeartypeCallHintForwardRefException):
        issubclass(Subclass, FORWARDREF_RELATIVE_CIRCULAR)
