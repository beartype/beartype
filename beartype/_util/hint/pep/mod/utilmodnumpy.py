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
from beartype.vale import IsAttr, IsEqual
# from beartype._util.cache.utilcachecall import callable_cached
from beartype._data.hint.pep.sign.datapepsigns import HintSignNumpyArray
from beartype._util.mod.utilmodimport import import_module_typing_any_attr
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_sign_or_none,
)
from typing import Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ REDUCERS                          }....................
#FIXME: Ideally, this reducer would be memoized. Sadly, the
#"numpy.typing.NDArray" type hint itself fails to memoize. Memoization here
#would just consume all available memory. *sigh*
#The solution is the exact same as for PEP 585 type hints, which similarly fail
#to memoize: forcefully coerce "numpy.typing.NDArray" type hints that have the
#same repr() into the same previously cached "numpy.typing.NDArray" type hint.
#This is particularly vital here, as the process of manually reducing each
#identical "numpy.typing.NDArray" type hint to the same underlying beartype
#validator consumes dramatically more *TIME* than a caching solution.

# @callable_cached
def reduce_hint_numpy_ndarray(
    # Mandatory parameters.
    hint: Any,

    # Optional parameters.
    hint_label: str = 'Annotated',
) -> Any:
    '''
    Beartype validator validating arbitrary objects to be NumPy arrays whose
    **NumPy array data type** (i.e., :class:`numpy.dtype` instance) is equal to
    that subscripting the passed PEP-noncompliant typed NumPy array (e.g.,
    ``numpy.dtype(numpy.float64)`` when passed
    ``numpy.typing.NDArray[numpy.float64]``).

    This getter effectively reduces any PEP-noncompliant third-party typed
    NumPy array to a semantically equivalent PEP-noncompliant first-party
    beartype validator -- which has the substantial merits of already being
    well-supported, well-tested, and well-known to generate optimally efficient
    type-checking by the :func:`beartype.beartype` decorator.

    Technically, beartype could instead explicitly handle typed NumPy arrays
    throughout the codebase. Of course, doing so would yield *no* tangible
    benefits while imposing a considerable maintenance burden.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        PEP-noncompliant typed NumPy array to return the data type of.
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to ``"Annotated"``.

    Raises
    ----------
    :exc:`BeartypeDecorHintNonPepNumPyException`
        If either:

        * The active Python interpreter targets Python < 3.9 and either:

          * The third-party :mod:`typing_extensions` module is unimportable.
          * The third-party :mod:`typing_extensions` module is importable but
            sufficiently old that it fails to declare the
            :attr:`typing_extensions.Annotated` attribute.

        * This hint is *not* a typed NumPy array.
        * This hint is a typed NumPy array but either:

          * *Not* subscripted by exactly two arguments.
          * Subscripted by exactly two arguments but whose second argument is
            neither:

            * A **NumPy data type** (i.e., :class:`numpy.dtype` instance).
            * An object coercible into a NumPy data type by passing to the
              :meth:`numpy.dtype.__init__` method.
    '''

    # Defer heavyweight imports.
    #
    # Note that third-party packages should typically *ONLY* be imported
    # via utility functions raising human-readable exceptions when those
    # packages are either uninstalled or unimportable. In this case,
    # however, NumPy will almost *ALWAYS* be importable. Why? Because this
    # hint was externally instantiated by the user by first importing the
    # "numpy.typing.NDArray" attribute passed to this getter.
    from numpy import dtype, ndarray

    # "typing.Annotated" attribute safely imported from whichever of the
    # "typing" or "typing_extensions" modules declares this attribute if one or
    # more do *OR* raise an exception otherwise.
    #
    # Note that this memoized function is intentionally passed positional
    # rather than keyword arguments for minor efficiency gains.
    typing_annotated = import_module_typing_any_attr(
        'Annotated', BeartypeDecorHintNonPepNumPyException)

    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # If this hint is *NOT* a typed NumPy array, raise an exception.
    if hint_sign is not HintSignNumpyArray:
        raise BeartypeDecorHintNonPepNumPyException(
            f'{hint_label} type hint {repr(hint)} not NumPy array type hint '
            f'(i.e., "numpy.typing.NDArray" instance).'
        )
    # Else, this hint is a typed NumPy array.

    # Objects subscripting this hint if any *OR* the empty tuple otherwise.
    hint_args = get_hint_pep_args(hint)

    # If this hint was *NOT* subscripted by exactly two arguments, this hint is
    # malformed as a typed NumPy array. In this case, raise an exception.
    if len(hint_args) != 2:
        raise BeartypeDecorHintNonPepNumPyException(
            f'{hint_label} NumPy array type hint {repr(hint)} '
            f'not subscripted by exactly two arguments.'
        )
    # Else, this hint was subscripted by exactly two arguments.

    # Data type subhint subscripting this hint. Yes, the "numpy.typing.NDArray"
    # type hint bizarrely encapsulates its data type argument into a private
    # "numpy._DTypeMeta" type subhint. Why? We have absolutely no idea, but we
    # have no say in the matter. NumPy, you're on notice for stupidity.
    hint_dtype_subhint = hint_args[1]

    # Objects subscripting this subhint if any *OR* the empty tuple otherwise.
    hint_dtype_subhint_args = get_hint_pep_args(hint_dtype_subhint)

    # If this hint was *NOT* subscripted by exactly one argument, this subhint
    # is malformed as a data type subhint. In this case, raise an exception.
    if len(hint_dtype_subhint_args) != 1:
        raise BeartypeDecorHintNonPepNumPyException(
            f'{hint_label} NumPy array type hint {repr(hint)} '
            f'data type subhint {repr(hint_dtype_subhint)} '
            f'not subscripted by exactly one argument.'
        )
    # Else, this subhint was subscripted by exactly one argument.

    # Data type-like object subscripting this subhint. Look, just do it.
    hint_dtype_like = hint_dtype_subhint_args[0]

    # Attempt to coerce this possibly non-data type into a proper data type.
    # Note that the dtype.__init__() constructor efficiently maps non-dtype
    # scalar types (e.g., "numpy.float64") to corresponding cached dtypes:
    #     >>> import numpy
    #     >>> i4_dtype = numpy.dtype('>i4')
    #     >>> numpy.dtype(i4_dtype) is numpy.dtype(i4_dtype)
    #     True
    #     >>> numpy.dtype(numpy.float64) is numpy.dtype(numpy.float64)
    #     True
    # Ergo, the call to this constructor here is guaranteed to already
    # effectively be memoized.
    try:
        hint_dtype = dtype(hint_dtype_like)
    # If this object is *NOT* coercible into a data type, raise an exception.
    # This is essential. As of NumPy 1.21.0, "numpy.typing.NDArray" fails to
    # validate its subscripted argument to actually be a data type: e.g.,
    #     >>> from numpy.typing import NDArray
    #     >>> NDArray['wut']
    #     numpy.ndarray[typing.Any, numpy.dtype['wut']]  # <-- you kidding me?
    except Exception as exception:
        raise BeartypeDecorHintNonPepNumPyException(
            f'{hint_label} NumPy array type hint {repr(hint)} '
            f'data type {repr(hint_dtype_like)} invalid '
            f'(i.e., neither data type nor coercible to data type).'
        ) from exception
    # Else, this object is now a proper data type.

    # Equivalent nested beartype validator reduced from this hint.
    hint_validator = IsAttr['dtype', IsEqual[hint_dtype]]   # type: ignore[type-arg,valid-type]

    # Render the machine-readable representation of this validator more
    # succinctly human-readable.
    hint_validator.get_repr = repr(hint)

    # Return this validator annotating the NumPy array type.
    return typing_annotated[ndarray, hint_validator]
