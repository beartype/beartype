#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`586` **utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep586` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                              }....................
def test_is_hint_pep586() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep586.die_unless_hint_pep586`
    raiser.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep586Exception
    from beartype.typing import Optional
    from beartype._util.hint.pep.proposal.pep586 import (
        die_unless_hint_pep586)
    from beartype._util.api.standard.utiltyping import get_typing_attrs
    from enum import Enum

    # ....................{ LOCALS                         }....................
    class _Color(Enum):
        '''
        Arbitrary enumeration to be tested below.
        '''

        RED = 0


    # Tuple of arbitrary objects permissible for use as arguments subscripting
    # PEP 586-compliant "Literal" type hints.
    #
    # For conformance, the items of this tuple are copied verbatim from a
    # prominent PEP 586 example under the "Legal parameters for Literal at type
    # check time" subsection.
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

    # ..................{ FACTORIES                          }..................
    # For each PEP 586-compliant "Literal" factory importable from each
    # currently importable "typing" module...
    for Literal in get_typing_attrs('Literal'):
        # ....................{ PASS                       }....................
        # For each object that is a valid literal argument, assert this raiser
        # raises no exception when passed that factory subscripted by that
        # argument.
        for literal_arg in _LITERAL_ARGS:
            die_unless_hint_pep586(Literal[literal_arg])

        # Assert this raiser raises no exception when passed that factory
        # subscripted by two or more such arguments.
        die_unless_hint_pep586(Literal[
            26, "hello world", b"hello world", True, _Color.RED, None])

        # ....................{ FAIL                       }....................
        # Assert this validator raises the expected exception when passed an
        # object that is *NOT* a literal.
        with raises(BeartypeDecorHintPep586Exception):
            die_unless_hint_pep586(Optional[str])

        # Assert this raiser raises the expected exception when passed that
        # unsubscripted factory.
        with raises(BeartypeDecorHintPep586Exception):
            die_unless_hint_pep586(Literal)

        # Assert this raiser raises the expected exception when passed that
        # factory subscripted by the empty tuple.
        with raises(BeartypeDecorHintPep586Exception):
            die_unless_hint_pep586(Literal[()])

        # Assert this raiser raises the expected exception when passed that
        # factory subscripted by an invalid literal argument.
        with raises(BeartypeDecorHintPep586Exception):
            die_unless_hint_pep586(Literal[object()])

        # Assert this raiser raises the expected exception when passed that
        # factory subscripted by one or more valid literal arguments and an
        # invalid literal argument.
        with raises(BeartypeDecorHintPep586Exception):
            die_unless_hint_pep586(Literal[
                26, "hello world", b"hello world", True, object(), _Color.RED])
