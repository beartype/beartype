#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint getter utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.utilhintget` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                             }....................
#FIXME: Test *ALL* kinds of hints reduced by this getter, including:
#* Typed NumPy arrays (e.g., "numpy.typing.NDArray[numpy.float64]").
def test_get_hint_reduced() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhintget.get_hint_reduced` getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintNonPepNumPyException
    from beartype.vale import IsEqual
    from beartype._cave._cavefast import NoneType
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignAnnotated,
    )
    from beartype._util.hint.utilhintget import get_hint_reduced
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        PEP484_GENERICS_IO)
    from beartype_test.util.mod.pytmodimport import (
        import_module_typing_any_attr_or_none_safe)
    from beartype_test.util.mod.pytmodtest import (
        is_package_numpy_typing_ndarray_supported)

    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_module_typing_any_attr_or_none_safe('Annotated')

    # Assert this getter preserves a PEP-noncompliant object as is.
    assert get_hint_reduced(int) is int

    # Assert this getter reduces "None" to "type(None)".
    assert get_hint_reduced(None) is NoneType

    # If the active Python interpreter targets Python >= 3.8 and thus declares
    # the "typing.Protocol" superclass...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from typing import Protocol

        # For each PEP 484-compliant "typing" IO generic superclass...
        for pep484_generic_io in PEP484_GENERICS_IO:
            # Equivalent PEP 544-compliant protocol reduced from this generic.
            pep544_protocol_io = get_hint_reduced(pep484_generic_io)

            # Assert this protocol actually is a protocol.
            assert issubclass(pep544_protocol_io, Protocol)

    # If this factory is importable, the active Python interpreter supports PEP
    # 593. In this case...
    if Annotated is not None:
        # Assert this getter reduces a beartype-agnostic metahint to the
        # lower-level hint it annotates.
        assert get_hint_reduced(Annotated[int, 42]) is int

        # Assert this getter preserves a beartype-specific metahint as is.
        leaves_when_laid = Annotated[str, IsEqual['In their noonday dreams.']]
        assert get_hint_reduced(leaves_when_laid) is leaves_when_laid

    # If the "numpy.typing.NDArray" type hint is supported by beartype under
    # the active Python interpreter...
    if is_package_numpy_typing_ndarray_supported():
        # Defer third party imports.
        from numpy import float64
        from numpy.typing import NDArray

        # Beartype validator reduced from a "numpy.typing.NDArray" type hint.
        ndarray_reduced = get_hint_reduced(NDArray[float64])

        # Assert this validator is a "typing{_extensions}.Annotated" type hint.
        assert get_hint_pep_sign(ndarray_reduced) is HintSignAnnotated

        # Assert that reducing a "numpy.typing.NDArray" type hint erroneously
        # subscripted by an object *NOT* reducible to a data type raises the
        # expected exception.
        with raises(BeartypeDecorHintNonPepNumPyException):
            get_hint_reduced(NDArray[
                'From my wings are shaken the dews that waken'])
