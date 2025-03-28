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
    is_hint_recursive,
    make_hint_sane_recursable,
)
from beartype._conf.confcls import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.datahinttyping import (
    DictStrToAny,
    TypeStack,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_BARE_IGNORABLE)
from beartype._util.func.arg.utilfuncargiter import ArgKind
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_sign_or_none,
)
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
    hint_parent_sane: Optional[HintSane] = None,
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
    hint_parent_sane : Optional[HintSane]
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
    # Validate passed parameters *AFTER* establishing defaults above.
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'
    assert isinstance(hint_parent_sane, NoneTypeOr[HintSane]), (
        f'{repr(hint_parent_sane)} neither sanified hint metadata nor "None".')
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

        # ....................{ PHASE ~ override           }....................
        # Attempt to reduce this hint to another hint configured by a
        # user-defined hint override *BEFORE* attempting standard reduction.
        # User preference takes precedence over standard precedent.

        #FIXME: Once we drop support for Python <= 3.11, "BeartypeHintOverrides"
        #can and should be internally implemented as PEP 695-compliant
        #unsubscripted type aliases. Note that, even after doing so, the logic
        #below will probably still need to be preserved as is.

        # Attempt to...
        #
        # Note that the is_object_hashable() tester is internally implemented
        # with the same Easier to Ask for Permission than Forgiveness
        # (EAFP)-based "try-except" block and is thus equally inefficient. In
        # fact, the current approach avoids an extraneous call to that tester
        # and is thus marginally faster. (Emphasis on "marginally.")
        try:
            # If this hint is *NOT* recursive, this hint *CANNOT* have already
            # been overridden by a previously performed reduction. Why? Because
            # an overridden hint revisited by the current breadth-first search
            # (BFS) would by definition by recursive. In this case...
            #
            # Note this tester raises "TypeError" when this hint is unhashable.
            if not is_hint_recursive(
                hint=hint, hint_parent_sane=hint_parent_sane):
                # User-defined hint overriding this hint if this beartype
                # configuration overrides this hint *OR* the sentinel otherwise
                # (i.e., if this hist is *NOT* overridden).
                # print(f'Overriding hint {repr(hint)} via {repr(conf.hint_overrides)}...')
                hint_overridden = conf_hint_overrides_get(hint_curr, SENTINEL)

                # If this hint is overridden...
                if hint_overridden is not SENTINEL:
                    # Sanified metadata guarding this hint against infinite
                    # recursion, recording this hint as already having been
                    # overridden *BEFORE* reducing and thus forgetting this
                    # hint.
                    #
                    # Note that this intentionally replaces the sanified type
                    # hint metadata of the parent hint of this hint by the
                    # sanified type hint metadata of this hint itself. Doing so
                    # ensures that the next reducer passed the
                    # "hint_parent_sane" parameter preserves this metadata
                    # during its reduction. Since the most recent reducer call
                    # received the prior "hint_parent_sane" parameter, that
                    # reducer has already safely preserved the parent metadata
                    # by compositing that metadata into this "hint_or_sane_curr"
                    # metadata that that reducer returned. Srsly.
                    hint_parent_sane = make_hint_sane_recursable(
                        hint=hint_overridden, hint_parent_sane=hint_parent_sane)

                    # Reduce this hint to this user-defined hint override.
                    hint_curr = hint_parent_sane.hint
                # Else, this hint is *NOT* overridden. In this case, preserve
                # this hint as is.
            # Else, this hint is recursive. In this case, avoid overriding this
            # hint yet again. Doing so would (almost certainly) provoke infinite
            # recursion (e.g., overriding "float" with "int | float").
            #
            # Certainly, various approaches to type-checking recursive hints
            # exists. @beartype currently embraces the easiest, fastest, and
            # laziest approach: just ignore all recursion! \o/
        # If doing so raises a "TypeError", this hint is unhashable and thus
        # inapplicable for hint overriding. In this case, ignore this hint.
        except TypeError:
            pass

        # ....................{ PHASE ~ shallow            }....................
        # Attempt to reduce this hint with trivial zero-cost tests *BEFORE*
        # spending scarce resources on non-trivial full-cost tests below.
        # These tests are shallow and thus exhibit amortized O(1) constant time
        # complexity with negligible constants.

        # If this hint is the root "object" superclass, this hint is trivially
        # shallowly ignorable. Why? Because this type is the transitive
        # superclass of all classes. Attributes annotated as "object"
        # unconditionally match *ALL* objects under isinstance()-based type
        # covariance and thus semantically reduce to unannotated attributes.
        # Reduce this hint to the ignorable "HINT_IGNORABLE" singleton.
        if hint_curr is object:
            return HINT_IGNORABLE
        # Else, this hint is *NOT* the root "object" superclass.

        # Sign uniquely identifying this hint if this hint is PEP-compliant *OR*
        # "None" otherwise (e.g., if this hint is PEP-noncompliant).
        hint_sign = get_hint_pep_sign_or_none(hint_curr)
        # print(f'reduce_hint() hint {hint} sign {hint_sign}')

        # If this hint is PEP-noncompliant...
        #
        # Note that this logic could also be handled in a reduce_hint_nonpep()
        # reducer mapped to the "None" sign, whose body is the body of this "if"
        # conditional. Indeed, the prior implementation of this logic did just
        # that. Technically, that approach did work. Pragmatically, that
        # approach was obfuscatory, obtuse, and ultimately unmaintainable. This
        # approach is equally efficient but *CONSIDERABLY* more sensible.
        if hint_sign is None:
            # If this hint is unsupported by @beartype, raise an exception.
            die_unless_hint(hint=hint_curr, exception_prefix=exception_prefix)
            # Else, this hint is supported by @beartype.

            # Return this hint as is. By definition, PEP-noncompliant hints are
            # irreducible. If this hint was instead reducible, the
            # get_hint_pep_sign_or_none() getter called above would have instead
            # returned a unique sign identifying this hint (rather than "None").
            return hint_curr
        # Else, this hint is PEP-compliant.
        #
        # If...
        elif (
            # This hint is unconditionally ignorable when unsubscripted *AND*...
            hint_sign in HINT_SIGNS_BARE_IGNORABLE and
            # This hint is unsubscripted...
            #
            # Note that calling this getter is slower than testing membership in
            # the above set. Ergo, this getter is intentionally called *AFTER*
            # the prior faster test.
            not get_hint_pep_args(hint_curr)
        # Then this hint is ignorable. Reduce this hint to the ignorable
        # "HINT_IGNORABLE" singleton.
        ):
            return HINT_IGNORABLE

        #FIXME: Excise the now-obsolete "HINTS_REPR_IGNORABLE_SHALLOW" set
        #everywhere from the codebase, please.
        #FIXME: Preserved for temporary posterity. Excise when feasible, please!
        # from beartype._data.hint.pep.datapeprepr import HINTS_REPR_IGNORABLE_SHALLOW
        # from beartype._util.hint.utilhintget import get_hint_repr
        # # Machine-readable representation of this hint.
        # hint_repr = get_hint_repr(hint_curr)
        #
        # # If this hint is shallowly ignorable, reduce this hint to the ignorable
        # # "HINT_IGNORABLE" singleton.
        # #
        # # Note that this reduction efficiently applies to multiple signs
        # # concurrently, including the "None", "HintSignOptional", and
        # # "HintSignUnion". Ergo, this reduction *CANNOT* be trivially
        # # implemented as a standard reduction assigned a single sign.
        # if hint_repr in HINTS_REPR_IGNORABLE_SHALLOW:
        #     return HINT_IGNORABLE
        # # Else, this hint is *NOT* shallowly ignorable.

        # ....................{ PHASE ~ deep               }....................
        # Attempt to deeply reduce this hint with a context-free reduction
        # *BEFORE* deeply reducing this hint with a contextual reduction. Due to
        # *NOT* depending on contextual state, context-free reductions are
        # easily memoizable and thus faster than contextual reductions.

        # Context-free reducer reducing this hint if such a reducer reduces
        # hints of this sign *OR* "None" otherwise.
        hint_reducer_cached = HINT_SIGN_TO_REDUCE_HINT_CACHED_get(hint_sign)

        # If a context-free reducer reduces hints of this sign...
        if hint_reducer_cached is not None:
            #FIXME: [SPEED] *ALL* of these reducers now need to be manually
            #memoized with the @callable_cached decorator. Trivial, of course.
            #Just unctuous. We sigh. *sigh*
            #FIXME: [SPEED] Is there any point to passing the "exception_prefix"
            #parameter? Possibly. Not sure. Isn't this parameter a constant? No?
            #Does it actually vary with context? Can't recall. Investigate up!
            #FIXME: [SPEED] Is passing the "conf" parameter here worthwhile? How
            #many cached reductions actually benefit from receiving a "conf"? If
            #the answer is "Hardly any, bro.", then:
            #* Those cached reductions that actually benefit from receiving a
            #  "conf" should just be refactored into uncached reductions.
            #* We should stop passing "conf" altogether below. Doing so improves
            #  caching efficiency for the general case, which is all that
            #  matters.

            # print(f'[_reduce_hint_cached] Reducing cached hint {repr(hint)}...')

            # Reduce this hint by calling this reducer.
            #
            # Note that parameters are intentionally passed positionally to this
            # memoized callable, which prohibits keyword parameters.
            hint_or_sane_curr = hint_reducer_cached(
                hint_curr, conf, exception_prefix)
            # print(f'[_reduce_hint_cached] ...to cached hint {repr(hint)}.')
        # Else, *NO* context-free reducer reduces hints of this sign. In this
        # case...
        else:
            # Contextual reducer reducing this hint if such a reducer reduces
            # hints of this sign *OR* "None" otherwise.
            hint_reducer_uncached = HINT_SIGN_TO_REDUCE_HINT_UNCACHED_get(
                hint_sign)

            # If a contextual reducer reduces hints of this sign...
            if hint_reducer_uncached is not None:  # type: ignore[call-arg]
                # print(f'[_reduce_hint_uncached] Reducing uncached hint {repr(hint)}...')
                # print(f'...with type variable lookup table {repr(typevar_to_hint)}...')

                # Reduce this hint by calling this reducer.
                hint_or_sane_curr = hint_reducer_uncached(
                    hint=hint_curr,  # pyright: ignore
                    arg_kind=arg_kind,
                    cls_stack=cls_stack,
                    conf=conf,
                    decor_meta=decor_meta,
                    hint_parent_sane=hint_parent_sane,
                    pith_name=pith_name,
                    reductions_count=reductions_count,
                    exception_prefix=exception_prefix,
                )
            # Else, *NO* contextual reducer reduces hints of this sign. In this
            # case, preserve this hint as is.
            else:
                hint_or_sane_curr = hint_curr
        # print(f'[_reduce_hint_uncached]...to uncached hint {repr(hint)}.')

        # If this hint is ignorable, halt reducing.
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
        #
        # If reducing this hint generated supplementary metadata...
        elif isinstance(hint_or_sane_curr, HintSane):
            # Replace the sanified type hint metadata of the parent hint of this
            # hint by the sanified type hint metadata of this hint itself. Doing
            # so ensures that the next reducer passed the "hint_parent_sane"
            # parameter preserves this metadata during its reduction. Since the
            # most recent reducer call received the prior "hint_parent_sane"
            # parameter, that reducer has already safely preserved the parent
            # metadata by compositing that metadata into this
            # "hint_or_sane_curr" metadata that that reducer returned. Srsly.
            hint_parent_sane = hint_or_sane_curr

            # Extract the currently reduced hint from this metadata.
            hint_curr = hint_or_sane_curr.hint
        # Else, reducing this hint did *NOT* generate supplementary metadata,
        # implying "hint_or_sane_curr" to be the currently reduced hint. In this
        # case, record this currently reduced hint.
        else:
            hint_curr = hint_or_sane_curr

        # ....................{ PHASE ~ next               }....................
        # Prepare for the next iterative reduction of this "while" loop.

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
    # have been reduced to the "HINT_IGNORABLE" singleton. In this case...
    if not isinstance(hint_or_sane_curr, HintSane):
        # Encapsulate this hint with such metadata, defined as either...
        hint_or_sane_curr = (
            # If this hint has *NO* parent, this is a root hint. In this case,
            # the trivial metadata shallowly encapsulating this root hint;
            HintSane(hint)
            if hint_parent_sane is None else
            # Else, this hint has a parent. In this case, the non-trivial
            # metadata deeply encapsulating both this non-root hint *AND* all
            # metadata already associated with this parent hint.
            hint_parent_sane.permute_sane(hint=hint_or_sane_curr)
        )
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
