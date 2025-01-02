#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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
    TypeVarToHint,
)
from beartype._data.hint.datahinttyping import TypeStack
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.func.arg.utilfuncargiter import ArgKind
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from beartype._util.kind.map.utilmapfrozen import (
    FROZEN_DICT_EMPTY,
    FrozenDict,
)
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
    pith_name: Optional[str] = None,
    typevar_to_hint: TypeVarToHint = FROZEN_DICT_EMPTY,
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
    pith_name : Optional[str], optional
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.

        Defaults to :data:`None`.
    typevar_to_hint : TypeVarToHint, optional
        **Type variable lookup table** (i.e., immutable dictionary mapping from
        the :pep:`484`-compliant **type variables** (i.e.,
        :class:`typing.TypeVar` objects) originally parametrizing the origins of
        all transitive parent hints of this hint to the corresponding child
        hints subscripting these parent hints). Defaults to
        :data:`.FROZEN_DICT_EMPTY`.
    exception_prefix : str, optional
        Human-readable substring prefixing exception messages raised by this
        reducer. Defaults to the empty string.

    Returns
    -------
    HintOrHintSanifiedData
        Either:

        * If the passed hint is reducible, either:

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
    hint_prev: Hint = SENTINEL  # pyright: ignore

    # Current number of total reductions internally performed by this call,
    # guarding against accidental infinite recursion between lower-level
    # reducers called below.
    reductions_count = 0

    # ....................{ REDUCTION                      }....................
    # Repeatedly reduce this hint to increasingly irreducible hints until this
    # hint is no longer reducible.
    while True:
        # print(f'[reduce_hint] Reducing {repr(hint)} with type variable lookup table {repr(typevar_to_hint)}...')

        # This possibly contextual hint inefficiently reduced to another hint.
        #
        # Note that we intentionally reduce lower-level contextual hints
        # *BEFORE* reducing higher-level context-free hints. In theory, order of
        # reduction *SHOULD* be insignificant; in practice, we suspect
        # unforeseen and unpredictable interactions between these two
        # reductions. To reduce the likelihood of fire-breathing dragons here,
        # we reduce lower-level hints first.
        hint = _reduce_hint_uncached(
            hint=hint,
            arg_kind=arg_kind,
            cls_stack=cls_stack,
            conf=conf,
            decor_meta=decor_meta,
            pith_name=pith_name,
            typevar_to_hint=typevar_to_hint,
            exception_prefix=exception_prefix,
        )

        # Sane hint reduced from this possibly insane hint if reducing this hint
        # did not generate supplementary metadata *OR* that metadata otherwise
        # (i.e., if reducing this hint generated supplementary metadata).
        hint_or_sane = _reduce_hint_cached(hint, conf, exception_prefix)

        # This possibly context-free hint efficiently reduced to another hint
        # and the resulting type variable lookup table.
        hint, typevar_to_hint = unpack_hint_or_sane(
            hint_or_sane=hint_or_sane,
            typevar_to_hint=typevar_to_hint,
        )
        # print(f'[reduce_hint] Reduced to {repr(hint)} and type variable lookup table {repr(typevar_to_hint)}.')

        # If the current and previously reduced instances of this hint are
        # identical, the above reductions preserved this hint as is rather than
        # reducing this hint, implying this hint to now be irreducible. In this
        # case, halt reducing.
        if hint is hint_prev:
            break
        # Else, the current and previously reduced instances of this hint
        # differ, implying this hint to still be reducible. In this case,
        # continue reducing.

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
                f'{repr(hint_prev)} and {repr(hint)}. Please open a new issue '
                f'on our friendly issue tracker providing this full traceback:\n'
                f'\t{URL_ISSUES}\n'
                f'Beartype thanks you for your noble (yet ultimately tragic) '
                f'sacrifice.'
            )
        # Else, the current number of total reductions internally performed
        # by this call is still less than the maximum. In this case, continue.

        # Previously reduced instance of this hint.
        hint_prev = hint

    # ....................{ RETURN                         }....................
    # Either this possibly reduced hint *OR* metadata describing this hint,
    # defined as...
    hint_or_sane = (
        # If this reduction maps *NO* type variables, *NO* supplementary
        # metadata describes this reduction. In this case, this hint alone.
        hint
        if not typevar_to_hint else
        # Else, this reduction maps one or more type variables. In this case,
        # metadata describing both this hint and this mapping.
        HintSanifiedData(hint=hint, typevar_to_hint=typevar_to_hint)
    )

    # Return this possibly reduced hint.
    return hint_or_sane


def reduce_hint_child(**kwargs) -> HintOrHintSanifiedData:
    '''
    Lower-level child hint reduced (i.e., converted) from the passed
    higher-level child hint if this child hint is reducible *or* this child hint
    as is otherwise (i.e., if this child hint is irreducible).

    This reducer is a convenience wrapper for the more general-purpose
    :func:`.reduce_hint` reducer, simplifying calls to that reducer when passed
    child hints. Specifically, this reducer silently ignores all passed keyword
    parameters inapplicable to child hints. This includes:

    * ``arg_kind``, applicable *only* to root hints directly annotating callable
       parameters.
    * ``decor_meta``, applicable *only* to root hints directly annotating
      callable parameters or returns.
    * ``pith_name``, applicable *only* to root hints directly annotating
      callable parameters or returns.
    '''

    # Remove all passed keyword parameters inapplicable to child hints *BEFORE*
    # reducing this child hint.
    #
    # Note that this is the standard idiom for efficiently removing dictionary
    # key-value pairs where this key is *NOT* guaranteed to exist in this
    # dictionary. Simplicity and speed supercedes readability, sadly.
    kwargs.pop('arg_kind', None)
    kwargs.pop('decor_meta', None)
    kwargs.pop('pith_name', None)

    # Return this child hint possibly reduced to a lower-level hint.
    return reduce_hint(**kwargs)

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

    # Attempt to...
    try:
        # If this beartype configuration coercively overrides this source hint
        # with a corresponding target hint, do so now *BEFORE* attempting to
        # reduce this hint via standard reduction heuristics. User preferences
        # take preference over standards.
        #
        # Note that this one-liner looks ridiculous, but actually works. More
        # importantly, this is the fastest way to accomplish this. Flex!
        # print(f'Overriding hint {repr(hint)} via {repr(conf.hint_overrides)}...')
        hint = conf.hint_overrides.get(hint, hint)
    # If doing so raises a "TypeError", this source hint is unhashable and thus
    # inapplicable for hint overriding. In this case, silently ignore this hint.
    except TypeError:
        pass

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
    pith_name: Optional[str],
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
    pith_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.
    typevar_to_hint : TypeVarToHint, optional
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
            pith_name=pith_name,
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
