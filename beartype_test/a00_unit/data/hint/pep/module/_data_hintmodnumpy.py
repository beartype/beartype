#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**NumPy-specific PEP-noncompliant type hints** (i.e., unofficial type hints
declared by the third-party :mod:`numpy` package) test data.

These hints include:

* **Typed NumPy arrays** (i.e., subscriptions of the
  :attr:`numpy.typing.NDArray` type hint factory).

Caveats
----------
Although NumPy-specific type hints are technically PEP-noncompliant, the
:mod:`beartype` codebase currently treats these hints as PEP-compliant to
dramatically simplify code generation for these hints. Ergo, so we do.
'''

# ....................{ IMPORTS                           }....................
from beartype_test._util.module.pytmodtest import (
    is_package_numpy_typing_ndarray_deep)

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :mod:`numpy`-specific type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # ..................{ UNSUPPORTED                       }..................
    # If beartype does *NOT* deeply support "numpy.typing.NDArray" type hints
    # under the active Python interpreter, silently reduce to a noop.
    if not is_package_numpy_typing_ndarray_deep():
        return
    # Else, beartype deeply supports "numpy.typing.NDArray" type hints under
    # the active Python interpreter.

    # ..................{ IMPORTS                           }..................
    # Defer attribute-dependent imports.
    from beartype.typing import Tuple
    from beartype.vale import Is
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignNumpyArray,
        HintSignTuple,
    )
    from beartype._util.module.lib.utiltyping import import_typing_attr
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # Defer NumPy-specific imports.
    from numpy import asarray, dtype, float32, float64, floating
    from numpy.typing import NDArray
    from typing import Any

    # ..................{ TUPLES                            }..................
    # Add NumPy-specific test type hints to this tuple global.
    data_module.HINTS_PEP_META.extend((
        # ................{ NUMPY ~ array                     }................
        # Untyped unsubscripted NumPy array.
        HintPepMetadata(
            hint=NDArray,
            pep_sign=HintSignNumpyArray,
            # "NDArray" is implemented as:
            # * Under Python >= 3.9, a PEP 585-compliant generic.
            # * Under Python >= 3.8, a pure-Python generic backport.
            is_pep585_builtin=IS_PYTHON_AT_LEAST_3_9,
            is_type_typing=False,
            is_typing=False,
            # Oddly, NumPy implicitly parametrizes the "NDArray[Any]" type hint
            # by expanding that hint to "numpy.typing.NDArray[+ScalarType]",
            # where "+ScalarType" is a public type variable declared by the
            # "numpy" package bounded above by the "numpy.generic" abstract
            # base class for NumPy scalars. *sigh*
            is_typevars=True,
            piths_meta=(
                # NumPy array containing only 64-bit integers.
                HintPithSatisfiedMetadata(asarray((
                    1, 0, 3, 5, 2, 6, 4, 9, 2, 3, 8, 4, 1, 3, 7, 7, 5, 0,))),
                # NumPy array containing only 64-bit floats.
                HintPithSatisfiedMetadata(asarray((
                    1.3, 8.23, 70.222, 726.2431, 8294.28730, 100776.357238,))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith='Ine Gerrymander‐consigned electorate sangu‐',
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected class.
                    exception_str_match_regexes=(r'\bnumpy\.ndarray\b',),
                ),
            ),
        ),

        # Untyped subscripted NumPy array.
        HintPepMetadata(
            hint=NDArray[Any],
            pep_sign=HintSignNumpyArray,
            is_pep585_builtin=IS_PYTHON_AT_LEAST_3_9,
            is_type_typing=False,
            is_typing=False,
            piths_meta=(
                # NumPy array containing only 64-bit integers.
                HintPithSatisfiedMetadata(asarray((
                    1, 7, 39, 211, 1168, 6728, 40561, 256297, 1696707,))),
                # NumPy array containing only 64-bit floats.
                HintPithSatisfiedMetadata(asarray((
                    1.1, 2.4, -4.4, 32.104, 400.5392, -3680.167936,))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith=(
                        'Inity my guinea‐konsealed Ğuinness’ pint '
                        'glockenspieled spells',
                    ),
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected class.
                    exception_str_match_regexes=(r'\bnumpy\.ndarray\b',),
                ),
            ),
        ),

        # ................{ NUMPY ~ array : dtype : equals    }................
        # Typed NumPy array subscripted by an actual data type (i.e., instance
        # of the "numpy.dtype" class).
        HintPepMetadata(
            hint=NDArray[dtype(float64)],
            pep_sign=HintSignNumpyArray,
            is_pep585_builtin=IS_PYTHON_AT_LEAST_3_9,
            is_type_typing=False,
            is_typing=False,
            piths_meta=(
                # NumPy array containing only 64-bit floats.
                HintPithSatisfiedMetadata(
                    asarray((1.0, 1.5, 1.8333, 2.08333, 2.28333, 2.45,)),
                ),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith='Aggrandizing strifes with‐in',
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected class.
                    exception_str_match_regexes=(r'\bnumpy\.ndarray\b',),
                ),
                # NumPy array containing only 64-bit integers.
                HintPithUnsatisfiedMetadata(
                    pith=asarray((4, 36, 624, 3744, 5108, 10200, 54912,)),
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected data type.
                    exception_str_match_regexes=(r'\bfloat64\b',),
                ),
            ),
        ),

        # Typed NumPy array subscripted by a scalar data type. Since scalar
        # data types are *NOT* actual data types, this exercises an edge case.
        HintPepMetadata(
            hint=NDArray[float64],
            pep_sign=HintSignNumpyArray,
            is_pep585_builtin=IS_PYTHON_AT_LEAST_3_9,
            is_type_typing=False,
            is_typing=False,
            piths_meta=(
                # NumPy array containing only 64-bit floats.
                HintPithSatisfiedMetadata(asarray(
                    (2.0, 2.5, 2.6, 2.7083, 2.716, 2.71805,))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith='Silver, ore, and almost dazedly aggro‐',
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected class.
                    exception_str_match_regexes=(r'\bnumpy\.ndarray\b',),
                ),
                # NumPy array containing only 64-bit integers.
                HintPithUnsatisfiedMetadata(
                    pith=asarray((1, 1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235,)),
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected data type.
                    exception_str_match_regexes=(r'\bfloat64\b',),
                ),
            ),
        ),

        # ................{ NUMPY ~ array : dtype : subclass  }................
        # Typed NumPy array subscripted by a data type superclass.
        HintPepMetadata(
            hint=NDArray[floating],
            pep_sign=HintSignNumpyArray,
            is_pep585_builtin=IS_PYTHON_AT_LEAST_3_9,
            is_type_typing=False,
            is_typing=False,
            piths_meta=(
                # NumPy array containing only 32-bit floats.
                HintPithSatisfiedMetadata(asarray(
                    (1.2, 2.4, 3.0, 3.6, 4.0, 4.5, 4.8, 5.6, 6.0, 6.3, 7.0,),
                    dtype=float32,
                )),
                # NumPy array containing only 64-bit floats.
                HintPithSatisfiedMetadata(asarray(
                    (3.2, 5, 1, 2, 1, 8, 2, 5, 1, 3, 1, 2.8, 1, 1.5, 1, 1, 4,),
                    dtype=float64,
                )),
                # String constant.
                HintPithUnsatisfiedMetadata('Then, and'),
                # NumPy array containing only 64-bit integers.
                HintPithUnsatisfiedMetadata(asarray(
                    (3, 6, 5, 12, 7, 18, 9, 12, 11, 30, 13, 16, 15, 18, 17,))),
            ),
        ),
    ))

    # ..................{ VALIDATORS ~ hints                }..................
    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise. By prior
    # validation, this factory *MUST* be non-"None" here.
    Annotated = import_typing_attr('Annotated')

    # Validator matching one-dimensional NumPy arrays of floats of 64-bit
    # precision, combining both validator and NumPy type hinting syntax. This
    # exercises an edge case previously generating syntactically invalid code.
    Numpy1DFloat64Array = Annotated[
        NDArray[float64], Is[lambda array: array.ndim == 1]]

    # ..................{ VALIDATORS ~ tuples               }..................
    # Add NumPy-specific test type hints to this tuple global.
    data_module.HINTS_PEP_META.extend((
        # ................{ NUMPY ~ array : nested            }................
        # 2-tuple of one-dimensional typed NumPy arrays of 64-bit floats.
        HintPepMetadata(
            hint=Tuple[Numpy1DFloat64Array, Numpy1DFloat64Array],
            pep_sign=HintSignTuple,
            isinstanceable_type=tuple,
            is_pep585_builtin=Tuple is tuple,
            piths_meta=(
                # 2-tuple of NumPy arrays containing only 64-bit floats.
                HintPithSatisfiedMetadata((
                    asarray((0.5, 0.75, 0.875, 0.9375, 0.96875, 0.984375)),
                    asarray((1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5)),
                )),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith=(
                        "A Spherically clerical,"
                        "cylindroid‐cindered cleft, and",
                    ),
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected class.
                    exception_str_match_regexes=(r'\bnumpy\.ndarray\b',),
                ),
                # 2-tuple of NumPy arrays containing only integers.
                HintPithUnsatisfiedMetadata(
                    pith=(
                        asarray((1, 1, 4, 6, 14, 23, 45, 72, 126, 195, 315,)),
                        asarray((1, 0, 1, 1, 2, 2, 5, 4, 9, 10, 16, 19, 31,)),
                    ),
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected data type.
                    exception_str_match_regexes=(r'\bfloat64\b',),
                ),
            ),
        ),
    ))
