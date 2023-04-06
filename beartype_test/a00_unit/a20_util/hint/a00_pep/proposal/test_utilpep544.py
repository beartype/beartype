#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`544` **utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep544` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep544_protocol() -> None:
    '''
    Test usage of the private
    :mod:`beartype._util.hint.pep.proposal.utilpep544.is_hint_pep544_protocol`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.utilpep544 import (
        is_hint_pep544_protocol)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from beartype_test.a00_unit.data.data_type import (
        TYPES_BUILTIN,
        Class,
    )

    # Intentionally import @beartype-unaccelerated protocols.
    from typing import (
        SupportsAbs,
        SupportsBytes,
        SupportsComplex,
        SupportsFloat,
        SupportsInt,
        SupportsRound,
        Union,
    )

    # ....................{ LOCALS                         }....................
    # Set of all PEP 544-compliant "typing" protocols.
    TYPING_PROTOCOLS = {
        SupportsAbs,
        SupportsBytes,
        SupportsComplex,
        SupportsFloat,
        SupportsInt,
        SupportsRound,
    }

    # ....................{ PASS                           }....................
    # Assert this tester rejects builtin types erroneously presenting themselves
    # as PEP 544-compliant protocols under Python >= 3.8.
    assert is_hint_pep544_protocol(int) is False
    assert is_hint_pep544_protocol(str) is False
    assert is_hint_pep544_protocol(type(None)) is False

    # Assert this tester rejects a user-defined type.
    assert is_hint_pep544_protocol(Class) is False
    # class Yam(object): pass
    # from typing import Protocol
    # assert not issubclass(Yam, Protocol)
    # assert is_hint_pep544_protocol(Yam) is False

    # Assert this tester accepts these classes *ONLY* if the active Python
    # interpreter targets at least Python >= 3.8 and thus supports PEP 544.
    for typing_protocol in TYPING_PROTOCOLS:
        assert is_hint_pep544_protocol(typing_protocol) is (
            IS_PYTHON_AT_LEAST_3_8)

    # Assert this tester rejects all builtin types. For unknown reasons, some
    # but *NOT* all builtin types (e.g., "int") erroneously present themselves
    # to be PEP 544-compliant protocols. *sigh*
    for class_builtin in TYPES_BUILTIN:
        assert is_hint_pep544_protocol(class_builtin) is False

    # Assert this tester rejects standard type hints in either case.
    assert is_hint_pep544_protocol(Union[int, str]) is False

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets at least Python >= 3.8 and thus
    # supports PEP 544...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from abc import abstractmethod

        # Intentionally import @beartype-accelerated protocols.
        from beartype.typing import (
            Protocol,
            runtime_checkable,
        )

        # User-defined protocol parametrized by *NO* type variables declaring
        # arbitrary concrete and abstract methods.
        @runtime_checkable
        class ProtocolCustomUntypevared(Protocol):
            def alpha(self) -> str:
                return 'Of a Spicily sated'

            @abstractmethod
            def omega(self) -> str: pass

        # Assert this accepts a standardized protocol.
        assert is_hint_pep544_protocol(SupportsInt) is True

        # Assert this accepts a user-defined protocol.
        assert is_hint_pep544_protocol(ProtocolCustomUntypevared) is True


def test_is_hint_pep544_io_generic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.utilpep544.is_hint_pep484_generic_io`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.utilpep544 import (
        is_hint_pep484_generic_io)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        PEP484_GENERICS_IO)
    from typing import Union

    # Assert this tester accepts these classes *ONLY* if the active Python
    # interpreter targets at least Python >= 3.8 and thus supports PEP 544.
    for pep484_generic_io in PEP484_GENERICS_IO:
        assert is_hint_pep484_generic_io(pep484_generic_io) is (
            IS_PYTHON_AT_LEAST_3_8)

    # Assert this tester rejects standard type hints in either case.
    assert is_hint_pep484_generic_io(Union[int, str]) is False

# ....................{ TESTS ~ getters                    }....................
def test_get_hint_pep544_io_protocol_from_generic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.utilpep544.reduce_hint_pep484_generic_io_to_pep544_protocol`
    tester.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep544Exception
    from beartype._util.hint.pep.proposal.utilpep544 import (
        reduce_hint_pep484_generic_io_to_pep544_protocol)
    from beartype._util.hint.pep.proposal.utilpep593 import is_hint_pep593
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        PEP484_GENERICS_IO)
    from pytest import raises
    from typing import Union

    # For each PEP 484-compliant "typing" IO generic base class...
    for pep484_generic_io in PEP484_GENERICS_IO:
        # If the active Python interpreter targets at least Python >= 3.8 and
        # thus supports PEP 544...
        if IS_PYTHON_AT_LEAST_3_8:
            # Defer version-dependent imports.
            from typing import Protocol

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
        # Else, assert this function raises an exception.
        else:
            with raises(BeartypeDecorHintPep544Exception):
                reduce_hint_pep484_generic_io_to_pep544_protocol(
                    pep484_generic_io, '')

    # Assert this function rejects standard type hints in either case.
    with raises(BeartypeDecorHintPep544Exception):
        reduce_hint_pep484_generic_io_to_pep544_protocol(Union[int, str], '')
