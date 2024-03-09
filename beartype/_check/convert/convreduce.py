#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint reducers** (i.e., low-level callables
*temporarily* converting type hints from one format into another, either
losslessly or in a lossy manner).

Type hint reductions imposed by this submodule are purely internal to
:mod:`beartype` itself and thus transient in nature. These reductions are *not*
permanently applied to the ``__annotations__`` dunder dictionaries of the
classes and callables annotated by these type hints.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    # Callable,
    Dict,
    Optional,
)
from beartype._conf.confcls import BeartypeConf
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAbstractSet,
    HintSignAnnotated,
    HintSignAsyncContextManager,
    HintSignAsyncGenerator,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
    HintSignAwaitable,
    HintSignByteString,
    HintSignCallable,
    HintSignChainMap,
    HintSignCollection,
    HintSignContainer,
    HintSignContextManager,
    HintSignCoroutine,
    HintSignCounter,
    HintSignDefaultDict,
    HintSignDeque,
    HintSignDict,
    HintSignFinal,
    HintSignFrozenSet,
    HintSignGenerator,
    HintSignGeneric,
    HintSignHashable,
    HintSignItemsView,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    HintSignLiteralString,
    HintSignMappingView,
    HintSignMapping,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    HintSignNewType,
    HintSignNone,
    HintSignNumpyArray,
    HintSignOrderedDict,
    HintSignPanderaAny,
    HintSignPattern,
    HintSignPep557DataclassInitVar,
    HintSignPep585BuiltinSubscriptedUnknown,
    HintSignPep695TypeAlias,
    HintSignReversible,
    HintSignSelf,
    HintSignSequence,
    HintSignSet,
    HintSignSized,
    HintSignTuple,
    HintSignType,
    HintSignTypeAlias,
    HintSignTypeGuard,
    HintSignTypeVar,
    HintSignTypedDict,
    HintSignValuesView,
)
from beartype._data.hint.datahinttyping import TypeStack
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.nonpep.mod.utilmodnumpy import (
    reduce_hint_numpy_ndarray)
from beartype._util.hint.nonpep.mod.utilmodpandera import (
    reduce_hint_pandera)
from beartype._util.hint.pep.proposal.pep484.utilpep484 import (
    reduce_hint_pep484_deprecated,
    reduce_hint_pep484_none,
)
from beartype._util.hint.pep.proposal.pep484.utilpep484generic import (
    reduce_hint_pep484_generic)
from beartype._util.hint.pep.proposal.pep484.utilpep484newtype import (
    reduce_hint_pep484_newtype)
from beartype._util.hint.pep.proposal.pep484.utilpep484typevar import (
    reduce_hint_pep484_typevar)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585type import (
    reduce_hint_pep484585_type)
from beartype._util.hint.pep.proposal.utilpep557 import (
    reduce_hint_pep557_initvar)
from beartype._util.hint.pep.proposal.utilpep585 import (
    reduce_hint_pep585_builtin_subscripted_unknown)
from beartype._util.hint.pep.proposal.utilpep589 import reduce_hint_pep589
from beartype._util.hint.pep.proposal.utilpep591 import reduce_hint_pep591
from beartype._util.hint.pep.proposal.utilpep593 import reduce_hint_pep593
from beartype._util.hint.pep.proposal.utilpep613 import reduce_hint_pep613
from beartype._util.hint.pep.proposal.utilpep647 import reduce_hint_pep647
from beartype._util.hint.pep.proposal.utilpep673 import reduce_hint_pep673
from beartype._util.hint.pep.proposal.utilpep675 import reduce_hint_pep675
from beartype._util.hint.pep.proposal.utilpep695 import reduce_hint_pep695
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from beartype._util.hint.pep.utilpepreduce import reduce_hint_pep_unsigned
from beartype._util.utilobject import SENTINEL
from collections.abc import Callable

# ....................{ REDUCERS                           }....................
def reduce_hint(
    # Mandatory parameters.
    hint: Any,
    conf: BeartypeConf,

    # Optional parameters.
    cls_stack: TypeStack = None,
    pith_name: Optional[str] = None,
    exception_prefix: str = '',
) -> object:
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
    hint : Any
        Type hint to be possibly reduced.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.
    pith_name : Optional[str], optional
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.

        Defaults to :data:`None`.
    exception_prefix : str, optional
        Substring prefixing exception messages raised by this function. Defaults
        to the empty string.

    Returns
    -------
    object
        Either:

        * If the passed hint is reducible, another hint reduced from this hint.
        * Else, this hint as is unmodified.
    '''

    # Previously reduced instance of this hint, initialized to the sentinel to
    # guarantee that the passed hint is *NEVER* equal to the previously reduced
    # instance of this hint unless actually reduced below. This is necessary, as
    # "None" is a valid type hint reduced to "type(None)" below.
    hint_prev: object = SENTINEL

    # Repeatedly reduce this hint to increasingly irreducible hints until this
    # hint is no longer reducible.
    while True:
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
            conf=conf,
            pith_name=pith_name,
            cls_stack=cls_stack,
            exception_prefix=exception_prefix,
        )

        # This possibly context-free hint efficiently reduced to another hint.
        hint = _reduce_hint_cached(hint, conf, exception_prefix)

        # If the current and previously reduced instances of this hint are
        # identical, the above reductions preserved this hint as is rather than
        # reducing this hint, implying this hint to irreducible. In this case,
        # stop reducing.
        if hint is hint_prev:
            break
        # Else, the current and previously reduced instances of this hint
        # differ, implying this hint to still be reducible. In this case,
        # continue reducing.

        # Previously reduced instance of this hint.
        hint_prev = hint

    # Return this possibly reduced hint.
    return hint

# ....................{ PRIVATE ~ reducers                 }....................
def _reduce_hint_uncached(
    hint: Any,
    conf: BeartypeConf,
    cls_stack: TypeStack,
    pith_name: Optional[str],
    exception_prefix: str,
) -> object:
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
    hint : Any
        Type hint to be possibly reduced.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    cls_stack : TypeStack
        **Type stack** (i.e., either tuple of zero or more arbitrary types *or*
        :data:`None`). See also the :func:`.beartype_object` decorator.
    pith_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.
    exception_prefix : str
        Substring prefixing exception messages raised by this function.

    Returns
    -------
    object
        Either:

        * If the passed hint is reducible, another hint reduced from this hint.
        * Else, this hint as is unmodified.
    '''

    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise (e.g., if this hint is merely an isinstanceable class).
    hint_sign = get_hint_pep_sign_or_none(hint)

    # Callable reducing this hint if a callable reducing hints of this sign was
    # previously registered *OR* "None" otherwise (i.e., if *NO* such callable
    # was registered, in which case this hint is preserved as is).
    hint_reducer = _HINT_SIGN_TO_REDUCE_HINT_UNCACHED.get(hint_sign)

    # If a callable reducing hints of this sign was previously registered,
    # reduce this hint to another hint via this callable.
    if hint_reducer is not None:  # type: ignore[call-arg]
        # print(f'Reducing hint {repr(hint)} to...')
        hint = hint_reducer(
            hint=hint,  # pyright: ignore[reportGeneralTypeIssues]
            conf=conf,
            cls_stack=cls_stack,
            pith_name=pith_name,
            exception_prefix=exception_prefix,
        )
        # print(f'...{repr(hint)}.')
    # Else, *NO* such callable was registered. Preserve this hint as is, you!

    # Return this possibly reduced hint.
    return hint


@callable_cached
def _reduce_hint_cached(
    hint: Any,
    conf: BeartypeConf,
    exception_prefix: str,
) -> object:
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
    hint : Any
        Type hint to be possibly reduced.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    exception_prefix : str
        Substring prefixing exception messages raised by this function.

    Returns
    -------
    object
        Either:

        * If the passed hint is reducible, another hint reduced from this hint.
        * Else, this hint as is unmodified.
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
    hint_reducer = _HINT_SIGN_TO_REDUCE_HINT_CACHED.get(hint_sign)

    # If a callable reducing hints of this sign was previously registered,
    # reduce this hint to another hint via this callable.
    if hint_reducer is not None:
        hint = hint_reducer(  # type: ignore[call-arg]
            hint=hint,  # pyright: ignore[reportGeneralTypeIssues]
            conf=conf,
            exception_prefix=exception_prefix,
        )
    # Else, *NO* such callable was registered. Preserve this hint as is, you!

    # Return this possibly reduced hint.
    return hint

# ....................{ PRIVATE ~ hints                    }....................
# Note that these type hints would ideally be defined with the mypy-specific
# "callback protocol" pseudostandard, documented here:
#     https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
#
# Doing so would enable static type-checkers to type-check that the values of
# these dictionaries are valid reducer functions. Sadly, that pseudostandard is
# absurdly strict to the point of practical uselessness. Attempting to conform
# to that pseudostandard would require refactoring *ALL* reducer functions to
# explicitly define the same signature. However, we have intentionally *NOT*
# done that. Why? Doing so would substantially increase the fragility of this
# API by preventing us from readily adding and removing infrequently required
# parameters (e.g., "cls_stack", "pith_name"). Callback protocols suck, frankly.
_HintSignToReduceHintCached = Dict[Optional[HintSign], Callable]
'''
PEP-compliant type hint matching a **cached reducer dictionary** (i.e.,
mapping from each sign uniquely identifying various type hints to a memoized
callable reducing those higher- to lower-level hints).
'''


_HintSignToReduceHintUncached = _HintSignToReduceHintCached
'''
PEP-compliant type hint matching an **uncached reducer dictionary** (i.e.,
mapping from each sign uniquely identifying various type hints to an unmemoized
callable reducing those higher- to lower-level hints).
'''

# ....................{ PRIVATE ~ dicts                    }....................
_HINT_SIGN_TO_REDUCE_HINT_CACHED: _HintSignToReduceHintCached = {
    # ..................{ NON-PEP                            }..................
    # If this hint is identified by *NO* sign, this hint is either an
    # isinstanceable type *OR* a hint unrecognized by beartype. In either case,
    # apply the following reductions:
    #
    # * If this configuration enables support for the PEP 484-compliant implicit
    #   numeric tower:
    #   * Expand the "float" type hint to the "float | int" union.
    #   * Expand the "complex" type hint to the "complex | float | int" union.
    None: reduce_hint_pep_unsigned,

    # ..................{ PEP 484                            }..................
    # If this hint is a PEP 484-compliant IO generic base class *AND* the active
    # Python interpreter targets Python >= 3.8 and thus supports PEP
    # 544-compliant protocols, reduce this functionally useless hint to the
    # corresponding functionally useful beartype-specific PEP 544-compliant
    # protocol implementing this hint.
    #
    # Note that PEP 484-compliant IO generic base classes are technically usable
    # under Python < 3.8 (e.g., by explicitly subclassing those classes from
    # third-party classes). Ergo, we can neither safely emit warnings nor raise
    # exceptions on visiting these classes under *ANY* Python version.
    HintSignGeneric: reduce_hint_pep484_generic,

    # If this hint is a PEP 484-compliant new type, reduce this new type to the
    # user-defined class aliased by this new type.
    HintSignNewType: reduce_hint_pep484_newtype,

    # If this is the PEP 484-compliant "None" singleton, reduce this hint to
    # the type of that singleton. While *NOT* explicitly defined by the
    # "typing" module, PEP 484 explicitly supports this singleton:
    #     When used in a type hint, the expression None is considered
    #     equivalent to type(None).
    #
    # The "None" singleton is used to type callables lacking an explicit
    # "return" statement and thus absurdly common.
    HintSignNone: reduce_hint_pep484_none,

    #FIXME: Remove this branch *AFTER* deeply type-checking type variables.
    # If this type variable was parametrized by one or more bounded
    # constraints, reduce this hint to these constraints.
    HintSignTypeVar: reduce_hint_pep484_typevar,

    # ..................{ PEP (484|585)                      }..................
    # If this hint is a PEP 484- or 585-compliant subclass type hint subscripted
    # by an ignorable child type hint (e.g., "object", "typing.Any"), silently
    # ignore this argument by reducing this hint to the "type" superclass.
    #
    # Note that:
    # * This reduction could be performed elsewhere, but remains here as doing
    #   so here dramatically simplifies matters elsewhere.
    # * This reduction *CANNOT* be performed by the is_hint_ignorable() tester,
    #   as subclass type hints subscripted by ignorable child type hints are
    #   *NOT* ignorable; they're reducible to the "type" superclass.
    HintSignType: reduce_hint_pep484585_type,

    # ..................{ PEP 557                            }..................
    # If this hint is a dataclass-specific initialization-only instance
    # variable (i.e., instance of the PEP 557-compliant "dataclasses.InitVar"
    # class introduced by Python 3.8.0), reduce this functionally useless hint
    # to the functionally useful child type hint subscripting this parent hint.
    HintSignPep557DataclassInitVar: reduce_hint_pep557_initvar,

    # ..................{ PEP 585                            }..................
    # If this hint is a PEP 585-compliant unrecognized subscripted builtin type
    # hint (i.e., C-based type hint that is *NOT* an isinstanceable type,
    # instantiated by subscripting a pure-Python origin class subclassing the
    # C-based "types.GenericAlias" type where that origin class is unrecognized
    # by :mod:`beartype` and thus PEP-noncompliant), reduce this C-based type
    # hint (which is *NOT* type-checkable as is) to its unsubscripted
    # pure-Python origin class (which is type-checkable as is). Examples include
    # "os.PathLike[...]" and "weakref.weakref[...]" type hints.
    HintSignPep585BuiltinSubscriptedUnknown: (
        reduce_hint_pep585_builtin_subscripted_unknown),

    # ..................{ PEP 589                            }..................
    #FIXME: Remove *AFTER* deeply type-checking typed dictionaries. For now,
    #shallowly type-checking such hints by reduction to untyped dictionaries
    #remains the sanest temporary work-around.

    # If this hint is a PEP 589-compliant typed dictionary (i.e.,
    # "typing.TypedDict" or "typing_extensions.TypedDict" subclass), silently
    # ignore all child type hints annotating this dictionary by reducing this
    # hint to the "Mapping" superclass. Yes, "Mapping" rather than "dict". By
    # PEP 589 edict:
    #     First, any TypedDict type is consistent with Mapping[str, object].
    #
    # Typed dictionaries are largely discouraged in the typing community, due to
    # their non-standard semantics and syntax.
    HintSignTypedDict: reduce_hint_pep589,

    # ..................{ PEP 591                            }..................
    #FIXME: Remove *AFTER* deeply type-checking final type hints.

    # If this hint is a PEP 591-compliant "typing.Final[...]" type hint,
    # silently reduce this hint to its subscripted argument (e.g., from
    # "typing.Final[int]" to merely "int").
    HintSignFinal: reduce_hint_pep591,

    # ..................{ PEP 593                            }..................
    # If this hint is a PEP 593-compliant beartype-agnostic type metahint,
    # ignore all annotations on this hint by reducing this hint to the
    # lower-level hint it annotates.
    HintSignAnnotated: reduce_hint_pep593,

    # ..................{ PEP 675                            }..................
    #FIXME: Remove *AFTER* deeply type-checking literal strings. Note that doing
    #so will prove extremely non-trivial or possibly even infeasible, suggesting
    #we will probably *NEVER* deeply type-check literal strings. It's *NOT*
    #simply a matter of efficiently parsing ASTs at runtime; it's that as well
    #as correctly transitively inferring literal strings across operations and
    #calls, which effectively requires parsing the entire codebase and
    #constructing an in-memory graph of all type relations. See also:
    #    https://peps.python.org/pep-0675/#inferring-literalstring

    # If this hint is a PEP 675-compliant "typing.LiteralString" type hint,
    # reduce this hint to the standard "str" type.
    HintSignLiteralString: reduce_hint_pep675,

    # ..................{ PEP 695                            }..................
    # If this hint is a PEP 695-compliant "type" alias, reduce this alias to the
    # underlying hint lazily referred to by this alias.
    HintSignPep695TypeAlias: reduce_hint_pep695,

    # ..................{ NON-PEP ~ numpy                    }..................
    # If this hint is a PEP-noncompliant typed NumPy array (e.g.,
    # "numpy.typing.NDArray[np.float64]"), reduce this hint to the equivalent
    # well-supported beartype validator.
    HintSignNumpyArray: reduce_hint_numpy_ndarray,

    # ..................{ NON-PEP ~ pandera                  }..................
    # If this hint is *ANY* PEP-noncompliant Pandera type hint (e.g.,
    # "pandera.typing.DataFrame[...]"), reduce this hint to an arbitrary
    # PEP-compliant ignorable type hint. See this reducer for commentary.
    HintSignPanderaAny: reduce_hint_pandera,
}
'''
Dictionary mapping from each sign uniquely identifying PEP-compliant type hints
to that sign's **cached reducer** (i.e., low-level function efficiently memoized
by the :func:`.callable_cached` decorator reducing those higher- to lower-level
hints).

Each value of this dictionary is expected to have a signature resembling:

.. code-block:: python

   def reduce_hint_pep{pep_number}(
       hint: object,
       conf: BeartypeConf,
       pith_name: Optional[str],
       exception_prefix: str,
       *args, **kwargs
   ) -> object:

Note that:

* Reducers should explicitly accept *only* those parameters they explicitly
  require. Ergo, a reducer requiring *only* the ``hint`` parameter should omit
  all of the other parameters referenced above.
* Reducers do *not* need to validate the passed type hint as being of the
  expected sign. By design, a reducer is only ever passed a type hint of the
  expected sign.
* Reducers should *not* be memoized (e.g., by the
  ``callable_cached`` decorator). Since the higher-level :func:`.reduce_hint`
  function that is the sole entry point to calling all lower-level reducers is
  itself memoized, reducers themselves neither require nor benefit from
  memoization. Moreover, even if they did either require or benefit from
  memoization, they couldn't be -- at least, not directly. Why? Because
  :func:`.reduce_hint` necessarily passes keyword arguments to all reducers. But
  memoized functions *cannot* receive keyword arguments (without destroying
  efficiency and thus the entire point of memoization).
'''


_HINT_SIGN_TO_REDUCE_HINT_UNCACHED: _HintSignToReduceHintUncached = {
    # ..................{ PEP 484                            }..................
    # Preserve deprecated PEP 484-compliant type hints as is while emitting one
    # non-fatal deprecation warning for each.
    #
    # Note that, to ensure that one such warning is emitted for each such hint,
    # these reducers are intentionally uncached rather than cached.
    HintSignAbstractSet: reduce_hint_pep484_deprecated,
    HintSignAsyncContextManager: reduce_hint_pep484_deprecated,
    HintSignAsyncGenerator: reduce_hint_pep484_deprecated,
    HintSignAsyncIterable: reduce_hint_pep484_deprecated,
    HintSignAsyncIterator: reduce_hint_pep484_deprecated,
    HintSignAwaitable: reduce_hint_pep484_deprecated,
    HintSignByteString: reduce_hint_pep484_deprecated,
    HintSignCallable: reduce_hint_pep484_deprecated,
    HintSignChainMap: reduce_hint_pep484_deprecated,
    HintSignCollection: reduce_hint_pep484_deprecated,
    HintSignContainer: reduce_hint_pep484_deprecated,
    HintSignContextManager: reduce_hint_pep484_deprecated,
    HintSignCoroutine: reduce_hint_pep484_deprecated,
    HintSignCounter: reduce_hint_pep484_deprecated,
    HintSignDefaultDict: reduce_hint_pep484_deprecated,
    HintSignDeque: reduce_hint_pep484_deprecated,
    HintSignDict: reduce_hint_pep484_deprecated,
    HintSignFrozenSet: reduce_hint_pep484_deprecated,
    HintSignGenerator: reduce_hint_pep484_deprecated,
    HintSignHashable: reduce_hint_pep484_deprecated,
    HintSignItemsView: reduce_hint_pep484_deprecated,
    HintSignIterable: reduce_hint_pep484_deprecated,
    HintSignIterator: reduce_hint_pep484_deprecated,
    HintSignKeysView: reduce_hint_pep484_deprecated,
    HintSignList: reduce_hint_pep484_deprecated,
    HintSignMappingView: reduce_hint_pep484_deprecated,
    HintSignMapping: reduce_hint_pep484_deprecated,
    HintSignMatch: reduce_hint_pep484_deprecated,
    HintSignMutableMapping: reduce_hint_pep484_deprecated,
    HintSignMutableSequence: reduce_hint_pep484_deprecated,
    HintSignMutableSet: reduce_hint_pep484_deprecated,
    HintSignOrderedDict: reduce_hint_pep484_deprecated,
    HintSignPattern: reduce_hint_pep484_deprecated,
    HintSignReversible: reduce_hint_pep484_deprecated,
    HintSignSequence: reduce_hint_pep484_deprecated,
    HintSignSet: reduce_hint_pep484_deprecated,
    HintSignSized: reduce_hint_pep484_deprecated,
    HintSignTuple: reduce_hint_pep484_deprecated,
    HintSignType: reduce_hint_pep484_deprecated,
    HintSignValuesView: reduce_hint_pep484_deprecated,

    # ..................{ PEP 613                            }..................
    # Reduce PEP 613-compliant "typing.TypeAlias" type hints to an arbitrary
    # ignorable type hint *AND* emit a non-fatal deprecation warning.
    #
    # Note that, to ensure that one such warning is emitted for each such hint,
    # this reducer is intentionally uncached rather than cached.
    HintSignTypeAlias: reduce_hint_pep613,

    # ..................{ PEP 647                            }..................
    # Reduce PEP 647-compliant "typing.TypeGuard[...]" type hints to either:
    # * If this hint annotates the return of some callable, the "bool" type.
    # * Else, raise an exception.
    HintSignTypeGuard: reduce_hint_pep647,

    # ..................{ PEP 673                            }..................
    # Reduce PEP 673-compliant "typing.Self" type hints to either:
    # * If @beartype is currently decorating a class, the most deeply nested
    #   class on the passed type stack.
    # * Else, raise an exception.
    HintSignSelf: reduce_hint_pep673,
}
'''
Dictionary mapping from each sign uniquely identifying various type hints to
that sign's **uncached reducer** (i.e., low-level function whose reduction
decision contextually depends on the currently decorated callable and thus
*cannot* be efficiently memoized by the :func:`.callable_cached` decorator).

See Also
--------
:data:`._HINT_SIGN_TO_REDUCE_HINT_CACHED`
    Further details.
'''
