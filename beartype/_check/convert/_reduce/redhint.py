#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint reducers** (i.e., low-level callables converting type
hints from one format into another, either losslessly or in a lossy manner).

Type hint reductions imposed by this submodule are purely internal to
:mod:`beartype` itself and thus transient in nature. These reductions are *not*
permanently applied to the ``__annotations__`` dunder dictionaries of the
classes and callables annotated by these type hints.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.meta import URL_ISSUES
from beartype.roar import BeartypeDecorHintReduceException
from beartype.typing import Optional
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.convert._reduce._redmap import (
    HINT_SIGN_TO_REDUCE_HINT_CACHED_get,
    HINT_SIGN_TO_REDUCE_HINT_UNCACHED_get,
)
from beartype._check.metadata.metadecor import BeartypeDecorMeta
from beartype._check.metadata.hint.hintsane import (
    HINT_IGNORABLE,
    HintOrSane,
    HintSane,
)
from beartype._conf.confcls import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.hint.datahintpep import (
    Hint,
    SetHints,
)
from beartype._data.hint.datahinttyping import (
    DictStrToAny,
    TypeStack,
)
from beartype._data.hint.pep.datapeprepr import HINTS_REPR_IGNORABLE_SHALLOW
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.func.arg.utilfuncargiter import ArgKind
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from beartype._util.hint.utilhintget import get_hint_repr
from beartype._util.hint.utilhinttest import die_unless_hint
from beartype._util.kind.map.utilmapset import remove_mapping_keys
from beartype._util.utilobject import SENTINEL

# ....................{ REDUCERS                           }....................
def reduce_hint(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    arg_kind: Optional[ArgKind] = None,
    cls_stack: TypeStack = None,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    decor_meta: Optional[BeartypeDecorMeta] = None,
    hints_overridden: Optional[SetHints] = None,
    parent_hint_sane: Optional[HintSane] = None,
    pith_name: Optional[str] = None,
    reductions_count: int = 0,
    exception_prefix: str = '',
) -> HintSane:
    '''
    Lower-level type hint reduced (i.e., converted) from the passed higher-level
    type hint if this hint is reducible *or* this hint as is otherwise (i.e., if
    this hint is irreducible).

    This reducer *cannot* be meaningfully memoized, since multiple passed
    parameters (e.g., ``pith_name``, ``cls_stack``) are typically isolated to a
    handful of callables across the codebase currently being decorated by
    :mod:`beartype`. Memoizing this reducer would needlessly consume space and
    time. To improve efficiency, this reducer is instead implemented in terms of
    two lower-level private reducers:

    * The memoized :func:`._reduce_hint_cached` reducer, responsible for
      efficiently reducing *most* (but not all) type hints.
    * The unmemoized :func:`._reduce_hint_uncached` reducer, responsible for
      inefficiently reducing the small subset of type hints contextually
      requiring these problematic parameters.

    Parameters
    ----------
    hint : Hint
        Type hint to be possibly reduced.
    arg_kind : Optional[ArgKind]
        Either:

        * If this hint annotates a parameter of some callable, that parameter's
          **kind** (i.e., :class:`.ArgKind` enumeration member conveying the
          syntactic class of that parameter, constraining how the callable
          declaring that parameter requires that parameter to be passed).
        * Else, :data:`None`.

        Defaults to :data:`None`.
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to the default beartype configuration.
    decor_meta : Optional[BeartypeDecorMeta], optional
        Either:

        * If this hint annotates a parameter or return of some callable, the
          :mod:`beartype`-specific decorator metadata describing that callable.
        * Else, :data:`None`.

        Defaults to :data:`None`.
    hints_overridden : set[Hint], optional
        Mutable set of all previously **overridden hints** (i.e., hints reduced
        to user-defined hint overrides configured by the
        :attr:`beartype.BeartypeConf.hint_overrides` dictionary) reduced by a
        prior call to this function, guarding against accidental infinite
        recursion between lower-level reducers and this higher-level function.
        If a hint has already been overridden in the current call stack rooted
        at the top-most call to this function, this function avoids dangerously
        re-overriding nested instances of the same hint. Defaults to the empty
        set.
    parent_hint_sane : Optional[HintSane]
        Either:

        * If the passed hint is a **root** (i.e., top-most parent hint of a tree
          of child hints), :data:`None`.
        * Else, the passed hint is a **child** of some parent hint. In this
          case, the **sanified parent type hint metadata** (i.e., immutable and
          thus hashable object encapsulating *all* metadata previously returned
          by :mod:`beartype._check.convert.convsanify` sanifiers after
          sanitizing the possibly PEP-noncompliant parent hint of this child
          hint into a fully PEP-compliant parent hint).

        Defaults to :data:`None`.
    pith_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.

        Defaults to :data:`None`.
    reductions_count : int, optional
        Current number of total reductions internally performed by *all* calls
        to this function rooted at this function in the current call stack,
        guarding against accidental infinite recursion between lower-level
        reducers and this higher-level function. Defaults to 0.
    exception_prefix : str, optional
        Human-readable substring prefixing exception messages raised by this
        reducer. Defaults to the empty string.

    Returns
    -------
    HintSane
        Either:

        * If this hint is ignorable, :data:`.HINT_IGNORABLE`.
        * Else if this unignorable hint is reducible to another hint, metadata
          encapsulating this reduction.
        * Else, this unignorable hint is irreducible. In this case, metadata
          encapsulating this hint unmodified.

    Raises
    ------
    BeartypeDecorHintReduceException
        If the number of total reductions internally performed by the current
        call to this function exceeds the maximum. This exception guards against
        accidental infinite recursion between lower-level PEP-specific reducers
        internally called by this higher-level reducer.
    '''

    # ....................{ PREAMBLE                       }....................
    # If passed *NO* hint overrides, default this set to the empty set.
    if hints_overridden is None:
        hints_overridden = set()
    # Else, hint overrides were passed. Preserve these hint overrides as is.

    # Validate passed parameters *AFTER* establishing defaults above.
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'
    assert isinstance(hints_overridden, set), (
        f'{repr(hints_overridden)} not set.')
    assert isinstance(parent_hint_sane, NoneTypeOr[HintSane]), (
        f'{repr(parent_hint_sane)} neither sanified hint metadata nor "None".')
    assert isinstance(reductions_count, int), (
        f'{repr(reductions_count)} not integer.')

    # ....................{ LOCALS                         }....................
    # Original unreduced hint passed to this reducer, preserved so as to be
    # embedded in human-readable exception messages.
    hint_old = hint

    # Currently reduced instance of this hint.
    hint_curr: Hint = hint

    # Currently reduced instance of either this hint *OR* metadata encapsulating
    # this hint.
    hint_or_sane_curr: HintOrSane = hint

    # Previously reduced instance of either this hint *OR* metadata
    # encapsulating this hint, initialized to the sentinel to guarantee that the
    # passed hint is *NEVER* equal to the previously reduced instance of this
    # hint unless actually reduced below. This is required for disambiguity, as
    # "None" is a valid type hint reduced to "type(None)" below.
    hint_or_sane_prev: HintOrSane = SENTINEL  # type: ignore[assignment]

    # BeartypeHintOverrides.get() method bound to the user-defined
    # "hint_overrides" dictionary of this beartype configuration, localized as a
    # negligible efficiency gain.
    conf_hint_overrides_get = conf.hint_overrides.get

    # Delete the passed "hint" parameter for safety. Permitting this parameter
    # to exist would only promote subtle lexical issues below, where the local
    # variable "hint_curr" is strongly preferred for disambiguity.
    del hint

    # ....................{ REDUCTION                      }....................
    # Repeatedly reduce this hint to increasingly irreducible hints until this
    # hint is no longer reducible.
    #
    # Note that this algorithm iteratively reduces this hint with a battery of
    # increasingly non-trivial reductions. For efficiency, reductions are
    # intentionally ordered from most to least efficient.
    while True:
        # print(f'[reduce_hint] Reducing {repr(hint)} with type variable lookup table {repr(typevar_to_hint)}...')

        # ....................{ PHASE ~ shallow            }....................
        # Attempt to shallowly reduce this hint to the ignorable
        # "HINT_IGNORABLE" singleton *BEFORE* attempting reductions that deeply
        # inspect the contents of this hint. Why? Several reasons:
        # * This shallow reduction is an O(1) constant-time operation with
        #   negligible constants and thus *INCREDIBLY* fast.
        # * Okay. That's all I've got. It's late, people. I exhaustedly sigh.

        #FIXME: This is... kinda silly. Turns out we already had an existing
        #mechanism for detecting shallowly ignorable hints: the
        #"HINT_SIGNS_BARE_IGNORABLE" set. The advantage of that over the
        #"HINTS_REPR_IGNORABLE_SHALLOW" set tested below is that the former is
        #*A LOT* less fragile. For example, the former trivially supports
        #"typing_extensions"; the latter does not.
        #    hint_sign = get_hint_pep_sign_or_none(hint)
        #    hint_args = get_hint_pep_args(hint)
        #
        #    if hint is object or (
        #        not hint_args and
        #        hint_sign in HINT_SIGNS_BARE_IGNORABLE
        #    ):
        #        return HINT_IGNORABLE

        # Machine-readable representation of this hint.
        hint_repr = get_hint_repr(hint_curr)

        # If this hint is shallowly ignorable, reduce this hint to the ignorable
        # "HINT_IGNORABLE" singleton.
        #
        # Note that this reduction efficiently applies to multiple signs
        # concurrently, including the "None", "HintSignOptional", and
        # "HintSignUnion". Ergo, this reduction *CANNOT* be trivially
        # implemented as a standard reduction assigned a single sign.
        if hint_repr in HINTS_REPR_IGNORABLE_SHALLOW:
            return HINT_IGNORABLE
        # Else, this hint is *NOT* shallowly ignorable.

        # ....................{ PHASE ~ override           }....................
        # Attempt to reduce this hint to another hint configured by a
        # user-defined hint override *BEFORE* attempting standard reduction.
        # User preference takes precedence over standard precedent.

        #FIXME: *UGH*. There's *NO* need at all for EAFP. Instead:
        #* Refactor this to use hint IDs rather than possibly unhashable hints.
        #* In fact, just refactor this to use our new "recursable_hints"
        #  approach entirely, please.

        # Attempt to...
        #
        # Note that the is_object_hashable() tester is internally implemented
        # with the same Easier to Ask for Permission than Forgiveness
        # (EAFP)-based "try-except" block and is thus equally inefficient. In
        # fact, the current approach avoids an extraneous call to that tester
        # and is thus marginally faster. (Emphasis on "marginally.")
        try:
            # If this hint has *NOT* already been overridden by a previously
            # performed reduction in this recursive tree of all previously
            # performed reductions...
            if hint_curr not in hints_overridden:
                # User-defined hint overriding this hint if this beartype
                # configuration overrides this hint *OR* the sentinel otherwise
                # (i.e., if this hist is *NOT* overridden).
                # print(f'Overriding hint {repr(hint)} via {repr(conf.hint_overrides)}...')
                hint_reduced = conf_hint_overrides_get(hint_curr, SENTINEL)

                # If this hint was overridden...
                if hint_reduced is not SENTINEL:
                    # Record this hint as already having been overridden
                    # *BEFORE* reducing (and thus obliterating) this hint.
                    hints_overridden.add(hint_curr)

                    # Reduce this hint to this user-defined hint override.
                    hint_curr = hint_reduced
                # Else, this hint was *NOT* overridden. In this case, preserve
                # this hint as is.
            # Else, this hint has already been overridden by a previously
            # performed reduction in this recursive tree of all previously
            # performed reductions. In this case, avoid overriding this hint yet
            # again. Doing so would (almost certainly) provoke infinite
            # recursion (e.g., overriding "float" with "int | float").
        # If doing so raises a "TypeError", this hint is unhashable and thus
        # inapplicable for hint overriding. In this case, ignore this hint.
        except TypeError:
            pass

        # ....................{ PHASE ~ uncached           }....................
        # Attempt to deeply reduce this possibly contextual hint to another hint
        # *BEFORE* attempting to context-free reductions. Why? Because the
        # former depends on context and is thus "lower-level" than the latter,
        # which depends on *NO* context and is thus "higher-level" in a sense.
        #
        # In theory, order of reduction *SHOULD* be insignificant; in practice,
        # we suspect unforeseen and unpredictable interactions between these two
        # reductions. To reduce the likelihood of fire-breathing dragons here,
        # we reduce contextual hints first.
        hint_or_sane_curr = _reduce_hint_uncached(
            hint=hint_curr,
            arg_kind=arg_kind,
            cls_stack=cls_stack,
            conf=conf,
            decor_meta=decor_meta,
            hints_overridden=hints_overridden,
            pith_name=pith_name,
            parent_hint_sane=parent_hint_sane,
            reductions_count=reductions_count,
            exception_prefix=exception_prefix,
        )

        #FIXME: Make sure we've replaced "Any" with "HINT_IGNORABLE" throughout
        #the codebase, please.
        # If this hint is ignorable, halt reducing.
        #
        # Note that this is an optional short-circuiting optimization avoiding
        # multiple repetitious reductions for each ignorable hint.
        if hint_or_sane_curr is HINT_IGNORABLE:
            return HINT_IGNORABLE
        # Else, this hint is currently unignorable. Continue reducing.

        #FIXME: Comment us up, please.
        hint_curr = (
            hint_or_sane_curr.hint
            if isinstance(hint_or_sane_curr, HintSane) else
            hint_or_sane_curr
        )

        # ....................{ PHASE ~ cached             }....................
        #FIXME: Is passing the "conf" parameter here worthwhile? How many cached
        #reductions actually benefit from receiving a "conf"? If the answer is
        #"Hardly any, bro.", then:
        #* Those cached reductions that actually benefit from receiving a "conf"
        #  should just be refactored into uncached reductions.
        #* We should stop passing "conf" altogether below. Doing so improves
        #  caching efficiency for the general case, which is all that matters.

        # Sane hint reduced from this possibly insane hint if reducing this hint
        # did not generate supplementary metadata *OR* that metadata otherwise
        # (i.e., if reducing this hint generated supplementary metadata).
        hint_or_sane_curr = _reduce_hint_cached(
            hint_curr, conf, exception_prefix)

        # If this hint is ignorable, halt reducing.
        #
        # Note that, unlike the similar test above, this test is required rather
        # than merely an optimization.
        if hint_or_sane_curr is HINT_IGNORABLE:
            return HINT_IGNORABLE
        # Else, this hint is currently unignorable. Continue reducing.
        #
        # If the current and previously reduced instances of this hint are
        # identical, the above reductions all preserved this hint as is rather
        # than reducing this hint. This implies this hint to now be irreducible.
        # Halt reducing.
        elif hint_or_sane_curr is hint_or_sane_prev:
            break
        # Else, the current and previously reduced instances of this hint
        # differ, implying this hint to still be reducible. Continue reducing.

        #FIXME: Improve commentary, please. *sigh*
        # If reducing this hint generated supplementary metadata...
        elif isinstance(hint_or_sane_curr, HintSane):
            if parent_hint_sane is not None:
                #FIXME: *AWFUL.* Do something sane here, please. Notably, we
                #should composite the "parent_hint_sane" and "hint_or_sane_curr"
                #metadata together into "hint_or_sane_curr".
                raise ValueError(
                    f'Sanified type hint {repr(hint_or_sane_curr)} '
                    f'returned by cached reducer.'
                )

            parent_hint_sane = hint_or_sane_curr
            hint_curr = hint_or_sane_curr.hint
        # elif parent_hint_sane is not None:
        #     hint_or_sane_curr = parent_hint_sane.permute(hint=hint_or_sane_curr)
        else:
            hint_curr = hint_or_sane_curr

        # Increment the current number of total reductions internally performed
        # by this call *BEFORE* detecting accidental recursion below.
        reductions_count += 1

        # If the current number of total reductions internally performed
        # by this call exceeds the maximum, raise an exception.
        #
        # Note that this should *NEVER* happen, but probably nonetheless will.
        if reductions_count >= _REDUCTIONS_COUNT_MAX:  # pragma: no cover
            raise BeartypeDecorHintReduceException(
                f'{exception_prefix}type hint {repr(hint_old)} irreducible; '
                f'recursion detected when reducing between reduced type hints '
                f'{repr(hint_or_sane_curr)} and {repr(hint_or_sane_prev)}. '
                f'Please submit this exception traceback as a new issue '
                f'on our friendly issue tracker:\n'
                f'\t{URL_ISSUES}\n'
                f'Beartype thanks you for your noble (yet ultimately tragic) '
                f'sacrifice.'
            )
        # Else, the current number of total reductions internally performed
        # by this call is still less than the maximum. In this case, continue.

        # Previously reduced instance of this hint.
        hint_or_sane_prev = hint_or_sane_curr

    # ....................{ RETURN                         }....................
    # If this hint is *NOT* already sanified type hint metadata, this hint is
    # unignorable. Why? Because, if this hint were ignorable, this hint would
    # have been reduced to the "HINT_IGNORABLE" singleton. In this case,
    # trivially encapsulate this hint with sanified type hint metadata.
    if not isinstance(hint_or_sane_curr, HintSane):
        hint_or_sane_curr = HintSane(hint)
    # Else, this hint is already sanified type hint metadata. In this case,
    # preserve this metadata as is.

    # Return this possibly reduced hint.
    return hint_or_sane_curr


def reduce_hint_child(
    hint: Hint, kwargs: DictStrToAny) -> HintSane:
    '''
    Lower-level child type hint reduced (i.e., converted) from the passed
    higher-level child type hint if reducible *or* this child type hint as
    is otherwise (i.e., if this child type hint is irreducible).

    This reducer is a convenience wrapper for the more general-purpose
    :func:`.reduce_hint` reducer, simplifying calls to that reducer when passed
    child hints.

    Parameters
    ----------
    hint : Hint
        Child type hint to be reduced.
    kwargs : DictStrToAny
        Keyword parameters to be passed after being unpacked to the lower-level
        :func:`.reduce_hint` reducer. For safety, this reducer silently ignores
        keyword parameters inapplicable to child hints. This includes:

        * ``arg_kind``, applicable *only* to root hints directly annotating
          callable parameters.
        * ``decor_meta``, applicable *only* to root hints directly annotating
          callable parameters or returns.
        * ``pith_name``, applicable *only* to root hints directly annotating
          callable parameters or returns.

    Returns
    -------
    HintSane
        Either:

        * If this hint is ignorable, :data:`.HINT_IGNORABLE`.
        * Else if this unignorable hint is reducible to another hint, metadata
          encapsulating this reduction.
        * Else, this unignorable hint is irreducible. In this case, metadata
          encapsulating this hint unmodified.
    '''

    # Remove all unsafe keyword parameters (i.e., parameters that are
    # inapplicable to child hints and thus *NOT* safely passable to the
    # subsequently called reduce_hint() function) from this dictionary.
    remove_mapping_keys(kwargs, _REDUCE_HINT_CHILD_ARG_NAMES_UNSAFE)

    # Return this child hint possibly reduced to a lower-level hint.
    return reduce_hint(hint=hint, **kwargs)

# ....................{ PRIVATE ~ reducers                 }....................
# Note that the higher-level reduce_hint() reducer defined above sequentially
# calls the lower-level _reduce_hint_uncached() reducer defined below *BEFORE*
# calling the lower-level _reduce_hint_cached() reducer defined below. As such,
# the current hint should be validated in the former rather than the latter.

def _reduce_hint_uncached(
    hint: Hint,
    arg_kind: Optional[ArgKind],
    cls_stack: TypeStack,
    conf: BeartypeConf,
    decor_meta: Optional[BeartypeDecorMeta],
    hints_overridden: SetHints,
    parent_hint_sane: Optional[HintSane],
    pith_name: Optional[str],
    reductions_count: int,
    exception_prefix: str,
) -> Hint:
    '''
    Lower-level **contextual type hint** (i.e., type hint contextually dependent
    on the kind of class, attribute, callable parameter, or callable return
    annotated by this hint) inefficiently reduced (i.e., converted) from the
    passed higher-level context-free type hint if this hint is reducible *or*
    this hint as is otherwise (i.e., if this hint is irreducible).

    This reducer *cannot* be meaningfully memoized, since multiple passed
    parameters (e.g., ``pith_name``, ``cls_stack``) are typically isolated to a
    handful of callables across the codebase currently being decorated by
    :mod:`beartype`. Thankfully, this reducer is responsible for reducing only a
    small subset of type hints requiring these problematic parameters.

    Parameters
    ----------
    hint : Hint
        Type hint to be possibly reduced.
    arg_kind : Optional[ArgKind]
        Either:

        * If this hint annotates a parameter of some callable, that parameter's
          **kind** (i.e., :class:`.ArgKind` enumeration member conveying the
          syntactic class of that parameter, constraining how the callable
          declaring that parameter requires that parameter to be passed).
        * Else, :data:`None`.
    cls_stack : TypeStack
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    decor_meta : Optional[BeartypeDecorMeta]
        Either:

        * If this hint annotates a parameter or return of some callable, the
          :mod:`beartype`-specific decorator metadata describing that callable.
        * Else, :data:`None`.
    hints_overridden : set[Hint]
        Mutable set of all previously **overridden hints** (i.e., hints reduced
        to user-defined hint overrides configured by the
        :attr:`beartype.BeartypeConf.hint_overrides` dictionary) reduced by a
        prior call to this function, guarding against accidental infinite
        recursion between lower-level reducers and this higher-level function.
        If a hint has already been overridden in the current call stack rooted
        at the top-most call to this function, this function avoids dangerously
        re-overriding nested instances of the same hint.
    parent_hint_sane : Optional[HintSane]
        Either:

        * If the passed hint is a **root** (i.e., top-most parent hint of a tree
          of child hints), :data:`None`.
        * Else, the passed hint is a **child** of some parent hint. In this
          case, the **sanified parent type hint metadata** (i.e., immutable and
          thus hashable object encapsulating *all* metadata previously returned
          by :mod:`beartype._check.convert.convsanify` sanifiers after
          sanitizing the possibly PEP-noncompliant parent hint of this child
          hint into a fully PEP-compliant parent hint).
    pith_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.
    reductions_count : int
        Current number of total reductions internally performed by *all* calls
        to this function rooted at this function in the current call stack,
        guarding against accidental infinite recursion between lower-level
        reducers and this higher-level function.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    Returns
    -------
    Hint
        Either:

        * If this hint is ignorable, :obj:`typing.Any`.
        * Else if this unignorable hint is reducible to another hint, that hint.
        * Else, this unignorable hint is irreducible. In this case, this hint
          unmodified.
    '''

    # Sign uniquely identifying this hint if this hint is PEP-compliant *OR*
    # "None" otherwise (e.g., if this hint is PEP-noncompliant).
    hint_sign = get_hint_pep_sign_or_none(hint)
    # print(f'_reduce_hint_uncached() hint_sign: {hint_sign}')

    # If this hint is PEP-noncompliant...
    #
    # Note that this logic could also be handled in a reduce_hint_nonpep()
    # reducer mapped to the "None" sign, whose body is the body of this "if"
    # conditional. Indeed, the prior implementation of this logic did just that.
    # Technically, that approach did work. Pragmatically, that approach was
    # obfuscatory, obtuse, and ultimately unmaintainable. This approach is
    # equally efficient but *CONSIDERABLY* more sensible. Sanity wins.
    if hint_sign is None:
        # If this hint is unsupported by @beartype, raise an exception.
        die_unless_hint(hint=hint, exception_prefix=exception_prefix)
        # Else, this hint is supported by @beartype.

        # Return this hint as is. By definition, PEP-noncompliant hints are
        # irreducible. If this hint was instead reducible, the
        # get_hint_pep_sign_or_none() getter called above would have instead
        # returned a unique sign identifying this hint (rather than "None").
        return hint
    # Else, this hint is PEP-compliant.

    # Callable reducing this hint if a callable reducing hints of this sign was
    # previously registered *OR* "None" otherwise (i.e., if *NO* such callable
    # was registered, in which case this hint is preserved as is).
    hint_reducer = HINT_SIGN_TO_REDUCE_HINT_UNCACHED_get(hint_sign)

    # If a callable reducing hints of this sign was previously registered,
    # reduce this hint to another hint via this callable.
    if hint_reducer is not None:  # type: ignore[call-arg]
        # print(f'[_reduce_hint_uncached] Reducing uncached hint {repr(hint)}...')
        # print(f'...with type variable lookup table {repr(typevar_to_hint)}...')
        hint = hint_reducer(
            hint=hint,  # pyright: ignore
            arg_kind=arg_kind,
            cls_stack=cls_stack,
            conf=conf,
            decor_meta=decor_meta,
            hints_overridden=hints_overridden,
            parent_hint_sane=parent_hint_sane,
            pith_name=pith_name,
            reductions_count=reductions_count,
            exception_prefix=exception_prefix,
        )
        # print(f'[_reduce_hint_uncached]...to uncached hint {repr(hint)}.')
    # Else, *NO* such callable was registered. Preserve this hint as is, you!

    # Return this possibly reduced hint.
    return hint


@callable_cached
def _reduce_hint_cached(
    hint: Hint, conf: BeartypeConf, exception_prefix: str) -> HintOrSane:
    '''
    Lower-level **context-free type hint** (i.e., type hint *not* contextually
    dependent on the kind of class, attribute, callable parameter, or callable
    return annotated by this hint) efficiently reduced (i.e., converted) from
    the passed higher-level context-free type hint if this hint is reducible
    *or* this hint as is otherwise (i.e., if this hint is irreducible).

    This reducer is memoized for efficiency. Thankfully, this reducer is
    responsible for reducing *most* (but not all) type hints.

    Parameters
    ----------
    hint : Hint
        Type hint to be possibly reduced.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    exception_prefix : str
        Substring prefixing exception messages raised by this function.

    Returns
    -------
    HintOrSane
        Either:

        * If this hint is ignorable, :data:`.HINT_IGNORABLE`.
        * Else if this unignorable hint is reducible to another hint, metadata
          encapsulating this reduction.
        * Else, this unignorable hint is irreducible. In this case, metadata
          encapsulating this hint unmodified.
    '''

    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise (e.g., if this hint is merely an isinstanceable class).
    hint_sign = get_hint_pep_sign_or_none(hint)

    # Callable reducing this hint if a callable reducing hints of this sign was
    # previously registered *OR* "None" otherwise (i.e., if *NO* such callable
    # was registered, in which case this hint is preserved as is).
    hint_reducer = HINT_SIGN_TO_REDUCE_HINT_CACHED_get(hint_sign)

    # If a callable reducing hints of this sign was previously registered,
    # reduce this hint to another hint via this callable.
    if hint_reducer is not None:
        # print(f'[_reduce_hint_cached] Reducing cached hint {repr(hint)}...')
        hint = hint_reducer(  # type: ignore[call-arg]
            hint=hint,  # pyright: ignore
            conf=conf,
            exception_prefix=exception_prefix,
        )
        # print(f'[_reduce_hint_cached] ...to cached hint {repr(hint)}.')
    # Else, *NO* such callable was registered. Preserve this hint as is, you!

    # Return this possibly reduced hint.
    return hint

# ....................{ PRIVATE ~ globals                  }....................
_REDUCTIONS_COUNT_MAX = 64
'''
Maximum number of total reductions internally performed by each call of the
:func:`reduce_hint` function.

This constant is a relatively arbitrary magic number selected so as to guard
against accidental infinite recursion between lower-level PEP-specific reducers
internally called by :func:`reduce_hint`.
'''


_REDUCE_HINT_CHILD_ARG_NAMES_UNSAFE = frozenset((
    # Applicable *ONLY* to root hints directly annotating callable parameters.
    'arg_kind',

    # Applicable *ONLY* to root hints directly annotating callable parameters
    # or returns.
    'decor_meta',
    'pith_name',
))
'''
Frozen set of the names of all **unsafe child type hint reducer keyword
parameters** (i.e., keyword parameters inapplicable to child type hints and thus
*not* safely passable from the higher-level :func:`.reduce_hint_child` to
lower-level :func:`.reduce_hint` reducer.
'''
