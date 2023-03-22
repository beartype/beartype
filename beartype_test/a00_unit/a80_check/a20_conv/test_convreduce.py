#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint conversion utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._check.conv.convreduce` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ reducers                   }....................
def test_reduce_hint() -> None:
    '''
    Test the private
    :func:`beartype._check.conv.convreduce.reduce_hint` reducer.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar import (
        BeartypeDecorHintNonpepNumpyException,
        BeartypeDecorHintNonpepNumpyWarning,
    )
    from beartype.vale import IsEqual
    from beartype._cave._cavefast import NoneType
    from beartype._check.conv.convreduce import reduce_hint
    from beartype._conf.confcls import (
        BEARTYPE_CONF_DEFAULT,
        BeartypeConf,
    )
    from beartype._data.datatyping import (
        Pep484TowerComplex,
        Pep484TowerFloat,
    )
    from beartype._data.hint.pep.sign.datapepsigns import HintSignAnnotated
    from beartype._util.hint.pep.proposal.utilpep593 import is_hint_pep593
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        PEP484_GENERICS_IO,
        T,
        T_BOUNDED,
        T_CONSTRAINED,
    )
    from beartype_test._util.mod.pytmodtyping import (
        import_typing_attr_or_none_safe)
    from beartype_test._util.mod.pytmodtest import (
        is_package_numpy,
        is_package_numpy_typing_ndarray_deep,
    )
    from pytest import raises, warns
    # from typing import TypeVar

    # ..................{ LOCALS                             }..................
    # Positional arguments to be passed to all calls to reduce_hints() below.
    args = (BEARTYPE_CONF_DEFAULT, None, '')

    # ..................{ CORE                               }..................
    # Assert this reducer preserves an isinstanceable type as is.
    assert reduce_hint(int, *args) is int

    # Assert this reducer reduces "None" to "type(None)".
    assert reduce_hint(None, *args) is NoneType

    # ..................{ PEP 484 ~ tower                    }..................
    # Assert this reducer expands the builtin "float" and "complex" types to
    # their corresponding numeric towers when configured to do so.
    assert reduce_hint(
        float, BeartypeConf(is_pep484_tower=True), None, '') is (
        Pep484TowerFloat)
    assert reduce_hint(
        complex, BeartypeConf(is_pep484_tower=True), None, '') is (
        Pep484TowerComplex)

    # Assert this reducer preserves the builtin "float" and "complex" types as
    # is when configured to disable the implicit numeric tower.
    assert reduce_hint(
        float,   BeartypeConf(is_pep484_tower=False), None, '') is float
    assert reduce_hint(
        complex, BeartypeConf(is_pep484_tower=False), None, '') is complex

    # ..................{ PEP 484 ~ typevar                  }..................
    # Assert this reducer preserves unbounded type variables as is.
    assert reduce_hint(T, *args) is T

    # Assert this reducer reduces bounded type variables to their upper bound.
    assert reduce_hint(T_BOUNDED, *args) is int

    # Union of all constraints parametrizing a constrained type variable,
    # reduced from that type variable.
    typevar_constraints_union = reduce_hint(T_CONSTRAINED, *args)

    # Assert this union contains all constraints parametrizing this variable.
    assert str   in typevar_constraints_union.__args__
    assert bytes in typevar_constraints_union.__args__

    # ..................{ PEP 544                            }..................
    # If the active Python interpreter targets Python >= 3.8 and thus declares
    # the "typing.Protocol" superclass...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from typing import Protocol

        # For each PEP 484-compliant "typing" IO generic superclass...
        for pep484_generic_io in PEP484_GENERICS_IO:
            # Equivalent protocol reduced from this generic.
            pep544_protocol_io = reduce_hint(pep484_generic_io, *args)

            # Assert this protocol is either...
            assert (
                # A PEP 593-compliant type metahint generalizing a protocol
                # *OR*...
                is_hint_pep593(pep544_protocol_io) or
                # A PEP 544-compliant protocol.
                issubclass(pep544_protocol_io, Protocol)
            )

    # ..................{ PEP 557                            }..................
    # If the active Python interpreter targets Python >= 3.8 and thus supports
    # PEP 557...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from dataclasses import InitVar

        # Assert this reducer reduces an "InitVar" to its subscripted argument.
        assert reduce_hint(InitVar[str], *args) is str

    # ..................{ PEP 593                            }..................
    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_typing_attr_or_none_safe('Annotated')

    # If the "typing.Annotated" type hint factory is importable, the active
    # Python interpreter supports PEP 593. In this case...
    if Annotated is not None:
        # Assert this reducer reduces a beartype-agnostic metahint to the
        # lower-level hint it annotates.
        assert reduce_hint(Annotated[int, 42], *args) is int

        # If the active Python interpreter targets Python >= 3.8 and thus
        # supports the __class_getitem__() dunder method required by beartype
        # validators...
        if IS_PYTHON_AT_LEAST_3_8:
            # Assert this reducer preserves a beartype-specific metahint as is.
            leaves_when_laid = Annotated[
                str, IsEqual['In their noonday dreams.']]
            assert reduce_hint(leaves_when_laid, *args) is leaves_when_laid

    # ..................{ NUMPY                              }..................
    # If a recent version of NumPy is importable...
    if is_package_numpy():
        # Defer third party imports.
        from numpy import float64, ndarray
        from numpy.typing import NDArray

        # If beartype deeply supports "numpy.typing.NDArray" type hints under
        # the active Python interpreter...
        if is_package_numpy_typing_ndarray_deep():
            # Beartype validator reduced from such a hint.
            ndarray_reduced = reduce_hint(NDArray[float64], *args)

            # Assert this validator is a "typing{_extensions}.Annotated" hint.
            assert get_hint_pep_sign(ndarray_reduced) is HintSignAnnotated

            # Assert that reducing a "numpy.typing.NDArray" type hint
            # erroneously subscripted by an object *NOT* reducible to a data
            # type raises the expected exception.
            with raises(BeartypeDecorHintNonpepNumpyException):
                reduce_hint(NDArray[
                    'From_my_wings_are_shaken_the_dews_that_waken'], *args)
        # Else, beartype only shallowly supports "numpy.typing.NDArray" type
        # hints under the active Python interpreter. In this case...
        else:
            # Assert this reducer reduces such a hint to the untyped NumPy
            # array class "numpy.ndarray" with a non-fatal warning.
            with warns(BeartypeDecorHintNonpepNumpyWarning):
                assert reduce_hint(NDArray[float64], *args) is ndarray
