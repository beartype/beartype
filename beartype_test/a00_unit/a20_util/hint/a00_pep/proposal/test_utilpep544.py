#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`544` **type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep544` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                    }....................
def test_is_hint_pep544_protocol() -> None:
    '''
    Test usage of the private
    :mod:`beartype._util.hint.pep.proposal.utilpep544.is_hint_pep544_protocol`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.utilpep544 import (
        is_hint_pep544_protocol)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from beartype_test.a00_unit.data.data_type import Class

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

        # Intentionally import @beartype-unaccelerated protocols.
        from typing import SupportsInt

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
