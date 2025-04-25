#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

# ....................{ TESTS                              }....................
'''
Beartype :pep:`544`-compliant **type hint reduction** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.convert._reduce._pep.redpep544` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ reducers                   }....................
def test_reduce_hint_pep484_generic_io_to_pep544_protocol() -> None:
    '''
    Test the
    :func:`beartype._check.convert._reduce._pep.redpep544.reduce_hint_pep484_generic_io_to_pep544_protocol`
    reducer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep544Exception
    from beartype.typing import Union
    from beartype._check.convert._reduce._pep.redpep544 import (
        reduce_hint_pep484_generic_io_to_pep544_protocol)
    from beartype._data.cls.datacls import TYPES_PEP484_GENERIC_IO
    from beartype._util.hint.pep.proposal.pep593 import is_hint_pep593
    from pytest import raises
    from typing import Protocol

    # ....................{ PASS                           }....................
    # For each PEP 484-compliant "typing" IO generic base class...
    for pep484_generic_io in TYPES_PEP484_GENERIC_IO:
        # Equivalent protocol reduced from this generic.
        pep544_protocol_io = (
            reduce_hint_pep484_generic_io_to_pep544_protocol(
                pep484_generic_io, ''))

        # Assert this protocol is either...
        assert (
            # A PEP 593-compliant type metahint generalizing a protocol
            # *OR*...
            is_hint_pep593(pep544_protocol_io) or
            # A PEP 544-compliant protocol.
            issubclass(pep544_protocol_io, Protocol)
        )

    # ....................{ FAIL                           }....................
    # Assert this function rejects standard type hints in either case.
    with raises(BeartypeDecorHintPep544Exception):
        reduce_hint_pep484_generic_io_to_pep544_protocol(Union[int, str], '')
