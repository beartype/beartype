#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint converter** (i.e., callables converting
type hints from one format into another, either permanently or temporarily
*and* either losslessly or in a lossy manner) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._cave._cavefast import NotImplementedType, NoneType
from beartype._data.func.datafunc import METHOD_NAMES_BINARY_DUNDER
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAnnotated,
    HintSignNewType,
    HintSignNumpyArray,
    HintSignType,
    HintSignTypeVar,
    HintSignTypedDict,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep484.utilpep484union import (
    make_hint_pep484_union)
from beartype._util.hint.pep.proposal.utilpep544 import (
    reduce_hint_pep484_generic_io_to_pep544_protocol,
    is_hint_pep484_generic_io,
)
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from collections.abc import Callable, Mapping
from typing import Any, Union

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ PRIVATE ~ mappings                }....................
#FIXME: Uncomment when adding PEP 585 coercion caching to coerce_hint() below.
#FIXME: This is non-thread-safe. Declare a new thread-safe dictionary class
#"beartype._util.cache.map.utilmapbig.CacheUnboundedStrong".
# _HINT_REPR_TO_HINT: Dict[str, Any] = {}
# '''
# **Type hint cache** (i.e., singleton dictionary mapping from the
# machine-readable representations of all non-self-cached type hints to those
# hints).**
#
# This dictionary caches:
#
# * :pep:`585`-compliant type hints, which do *not* cache themselves.
# * :pep:`563`-compliant **deferred type hints** (i.e., type hints persisted as
#   evaluatable strings rather than actual type hints), enabled if the active
#   Python interpreter targets either:
#
#   * Python 3.7.0 *and* the module declaring this callable explicitly enables
#     :pep:`563` support with a leading dunder importation of the form ``from
#     __future__ import annotations``.
#   * Python 4.0.0, where `PEP 563`_ is expected to be mandatory.
#
# This dictionary does *not* cache:
#
# * Type hints declared by the :mod:`typing` module, which implicitly cache
#   themselves on subscription thanks to inscrutable metaclass magic.
#
# Implementation
# --------------
# This dictionary is intentionally designed as a naive dictionary rather than
# robust LRU cache, for the same reasons that callables accepting hints are
# memoized by the :func:`beartype._util.cache.utilcachecall.callable_cached`
# rather than the :func:`functools.lru_cache` decorator. Why? Because:
#
# * The number of different type hints instantiated across even worst-case
#   codebases is negligible in comparison to the space consumed by those hints.
# * The :attr:`sys.modules` dictionary persists strong references to all
#   callables declared by previously imported modules. In turn, the
#   ``func.__annotations__`` dunder dictionary of each such callable persists
#   strong references to all type hints annotating that callable. In turn, these
#   two statements imply that type hints are *never* garbage collected but
#   instead persisted for the lifetime of the active Python process. Ergo,
#   temporarily caching hints in an LRU cache is pointless, as there are *no*
#   space savings in dropping stale references to unused hints.
# '''

# ....................{ COERCERS                          }....................
def coerce_hint(
    hint: object,
    func: Callable,
    pith_name: str,
    exception_prefix: str,
) -> Any:
    '''
    PEP-compliant type hint coerced (i.e., converted) from the passed possibly
    PEP-noncompliant type hint annotating the parameter or return value with
    the passed name of the passed callable if this hint is coercible *or* this
    hint as is otherwise (i.e., if this hint is irreducible).

    Specifically, if the passed hint is:

    * A **PEP-compliant uncached type hint** (i.e., PEP-compliant type hint
      *not* already internally cached by its parent class or module, notably
      including all :pep:`585`-compliant type hints), this function:

      * If this hint has already been passed to a prior call of this function,
        returns the semantically equivalent PEP-compliant type hint having the
        same machine-readable representation as this hint cached by that call.
        Doing so deduplicates this hint, minimizing memory space consumption
        across the lifetime of the active Python process.
      * Else, internally caches this hint with a thread-safe global cache and
        returns this hint as is.

    * A **PEP-noncompliant tuple union** (i.e., tuple of one or more standard
      classes and forward references to standard classes), this function:

      * Coerces this tuple union into the equivalent :pep:`484`-compliant
        union.
      * Replaces this tuple union in the ``__annotations__`` dunder tuple of
        this callable with this :pep:`484`-compliant union.
      * Returns this :pep:`484`-compliant union.

    * Already self-cached, this hint is already PEP-compliant by definition. In
      this case, this function preserves and returns this hint as is.

    This function is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Since the hint returned by this
    function conditionally depends upon the passed callable, memoizing this
    function would consume space needlessly with *no* useful benefit.

    Parameters
    ----------
    hint : object
        Type hint to be possible coerced.
    func : Callable
        Callable annotated by this hint.
    pith_name : str
        Either:

        * If this hint annotates a parameter of that callable, the name of that
          parameter.
        * If this hint annotates the return of that callable, ``"return"``.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    Any
        Either:

        * If the passed possibly PEP-noncompliant type hint is coercible, a
          PEP-compliant type hint coerced from this hint.
        * Else, this hint as is unmodified.
    '''

    # ..................{ MYPY                              }..................
    # If...
    if (
        # This hint annotates the return for the decorated callable *AND*...
        pith_name == 'return' and
        # The decorated callable is a binary dunder method (e.g., __eq__())...
        func.__name__ in METHOD_NAMES_BINARY_DUNDER
    ):
        # Expand this hint to accept both this hint *AND* the "NotImplemented"
        # singleton as valid returns from this method. Why? Because this
        # expansion has been codified by mypy and is thus a de-facto typing
        # standard, albeit one currently lacking formal PEP standardization.
        #
        # Consider this representative binary dunder method:
        #     class MuhClass:
        #         @beartype
        #         def __eq__(self, other: object) -> bool:
        #             if isinstance(other, TheCloud):
        #                 return self is other
        #             return NotImplemented
        #
        # Technically, that method *COULD* be retyped to return:
        #         def __eq__(self, other: object) -> Union[
        #             bool, type(NotImplemented)]:
        #
        # Pragmatically, mypy and other static type checkers do *NOT* currently
        # support the type() builtin in a sane manner and thus raise errors
        # given the otherwise valid logic above. This means that the following
        # equivalent approach also yields the same errors:
        #     NotImplementedType = type(NotImplemented)
        #     class MuhClass:
        #         @beartype
        #         def __eq__(self, other: object) -> Union[
        #             bool, NotImplementedType]:
        #             if isinstance(other, TheCloud):
        #                 return self is other
        #             return NotImplemented
        #
        # Of course, the latter approach can be manually rectified by
        # explicitly typing that type as "Any": e.g.,
        #     NotImplementedType: Any = type(NotImplemented)
        #
        # Of course, expecting users to be aware of these ludicrous sorts of
        # mypy idiosyncrasies merely to annotate an otherwise normal binary
        # dunder method is one expectation too far.
        #
        # Ideally, official CPython developers would resolve this by declaring
        # a new "types.NotImplementedType" type global resembling the existing
        # "types.NoneType" type global. As that has yet to happen, mypy has
        # instead taken the surprisingly sensible course of silently ignoring
        # this edge case by effectively performing the same type expansion as
        # performed here. *applause*
        hint = Union[hint, NotImplementedType]
    # Else, this hint is *NOT* the mypy-compliant "NotImplemented" singleton.
    #
    # ..................{ NON-PEP                           }..................
    # If this hint is a PEP-noncompliant tuple union, coerce this union into
    # the equivalent PEP-compliant union subscripted by the same child hints.
    # By definition, PEP-compliant unions are a superset of PEP-noncompliant
    # tuple unions and thus accept all child hints accepted by the latter.
    elif isinstance(hint, tuple):
        hint = make_hint_pep484_union(hint)
    # Else, this hint is *NOT* a PEP-noncompliant tuple union.

    # Return this possibly coerced hint.
    return hint

# ....................{ REDUCERS                          }....................
@callable_cached
def reduce_hint(
    # Mandatory parameters.
    hint: Any,

    # Optional parameters.
    exception_prefix: str = '',
) -> Any:
    '''
    Lower-level type hint reduced (i.e., converted) from the passed
    higher-level type hint if this hint is reducible *or* this hint as is
    otherwise (i.e., if this hint is irreducible).

    Specifically, if the passed hint is:

    * *Not* PEP-compliant, this hint is returned as is unmodified.
    * PEP 593-compliant (i.e., :class:`typing.Annotated`) but beartype-agnostic
      (i.e., its second argument is *not* an instance of the
      :class:`beartype.vale._valevale.BeartypeValidator` class produced by
      subscripting the :class:`beartype.vale.Is` class), this hint is reduced
      to the first argument subscripting this hint. Doing so ignores *all*
      irrelevant annotations on this hint (e.g., reducing
      ``typing.Annotated[str, 50, False]`` to simply ``str``).

    This function is memoized for efficiency.

    Parameters
    ----------
    hint : Any
        Type hint to be possibly reduced.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    Any
        Either:

        * If the passed higher-level type hint is reducible, a lower-level type
          hint reduced (i.e., converted, extracted) from this hint.
        * Else, this hint as is unmodified.

    Raises
    ----------
    :exc:`BeartypeDecorHintNonpepNumpyException`
        See the
        :func:`beartype._util.hint.pep.mod.utilmodnumpy.reduce_hint_numpy_ndarray`
        function for further details.
    '''

    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # This reduction is intentionally implemented as a linear series of tests,
    # ordered in descending likelihood of a match for efficiency. While
    # alternatives (that are more readily readable and maintainable) do exist,
    # these alternatives all appear to be substantially less efficient.
    #
    # ..................{ NON-PEP                           }..................
    # If this hint is unidentifiable, return this hint as is unmodified.
    #
    # Since this includes *ALL* isinstanceable classes (including both
    # user-defined classes and builtin types), this is *ALWAYS* detected first.
    if hint_sign is None:
        return hint
    # ..................{ PEP 484 ~ none                    }..................
    # If this is the PEP 484-compliant "None" singleton, reduce this hint to
    # the type of that singleton. While *NOT* explicitly defined by the
    # "typing" module, PEP 484 explicitly supports this singleton:
    #     When used in a type hint, the expression None is considered
    #     equivalent to type(None).
    #
    # The "None" singleton is used to type callables lacking an explicit
    # "return" statement and thus absurdly common. Ergo, detect this early.
    elif hint is None:
        hint = NoneType
    # ..................{ PEP 484 ~ typevar                 }..................
    #FIXME: Remove this *AFTER* deeply type-checking type variables.
    # If this is a PEP 484-compliant type variable...
    #
    # Type variables are excruciatingly common and thus detected very early.
    elif hint_sign is HintSignTypeVar:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484.utilpep484typevar import (
            get_hint_pep484_typevar_bound_or_none)

        # PEP-compliant type hint synthesized from all bounded constraints
        # parametrizing this type variable if any *OR* "None" otherwise.
        hint_bound = get_hint_pep484_typevar_bound_or_none(hint)
        # print(f'Reducing PEP 484 type variable {repr(hint)} to {repr(hint_bound)}...')

        # If this type variable was parametrized by one or more bounded
        # constraints, reduce this hint to these constraints.
        if hint_bound is not None:
            # print(f'Reducing non-beartype PEP 593 type hint {repr(hint)}...')
            hint = hint_bound
        # Else, this type variable was parametrized by no bounded constraints.
    # ..................{ PEP 593                           }..................
    # If this hint is a PEP 593-compliant metahint...
    #
    # Since metahints form the core backbone of our beartype-specific data
    # validation API, metahints are extremely common and thus detected early.
    elif hint_sign is HintSignAnnotated:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.utilpep593 import (
            get_hint_pep593_metahint,
            is_hint_pep593_beartype,
        )

        # If this metahint is beartype-agnostic and thus irrelevant to us,
        # ignore all annotations on this hint by reducing this hint to the
        # lower-level hint it annotates.
        if not is_hint_pep593_beartype(hint):
            # print(f'Reducing non-beartype PEP 593 type hint {repr(hint)}...')
            hint = get_hint_pep593_metahint(hint)
        # Else, this metahint is beartype-specific. In this case, preserve
        # this hint as is for subsequent handling elsewhere.
    # ..................{ NON-PEP ~ numpy                   }..................
    # If this hint is a PEP-noncompliant typed NumPy array (e.g.,
    # "numpy.typing.NDArray[np.float64]"), reduce this hint to the equivalent
    # well-supported beartype validator.
    #
    # Typed NumPy arrays are increasingly common and thus detected early.
    elif hint_sign is HintSignNumpyArray:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.mod.utilmodnumpy import (
            reduce_hint_numpy_ndarray)
        hint = reduce_hint_numpy_ndarray(
            hint=hint, exception_prefix=exception_prefix)
    # ..................{ PEP (484|585) ~ subclass          }..................
    # If this hint is a PEP 484-compliant subclass type hint subscripted by an
    # ignorable child type hint (e.g., "object", "typing.Any"), silently ignore
    # this argument by reducing this hint to the "type" superclass. Although
    # this logic could also be performed elsewhere, doing so here simplifies
    # matters dramatically. Note that this reduction *CANNOT* be performed by
    # the is_hint_ignorable() tester, as subclass type hints subscripted by
    # ignorable child type hints are *NOT* ignorable; they're simply safely
    # reducible to the "type" superclass.
    #
    # Subclass type hints are reasonably uncommon and thus detected late.
    elif hint_sign is HintSignType:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484585.utilpep484585type import (
            reduce_hint_pep484585_subclass_superclass_if_ignorable)
        hint = reduce_hint_pep484585_subclass_superclass_if_ignorable(
            hint=hint, exception_prefix=exception_prefix)
    # ..................{ PEP 589                           }..................
    #FIXME: Remove *AFTER* deeply type-checking typed dictionaries. For now,
    #shallowly type-checking such hints by reduction to untyped dictionaries
    #remains the sanest temporary work-around.
    #FIXME: The PEP 589 edict that "any TypedDict type is consistent with
    #"Mapping[str, object]" suggests that we should trivially reduce this hint
    #to "Mapping[str, object]" rather than merely "Mapping" *AFTER* we deeply
    #type-check mappings. Doing so will get us slightly deeper type-checking of
    #typed dictionaries, effectively for free. Note that:
    #* Care should be taken to ensure that the "Mapping" factory appropriate
    #  for the active Python interpreter is used. PEP 585 gonna PEP 585.
    #* We should cache "Mapping[str, object]" to a private global above rather
    #  than return a new "Mapping[str, object]" type hint on each call. Right?

    # If this hint is a PEP 589-compliant typed dictionary (i.e.,
    # "typing.TypedDict" or "typing_extensions.TypedDict" subclass), silently
    # ignore all child type hints annotating this dictionary by reducing this
    # hint to the "Mapping" superclass. Yes, "Mapping" rather than "dict". By
    # PEP 589 edict:
    #     First, any TypedDict type is consistent with Mapping[str, object].
    #
    # Typed dictionaries are largely discouraged in the typing community, due
    # to their non-standard semantics and syntax. Ergo, typed dictionaries are
    # reasonably uncommon and thus detected late.
    elif hint_sign is HintSignTypedDict:
        return Mapping
    # ..................{ PEP 484 ~ new type                }..................
    # If this hint is a PEP 484-compliant new type, reduce this hint to the
    # user-defined class aliased by this hint. Although this logic could also
    # be performed elsewhere, doing so here simplifies matters.
    #
    # New type hints are functionally useless for most meaningful purposes and
    # thus fairly rare in the wild. Ergo, detect these late.
    elif hint_sign is HintSignNewType:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484.utilpep484newtype import (
            get_hint_pep484_newtype_class)
        hint = get_hint_pep484_newtype_class(hint)
    # ..................{ PEP 484 ~ io                      }..................
    # If this hint is a PEP 484-compliant IO generic base class *AND* the
    # active Python interpreter targets Python >= 3.8 and thus supports PEP
    # 544-compliant protocols, reduce this functionally useless hint to the
    # corresponding functionally useful beartype-specific PEP 544-compliant
    # protocol implementing this hint.
    #
    # IO generic base classes are extremely rare and thus detected even later.
    #
    # Note that PEP 484-compliant IO generic base classes are technically
    # usable under Python < 3.8 (e.g., by explicitly subclassing those classes
    # from third-party classes). Ergo, we can neither safely emit warnings nor
    # raise exceptions on visiting these classes under *ANY* Python version.
    elif is_hint_pep484_generic_io(hint):
        hint = reduce_hint_pep484_generic_io_to_pep544_protocol(hint)

    # Return this possibly reduced hint.
    return hint
