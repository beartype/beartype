#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-noncompliant NumPy type hint** (i.e., type hint defined by
the third-party :mod:`numpy` package) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: The top-level of this module should avoid importing from third-party
# optional libraries, both because those libraries cannot be guaranteed to be
# either installed or importable here *AND* because those imports are likely to
# be computationally expensive, particularly for imports transitively importing
# C extensions (e.g., anything from NumPy or SciPy).
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.roar import BeartypeDecorHintNonPepNumPyException
from beartype._util.data.hint.pep.sign.datapepsigns import HintSignNumpyArray
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from typing import Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ VALIDATORS                        }....................
#FIXME: Implement us up, please. Note that doing so will require
#differentiating between:
#* "numpy.dtype.type" objects like "np.float64", which actually isn't a dtype
#  even though NumPy externally pretends it is. Gracias, NumPy.
#* "numpy.dtype" objects like "np.dtype('>i4')", which actually is a dtype even
#  though nobody has ever seen one of those in real life.
#FIXME: Unit test us up, please.

# Note this getter's return annotation is intentionally deferred as a forward
# reference to avoid
def get_hint_numpy_ndarray_dtype(hint: Any) -> 'numpy.dtype':  # type: ignore[name-defined]
    '''
    **NumPy array data type** (i.e., :class:`numpy.dtype` instance)
    subscripting the passed PEP-noncompliant typed NumPy array (e.g.,
    ``numpy.dtype(numpy.float64)`` when passed
    ``numpy.typing.NDArray[numpy.float64]``).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        PEP-noncompliant typed NumPy array to return the data type of.

    Raises
    ----------
    :exc:`BeartypeDecorHintNonPepNumPyException`
        If either:

        * This hint is *not* a typed NumPy array.
    '''

    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # If this hint is *NOT* a typed NumPy array, raise an exception.
    if hint_sign is not HintSignNumpyArray:
        raise BeartypeDecorHintNonPepNumPyException(
            f'Type hint {repr(hint)} not typed NumPy array.')
    # Else, this hint is a typed NumPy array.

    #FIXME: Clearly, even this is unsafe. Ensure this hint is actually
    #subscripted and of length > 2, please. Assume *NOTHING* here, because this
    #is a third-party API that could change at anyone's whim.

    # Data type *OR* data type type subscripting this hint.
    hint_dtype_or_dtype_type = hint.__args__[1]
