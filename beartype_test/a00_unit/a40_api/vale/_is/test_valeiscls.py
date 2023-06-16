#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype code-based type data validation unit tests.**

This submodule unit tests the subset of the public API of the
:mod:`beartype.vale` subpackage defined by the private
:mod:`beartype.vale._is._valeistype` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ class : isinstance        }....................
def test_api_vale_isinstance_pass() -> None:
    '''
    Test successful usage of the :class:`beartype.vale.IsInstance` factory.
    '''

    # Defer test-specific imports.
    from beartype.vale import IsInstance
    from beartype.vale._core._valecore import BeartypeValidator
    from beartype._util.utilobject import get_object_name
    from beartype_test.a00_unit.data.data_type import (
        Class, Subclass, SubclassSubclass)

    # Subclasses of classes subscripting this factory below.
    class UnicodeStr(str): pass
    class ByteStr(bytes): pass

    # Instances of classes imported or declared above.
    class_instance = Class()
    subclass_instance = Subclass()
    subclasssubclass_instance = SubclassSubclass()
    unicodestr_instance = UnicodeStr(
        'Driven like a homeless cloud from steep to steep')
    bytestr_instance = ByteStr(b'That vanishes among the viewless gales!')

    # Validators produced by subscripting this factory with one superclass.
    IsClassInstance = IsInstance[Class]
    IsSubclassInstance = IsInstance[Subclass]

    # Validator produced by subscripting this factory with two or more
    # superclasses.
    IsStrOrBytesInstance = IsInstance[str, bytes]

    # Assert these validators satisfy the expected API.
    assert isinstance(IsClassInstance, BeartypeValidator)
    assert isinstance(IsSubclassInstance, BeartypeValidator)
    assert isinstance(IsStrOrBytesInstance, BeartypeValidator)

    # Assert these validators produce the same objects when subscripted by the
    # same arguments (and are thus memoized on subscripted arguments).
    assert IsClassInstance is IsInstance[Class]
    assert IsSubclassInstance is IsInstance[Subclass]
    assert IsStrOrBytesInstance is IsInstance[str, bytes]

    # Assert these validators accept the superclasses subscripting these
    # validators. By definition, any class is a subclass of itself.
    assert IsClassInstance.is_valid(class_instance) is True
    assert IsSubclassInstance.is_valid(subclass_instance) is True
    assert IsStrOrBytesInstance.is_valid(unicodestr_instance) is True
    assert IsStrOrBytesInstance.is_valid(bytestr_instance) is True

    # Assert these validators accept instances of subclasses of the
    # superclasses subscripting these validators.
    assert IsClassInstance.is_valid(subclass_instance) is True
    assert IsSubclassInstance.is_valid(subclasssubclass_instance) is True
    assert IsStrOrBytesInstance.is_valid(unicodestr_instance) is True
    assert IsStrOrBytesInstance.is_valid(bytestr_instance) is True

    # Assert these validators reject objects *NOT* instancing the superclasses
    # subscripting these validators.
    assert IsClassInstance.is_valid(
        'Far, far above, piercing the infinite sky,') is False
    assert IsSubclassInstance.is_valid(class_instance) is False
    assert IsStrOrBytesInstance.is_valid(subclass_instance) is False

    # Assert these validators reject classes.
    assert IsClassInstance.is_valid(Class) is False
    assert IsSubclassInstance.is_valid(Subclass) is False
    assert IsStrOrBytesInstance.is_valid(str) is False
    assert IsStrOrBytesInstance.is_valid(bytes) is False

    # Assert these validators have the expected representation.
    assert get_object_name(Class) in repr(IsClassInstance)
    assert get_object_name(Subclass) in repr(IsSubclassInstance)
    assert 'str' in repr(IsStrOrBytesInstance)
    assert 'bytes' in repr(IsStrOrBytesInstance)

    # Validator synthesized from the above validators with the domain-specific
    # language (DSL) supported by these validators.
    IsClassOrStrOrBytesInstance = (
        IsSubclassInstance | IsStrOrBytesInstance | IsClassInstance)

    # Assert this validator performs the expected validation.
    assert IsClassOrStrOrBytesInstance.is_valid(class_instance) is True
    assert IsClassOrStrOrBytesInstance.is_valid(subclass_instance) is True
    assert IsClassOrStrOrBytesInstance.is_valid(subclasssubclass_instance) is (
        True)
    assert IsClassOrStrOrBytesInstance.is_valid(unicodestr_instance) is True
    assert IsClassOrStrOrBytesInstance.is_valid(bytestr_instance) is True

    # Assert this validator provides the expected representation.
    assert '|' in repr(IsClassOrStrOrBytesInstance)


def test_api_vale_isinstance_fail() -> None:
    '''
    Test unsuccessful usage of the :class:`beartype.vale.IsInstance` factory.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype.vale import IsInstance
    from beartype_test.a00_unit.data.data_type import NonIsinstanceableClass
    from pytest import raises

    # Assert that subscripting this factory with the empty tuple raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsInstance[()]

    # Assert that subscripting this factory with a non-class raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsInstance['Mont Blanc appears—still, snowy, and serene;']

    # Assert that subscripting this factory with a non-isinstanceable class
    # raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsInstance[NonIsinstanceableClass]

    # Assert that subscripting this factory with both a class and non-class
    # raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsInstance[str, 'Its subject mountains their unearthly forms']

    # Assert that subscripting this factory with both an isinstanceable and
    # non-isinstanceable class raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsInstance[bytes, NonIsinstanceableClass]

# ....................{ TESTS ~ class : issubclass        }....................
def test_api_vale_issubclass_pass() -> None:
    '''
    Test successful usage of the :class:`beartype.vale.IsSubclass` factory.
    '''

    # Defer test-specific imports.
    from beartype.vale import IsSubclass
    from beartype.vale._core._valecore import BeartypeValidator
    from beartype._util.utilobject import get_object_name
    from beartype_test.a00_unit.data.data_type import (
        Class, Subclass, SubclassSubclass)

    # Subclasses of classes subscripting this factory below.
    class UnicodeStr(str): pass
    class ByteStr(bytes): pass

    # Validators produced by subscripting this factory with one superclass.
    IsClassSubclass = IsSubclass[Class]
    IsSubclassSubclass = IsSubclass[Subclass]

    # Validator produced by subscripting this factory with two or more
    # superclasses.
    IsStrOrBytesSubclass = IsSubclass[str, bytes]

    # Assert these validators satisfy the expected API.
    assert isinstance(IsClassSubclass, BeartypeValidator)
    assert isinstance(IsSubclassSubclass, BeartypeValidator)
    assert isinstance(IsStrOrBytesSubclass, BeartypeValidator)

    # Assert these validators produce the same objects when subscripted by the
    # same arguments (and are thus memoized on subscripted arguments).
    assert IsClassSubclass is IsSubclass[Class]
    assert IsSubclassSubclass is IsSubclass[Subclass]
    assert IsStrOrBytesSubclass is IsSubclass[str, bytes]

    # Assert these validators accept the superclasses subscripting these
    # validators. By definition, any class is a subclass of itself.
    assert IsClassSubclass.is_valid(Class) is True
    assert IsSubclassSubclass.is_valid(Subclass) is True
    assert IsStrOrBytesSubclass.is_valid(str) is True
    assert IsStrOrBytesSubclass.is_valid(bytes) is True

    # Assert these validators accept subclasses of the superclasses
    # subscripting these validators.
    assert IsClassSubclass.is_valid(Subclass) is True
    assert IsSubclassSubclass.is_valid(SubclassSubclass) is True
    assert IsStrOrBytesSubclass.is_valid(UnicodeStr) is True
    assert IsStrOrBytesSubclass.is_valid(ByteStr) is True

    # Assert these validators reject classes *NOT* subclassing the superclasses
    # subscripting these validators.
    assert IsClassSubclass.is_valid(type) is False
    assert IsSubclassSubclass.is_valid(Class) is False
    assert IsStrOrBytesSubclass.is_valid(Subclass) is False

    # Assert these validators reject non-classes.
    assert IsClassSubclass.is_valid(
        'Over whose pines, and crags, and caverns sail') is False
    assert IsSubclassSubclass.is_valid(
        'Fast cloud-shadows and sunbeams: awful scene,') is False
    assert IsStrOrBytesSubclass.is_valid(
        'Bursting through these dark mountains like the flame') is False

    # Assert these validators have the expected representation.
    assert get_object_name(Class) in repr(IsClassSubclass)
    assert get_object_name(Subclass) in repr(IsSubclassSubclass)
    assert 'str' in repr(IsStrOrBytesSubclass)
    assert 'bytes' in repr(IsStrOrBytesSubclass)

    # Validator synthesized from the above validators with the domain-specific
    # language (DSL) supported by these validators.
    IsClassOrStrOrBytesSubclass = (
        IsSubclassSubclass | IsStrOrBytesSubclass | IsClassSubclass)

    # Assert this validator performs the expected validation.
    assert IsClassOrStrOrBytesSubclass.is_valid(Class) is True
    assert IsClassOrStrOrBytesSubclass.is_valid(Subclass) is True
    assert IsClassOrStrOrBytesSubclass.is_valid(SubclassSubclass) is True
    assert IsClassOrStrOrBytesSubclass.is_valid(UnicodeStr) is True
    assert IsClassOrStrOrBytesSubclass.is_valid(ByteStr) is True

    # Assert this validator provides the expected representation.
    assert '|' in repr(IsClassOrStrOrBytesSubclass)


def test_api_vale_issubclass_fail() -> None:
    '''
    Test unsuccessful usage of the :class:`beartype.vale.IsSubclass` factory.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype.vale import IsSubclass
    from beartype_test.a00_unit.data.data_type import NonIssubclassableClass
    from pytest import raises

    # Assert that subscripting this factory with the empty tuple raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsSubclass[()]

    # Assert that subscripting this factory with a non-class raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsSubclass['Where Power in likeness of the Arve comes down']

    # Assert that subscripting this factory with a non-issubclassable class
    # raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsSubclass[NonIssubclassableClass]

    # Assert that subscripting this factory with both a class and non-class
    # raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsSubclass[str, 'Of lightning through the tempest;—thou dost lie,']

    # Assert that subscripting this factory with both an issubclassable and
    # non-issubclassable class raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsSubclass[bytes, NonIssubclassableClass]
