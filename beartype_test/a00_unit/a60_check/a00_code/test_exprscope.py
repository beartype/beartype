#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant code wrapper scope utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._check.code._codescope` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ adder : type               }....................
def test_add_func_scope_type_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._check.code._codescope.add_func_scope_type` function.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeDecorBeartypistryException
    from beartype._cave._cavefast import NoneType, RegexCompiledType
    from beartype._check.code._codescope import add_func_scope_type
    from beartype._util.utilobject import get_object_type_basename

    # Arbitrary scope to be added to below.
    func_scope = {}

    # Assert this function supports...
    classes_nonbuiltin = (
        # Adding a non-builtin type.
        RegexCompiledType,
        # Readding that same type.
        RegexCompiledType,
        # Adding the type of the "None" singleton (despite technically being
        # listed as belonging to the "builtin" module) under a unique name
        # rather than its unqualified basename "NoneType" (which doesn't
        # actually exist, which is inconsistent nonsense, but whatever).
        NoneType,
    )
    for cls in classes_nonbuiltin:
        cls_scope_name = add_func_scope_type(cls=cls, func_scope=func_scope)
        assert cls_scope_name != get_object_type_basename(cls)
        assert func_scope[cls_scope_name] is cls

    # Assert this function does *NOT* add builtin types but instead simply
    # returns the unqualified basenames of those types.
    cls = list
    cls_scope_name = add_func_scope_type(cls=cls, func_scope=func_scope)
    assert cls_scope_name == get_object_type_basename(cls)
    assert cls_scope_name not in func_scope


def test_add_func_scope_type_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._check.code._codescope.add_func_scope_type` function.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep3119Exception
    from beartype._check.code._codescope import add_func_scope_type
    from beartype_test.a00_unit.data.data_type import NonIsinstanceableClass
    from pytest import raises

    # Arbitrary scope to be added to below.
    func_scope = {}

    # Assert this function raises the expected exception for non-types.
    with raises(BeartypeDecorHintPep3119Exception):
        add_func_scope_type(
            cls=(
                'The best lack all conviction, while the worst',
                'Are full of passionate intensity',
            ),
            func_scope=func_scope,
        )

    # Assert this function raises the expected exception for PEP 560-compliant
    # classes whose metaclasses define an __instancecheck__() dunder method to
    # unconditionally raise exceptions.
    with raises(BeartypeDecorHintPep3119Exception):
        add_func_scope_type(cls=NonIsinstanceableClass, func_scope=func_scope)

# ....................{ TESTS ~ adder : tuple              }....................
def test_add_func_scope_types_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._check.code._codescope.add_func_scope_types` function.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeDecorBeartypistryException
    from beartype._cave._cavefast import CallableTypes, ModuleOrStrTypes
    from beartype._cave._cavemap import NoneTypeOr
    from beartype._check.code._codescope import add_func_scope_types
    from beartype._util.utilobject import get_object_type_basename
    from beartype_test.a00_unit.data.data_type import Class

    # Arbitrary scope to be added to below.
    func_scope = {}

    # Assert this function adds a tuple of one or more standard types.
    #
    # Note that, unlike types, tuples are internally added under different
    # objects than their originals (e.g., to ignore both duplicates and
    # ordering) and *MUST* thus be tested by conversion to sets.
    types = CallableTypes
    types_scope_name = add_func_scope_types(
        types=types, func_scope=func_scope)
    assert set(types) == set(func_scope[types_scope_name])

    # Assert this function readds the same tuple as well.
    types_scope_name_again = add_func_scope_types(
        types=types, func_scope=func_scope)
    assert types_scope_name == types_scope_name_again

    # Assert this function adds a frozenset of one or more standard types.
    types = frozenset(ModuleOrStrTypes)
    types_scope_name = add_func_scope_types(
        types=types, func_scope=func_scope)
    assert set(types) == set(func_scope[types_scope_name])

    # Assert this function does *NOT* add tuples of one non-builtin types but
    # instead simply returns the unqualified basenames of those types.
    types = (int,)
    types_scope_name = add_func_scope_types(
        types=types, func_scope=func_scope)
    assert types_scope_name == get_object_type_basename(types[0])
    assert types_scope_name not in func_scope

    # Assert this function adds tuples of one non-builtin type as merely that
    # type rather than that tuple.
    types = (Class,)
    types_scope_name = add_func_scope_types(types=types, func_scope=func_scope)
    assert func_scope[types_scope_name] is Class

    # Assert this function adds tuples containing duplicate types as tuples
    # containing only the proper subset of non-duplicate types.
    types = (Class,)*3
    types_scope_name = add_func_scope_types(types=types, func_scope=func_scope)
    assert func_scope[types_scope_name] == (Class,)

    # Assert this function registers tuples containing *NO* duplicate types.
    types = NoneTypeOr[CallableTypes]
    types_scope_name = add_func_scope_types(
        types=types, func_scope=func_scope, is_unique=True)
    assert func_scope[types_scope_name] == types

    # Assert this function registers tuples containing the same types in
    # different orders to differing objects and thus preserving ordering.
    types_a = (int, str,)
    types_b = (str, int,)
    types_scope_name_a = add_func_scope_types(
        types=types_a, func_scope=func_scope, is_unique=True)
    types_scope_name_b = add_func_scope_types(
        types=types_b, func_scope=func_scope, is_unique=True)
    assert func_scope[types_scope_name_a] == types_a
    assert func_scope[types_scope_name_b] == types_b
    assert func_scope[types_scope_name_a] != func_scope[types_scope_name_b]


def test_add_func_scope_types_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._check.code._codescope.add_func_scope_types` function.
    '''

    # Defer test-specific imports
    from beartype.roar import BeartypeDecorHintNonpepException
    from beartype._check.code._codescope import add_func_scope_types
    from beartype_test.a00_unit.data.data_type import NonIsinstanceableClass
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        Pep484GenericTypevaredSingle)
    from pytest import raises

    # Arbitrary scope to be added to below.
    func_scope = {}

    # Assert this function raises the expected exception for unhashable tuples.
    with raises(BeartypeDecorHintNonpepException):
        add_func_scope_types(
            types=(
                int, str, {
                    'Had': "I the heaven’s embroidered cloths,",
                    'Enwrought': "with golden and silver light,",
                    'The': 'blue and the dim and the dark cloths',
                    'Of': 'night and light and the half-light,',
                    'I': 'would spread the cloths under your feet:',
                    'But': 'I, being poor, have only my dreams;',
                    'I have': 'spread my dreams under your feet;',
                    'Tread': 'softly because you tread on my dreams.',
                },
            ),
            func_scope=func_scope,
        )

    # Assert this function raises the expected exception for non-tuples.
    with raises(BeartypeDecorHintNonpepException):
        add_func_scope_types(
            types='\n'.join((
                'I will arise and go now, and go to Innisfree,',
                'And a small cabin build there, of clay and wattles made;',
                'Nine bean-rows will I have there, a hive for the honey-bee,',
                'And live alone in the bee-loud glade.',
            )),
            func_scope=func_scope,
        )

    # Assert this function raises the expected exception for empty tuples.
    with raises(BeartypeDecorHintNonpepException):
        add_func_scope_types(types=(), func_scope=func_scope)

    # Assert this function raises the expected exception for tuples containing
    # one or more PEP-compliant types.
    with raises(BeartypeDecorHintNonpepException):
        add_func_scope_types(
            types=(int, Pep484GenericTypevaredSingle, str,),
            func_scope=func_scope,
        )

    # Assert this function raises the expected exception for tuples containing
    # one or more PEP 560-compliant classes whose metaclasses define an
    # __instancecheck__() dunder method to unconditionally raise exceptions.
    with raises(BeartypeDecorHintNonpepException):
        add_func_scope_types(
            types=(bool, NonIsinstanceableClass, float,),
            func_scope=func_scope,
        )

# ....................{ TESTS ~ expresser : type           }....................
def test_express_func_scope_type_forwardref() -> None:
    '''
    Test the
    :func:`beartype._check.code._codescope.express_func_scope_type_forwardref`
    function.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintForwardRefException
    from beartype._check.forward.fwdtype import bear_typistry
    from beartype._check.checkmagic import ARG_NAME_TYPISTRY
    from beartype._check.code._codescope import (
        express_func_scope_type_forwardref)
    from beartype._util.hint.pep.proposal.pep484.utilpep484ref import (
        HINT_PEP484_FORWARDREF_TYPE)
    from pytest import raises

    # Arbitrary scope to be added to below.
    func_scope = {}

    # Set of the unqualified classnames referred to by all relative forward
    # references relative to this scope if any *OR* "None" otherwise (i.e., if
    # no such references have been expressed relative to this scope yet).
    forwardrefs_class_basename = None

    # Fully-qualified classname of a non-existing class.
    CLASSNAME_QUALIFIED = 'Thy.giant.brood.of.pines.around.thee.clinging'

    # Unqualified classname of a non-existing class.
    CLASSNAME_UNQUALIFIED = 'Children_of_elder_time_in_whose_devotion'

    # Tuple of all PEP-compliant forward references to this fully-qualified
    # class, including...
    FORWARDREFS_QUALIFIED = (
        # PEP 484-compliant forward reference to this class.
        HINT_PEP484_FORWARDREF_TYPE(CLASSNAME_QUALIFIED),
        # PEP 585-compliant forward reference to this class.
        CLASSNAME_QUALIFIED,
    )

    # Tuple of all PEP-compliant forward references to this unqualified class,
    # including...
    FORWARDREFS_UNQUALIFIED = (
        # PEP 484-compliant forward reference to this class.
        HINT_PEP484_FORWARDREF_TYPE(CLASSNAME_UNQUALIFIED),
        # PEP 585-compliant forward reference to this class.
        CLASSNAME_UNQUALIFIED,
    )

    # For each PEP-compliant forward reference to a fully-qualified class...
    for forwardref_qualified in FORWARDREFS_QUALIFIED:
        # Express a fully-qualified forward reference to a non-existing class.
        forwardref_expr, forwardrefs_class_basename = (
            express_func_scope_type_forwardref(
                forwardref=forwardref_qualified,
                forwardrefs_class_basename=forwardrefs_class_basename,
                func_scope=func_scope,
            ))

        # Assert this expression references this class.
        assert CLASSNAME_QUALIFIED in forwardref_expr

        # Assert this set remains empty.
        assert forwardrefs_class_basename is None

        # Assert the beartypistry singleton has been added to this scope as a
        # private "__beartypistry" attribute.
        assert func_scope[ARG_NAME_TYPISTRY] is bear_typistry

        # Assert this function rexpresses the same forward reference.
        forwardref_expr_again, forwardrefs_class_basename_again = (
            express_func_scope_type_forwardref(
                forwardref=forwardref_qualified,
                forwardrefs_class_basename=forwardrefs_class_basename,
                func_scope=func_scope,
            ))
        assert forwardref_expr_again == forwardref_expr
        assert forwardrefs_class_basename_again is forwardrefs_class_basename

    # For each PEP-compliant forward reference to an unqualified class...
    for forwardref_unqualified in FORWARDREFS_UNQUALIFIED:
        # Express an unqualified forward reference to a non-existing class.
        forwardref_expr, forwardrefs_class_basename = (
            express_func_scope_type_forwardref(
                forwardref=forwardref_unqualified,
                forwardrefs_class_basename=forwardrefs_class_basename,
                func_scope=func_scope,
            ))

        # Assert this expression references this class.
        assert CLASSNAME_UNQUALIFIED in forwardref_expr

        # Assert this set now contains only this classname.
        assert forwardrefs_class_basename == {CLASSNAME_UNQUALIFIED,}

        # Assert this function rexpresses the same forward reference.
        forwardref_expr_again, forwardrefs_class_basename_again = (
            express_func_scope_type_forwardref(
                forwardref=forwardref_unqualified,
                forwardrefs_class_basename=forwardrefs_class_basename,
                func_scope=func_scope,
            ))
        assert forwardref_expr_again == forwardref_expr
        assert forwardrefs_class_basename_again == {CLASSNAME_UNQUALIFIED,}

    # Assert this function raises the expected exception for arbitrary objects
    # that are *NOT* forward references.
    with raises(BeartypeDecorHintForwardRefException):
        express_func_scope_type_forwardref(
            forwardref=b'The chainless winds still come and ever came',
            forwardrefs_class_basename=forwardrefs_class_basename,
            func_scope=func_scope,
        )
