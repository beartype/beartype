#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural type
hint inference API** unit tests.

This submodule unit tests the public :mod:`beartype.door.infer_hint` function.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
def test_door_infer_hint(
    door_cases_infer_hint: (
    'Dict[beartype.BeartypeConf, Iterable[Tuple[object, object]]]')) -> None:
    '''
    Test the :func:`beartype.door.infer_hint` function.

    Parameters
    ----------
    door_cases_infer_hint : Dict[beartype.BeartypeConf, Iterable[Tuple[object, object]]]
        Dictionary mapping from each relevant beartype configuration to a
        corresponding iterable of all **type hint inference cases** specific to
        that configuration.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import infer_hint
    from beartype.roar import BeartypeConfException
    from beartype._conf.confcommon import get_beartype_conf_strategy_on
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Default linear-time configuration.
    CONF_STRATEGY_ON = get_beartype_conf_strategy_on()

    # ....................{ PASS                           }....................
    # For each relevant beartype configuration...
    for conf, cases in door_cases_infer_hint.items():
        # If this is the default linear-time configuration...
        if conf == CONF_STRATEGY_ON:
            # For each test object and expected type hint to be inferred from
            # that object...
            for obj, hint in cases:
                # Assert this function returns this type hint for this object
                # *WITHOUT* explicitly passing this configuration. Doing so
                # exercises that this function behaves as expected when passed
                # *NO* configuration.
                assert infer_hint(obj) == hint
        # Else, this is a non-default configuration. In this case...
        else:
            # For each test object and expected type hint to be inferred from
            # that object...
            for obj, hint in cases:
                # Assert this function returns this type hint for this object
                # under this non-default configuration.
                assert infer_hint(obj, conf=conf) == hint

    # ....................{ FAIL                           }....................
    # Assert that this function raises the expected exception when passed an
    # arbitrary object and an invalid beartype configuration.
    with raises(BeartypeConfException):
        infer_hint('Red, yellow,', conf='or ethereally pale,')


def test_door_infer_hint_recursion() -> None:
    '''
    Test the :func:`beartype.door.infer_hint` function with respect to
    **container recursion** (i.e., objects self-referentially containing
    themselves as items inside themselves).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        BeartypeStrategy,
    )
    from beartype.door import infer_hint
    from beartype.door._func.infer.inferhint import (
        BeartypeInferHintContainerRecursion)
    from beartype.roar import BeartypeDoorInferHintRecursionWarning
    from beartype.typing import (
        List,
        Union,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from pytest import warns

    # ..................{ LOCALS ~ list                      }..................
    # Recursive list containing *ONLY* a reference to itself and thus suitable
    # for O(1) constant-time type hint inference.
    LIST_RECURSIVE_STRATEGY_O1 = []
    LIST_RECURSIVE_STRATEGY_O1.append(LIST_RECURSIVE_STRATEGY_O1)

    # Recursive list containing a reference to itself as well as other unrelated
    # items and thus suitable for O(n) linear-time type hint inference.
    LIST_RECURSIVE_STRATEGY_ON = [
        "Rivals the pride of summer. 'Tis the haunt",
        b'Of every gentle wind, whose breath can teach',
    ]
    LIST_RECURSIVE_STRATEGY_ON.append(LIST_RECURSIVE_STRATEGY_ON)

    # ..................{ ASSERTS                            }..................
    # Assert that this function, when configured for O(1) constant-time type
    # hint inference and passed a recursive list containing *ONLY* a reference
    # to itself:
    # * Emits the expected warning.
    # * Returns the expected type hint.
    with warns(BeartypeDoorInferHintRecursionWarning):
        assert infer_hint(
            LIST_RECURSIVE_STRATEGY_O1,
            conf=BeartypeConf(strategy=BeartypeStrategy.O1),
        ) == List[BeartypeInferHintContainerRecursion]

    # Assert that this function, when configured for O(n) linear-time type hint
    # inference and passed a recursive list containing a reference to itself as
    # well as other unrelated itemsf:
    # * Emits the expected warning.
    # * Returns the expected type hint.
    with warns(BeartypeDoorInferHintRecursionWarning):
        assert infer_hint(LIST_RECURSIVE_STRATEGY_ON) == List[
            # If the active Python interpreter targets Python >= 3.10 and thus
            # supports PEP 604-compliant new-style unions, this kind of union;
            str | bytes | BeartypeInferHintContainerRecursion
            if IS_PYTHON_AT_LEAST_3_10 else
            # Else, the active Python interpreter targets Python < 3.10 and thus
            # fails to support PEP 604-compliant new-style unions. In this case,
            # fallback to a PEP 484-compliant old-style union.
            Union[str, bytes, BeartypeInferHintContainerRecursion]
        ]

# ....................{ TESTS ~ third-party                }....................
# Tests exercising infer_hint() with respect to third-party packages.

def test_door_infer_hint_numpy(
    door_cases_infer_hint: 'Iterable[Tuple[object, object]]',
    numpy_arrays: 'beartype_test.a00_unit.data.api.data_apinumpy._NumpyArrays',
) -> None:
    '''
    Test the :func:`beartype.door.infer_hint` function with respect to
    third-party :mod:`numpy` arrays if :mod:`numpy` is importable *or* silently
    skip this test otherwise (i.e., if :mod:`numpy` is unimportable).

    Parameters
    ----------
    door_cases_infer_hint : Iterable[Tuple[object, object]]
        Iterable of **type hint inference cases** (i.e., 2-tuples ``(obj,
        hint)`` describing the type hint matching an arbitrary object).
    numpy_arrays : beartype_test.a00_unit.data.api.data_apinumpy._NumpyArrays
        **NumPy arrays dataclass** (i.e., well-typed and -described object
        comprising various :mod:`numpy` arrays).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import infer_hint
    from beartype.vale import (
        IsAttr,
        IsEqual,
    )
    from beartype._util.api.standard.utiltyping import import_typing_attr_or_none
    from numpy import unsignedinteger
    from numpy.typing import NDArray

    # ....................{ LOCALS                         }....................
    # PEP 593-compliant "Annotated" type hint factory imported from either the
    # standard "typing" or third-party "typing_extensions" modules if importable
    # from at least one of those modules *OR* "None" otherwise.
    Annotated = import_typing_attr_or_none('Annotated')

    # List of all NumPy type hint inference cases (i.e., 2-tuples "(obj, hint)"
    # describing the type hint matching a NumPy array).
    INFER_HINT_NUMPY_CASES = [
        # ..................{ NUMPY                          }..................
        # One-dimensional NumPy boolean arrays are annotated as either...
        (numpy_arrays.array_1d_boolean, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "bool" type annotated to require a one-dimensional array.
            Annotated[NDArray[bool], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[bool]
        )),
        # One-dimensional NumPy complex arrays are annotated as either...
        (numpy_arrays.array_1d_complex_128, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "complex" type annotated to require a one-dimensional
            # array.
            Annotated[NDArray[complex], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[complex]
        )),
        # One-dimensional NumPy 32-bit floating point arrays are annotated as
        # either...
        (numpy_arrays.array_1d_float_32, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "float" type annotated to require a one-dimensional array.
            Annotated[NDArray[float], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[float]
        )),
        # One-dimensional NumPy 64-bit floating point arrays are annotated as
        # either...
        (numpy_arrays.array_1d_float_64, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "float" type annotated to require a one-dimensional array.
            Annotated[NDArray[float], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[float]
        )),
        # One-dimensional NumPy 32-bit integer arrays are annotated as either...
        (numpy_arrays.array_1d_int_32, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "int" type annotated to require a one-dimensional array.
            Annotated[NDArray[int], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[int]
        )),
        # One-dimensional NumPy 64-bit integer arrays are annotated as either...
        (numpy_arrays.array_1d_int_64, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "int" type annotated to require a one-dimensional array.
            Annotated[NDArray[int], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[int]
        )),
        # One-dimensional NumPy 32-bit unsigned integer arrays are annotated as
        # either...
        (numpy_arrays.array_1d_uint_32, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # "numpy.unsignedinteger" dtype annotated to require a
            # one-dimensional array.
            Annotated[NDArray[unsignedinteger], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[unsignedinteger]
        )),
        # One-dimensional NumPy 64-bit unsigned integer arrays are annotated as
        # either...
        (numpy_arrays.array_1d_uint_64, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # "numpy.unsignedinteger" dtype annotated to require a
            # one-dimensional array.
            Annotated[NDArray[unsignedinteger], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[unsignedinteger]
        )),
        # One-dimensional NumPy array serving as a memory view over arbitrary
        # bytes all of the same length are annotated as either...
        (numpy_arrays.array_1d_memory_view, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "memoryview" type annotated to require a one-dimensional
            # array.
            Annotated[NDArray[memoryview], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[memoryview]
        )),
        # One-dimensional NumPy byte string arrays are annotated as either...
        (numpy_arrays.array_1d_string_byte, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "bytes" type annotated to require a one-dimensional array.
            Annotated[NDArray[bytes], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[bytes]
        )),
        # One-dimensional NumPy Unicode string arrays are annotated as either...
        (numpy_arrays.array_1d_string_char, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "str" type annotated to require a one-dimensional array.
            Annotated[NDArray[str], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[str]
        )),
    ]

    # ....................{ ASSERTS                        }....................
    # For each type hint inference case to be tested...
    for obj, hint in INFER_HINT_NUMPY_CASES:
        # Assert this function returns the expected type hint for this object.
        assert infer_hint(obj) == hint


@skip_unless_package('pygments')
def test_door_infer_hint_pygments() -> None:
    '''
    Test the :func:`beartype.door.infer_hint` function with respect to
    third-party :mod:`pygments` package if that package is importable *or*
    silently skip this test otherwise (i.e., if that package is unimportable).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import infer_hint
    from beartype._data.hint.pep.sign.datapepsigns import HintSignList
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
    from pygments.lexers import PythonLexer

    # ....................{ LOCALS                         }....................
    # List of all root tokens exposed by the pygments Python lexer, exercising
    # edge cases in the infer_hint() function that continued to break. Ugh!
    root_tokens = PythonLexer().tokens['root']

    # Hint inferred for this list, implicitly exercising that the infer_hint()
    # function successfully infers this hint *WITHOUT* raising an exception --
    # which it used to.
    root_tokens_hint = infer_hint(root_tokens)

    # ....................{ ASSERTS                        }....................
    # Assert that this hint is a subscripted "list[...]" hint.
    #
    # Note that we intentionally do *NOT* assert the specific child hints
    # subscripting this hint. Why? Because these child hints include references
    # to private "pygments" types (e.g., "pygments._token.TokenType") dependent
    # on the current pygments version. For that reason, we intentionally omit
    # this hint from the "door_cases_infer_hint" fixture leveraged above.
    assert get_hint_pep_sign_or_none(root_tokens_hint) is HintSignList
