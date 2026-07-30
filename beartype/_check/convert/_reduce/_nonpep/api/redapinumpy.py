#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-noncompliant NumPy type hint reducers** (i.e., low-level
callables converting higher-level type hints defined by the third-party
:mod:`numpy` package that do *not* comply with any specific PEP but are
nonetheless shallowly supported by :mod:`beartype` to lower-level type hints
more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Actually validate NumPy array shapes as well. Purely because lazy and
#tired, we currently ignore shape concerns. Bad @beartype is bad. =<

#FIXME: The "beartype.vale"-based approach leveraged below *DOES* technically
#work, but also results in mostly unreadable type-checking violation messages.
#There are many viable alternatives producing readable type-checking violation
#messages. For example, rather than reduce the passed NumPy type hint to a
#beartype validator, consider instead:
#* Reduce the passed NumPy type hint to a new beartype-specific class whose
#  metaclass defines the __instancecheck__(), __instancecheck_str__(), *AND*
#  __subclasscheck__() dunder methods in a reasonably sane and straightforward
#  manner. Note that, if we do decide to go down this road, then the resulting
#  new beartype-specific class could actually serve as the basis for a new
#  public beartype-specific tensor type-checking API.
#* Reduce the passed NumPy type hint to a competing third-party tensor
#  type-checking type hint already produced by one or all of the following
#  third-party Python packages:
#  * "jaxtyping", obviously. \o/
#  * "bearshape", which currently lives at:
#        https://github.com/acecchini/bearshape

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: The top-level of this module should avoid importing from third-party
# optional libraries, both because those libraries cannot be guaranteed to be
# either installed or importable here *AND* because those imports are likely to
# be computationally expensive, particularly for imports transitively importing
# C extensions (e.g., anything from NumPy or SciPy).
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.roar import BeartypeDecorHintNonpepNumpyException
from beartype._check.cls.hint.hintsane import HINT_SANE_IGNORABLE
from beartype._data.typing.datatypingport import Hint
from beartype._util.api.external.utilnumpy import (
    get_numpy_dtype_type_abcs,
    make_numpy_dtype,
)
from beartype._util.hint.pep.utilpepget import get_hint_pep_childs
from beartype._util.hint.pep.utilpeptest import is_hint_pep
from beartype._util.utilobjtest import is_object_hashable
from typing import Annotated

# ....................{ REDUCERS                           }....................
def reduce_hint_numpy_ndarray(
    hint: Hint, exception_prefix: str, **kwargs) -> Hint:
    '''
    Reduce the passed **PEP-noncompliant typed NumPy array** (i.e.,
    subscription of the third-party :attr:`numpy.typing.NDArray` type hint
    factory) to the equivalent PEP-compliant beartype validator validating
    arbitrary objects be instances of that array type -- which has the
    substantial merit of already being well-supported, well-tested, and
    well-known to generate optimally efficient type-checking by the
    :func:`beartype.beartype` decorator.

    Technically, beartype could instead explicitly handle typed NumPy arrays
    throughout the codebase. Of course, doing so would yield *no* tangible
    benefits while imposing a considerable maintenance burden.

    This reducer is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), due to accepting one or more non-memoizable
    parameters (e.g., ``hint_parent_sane``).

    Parameters
    ----------
    hint : Hint
        PEP-noncompliant typed NumPy array to be reduced.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed keyword-only parameters are passed as is to the
    :func:`beartype._check.convert._reduce.redmain.reduce_hint_child` reducer
    recursively called by this reducer.

    Returns
    -------
    Hint
        This PEP-noncompliant typed NumPy array reduced to a PEP-compliant type
        hint supported by :mod:`beartype`.

    Raises
    ------
    BeartypeDecorHintNonpepNumpyException
        If this hint is a typed NumPy array but either:

        * *Not* subscripted by exactly two arguments.
        * Subscripted by exactly two arguments but whose second argument is
          neither:

          * A **NumPy data type** (i.e., :class:`numpy.dtype` instance).
          * An object coercible into a NumPy data type by passing to the
            :meth:`numpy.dtype.__init__` method.
    '''
    # print(f'[reduce_hint_numpy_ndarray] hint_parent_sane: {hint_parent_sane}')

    # ..................{ IMPORTS                            }..................
    # Defer heavyweight imports until *AFTER* validating this hint to be a typed
    # NumPy array. Why? Because these imports are *ONLY* safely importable if
    # this hint is a typed NumPy array. Why? Because instantiating this hint
    # required these imports. QED.
    #
    # Note that third-party packages should typically *ONLY* be imported via
    # utility functions raising human-readable exceptions when those packages
    # are either uninstalled or unimportable. In this case, however, NumPy will
    # almost *ALWAYS* be importable. Why? Because this hint was externally
    # instantiated by the user who first imported the "numpy.typing.NDArray"
    # type hint factory passed to this getter.
    from beartype._check.convert._reduce.redmain import reduce_hint_child
    from beartype.vale import (
        IsAttr,
        IsEqual,
        IsSubclass,
    )
    from numpy import ndarray  # pyright: ignore
    from numpy.typing import NDArray  # type: ignore[attr-defined]

    #FIXME: Consider submitting an upstream issue about this. We don't
    #particularly feel like arguing tonight, because that's a lonely hill.

    # If this hint is the unsubscripted "NDArray" type hint, this hint
    # permissively matches *ALL* NumPy arrays rather than strictly matching
    # *ONLY* appropriately typed NumPy arrays. In this case, reduce this hint
    # to the untyped "numpy.ndarray" class.
    #
    # Note the similar test matching the subscripted "NDArray[Any]" hint below.
    # Moreover, note this test *CANNOT* be performed elsewhere (e.g., by
    # adding "HintSignNumpyArray" to the "HINT_SIGNS_ORIGIN_ISINSTANCEABLE"
    # frozen set of all signs whose unsubscripted type hint factories are
    # shallowly type-checkable). Why? Because the "NDArray" type hint factory
    # violates type hinting standards. Specifically, this factory implicitly
    # subscripts *AND* parametrizes itself with the "numpy.ScalarType" type
    # variable bounded above by the "numpy.generic" abstract base class for
    # NumPy scalars.
    #
    # We have *NO* idea why NumPy does this. This implicit behaviour is
    # semantically lossy rather than lossless and thus arguably constitutes an
    # upstream bug. Why? Because this behaviour violates:
    # * The NumPy API. The "NDArray" type hint factory is subscriptable by more
    #   than merely NumPy scalar types. Ergo, "NDArray" is semantically
    #   inaccurate!
    # * PEP 484, which explicitly standardizes an equivalence between
    #   unsubscripted type hint factories and the same factories subscripted by
    #   the "typing.Any" singleton. However, "NDArray" is *MUCH* semantically
    #   narrower than and thus *NOT* equivalent to "NDArray[Any]"!
    #
    # Of course, upstream is unlikely to see it that way. We're *NOT* dying on
    # an argumentative hill about semantics. Upstream makes the rules. Do it.
    if hint is NDArray:
        return ndarray
    # Else, this hint is *NOT* the unsubscripted "NDArray" type hint.

    # ..................{ LOCALS                             }..................
    # Frozen set of all NumPy scalar data type abstract base classes (ABCs).
    NUMPY_DTYPE_TYPE_ABCS = get_numpy_dtype_type_abcs()

    # ..................{ LOCALS ~ childs                    }..................
    # Child hints subscripting this hint if any *OR* the empty tuple otherwise.
    hint_childs = get_hint_pep_childs(hint)

    # If this hint was *NOT* subscripted by exactly two child hints, this hint
    # is malformed as a typed NumPy array. In this case, raise an exception.
    if len(hint_childs) != 2:
        raise BeartypeDecorHintNonpepNumpyException(
            f'{exception_prefix}'
            f'typed NumPy array {repr(hint)} '
            f'not subscripted by exactly two child type hints '
            f'(i.e., {len(hint_childs)} != 2).'
        )
    # Else, this hint was subscripted by exactly two child hints.

    # Shape (i.e., NumPy-specific dimensionality) and dtype (i.e.,
    # NumPy-specific data type) child hints subscripting this hint.
    hint_child_shape, hint_child_dtype = hint_childs

    # ..................{ LOCALS ~ childs : dtype            }..................
    # Child child hints subscripting this dtype child hint if any *OR* the empty
    # tuple otherwise.
    hint_child_dtype_childs = get_hint_pep_childs(hint_child_dtype)

    # If this dtype child hint was *NOT* subscripted by exactly one child child
    # hint, this dtype child hint is malformed. In this case, raise an
    # exception.
    if len(hint_child_dtype_childs) != 1:
        raise BeartypeDecorHintNonpepNumpyException(
            f'{exception_prefix}'
            f'typed NumPy array {repr(hint)} '
            f'data type subhint {repr(hint_child_dtype)} '
            f'not subscripted by exactly one argument.'
        )
    # Else, this dtype child hint was correctly subscripted by exactly one child
    # child hint.

    # Dtype-like object (i.e., either dtype *OR* non-dtype object safely
    # coercible into a dtype by being passed to the numpy.dtype() constructor)
    # subscripting this dtype child hint.
    #
    # If the passed hint was originally directly defined via:
    # * The higher-level "numpy.typing.NDArray[...]" type hint factory, this
    #   object is guaranteed to be the PEP 484-compliant NumPy-specific type
    #   variable "numpy.typing.ScalarT". Why? Because NumPy >= 2.5.0 defines
    #   this factory to be a PEP 695-compliant type alias parametrized by that
    #   type variable: e.g.,
    #       type NDArray[ScalarT] = np.ndarray[_AnyShape, np.dtype[ScalarT]]
    #   Clearly, a type variable *CANNOT* be passed to the numpy.dtype()
    #   constructor and is thus *NOT* a valid dtype-like object. Type variables
    #   are purely runtime QA constructs of interest only to static and runtime
    #   type-checkers. Ergo, this type variable *MUST* be replaced by the
    #   corresponding concrete child hint directly subscripting the passed hint.
    #   How? By passing this type variable to the reduce_hint_child() function
    #   called below *BEFORE* inspecting this object for any reason.
    # * The lower-level "numpy.ndarray[...]" type hint factory, this object
    #   *COULD* be (and usually is) a valid dtype-like object. If it is, we
    #   maximize safety by avoiding passing this object to the
    #   reduce_hint_child() function for safety. Else, we do.
    #
    # Beartype: "Just QA it."
    hint_dtypelike = hint_child_dtype_childs[0]

    # If this object is actually a PEP-compliant child hint, this object is
    # currently *NOT* a valid dtype-like. In this case...
    if is_hint_pep(hint_dtypelike):
        # Metadata encapsulating the sanification of this child hint.
        # print(f'Reducing union {hint} insane child {hint_child_insane} with {kwargs}...')
        hint_dtypelike_sane = reduce_hint_child(
            hint=hint_dtypelike,
            # Request that this reducer return any PEP-noncompliant child hint
            # (typically, a PEP-noncompliant NumPy-specific dtype-like object)
            # to which this PEP-compliant child hint reduces as is *WITHOUT*
            # raising the usual "BeartypeDecorHintNonpepException" exception.
            is_hint_nonpep_irreducible=True,
            **kwargs,
        )

        # If this child hint reduces to the ignorable metadata singleton (e.g.,
        # if this child hint is "typing.Any"), this hint permissively matches
        # *ALL* NumPy arrays rather than strictly matching *ONLY* appropriately
        # typed NumPy arrays. In this case, reduce this hint to the untyped
        # "numpy.ndarray" class.
        #
        # Note the similar test matching the unsubscripted "NDArray" hint above.
        if hint_dtypelike_sane is HINT_SANE_IGNORABLE:
            return ndarray  # pyright: ignore
        # Else, this child hint is unignorable.

        # Dtype-like object sanified from this child hint. For example:
        # * If this hint is the PEP 695-compliant "numpy.typing.NDArray[...]"
        #   type alias originally parametrized (in the NumPy codebase) by the
        #   PEP 484-compliant NumPy-specific type variable
        #   "numpy.typing.ScalarT" and since subscripted (in the external
        #   non-NumPy codebase being runtime type-checked by beartype) by a
        #   concrete child hint, this assignment replaces that otherwise
        #   unusable type variable by that directly usable concrete child hint.
        hint_dtypelike = hint_dtypelike_sane.hint
    # Else, this object is *NOT* actually a PEP-compliant child hint. In this
    # case, this object is assumed to already be a valid dtype-like.
    #
    # In either case, this object *SHOULD* now be a valid dtype-like.

    # ..................{ REDUCTION                          }..................
    # Equivalent nested beartype validator reduced from this hint.
    hint_validator = None  # type: ignore[assignment]

    # If...
    if (
        # This dtype-like is hashable *AND*...
        is_object_hashable(hint_dtypelike) and
        # This dtype-like is a scalar data type abstract base class (ABC)...
        hint_dtypelike in NUMPY_DTYPE_TYPE_ABCS
    ):
        # Then avoid attempting to coerce this possibly non-dtype into a proper
        # dtype. Although NumPy previously silently coerced these ABCs into
        # dtypes (e.g., from "numpy.floating" to "numpy.float64"), recent
        # versions of NumPy now emit non-fatal deprecation warnings on doing so
        # and will presumably raise fatal exceptions in the near future:
        #     >>> import numpy as np
        #     >>> np.dtype(np.floating)
        #     DeprecationWarning: Converting `np.inexact` or `np.floating` to a
        #     dtype is deprecated. The current result is `float64` which is not
        #     strictly correct.
        #
        # Instead, we follow mypy's lead. Presumably defined somewhere in the
        # incredibly complex innards of NumPy's mypy plugin (which we admittedly
        # failed to grep despite ~~wasting~~ "investing" several hours in doing
        # so), mypy treats subscriptions of the "numpy.typing.NDArray" type hint
        # factory by one of these ABCs (rather than either a scalar or proper
        # dtype) as a type inheritance (rather than object equality) relation.
        # Since this is sensible, we do too.

        # Equivalent nested beartype validator reduced from this hint.
        hint_validator = (
            IsAttr['dtype', IsAttr['type', IsSubclass[hint_dtypelike]]])
    # Else, this dtype-like is either unhashable *OR* not such an ABC. In this
    # case...
    else:
        # Proper dtype coerced from this possibly non-dtype.
        hint_dtype = make_numpy_dtype(
            dtype=hint_dtypelike,
            exception_cls=BeartypeDecorHintNonpepNumpyException,
            exception_prefix=exception_prefix,
        )

        # Equivalent nested beartype validator reduced from this hint.
        hint_validator = IsAttr['dtype', IsEqual[hint_dtype]]

    # Replace the usually less readable representation of this validator with
    # the usually more readable representation of this hint (e.g.,
    # "numpy.ndarray[typing.Any, numpy.float64]").
    hint_validator.get_repr = repr(hint)

    # Return this validator annotating the NumPy array type.
    return Annotated[ndarray, hint_validator]  # type: ignore[return-value]  # pyright: ignore
