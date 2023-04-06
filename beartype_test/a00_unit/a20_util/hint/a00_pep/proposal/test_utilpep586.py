#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`586` **utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep586` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from enum import Enum
from pytest import raises

# ....................{ PRIVATE ~ constants                }....................
#FIXME: Shift these into the unit test defined below, please.
class _Color(Enum):
    '''
    Arbitrary enumeration accessed as given in a prominent :pep:`586` example.
    '''

    RED = 0


_LITERAL_ARGS = (
    26,
    0x1A,
    -4,
    "hello world",
    b"hello world",
    u"hello world",
    True,
    _Color.RED,
    None,
)
'''
Tuple of arbitrary objects permissible for use as arguments subscripting
:pep:`586`-compliant :attr:`typing.Literal` type hints.

For conformance, the items of this tuple are copied verbatim from a prominent
:pep:`586` example under the "Legal parameters for Literal at type check time"
subsection.
'''

# ....................{ TESTS                              }....................
def test_is_hint_pep586() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.utilpep586.die_unless_hint_pep586`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep586Exception
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype._util.hint.pep.proposal.utilpep586 import (
        die_unless_hint_pep586)
    from typing import Optional

    # Assert this validator raises the expected exception when passed an
    # object that is *NOT* a literal.
    with raises(BeartypeDecorHintPep586Exception):
        die_unless_hint_pep586(Optional[str])

    # If the active Python interpreter targets at least Python >= 3.9 and thus
    # supports PEP 586...
    if IS_PYTHON_AT_LEAST_3_9:
        # Defer imports specific to this Python version.
        from typing import Literal

        # For each object that is a valid literal argument, assert this
        # validator raises no exception when passed that singleton subscripted
        # by that argument.
        for literal_arg in _LITERAL_ARGS:
            die_unless_hint_pep586(Literal[literal_arg])

        # Assert this validator raises no exception when passed that singleton
        # subscripted by two or more such arguments.
        die_unless_hint_pep586(Literal[
            26, "hello world", b"hello world", True, _Color.RED, None])

        # Assert this validator raises the expected exception when passed that
        # singleton subscripted by the empty tuple.
        with raises(BeartypeDecorHintPep586Exception):
            die_unless_hint_pep586(Literal[()])

        # Assert this validator raises the expected exception when passed that
        # singleton subscripted by an invalid literal argument.
        with raises(BeartypeDecorHintPep586Exception):
            die_unless_hint_pep586(Literal[object()])

        # Assert this validator raises the expected exception when passed that
        # singleton subscripted by one or more valid literal arguments and an
        # invalid literal argument.
        with raises(BeartypeDecorHintPep586Exception):
            die_unless_hint_pep586(Literal[
                26, "hello world", b"hello world", True, object(), _Color.RED])
