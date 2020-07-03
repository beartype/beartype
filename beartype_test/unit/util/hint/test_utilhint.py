#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.utilhint` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest, typing

# ....................{ TESTS                             }....................
def test_utilhint_die_unless_hint() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhint.die_unless_hint`
    validator.
    '''

    # Defer heavyweight imports.
    from beartype import cave
    from beartype.roar import BeartypeDecorHintValueNonPepException
    from beartype._util.hint.utilhintnonpep import die_unless_hint_nonpep

    # Tuple of PEP-noncompliant type hints accepted by this function.
    HINTS_VALID = (
        # Type *NOT* defined by the stdlib "typing" module.
        dict,
        # Forward reference.
        'dict',
        # Tuple containing only such types and forward references.
        (str, 'str', cave.AnyType, cave.NoneType,),
    )

    # Tuple of other objects rejected by this function.
    HINTS_INVALID = (
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
    for hint_valid in HINTS_VALID:
        die_unless_hint_nonpep(hint_valid)

    # Explicitly assert this function rejects objects excepted to be rejected.
    for hint_invalid in HINTS_INVALID:
        with pytest.raises(BeartypeDecorHintValueNonPepException):
            die_unless_hint_nonpep(hint_invalid)
