#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint sanitizers** (i.e., high-level callables
converting type hints from one format into another, either permanently or
temporarily and either losslessly or in a lossy manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    Optional,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.metadata.metadecor import BeartypeDecorMeta
from beartype._check.convert.convcoerce import (
    coerce_func_hint_root,
    coerce_hint_any,
    coerce_hint_root,
)
from beartype._check.convert.convreduce import reduce_hint
from beartype._conf.confcls import BeartypeConf
from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.hint.datahinttyping import TypeStack
from beartype._util.cache.map.utilmapbig import CacheUnboundedStrong
from beartype._util.func.arg.utilfuncargiter import ArgKind
from beartype._util.hint.pep.proposal.pep484585.utilpep484585func import (
    reduce_hint_pep484585_func_return)
from beartype._util.hint.utilhinttest import is_hint_ignorable

# ....................{ SANIFIERS ~ root                   }....................
#FIXME: Unit test us up, please.
def sanify_hint_root_func(
    # Mandatory parameters.
    decor_meta: BeartypeDecorMeta,
    hint: object,
    pith_name: str,

    # Optional parameters.
    arg_kind: Optional[ArgKind] = None,
    exception_prefix: str = EXCEPTION_PLACEHOLDER,
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
    -------
    This sanifier *cannot* be meaningfully memoized, since the passed type hint
    is *not* guaranteed to be cached somewhere. Only functions passed cached
    type hints can be meaningfully memoized. Even if this function *could* be
    meaningfully memoized, there would be no benefit; this function is only
    called once per parameter or return of the currently decorated callable.

    This sanifier is intended to be called *after* all possibly
    :pep:`563`-compliant **deferred type hints** (i.e., type hints persisted as
    evaluatable strings rather than actual type hints) annotating this callable
    if any have been evaluated into actual type hints.

    Parameters
    ----------
    decor_meta : BeartypeDecorMeta
        Decorated callable directly annotated by this hint.
    hint : object
        Possibly PEP-noncompliant root type hint to be sanified.
    pith_name : str
        Either:

        * If this hint annotates a parameter, the name of that parameter.
        * If this hint annotates the return, ``"return"``.
    arg_kind : Optional[ArgKind]
        Either:

        * If this hint annotates a parameter, that parameter's **kind** (i.e.,
          :class:`.ArgKind` enumeration member conveying the syntactic class of
          that parameter, constraining how the callable declaring that parameter
          requires that parameter to be passed).
        * If this hint annotates the return, :data:`None`.

        Defaults to :data:`None`.
    exception_prefix : str, optional
        Human-readable label prefixing exception messages raised by this
        function. Defaults to :data:`EXCEPTION_PLACEHOLDER`.

    Returns
    -------
    object
        Either:

        * If this hint is PEP-noncompliant, a PEP-compliant type hint converted
          from this hint.
        * If this hint is PEP-compliant, this hint unmodified as is.

    Raises
    ------
    BeartypeDecorHintNonpepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''
    assert isinstance(arg_kind, NoneTypeOr[ArgKind]), (
        f'{repr(arg_kind)} neither argument kind nor "None".')

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the sanify_hint_root_statement() sanitizer.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    #FIXME: This attempt at mutating the "__annotations__" dunder dictionary is
    #likely to fail under Python >= 3.13. Contemplate alternatives, please.
    # PEP-compliant type hint coerced from this possibly (i.e., permanently
    # converted in the annotations dunder dictionary of the passed callable)
    # PEP-noncompliant type hint if this hint is coercible *OR* this hint as is
    # otherwise. Since the passed hint is *NOT* necessarily PEP-compliant,
    # perform this coercion *BEFORE* validating this hint to be PEP-compliant.
    hint = decor_meta.func_arg_name_to_hint[pith_name] = coerce_func_hint_root(
        decor_meta=decor_meta,
        hint=hint,
        pith_name=pith_name,
        exception_prefix=exception_prefix,
    )

    # If this hint annotates the return, then (in order):
    # * If this hint is contextually invalid for this callable (e.g., generator
    #   whose return is not annotated as "Generator[...]"), raise an exception.
    # * If this hint is either PEP 484- or 585-compliant *AND* requires
    #   reduction (e.g., from "Coroutine[None, None, str]" to just "str"),
    #   reduce this hint accordingly.
    #
    # Perform this reduction *BEFORE* performing subsequent tests (e.g., to
    # accept "Coroutine[None, None, typing.NoReturn]" as expected). Note that
    # this logic *ONLY* pertains to callables (rather than statements) and is
    # thus *NOT* performed by the sanify_hint_root_statement() sanitizer.
    if pith_name == ARG_NAME_RETURN:
        hint = reduce_hint_pep484585_func_return(
            func=decor_meta.func_wrappee,
            func_arg_name_to_hint=decor_meta.func_arg_name_to_hint,
            exception_prefix=exception_prefix,
        )
    # Else, this hint annotates a parameter.

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
    # In either case, coerced type hints are generally harmful in *ALL* possible
    # contexts for *ALL* possible consumers (including other competing runtime
    # type-checkers). Reduced type hints, however, are *NOT* harmful in any
    # sense whatsoever; they're simply non-trivial for @beartype to support in
    # their current form and thus temporarily reduced in-memory into a more
    # convenient form for beartype-specific type-checking purposes elsewhere.
    #
    # Return sanified hint.
    # Note that parameters are intentionally passed positionally to both
    # optimize memoization efficiency and circumvent memoization warnings.
    return reduce_hint(
        hint=hint,
        conf=decor_meta.conf,
        decor_meta=decor_meta,
        arg_kind=arg_kind,
        cls_stack=decor_meta.cls_stack,
        pith_name=pith_name,
        exception_prefix=exception_prefix,
    )


#FIXME: Unit test us up, please.
def sanify_hint_root_statement(
    hint: object,
    conf: BeartypeConf,
    exception_prefix: str,
) -> object:
    '''
    PEP-compliant type hint sanified (i.e., sanitized) from the passed **root
    type hint** (i.e., possibly PEP-noncompliant type hint that has *no* parent
    type hint) if this hint is reducible *or* this hint as is otherwise (i.e.,
    if this hint is irreducible).

    This sanifier is principally intended to be called by a **statement-level
    type-checker factory** (i.e., a function creating and returning a runtime
    type-checker type-checking this hint, outside the context of any standard
    type hinting annotation like a user-defined class variable, callable
    parameter or return, or assignment statement). Such factories include:

    * The private :func:`beartype._check.checkmake.make_func_tester` factory,
      internally called by:

      * The public :func:`beartype.door.is_bearable` function.
      * The public :meth:`beartype.door.TypeHint.is_bearable` method.

    Parameters
    ----------
    hint : object
        Possibly PEP-noncompliant root type hint to be sanified.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    -------
    object
        Either:

        * If this hint is PEP-noncompliant, a PEP-compliant type hint converted
          from this hint.
        * If this hint is PEP-compliant, this hint unmodified as is.

    Raises
    ------
    BeartypeDecorHintNonpepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.

    See Also
    --------
    :func:`.sanify_hint_root_func`
        Further details.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the sanify_hint_root_func() sanitizer, please.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # PEP-compliant type hint coerced from this possibly PEP-noncompliant type
    # hint if this hint is coercible *OR* this hint as is otherwise. Since the
    # passed hint is *NOT* necessarily PEP-compliant, perform this coercion
    # *BEFORE* validating this hint to be PEP-compliant.
    hint = coerce_hint_root(hint=hint, exception_prefix=exception_prefix)

    # Reduce this hint to a lower-level PEP-compliant type hint if this hint is
    # reducible *OR* this hint as is otherwise and return it. See
    # sanify_hint_root_func() for further commentary.
    return reduce_hint(hint=hint, conf=conf, exception_prefix=exception_prefix)


# ....................{ SANIFIERS ~ any                    }....................
#FIXME: Unit test us up, please.
def sanify_hint_child_if_unignorable_or_none(*args, **kwargs) -> Any:
    '''
    Type hint sanified (i.e., sanitized) from the passed **possibly insane child
    type hint** (i.e., hint transitively subscripting the root type hint
    annotating a parameter or return of the currently decorated callable) if
    this hint is both reducible and ignorable, this hint unmodified if this hint
    is both irreducible and ignorable, and :data:`None` otherwise (i.e., if this
    hint is ignorable).

    This high-level sanifier effectively chains the lower-level
    :func:`sanify_hilt_child` sanifier and
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester into a
    single unified function, streamlining sanification and ignorability
    detection throughout the codebase.

    Note that a :data:`None` return unambiguously implies this hint to be
    ignorable, even if the passed hint is itself :data:`None`. Why? Because if
    the passed hint were :data:`None`, then a :pep:`484`-compliant reducer will
    internally reduce this hint to ``type(None)``. After reduction, *all* hints
    are guaranteed to be non-:data:`None`.

    Parameters
    ----------
    All passed arguments are passed as is to the lower-level
    :func:`sanify_hilt_child` sanifier.

    Returns
    -------
    object
        Either:

        * If the passed possibly insane child type hint is ignorable after
          reduction to a sane child type hint, :data:`None`.
        * Else, the sane child type hint to which this hint reduces.
    '''

    # Sane child hint sanified from this possibly insane child hint if this hint
    # is reducible *OR* this hint as is otherwise (i.e., if irreducible).
    hint_child = sanify_hint_child(*args, **kwargs)

    # Return either "None" if this hint is ignorable or this hint otherwise.
    return None if is_hint_ignorable(hint_child) else hint_child


def sanify_hint_child(
    # Mandatory parameters.
    hint: object,
    conf: BeartypeConf,
    exception_prefix: str,

    # Optional parameters.
    cls_stack: TypeStack = None,
    pith_name: Optional[str] = None,
) -> Any:
    '''
    Type hint sanified (i.e., sanitized) from the passed **possibly insane child
    type hint** (i.e., hint transitively subscripting the root type hint
    annotating a parameter or return of the currently decorated callable) if
    this hint is reducible *or* this hint unmodified otherwise (i.e., if this
    hint is irreducible).

    Parameters
    ----------
    hint : object
        Type hint to be sanified.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    exception_prefix : str
        Substring prefixing exception messages raised by this function.
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.
    pith_name : Optional[str], optional
        Either:

        * If this hint directly annotates a callable parameter (as the root type
          hint of that parameter), the name of this parameter.
        * If this hint directly annotates a callable return (as the root type
          hint of that return), the magic string ``"return"``.
        * Else, :data:`None`.

        Defaults to :data:`None`.

    Returns
    -------
    object
        Type hint sanified from this possibly insane child type hint.
    '''

    # This sanifier covers the proper subset of logic performed by the
    # sanify_hint_root_statement() sanifier applicable to child type hints.

    # PEP-compliant type hint coerced (i.e., permanently converted in the
    # annotations dunder dictionary of the passed callable) from this possibly
    # PEP-noncompliant type hint if this hint is coercible *OR* this hint as is
    # otherwise. Since the passed hint is *NOT* necessarily PEP-compliant,
    # perform this coercion *BEFORE* validating this hint to be PEP-compliant.
    hint = coerce_hint_any(hint)

    # Return this hint reduced.
    return reduce_hint(
        hint=hint,
        conf=conf,
        cls_stack=cls_stack,
        pith_name=pith_name,
        exception_prefix=exception_prefix,
    )


# ....................{ PRIVATE ~ mappings                 }....................
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

Design
------
**This dictionary is intentionally thread-safe.** Why? Because this dictionary
is used to modify the ``__attributes__`` dunder variable of arbitrary callables.
Since most of those callables are either module- or class-scoped, that variable
is effectively global. To prevent race conditions between competing threads
contending over that global variable, this dictionary *must* be thread-safe.

This dictionary is intentionally designed as a naive dictionary rather than a
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
