#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **generic type hint
iterators** (i.e., low-level callables generically iterating over both
:pep:`484`- and :pep:`585`-compliant generic class hierarchies).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Any
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype._check.metadata.metasane import (
    IterableHintOrSanifiedData,
    get_hint_or_sane_hint,
)
from beartype._conf.confcls import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.hint.datahintpep import (
    Hint,
    # IterableHints,
    TypeVarToHint,
)
from beartype._data.hint.datahinttyping import TypeException
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._util.cache.pool.utilcachepoollistfixed import (
    FIXED_LIST_SIZE_MEDIUM,
    acquire_fixed_list,
    release_fixed_list,
)
from beartype._util.kind.map.utilmapfrozen import FrozenDict

# ....................{ ITERATORS                          }....................
#FIXME: Unit test us up, please.
def iter_hint_pep484585_generic_bases_unerased(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    typevar_to_hint: TypeVarToHint = FROZENDICT_EMPTY,
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> IterableHintOrSanifiedData:
    '''
    Breadth-first search (BFS) generator iteratively yielding the one or more
    unignorable unerased transitive pseudo-superclasses originally declared as
    superclasses prior to their type erasure of the passed :pep:`484`- or
    :pep:`585`-compliant generic.

    This generator yields the full tree of all pseudo-superclasses by
    transitively visiting both all direct pseudo-superclasses of this generic
    *and* all indirect pseudo-superclasses transitively superclassing all direct
    pseudo-superclasses of this generic. For efficiency, this generator is
    internally implemented with an efficient imperative First In First Out
    (FILO) queue rather than an inefficient (and dangerous, due to both
    unavoidable stack exhaustion and avoidable infinite recursion) tree of
    recursive function calls.

    Motivation
    ----------
    Ideally, a BFS would *not* be necessary. Instead, pseudo-superclasses
    visited by this BFS should be visitable as is via whatever external parent
    BFS is currently iterating over the tree of all transitive type hints (e.g.,
    our code generation algorithm implemented by the
    :func:`beartype._check.code.codemake.make_func_pith_code` function).
    That's how we transitively visit all other kinds of type hints, right?
    Sadly, that simple solution fails to scale to all possible edge cases that
    arise with generics. Why? Because our code generation algorithm sensibly
    requires that *only* unignorable hints may be enqueued onto its outer BFS.
    Generics confound that constraint. Some pseudo-superclasses are
    paradoxically:

    * Ignorable from the perspective of code generation. *No* type-checking code
      should be generated for these pseudo-superclasses. See reasons below.
    * Unignorable from the perspective of algorithm visitation. These
      pseudo-superclasses generate *no* code but may themselves subclass other
      pseudo-superclasses for which type-checking code should be generated and
      which must thus be visited by our outer BFS.

    Paradoxical pseudo-superclasses include:

    * User-defined :pep:`484`-compliant subgenerics (i.e., user-defined generics
      subclassing one or more parent user-defined generic superclasses).
    * User-defined :pep:`544`-compliant subprotocols (i.e., user-defined
      protocols subclassing one or more parent user-defined protocol
      superclasses).

    Consider this example :pep:`544`-compliant subprotocol:

    .. code-block:: pycon

       >>> import typing as t
       >>> class UserProtocol(t.Protocol[t.AnyStr]): pass
       >>> class UserSubprotocol(UserProtocol[str], t.Protocol): pass
       >>> UserSubprotocol.__orig_bases__
       (UserProtocol[str], typing.Protocol)  # <-- good
       >>> UserProtocolUnerased = UserSubprotocol.__orig_bases__[0]
       >>> UserProtocolUnerased is UserProtocol
       False
       >>> isinstance(UserProtocolUnerased, type)
       False  # <-- bad

    :pep:`585`-compliant generics suffer no such issues:

    .. code-block:: pycon

       >>> from beartype._util.hint.pep.proposal.pep585 import is_hint_pep585_builtin_subscripted
       >>> class UserGeneric(list[int]): pass
       >>> class UserSubgeneric(UserGeneric[int]): pass
       >>> UserSubgeneric.__orig_bases__
       (UserGeneric[int],)
       >>> UserGenericUnerased = UserSubgeneric.__orig_bases__[0]
       >>> isinstance(UserGenericUnerased, type)
       True  # <-- good
       >>> UserGenericUnerased.__mro__
       (UserGeneric, list, object)
       >>> is_hint_pep585_builtin_subscripted(UserGenericUnerased)
       True

    Iteratively walking up the unerased inheritance hierarchy for any such
    paradoxical generic or protocol subclass (e.g., ``UserSubprotocol`` but
    *not* ``UserSubgeneric`` above) would visit a user-defined generic or
    protocol pseudo-superclass subscripted by type variables. Due to poorly
    defined obscurities in the :mod:`typing` implementation, that
    pseudo-superclass is *not* actually a class but rather an instance of a
    private :mod:`typing` class (e.g., :class:`typing._SpecialForm`). This
    algorithm would then detect that pseudo-superclass as neither a generic nor
    a :mod:`typing` object and thus raise an exception. Fortunately, that
    pseudo-superclass conveys no meaningful intrinsic semantics with respect to
    type-checking; its only use is to register its own pseudo-superclasses (one
    or more of which could convey meaningful intrinsic semantics with respect to
    type-checking) for visitation by this BFS.

    Parameters
    ----------
    hint : object
        Generic type hint to be inspected.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to :data:`.BEARTYPE_CONF_DEFAULT`, the default :math:`O(1)`
        type-checking configuration.
    typevar_to_hint : TypeVarToHint, optional
        **Type variable lookup table** (i.e., immutable dictionary mapping from
        type variables to the concrete hints those type variables map to).
        Defaults to the empty type variable lookup table.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    IterableHintOrSanifiedData
        Breadth-first search (BFS) generator iteratively yielding the one or
        more unignorable unerased transitive pseudo-superclasses originally
        declared as superclasses prior to their type erasure of this generic.

    Raises
    ------
    exception_cls
        If this hint is *not* a generic.

    See Also
    --------
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget.get_hint_pep484585_generic_type_or_none`
        Further details.
    '''
    assert isinstance(typevar_to_hint, FrozenDict), (
        f'{repr(typevar_to_hint)} not frozen dictionary.')

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._check.convert.convsanify import (
        sanify_hint_child)
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_bases_unerased)
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic_user)

    # ....................{ LOCALS                         }....................
    # Tuple of the one or more unerased pseudo-superclasses originally listed as
    # superclasses prior to their type erasure by this generic.
    hint_bases_direct = get_hint_pep484585_generic_bases_unerased(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # print(f'generic {hint} hint_bases_direct: {hint_bases_direct}')

    # Fixed list of the one or more unerased transitive pseudo-superclasses
    # originally listed as superclasses prior to their type erasure by this
    # generic that have yet to be visited by the breadth-first search (BFS) over
    # these pseudo-superclasses performed below.
    hint_bases = acquire_fixed_list(size=FIXED_LIST_SIZE_MEDIUM)

    # 0-based index of the currently visited pseudo-superclass of this list.
    hint_bases_index_curr = 0

    # 0-based index of one *PAST* the last pseudo-superclass of this list.
    hint_bases_index_past_last = len(hint_bases_direct)

    # Initialize this list to these direct pseudo-superclasses of this generic.
    hint_bases[0:hint_bases_index_past_last] = hint_bases_direct
    # print(f'generic pseudo-superclasses [initial]: {repr(hint_bases_direct}')

    # ....................{ SEARCH                         }....................
    # While the 0-based index of the next visited pseudo-superclass does *NOT*
    # exceed that of the last pseudo-superclass in this list, there remains one
    # or more pseudo-superclasses to be visited in this BFS.
    while hint_bases_index_curr < hint_bases_index_past_last:
        # Sane pseudo-superclass sanified from this possibly insane
        # pseudo-superclass if sanifying this pseudo-superclass did not generate
        # supplementary metadata *OR* that metadata (i.e., if doing so generated
        # supplementary metadata).
        hint_or_sane_base = sanify_hint_child(
            hint=hint_bases[hint_bases_index_curr],
            #FIXME: Possibly also pass this, please. Ignorable for now. *shrug*
            # cls_stack=cls_stack,
            conf=conf,
            typevar_to_hint=typevar_to_hint,
            exception_prefix=exception_prefix,
        )
        # print(f'generic {hint} base: {repr(hint_base)}')

        # If this pseudo-superclass is unignorable...
        if hint_or_sane_base is not Any:
            # Pseudo-superclass encapsulated by this metadata.
            hint_base = get_hint_or_sane_hint(hint_or_sane_base)

            # If this pseudo-superclass is a user-defined PEP 484-compliant
            # generic or 544-compliant protocol, generate *NO* type-checking
            # code for this pseudo-superclass; instead, we only enqueue *ALL*
            # parent pseudo-superclasses of this child pseudo-superclass for
            # visitation by later iteration of this inner BFS.
            #
            # See "hints_bases" for explanatory commentary.
            if is_hint_pep484585_generic_user(hint_base):
                # Tuple of the one or more parent pseudo-superclasses of this
                # child pseudo-superclass.
                hint_base_bases = get_hint_pep484585_generic_bases_unerased(
                    hint=hint_base,
                    exception_cls=exception_cls,
                    exception_prefix=exception_prefix,
                )

                # 0-based index of the last pseudo-superclass of this list
                # *BEFORE* adding onto this list.
                hint_bases_index_past_last_prev = hint_bases_index_past_last

                # 0-based index of the last pseudo-superclass of this list
                # *AFTER* adding onto this list.
                hint_bases_index_past_last += len(hint_base_bases)

                # Enqueue these superclasses onto this list.
                hint_bases[
                    hint_bases_index_past_last_prev:
                    hint_bases_index_past_last
                ] = hint_base_bases
            # Else, this pseudo-superclass is neither an ignorable user-defined
            # PEP 484-compliant generic *NOR* an ignorable 544-compliant
            # protocol.
            #
            # If this pseudo-superclass is identified by a sign, this
            # pseudo-superclass is *NOT* an isinstanceable type conveying *NO*
            # meaningful semantics. This pseudo-superclass is unignorable. Yield
            # this unignorable pseudo-superclass.
            elif get_hint_pep_sign_or_none(hint_base) is not None:
                yield hint_or_sane_base
            # Else, this pseudo-superclass is an isinstanceable type conveying
            # *NO* meaningful semantics and is thus effectively ignorable. Why?
            # Because the caller already type-checks this pith against the
            # generic subclassing this superclass and thus this superclass as
            # well in an isinstance() call (e.g., in the
            # "CODE_PEP484585_GENERIC_PREFIX" snippet leveraged by the
            # "beartype._check.code.codemake" submodule).
        # Else, this pseudo-superclass is ignorable.
        # else:
        #     print(f'Ignoring generic {repr(hint)} base {repr(hint_base)}...')
        #     print(f'Is generic {hint} base {repr(hint_base)} type? {isinstance(hint_base, type)}')

        # Nullify the previously visited pseudo-superclass in this list.
        hint_bases[hint_bases_index_curr] = None

        # Increment the 0-based index of the next visited pseudo-superclass in
        # this list *BEFORE* visiting that pseudo-superclass but *AFTER*
        # performing all other logic for the current pseudo-superclass.
        hint_bases_index_curr += 1

    # ....................{ POSTAMBLE                      }....................
    # Release this list. Pray for salvation, for we find none here.
    release_fixed_list(hint_bases)
