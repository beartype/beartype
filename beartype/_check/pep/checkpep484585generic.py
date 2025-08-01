#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **generic type iterators**
(i.e., low-level callables generically iterating over both :pep:`484`- and
:pep:`585`-compliant generic class hierarchies).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype.typing import (
    Iterable,
    Tuple,
)
from beartype._check.convert.convmain import sanify_hint_child
from beartype._check.metadata.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintSane,
)
from beartype._conf.confmain import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.typing.datatyping import (
    TypeException,
    TypeStack,
)
from beartype._data.hint.sign.datahintsigncls import HintSign
from beartype._util.cache.pool.utilcachepoollistfixed import (
    FIXED_LIST_SIZE_MEDIUM,
    acquire_fixed_list,
    release_fixed_list,
)
from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
    get_hint_pep484585_generic_base_extrinsic_sign_or_none,
    get_hint_pep484585_generic_bases_unerased,
)
from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
    is_hint_pep484585_generic_user)
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

# ....................{ ITERATORS                          }....................
#FIXME: Unit test us up, please.
#FIXME: Note that this would be, ideally, internally refactored to leverage the
#lower-level iter_hint_pep560_bases_unerased() iterator. We tried,
#actually... and failed hard. The current approach is "good enough." *shrug*
def iter_hint_pep484585_generic_unsubbed_bases_unerased(
    # Mandatory parameters.
    hint_sane: HintSane,

    # Optional parameters.
    cls_stack: TypeStack = None,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> Iterable[Tuple[HintSane, HintSign]]:
    '''
    Generator iteratively yielding the one or more **unerased
    pseudo-superclasses** (i.e., unignorable PEP-compliant type hints originally
    declared as transitive superclasses prior to type erasure) of the passed
    :pep:`484`- or :pep:`585`-compliant unsubscripted generic, effectively
    performing a breadth-first search (BFS) over these pseudo-superclasses.

    This generator yields the full tree of all pseudo-superclasses by
    transitively visiting both all direct pseudo-superclasses of this generic
    *and* all indirect pseudo-superclasses transitively superclassing all direct
    pseudo-superclasses of this generic. For efficiency, this generator is
    internally implemented with an efficient imperative First In First Out
    (FILO) queue rather than an inefficient (and dangerous, due to both
    unavoidable stack exhaustion and avoidable infinite recursion) tree of
    recursive function calls.

    This generator is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator). Memoization is the caller's responsibility.

    Caveats
    -------
    **This generator exhibits** :math:`O(n)` **linear time complexity for**
    :math:`n` the number of transitive pseudo-superclasses of this generic. So,
    this generator is slow. The caller is expected to memoize *all* calls to
    this generator, which is itself *not* memoized.

    Design
    ------
    Note that there exist two kinds of pseudo-superclasses with respect to
    type-checking. Each pseudo-superclass yielded by this generator is either:

    * An **intrinsic pseudo-superclass** (i.e., whose type-checking is
      intrinsically defined as a type hint such that all data required to
      type-check this pseudo-superclass is fully defined by this hint). *All*
      intrinsic pseudo-superclasses are valid type hints. This is the common
      case and, indeed, almost all cases. Examples include :pep:`484`- and
      :pep:`585`-compliant subscripted container type hints: e.g.,

        .. code-block:: python

           # The PEP 585-compliant "list[T]" pseudo-superclass is a valid hint
           # whose type-checking is intrinsic to this hint.
           class GenericList[T](list[T]):
               def generic_method(self, arg: T) -> T:
                   return arg

    * An **extrinsic pseudo-superclass (i.e., whose type-checking is
      extrinsically defined by this unsubscripted generic such that only the
      combination of this pseudo-superclass and this unsubscripted generic
      suffices to provide all data required to type-check this
      pseudo-superclass). Extrinsic pseudo-superclasses are *not* necessarily
      valid type hints, though some might be. Examples include:

      * **Generic named tuples** (i.e., types subclassing both the
        :pep:`484`-compliant :class:`typing.Generic` superclass *and* the
        :pep:`484`-compliant :class:`typing.NamedTuple` superclass): e.g.,

        .. code-block:: python

           from typing import Generic, NamedTuple
           class GenericNamedTuple[T](NamedTuple, Generic[T]):
               generic_item: T

        When iterating over the :class:`typing.NamedTuple` pseudo-superclass of
        a generic typed dictionary, this generator yields the 2-tuple
        ``(hint_sane.hint, HintSignNamedTuple)`` (e.g.,
        ``(GenericNamedTuple, HintSignNamedTuple)`` for the above generic).

      * **Generic typed dictionaries** (i.e., types subclassing both the
        :pep:`484`-compliant :class:`typing.Generic` superclass *and* the
        :pep:`589`-compliant :class:`typing.TypedDict` superclass): e.g.,

        .. code-block:: python

           from typing import Generic, TypedDict
           class GenericTypedDict[T](TypedDict, Generic[T]):
               generic_item: T

        When iterating over the :class:`typing.TypedDict` pseudo-superclass of
        a generic typed dictionary, this generator yields the 2-tuple
        ``(hint_sane.hint, HintSignTypedDict)`` (e.g.,
        ``(GenericTypedDict, HintSignTypedDict)`` for the above generic).

    Motivation
    ----------
    Ideally, a BFS would *not* be necessary. Instead, pseudo-superclasses
    visited by this BFS should be visitable as is via whatever external parent
    BFS is currently iterating over the tree of all transitive type hints (e.g.,
    our code generation algorithm implemented by the
    :func:`beartype._check.code.codemain.make_func_pith_code` function).
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

       >>> from beartype._util.hint.pep.proposal.pep585 import is_hint_pep585_builtin_subbed
       >>> class UserGeneric(list[int]): pass
       >>> class UserSubgeneric(UserGeneric[int]): pass
       >>> UserSubgeneric.__orig_bases__
       (UserGeneric[int],)
       >>> UserGenericUnerased = UserSubgeneric.__orig_bases__[0]
       >>> isinstance(UserGenericUnerased, type)
       True  # <-- good
       >>> UserGenericUnerased.__mro__
       (UserGeneric, list, object)
       >>> is_hint_pep585_builtin_subbed(UserGenericUnerased)
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
    hint_sane : HintSane
        **Sanified type hint metadata** (i.e., :data:`.HintSane` object)
        encapsulating the :pep:`484`- or :pep:`585`-compliant unsubscripted
        generic to be inspected.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to :data:`.BEARTYPE_CONF_DEFAULT`, the default :math:`O(1)`
        type-checking configuration.
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.
    exception_cls : TypeException, default: BeartypeDecorHintPep484585Exception
        Type of exception to be raised in the event of fatal error. Defaults to
        :exc:`.BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Yields
    ------
    Tuple[HintSane, HintSign]
        2-tuple ``(hint_sane, hint_sign)``, where:

        * ``hint_sane`` is an unignorable unerased transitive pseudo-superclass
          originally declared as a superclass prior to its type erasure of this
          unsubscripted generic.
        * ``hint_sign`` is the sign uniquely identifying this pseudo-superclass.
          Since this sign does *not* necessarily correspond to the sign returned
          by the :func:`.get_hint_pep_sign_or_none` getter when passed this
          pseudo-superclass, callers should take care to preserve this sign.

    Raises
    ------
    exception_cls
        If this hint is *not* a generic.

    See Also
    --------
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget.get_hint_pep484585_generic_type_or_none`
        Further details.
    '''
    # assert is_hint_pep484585_generic_unsubbed(hint_sane.hint)
    assert isinstance(hint_sane, HintSane), (
        f'{repr(hint_sane)} not sanified metadata.')

    # ....................{ LOCALS                         }....................
    # This unsubscripted generic.
    hint = hint_sane.hint

    # Tuple of the one or more unerased pseudo-superclasses originally listed as
    # superclasses prior to their type erasure by this unsubscripted generic.
    hint_bases_direct = get_hint_pep484585_generic_bases_unerased(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # print(f'generic {hint} hint_bases_direct: {hint_bases_direct}')

    # ....................{ LOCALS ~ bases : indirect      }....................
    # Fixed list of 2-tuples "(hint_base, hint_base_subclass_sane)" describing
    # the one or more unerased transitive pseudo-superclasses originally listed
    # as superclasses prior to their type erasure by this generic that have yet
    # to be visited by the breadth-first search (BFS) over these
    # pseudo-superclasses performed below, where:
    # * "hint_base" is each such pseudo-superclass.
    # * "hint_base_subclass_sane" is the sanified hint metadata encapsulating
    #   the direct pseudo-*SUBCLASS* of this "hint_base", which will then be
    #   passed as the "hint_parent_sane" parameter to sanify this "hint_base".
    #   Specifically, this is either:
    #   * If this "hint_base" is a direct pseudo-superclass of the passed
    #     generic, the passed "hint_sane" metadata as is.
    #   * Else, this "hint_base" is a transitive pseudo-superclass two or more
    #     class levels above the passed generic. In this case, this is the
    #     "hint_base_sane" local calculated below.
    hint_bases = acquire_fixed_list(size=FIXED_LIST_SIZE_MEDIUM)

    # 0-based index of the currently visited pseudo-superclass of this list.
    hint_bases_index_curr = 0

    # 0-based index of one *PAST* the last pseudo-superclass of this list.
    hint_bases_index_past_last = len(hint_bases_direct)

    #FIXME: [SPEED] Optimize into a "while" loop. *sigh*
    # For the 0-based index of each direct pseudo-superclass of the passed
    # generic *AND* this direct pseudo-superclass...
    for hint_base_direct_index, hint_base_direct in enumerate(hint_bases_direct):
        # Enqueue this direct pseudo-superclass and the sanified hint metadata
        # applicable to this pseudo-superclass onto the "hint_bases" list.
        hint_bases[hint_base_direct_index] = (hint_base_direct, hint_sane)
    # print(f'generic pseudo-superclasses [initial]: {repr(hint_bases_direct}')

    # ....................{ SEARCH                         }....................
    # While the 0-based index of the next visited pseudo-superclass does *NOT*
    # exceed that of the last pseudo-superclass in this list, there remains one
    # or more pseudo-superclasses to be visited in this BFS. Let us do so.
    #
    # Each iteration of this search is subdivided into two phases, enabling this
    # search to discern between intrinsic and extrinsic pseudo-superclasses --
    # whose handling is fundamentally different. See the function docstring for
    # the distinction between the two.
    while hint_bases_index_curr < hint_bases_index_past_last:
        # ....................{ LOCALS                     }....................
        # Dismantled, this is:
        # * "hint_base", the currently visited transitive pseudo-superclass of
        #   the passed generic.
        # * "hint_base_subclass_sane", the sanified hint metadata applicable to
        #   this "hint_base". See the "hint_bases" definition above for details.
        hint_base, hint_base_subclass_sane = hint_bases[hint_bases_index_curr]

        # ....................{ PHASE ~ extrinsic          }....................
        # In this first phase, we:
        # 1. Decide whether this pseudo-superclass is extrinsic.
        # 2. If so, return this subscripted generic (rather than this
        #    pseudo-superclass) *AND* the sign uniquely identifying this
        #    pseudo-superclass. To distinguish this sign from the normal sign
        #    identifying a hint, this sign is referred to as the "subsign"
        #    (i.e., subclass sign applicable to this subscripted generic
        #    subclassing this pseudo-superclass rather than this
        #    pseudo-superclass itself).
        #
        # Note that:
        # * Extrinsic pseudo-superclasses are *EXTREMELY* rare. Almost all
        #   pseudo-superclasses are intrinsic.
        # * Extrinsic pseudo-superclasses are efficiently detectable in
        #   non-amortized O(1) time. Even though extrinsic pseudo-superclasses
        #   are rare, the cost of handling them is thankfully minimal.
        # * Extrinsic pseudo-superclasses *MUST* be detected before intrinsic
        #   pseudo-superclasses. Some extrinsic pseudo-superclasses (e.g.,
        #   "typing.TypedDict") are also valid type hints and thus also valid
        #   intrinsic pseudo-superclasses. Extrinsic pseudo-superclasses convey
        #   more fine-grained data for type-checking purposes than intrinsic
        #   pseudo-superclasses; the former are thus preferable to the latter.

        # Sign additionally identifying this pseudo-superclass if this
        # pseudo-superclass is extrinsic *OR* "None" otherwise (i.e., if this
        # pseudo-superclass is intrinsic).
        hint_base_extrinsic_sign = (
            get_hint_pep484585_generic_base_extrinsic_sign_or_none(
                hint_base=hint_base,
                exception_cls=exception_cls,
                exception_prefix=exception_prefix,
            ))

        # If this pseudo-superclass is extrinsic, yield the 2-tuple of:
        # * This *UNSUBSCRIPTED GENERIC* (rather than this extrinsic
        #   pseudo-superclass). Why? Because, by definition, an extrinsic
        #   pseudo-superclass itself conveys insufficient metadata required to
        #   type-check the unsubscripted generic subclassing that
        #   pseudo-superclass; that metadata is extrinsic to that
        #   pseudo-superclass, residing in this unsubscripted generic.
        # * This sign.
        if hint_base_extrinsic_sign is not None:
            yield hint_base_subclass_sane, hint_base_extrinsic_sign
        # Else, this pseudo-superclass is intrinsic. Continue to the next phase
        # deciding the sign identifying this intrinsic.
        #
        # ....................{ PHASE ~ intrinsic          }....................
        # In this second phase, we fallback to treating this pseudo-superclass
        # as intrinsic by returning both this pseudo-superclass *AND* the sign
        # uniquely identifying this pseudo-superclass. This is the common case.
        else:
            # Metadata encapsulating the sanification of this possibly insane
            # pseudo-superclass.
            hint_base_sane = sanify_hint_child(
                hint=hint_base,
                hint_parent_sane=hint_base_subclass_sane,
                cls_stack=cls_stack,
                conf=conf,
                exception_prefix=exception_prefix,
            )
            # print(f'generic {hint} base: {repr(hint_base)}')

            # If this pseudo-superclass is unignorable...
            if hint_base_sane is not HINT_SANE_IGNORABLE:
                # Sanified pseudo-superclass encapsulated by this metadata.
                hint_base = hint_base_sane.hint

                # If this pseudo-superclass is a user-defined PEP 484-compliant
                # generic or 544-compliant protocol, generate *NO* type-checking
                # code for this pseudo-superclass; instead, we only enqueue
                # *ALL* parent pseudo-superclasses of this child
                # pseudo-superclass for visitation by later iteration of this
                # inner BFS.
                if is_hint_pep484585_generic_user(hint_base):
                    # Tuple of the one or more parent pseudo-superclasses of
                    # this child pseudo-superclass.
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

                    # For the 0-based index of each parent pseudo-superclass of
                    # this child pseudo-superclass *AND* that parent
                    # pseudo-superclass...
                    for hint_base_base_index, hint_base_base in enumerate(
                        hint_base_bases):
                        # Enqueue this parent pseudo-superclass and the sanified
                        # hint metadata applicable to this pseudo-superclass
                        # onto the "hint_bases" list.
                        hint_bases[
                            hint_bases_index_past_last_prev +
                            hint_base_base_index
                        ] = (hint_base_base, hint_base_sane)
                # Else, this pseudo-superclass is neither an ignorable
                # user-defined PEP 484-compliant generic *NOR* an ignorable
                # 544-compliant protocol. In either case, this pseudo-superclass
                # is unignorable. In this case...
                else:
                    # Sign uniquely identifying this intrinsic pseudo-superclass
                    # if this pseudo-superclass is PEP-compliant *OR* "None"
                    # otherwise (i.e., if this pseudo-superclass is
                    # PEP-noncompliant).
                    hint_base_intrinsic_sign = get_hint_pep_sign_or_none(
                        hint_base)

                    # If this pseudo-superclass is PEP-compliant, this
                    # pseudo-superclass is a type hint conveying meaningful
                    # semantics. Yield the 2-tuple of:
                    # * This intrinsic pseudo-superclass.
                    # * This sign.
                    if hint_base_intrinsic_sign is not None:
                        yield hint_base_sane, hint_base_intrinsic_sign
                    # Else, this pseudo-superclass is an isinstanceable type
                    # conveying *NO* meaningful semantics and is thus
                    # effectively ignorable. Why? Because the caller already
                    # type-checks this pith against the generic subclassing this
                    # superclass and thus this superclass as well inside an
                    # isinstance() call (e.g., in the
                    # "CODE_PEP484585_GENERIC_PREFIX" snippet leveraged by the
                    # "beartype._check.code.codemain" submodule).
            # Else, this pseudo-superclass is ignorable.
            # else:
            #     print(f'Ignoring generic {repr(hint)} base {repr(hint_base)}...')
            #     print(f'Is generic {hint} base {repr(hint_base)} type? {isinstance(hint_base, type)}')

        #FIXME: *NICE*. For safety, we should also be doing something similar in
        #our make_check_expr()-driven dynamic code generator as well.
        # Nullify the previously visited pseudo-superclass in this list,
        # avoiding spurious memory leaks by encouraging garbage collection.
        hint_bases[hint_bases_index_curr] = None

        # Increment the 0-based index of the next visited pseudo-superclass in
        # this list *BEFORE* visiting that pseudo-superclass but *AFTER*
        # performing all other logic for the current pseudo-superclass.
        hint_bases_index_curr += 1

    # ....................{ POSTAMBLE                      }....................
    # Release this list. Pray for salvation, for we find none here.
    release_fixed_list(hint_bases)
