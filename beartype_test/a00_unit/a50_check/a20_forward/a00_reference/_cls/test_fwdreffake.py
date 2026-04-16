#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference fake proxy factory** unit tests.

This submodule unit tests the
:func:`beartype._check.forward.reference._cls.fwdreffake` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_proxy_hint_pep484_ref_str_nested() -> None:
    '''
    Test the
    :func:`beartype._check.forward.reference._cls.fwdreffake.proxy_hint_pep484_ref_str_nested`
    factory.
    '''

    # ....................{ LOCALS                         }....................
    # Defer test-specific imports.
    from beartype_test.a00_unit.data.data_type import (
        OtherClass,

        # Arbitrary types intentionally imported under different local variable
        # names to validate that forward reference fake proxies are robust
        # against such trivial basename aliases.
        Class as SailTheirOrb,
        Subclass as ThoseSilverWings,
        SubclassSubclass as OperationsOfTheDawn,
    )
    from beartype._check.forward.reference._cls.fwdreffake import (
        proxy_hint_pep484_ref_str_nested)
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Forward reference fake proxy pretending to proxy a subclass of an
    # arbitrary type.
    #
    # Note that this factory is memoized and thus requires that all parameters
    # only be passed positionally.
    Subclass_proxy = proxy_hint_pep484_ref_str_nested(
        'beartype_test.a00_unit.data.data_type', 'Subclass')

    # Arbitrary instance of that type, intentionally accessed under a unique
    # local variable name than that of that type to validate that forward
    # reference fake proxies are robust against such trivial basename aliases.
    Subclass_object = ThoseSilverWings()

    # Arbitrary instance of a subclass of that type.
    SubclassSubclass_object = OperationsOfTheDawn()

    # Arbitrary instance of a superclass of that type.
    Class_object = SailTheirOrb()

    # ....................{ PASS ~ instance                }....................
    # Assert that an instance of a type pretends to be an instance of a fake
    # proxy proxying that type.
    assert isinstance(Subclass_object, Subclass_proxy) is True

    # Assert that an instance of a subclass of a type pretends to be an instance
    # of a fake proxy proxying that type.
    assert isinstance(SubclassSubclass_object, Subclass_proxy) is True

    # Assert that an instance of a superclass of a type pretends to *NOT* be an
    # instance of a fake proxy proxying that type.
    assert isinstance(Class_object, Subclass_proxy) is False

    # Assert that a type pretends to *NOT* be an instance of a fake proxy
    # proxying that type.
    assert isinstance(ThoseSilverWings, Subclass_proxy) is False

    # Assert that an arbitrary object that is *NOT* an instance of a type
    # pretends to *NOT* be an instance of a fake proxy proxying that type.
    assert isinstance(
        "Stay'd in their birth, even as here 'tis told.",
        Subclass_proxy,
    ) is False

    # ....................{ PASS ~ subclass                }....................
    # Assert that a type pretends to be a subclass of a fake proxy proxying that
    # type.
    assert issubclass(ThoseSilverWings, Subclass_proxy) is True

    # Assert that a subclass of a type pretends to be a subclass of a fake proxy
    # proxying that type.
    assert issubclass(OperationsOfTheDawn, Subclass_proxy) is True

    # Assert that a superclass of a type pretends to *NOT* be a subclass of a
    # fake proxy proxying that type.
    assert issubclass(SailTheirOrb, Subclass_proxy) is False

    # Assert that an arbitrary type that is neither a type *NOR* a subclass of
    # that type pretends to *NOT* be a subclass of a fake proxy proxying that
    # type.
    assert issubclass(OtherClass, Subclass_proxy) is False

    # ....................{ FAIL                           }....................
    # Assert that the issubclass() builtin when passed an arbitrary non-type
    # object and a fake proxy (in that order) raises the expected exception.
    with raises(TypeError):
        issubclass(
            'Therefore the operations of the dawn', Subclass_proxy)
