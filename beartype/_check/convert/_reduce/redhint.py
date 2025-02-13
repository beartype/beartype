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
from beartype.typing import (
    Any,
    Optional,
)
from beartype._check.convert._reduce._redmap import (
    HINT_SIGN_TO_REDUCE_HINT_CACHED_get,
    HINT_SIGN_TO_REDUCE_HINT_UNCACHED_get,
)
from beartype._check.metadata.metadecor import BeartypeDecorMeta
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    HintSanifiedData,
    unpack_hint_or_sane,
)
from beartype._conf.confcls import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.hint.datahintpep import (
    Hint,
    SetHints,
    TypeVarToHint,
)
from beartype._data.hint.datahinttyping import (
    DictStrToAny,
    TypeStack,
)
from beartype._data.hint.pep.datapeprepr import HINTS_REPR_IGNORABLE_SHALLOW
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.func.arg.utilfuncargiter import ArgKind
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from beartype._util.hint.utilhintget import get_hint_repr
from beartype._util.kind.map.utilmapfrozen import FrozenDict
from beartype._util.kind.map.utilmapset import remove_mapping_keys
from beartype._util.utilobject import SENTINEL

# ....................{ REDUCERS                           }....................
def reduce_hint_child(
    hint: Hint, kwargs: DictStrToAny) -> HintOrHintSanifiedData:
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
    HintOrHintSanifiedData
        Either:

        * If this hint is reducible, either:

          * If reducing this hint to a lower-level hint generates supplementary
            metadata, that metadata including that lower-level hint.
          * Else, that lower-level hint alone.

        * Else, this hint is irreducible. In this case, this hint unmodified.
    '''

    # Remove all unsafe keyword parameters (i.e., parameters that are
    # inapplicable to child hints and thus *NOT* safely passable to the
    # subsequently called reduce_hint() function) from this dictionary.
    remove_mapping_keys(kwargs, _REDUCE_HINT_CHILD_ARG_NAMES_UNSAFE)

    # Return this child hint possibly reduced to a lower-level hint.
    return reduce_hint(hint=hint, **kwargs)


def reduce_hint(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    arg_kind: Optional[ArgKind] = None,
    cls_stack: TypeStack = None,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    decor_meta: Optional[BeartypeDecorMeta] = None,
    hints_overridden: SetHints = None,  # type: ignore[assignment]
    pith_name: Optional[str] = None,
    reductions_count: int = 0,
    typevar_to_hint: TypeVarToHint = FROZENDICT_EMPTY,
    exception_prefix: str = '',
) -> HintOrHintSanifiedData:
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
    pith_name : Optional[str], optional
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
    typevar_to_hint : TypeVarToHint, optional
        **Type variable lookup table** (i.e., immutable dictionary mapping from
        the :pep:`484`-compliant **type variables** (i.e.,
        :class:`typing.TypeVar` objects) originally parametrizing the origins of
        all transitive parent hints of this hint to the corresponding child
        hints subscripting these parent hints). Defaults to
        :data:`.FROZENDICT_EMPTY`.
    exception_prefix : str, optional
        Human-readable substring prefixing exception messages raised by this
        reducer. Defaults to the empty string.

    Returns
    -------
    HintOrHintSanifiedData
        Either:

        * If this hint is reducible, either:

          * If reducing this hint to a lower-level hint generates supplementary
            metadata, that metadata including that lower-level hint.
          * Else, that lower-level hint alone.

        * Else, this hint is irreducible. In this case, this hint unmodified.

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
    assert isinstance(reductions_count, int), (
        f'{repr(reductions_count)} not integer.')
    assert isinstance(typevar_to_hint, FrozenDict), (
        f'{repr(typevar_to_hint)} not frozen dictionary.')

    # ....................{ LOCALS                         }....................
    # Original unreduced hint passed to this reducer, preserved so as to be
    # embedded in human-readable exception messages.
    hint_old = hint

    # Previously reduced instance of this hint, initialized to the sentinel to
    # guarantee that the passed hint is *NEVER* equal to the previously reduced
    # instance of this hint unless actually reduced below. This is necessary, as
    # "None" is a valid type hint reduced to "type(None)" below.
    hint_or_sane_prev: HintOrHintSanifiedData = SENTINEL  # pyright: ignore

    # BeartypeHintOverrides.get() method bound to the user-defined
    # "hint_overrides" dictionary of this beartype configuration, localized as a
    # negligible efficiency gain.
    conf_hint_overrides_get = conf.hint_overrides.get

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
        # Attempt to shallowly reduce this hint to the ignorable "typing.Any"
        # singleton *BEFORE* attempting reductions that deeply inspect the
        # contents of this hint. Why? Several reasons:
        # * This shallow reduction is an O(1) constant-time operation with
        #   negligible constants and thus *INCREDIBLY* fast.
        # * Okay. That's all I've got. It's late, people. I exhaustedly sigh.

        # Machine-readable representation of this hint.
        hint_repr = get_hint_repr(hint)

        #FIXME: Preserved for posterity, as this seems generically useful. *sigh*
        # # If this hint is beartype-blacklisted (i.e., defined in a third-party
        # # package or module that is hostile to runtime type-checking), return true.
        # # print(f'Testing hint {repr(hint)} third-party blacklisting...')
        # if is_object_module_thirdparty_blacklisted(hint):
        #     # print('Blacklisted!')
        #     return True
        # # Else, this hint is *NOT* beartype-blacklisted.

        # If this hint is shallowly ignorable, reduce this hint to the ignorable
        # "typing.Any" singleton.
        #
        # Note that this reduction efficiently applies to multiple signs
        # concurrently, including the "None", "HintSignOptional", and
        # "HintSignUnion". Ergo, this reduction *CANNOT* be trivially
        # implemented as a standard reduction assigned a single sign.
        if hint_repr in HINTS_REPR_IGNORABLE_SHALLOW:
            return Any  # pyright: ignore
        # Else, this hint is *NOT* shallowly ignorable.

        # ....................{ PHASE ~ override           }....................
        # Attempt to reduce this hint to another hint configured by a
        # user-defined hint override *BEFORE* attempting standard reduction.
        # User preference takes precedence over standard precedent.

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
            if hint not in hints_overridden:
                # User-defined hint overriding this hint if this beartype
                # configuration overrides this hint *OR* the sentinel placeholder
                # otherwise (i.e., if this hist is *NOT* overridden).
                # print(f'Overriding hint {repr(hint)} via {repr(conf.hint_overrides)}...')
                hint_reduced = conf_hint_overrides_get(hint, SENTINEL)

                # If this hint was overridden...
                if hint_reduced is not SENTINEL:
                    # Record this hint as already having been overridden
                    # *BEFORE* reducing (and thus obliterating) this hint.
                    hints_overridden.add(hint)

                    # Reduce this hint to this user-defined hint override.
                    hint = hint_reduced
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
        hint = _reduce_hint_uncached(
            hint=hint,
            arg_kind=arg_kind,
            cls_stack=cls_stack,
            conf=conf,
            decor_meta=decor_meta,
            hints_overridden=hints_overridden,
            pith_name=pith_name,
            reductions_count=reductions_count,
            typevar_to_hint=typevar_to_hint,
            exception_prefix=exception_prefix,
        )

        # If this hint reduces to the PEP 484-compliant "typing.Any" singleton,
        # this hint is ignorable. In this case, halt reducing.
        #
        # Note that this is an optional short-circuiting optimization avoiding
        # multiple repetitious reductions for each ignorable hint.
        if hint is Any:
            return Any
        # Else, this hint is currently unignorable. Continue reducing.

        # ....................{ PHASE ~ cached             }....................
        # Sane hint reduced from this possibly insane hint if reducing this hint
        # did not generate supplementary metadata *OR* that metadata otherwise
        # (i.e., if reducing this hint generated supplementary metadata).
        hint_or_sane = _reduce_hint_cached(hint, conf, exception_prefix)

        # If this hint reduces to the PEP 484-compliant "typing.Any" singleton,
        # this hint is ignorable. In this case, halt reducing.
        #
        # Note that, unlike the similar test above, this test is required rather
        # than merely an optimization.
        if hint_or_sane is Any:
            return Any  # pyright: ignore
        # Else, this hint is currently unignorable. Continue reducing.
        #
        # If the current and previously reduced instances of this hint are
        # identical, the above reductions all preserved this hint as is rather
        # than reducing this hint. This implies this hint to now be irreducible.
        # Halt reducing.
        elif hint_or_sane is hint_or_sane_prev:
            break
        # Else, the current and previously reduced instances of this hint
        # differ, implying this hint to still be reducible. Continue reducing.

        # This possibly context-free hint efficiently reduced to another hint
        # and the resulting type variable lookup table.
        hint, typevar_to_hint = unpack_hint_or_sane(
            hint_or_sane=hint_or_sane, typevar_to_hint=typevar_to_hint)
        # print(f'[reduce_hint] Reduced to {repr(hint)} and type variable lookup table {repr(typevar_to_hint)}.')

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
                f'{repr(hint_or_sane_prev)} and {repr(hint)}. Please open a new issue '
                f'on our friendly issue tracker providing this full traceback:\n'
                f'\t{URL_ISSUES}\n'
                f'Beartype thanks you for your noble (yet ultimately tragic) '
                f'sacrifice.'
            )
        # Else, the current number of total reductions internally performed
        # by this call is still less than the maximum. In this case, continue.

        # Previously reduced instance of this hint.
        hint_or_sane_prev = hint

    # ....................{ RETURN                         }....................
    # Either this possibly reduced hint *OR* metadata describing this hint,
    # defined as either...
    hint_or_sane = (
        # If either...
        #
        # Then *NO* metadata describes this reduction. In this case, ignore this
        # metadata by reducing to this hint alone.
        hint
        if (
            # This hint reduces to the PEP 484-compliant "typing.Any" singleton,
            # this hint is ignorable. Since this hint is ignorable, any
            # extraneous metadata associated with this hint (e.g., type variable
            # lookup table) is also ignorable. We intentionally ignore this
            # metadata by reducing this hint to simply "typing.Any",
            # trivializing detection of ignorable hints throughout the codebase;
            hint is Any or
            # This hint maps *NO* type variables.
            not typevar_to_hint
        ) else
        # Else, this reduction maps one or more type variables. In this case,
        # metadata describing both this hint and this mapping.
        HintSanifiedData(hint=hint, typevar_to_hint=typevar_to_hint)
    )

    # Return this possibly reduced hint.
    return hint_or_sane

# ....................{ PRIVATE ~ reducers                 }....................
@callable_cached
def _reduce_hint_cached(
    hint: Hint,
    conf: BeartypeConf,
    exception_prefix: str,
) -> HintOrHintSanifiedData:
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
    HintOrHintSanifiedData
        Either:

        * If the passed hint is reducible, either:

          * If reducing this hint to a lower-level hint generates supplementary
            metadata, that metadata including that lower-level hint.
          * Else, that lower-level hint alone.

        * Else, this hint is irreducible. In this case, this hint unmodified.
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
            hint=hint,  # pyright: ignore[reportGeneralTypeIssues]
            conf=conf,
            exception_prefix=exception_prefix,
        )
        # print(f'[_reduce_hint_cached] ...to cached hint {repr(hint)}.')
    # Else, *NO* such callable was registered. Preserve this hint as is, you!

    # Return this possibly reduced hint.
    return hint


def _reduce_hint_uncached(
    hint: Hint,
    arg_kind: Optional[ArgKind],
    cls_stack: TypeStack,
    conf: BeartypeConf,
    decor_meta: Optional[BeartypeDecorMeta],
    hints_overridden: SetHints,
    pith_name: Optional[str],
    reductions_count: int,
    typevar_to_hint: TypeVarToHint,
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
    typevar_to_hint : TypeVarToHint
        **Type variable lookup table** (i.e., immutable dictionary mapping from
        the :pep:`484`-compliant **type variables** (i.e.,
        :class:`typing.TypeVar` objects) originally parametrizing the origins of
        all transitive parent hints of this hint to the corresponding child
        hints subscripting these parent hints).
    exception_prefix : str
        Human-readable substring prefixing exception messages raised by this
        reducer.

    Returns
    -------
    Hint
        Either:

        * If the passed hint is reducible, another hint reduced from this hint.
        * Else, this hint as is unmodified.
    '''

    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise (e.g., if this hint is merely an isinstanceable class).
    hint_sign = get_hint_pep_sign_or_none(hint)
    # print(f'_reduce_hint_uncached() hint_sign: {hint_sign}')

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
            pith_name=pith_name,
            reductions_count=reductions_count,
            typevar_to_hint=typevar_to_hint,
            exception_prefix=exception_prefix,
        )
        # print(f'[_reduce_hint_uncached]...to uncached hint {repr(hint)}.')
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
