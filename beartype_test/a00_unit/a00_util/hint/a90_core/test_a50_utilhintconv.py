#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint conversion utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.utilhintconv` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ coercers                  }....................
def test_coerce_hint_root() -> None:
    '''
    Test the private :func:`beartype._util.hint.utilhintconv._coerce_hint_root`
    reducer.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.utilhintconv import _coerce_hint_root

    # ..................{ CALLABLES                         }..................
    def one_legion_of_wild_thoughts() -> str:
        return 'whose wandering wings'

    # ..................{ CORE                              }..................
    # Assert this coercer preserves an isinstanceable type as is.
    assert _coerce_hint_root(
        hint=str,
        func=one_legion_of_wild_thoughts,
        pith_name='return',
        exception_prefix='',
    ) is str

    # ..................{ PEP 585                           }..................
    # Note that the PEP 585-specific logic implemented by this coercer is
    # tested by the test_coerce_hint_any() unit test below.
    # ..................{ MYPY                              }..................
    # Note that the mypy-specific logic implemented by this coercer is
    # tested by the "a00_unit.a90_decor.code.nonpep.test_codemypy" submodule.
    # ..................{ NON-PEP                           }..................
    # Note that the tuple union-specific logic implemented by this coercer is
    # tested by... something else, presumably? *sigh*


def test_coerce_hint_any() -> None:
    '''
    Test the private :func:`beartype._util.hint.utilhintconv._coerce_hint_any`
    reducer.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.utilhintconv import _coerce_hint_any
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

    # ..................{ CORE                              }..................
    # Assert this coercer preserves an isinstanceable type as is.
    assert _coerce_hint_any(int) is int

    # ..................{ PEP 585                           }..................
    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585...
    if IS_PYTHON_AT_LEAST_3_9:
        # Arbitrary PEP 585-compliant type hint.
        hint_pep585 = list[int]

        # Assert this coercer preserves the first passed instance of a PEP
        # 585-compliant type hint as is.
        assert _coerce_hint_any(hint_pep585) is hint_pep585

        # Assert this coercer returns the first passed instance of a PEP
        # 585-compliant type hint when passed a copy of that instance. PEP
        # 585-compliant type hints are *NOT* self-caching: e.g.,
        #     >>> list[int] is list[int]
        #     False
        assert _coerce_hint_any(list[int]) is hint_pep585

# ....................{ TESTS ~ reducers                  }....................
def test_reduce_hint() -> None:
    '''
    Test the private :func:`beartype._util.hint.utilhintconv._reduce_hint`
    reducer.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintNonpepNumpyException,
        BeartypeDecorHintNonpepNumpyWarning,
    )
    from beartype.vale import IsEqual
    from beartype._cave._cavefast import NoneType
    from beartype._data.hint.pep.sign.datapepsigns import HintSignAnnotated
    from beartype._util.hint.pep.proposal.utilpep593 import is_hint_pep593
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    from beartype._util.hint.utilhintconv import _reduce_hint
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        PEP484_GENERICS_IO,
        T,
        T_BOUNDED,
        T_CONSTRAINED,
    )
    from beartype_test.util.mod.pytmodimport import (
        import_module_typing_any_attr_or_none_safe)
    from beartype_test.util.mod.pytmodtest import (
        is_package_numpy,
        is_package_numpy_typing_ndarray_deep,
    )
    from pytest import raises, warns
    # from typing import TypeVar

    # ..................{ CORE                              }..................
    # Assert this reducer preserves an isinstanceable type as is.
    assert _reduce_hint(int, '') is int

    # Assert this reducer reduces "None" to "type(None)".
    assert _reduce_hint(None, '') is NoneType

    # ..................{ PEP 484 ~ typevar                 }..................
    # Assert this reducer preserves unbounded type variables as is.
    assert _reduce_hint(T, '') is T

    # Assert this reducer reduces bounded type variables to their upper bound.
    assert _reduce_hint(T_BOUNDED, '') is int

    # Union of all constraints parametrizing a constrained type variable,
    # reduced from that type variable.
    typevar_constraints_union = _reduce_hint(T_CONSTRAINED, '')

    # Assert this union contains all constraints parametrizing this variable.
    assert str   in typevar_constraints_union.__args__
    assert bytes in typevar_constraints_union.__args__

    # ..................{ PEP 544                           }..................
    # If the active Python interpreter targets Python >= 3.8 and thus declares
    # the "typing.Protocol" superclass...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from typing import Protocol

        # For each PEP 484-compliant "typing" IO generic superclass...
        for pep484_generic_io in PEP484_GENERICS_IO:
            # Equivalent protocol reduced from this generic.
            pep544_protocol_io = _reduce_hint(pep484_generic_io, '')

            # Assert this protocol is either...
            assert (
                # A PEP 593-compliant type metahint generalizing a protocol
                # *OR*...
                is_hint_pep593(pep544_protocol_io) or
                # A PEP 544-compliant protocol.
                issubclass(pep544_protocol_io, Protocol)
            )

    # ..................{ PEP 557                           }..................
    # If the active Python interpreter targets Python >= 3.8 and thus supports
    # PEP 557...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from dataclasses import InitVar

        # Assert this reducer reduces an "InitVar" to its subscripted argument.
        assert _reduce_hint(InitVar[str], '') is str

    # ..................{ PEP 593                           }..................
    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_module_typing_any_attr_or_none_safe('Annotated')

    # If the "typing.Annotated" type hint factory is importable, the active
    # Python interpreter supports PEP 593. In this case...
    if Annotated is not None:
        # Assert this reducer reduces a beartype-agnostic metahint to the
        # lower-level hint it annotates.
        assert _reduce_hint(Annotated[int, 42], '') is int

        # If the active Python interpreter targets Python >= 3.8 and thus
        # supports the __class_getitem__() dunder method required by beartype
        # validators...
        if IS_PYTHON_AT_LEAST_3_8:
            # Assert this reducer preserves a beartype-specific metahint as is.
            leaves_when_laid = Annotated[
                str, IsEqual['In their noonday dreams.']]
            assert _reduce_hint(leaves_when_laid, '') is leaves_when_laid

    # ..................{ NUMPY                             }..................
    # If a recent version of NumPy is importable...
    if is_package_numpy():
        # Defer third party imports.
        from numpy import float64, ndarray
        from numpy.typing import NDArray

        # If beartype deeply supports "numpy.typing.NDArray" type hints under
        # the active Python interpreter...
        if is_package_numpy_typing_ndarray_deep():
            # Beartype validator reduced from such a hint.
            ndarray_reduced = _reduce_hint(NDArray[float64], '')

            # Assert this validator is a "typing{_extensions}.Annotated" hint.
            assert get_hint_pep_sign(ndarray_reduced) is HintSignAnnotated

            # Assert that reducing a "numpy.typing.NDArray" type hint
            # erroneously subscripted by an object *NOT* reducible to a data
            # type raises the expected exception.
            with raises(BeartypeDecorHintNonpepNumpyException):
                _reduce_hint(NDArray[
                    'From my wings are shaken the dews that waken'], '')
        # Else, beartype only shallowly supports "numpy.typing.NDArray" type
        # hints under the active Python interpreter. In this case...
        else:
            # Assert this reducer reduces such a hint to the untyped NumPy
            # array class "numpy.ndarray" with a non-fatal warning.
            with warns(BeartypeDecorHintNonpepNumpyWarning):
                assert _reduce_hint(NDArray[float64], '') is ndarray
