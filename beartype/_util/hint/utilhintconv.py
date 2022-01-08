#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint converter** (i.e., callables converting
type hints from one format into another, either permanently or temporarily
*and* either losslessly or in a lossy manner) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: coerce_hint() should also rewrite unhashable hints to be hashable *IF
#FEASIBLE.* This isn't always feasible, of course (e.g., "Annotated[[]]",
#"Literal[[]]"). The one notable place where this *IS* feasible is with PEP
#585-compliant type hints subscripted by unhashable rather than hashable
#iterables, which can *ALWAYS* be safely rewritten to be hashable (e.g.,
#coercing "callable[[], None]" to "callable[(), None]").

#FIXME: coerce_hint() should also coerce PEP 544-compatible protocols *NOT*
#decorated by @typing.runtime_checkable to be decorated by that decorator, as
#such protocols are unusable at runtime. Yes, we should always try something
#*REALLY* sneaky and clever.
#
#Specifically, rather than accept "typing" nonsense verbatim, we could instead:
#* Detect PEP 544-compatible protocol type hints *NOT* decorated by
#  @typing.runtime_checkable. The existing is_type_isinstanceable() tester now
#  detects whether arbitrary classes are isinstanceable, so just call that.
#* Emit a non-fatal warning advising the end user to resolve this on their end.
#* Meanwhile, beartype can simply:
#  * Dynamically fabricate a new PEP 544-compatible protocol decorated by
#    @typing.runtime_checkable using the body of the undecorated user-defined
#    protocol as its base. Indeed, simply subclassing a new subclass decorated
#    by @typing.runtime_checkable from the undecorated user-defined protocol as
#    its base with a noop body of "pass" should suffice.
#  * Replacing all instances of the undecorated user-defined protocol with that
#    decorated beartype-defined protocol in annotations. Note this would
#    strongly benefit from some form of memoization or caching. Since this edge
#    case should be fairly rare, even a dictionary would probably be overkill.
#    Just implementing something resembling the following memoized getter
#    in the "utilpep544" submodule would probably suffice:
#        @callable_cached
#        def get_pep544_protocol_checkable_from_protocol_uncheckable(
#            protocol_uncheckable: object) -> Protocol:
#            ...
#
#Checkmate, "typing". Checkmate.

# ....................{ IMPORTS                           }....................
from beartype._cave._cavefast import NotImplementedType, NoneType
from beartype._data.func.datafunc import METHOD_NAMES_BINARY_DUNDER
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAnnotated,
    HintSignNewType,
    HintSignNumpyArray,
    HintSignDataclassInitVar,
    HintSignType,
    HintSignTypeVar,
    HintSignTypedDict,
)
from beartype._util.cache.map.utilmapbig import CacheUnboundedStrong
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep484.utilpep484union import (
    make_hint_pep484_union)
from beartype._util.hint.pep.proposal.utilpep544 import (
    is_hint_pep484_generic_io,
    reduce_hint_pep484_generic_io_to_pep544_protocol,
)
from beartype._util.hint.pep.proposal.utilpep557 import (
    get_hint_pep557_initvar_arg)
from beartype._util.hint.pep.proposal.utilpep585 import is_hint_pep585_builtin
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from beartype._util.hint.utilhinttest import die_unless_hint
from collections.abc import Callable, Mapping
from typing import Any, Union

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ PRIVATE ~ mappings                }....................
_HINT_REPR_TO_HINT = CacheUnboundedStrong()
'''
**Type hint cache** (i.e., thread-safe cache mapping from the machine-readable
representations of all non-self-cached type hints to those hints).**

This cache caches:

* :pep:`585`-compliant type hints, which do *not* cache themselves.

This cache does *not* cache:

* Type hints declared by the :mod:`typing` module, which implicitly cache
  themselves on subscription thanks to inscrutable metaclass magic.
* :pep:`563`-compliant **deferred type hints** (i.e., type hints persisted as
  evaluable strings rather than actual type hints). Ideally, this cache would
  cache the evaluations of *all* deferred type hints. Sadly, doing so is
  infeasible in the general case due to global and local namespace lookups
  (e.g., ``Dict[str, int]`` only means what you think it means if an
  importation resembling ``from typing import Dict`` preceded that type hint).

Implementation
--------------
This dictionary is intentionally designed as a naive dictionary rather than
robust LRU cache, for the same reasons that callables accepting hints are
memoized by the :func:`beartype._util.cache.utilcachecall.callable_cached`
rather than the :func:`functools.lru_cache` decorator. Why? Because:

* The number of different type hints instantiated across even worst-case
  codebases is negligible in comparison to the space consumed by those hints.
* The :attr:`sys.modules` dictionary persists strong references to all
  callables declared by previously imported modules. In turn, the
  ``func.__annotations__`` dunder dictionary of each such callable persists
  strong references to all type hints annotating that callable. In turn, these
  two statements imply that type hints are *never* garbage collected but
  instead persisted for the lifetime of the active Python process. Ergo,
  temporarily caching hints in an LRU cache is pointless, as there are *no*
  space savings in dropping stale references to unused hints.
'''

# ....................{ SANIFIERS                         }....................
#FIXME: Unit test us up, please.
#FIXME: Revise docstring in accordance with recent dramatic improvements.
def sanify_hint_root(
    hint: object,
    func: Callable,
    pith_name: str,
    exception_prefix: str,
) -> object:
    '''
    PEP-compliant type hint sanified (i.e., sanitized) from the passed **root
    type hint** (i.e., possibly PEP-noncompliant type hint annotating the
    parameter or return with the passed name of the passed callable) if this
    hint is reducible *or* this hint as is otherwise (i.e., if this hint is
    irreducible).

    Specifically, this function:

    * If this hint is a **PEP-noncompliant tuple union** (i.e., tuple of one or
      more standard classes and forward references to standard classes):

      * Coerces this tuple union into the equivalent :pep:`484`-compliant
        union.
      * Replaces this tuple union in the ``__annotations__`` dunder tuple of
        this callable with this :pep:`484`-compliant union.
      * Returns this :pep:`484`-compliant union.

    * Else if this hint is already PEP-compliant, preserves and returns this
      hint unmodified as is.
    * Else (i.e., if this hint is neither PEP-compliant nor -noncompliant and
      thus invalid as a type hint), raise an exception.

    Caveats
    ----------
    This function *cannot* be meaningfully memoized, since the passed type hint
    is *not* guaranteed to be cached somewhere. Only functions passed cached
    type hints can be meaningfully memoized. Even if this function *could* be
    meaningfully memoized, there would be no benefit; this function is only
    called once per parameter or return of the currently decorated callable.

    This function is intended to be called *after* all possibly
    :pep:`563`-compliant **deferred type hints** (i.e., type hints persisted as
    evaluatable strings rather than actual type hints) annotating this callable
    if any have been evaluated into actual type hints.

    Parameters
    ----------
    hint : object
        Possibly PEP-noncompliant root type hint to be sanified.
    func : Callable
        Callable that this hint directly annotates a parameter or return of.
    pith_name : str
        Either:

        * If this hint annotates a parameter, the name of that parameter.
        * If this hint annotates the return, ``"return"``.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    object
        Either:

        * If this hint is PEP-noncompliant, a PEP-compliant type hint converted
          from this hint.
        * If this hint is PEP-compliant, this hint unmodified as is.

    Raises
    ----------
    BeartypeDecorHintNonpepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''

    # PEP-compliant type hint coerced (i.e., permanently converted in the
    # annotations dunder dictionary of the passed callable) from this possibly
    # PEP-noncompliant type hint if this hint is coercible *OR* this hint as is
    # otherwise. Since the passed hint is *NOT* necessarily PEP-compliant,
    # perform this coercion *BEFORE* validating this hint to be PEP-compliant.
    hint = func.__annotations__[pith_name] = _coerce_hint_root(
        hint=hint,
        func=func,
        pith_name=pith_name,
        exception_prefix=exception_prefix,
    )

    # If this object is neither a PEP-noncompliant type hint *NOR* supported
    # PEP-compliant type hint, raise an exception.
    die_unless_hint(hint=hint, exception_prefix=exception_prefix)
    # Else, this object is a supported PEP-compliant type hint.

    # Reduce this hint to a lower-level PEP-compliant type hint if this hint is
    # reducible *OR* this hint as is otherwise. Reductions simplify subsequent
    # logic elsewhere by transparently converting non-trivial hints (e.g.,
    # numpy.typing.NDArray[...]) into semantically equivalent trivial hints
    # (e.g., beartype validators).
    #
    # Whereas the above coercion permanently persists for the duration of the
    # active Python process (i.e., by replacing the original type hint in the
    # annotations dunder dictionary of this callable), this reduction only
    # temporarily persists for the duration of the current call stack. Why?
    # Because hints explicitly coerced above are assumed to be either:
    # * PEP-noncompliant and thus harmful (in the general sense).
    # * PEP-compliant but semantically deficient and thus equally harmful (in
    #   the general sense).
    #
    # In either case, coerced type hints are generally harmful in *ALL*
    # possible contexts for *ALL* possible consumers (including other competing
    # runtime type-checkers). Reduced type hints, however, are *NOT* harmful in
    # any sense whatsoever; they're simply non-trivial for @beartype to support
    # in their current form and thus temporarily reduced in-memory into a more
    # convenient form for beartype-specific type-checking purposes elsewhere.
    #
    # Note that parameters are intentionally passed positionally to both
    # optimize memoization efficiency and circumvent memoization warnings.
    hint = _reduce_hint(hint, exception_prefix)

    # Return this sanified hint.
    return hint


def sanify_hint_child(hint: object, exception_prefix: str) -> Any:
    '''
    PEP-compliant type hint sanified (i.e., sanitized) from the passed
    **PEP-compliant child type hint** (i.e., hint transitively
    subscripting the root type hint annotating a parameter or return of the
    currently decorated callable) if this hint is reducible *or* this
    hint as is otherwise (i.e., if this hint is *not* irreducible).

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be sanified.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    object
        PEP-compliant type hint sanified from this hint.
    '''

    # Return this hint first coerced and then reduced, intentionally covering
    # the subset of the logic performed by the sanify_hint_root() sanifier
    # specifically applicable to child type hints.
    return _reduce_hint(_coerce_hint_any(hint), exception_prefix)

# ....................{ COERCERS                          }....................
#FIXME: Document mypy-specific coercion in the docstring as well, please.
def _coerce_hint_root(
    hint: object,
    func: Callable,
    pith_name: str,
    exception_prefix: str,
) -> object:
    '''
    PEP-compliant type hint coerced (i.e., converted) from the passed **root
    type hint** (i.e., possibly PEP-noncompliant type hint annotating the
    parameter or return with the passed name of the passed callable if this
    hint is coercible *or* this hint as is otherwise (i.e., if this hint is
    *not* coercible).

    Specifically, if the passed hint is:

    * A **PEP-noncompliant tuple union** (i.e., tuple of one or more standard
      classes and forward references to standard classes), this function:

      * Coerces this tuple union into the equivalent :pep:`484`-compliant
        union.
      * Replaces this tuple union in the ``__annotations__`` dunder tuple of
        this callable with this :pep:`484`-compliant union.
      * Returns this :pep:`484`-compliant union.

    This function is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Since the hint returned by this
    function conditionally depends upon the passed callable, memoizing this
    function would consume space needlessly with *no* useful benefit.

    Caveats
    ----------
    This function *cannot* be meaningfully memoized, since the passed type hint
    is *not* guaranteed to be cached somewhere. Only functions passed cached
    type hints can be meaningfully memoized. Since this high-level function
    internally defers to unmemoized low-level functions that are ``O(n)`` in
    ``n`` the size of the inheritance hierarchy of this hint, this function
    should be called sparingly. See the :mod:`beartype._decor._cache.cachehint`
    submodule for further details.

    Parameters
    ----------
    hint : object
        Possibly PEP-noncompliant type hint to be possibly coerced.
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
    object
        Either:

        * If this possibly PEP-noncompliant hint is coercible, a PEP-compliant
          type hint coerced from this hint.
        * Else, this hint as is unmodified.
    '''
    assert callable(func), f'{repr(func)} not callable.'
    assert isinstance(pith_name, str), f'{pith_name} not string.'

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
        # "types.NoneType" type global. Since that has yet to happen, mypy has
        # instead taken the surprisingly sensible course of silently ignoring
        # this edge case by effectively performing the same type expansion as
        # performed here. *applause*
        return Union[hint, NotImplementedType]
    # Else, this hint is *NOT* the mypy-compliant "NotImplemented" singleton.
    # ..................{ NON-PEP                           }..................
    # If this hint is a PEP-noncompliant tuple union, coerce this union into
    # the equivalent PEP-compliant union subscripted by the same child hints.
    # By definition, PEP-compliant unions are a superset of PEP-noncompliant
    # tuple unions and thus accept all child hints accepted by the latter.
    elif isinstance(hint, tuple):
        return make_hint_pep484_union(hint)
    # Else, this hint is *NOT* a PEP-noncompliant tuple union.

    # Since none of the above conditions applied, this hint could *NOT* be
    # specifically coerced as a root type hint. Nonetheless, this hint may
    # still be generically coercible as a hint irrespective of its contextual
    # position relative to other type hints.
    #
    # Return this hint, possibly coerced as a context-agnostic type hint.
    return _coerce_hint_any(hint)


def _coerce_hint_any(hint: object) -> Any:
    '''
    PEP-compliant type hint coerced (i.e., converted) from the passed
    PEP-compliant type hint if this hint is coercible *or* this hint as is
    otherwise (i.e., if this hint is *not* coercible).

    Specifically, if the passed hint is:

    * A **PEP-compliant uncached type hint** (i.e., hint *not* already
      internally cached by its parent class or module), this function:

      * If this hint has already been passed to a prior call of this function,
        returns the semantically equivalent PEP-compliant type hint having the
        same machine-readable representation as this hint cached by that call.
        Doing so deduplicates this hint, which both:

        * Minimizes space complexity across the lifetime of this process.
        * Minimizes time complexity by enabling beartype-specific memoized
          callables to efficiently reduce to constant-time lookup operations
          when repeatedly passed copies of this hint nonetheless sharing the
          same machine-readable representation.

      * Else, internally caches this hint with a thread-safe global cache and
        returns this hint as is.

      Uncached hints include:

      * :pep:`484`-compliant subscripted generics under Python >= 3.9 (e.g.,
        ``from typing import List; class MuhPep484List(List): pass;
        MuhPep484List[int]``). See below for further commentary.
      * :pep:`585`-compliant type hints, including both:

        * Builtin :pep:`585`-compliant type hints (e.g., ``list[int]``).
        * User-defined :pep:`585`-compliant generics (e.g.,
          ``class MuhPep585List(list): pass; MuhPep585List[int]``).

    * Already cached, this hint is already PEP-compliant by definition. In this
      case, this function preserves and returns this hint as is.

    This function is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Since the hint returned by this
    function conditionally depends upon the passed callable, memoizing this
    function would consume space needlessly with *no* useful benefit.

    Design
    ------
    This function does *not* bother caching **self-caching type hints** (i.e.,
    type hints that externally cache themselves), as these hints are already
    cached elsewhere. Self-cached type hints include most type hints created by
    subscripting type hint factories declared by the :mod:`typing` module,
    which internally cache their resulting type hints: e.g.,

    .. code-block:: python

       >>> import typing
       >>> typing.List[int] is typing.List[int]
       True

    Equivalently, this function *only* caches **uncached type hints** (i.e.,
    type hints that do *not* externally cache themselves), as these hints are
    *not* already cached elsewhere. Uncached type hints include *all*
    :pep:`585`-compliant type hints produced by subscripting builtin container
    types, which fail to internally cache their resulting type hints: e.g.,

    .. code-block:: python

       >>> list[int] is list[int]
       False

    This function enables callers to coerce uncached type hints into
    :mod:`beartype`-cached type hints. :mod:`beartype` effectively requires
    *all* type hints to be cached somewhere! :mod:`beartype` does *not* care
    who, what, or how is caching those type hints -- only that they are cached
    before being passed to utility functions in the :mod:`beartype` codebase.
    Why? Because most such utility functions are memoized for efficiency by the
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator, which
    maps passed parameters (typically including the standard ``hint`` parameter
    accepting a type hint) based on object identity to previously cached return
    values. You see the problem, we trust.

    Uncached type hints that are otherwise semantically equal are nonetheless
    distinct objects and will thus be treated as distinct parameters by
    memoization decorators. If this function did *not* exist, uncached type
    hints could *not* be coerced into :mod:`beartype`-cached type hints and
    thus could *not* be memoized, dramatically reducing the efficiency of
    :mod:`beartype` for standard type hints.

    Caveats
    ----------
    This function *cannot* be meaningfully memoized, since the passed type hint
    is *not* guaranteed to be cached somewhere. Only functions passed cached
    type hints can be meaningfully memoized. Since this high-level function
    internally defers to unmemoized low-level functions that are ``O(n)`` in
    ``n`` the size of the inheritance hierarchy of this hint, this function
    should be called sparingly. See the :mod:`beartype._decor._cache.cachehint`
    submodule for further details.

    This function intentionally does *not* cache :pep:`484`-compliant generics
    subscripted by type variables under Python < 3.9. Those hints are
    technically uncached but silently treated by this function as self-cached
    and thus preserved as is. Why? Because correctly detecting those hints as
    uncached would require an unmemoized ``O(n)`` search across the inheritance
    hierarchy of *all* passed objects and thus all type hints annotating
    callables decorated by :func:`beartype.beartype`. Since this failure only
    affects obsolete Python versions *and* since the only harms induced by this
    failure are a slight increase in space and time consumption for edge-case
    type hints unlikely to actually be used in real-world code, this tradeoff
    is more than acceptable. We're not the bad guy here. Right?

    Parameters
    ----------
    hint : object
        Type hint to be possibly coerced.

    Returns
    ----------
    object
        Either:

        * If this PEP-compliant type hint is coercible, another PEP-compliant
          type hint coerced from this hint.
        * Else, this hint as is unmodified.
    '''

    # ..................{ PEP 585                           }..................
    # If this hint is PEP 585-compliant (e.g., "list[str]"), this hint is *NOT*
    # self-caching (e.g., "list[str] is not list[str]") and *MUST* thus be
    # explicitly cached here. Failing to do so disables subsequent memoization,
    # dramatically reducing decoration-time efficiency when decorating
    # callables repeatedly annotated by copies of this hint.
    #
    # Specifically, deduplicate this hint by either:
    # * If this is the first copy of this hint passed to this function, cache
    #   this hint under its machine-readable implementation.
    # * Else, one or more prior copies of this hint have already been passed to
    #   this function. In this case, replace this subsequent copy by the first
    #   copy of this hint originally passed to a prior call of this function.
    if is_hint_pep585_builtin(hint):
        return _HINT_REPR_TO_HINT.get_value_static(key=repr(hint), value=hint)
    # Else, this hint is *NOT* PEP 585-compliant.

    # Return this uncoerced hint as is.
    return hint

# ....................{ REDUCERS                          }....................
#FIXME: Improve documentation to list all reductions performed by this reducer.
#Sadly, this documentation is currently quite out-of-date. What? It happens!
@callable_cached
def _reduce_hint(hint: Any, exception_prefix: str) -> object:
    '''
    Lower-level type hint reduced (i.e., converted) from the passed
    higher-level type hint if this hint is reducible *or* this hint as is
    otherwise (i.e., if this hint is irreducible).

    Specifically, if the passed hint is:

    * *Not* PEP-compliant, this hint is returned as is unmodified.
    * PEP 593-compliant (i.e., :class:`typing.Annotated`) but beartype-agnostic
      (i.e., its second argument is *not* an instance of the
      :class:`beartype.vale._core._valecore.BeartypeValidator` class produced by
      subscripting the :class:`beartype.vale.Is` class), this hint is reduced
      to the first argument subscripting this hint. Doing so ignores *all*
      irrelevant annotations on this hint (e.g., reducing
      ``typing.Annotated[str, 50, False]`` to simply ``str``).

    This function is memoized for efficiency.

    Parameters
    ----------
    hint : Any
        Type hint to be possibly reduced.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    object
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
        hint = reduce_hint_pep484_generic_io_to_pep544_protocol(
            hint=hint, exception_prefix=exception_prefix)
    # ..................{ PEP 557                           }..................
    # If this hint is a dataclass-specific initialization-only instance
    # variable (i.e., instance of the PEP 557-compliant "dataclasses.InitVar"
    # class introduced by Python 3.8.0), reduce this functionally useless hint
    # to the functionally useful child type hint subscripting this parent hint.
    #
    # "InitVar" instances are stupefyingly rare and thus detected even later.
    elif hint_sign is HintSignDataclassInitVar:
        hint = get_hint_pep557_initvar_arg(
            hint=hint, exception_prefix=exception_prefix)

    # Return this possibly reduced hint.
    return hint
