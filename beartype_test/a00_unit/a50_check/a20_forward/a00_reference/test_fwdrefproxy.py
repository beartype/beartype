#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference proxy factory** unit tests.

This submodule unit tests the
:func:`beartype._check.forward.reference.fwdrefproxy` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_proxy_hint_pep484_ref_str_subbable() -> None:
    '''
    Test the
    :func:`beartype._check.forward.reference.fwdrefproxy.proxy_hint_pep484_ref_str_subbable`
    factory.
    '''

    # ....................{ LOCALS                         }....................
    # Defer test-specific imports.
    from beartype.roar import (
        BeartypeCallHintForwardRefException,
        BeartypeDecorHintForwardRefException,
    )
    from beartype_test.a00_unit.data.data_type import (
        Class,
        Subclass,
    )
    from beartype_test.a00_unit.data.pep.data_pep585 import Pep585Hint
    from beartype_test.a00_unit.data.pep.pep484.forward.data_pep484ref_proxy import (
        SCOPE_NAME,
        TYPE_BASENAME,
        TYPE_NAME,
        TYPE_SUBMODULE_BASENAME,
        TYPE_SUBMODULE_NAME,
        TYPE_SUBPACKAGE_NAME,
        hint_ref_str_proxy_absolute,
        type_ref_str_proxy_absolute,
        type_ref_str_proxy_module_absolute,
        type_ref_str_proxy_module_absolute_class,
        type_ref_str_proxy_relative,
        ref_str_proxy_relative_circular,
    )
    from beartype_test._util.error.pyterrraise import raises_uncached
    from beartype_test._util.error.pyterrwarn import warns_uncached

    # ....................{ LOCALS                         }....................
    # Arbitrary instance of a subclass of that class.
    obj_subclass = Subclass()

    # Arbitrary object satisfying the hint referred to by the
    # "hint_ref_str_proxy_absolute" proxy.
    obj_hint = ['Of stone,', 'or marble swart;', 'their import gone,']

    # ....................{ PASS                           }....................
    # Assertions are intentionally ordered in increasing level from lower- to
    # higher-level, ensuring that lower-level failures are caught before
    # higher-level failures.

    # ....................{ PASS ~ attr                    }....................
    # Validate lowest-level class variables bound to these proxies.

    # Assert that these proxies have the expected class names.
    assert type_ref_str_proxy_absolute.__name__ == TYPE_BASENAME
    assert type_ref_str_proxy_relative.__name__ == TYPE_BASENAME
    assert type_ref_str_proxy_module_absolute.__name__ == (
        TYPE_SUBMODULE_BASENAME)
    assert type_ref_str_proxy_module_absolute_class.__name__ == TYPE_BASENAME

    # Assert that these proxies have the expected module names.
    assert type_ref_str_proxy_absolute.__module__ == TYPE_SUBMODULE_NAME
    assert type_ref_str_proxy_relative.__module__ == TYPE_SUBMODULE_NAME
    assert type_ref_str_proxy_module_absolute.__module__ == TYPE_SUBPACKAGE_NAME
    assert type_ref_str_proxy_module_absolute_class.__module__ == (
        f'{TYPE_SUBPACKAGE_NAME}.{TYPE_SUBMODULE_BASENAME}')

    # Assert that these proxies have the expected hint names.
    assert type_ref_str_proxy_absolute.__hint_name_beartype__ == TYPE_NAME
    assert type_ref_str_proxy_relative.__hint_name_beartype__ == TYPE_BASENAME
    assert type_ref_str_proxy_module_absolute.__hint_name_beartype__ == (
        TYPE_SUBMODULE_NAME)
    assert type_ref_str_proxy_module_absolute_class.__hint_name_beartype__ == (
        TYPE_NAME)

    # Assert that these proxies have the expected scope names.
    assert type_ref_str_proxy_absolute.__scope_name_beartype__ == SCOPE_NAME
    assert type_ref_str_proxy_relative.__scope_name_beartype__ == (
        TYPE_SUBMODULE_NAME)
    assert type_ref_str_proxy_module_absolute.__scope_name_beartype__ == (
        SCOPE_NAME)
    assert type_ref_str_proxy_module_absolute_class.__scope_name_beartype__ == (
        SCOPE_NAME)

    # ....................{ PASS ~ repr                    }....................
    # Validate the low-level __repr__() dunder method defined to these proxies.

    # Machine-readable representation of a forward reference proxy.
    FORWARDREF_REPR = repr(type_ref_str_proxy_absolute)

    # Tuple of one or more substrings expected to be in this representation.
    FORWARDREF_REPR_SUBSTRS = (
        # Unqualified basename of the type this forward reference proxies.
        type_ref_str_proxy_absolute.__name__,
        # Machine-readable representations of all class variables of all
        # unsubscripted forward reference proxies.
        repr(type_ref_str_proxy_absolute.__scope_name_beartype__),
        repr(type_ref_str_proxy_absolute.__hint_name_beartype__),
    )

    # Assert that this representation contains the expected substrings.
    for fwdref_repr_substr in FORWARDREF_REPR_SUBSTRS:
        assert fwdref_repr_substr in FORWARDREF_REPR

    # ....................{ PASS ~ property                }....................
    # Validate higher-level dynamic properties defined on these proxies.

    # Assert that this property of these forward reference proxies all evaluate
    # to the expected type hints.
    assert hint_ref_str_proxy_absolute.__resolved_hint_beartype__ is Pep585Hint
    assert type_ref_str_proxy_absolute.__resolved_hint_beartype__ is Class
    assert type_ref_str_proxy_relative.__resolved_hint_beartype__ is Class
    assert type_ref_str_proxy_module_absolute_class.__resolved_hint_beartype__ is (
        Class)

    # Assert that this property of these forward reference proxies all evaluate
    # to the expected types.
    assert type_ref_str_proxy_absolute.__resolved_type_beartype__ is Class
    assert type_ref_str_proxy_relative.__resolved_type_beartype__ is Class
    assert type_ref_str_proxy_module_absolute_class.__resolved_type_beartype__ is (
        Class)

    # Assert that this property of these forward reference proxies all evaluate
    # to the same expected types while also issuing non-fatal warnings.
    with warns_uncached(DeprecationWarning):
        assert type_ref_str_proxy_absolute.__type_beartype__ is Class

    # ....................{ PASS ~ check                   }....................
    # Validate the highest-level __instancecheck__() and __subclasscheck__()
    # dunder methods defined on the metaclass of these proxies.

    # Assert that an object satisfying this hint is an "instance" of this proxy.
    # Look. We don't make the rules. We just break them over the knees of PEP
    # 484, which created this monstrous mess we now cleanup with cheap hacks.
    assert isinstance(obj_hint, hint_ref_str_proxy_absolute)

    # Assert that an instance of a subclass of that class is also an instance of
    # these proxies.
    assert isinstance(obj_subclass, type_ref_str_proxy_absolute)
    assert isinstance(obj_subclass, type_ref_str_proxy_relative)
    assert isinstance(obj_subclass, type_ref_str_proxy_module_absolute_class)

    # Assert that that subclass is also a subclass of these proxies.
    assert issubclass(Subclass, type_ref_str_proxy_absolute)
    assert issubclass(Subclass, type_ref_str_proxy_relative)
    assert issubclass(Subclass, type_ref_str_proxy_module_absolute_class)

    # ....................{ FAIL                           }....................
    # Assertions are intentionally ordered in the exact same order as above.

    # Assert that attempting to instantiate a forward reference proxy raises the
    # expected exception.
    with raises_uncached(BeartypeDecorHintForwardRefException):
        type_ref_str_proxy_absolute()

    # ....................{ FAIL ~ attr                    }....................
    # Assert that attempting to access an undefined dunder attribute of a
    # forward reference proxy raises the expected exception.
    with raises_uncached(AttributeError):
        type_ref_str_proxy_absolute.__the_beating_of_her_heart_was_heard_to_fill__

    # Assert that attempting to test an undefined *NON-DUNDER* attribute of a
    # forward reference proxy raises the expected exception *AFTER* that same
    # forward reference proxy has already resolved its referent due to a prior
    # call to the isinstance() or issubclass() builtins against this proxy.
    with raises_uncached(AttributeError):
        type_ref_str_proxy_module_absolute_class.and_buried_from_all_godlike_exercise

    # ....................{ FAIL ~ check                   }....................
    # Assert that attempting to call the issubclass() builtin against a proxy
    # encapsulating a forward reference referring to a PEP-compliant type hint
    # that is *NOT* an isinstanceable type raises the expected exception.
    with raises_uncached(BeartypeCallHintForwardRefException):
        issubclass(obj_hint, hint_ref_str_proxy_absolute)

    # Assert that attempting to validate a forward reference proxy to a module
    # as either an instance or subclass of a type raises the expected exception.
    with raises_uncached(BeartypeCallHintForwardRefException):
        isinstance(obj_subclass, type_ref_str_proxy_module_absolute)
    with raises_uncached(BeartypeCallHintForwardRefException):
        issubclass(Subclass, type_ref_str_proxy_module_absolute)

    # Assert that attempting to test an arbitrary object as an instance of a
    # circular forward reference proxy raises the expected exception.
    with raises_uncached(BeartypeCallHintForwardRefException):
        isinstance(obj_subclass, ref_str_proxy_relative_circular)

    # Assert that attempting to test an arbitrary type as a subclass of a
    # circular forward reference proxy raises the expected exception.
    with raises_uncached(BeartypeCallHintForwardRefException):
        issubclass(Subclass, ref_str_proxy_relative_circular)
