#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype utility annotation and type hinting unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilhint` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest, typing

# ....................{ TESTS                             }....................
def test_utilhint_die_unless_hint_nonpep() -> None:
    '''
    Test the :func:`beartype._util.utilhint.die_unless_hint_nonpep` validator.
    '''

    # Defer heavyweight imports.
    from beartype import cave
    from beartype.roar import BeartypeDecorHintValueNonPepException
    from beartype._util.utilhint import die_unless_hint_nonpep
    # from beartype_test.unit.pep.p484.data_p484 import P484_TYPES

    # Tuple of PEP-noncompliant type hints accepted by this function.
    OBJS_VALID = (
        # Type *NOT* defined by the stdlib "typing" module.
        dict,
        # Forward reference.
        'dict',
        # Tuple containing only such types and forward references.
        (str, 'str', cave.AnyType, cave.NoneType,),
    )

    # Tuple of other objects rejected by this function.
    OBJS_INVALID = (
        # Type defined by the stdlib "typing" module.
        typing.Any,
        # Object neither a type nor forward reference despite containing both.
        {dict, 'dict',},
        # Empty tuple.
        (),
        # Tuple containing a type defined by the stdlib "typing" module.
        (set, 'set', typing.Any, cave.NoneType,),
        # Tuple containing an object neither a type nor forward reference.
        (list, 'list', 0, cave.NoneType,),
    )

    # Implicitly assert this function accepts PEP-noncompliant type hints.
    for obj_valid in OBJS_VALID:
        die_unless_hint_nonpep(obj_valid)

    # Explicitly assert this function rejects objects excepted to be rejected.
    for obj_invalid in OBJS_INVALID:
        with pytest.raises(BeartypeDecorHintValueNonPepException):
            die_unless_hint_nonpep(obj_invalid)


def test_utilhint_is_hint_typing() -> None:
    '''
    Test the :func:`beartype._util.utilhint.is_hint_typing` tester.
    '''

    # Defer heavyweight imports.
    from beartype import cave
    from beartype._util.utilhint import is_hint_typing
    from beartype_test.unit.data.data_hint import P484_TYPES

    # Tuple of various non-"typing" types of interest.
    NONP484_TYPES = (
        list,
        str,
        cave.AnyType,
        cave.NoneType,
        cave.NoneTypeOr[cave.AnyType],
    )

    # Assert that various "typing" types are correctly detected.
    for p484_type in P484_TYPES:
        print('PEP 484 type: {!r}'.format(p484_type))
        assert is_hint_typing(p484_type) is True

    # Assert that various non-"typing" types are correctly detected.
    for nonp484_type in NONP484_TYPES:
        print('Non-PEP 484 type: {!r}'.format(nonp484_type))
        assert is_hint_typing(nonp484_type) is False
