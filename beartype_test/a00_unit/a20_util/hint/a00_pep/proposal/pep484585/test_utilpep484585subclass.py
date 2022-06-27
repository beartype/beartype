#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` and :pep:`585` **subclass type hint utility unit
tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585.utilpep484585type` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ kind : subclass            }....................
def test_get_hint_pep484585_subclass_superclass() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.utilpep484585type.get_hint_pep484585_subclass_superclass`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintPep3119Exception,
        BeartypeDecorHintPep484585Exception,
        BeartypeDecorHintPep585Exception,
    )
    from beartype._util.hint.pep.proposal.pep484.utilpep484ref import (
        HINT_PEP484_FORWARDREF_TYPE)
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585type import (
        get_hint_pep484585_subclass_superclass)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype_test.a00_unit.data.data_type import NonIssubclassableClass
    from pytest import raises
    from typing import Type, Union

    # Assert this getter returns the expected object when passed a PEP
    # 484-compliant subclass type hint subscripted by a class.
    assert get_hint_pep484585_subclass_superclass(Type[str], '') is str

    # Assert this getter returns the expected object when passed a PEP
    # 484-compliant subclass type hint subscripted by a union of classes.
    hint_superclass = get_hint_pep484585_subclass_superclass(
        Type[Union[dict, set]], '')
    assert hint_superclass == (dict, set) or hint_superclass == (set, dict)

    # Assert this getter returns the expected object when passed a PEP
    # 484-compliant subclass type hint subscripted by a forward reference to a
    # class.
    assert get_hint_pep484585_subclass_superclass(Type['bytes'], '') == (
        HINT_PEP484_FORWARDREF_TYPE('bytes'))

    # Assert this getter raises the expected exception when passed a PEP
    # 484-compliant subclass type hint subscripted by a non-issubclassable
    # class.
    with raises(BeartypeDecorHintPep3119Exception):
        get_hint_pep484585_subclass_superclass(
            Type[NonIssubclassableClass], '')

    # Assert this getter raises the expected exception when passed an arbitrary
    # object that is neither a PEP 484- nor 585-compliant subclass type hint.
    with raises(BeartypeDecorHintPep484585Exception):
        get_hint_pep484585_subclass_superclass('Caustically', '')

    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585...
    if IS_PYTHON_AT_LEAST_3_9:
        # Assert this getter returns the expected object when passed a PEP
        # 585-compliant subclass type hint subscripted by a class.
        assert get_hint_pep484585_subclass_superclass(type[bool], '') is bool

        # Assert this getter returns the expected object when passed a PEP
        # 585-compliant subclass type hint subscripted by a union of classes.
        hint_superclass = get_hint_pep484585_subclass_superclass(
            type[Union[dict, set]], '')
        assert hint_superclass == (dict, set) or hint_superclass == (set, dict)

        # Assert this getter returns the expected object when passed a PEP
        # 585-compliant subclass type hint subscripted by a forward reference
        # to a class.
        assert get_hint_pep484585_subclass_superclass(type['complex'], '') == (
            'complex')

        # Assert this getter raises the expected exception when passed a PEP
        # 585-compliant subclass type hint subscripted by a non-issubclassable
        # class.
        with raises(BeartypeDecorHintPep3119Exception):
            get_hint_pep484585_subclass_superclass(
                type[NonIssubclassableClass], '')

        # Assert this getter raises the expected exception when passed a PEP
        # 585-compliant subclass type hint subscripted by *NO* classes.
        #
        # Note there intentionally exists *NO* corresponding PEP 484 test, as
        # the "typing.Type" factory already validates this to be the case.
        with raises(BeartypeDecorHintPep484585Exception):
            get_hint_pep484585_subclass_superclass(type[()], '')

        # Assert this getter raises the expected exception when passed a PEP
        # 585-compliant subclass type hint subscripted by two or more classes.
        #
        # Note there intentionally exists *NO* corresponding PEP 484 test, as
        # the "typing.Type" factory already validates this to be the case.
        with raises(BeartypeDecorHintPep585Exception):
            get_hint_pep484585_subclass_superclass(type[int, float], '')

        # Assert this getter raises the expected exception when passed a PEP
        # 585-compliant subclass type hint subscripted by an object that is
        # neither a class nor a forward reference to a class.
        #
        # Note there intentionally exists *NO* corresponding PEP 484 test, as
        # the "typing.Type" factory already validates this to be the case.
        with raises(BeartypeDecorHintPep484585Exception):
            get_hint_pep484585_subclass_superclass(type[
                b'Counterrevolutionary'], '')
