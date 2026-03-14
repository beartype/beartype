#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward scope type hierarchy** unit tests.

This submodule unit tests the
:func:`beartype._check.forward.scope.fwdscopecls` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_beartype_forward_scope() -> None:
    '''
    Test the
    :class:`beartype._check.forward.scope.fwdscopecls.BeartypeForwardScope`
    dictionary subclass.
    '''

    # ....................{ LOCALS                         }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintForwardRefException
    from beartype._check.forward.reference.fwdreftest import (
        is_beartype_forwardref)
    from beartype._check.forward.scope.fwdscopecls import BeartypeForwardScope
    from beartype_test.a00_unit.data.data_type import (
        Class,
        OtherClass,
        OtherSubclass,
        OtherSubclassSubclass,
        Subclass,
        SubclassSubclass,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Forward scope resolving stringified relative forward references against...
    scope_forward = BeartypeForwardScope(
        # First, this lexical scope intended to encapsulate the local and global
        # scope of some user-defined module, type, or callable.
        scope_dict={
            'Class': Class,
            'Subclass': Subclass,
            'OtherClass': OtherClass,
            'OtherSubclass': OtherSubclass,
            'OtherSubclassSubclass': OtherSubclassSubclass,
        },
        # Last, the fully-qualified name of the forward reference-specific data
        # submodule imported from above (as a fallback).
        scope_name='beartype_test.a00_unit.data.data_type',
        # Ignorable remaining mandatory parameters.
        exception_prefix='',
    )

    # ....................{ PASS ~ resolve                 }....................
    # Assert that this forward scope trivially resolves references to attributes
    # seeded at initialization time through the "scope_dict" parameter *WITHOUT*
    # encapsulating those references in forward reference proxies.
    assert scope_forward['Class'] is Class
    assert scope_forward['Subclass'] is Subclass

    # Assert that this forward scope non-trivially proxies references to
    # attributes *NOT* seeded at initialization time through the "scope_dict"
    # parameter by encapsulating those references in forward reference proxies.
    SubclassSubclassProxy = scope_forward.resolve_pep484_hint_str(
        'SubclassSubclass')
    assert is_beartype_forwardref(SubclassSubclassProxy) is True

    # Assert that these proxies successfully proxy isinstance() checks against
    # the classes they proxy.
    assert isinstance(SubclassSubclass(), SubclassSubclassProxy)

    # ....................{ PASS ~ minify                  }....................
    # Minify this forward scope.
    scope_forward_min = scope_forward.minify()

    # Assert that minification reduced this forward scope to a dictionary.
    assert scope_forward_min.__class__ is dict

    # Assert that minification truncated this dictionary to the proper subset of
    # key-value pairs directly accessed above.
    assert scope_forward_min == {
        'Class': Class,
        'Subclass': Subclass,
        'SubclassSubclass': SubclassSubclassProxy,
    }

    # ....................{ PASS ~ clear                   }....................
    # Assert that this forward scope is currently non-empty.
    assert bool(scope_forward) is True
    assert bool(scope_forward._hint_names_destringified) is True

    # Clear this forward scope.
    scope_forward.clear()

    # Assert that this forward scope is now empty.
    assert bool(scope_forward) is False
    assert bool(scope_forward._hint_names_destringified) is False

    # ....................{ FAIL                           }....................
    # Assert that attempting to instantiate a forward scope with a scope name
    # that is *NOT* a valid Python identifier raises the expected exception.
    with raises(BeartypeDecorHintForwardRefException):
        BeartypeForwardScope(
            scope_name="He breath'd fierce breath against the sleepy portals,",
            exception_prefix='',
        )

    # Assert that this forward scope accessed by an arbitrary non-string object
    # raises the expected exception.
    with raises(BeartypeDecorHintForwardRefException):
        scope_forward[b'To the eastern gates, and full six dewy hours']

    # Assert that this forward scope accessed by an arbitrary string object that
    # is *NOT* a valid Python identifier raises the expected exception.
    with raises(BeartypeDecorHintForwardRefException):
        scope_forward['Before the dawn in season due should blush,']

    # Assert that this forward scope accessed by a valid Python identifier
    # raises the standard "KeyError" exception.
    with raises(KeyError):
        scope_forward['Cleared_them_of_heavy_vapours_burst_them_wide']
