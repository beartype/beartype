#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **generic type hint
utilities** (i.e., callables generically applicable to both :pep:`484`-
and :pep:`585`-compliant generic classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype.typing import (
    List,
    Optional,
    Sequence,
    Tuple,
)
# from beartype._cave._cavemap import NoneTypeOr
from beartype._conf.confcls import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.cls.datacls import TYPES_PEP484544_GENERIC
from beartype._data.hint.datahintpep import (
    Hint,
    HintArgs,
    IterableHints,
    ListHints,
    SetHints,
)
from beartype._data.hint.datahinttyping import TypeException
from beartype._data.hint.pep.sign.datapepsigns import (
    # HintSignGeneric,
    HintSignTypeVar,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cache.pool.utilcachepoollistfixed import (
    # FIXED_LIST_SIZE_LARGE,
    FIXED_LIST_SIZE_MEDIUM,
    acquire_fixed_list,
    release_fixed_list,
)
from beartype._util.hint.pep.proposal.pep484.utilpep484generic import (
    get_hint_pep484_generic_bases_unerased,
    is_hint_pep484_generic,
)
from beartype._util.hint.pep.proposal.utilpep585 import (
    get_hint_pep585_generic_bases_unerased,
    is_hint_pep585_generic,
    is_hint_pep585_builtin_subscripted,
)
from beartype._util.kind.sequence.utilseqmake import make_stack
from beartype._util.module.utilmodtest import (
    is_object_module_thirdparty_blacklisted)
from itertools import count

# Intentionally import PEP 484-compliant "typing" type hint factories rather
# than possibly PEP 585-compliant "beartype.typing" type hint factories.
from typing import Generic

# ....................{ TESTERS                            }....................
@callable_cached
def is_hint_pep484585_generic(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **generic** (i.e., object that may *not* actually be a
    class despite subclassing at least one PEP-compliant type hint that also
    may *not* actually be a class).

    Specifically, this tester returns :data:`True` only if this object is
    either:

    * A :pep:`484`-compliant generic as tested by the lower-level
      :func:`.is_hint_pep484_generic` function.
    * A :pep:`585`-compliant generic as tested by the lower-level
      :func:`.is_hint_pep585_generic` function.

    This tester is memoized for efficiency.

    Caveats
    -------
    **Generics are not necessarily classes,** despite originally being declared
    as classes. Although *most* generics are classes, subscripting a generic
    class usually produces a generic non-class that *must* nonetheless be
    transparently treated as a generic class: e.g.,

    .. code-block:: pycon

       >>> from typing import Generic, TypeVar
       >>> S = TypeVar('S')
       >>> T = TypeVar('T')
       >>> class MuhGeneric(Generic[S, T]): pass
       >>> non_class_generic = MuhGeneric[S, T]
       >>> isinstance(non_class_generic, type)
       False

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a generic.

    See Also
    --------
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_typevars`
        Commentary on the relation between generics and parametrized hints.
    '''

    # True only if this hint is either a...
    is_hint_generic = (
        # PEP 484-compliant generic. Note this test trivially reduces to a fast
        # O(1) operation and is thus tested first.
        is_hint_pep484_generic(hint) or
        # PEP 585-compliant generic. Note this test is O(n) for n the number of
        # pseudo-superclasses originally subclassed by this generic and is thus
        # tested last.
        is_hint_pep585_generic(hint)
    )

    # If this hint is a PEP 484- or 585-compliant generic...
    if is_hint_generic:
        # Either:
        # * If this generic is already unsubscripted, this generic as is.
        # * Else, this generic is subscripted. In this case, the unsubscripted
        #   generic underlying this subscripted generic.
        hint_type = get_hint_pep484585_generic_type(hint)

        # For each possibly erased superclass of this generic, arbitrarily
        # iterated according to the method resolution order (MRO) for this
        # generic...
        for hint_base in hint_type.__mro__:
            # If this superclass is beartype-blacklisted (i.e., defined in a
            # third-party package or module that is hostile to runtime
            # type-checking), extend this blacklist to this entire generic by
            # immediately returning false.
            #
            # By default, beartype deeply type-checks a non-blacklisted generic
            # by iteratively type-checking all unerased superclasses of that
            # generic. Contrariwise, beartype only shallowly type-checks a
            # blacklisted generic by reducing that generic to a PEP-noncompliant
            # class effectively stripped of all PEP-compliant annotations.
            # Beartype-blacklisted generics are PEP-noncompliant and thus
            # fundamentally unsafe. For safety, we "strip" their genericity.
            if is_object_module_thirdparty_blacklisted(hint_base):
                return False
            # Else, this superclass is *NOT* beartype-blacklisted. In this case,
            # continue to the next such superclass of this generic.
        # Else, all superclasses of this generic are *NOT* beartype-blacklisted.

        # Return true in this case.
        return True
    # Else, this hint is *NOT* a PEP 484- or 585-compliant generic.

    # Return false in this case.
    return False


def is_hint_pep484585_generic_ignorable(hint: object) -> bool:
    '''
    :data:`True` only if the passed :pep:`484`- or :pep:`585`-compliant generic
    is ignorable.

    Specifically, this tester ignores *all* parametrizations of the
    :class:`typing.Generic` abstract base class (ABC) by one or more type
    variables. As the name implies, this ABC is generic and thus fails to impose
    any meaningful constraints. Since a type variable in and of itself also
    fails to impose any meaningful constraints, these parametrizations are
    safely ignorable in all possible contexts: e.g.,

    .. code-block:: python

       from typing import Generic, TypeVar
       T = TypeVar('T')
       def noop(param_hint_ignorable: Generic[T]) -> T: pass

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only safely callable by
    the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this :pep:`484`-compliant type hint is ignorable.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_origin_or_none
    # print(f'Testing generic hint {repr(hint)} deep ignorability...')

    # If this generic is the "typing.Generic" superclass directly parametrized
    # by one or more type variables (e.g., "typing.Generic[T]"), return true.
    #
    # Note that we intentionally avoid calling the
    # get_hint_pep_origin_type_isinstanceable_or_none() function here, which has
    # been intentionally designed to exclude PEP-compliant type hints
    # originating from "typing" type origins for stability reasons.
    if get_hint_pep_origin_or_none(hint) is Generic:
        # print(f'Testing generic hint {repr(hint)} deep ignorability... True')
        return True
    # Else, this generic is *NOT* the "typing.Generic" superclass directly
    # parametrized by one or more type variables and thus *NOT* an ignorable
    # non-protocol.
    #
    # Note that this condition being false is *NOT* sufficient to declare this
    # hint to be unignorable. Notably, the origin type originating both
    # ignorable and unignorable protocols is "Protocol" rather than "Generic".
    # Ergo, this generic could still be an ignorable protocol.
    # print(f'Testing generic hint {repr(hint)} deep ignorability... False')

    #FIXME: Probably insufficient. *shrug*
    return False


def is_hint_pep484585_generic_user(hint: object) -> bool:
    '''
    :data:`True` only if the passed :pep:`484`- or :pep:`585`-compliant generic
    is **user-defined** (i.e., defined by a third-party downstream codebase
    rather than CPython's first-party upstream standard library).

    Specifically, this tester returns :data:`True` only if this generic is
    neither:

    * A :pep:`484`- or :pep:`544`-compliant superclass defined by the
      :mod:`typing` module (e.g., :class:`typing.Generic`) *nor*...
    * A :pep:`585`-compliant superclass (e.g., ``list[T]``).

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to
    an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this is a user-defined generic.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_origin_type_or_none)

    # Return true only if...
    return (
        # This object is a generic that is neither...
        is_hint_pep484585_generic(hint) and not (
            # A subscripted PEP 585-compliant superclass (e.g., "list[T]")
            # *NOR*...
            is_hint_pep585_builtin_subscripted(hint) or
            # A subscripted or unsubscripted PEP 484- or 544-compliant
            # superclass defined by the standard "typing" module, including:
            # * "typing.Generic".
            # * "typing.Generic[S]".
            # * "typing.Protocol".
            # * "typing.Protocol[S]".
            get_hint_pep_origin_type_or_none(
                hint=hint,
                # Preserve "typing.Generic" and "typing.Protocol" as themselves,
                # as doing so dramatically simplifies this test. *shrug*
                is_self_fallback=True,
            ) in TYPES_PEP484544_GENERIC
        )
    )

# ....................{ GETTERS ~ args                     }....................
#FIXME: Memoize us up once debugged, please. *sigh*
#FIXME: Update the worst-case time complexity. Looks more like O(n**3), eh?
# def get_hint_pep484585_generic_args_full2(
#     # Mandatory parameters.
#     hint: object,
#
#     # Optional parameters.
#     hint_base_target: Optional[Hint] = None,
#     exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
#     exception_prefix: str = '',
# ) -> HintArgs:
#     '''
#     Tuple of the one or more **full child type hints** (i.e., complete tuple of
#     *all* type hints directly subscripting both the passed generic *and*
#     one or more pseudo-superclasses of this generic) transitively subscripting
#     the passed :pep:`484`- or :pep:`585`-compliant **generic** (i.e., class
#     superficially subclassing at least one PEP-compliant type hint that is
#     possibly *not* an actual class) if this object is a generic *or* raise an
#     exception otherwise (i.e., if this object is not a generic).
#
#     This getter greedily replaces in the passed tuple as many abstract
#     :pep:`484`-compliant **type variables** (i.e., :class:`typing.TypeVar`
#     objects) as there are concrete child type hints directly subscripting the
#     passed generic. Doing so effectively "bubbles up" these concrete children up
#     the class hierarchy into the "empty placeholders" established by the type
#     variables transitively subscripting all pseudo-superclasses of this generic.
#
#     This getter is guaranteed to return a non-empty tuple. By definition, a
#     generic subclasses one or more generic superclasses necessarily subscripted
#     by one or more child type hints.
#
#     This getter is memoized for efficiency.
#
#     Caveats
#     -------
#     **This getter is computationally complex in both space and time.** This
#     getter exhibits:
#
#     * Amortized :math:`O(1)` constant time complexity, thanks to memoization.
#     * Non-amortized worst-case :math:`O(jk)` quadratic time complexity for:
#
#       * :math:`j` the largest number of child type hints transitively
#         subscripting a pseudo-superclass of this generic.
#       * :math:`k` the total number of transitive pseudo-superclasses of this
#         generic.
#
#     **This getter is currently implemented with recursion.** Doing so yields a
#     relatively trivial algorithm at a relatively non-trivial increase in runtime
#     overhead, due to overhead associated with function calls in Python.
#
#     Parameters
#     ----------
#     hint : object
#         Generic type hint to be inspected.
#     hint_base_target : Optional[Hint] = None
#         **Pseudo-superclass target** (i.e., erased transitive pseudo-superclass
#         of the passed generic to specifically search, filter, and return the
#         child type hints of). Defaults to :data:`None`. Specifically:
#
#         * If this parameter is :data:`None`, this getter returns the complete
#           tuple of *all* type hints directly subscripting both the passed
#           generic *and* one or more pseudo-superclasses of this generic.
#         * If this parameter is *not* :data:`None`, this getter returns the
#           partial tuple of *only* type hints directly subscripting both the
#           passed generic *and* this passed pseudo-superclass of this generic.
#
#         This parameter is typically passed to deduce whether two arbitrary
#         generics are related according to the :func:`beartype.door.is_subhint`
#         relation. If all child type hints in the tuple returned by this getter
#         passed some generic and its pseudosuperclass are subhints of all
#         child type hints in the tuple returned by this getter passed *only*
#         that pseudosuperclass, then that generic is necessarily a subhint of
#         that pseudosuperclass. Look. Just go with it, people.
#     exception_cls : TypeException
#         Type of exception to be raised. Defaults to
#         :exc:`.BeartypeDecorHintPep484585Exception`.
#     exception_prefix : str, optional
#         Human-readable substring prefixing the representation of this object in
#         the exception message. Defaults to the empty string.
#
#     Returns
#     -------
#     tuple
#         Tuple of the one or more full child type hints transitively subscripting
#         this generic.
#
#     Raises
#     ------
#     exception_cls
#         If this hint is either:
#
#         * Neither a :pep:`484`- nor :pep:`585`-compliant generic.
#         * A :pep:`484`- or :pep:`585`-compliant generic subclassing *no*
#           pseudo-superclasses.
#
#     Examples
#     --------
#     .. code-block:: python
#
#        >>> from beartype.typing import Generic, TypeVar
#        >>> from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
#        ...     get_hint_pep484585_generic_args_full)
#
#        >>> S = TypeVar('S')
#        >>> T = TypeVar('T')
#
#        >>> class GenericSuperclass(Generic[S], list[T]): pass
#        >>> class GenericList(list[complex]): pass
#        >>> class GenericSubclass(GenericSuperclass[int, T], GenericList): pass
#
#        >>> get_hint_pep484585_generic_args_full(GenericSuperclass)
#        (S, T)
#        >>> get_hint_pep484585_generic_args_full(GenericSuperclass[int, float])
#        (int, float)
#        >>> get_hint_pep484585_generic_args_full(GenericSubclass)
#        (int, T, complex)
#        >>> get_hint_pep484585_generic_args_full(GenericSubclass[float])
#        (int, float, complex)
#        >>> get_hint_pep484585_generic_args_full(GenericSubclass[float])
#        (int, float, complex)
#     '''
#     assert isinstance(exception_cls, type), (
#         f'{repr(exception_cls)} not exception type.')
#     assert isinstance(exception_prefix, str), (
#         f'{repr(exception_prefix)} not string.')
#
#     # ....................{ IMPORTS                        }....................
#     # Avoid circular import dependencies.
#     from beartype._util.hint.pep.utilpepget import (
#         get_hint_pep_args,
#         # get_hint_pep_origin_or_none,
#         # get_hint_pep_origin_type_or_none,
#         get_hint_pep_sign_or_none,
#     )
#
#     # ....................{ PREAMBLE                       }....................
#     #FIXME: Preserved due to the large useful comment below, which we should
#     #copy-paste elsewhere. Still, explicit is better than implicit. If the
#     #caller wants the unsubscripted generic underlying the passed target, then
#     #they need to explicitly pass that instead of the passed target. In other
#     #words, defer to the caller here. They run the show: not us.
#     # # If the caller explicitly passed a pseudo-superclass target...
#     # #
#     # # Note that this is the common case for this getter and thus tested first.
#     # if hint_base_target:
#     #     # If this pseudo-superclass target is this generic, this
#     #     # pseudo-superclass target is effectively meaningless (albeit
#     #     # technically valid). In this case, silently ignore this
#     #     # pseudo-superclass target.
#     #     if hint is hint_base_target:
#     #         hint_base_target = None
#     #     # Else, this pseudo-superclass target is *NOT* this generic. In this
#     #     # case...
#     #     else:
#     #         # Unsubscripted generic underlying this possibly subscripted target
#     #         # pseudo-superclass generic. For search purposes, *ANY* child hints
#     #         # subscripting this generic are not only irrelevant but harmful --
#     #         # promoting false negatives in higher-level functions (e.g.,
#     #         # beartype.door.is_subhint()) internally leveraging this lower-level
#     #         # getter. Ignoring these child hints is thus imperative. Since
#     #         # deciding child hint compatibility between the passed generic and
#     #         # this target pseudo-superclass is a non-trivial decision problem,
#     #         # this lower-level getter defers that problem to the caller by
#     #         # unconditionally returning the same result regardless of child
#     #         # hints subscripting this target pseudo-superclass.
#     #         #
#     #         # Consider the PEP 484-compliant catch-all "typing.Any", for
#     #         # example. Clearly, this getter should return the same tuple when
#     #         # passed an unsubscripted target pseudo-superclass as when passed a
#     #         # target pseudo-superclass subscripted by "typing.Any": e.g.,
#     #         #     >>> from typing import Any, Generic
#     #         #     >>> class MuhGeneric[S, T](Generic[S, T]): pass
#     #         #     >>> get_hint_pep484585_generic_args_full(
#     #         #     ...     MuhGeneric, hint_base_target=Generic)
#     #         #     (S, T)
#     #         #     >>> get_hint_pep484585_generic_args_full(
#     #         #     ...     MuhGeneric, hint_base_target=Generic[Any])
#     #         #     (S, T)
#     #         #     >>> get_hint_pep484585_generic_args_full(
#     #         #     ...     MuhGeneric, hint_base_target=Generic[S, T])
#     #         #     (S, T)
#     #         #     >>> get_hint_pep484585_generic_args_full(
#     #         #     ...     MuhGeneric, hint_base_target=Generic[int, float])
#     #         #     (S, T)
#     #         hint_base_target = get_hint_pep484585_generic_type(  # pyright: ignore
#     #             hint=hint_base_target,
#     #             exception_cls=exception_cls,
#     #             exception_prefix=exception_prefix,
#     #         )
#     # # Else, the caller passed *NO* pseudosuperclass target. In this case...
#
#     # ....................{ LOCALS                         }....................
#     # List of the zero or more child hints transitively subscripting this
#     # generic, which this depth-first search (DFS) computes below and then
#     # eventually returns as the value returned by this getter. In other words,
#     # this is the "thing we are *REALLY* interested in."
#     hint_full_args = []
#
#     # Unvisited pseudo-superclass stack (i.e., efficiently poppable list of
#     # *ALL* transitive pseudo-superclasses of this generic, intentionally
#     # reordered in reverse order to enable the non-recursive depth-first search
#     # (DFS) performed below to both visit and pop these pseudo-superclasses in
#     # the expected order), seeded with metadata describing the root generic.
#     #
#     # Each item of this stack is a 5-list matched by the
#     # "_HintFullBase" type hint describing metadata of an unvisited
#     # pseudo-superclass. See the docstring for further details.
#     hint_full_bases: _HintFullBases = [(
#         # This generic.
#         hint,
#
#         # Poppable stack of the zero or more child hints directly subscripting
#         # this generic.
#         #
#         # Note that an alternative to producing a stack would be to additionally
#         # record the currently indexed child hint of this tuple *AND* the total
#         # number of child hints in this tuple. Although trivial, doing so would
#         # necessitate additional space *AND* time consumption (e.g., to both
#         # assign and access this metadata). Since the average Python statement
#         # is so slow, a 2-liner producing a poppable stack minimizes the number
#         # of Python statements and is thus (almost certainly) faster.
#         make_stack(get_hint_pep_args(hint)),
#
#         # List of the zero or more child hints transitively subscripting this
#         # generic, which this depth-first search (DFS) computes below and then
#         # eventually returns as the value returned by this getter. In other
#         # words, this is the "thing we are *REALLY* interested in."
#         hint_full_args,
#
#         # Metadata describing the direct parent pseudo-superclass of this
#         # generic. By definition, this generic is the root of this n-ary tree
#         # and thus has *NO* parent (either direct or indirect).
#         None,
#     )]
#
#     # Set of the unique identifiers of all transitive pseudo-superclasses of
#     # this generic that have been previously visited by this depth-first search
#     # (DFS). Maintaining this set enables us to efficiently decide, when
#     # visiting any given item of this stack, whether this DFS is currently
#     # recursing down into *OR* back out of this item.
#     hint_base_ids_seen: SetHints = set()
#
#     # ....................{ SEARCH                         }....................
#     # With at least one transitive pseudo-superclass of this generic remains
#     # unvisited...
#     while hint_full_bases:
#         # Metadata describing the currently visited transitive pseudo-superclass
#         # of this generic defined as the top-most item of this stack.
#         #
#         # Note that we intentionally avoid popping this pseudo-superclass off
#         # this stack yet. We only pop a pseudo-superclass off this stack *AFTER*
#         # resolving all child pseudo-superclasses of that pseudo-superclass,
#         # which simulates the "backing out" performed by genuine recursion.
#         hint_base_data = hint_full_bases[-1]
#
#         # Currently visited transitive pseudo-superclass of this generic.
#         hint_base = hint_base_data[_HINT_FULL_BASES_INDEX_HINT]
#
#         # Unique identifier of this pseudo-superclass.
#         hint_full_base_id = id(hint_base)
#
#         # If...
#         if (
#             # This DFS has *NOT* yet visited this pseudo-superclass...
#             hint_full_base_id not in hint_base_ids_seen and
#             # This pseudo-superclass is itself a PEP 484- or 585-compliant
#             # user-defined generic. Standard generics (i.e., that are *NOT*
#             # user-defined) have *NO* pseudo-superclasses and are thus omitted.
#             # Examples of standard generics include:
#             # * "dict[str, U]".
#             # * "typing.Generic[S, int]").
#             # * "typing.Protocol[float, T]").
#             #
#             # Note that this tester is mildly slower than the prior test and
#             # thus intentionally tested later.
#             is_hint_pep484585_generic_user(hint_base)
#         # Then this DFS is currently recursing down into the child
#         # pseudo-superclasses of this pseudo-superclass. In this case...
#         ):
#             # Record this pseudo-superclass as having now been visited.
#             hint_base_ids_seen.add(hint_full_base_id)
#
#             # Tuple of the one or more child pseudo-superclasses of this
#             # pseudo-superclass.
#             # print(f'Introspecting generic {hint} unerased bases...')
#             hint_child_bases = get_hint_pep484585_generic_bases_unerased(
#                 hint=hint_base,
#                 exception_cls=exception_cls,
#                 exception_prefix=exception_prefix,
#             )
#             # print(f'Generic {hint} unerased bases: {hint_child_bases}')
#
#             # For each child pseudo-superclass of this pseudo-superclass,
#             # intentionally iterated in reverse order so as to ensure that the
#             # *FIRST* child pseudo-superclass is the *LAST* item of this stack
#             # (and thus the *FIRST* unvisited pseudo-superclass to be visited by
#             # this depth-first search (DFS) next).
#             #
#             # Note that the reversed() builtin is well-known to be the most
#             # efficient means of producing a reversed iterable for iteration
#             # purposes. See also:
#             #     https://stackoverflow.com/a/16514411/2809027
#             for hint_child_base in reversed(hint_child_bases):
#                 # Push metadata describing this unvisited child
#                 # pseudo-superclass onto this stack.
#                 hint_full_bases.append((
#                     # This child pseudo-superclass.
#                     hint_child_base,
#
#                     #FIXME: Inefficient. If this child pseudo-superclass is
#                     #a leaf terminal, this serves no purpose whatsoever. In
#                     #that case:
#                     #* This stack should just be set to "None".
#                     #* The list below should be set to
#                     #  "get_hint_pep_args(hint_child_base)".
#                     #Probably? Contemplate deeper, please.
#                     #FIXME: Actually, the optimal way to do this is probably:
#                     #* Rename "_HINT_FULL_BASES_INDEX_ARGS" to
#                     #  "_HINT_FULL_BASES_INDEX_ARGS_STACK".
#                     #* Define a new "_HINT_FULL_BASES_INDEX_ARGS".
#                     #* Pass as follows both here and above:
#                     #      get_hint_pep_args(hint_child_base),  # ARGS
#                     #      None,  # ARGS_STACK
#                     #      None,  # FULL_ARGS
#                     #
#                     #Refactor as follows: it then becomes the responsibility
#                     #of the "else:" branch below to conditionally initialize
#                     #the "ARGS_STACK" and "FULL_ARGS" of the *PARENT*
#                     #pseudo-superclass as needed.
#
#                     # Poppable stack of the zero or more child hints
#                     # directly subscripting this child pseudo-superclass.
#                     make_stack(get_hint_pep_args(hint_child_base)),
#
#                     # List of the zero or more child hints transitively
#                     # subscripting this child pseudo-superclass.
#                     [],
#
#                     # Metadata describing the direct parent
#                     # pseudo-superclass of this child pseudo-superclass.
#                     hint_base_data,
#                 ))
#         # Else, either:
#         # * This DFS has already visited this pseudo-superclass *OR*...
#         # * This pseudo-superclass is a "terminal" leaf generic *OR*...
#         # * This pseudo-superclass is *NOT* a generic.
#         #
#         # In any case, this DFS should *NOT* recurse (back) down into this
#         # pseudo-superclass. Therefore, this DFS is currently recursing back up
#         # out of this pseudo-superclass into its parent pseudo-superclass.
#         else:
#             # Pop this pseudo-superclass off this stack.
#             hint_full_bases.pop()
#
#             # Metadata describing the direct parent pseudo-superclass of this
#             # pseudo-superclass.
#             hint_base_super_data = hint_base_data[
#                 _HINT_FULL_BASES_INDEX_PARENT]
#             # print(f'Resuming generic {hint} pseudo-superclass {hint_base} args {hint_base_args}...')
#
#             # If this pseudo-superclass has a parent pseudo-superclass (i.e.,
#             # this pseudo-superclass is *NOT* the passed root generic and is
#             # thus a transitive child of this generic)...
#             if hint_base_super_data:
#                 # Poppable stack of the zero or more child hints directly
#                 # subscripting this parent pseudo-superclass.
#                 hint_base_super_args = hint_base_super_data[
#                     _HINT_FULL_BASES_INDEX_ARGS]
#
#                 # List of the zero or more child hints transitively subscripting
#                 # this parent pseudo-superclass of this pseudo-superclass.
#                 hint_base_super_full_args = hint_base_super_data[
#                     _HINT_FULL_BASES_INDEX_FULL_ARGS]
#
#                 # List of the zero or more child hints transitively subscripting
#                 # this pseudo-superclass.
#                 hint_base_full_args = hint_base_data[
#                     _HINT_FULL_BASES_INDEX_FULL_ARGS]
#
#                 # # Possibly modifiable sequence of the zero or more full child hints
#                 # # transitively subscripting this pseudo-superclass if this
#                 # # pseudo-superclass is either the passed target pseudo-superclass
#                 # # *OR* a subclass of that target pseudo-superclass.
#                 # hint_base_target_args: Sequence[Hint] = ()
#
#                 # If...
#                 if (
#                     # This parent pseudo-superclass of this pseudo-superclass is
#                     # still directly subscripted by one or more child hints that
#                     # have yet to "bubble up" the class hierarchy (i.e., by
#                     # replacing the first unused type variable transitively
#                     # subscripting this child pseudo-superclass) *AND*...
#                     hint_base_super_args and
#                     # This pseudo-superclass is transitively subscripted by at
#                     # least one child hint.
#                     hint_base_full_args
#                 ):
#                     # For the 0-based index of each child hint transitively
#                     # subscripting this pseudo-superclass and this hint...
#                     for hint_base_full_arg_index, hint_base_full_arg in (
#                         enumerate(hint_base_full_args)):
#                         # Sign uniquely identifying this child hint transitively
#                         # subscripting this pseudo-superclass if any *OR*
#                         # "None" (i.e., if this child hint is a simple type).
#                         hint_base_arg_sign = get_hint_pep_sign_or_none(
#                             hint_base_full_arg)
#
#                         # If this hint is a type variable...
#                         if hint_base_arg_sign is HintSignTypeVar:
#                             # "Bubble up" the currently unassigned child hint
#                             # directly subscripting this parent
#                             # pseudo-superclass into the "empty placeholder"
#                             # signified by this type variable in this list of
#                             # child hints transitively subscripting this
#                             # pseudo-superclass.   <-- lolwat
#                             hint_base_full_args[hint_base_full_arg_index] = (
#                                 hint_base_super_args.pop())
#                             # print(f'Bubbled up generic {hint} arg {hint_args[hint_args_index_curr]}...')
#                             # print(f'...into pseudo-superclass {hint_base} args {hint_base_args}!')
#
#                             # If all child hints directly subscripting this
#                             # parent pseudo-superclass have now been bubbled up,
#                             # halt this nested iteration.
#                             if not hint_base_super_args:
#                                 break
#                             # Else, one or more child hints directly
#                             # subscripting this parent pseudo-superclass have
#                             # yet to be bubbled up. In this case, continue to
#                             # the next such hint.
#                         # Else, this hint is *NOT* a type variable. In this
#                         # case, preserve this hint and continue to the next.
#                 # Else, either this pseudo-superclass is transitively
#                 # unsubscripted *OR* all child hints directly subscripting this
#                 # parent pseudo-superclass of this pseudo-superclass have
#                 # already been bubbled up. In either case, no further bubbling
#                 # is warranted.
#
#                 # If this pseudo-superclass is the target pseudo-superclass...
#                 if hint_base is hint_base_target:
#                     # Immediately return the list of the zero or more child
#                     # hints transitively subscripting this target
#                     # pseudo-superclass, effectively short-circuiting all
#                     # further recursion.
#                     #
#                     # Note that this short-circuiting is one of several reasons
#                     # to prefer a non-recursive algorithm. This algorithm was
#                     # initially implemented recursively for supposed simplicity;
#                     # however, doing so introduced significant unforeseen
#                     # complications by effectively preventing short-circuiting.
#                     # After all, a recursive algorithm cannot short-circuit up
#                     # out of a deeply nested recursive call stack.
#                     return hint_base_full_args
#                 # Else, either no pseudo-superclass is being targeted *OR* a
#                 # pseudo-superclass is being targeted but this is not that
#                 # pseudo-superclass. In either case, noop.
#
#                 # Append this possibly modified list of all child hints
#                 # transitively subscripting this pseudo-superclass to this list
#                 # of all child hints transitively subscripting this parent
#                 # pseudo-superclass of this pseudo-superclass.
#                 hint_base_super_full_args.extend(hint_base_full_args)
#                 # print(f'Inspected generic {hint} pseudo-superclass {hint_base} args {hint_base_args}!')
#
#     # ....................{ RETURN                         }....................
#     # If the caller passed a target pseudo-superclass, that target *CANNOT* be a
#     # pseudo-superclass of this generic. Why? Because if that target had been a
#     # pseudo-superclass of this generic, then the above DFS would have found
#     # that target and immediately returned the desired list on doing so.
#     # However, that DFS failed to return and thus find that target. In this
#     # case, raise an exception.
#     if hint_base_target:
#         raise exception_cls(
#             f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
#             f'pseudo-superclass target {repr(hint_base_target)} not found.'
#         )
#     # Else, the caller did *NOT* pass a target pseudo-superclass.
#
#     # Return all child hints transitively subscripting this generic.
#     return hint_full_args


#FIXME: Ideally, all of the below should themselves be annotated as ": Hint".
#Mypy likes that but pyright hates that. This is why we can't have good things.
_HintFullBase = Tuple[Hint, ListHints, ListHints, '_HintFullBase']
'''
PEP-compliant type hint matching each **unvisited pseudo-superclass** (i.e.,
item of the ``hint_full_bases`` fixed list local to the
:func:`.get_hint_pep484585_generic_args_full` getter, describing each
pseudo-superclass of the generic passed to that getter that has yet to be
internally visited by the depth-first search (DFS) performed by that getter).
'''


_HintFullBases = List[_HintFullBase]
'''
PEP-compliant type hint matching the ``hint_full_bases`` fixed list local to the
:func:`.get_hint_pep484585_generic_args_full` getter.
'''


# Iterator yielding the next integer incrementation starting at 0, to be safely
# deleted *AFTER* defining the following 0-based indices via this iterator.
__hint_full_bases_counter = count(start=0, step=1)


_HINT_FULL_BASES_INDEX_HINT = next(__hint_full_bases_counter)
'''
0-based index into each **pseudo-superclass node** (i.e., node of an n-ary tree
describing a transitive pseudo-superclass of the :pep:`484`- or
:pep:`585`-compliant generic passed to the
:func:`.get_hint_pep484585_generic_args_full` getter) stored in the
``hint_full_bases`` fixed list local to that getter, providing the currently
visited pseudo-superclass itself.
'''


_HINT_FULL_BASES_INDEX_ARGS = next(__hint_full_bases_counter)
'''
0-based index into each **pseudo-superclass node** (i.e., node of an n-ary tree
describing a transitive pseudo-superclass of the :pep:`484`- or
:pep:`585`-compliant generic passed to the
:func:`.get_hint_pep484585_generic_args_full` getter) stored in the
``hint_full_bases`` fixed list local to that getter, providing the currently
visited pseudo-superclass' **direct child type hint stack** (i.e., list of the
zero or more child hints directly subscripting this generic in reverse order,
embodying an efficiently poppable stack of these hints).
'''


_HINT_FULL_BASES_INDEX_FULL_ARGS = next(__hint_full_bases_counter)
'''
0-based index into each **pseudo-superclass node** (i.e., node of an n-ary tree
describing a transitive pseudo-superclass of the :pep:`484`- or
:pep:`585`-compliant generic passed to the
:func:`.get_hint_pep484585_generic_args_full` getter) stored in the
``hint_full_bases`` fixed list local to that getter, providing the currently
visited pseudo-superclass' **...** (i.e., ...).
'''


_HINT_FULL_BASES_INDEX_PARENT = next(__hint_full_bases_counter)
'''
0-based index into each **pseudo-superclass node** (i.e., node of an n-ary tree
describing a transitive pseudo-superclass of the :pep:`484`- or
:pep:`585`-compliant generic passed to the
:func:`.get_hint_pep484585_generic_args_full` getter) stored in the
``hint_full_bases`` fixed list local to that getter, providing the currently
visited pseudo-superclass' **...** (i.e., ...).
'''




# Delete the above counter for safety and sanity in equal measure.
del __hint_full_bases_counter


#FIXME: *EXCISE EVERYTHING BELOW* pertaining to this now-obsolete
#get_hint_pep484585_generic_args_full() getter, please.
#FIXME: Unit test up "hint_base_target", please.
def get_hint_pep484585_generic_args_full(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_base_target: Optional[Hint] = None,
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> HintArgs:
    '''
    Tuple of the one or more **full child type hints** (i.e., complete tuple of
    *all* type hints directly subscripting both the passed generic *and*
    one or more pseudo-superclasses of this generic) transitively subscripting
    the passed :pep:`484`- or :pep:`585`-compliant **generic** (i.e., class
    superficially subclassing at least one PEP-compliant type hint that is
    possibly *not* an actual class) if this object is a generic *or* raise an
    exception otherwise (i.e., if this object is not a generic).

    This getter greedily replaces in the passed tuple as many abstract
    :pep:`484`-compliant **type variables** (i.e., :class:`typing.TypeVar`
    objects) as there are concrete child type hints directly subscripting the
    passed generic. Doing so effectively "bubbles up" these concrete children up
    the class hierarchy into the "empty placeholders" established by the type
    variables transitively subscripting all pseudo-superclasses of this generic.

    This getter is guaranteed to return a non-empty tuple. By definition, a
    generic subclasses one or more generic superclasses necessarily subscripted
    by one or more child type hints.

    This getter is memoized for efficiency.

    Caveats
    -------
    **This getter is computationally complex in both space and time.** This
    getter exhibits:

    * Amortized :math:`O(1)` constant time complexity, thanks to memoization.
    * Non-amortized worst-case :math:`O(jk)` quadratic time complexity for:

      * :math:`j` the largest number of child type hints transitively
        subscripting a pseudo-superclass of this generic.
      * :math:`k` the total number of transitive pseudo-superclasses of this
        generic.

    **This getter is currently implemented with recursion.** Doing so yields a
    relatively trivial algorithm at a relatively non-trivial increase in runtime
    overhead, due to overhead associated with function calls in Python.

    Parameters
    ----------
    hint : object
        Generic type hint to be inspected.
    hint_base_target : Optional[Hint] = None
        **Pseudo-superclass target** (i.e., erased transitive pseudo-superclass
        of the passed generic to specifically search, filter, and return the
        child type hints of). Defaults to :data:`None`. Specifically:

        * If this parameter is :data:`None`, this getter returns the complete
          tuple of *all* type hints directly subscripting both the passed
          generic *and* one or more pseudo-superclasses of this generic.
        * If this parameter is *not* :data:`None`, this getter returns the
          partial tuple of *only* type hints directly subscripting both the
          passed generic *and* this passed pseudo-superclass of this generic.

        This parameter is typically passed to deduce whether two arbitrary
        generics are related according to the :func:`beartype.door.is_subhint`
        relation. If all child type hints in the tuple returned by this getter
        passed some generic and its pseudosuperclass are subhints of all
        child type hints in the tuple returned by this getter passed *only*
        that pseudosuperclass, then that generic is necessarily a subhint of
        that pseudosuperclass. Look. Just go with it, people.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`.BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    tuple
        Tuple of the one or more full child type hints transitively subscripting
        this generic.

    Raises
    ------
    exception_cls
        If this hint is either:

        * Neither a :pep:`484`- nor :pep:`585`-compliant generic.
        * A :pep:`484`- or :pep:`585`-compliant generic subclassing *no*
          pseudo-superclasses.

    Examples
    --------
    .. code-block:: python

       >>> from beartype.typing import Generic, TypeVar
       >>> from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
       ...     get_hint_pep484585_generic_args_full)

       >>> S = TypeVar('S')
       >>> T = TypeVar('T')

       >>> class GenericSuperclass(Generic[S], list[T]): pass
       >>> class GenericList(list[complex]): pass
       >>> class GenericSubclass(GenericSuperclass[int, T], GenericList): pass

       >>> get_hint_pep484585_generic_args_full(GenericSuperclass)
       (S, T)
       >>> get_hint_pep484585_generic_args_full(GenericSuperclass[int, float])
       (int, float)
       >>> get_hint_pep484585_generic_args_full(GenericSubclass)
       (int, T, complex)
       >>> get_hint_pep484585_generic_args_full(GenericSubclass[float])
       (int, float, complex)
       >>> get_hint_pep484585_generic_args_full(GenericSubclass[float])
       (int, float, complex)
    '''
    assert isinstance(exception_cls, type), (
        f'{repr(exception_cls)} not exception type.')
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    #FIXME: Unit test us up, please.
    # If the caller explicitly passed a pseudosuperclass target...
    #
    # Note that this is the common case for this getter and thus tested first.
    if hint_base_target:
        # Unsubscripted generic underlying this possibly subscripted target
        # pseudo-superclass generic. For search purposes, *ANY* child hints
        # subscripting this generic are not only irrelevant but harmful --
        # promoting false negatives in higher-level functions (e.g.,
        # beartype.door.is_subhint()) internally leveraging this lower-level
        # getter. Ignoring these child hints is thus imperative. Since deciding
        # child hint compatibility between the passed generic and this target
        # pseudo-superclass is a non-trivial decision problem, this lower-level
        # getter defers that problem to the caller by unconditionally returning
        # the same result regardless of child hints subscripting this target
        # pseudo-superclass.
        #
        # Consider the PEP 484-compliant catch-all "typing.Any", for example.
        # Clearly, this getter should return the same tuple when passed an
        # unsubscripted target pseudo-superclass as when passed a target
        # pseudo-superclass subscripted by "typing.Any": e.g.,
        #     >>> from typing import Any, Generic
        #     >>> class MuhGeneric[S, T](Generic[S, T]): pass
        #     >>> get_hint_pep484585_generic_args_full(
        #     ...     MuhGeneric, hint_base_target=Generic)
        #     (S, T)
        #     >>> get_hint_pep484585_generic_args_full(
        #     ...     MuhGeneric, hint_base_target=Generic[Any])
        #     (S, T)
        #     >>> get_hint_pep484585_generic_args_full(
        #     ...     MuhGeneric, hint_base_target=Generic[S, T])
        #     (S, T)
        #     >>> get_hint_pep484585_generic_args_full(
        #     ...     MuhGeneric, hint_base_target=Generic[int, float])
        #     (S, T)
        hint_base_target = get_hint_pep484585_generic_type(  # pyright: ignore
            hint=hint_base_target,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

        # Partial tuple of *ONLY* hints directly
        # subscripting both this generic and this target pseudo-superclass.
        _, hint_base_target_args_full = _get_hint_pep484585_generic_args_full(
            hint, hint_base_target, exception_cls, exception_prefix)

        # If *NO* hints directly subscript both this generic and target
        # pseudo-superclass, raise an exception.
        if not hint_base_target_args_full:
            raise exception_cls(
                f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
                f'pseudo-superclass target {repr(hint_base_target)} not found.'
            )
        # Else, one or more hints directly subscript both this generic and
        # target pseudo-superclass.

        # Return this partial tuple of these hints.
        return hint_base_target_args_full
    # Else, the caller passed *NO* pseudosuperclass target. In this case...

    # Complete tuple of *ALL* hints directly subscripting both this generic and
    # *ALL* pseudo-superclasses of this generic.
    hint_args_full, _ = _get_hint_pep484585_generic_args_full(
        hint, hint_base_target, exception_cls, exception_prefix)

    # If *NO* hints directly subscript both this generic and *ALL*
    # pseudo-superclasses of this generic, raise an exception.
    if not hint_args_full:
        raise exception_cls(
            f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
            f'pseudo-superclasses not found.'
        )
    # Else, one or more hints directly subscript both this generic and *ALL*
    # pseudo-superclasses of this generic.

    # Return this complete tuple of these hints.
    return hint_args_full


#FIXME: Refactor away this recursion into a non-recursive algorithm. This
#recursion currently prevents us from short-circuiting after finding the desired
#"hint_base_target", dramatically reducing efficiency in the common case. The
#current recursion also turns out to be unreadable and unmaintainable. Ugh!
@callable_cached
def _get_hint_pep484585_generic_args_full(
    hint: object,
    hint_base_target: Optional[Hint],
    exception_cls: TypeException,
    exception_prefix: str,
) -> Tuple[HintArgs, HintArgs]:
    '''
    Lower-level memoized private getter underlying the higher-level unmemoized
    public :func:`.get_hint_pep484585_generic_args_full` getter.

    This private getter enables that public getter to present a user-friendly
    API while still benefiting from extreme memoization.

    Returns
    -------
    Tuple[tuple, tuple]
        2-tuple ``(hint_args_full, hint_base_target_args_full)``, where:

        * ``hint_args_full`` is the complete tuple of *all* type hints directly
          subscripting both the passed generic and *all* pseudo-superclasses of
          this generic.
        * ``hint_base_target_args_full`` is the partial tuple of *only* type
          hints directly subscripting both the passed generic and the passed
          target pseudo-superclass of this generic.
    '''
    # print(f'Introspecting generic {hint} full arguments...')

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        get_hint_pep_origin_or_none,
        get_hint_pep_sign_or_none,
    )

    # ....................{ LOCALS                         }....................
    # List of *ALL* child hints transitively subscripting this generic, to be
    # returned as a coerced tuple.
    hint_args_full: Sequence[Hint] = []

    # Sequence of *ONLY* child hints transitively subscripting both this generic
    # and this target pseudo-superclass of this generic.
    hint_base_target_args_full: HintArgs = ()

    # Tuple of the zero or more child type hints directly subscripting this
    # generic.
    hint_args = get_hint_pep_args(hint)

    # 0-based index of the currently visited child type hint directly
    # subscripting this generic in this tuple.
    hint_args_index_curr = 0

    # Either:
    # * If this generic is directly subscripted by at least one child type hint,
    #   the 0-based index of the last such hint in this tuple.
    # * Else, this generic is directly unsubscripted. In this case, "-1".
    hint_args_index_last = len(hint_args) - 1

    # Tuple of the one or more unerased pseudo-superclasses originally listed as
    # superclasses prior to their type erasure by this generic.
    # print(f'Introspecting generic {hint} unerased bases...')
    hint_bases = get_hint_pep484585_generic_bases_unerased(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # print(f'Generic {hint} unerased bases: {hint_bases}')

    # ....................{ SEARCH                         }....................
    # For each pseudo-superclass of this generic...
    for hint_base in hint_bases:
        print(f'Inspecting generic {hint} pseudo-superclass {hint_base}...')

        # Possibly modifiable sequence of the zero or more full child type hints
        # transitively subscripting this pseudo-superclass.
        hint_base_args: Sequence[Hint] = ()

        # Possibly modifiable sequence of the zero or more full child type hints
        # transitively subscripting this pseudo-superclass if this
        # pseudo-superclass is either the passed target pseudo-superclass *OR* a
        # subclass of that target pseudo-superclass.
        hint_base_target_args: Sequence[Hint] = ()

        # If both of the following conditions are satisfied:
        if (
            # This pseudo-superclass is neither:
            # * A root PEP 484-compliant "Generic[...]" type hint (e.g.,
            #   "typing.Generic[S, int]").
            # * A root PEP 544-compliant "Protocol[...]" type hint (e.g.,
            #   "typing.Protocol[float, T]").
            #
            # Neither of these kinds of root "terminal" generics are valid
            # generics from the perspective of this getter function, which
            # expects a user-defined class transitively subscripting one or more
            # of these kinds of root "terminal" generics.
            #
            # Recursively passing either of these kinds of root "terminal"
            # generics to this getter would raise an exception.
            get_hint_pep_origin_or_none(hint_base) not in (
                TYPES_PEP484544_GENERIC) and
            # This pseudo-superclass is a PEP 484- or 585-compliant generic.
            # Note that this tester is mildly slower than the prior test and
            # thus intentionally tested later.
            is_hint_pep484585_generic(hint_base)
        ):
            # Tuple of the zero or more full child type hints transitively
            # subscripting this pseudo-superclass, obtained by recursively
            # calling this getter again with this pseudo-superclass...
            hint_base_args, hint_base_target_args = (
                _get_hint_pep484585_generic_args_full(
                    hint_base,
                    hint_base_target,
                    exception_cls,
                    exception_prefix,
                ))
            # print(f'hint_base_args: {hint_base_args}')
        # Else, this pseudo-superclass is either not a generic *OR* is a generic
        # but is a root "terminal" generic. In either case, non-recursively
        # obtain the tuple of the zero or more child type hints directly
        # subscripting this pseudo-superclass.
        else:
            hint_base_args = get_hint_pep_args(hint_base)
        print(f'Resuming generic {hint} pseudo-superclass {hint_base} args {hint_base_args}...')
        print(f'hint_args: {hint_args}')
        print(f'hint_args_index_curr: {hint_args_index_curr}')
        print(f'hint_args_index_last: {hint_args_index_last}')

        # If...
        if (
            # This pseudo-superclass is subscripted by at least one child type
            # hint *AND*...
            hint_base_args and
            # The passed generic is still directly subscripted by one or more
            # child type hints that have yet to be "bubbled up" the class
            # hierarchy (i.e., by replacing the first unused PEP 484-compliant
            # type variable transitively subscripting this pseudo-superclass).
            hint_args_index_curr <= hint_args_index_last
        ):
            # Modifiable list of the one or more child type hints subscripting
            # this pseudo-superclass, coerced from this tuple.
            hint_base_args = list(hint_base_args)

            # For the 0-based index of each full child type hint transitively
            # subscripting this pseudo-superclass and this hint...
            for hint_base_arg_index, hint_base_arg in enumerate(hint_base_args):
                # Sign uniquely identifying this child type hint transitively
                # subscripting this pseudo-superclass if any *OR* "None".
                hint_base_arg_sign = get_hint_pep_sign_or_none(hint_base_arg)

                # If this hint is a PEP 484-compliant type variable...
                if hint_base_arg_sign is HintSignTypeVar:
                    # "Bubble up" the currently unassigned child type hint
                    # directly subscripting the passed generic into the
                    # "empty placeholder" signified by this type variable in
                    # this list of child type hints transitively subscripting
                    # this pseudo-superclass of this generic. <-- lolwat
                    hint_base_args[hint_base_arg_index] = hint_args[
                        hint_args_index_curr]
                    print(f'Bubbled up generic {hint} arg {hint_args[hint_args_index_curr]}...')
                    print(f'...into pseudo-superclass {hint_base} args {hint_base_args}!')

                    # Note that the current child type hint directly
                    # subscripting this generic has now been bubbled up.
                    hint_args_index_curr += 1

                    # If all child type hints directly subscripting this generic
                    # have now been bubbled up, halt this nested iteration.
                    if hint_args_index_curr > hint_args_index_last:
                        break
                    # Else, one or more child type hints directly subscripting
                    # this generic have yet to be bubbled up. In this case,
                    # continue to the next such hint.
                # Else, this hint is *NOT* a PEP 484-compliant type variable. In
                # this case, preserve this hint as is and continue to the next.
        # Else, either this pseudo-superclass is unsubscripted *OR* all child
        # type hints directly subscripting this generic have already been
        # bubbled up. In either case, no further bubbling is warranted.

        # If isolating child type hints to a target pseudo-superclass...
        if hint_base_target:
            # Unsubscripted generic underlying this possibly subscripted
            # pseudo-superclass generic. Strip this pseudo-superclass of *ALL*
            # child hints to compare this unsubscripted current
            # pseudo-superclass with this unsubscripted target
            # pseudo-superclass.
            hint_base_type = get_hint_pep484585_generic_type(
                hint=hint_base,
                exception_cls=exception_cls,
                exception_prefix=exception_prefix,
            )

            # If this current pseudo-superclass is this target
            # pseudo-superclass...
            if hint_base_type is hint_base_target:
                # If this sequence of child hints transitively subscripting both
                # this generic and this target pseudo-superclass has already
                # been established, this generic has redundantly subclassed this
                # target pseudo-superclass at least twice. However, one or more
                # of the child hints subscripting this generic may have already
                # been "consumed" by prior logic "bubbling up" these hints to
                # this target pseudo-superclass. In this case, silently ignoring
                # this edge case would erroneously override this previously
                # established sequence of "bubbled up" child hints with a new
                # distinct sequence of non-bubbled up child hints. Raising an
                # exception here avoids that badness *AND* informs the caller of
                # an almost certain bug in their codebase.
                if hint_base_target_args_full:
                    raise exception_cls(
                        f'{exception_prefix}PEP 484 or 585 generic '
                        f'{repr(hint)} redundantly subclasses '
                        f'pseudo-superclass target {repr(hint_base_target)}.'
                    )
                # Else, this sequence has *NOT* already been established.
                #
                # If this target pseudo-superclass is transitively
                # unsubscripted, raise an exception. By definition, *ALL*
                # generics *MUST* be transitively subscripted by at least one
                # child hint across their class hierarchies.
                elif not hint_base_args:
                    raise exception_cls(
                        f'{exception_prefix}PEP 484 or 585 generic '
                        f'{repr(hint)} pseudo-superclass target '
                        f'{repr(hint_base_target)} transitively unsubscripted '
                        f'(i.e., subscripted by no child type hints either '
                        f'directly or indirectly across its class hierarchy).'
                    )
                # Else, this target pseudo-superclass is transitively
                # subscripted by one or more child hints.
                print(f'Found generic {hint} target psuedo-superclass {hint_base} args {hint_base_args}!')

                #FIXME: Almost there, but *NOT* quite. Desynchronization between
                #this and the branch above complicates matters. Perhaps we want
                #to instead return these two integers instead of
                #"hint_base_target_args_full":
                #    hint_base_target_args_index_first = len(hint_args_full)
                #    hint_base_target_args_len = len(hint_base_args)
                #
                #Then return below:
                #    return (
                #        hint_args_full,
                #        hint_base_target_args_index_first,
                #        hint_base_target_args_len,
                #    )
                #
                #Then initialize above:
                #    hint_base_target_args_index_first = None
                #    hint_base_target_args_len = None
                #
                #Next modify the above recursive call to resemble:
                #    (
                #        hint_base_args,
                #        hint_base_target_args_index_first,
                #        hint_base_target_args_len,
                #    ) = _get_hint_pep484585_generic_args_full(...)
                #
                #Next add a new "if" conditional branch inside this existing
                #"if hint_base_target:" block, which should resemble:
                #    # If isolating child type hints to a target pseudo-superclass...
                #    if hint_base_target:
                #        if hint_base_target_args_index_first is not None:
                #            assert hint_base_target_args_len is not None
                #
                #            #FIXME: Ideally, we'd short-circuit here by
                #            #immediately returning. This is all the caller
                #            #wants. That would be trivial if this were
                #            #implemented as a non-recursive algorithm. Alas,
                #            #this is a recursive algorithm. *sigh*
                #            #FIXME: Actually, can't we just do this here?
                #            #    break
                #            #Pretty sure that *ALMOST* works. We need to
                #            #perform the "break" statement *AFTER* calling
                #            #"hint_args_full.extend(hint_base_args)". Of
                #            #course, we have to be *VERY* careful about how we
                #            #do that. Notably, a premature "break" statement
                #            #probably breaks various edge cases by preventing
                #            #all "hint_args" from being "bubbled up". In other
                #            #words, we have to stop "bubbling up" *AFTER* the
                #            #first "break" statement. We could probably force
                #            #that with yet another item in the return tuple
                #            #called "is_breaking" or something. But... yeah.
                #            #That's getting pretty gnarly pretty fast.
                #            #
                #            #At that point, it'd be substantially better to
                #            #just refactor all of this recursion away. *sigh*
                #            hint_base_target_args_index_first += len(hint_args_full)
                #
                #Lastly, refactor get_hint_pep484585_generic_args_full() to
                #slice out these child hints from the passed "hint_args_full"
                #tuple using this index and length. Pretty sure that works --
                #and quite efficiently, too.

                # Record this sequence, coerced from this list.
                hint_base_target_args_full = tuple(hint_base_args)
            # Else, this current pseudo-superclass is *NOT* this target
            # pseudo-superclass.
        # Else, child type hints are *NOT* isolated to such a pseudo-superclass.

        # Append this possibly modified sequence of all child type hints
        # transitively subscripting this pseudo-superclass to this list of all
        # child type hints transitively subscripting this generic.
        hint_args_full.extend(hint_base_args)  # type: ignore[attr-defined]
        print(f'Inspected generic {hint} pseudo-superclass {hint_base} args {hint_base_args}!')

    # ....................{ RETURN                         }....................
    # Tuple of all full child type hints transitively subscripting this generic,
    # coerced from this list.
    hint_args_full = tuple(hint_args_full)

    # Return a 2-tuple of these tuples of full child type hints.
    return (hint_args_full, hint_base_target_args_full)

# ....................{ GETTERS ~ bases                    }....................
def get_hint_pep484585_generic_bases_unerased(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> tuple:
    '''
    Tuple of the one or more **unerased pseudo-superclasses** (i.e.,
    PEP-compliant objects originally listed as superclasses prior to their
    implicit type erasure under :pep:`560`) of the passed :pep:`484`- or
    :pep:`585`-compliant **generic** (i.e., class superficially subclassing at
    least one PEP-compliant type hint that is possibly *not* an actual class) if
    this object is a generic *or* raise an exception otherwise (i.e., if this
    object is *not* a generic).

    This getter is guaranteed to return a non-empty tuple. By definition, a
    generic is a type subclassing one or more generic superclasses.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__orig_bases__`` **dunder instance variable.**
    Most PEP-compliant type hints fail to declare that variable, guaranteeing
    :class:`AttributeError` exceptions from all general-purpose logic
    attempting to directly access that variable. Thus this function, which
    "fills in the gaps" by implementing this oversight.

    **This function returns tuples possibly containing a mixture of actual
    superclasses and pseudo-superclasses superficially masquerading as actual
    superclasses subscripted by one or more PEP-compliant child hints or type
    variables** (e.g., ``(typing.Iterable[T], typing.Sized[T])``). Indeed, most
    type hints used as superclasses produced by subscripting PEP-compliant type
    hint factories are *not* actually types but singleton objects devilishly
    masquerading as types. Most actual :mod:`typing` superclasses are private,
    fragile, and prone to alteration or even removal between Python versions.

    Motivation
    ----------
    :pep:`560` (i.e., "Core support for typing module and generic types)
    formalizes the ``__orig_bases__`` dunder attribute first informally
    introduced by the :mod:`typing` module's implementation of :pep:`484`.
    Naturally, :pep:`560` remains as unusable as :pep:`484` itself. Ideally,
    :pep:`560` would have generalized the core intention of preserving each
    original user-specified subclass tuple of superclasses as a full-blown
    ``__orig_mro__`` dunder attribute listing the original method resolution
    order (MRO) of that subclass had that tuple *not* been modified.

    Naturally, :pep:`560` did no such thing. The original MRO remains obfuscated
    and effectively inaccessible. While computing that MRO would technically be
    feasible, doing so would also be highly non-trivial, expensive, and fragile.
    Instead, this function retrieves *only* the tuple of :mod:`typing`-specific
    pseudo-superclasses that this object's class originally attempted (but
    failed) to subclass.

    You are probably now agitatedly cogitating to yourself in the darkness: "But
    @leycec: what do you mean :pep:`560`? Wasn't :pep:`560` released *after*
    :pep:`484`? Surely no public API defined by the Python stdlib would be so
    malicious as to silently alter the tuple of base classes listed by a
    user-defined subclass?"

    As we've established both above and elsewhere throughout the codebase,
    everything developed for :pep:`484` -- including :pep:`560`, which derives
    its entire raison d'etre from :pep:`484` -- are fundamentally insane. In
    this case, :pep:`484` is insane by subjecting parametrized :mod:`typing`
    types employed as base classes to "type erasure," because:

         ...it is common practice in languages with generics (e.g. Java,
         TypeScript).

    Since Java and TypeScript are both terrible languages, blindly
    recapitulating bad mistakes baked into such languages is an equally bad
    mistake. In this case, "type erasure" means that the :mod:`typing` module
    *intentionally* destroys runtime type information for nebulous and largely
    unjustifiable reasons (i.e., Big Daddy Java and TypeScript do it, so it
    must be unquestionably good).

    Specifically, the :mod:`typing` module intentionally munges :mod:`typing`
    types listed as base classes in user-defined subclasses as follows:

    * All base classes whose origin is a builtin container (e.g.,
      ``typing.List[T]``) are reduced to that container (e.g., :class:`list`).
    * All base classes derived from an abstract base class declared by the
      :mod:`collections.abc` subpackage (e.g., ``typing.Iterable[T]``) are
      reduced to that abstract base class (e.g., ``collections.abc.Iterable``).
    * All surviving base classes that are parametrized (e.g.,
      ``typing.Generic[S, T]``) are stripped of that parametrization (e.g.,
      :class:`typing.Generic`).

    Since there exists no counterpart to the :class:`typing.Generic` superclass,
    the :mod:`typing` module preserves that superclass in unparametrized form.
    Naturally, this is useless, as an unparametrized :class:`typing.Generic`
    superclass conveys no meaningful type information. All other superclasses
    are reduced to their non-:mod:`typing` counterparts: e.g.,

        .. code-block:: python

        >>> from typing import TypeVar, Generic, Iterable, List
        >>> T = TypeVar('T')
        >>> class UserDefinedGeneric(List[T], Iterable[T], Generic[T]): pass
        # This is type erasure.
        >>> UserDefinedGeneric.__mro__
        (list, collections.abc.Iterable, Generic)
        # This is type preservation -- except the original MRO is discarded.
        # So, it's not preservation; it's reduction! We take what we can get.
        >>> UserDefinedGeneric.__orig_bases__
        (typing.List[T], typing.Iterable[T], typing.Generic[T])
        # Guess which we prefer?

    So, we prefer the generally useful ``__orig_bases__`` dunder tuple over the
    generally useless ``__mro__`` dunder tuple. Note, however, that the latter
    *is* still occasionally useful and thus occasionally returned by this
    getter. For inexplicable reasons, **single-inherited protocols** (i.e.,
    classes directly subclassing *only* the :pep:`544`-compliant
    :attr:`typing.Protocol` abstract base class (ABC)) are *not* subject to type
    erasure and thus constitute a notable exception to this heuristic:

        .. code-block:: python

        >>> from typing import Protocol
        >>> class UserDefinedProtocol(Protocol): pass
        >>> UserDefinedProtocol.__mro__
        (__main__.UserDefinedProtocol, typing.Protocol, typing.Generic, object)
        >>> UserDefinedProtocol.__orig_bases__
        AttributeError: type object 'UserDefinedProtocol' has no attribute
        '__orig_bases__'

    Welcome to :mod:`typing` hell, where even :mod:`typing` types lie broken and
    misshapen on the killing floor of overzealous theory-crafting purists.

    Parameters
    ----------
    hint : object
        Generic type hint to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    tuple
        Tuple of the one or more unerased pseudo-superclasses of this generic.

    Raises
    ------
    exception_cls
        If this hint is either:

        * Neither a :pep:`484`- nor :pep:`585`-compliant generic.
        * A :pep:`484`- or :pep:`585`-compliant generic subclassing *no*
          pseudo-superclasses.

    Examples
    --------
    .. code-block:: python

       >>> from beartype.typing import Container, Iterable, TypeVar
       >>> from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
       ...     get_hint_pep484585_generic_bases_unerased)

       >>> T = TypeVar('T')
       >>> class MuhIterable(Iterable[T], Container[T]): pass

       >>> get_hint_pep585_generic_bases_unerased(MuhIterable)
       (typing.Iterable[~T], typing.Container[~T])

       >>> MuhIterable.__mro__
       (MuhIterable,
        collections.abc.Iterable,
        collections.abc.Container,
        typing.Generic,
        object)
    '''

    # Tuple of either...
    #
    # Note this implicitly raises a "BeartypeDecorHintPepException" if this
    # object is *NOT* a PEP-compliant generic. Ergo, we need not explicitly
    # validate that above.
    hint_pep_generic_bases_unerased = (
        # If this is a PEP 585-compliant generic, all unerased
        # pseudo-superclasses of this PEP 585-compliant generic.
        #
        # Note that this unmemoized getter accepts keyword arguments.
        get_hint_pep585_generic_bases_unerased(
            hint=hint,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
        if is_hint_pep585_generic(hint) else
        # Else, this *MUST* be a PEP 484-compliant generic. In this case, all
        # unerased pseudo-superclasses of this PEP 484-compliant generic.
        #
        # Note that this memoized getter prohibits keyword arguments.
        get_hint_pep484_generic_bases_unerased(
            hint,
            exception_cls,
            exception_prefix,
        )
    )

    # If this generic....
    if (
        # Subclasses no pseudo-superclasses *AND*...
        not hint_pep_generic_bases_unerased and
        # Is user-defined by a third-party downstream codebase.
        is_hint_pep484585_generic_user(hint)
    ):
        # Raise an exception. By definition, *ALL* user-defined generics should
        # subclass at least one pseudo-superclass. Note that this constraint:
        # * Does *NOT* apply to standard generics defined by either:
        #   * The standard "typing" module (e.g., "typing.Generic[S, T]").
        #   * The Python interpreter itself (e.g., "list[T]").
        #   Why? Because these generics are the root superclasses that other
        #   user-defined generics subclass. Clearly, they have no
        #   pseudo-superclasses.
        # * Should have already been guaranteed on our behalf by:
        #   * If this generic is PEP 484-compliant, the standard "typing" module.
        #   * If this generic is PEP 585-compliant, the Python interpreter itself.
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        raise exception_cls(
            f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
            f'subclasses no superclasses.'
        )
    # Else, this generic subclasses one or more pseudo-superclasses.

    # Return this tuple of these pseudo-superclasses.
    return hint_pep_generic_bases_unerased


def get_hint_pep484585_generic_base_in_module_first(
    # Mandatory parameters.
    hint: object,
    module_name: str,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> type:
    '''
    Iteratively find and return the first **unerased superclass** (i.e.,
    unerased pseudo-superclass that is an actual superclass) transitively
    defined under the third-party package or module with the passed name
    subclassed by the unsubscripted generic type underlying the passed
    :pep:`484`- or :pep:`585`-compliant **generic** (i.e., object that may *not*
    actually be a class despite subclassing at least one PEP-compliant type hint
    that also may *not* actually be a class).

    This finder is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Although doing so *would* dramatically
    improve the efficiency of this getter, doing so:

    * Would require all passed parameters be passed positionally, which becomes
      rather cumbersome given the number of requisite parameters.
    * Is (currently) unnecessary, as all callers of this function are themselves
      already memoized.

    Motivation
    ----------
    This finder is typically called to reduce **descriptive generics** (i.e.,
    generics defined in third-party packages intended to be used *only* as
    descriptive type hints rather than actually instantiated as objects as most
    generics are) to the isinstanceable classes those generics describe.
    Although the mere existence of descriptive generics should be considered to
    be a semantic (if not syntactic) violation of :pep:`484`, the widespread
    proliferation of descriptive generics leaves :mod:`beartype` with little
    choice but to grin wanly and bear the pain they subject us to. As example,
    this finder is currently called elsewhere to:

    * Reduce Pandera type hints (e.g., `pandera.typing.DataFrame[...]`) to the
      Pandas types they describe (e.g., `pandas.DataFrame`).
    * Reduce NumPy type hints (e.g., `numpy.typing.NDArray[...]`) to the
      NumPy types they describe (e.g., `numpy.ndarray`).

    See examples below for further discussion.

    Parameters
    ----------
    hint : object
        Generic type hint to be inspected.
    module_name : str
        Fully-qualified name of the third-party package or module to find the
        first class in this generic type hint of.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`.BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    type
        First unerased superclass transitively defined under this package or
        module subclassed by the unsubscripted generic type underlying this
        generic type hint.

    Examples
    --------
    .. code-block:: python

       >>> from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
       ...     find_hint_pep484585_generic_base_first_in_module)

       # Reduce a Pandera type hint to the Pandas type it describes.
       >>> from pandera import DataFrameModel
       >>> from pandera.typing import DataFrame
       >>> class MuhModel(DataFrameModel): pass
       >>> find_hint_pep484585_generic_base_first_in_module(
       ...     hint=DataFrame[MuhModel], module_name='pandas', ...)
       <class 'pandas.DataFrame'>
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodget import get_object_module_name_or_none

    # Either:
    # * If this generic is unsubscripted, this unsubscripted generic type as is.
    # * If this generic is subscripted, the unsubscripted generic type
    #   underlying this subscripted generic (e.g., the type
    #   "pandera.typing.pandas.DataFrame" given the type hint
    #   "pandera.typing.DataFrame[...]").
    hint_type = get_hint_pep484585_generic_type(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # Fully-qualified name of the module to be searched for suffixed by a "."
    # delimiter. This is a micro-optimization improving lookup speed below.
    module_name_prefix = f'{module_name}.'

    # Tuple of the one or more unerased pseudo-superclasses which this
    # unsubscripted generic type originally subclassed prior to type erasure.
    #
    # Note that we could also inspect the method-resolution order (MRO) of this
    # type via the "hint.__mro__" dunder tuple, but that doing so would only
    # needlessly reduce the efficiency of the following iteration by
    # substantially increasing the number of iterations required to find the
    # desired superclass and thus the worst-case complexity of that iteration.
    hint_type_bases = get_hint_pep484585_generic_bases_unerased(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # For each unerased pseudo-superclass of this unsubscripted generic type...
    for hint_base in hint_type_bases:
        # If this pseudo-superclass is *NOT* an actual superclass, silently
        # ignore this non-superclass and continue to the next pseudo-superclass.
        if not isinstance(hint_base, type):
            continue
        # Else, this pseudo-superclass is an actual superclass.

        # Fully-qualified name of the module declaring this superclass if any
        # *OR* "None" otherwise (i.e., if this type is only defined in-memory).
        hint_base_module_name = get_object_module_name_or_none(hint_base)

        # If this module exists *AND* either...
        if hint_base_module_name and (
            # This module is the desired module itself *OR*...
            hint_base_module_name == module_name_prefix or
            # This module is a submodule of the desired module...
            hint_base_module_name.startswith(module_name_prefix)
        # Then return this superclass.
        ):
            # print(f'Found generic {repr(hint)} type {repr(hint_type)} "{module_name}" superclass {repr(hint_base)}!')
            return hint_base
        # Else, this is *NOT* the desired module. In this case, continue to the
        # next superclass.
    # Else, *NO* superclass of this generic resides in the desired module.

    # Raise an exception of the passed type.
    raise exception_cls(
        f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
        f'type {repr(hint_type)} subclasses no "{module_name}" type '
        f'(i.e., type with module name prefixed by "{module_name}" not '
        f'found in method resolution order (MRO) {repr(hint_type.__mro__)}).'
    )

# ....................{ GETTERS ~ type                     }....................
#FIXME: Unit test us up, please.
def get_hint_pep484585_generic_type(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> type:
    '''
    Either the passed :pep:`484`- or :pep:`585`-compliant **generic** (i.e.,
    class superficially subclassing at least one PEP-compliant type hint that is
    possibly *not* an actual class) if **unsubscripted** (i.e., indexed by *no*
    arguments or type variables), the unsubscripted generic underlying this
    generic if **subscripted** (i.e., indexed by one or more child type hints
    and/or type variables), *or* raise an exception otherwise (i.e., if this
    hint is *not* a generic).

    Specifically, this getter returns (in order):

    * If this hint originates from an **origin type** (i.e., isinstanceable
      class such that *all* objects satisfying this hint are instances of that
      class), this type regardless of whether this hint is already a class.
    * Else if this hint is already a class, this hint as is.
    * Else, raise an exception.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This getter returns false positives in edge cases.** That is, this getter
    returns non-:data:`None` values for both generics and non-generics --
    notably, non-generics defining the ``__origin__`` dunder attribute to an
    isinstanceable class. Callers *must* perform subsequent tests to distinguish
    these two cases.

    Parameters
    ----------
    hint : object
        Generic type hint to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    type
        Class originating this generic.

    Raises
    ------
    exception_cls
        If this hint is *not* a generic.

    See Also
    --------
    :func:`get_hint_pep484585_generic_type_or_none`
        Further details.
    '''

    # This hint if this hint is an unsubscripted generic, the unsubscripted
    # generic underlying this hint if this hint is a subscripted generic, *OR*
    # "None" if this hint is not a generic.
    hint_generic_type = get_hint_pep484585_generic_type_or_none(hint)

    # If this hint is *NOT* a generic, raise an exception.
    if hint_generic_type is None:
        raise exception_cls(
            f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
            f'not generic (i.e., originates from no isinstanceable class).'
        )
    # Else, this hint is a generic.

    # Return this class.
    return hint_generic_type


def get_hint_pep484585_generic_type_or_none(hint: object) -> Optional[type]:
    '''
    Either the passed :pep:`484`- or :pep:`585`-compliant **generic** (i.e.,
    class superficially subclassing at least one PEP-compliant type hint that is
    possibly *not* an actual class) if **unsubscripted** (i.e., indexed by *no*
    arguments or type variables), the unsubscripted generic underlying this
    generic if **subscripted** (i.e., indexed by one or more child type hints
    and/or type variables), *or* :data:`None` otherwise (i.e., if this hint is
    *not* a generic).

    Specifically, this getter returns (in order):

    * If this hint originates from an **origin type** (i.e., isinstanceable
      class such that *all* objects satisfying this hint are instances of that
      class), this type regardless of whether this hint is already a class.
    * Else if this hint is already a class, this hint as is.
    * Else, :data:`None`.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This getter returns false positives in edge cases.** That is, this getter
    returns non-:data:`None`` values for both generics and non-generics --
    notably, non-generics defining the ``__origin__`` dunder attribute to an
    isinstanceable class. Callers *must* perform subsequent tests to distinguish
    these two cases.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    Optional[type]
        Either:

        * If this hint is a generic, the class originating this generic.
        * Else, :data:`None`.

    See Also
    --------
    :func:`get_hint_pep_origin_or_none`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_origin_or_none

    # Arbitrary object originating this hint if any *OR* "None" otherwise.
    hint_origin = get_hint_pep_origin_or_none(hint)
    # print(f'{repr(hint)} hint_origin: {repr(hint_origin)}')

    # If this origin is a type, this is the origin type originating this hint.
    # In this case, return this type.
    if isinstance(hint_origin, type):
        return hint_origin
    # Else, this origin is *NOT* a type.
    #
    # Else if this hint is already a type, this type is effectively already its
    # origin type. In this case, return this type as is.
    elif isinstance(hint, type):
        return hint
    # Else, this hint is *NOT* a type. In this case, this hint originates from
    # *NO* origin type.

    # Return the "None" singleton.
    return None

# ....................{ ITERATORS                          }....................
#FIXME: Unit test us up, please.
def iter_hint_pep484585_generic_bases_unerased_tree(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> IterableHints:
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

       >>> from beartype._util.hint.pep.proposal.utilpep585 import is_hint_pep585_builtin_subscripted
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
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    Iterable[Hint]
        Breadth-first search (BFS) generator iteratively yielding the one or
        more unignorable unerased transitive pseudo-superclasses originally
        declared as superclasses prior to their type erasure of this generic.

    Raises
    ------
    exception_cls
        If this hint is *not* a generic.

    See Also
    --------
    :func:`get_hint_pep484585_generic_type_or_none`
        Further details.
    '''

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._check.convert.convsanify import (
        sanify_hint_child_if_unignorable_or_none)
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none

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
        # Unignorable sane pseudo-superclass sanified from this possibly
        # ignorable insane pseudo-superclass *OR* "None" otherwise (i.e.,
        # if this pseudo-superclass is ignorable).
        hint_base = sanify_hint_child_if_unignorable_or_none(
            hint=hint_bases[hint_bases_index_curr],
            conf=conf,
            #FIXME: Possibly also pass this, please. Ignorable for now. *shrug*
            # cls_stack=cls_stack,
            exception_prefix=exception_prefix,
        )
        # print(f'generic {hint} base: {repr(hint_base)}')

        # If this pseudo-superclass is unignorable...
        if hint_base is not None:
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
                yield hint_base
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
