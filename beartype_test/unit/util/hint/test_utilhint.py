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
    from beartype.roar import BeartypeDecorHintNonPepException
    from beartype._util.hint.utilhint import die_unless_hint

    #FIXME: Add PEP-compliant objects *AFTER* supported by this function.
    # Tuple of PEP-compliant and -noncompliant objects accepted by this
    # function.
    HINTS_VALID = (
        # PEP-compliant types.
        #typing.Any,
        # PEP-noncompliant type *NOT* defined by the stdlib "typing" module.
        dict,
        # PEP-noncompliant forward reference.
        'dict',
        # PEP-noncompliant tuple containing only PEP-noncompliant types and
        # forward references.
        (str, 'str', cave.AnyType, cave.NoneType,),
    )

    # Tuple of unhashable objects rejected by this function.
    HINTS_INVALID_UNHASHABLE = (
        # Dictionary.
        {'For all things turn to barrenness': 'In the dim glass the demons hold,',},
        # List.
        ['The glass of outer weariness,', 'Made when God slept in times of old.',],
        # Set.
        {'There, through the broken branches, go', 'The ravens of unresting thought;',},
    )

    # Tuple of hashable non-PEP-noncompliant objects rejected by this function.
    HINTS_INVALID_NONPEP = (
        # Number.
        0xDEADBEEF,
        # Empty tuple.
        (),
        # Tuple containing a type defined by the stdlib "typing" module.
        (set, 'set', typing.Any, cave.NoneType,),
        # Tuple containing an object neither a type nor forward reference.
        (list, 'list', 0, cave.NoneType,),
    )

    # Assert this function accepts PEP-noncompliant type hints.
    for hint_valid in HINTS_VALID:
        die_unless_hint(hint_valid)

    # Assert this function rejects unhashable objects.
    for hint_invalid_unhashable in HINTS_INVALID_UNHASHABLE:
        with pytest.raises(TypeError):
            die_unless_hint(hint_invalid_unhashable)

    # Assert this function rejects non-PEP-noncompliant objects.
    for hint_invalid_nonpep in HINTS_INVALID_NONPEP:
        with pytest.raises(BeartypeDecorHintNonPepException):
            print('Non-PEP-noncompliant hint: {!r}'.format(hint_invalid_nonpep))
            die_unless_hint(hint_invalid_nonpep)

    # Assert this function rejects forward references when instructed to do so.
    with pytest.raises(BeartypeDecorHintNonPepException):
        die_unless_hint(hint='dict', is_str_valid=False)
