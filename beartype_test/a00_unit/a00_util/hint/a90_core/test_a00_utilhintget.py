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

# ....................{ TESTS                             }....................
#FIXME: Test *ALL* kinds of hints reduced by this getter, including:
#* Typed NumPy arrays (e.g., "numpy.typing.NDArray[numpy.float64]").
def test_get_hint_reduced() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhintget.get_hint_reduced` getter.
    '''

    # Defer heavyweight imports.
    # from beartype.roar import (
    # )
    from beartype.vale import IsEqual
    from beartype._cave._cavefast import NoneType
    from beartype._util.data.hint.pep.sign.datapepsigns import (
        HintSignAnnotated,
    )
    from beartype._util.hint.utilhintget import get_hint_reduced
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype_test.util.mod.pytmodoptional import (
        is_package_numpy_typing_ndarray_supported,
        is_package_typing_extensions,
    )

    # Assert this function preserves a PEP-noncompliant object as is.
    assert get_hint_reduced(int) is int

    # Assert this function reduces "None" to "type(None)".
    assert get_hint_reduced(None) is NoneType

    # If the active Python interpreter targets Python > 3.9 and thus provides
    # the "typing.Annotated" type hint...
    if IS_PYTHON_AT_LEAST_3_9:
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize changes with "typing_extensions" logic below.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Defer version-specific imports.
        from typing import Annotated

        # Assert this function reduces a beartype-agnostic metahint to the
        # lower-level hint it annotates.
        assert get_hint_reduced(Annotated[int, 42]) is int

        # Assert this function preserves a beartype-specific metahint as is.
        leaves_when_laid = Annotated[str, IsEqual['In their noonday dreams.']]
        assert get_hint_reduced(leaves_when_laid) is leaves_when_laid

    # If a reasonably recent version of the third-party "typing_extensions"
    # package (providing the "typing_extensions.Annotated" type hint) is
    # importable...
    if is_package_typing_extensions():
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize changes with "typing" logic above.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Defer version-specific imports.
        from typing_extensions import Annotated

        # Assert this function reduces a beartype-agnostic metahint to the
        # lower-level hint it annotates.
        assert get_hint_reduced(Annotated[int, 42]) is int

        # Assert this function preserves a beartype-specific metahint as is.
        leaves_when_laid = Annotated[str, IsEqual['In their noonday dreams.']]
        assert get_hint_reduced(leaves_when_laid) is leaves_when_laid

    #FIXME: Test all possible edge cases (including failure states) of the
    #reduce_hint_numpy_ndarray() function, please.

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
