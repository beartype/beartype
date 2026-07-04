#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **generic type hint
finders** (i.e., low-level callables generically traversing over the transitive
pseudo-superclasses subscripting both :pep:`484`- and :pep:`585`-compliant
generic subclasses).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype._data.typing.datatypingport import (
    Hint,
    HintOrNone,
    ListHints,
    Pep484612646TypeArgUnpackedToHint,
    TupleHints,
)
from beartype._data.typing.datatyping import TypeException
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep646.pep484612646typevar import (
    is_hint_pep484612646_typearg_unpacked)
#FIXME: Excise us up, please. *sigh*
# from beartype._util.kind.sequence.utilseqmake import make_stack
from itertools import count
from typing import (
    Optional,
    Union,
)

# ....................{ FINDERS                            }....................
#FIXME: Document all of the edge cases in which this getter raises exceptions.
#FIXME: Unit test this getter with respect to generics subscripted by PEP
#646-compliant unpacked type variable tuples: e.g.,
#    class MuhGeneric[*Ts](Generic[*Ts]): ...
#
#We currently only test this getter with respect to generics subscripted by PEP
#484-compliant type variables. *sigh*
#FIXME: *HMM.* The "exception_cls" and "exception_prefix" parameters are at odds
#with memoization. Do we actually pass these parameters? If so, can we stop?
#Memoization is quite important here. This is an *EXTREMELY* slow algorithm.
#Note that, if we *DO* actually pass these parameters, we can still memoize this
#finder (albeit at a performance hit) by deferring to a lower-level memoized
#private function. *shrug*
#FIXME: For disambiguity, also globally rename:
#* get_hint_pep484585_generic_type() to
#  get_hint_pep484585_generic_type_unsubbed().
#* get_hint_pep484585_generic_type_isinstanceable() to
#  get_hint_pep484585_generic_type_unsubbed_isinstanceable().
#* get_hint_pep484585_generic_type_or_none() to
#  get_hint_pep484585_generic_type_unsubbed_or_none().
#FIXME: Once worky:
#* Globally replace all calls to get_hint_pep484585_generic_args_full() by
#  calls to this finder.
#* Excise up the get_hint_pep484585_generic_args_full() getter entirely.
@callable_cached
def find_hint_pep484585_generic_args_full(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    hint_base_target: HintOrNone = None,
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> TupleHints:
    '''
    Tuple of the one or more **full child type hints** (i.e., complete tuple of
    *all* type hints directly subscripting both the passed generic *and*
    one or more pseudo-superclasses of this generic) transitively subscripting
    the passed :pep:`484`- or :pep:`585`-compliant **generic** (i.e., class
    superficially subclassing at least one PEP-compliant type hint that is
    possibly *not* an actual class) if this object is a generic *or* raise an
    exception otherwise (i.e., if this object is not a generic).

    This getter greedily replaces in the returned tuple as many abstract
    :pep:`484`-compliant **type parameters** (e.g., :pep:`484`-compliant
    :class:`typing.TypeVar` object, :pep:`612`-compliant
    class:`typing.ParamSpec` object, :pep:`646`-compliant
    :class:`typing.TypeVarTuple` object) as there are **concrete child type
    hints** (i.e., *any* hint other than a type parameter) directly subscripting
    the passed generic. Doing so effectively "bubbles up" these concrete
    children up the class hierarchy into the "empty placeholders" established by
    the type variables transitively subscripting all pseudo-superclasses of this
    generic.

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
    hint : Hint
        Generic type hint to be inspected.
    hint_base_target : Optional[Hint] = None
        **Target pseudo-superclass** (i.e., erased transitive pseudo-superclass
        of the passed generic to specifically search, filter, and return the
        child type hints of). Defaults to :data:`None`. Specifically:

        * If this parameter is :data:`None`, this getter returns the complete
          tuple of *all* type hints directly subscripting both the passed
          generic *and* one or more pseudo-superclasses of this generic.
        * If this parameter is *not* :data:`None`, this getter returns the
          partial tuple of *only* type hints directly subscripting both the
          passed generic *and* this passed pseudo-superclass of this generic.

        A target pseudo-superclass is passed to deduce whether two generics are
        related according to the :func:`beartype.door.is_subhint` relation. If
        all child type hints in the tuple returned by this getter (when passed
        some generic and its pseudo-superclass) are subhints of all child type
        hints in the tuple returned by this getter passed *only* that
        pseudo-superclass, then that generic is necessarily a subhint of that
        pseudo-superclass. Look. Just go with it, people.

        Lastly, note that this getter intentionally ignores *all* child hints
        subscripting this target pseudo-superclass. For search purposes, *any*
        child hints subscripting this target pseudo-superclass are not only
        irrelevant but harmful -- promoting false negatives in higher-level
        functions (e.g., :func:`beartype.door.is_subhint`) internally leveraging
        this lower-level getter. Ignoring these child hints is thus imperative.
        Since deciding child hint compatibility between the passed generic and
        this target pseudo-superclass is a non-trivial decision problem, this
        lower-level getter defers that problem to the caller by unconditionally
        returning the same result regardless of child hints subscripting this
        target pseudo-superclass.

        For example, consider the :pep:`484`-compliant :obj:`typing.Any`.
        Clearly, this getter should return the same tuple when passed an
        unsubscripted target pseudo-superclass as when passed a target
        pseudo-superclass subscripted by :obj:`typing.Any`: e.g.,

        .. code-block:: pycon

           >>> from typing import Any, Generic
           >>> class MuhGeneric[S, T](Generic[S, T]): pass
           >>> get_hint_pep484585_generic_args_full(
           ...     MuhGeneric, hint_base_target=Generic)
           (S, T)
           >>> get_hint_pep484585_generic_args_full(
           ...     MuhGeneric, hint_base_target=Generic[Any])
           (S, T)
           >>> get_hint_pep484585_generic_args_full(
           ...     MuhGeneric, hint_base_target=Generic[S, T])
           (S, T)
           >>> get_hint_pep484585_generic_args_full(
           ...     MuhGeneric, hint_base_target=Generic[int, float])
           (S, T)

    exception_cls : TypeException, default: BeartypeDecorHintPep484585Exception
        Type of exception to be raised. Defaults to
        :exc:`.BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Tuple[Hint, ...]
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
    .. code-block:: pycon

       >>> from beartype.typing import Generic, TypeVar
       >>> from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
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

    # ....................{ DESCRIPTION                    }....................
    # This function implements an extremely non-trivial depth-first search (DFS)
    # over all the abstract n-ary tree of all PEP 484- and 585-compliant generic
    # transitive pseudo-superclasses of the passed generic subclass. Indeed,
    # this function is currently the least trivial single function across this
    # entire pure-Python codebase.
    #
    # Semantically, this DFS performs a recursive traversal over this tree.
    # Syntactically, this DFS performs non-recursive iteration only simulating
    # such recursive traversal. While less intuitive (and debuggable,
    # maintainable, and readable), non-recursive iteration is substantially more
    # performant in general and enables even greater performance gains via
    # short-circuiting in this specific case. Due to the extreme
    # non-trivialities involved, we now define terms for sanity and goodwill:
    #
    # * DFS: A naturally recursive form of search typically optimized into a
    #   non-recursive iterative implementation leveraging a Last-In-First-Out
    #   (LIFO) stack. Pure-Python lists define all requisite methods needed to
    #   natively express a LIFO stack and are thus the natural builtin
    #   containers for implementing a DFS non-recursively in Python. Doing so
    #   requires semantically (and usually syntactically) reversing the items
    #   of this list such that the "top" of the LIFO stack expressed by this
    #   list is the last item of this stack. These methods thus include:
    #   * append(), pushing an item into the top of this stack.
    #   * extend(), pushing zero or more items into the top of this stack.
    #   * pop(), popping an item from the top of this non-empty stack.
    # * n-ary tree: A graph-like recursive data structure comprised of nodes and
    #   directed edges between nodes rooted at a single node such that nodes
    #   referred to as:
    #   * Leaves terminate this recursive data structure by originating *NO*
    #     directed edges to other nodes.
    #   * Non-leaves perpetuate this recursive data structure by originating "n"
    #     directed edges to other nodes deeper in the tree, where "n" is a
    #     variable non-zero integer specific to each node.
    # * Pseudo-superclass: Any user-defined PEP 484- and 585-compliant generic
    #   subclasses at least one pseudo-superclass. Since the superclasses that a
    #   generics subclasses are resolved dynamically at inheritance-time via a
    #   non-trivial process referred to as "type erasure," the superficial
    #   subclasses that a generic syntactically appears to subclass may differ
    #   from the actual subclasses that a generic semantically subclasses. For
    #   example, consider this Python snippet defining a type hierarchy of two
    #   non-generics and four generics:
    #       from typing import Generic
    #       class Y(object): ...
    #       class Z(object): ...
    #       class A[S](Z, Generic[S]): ...
    #       class B[T](Y, Generic[T]): ...
    #       class C[S, T](A[S], B[T]): ...
    #       class D[S, T, U](list[T], C[S, T]): ...
    #
    #   These four generics subclass these pseudo-superclasses:
    #   * Generic "A" subclasses both:
    #     * Superclass "Z", which is a normal class (rather than a generic) and
    #       thus an actual superclass of "A" rather than merely a
    #       pseudo-superclass of "A".
    #     * Pseudo-superclass "Generic[S]", which is a subscripted generic and
    #       thus *NOT* an actual superclass of "A". Rather, a private metaclass
    #       of "A" defined by the standard "typing" module silently erases this
    #       pseudo-superclass at inheritance time and permanently replaces this
    #       pseudo-superclass by the normal class "typing.Generic". Ergo,
    #       "Generic[S]" is merely a pseudo-superclass. Syntactically,
    #       "Generic[S]" appears to be a real superclass. Semantically,
    #       "Generic[S]" only masquerades as a real superclass.
    #   * Generic "B" subclasses both superclass "Y" and pseudo-superclass
    #     "Generic[T]", for the exact same reasons.
    #   * Generic "C" subclasses both pseudo-superclasses "A[S]" and "B[T]".
    #   * Generic "D" subclasses both pseudo-superclasses "list[T]" and
    #     "C[S, T]".
    #
    #   This algorithm is principally interested in pseudo-superclasses rather
    #   than the actual superclasses those generics were erased to.
    # * Transitive pseudo-superclass: Any pseudo-superclass anywhere in the
    #   method-resolution order (MRO) of a user-defined PEP 484- and
    #   585-compliant generic. Reusing the above example, the four generics
    #   defined above subclass these transitive pseudo-superclasses:
    #   * Generic "A" transitively subclasses "Z", "Generic[S]", and "object".
    #   * Generic "B" transitively subclasses "Y", "Generic[T]", and "object".
    #   * Generic "C" transitively subclasses "A[S]", "Z", "Generic[S]", "B[T]",
    #     "Y", "Generic[T]", and "object".
    #   * Generic "D" transitively subclasses "list[T]", "C[S, T]", "A[S]", "Z",
    #     "Generic[S]", "B[T]", "Y", "Generic[T]", and "object".
    # * Transitive pseudo-superclass n-ary tree: The n-ary tree rooted at any
    #   user-defined PEP 484- and 585-compliant generic expressing the
    #   relationship of that generic to its transitive pseudo-superclasses. This
    #   tree corresponds to the standard understanding of the relationship
    #   between a subclass and its superclasses, with each subclass treated as a
    #   "child" layered underneath each superclass treated as a "parent".
    #   Reusing the above example, the n-ary tree rooted at generic "D"
    #   expresses the relationship of that generic to its 9 transitive
    #   pseudo-superclasses. In plaintext ASCII, this tree could be depicted as:
    #                               object object object object
    #                                  |     |       |     |
    #                                  Z Generic[S]  Y Generic[T]
    #                                  \ /           \ /
    #                           object A[S]    -----B[T]
    #                              |      \   /
    #                           list[T] C[S, T]
    #                                 \ /
    #                                  D
    # * DFS traversal tree: The same exact tree as the transitive
    #   pseudo-superclass n-ary tree rooted at any user-defined PEP 484- and
    #   585-compliant generic, except depicted such that that generic is the
    #   top-most root node of that tree and each transitive pseudo-superclass of
    #   that generic is a transitive child node of that root node. Although
    #   confusing, this depiction is the "natural" way to express the traversal
    #   order of a DFS over a type hierarchy. Although we typically conceive of
    #   subclasses as "children" of "parent" superclasses, a DFS that traverses
    #   over a type hierarchy asks that we instead momentarily conceive of
    #   subclasses as "parents" of "children" superclasses with respect to
    #   traversal order. Reusing the above example, the DFS traversal rooted at
    #   generic "D" expresses the order in which a DFS traverses over that
    #   generic and its 9 transitive pseudo-superclasses. In plaintext ASCII,
    #   this traversal could be depicted as:
    #                                  D
    #                                 / \
    #                           list[T] C[S, T]
    #                              |      /   \
    #                           object A[S]    -----B[T]
    #                                  / \           / \
    #                                  Z Generic[S]  Y Generic[T]
    #                                  |     |       |     |
    #                               object object object object
    # * Child pseudo-superclass: A pseudo-superclass subclassed by the generic
    #   currently being visited by this DFS. This nomenclature is intrinsic to
    #   the action of a DFS but somewhat counterintuitive from the perspective
    #   of subclass inheritance, where we typically conceive of a subclass as
    #   instead the "child" of a "parent" superclass. Reusing the above example,
    #   "list[T]" and "C[S, T]" are child pseudo-superclasses of generic "D".
    # * Parent pseudo-superclass: A generic or pseudo-superclass subclassing the
    #   generic or pseudo-superclass currently being visited by this DFS. Again,
    #   this nomenclature is intrinsic to the action of a DFS but somewhat
    #   counterintuitive. Reusing the above example, generic "D" is the parent
    #   pseudo-superclass of child pseudo-superclasses "list[T]" and "C[S, T]".
    # * Unpacked type parameter: An abstract type hint to be replaced by a
    #   concrete type hint through the bubbling performed by this DFS.
    #   Specifically, either:
    #   * A PEP 484-compliant type variable (i.e., "typing.TypeVar" object).
    #   * A PEP 612-compliant parameter specification (i.e., "typing.ParamSpec"
    #     object unpacked by the unary "*" prefix operator). For example, the
    #     parameter specification "*P" where "P = typing.ParamSpec('P')".
    #   * A PEP 646-compliant tuple type variable (i.e., "typing.TypeVarTuple"
    #     object unpacked by the unary "*" prefix operator). For example, the
    #     tuple type variable "*Ts" where "Ts = typing.TypeVarTuple('Ts')".
    # * Concrete type hint: Any type hint subscripting a generic such that that
    #   type hint is *NOT* an unpacked type parameter.
    # * Bubbling: The process by which this DFS recursively replaces each
    #   unpacked type parameter parametrizing the target pseudo-superclass of
    #   the passed generic with the corresponding concrete type hint
    #   subscripting the passed generics and transitive pseudo-superclasses of
    #   that generic. Under this nomenclature, concrete type hints are seen as:
    #   * "Bubbling down" the DFS traversal tree from the passed generic rooting
    #     this tree into unpacked type parameters parametrizing the transitive
    #     pseudo-superclasses of that generic.
    #   * "Bubbling up" the transitive pseudo-superclass n-ary tree from the
    #     passed generic rooting this tree in the same manner. Since the natural
    #     depiction of a DFS is a DFS traversal tree, discussion below favours
    #     the term "bubbling down" to "bubbling up." The result is the same!
    #
    # And that's how @leycec got so exhausted in life. Not with an explosive
    # bang on GitHub Actions-hosted continuous integration (CI) workflows, but a
    # whimper as he quietly weeps into his tear-stained keyboard at night.

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_bases_unerased,
        get_hint_pep484585_generic_type,
    )
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic_user)
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        get_hint_pep_typeargs_unpacked,
    )

    # ....................{ LOCALS ~ data                  }....................
    # Metadata describing the passed generic, used to seed the depth-first
    # search (DFS) below with the first pseudo-superclass to be visited.
    hint_root_data: ListHints = [  # pyright: ignore
        # This generic.
        hint,

        # Metadata describing the direct parent pseudo-superclass of this
        # generic. By definition, this generic is the root of this n-ary tree
        # and thus has *NO* parent (either direct or indirect).
        None,  # pyright: ignore
    ]

    # Unvisited pseudo-superclass stack (i.e., efficiently poppable list of
    # metadata describing *ALL* unvisited transitive pseudo-superclasses of this
    # generic, intentionally reordered in reverse order to enable the
    # non-recursive depth-first search (DFS) performed below to both visit and
    # pop these pseudo-superclasses in the expected order), seeded with metadata
    # describing the passed generic.
    #
    # Each item of this stack is a list of metadata describing an unvisited
    # transitive pseudo-superclass of this generic such that this list is
    # either:
    # * If this pseudo-superclass has yet to be visited by this DFS, a 2-list
    #   "(hint, hint_super_data)" where:
    #   * "hint" is this pseudo-superclass.
    #   * "hint_super_data" is either:
    #     * If this pseudo-superclass has a parent pseudo-superclass, the item
    #       of this stack describing that parent pseudo-superclass.
    #     * Else, this pseudo-superclass is the passed generic. Since this
    #       generic has *NO* parent pseudo-superclass, "None".
    # * If this pseudo-superclass is itself a user-defined generic (i.e.,
    #   defined by a third-party downstream package) that has already been
    #   visited by this DFS, a 4-list "(hint, hint_super_data, hint_args_stack,
    #   hint_args_full)" where:
    #   * "hint" is this pseudo-superclass.
    #   * "hint_super_data" is as defined above.
    #   * "hint_args_stack" is this pseudo-superclass' direct child hint stack
    #     (i.e., list of the zero or more child hints directly subscripting this
    #     pseudo-superclass in reverse order, embodying an efficiently poppable
    #     stack of these hints), popped off while recursing up from the child
    #     pseudo-superclasses of this pseudo-superclass.
    #   * "hint_args_full" is the list of zero or more child hints transitively
    #     subscripting this pseudo-superclass, defined while recursing up from
    #     the child pseudo-superclasses of this pseudo-superclass.
    #
    # In short, there be dragons here -- albeit extremely efficient dragons.
    hint_bases_data: _HintBasesData = [hint_root_data]  # type: ignore[list-item]

    # ....................{ LOCALS ~ target                }....................
    # List of zero or more child hints transitively subscripting the passed
    # target pseudo-superclass of this generic if this pseudo-superclass has
    # already been visited by the DFS below *OR* "None" otherwise (i.e., if this
    # pseudo-superclass has yet to be visited by this DFS).
    hint_base_target_args_full: Optional[ListHints] = None

    # True only if the pseudo-superclass currently visited by the DFS below is
    # still transitively subscripted by one or more PEP 484-compliant type
    # variables (i.e., "TypeVar" objects) that have yet to be replaced by
    # concrete hints of a parent pseudo-superclass of that pseudo-superclass.
    is_hint_base_arg_typearg = False

    # If the caller explicitly passed a pseudo-superclass target...
    #
    # Note that this is the common case for this getter and thus tested first.
    if hint_base_target:
        hint_base_target = (
            # If this pseudo-superclass target is this generic, this
            # pseudo-superclass target is effectively meaningless (albeit
            # technically valid). In this case, silently ignore this
            # pseudo-superclass target.
            None
            if hint is hint_base_target else
            # Else, this pseudo-superclass target is *NOT* this generic. In this
            # case, the unsubscripted generic underlying this possibly
            # subscripted target pseudo-superclass generic. See the docstring.
            get_hint_pep484585_generic_type(  # pyright: ignore
                hint=hint_base_target,
                exception_cls=exception_cls,
                exception_prefix=exception_prefix,
            )
        )
    # Else, the caller passed *NO* pseudosuperclass target. In this case...

    # ....................{ LOCALS ~ typearg->nontypearg   }....................
    #FIXME: Excise us up, please. Before doing so, though, copy this comment
    #onto the "hint_base_parent_typearg_to_hint" local below. *sigh*
    # Dictionary mapping from each previously observed PEP-compliant type
    # parameter (e.g., PEP 484-compliant "typing.TypeVar" object, PEP
    # 612-compliant "typing.ParamSpec" object, PEP 646-compliant
    # "typing.TypeVarTuple" object) subscripting a transitive pseudo-superclass
    # of this generic to the corresponding concrete child hint (i.e., *ANY* type
    # hint other than a type parameter) "bubbled down" from a subclass of that
    # pseudo-superclass into that type parameter.
    #
    # This dictionary enables the DFS below to reliably "bubble down" a single
    # concrete child hint to the same type parameter appearing multiple times
    # throughout a generics hierarchy. For example, this dictionary enables the
    # "int" child hint subscripting the "GenericList" generic to be "bubbled
    # down" into the type parameter "T" subscripting the pseudo-superclasses
    # "List" and "Generic" of this generic: e.g.,
    #     >>> class GenericList[T](List[T], Generic[T]): pass
    #     >>> get_hint_pep484585_generic_args_full(GenericList[int])
    #     (int, int)
    #
    # For the above call, this contents of this dictionary resemble:
    #     typearg_to_nontypearg = {T: int}
    # typearg_to_nontypearg: Pep484612646TypeArgUnpackedToHint = {}

    # ....................{ SEARCH                         }....................
    # Iteration simulating a recursive depth-first search (DFS), efficiently
    # deciding the tuple of all child hints transitively subscripting the
    # desired pseudo-superclass of this generic.

    # With at least one transitive pseudo-superclass of this generic remains
    # unvisited...
    while hint_bases_data:
        # Metadata describing the currently visited transitive pseudo-superclass
        # of this generic defined as the top-most item of this stack.
        #
        # Note that we intentionally avoid popping this pseudo-superclass off
        # this stack yet. We only pop a pseudo-superclass off this stack *AFTER*
        # resolving all child pseudo-superclasses of that pseudo-superclass,
        # which simulates the "backing out" performed by genuine recursion.
        hint_base_data = hint_bases_data[-1]

        # Currently visited transitive pseudo-superclass of this generic.
        hint_base = hint_base_data[_HINT_BASES_INDEX_HINT]

        # True only if the metadata describing this pseudo-superclass is still
        # its initial size, implying that this DFS has yet to visit this
        # pseudo-superclass by recursing down into the child pseudo-superclasses
        # of this parent pseudo-superclass.
        is_hint_base_leaf = len(hint_base_data) == _HINT_BASE_DATA_LEN_LEAF

        # ....................{ RECURSE ~ down             }....................
        # If...
        if (
            # This DFS has yet to visit this pseudo-superclass *AND*...
            is_hint_base_leaf and
            # This pseudo-superclass is itself a PEP 484- or 585-compliant
            # user-defined generic. Standard generics (i.e., that are *NOT*
            # user-defined) have *NO* pseudo-superclasses and are thus omitted.
            # Examples of omittable standard generics include:
            # * "dict[str, U]".
            # * "typing.Generic[S, int]").
            # * "typing.Protocol[float, T]").
            #
            # Note that this tester is mildly slower than the prior test and
            # thus intentionally tested later.
            is_hint_pep484585_generic_user(hint_base)  # type: ignore[arg-type]
        # Then this DFS is currently recursing down into the child
        # pseudo-superclasses of this pseudo-superclass. In this case...
        ):
            # This pseudo-superclass in unsubscripted form (i.e., unsubscripted
            # generic underlying this pseudo-superclass if this
            # pseudo-superclass is subscripted *OR* this pseudo-superclass as
            # is otherwise).
            hint_base_unsubbed = get_hint_pep484585_generic_type(
                hint=hint_base,  # pyright: ignore
                exception_cls=exception_cls,
                exception_prefix=exception_prefix,
            )

            # Tuple of the one or more type parameters transitively
            # parametrizing this pseudo-superclass in unsubscripted form.
            #
            # Note that this tuple can differ from the tuple of the one or more
            # type parameters parametrizing this pseudo-superclass if this
            # pseudo-superclass is subscripted: e.g.,
            #    >>> T = TypeVar('T')
            #    >>> class Ugh(Generic[T]): pass
            #    >>> print(get_hint_pep_typeargs_packed(Ugh))
            #    (~T,)  # <-- good
            #    >>> print(get_hint_pep_typeargs_packed(Ugh[int]))
            #    ()  # <----- less good for this use case, but understandable
            hint_base_typeargs = get_hint_pep_typeargs_unpacked(
                hint_base_unsubbed)

            # Tuple of the zero or more child hints directly subscripting this
            # pseudo-superclass if this pseudo-superclass is subscripted *OR*
            # the empty tuple if this pseudo-superclass is unsubscripted.
            hint_base_args = get_hint_pep_args(hint_base)

            #FIXME: Comment us up, please. *sigh*
            hint_base_typearg_index = 0
            hint_base_typeargs_len = len(hint_base_typeargs)
            hint_base_args_len = len(hint_base_args)

            #FIXME: We probably want to detect the following error condition and
            #raise some sort of fatal exception here. No idea if the
            #"typing.Generic" superclass even permits these sorts of
            #shenanigans, but maybe it does:
            #    if hint_base_args_len > hint_base_typeargs_len:
            #        raise MuhException('OH GOLLY JEE!')

            #FIXME: Revise comment up, please. *sigh*
            # Dictionary mapping from each previously observed PEP-compliant
            # type parameter (e.g., PEP 484-compliant "typing.TypeVar" object,
            # PEP 612-compliant "typing.ParamSpec" object, PEP 646-compliant
            # "typing.TypeVarTuple" object) subscripting a transitive
            # pseudo-superclass of this generic to the corresponding concrete
            # child hint (i.e., *ANY* type hint other than a type parameter)
            # "bubbled down" from a subclass of that pseudo-superclass into that
            # type parameter, defaulting to the empty dictionary and then
            # initialized by the subsequent iteration.
            #
            # This dictionary enables this DFS to reliably "bubble down" a
            # single concrete child hint to the same type parameter appearing
            # multiple times throughout a generics hierarchy. For example, this
            # dictionary enables the "int" child hint subscripting the
            # "GenericList" generic to be "bubbled down" into the type parameter
            # "T" subscripting the pseudo-superclasses "List" and "Generic" of
            # this generic: e.g.,
            #     >>> class GenericList[T](List[T], Generic[T]): pass
            #     >>> get_hint_pep484585_generic_args_full(GenericList[int])
            #     (int, int)
            #
            # For the above call, this contents of this dictionary resemble:
            #     hint_base_typearg_to_hint == {T: int}
            hint_base_typearg_to_hint: Pep484612646TypeArgUnpackedToHint = {}

            #FIXME: Finish commentary, please. *sigh*
            # Map each type parameter parametrizing this pseudo-superclass in
            # unsubscripted form to the corresponding child hint subscripting
            # this pseudo-superclass in possibly subscripted form.
            #
            # Specifically...
            while hint_base_typearg_index < hint_base_typeargs_len:
                #FIXME: Comment us up, please. *sigh*
                hint_base_typearg = hint_base_typeargs[hint_base_typearg_index]

                #FIXME: Comment us up, please. *sigh*
                if hint_base_typearg_index < hint_base_args_len:
                    hint_base_arg = hint_base_args[hint_base_typearg_index]
                #FIXME: Comment us up, please. Basically, if there are
                #insufficient child hints directly subscripting this
                #pseudo-superclass, then we simply inject the identity mapping
                #from each surplus (excess) type parameter parametrizing this
                #pseudo-superclass in unsubscripted form to that same type
                #parameter. Doing so preserves such surplus (excess) type
                #parameters as is.
                #
                #Note that this common case arises both:
                #* When this pseudo-superclass is already unsubscripted.
                #* When this pseudo-superclass is directly subscripted by fewer
                #  child hints than the number of type parameters parametrizing
                #  this pseudo-superclass in unsubscripted form.
                else:
                    hint_base_arg = hint_base_typearg

                # print(f'Preseeding {hint_base_typearg} -> {hint_base_arg}...')

                #FIXME: Comment us up, please. *sigh*
                #FIXME: Should we do anything about pseudo-superclasses with
                #duplicate mappings? Probably. It's probably fine if duplicate
                #mappings exist *SO LONG AS ALL DUPLICATES ARE IDENTICAL*. That
                #is, it's fine if a type parameter appears two or more times in
                #a parametrization (e.g., "Generic[T, T]") so long as that same
                #type parameter maps to the same subscripted child hint each
                #time. Honestly, this is kinda weirdo stuff. Does the
                #"typing.Generic" superclass even permit duplicate type
                #parametrizations? No idea. Never really thought about it! Ugh!
                hint_base_typearg_to_hint[hint_base_typearg] = hint_base_arg  # pyright: ignore

                #FIXME: Comment us up, please. *sigh*
                hint_base_typearg_index += 1

            #FIXME: Excise us up, please. *sigh*
            # for hint_base_typearg, hint_base_arg in zip(
            #     hint_base_typeargs, hint_base_args):
            #         typearg_to_nontypearg[hint_base_typearg] = hint_base_arg
            #         print(f'Preseeding {hint_base_typearg} -> {hint_base_arg}...')
            #
            #         #FIXME: Do we still need this? No idea, bro. *sigh*
            #         # hint_typeargs_preseeded.add(hint_typearg)

            # Expand the metadata describing this pseudo-superclass from its
            # current 2-list "(hint, hint_super_data)" into the expanded 4-list
            # "(hint, hint_super_data, hint_args_stack, hint_args_full)".
            # Specifically, append (in order):
            hint_base_data.extend((
                #FIXME: Excise us up, please. *sigh*
                # # Poppable stack of the zero or more child hints directly
                # # subscripting this child pseudo-superclass.
                # make_stack(get_hint_pep_args(hint_base)),

                #FIXME: Comment us up, please. *sigh*
                hint_base_typearg_to_hint,

                # List of the zero or more child hints transitively subscripting
                # this child pseudo-superclass, initialized to the empty list.
                [],
            ))

            # Tuple of the one or more child pseudo-superclasses of this
            # pseudo-superclass.
            # print(f'Introspecting generic {hint} unerased bases...')
            hint_child_bases = get_hint_pep484585_generic_bases_unerased(
                hint=hint_base,  # type: ignore[arg-type]
                exception_cls=exception_cls,
                exception_prefix=exception_prefix,
            )
            # print(f'Generic {hint} unerased bases: {hint_child_bases}')

            # For each child pseudo-superclass of this pseudo-superclass,
            # intentionally iterated in reverse order so as to ensure that the
            # *FIRST* child pseudo-superclass is the *LAST* item of this stack
            # (and thus the *FIRST* unvisited pseudo-superclass to be visited by
            # this depth-first search (DFS) next).
            #
            # Note that the reversed() builtin is well-known to be the most
            # efficient means of producing a reversed iterable for iteration
            # purposes. See also:
            #     https://stackoverflow.com/a/16514411/2809027
            for hint_child_base in reversed(hint_child_bases):
                # Push metadata describing this unvisited child
                # pseudo-superclass onto this stack.
                hint_bases_data.append([
                    # This child pseudo-superclass.
                    hint_child_base,

                    # Metadata describing the direct parent
                    # pseudo-superclass of this child pseudo-superclass.
                    hint_base_data,
                ])

            # Visit the next transitive pseudo-superclass of this generic by
            # recursing either down or up this DFS as needed.
            continue

        # ....................{ RECURSE ~ up               }....................
        # Else, either:
        # * This DFS has already visited this pseudo-superclass *OR*...
        # * This pseudo-superclass is a "terminal" leaf generic *OR*...
        # * This pseudo-superclass is *NOT* a generic.
        #
        # In any case, this DFS should *NOT* recurse (back) down into this
        # pseudo-superclass. Therefore, this DFS is currently recursing back up
        # out of this pseudo-superclass into its parent pseudo-superclass.

        # Pop this pseudo-superclass off this stack.
        hint_bases_data.pop()
        # print(f'Resuming generic {hint} pseudo-superclass {hint_base} args {hint_base_args}...')

        # List of the zero or more child hints transitively subscripting this
        # pseudo-superclass, defined as either...
        hint_base_args_full: ListHints = (  # pyright: ignore
            # If this is a terminal leaf pseudo-superclass, the tuple of zero or
            # more child hints directly subscripting this pseudo-superclass.
            # Why? Because this pseudo-superclass has *NO* child
            # pseudo-superclass to recurse down into. If this pseudo-superclass
            # had one or more child pseudo-superclasses to recurse down into,
            # then those child pseudo-superclasses would have defined the
            # "hint_base_data[_HINT_BASES_INDEX_ARGS_FULL]" list accessed by the
            # "else" branch of this "if" conditional below, providing the list
            # of zero or more child hints transitively subscripting this
            # pseudo-superclass. Although that list remains undefined, the tuple
            # of zero or more child hints directly subscripting this
            # pseudo-superclass is semantically equivalent to what that list
            # would have been (had that list actually been defined).
            list(get_hint_pep_args(hint_base))  # type: ignore[assignment]
            if is_hint_base_leaf else
            # Else, this is *NOT* a terminal leaf pseudo-superclass. In this
            # case, the list of zero or more child hints transitively
            # subscripting this pseudo-superclass previously defined by child
            # pseudo-superclasses of this pseudo-superclass in lower-level
            # recursion performed by this DFS.
            hint_base_data[_HINT_BASES_INDEX_ARGS_FULL]
        )

        # Reset this boolean to its default value (i.e., "False") *BEFORE*
        # possibly setting this boolean to "True" below, facilitating
        # efficient communication between the "if hint_base_args_full:" and
        # "if hint_base_target:" branches below.
        #
        # Equivalently, record that this pseudo-superclass is transitively
        # subscripted by *NO* type parameters. Since the "if
        # hint_base_args_full:" branch below works as hard as possible to
        # ensure that this is the case, this default is sensible until
        # proven otherwise below.
        is_hint_base_arg_typearg = False

        # If this pseudo-superclass is transitively subscripted by at least
        # one child hint...
        if hint_base_args_full:
            # Metadata describing the direct parent pseudo-superclass of this
            # pseudo-superclass.
            hint_base_parent_data: _HintBasesData = hint_base_data[  # type: ignore[assignment]
                _HINT_BASES_INDEX_PARENT]
            # print(f'Resuming generic {hint} pseudo {hint_base} parent {hint_base_parent_data[0]}...')

            # If this pseudo-superclass has a parent pseudo-superclass (i.e.,
            # this pseudo-superclass is *NOT* the passed root generic and is
            # thus a transitive child of that generic)...
            if hint_base_parent_data:
                #FIXME: Excise us up, please. *sigh*
                # # Poppable stack of the zero or more child hints directly
                # # subscripting this parent pseudo-superclass.
                # hint_base_parent_args_stack = hint_base_parent_data[  # pyright: ignore
                #     _HINT_BASES_INDEX_ARGS_STACK]

                #FIXME: Comment us up, please. *sigh*
                hint_base_parent_typearg_to_hint: (
                    Pep484612646TypeArgUnpackedToHint) = hint_base_parent_data[  # type: ignore[assignment]
                        _HINT_BASES_INDEX_TYPEARG_TO_HINT]

                #FIXME: Revise commentary, please. Unsure whether any of the
                #"Note that..." commentary actually applies anymore. *shrug*
                # For the 0-based index of each child hint transitively
                # subscripting this pseudo-superclass and this hint...
                #
                # Note that this iteration could be fenced behind an "if"
                # conditional resembling:
                #     if not (
                #         hint_base_parent_args_stack or
                #         typearg_to_nontypearg
                #     ):
                #
                # However, doing so would be almost entirely pointless. Why?
                # Because almost *ALL* generics are transitively subscripted
                # by one or more type parameters. Ergo, "typearg_to_nontypearg" is
                # almost *ALWAYS* non-empty. Ergo, the above "if"
                # conditional reduces to "if True:" in most cases. We sigh.
                for hint_base_arg_full_index, hint_base_arg_full in (
                    enumerate(hint_base_args_full)):
                    # If this child hint is *NOT* a type parameter, this child
                    # hint is already concrete. In this case, preserve this
                    # child hint as is and continue to the next.
                    if not is_hint_pep484612646_typearg_unpacked(
                        hint_base_arg_full):
                        continue
                    # Else, this child hint is a type parameter.

                    #FIXME: Revise comment up, please. *sigh*
                    #FIXME: This condition should now be true in 99% of cases.
                    #Unsure what to do if it isn't. Ergo, we currently blindly
                    #assume this to be the case. WHATEVAHS! *sigh*
                    # If a concrete (i.e., non-type parameter) child hint
                    # directly subscripting a sibling pseudo-superclass of this
                    # pseudo-superclass has already been "bubbled down" into
                    # this type parameter, preserve that bubbling by re-bubbling
                    # down the same child hint back into this type parameter. <-- lol

                    #FIXME: Let's just assert this for now and see what blows
                    #up. Surely, this is a plan. Ugh!
                    assert hint_base_arg_full in hint_base_parent_typearg_to_hint
                    if hint_base_arg_full in hint_base_parent_typearg_to_hint:
                        # print(f'Rebubbling hint {hint_base_parent_typearg_to_hint[hint_base_arg_full]} into...')
                        # print(f'base {hint_base} typevar {hint_base_arg_full}!')

                        #FIXME: Comment us up, please. *sigh*
                        hint_base_arg_full_new = (
                        hint_base_args_full[hint_base_arg_full_index]) = (
                            hint_base_parent_typearg_to_hint[
                                hint_base_arg_full])  # type: ignore[index]

                        # print(f'Bubbling base {hint_base} typevar {hint_base_arg_full} ->...')
                        # print(f'... {hint_base_arg_full_new}!')

                        #FIXME: Unclear if this is relevant anymore. *shrug*
                        # If this next unassigned child hint directly
                        # subscripting this parent pseudo-superclass is
                        # itself a type parameter, record that this
                        # child pseudo-superclass is now known to be
                        # subscripted by at least one type parameter.
                        if is_hint_pep484612646_typearg_unpacked(
                            hint_base_arg_full_new):  # pyright: ignore
                            # print(f'Recording base {hint_base} bubbled typevar {hint_base_arg_full_new}...')
                            is_hint_base_arg_typearg = True

                        #FIXME: Excise us up, please. *sigh*
                        # if hint_base_arg_full in typearg_to_nontypearg:

                        #FIXME: Revise comment up, please. *sigh*
                        # If a concrete (i.e., non-type parameter) child hint
                        # directly subscripting a sibling pseudo-superclass of
                        # this pseudo-superclass has already been "bubbled down"
                        # into this type parameter, preserve that bubbling by
                        # re-bubbling down the same child hint back into this
                        # type parameter. <-- lol

                        # if hint_base_arg_full in (
                        #     hint_base_parent_typearg_to_hint):
                        #     # print(f'Rebubbling hint {typearg_to_nontypearg[hint_base_arg]} into...')
                        #     # print(f'base {hint_base} typevar {hint_base_arg}!')
                        #
                        #     #FIXME: Excise us up, please. *sigh*
                        #     # hint_base_args_full[hint_base_arg_full_index] = (
                        #     #     typearg_to_nontypearg[hint_base_arg_full])  # type: ignore[index]
                        #
                        #     #FIXME: Comment us up, please. *sigh*
                        #     hint_base_args_full[hint_base_arg_full_index] = (
                        #         hint_base_parent_typearg_to_hint[
                        #             hint_base_arg_full])  # type: ignore[index]
                        #
                        # #FIXME: Revise comments up, please. *sigh*
                        # # Else, *NO* child hint directly subscripting a
                        # # sibling pseudo-superclass of this child
                        # # pseudo-superclass has already been "bubbled down"
                        # # into this type parameter.
                        # #
                        # # If this parent pseudo-superclass of this child
                        # # pseudo-superclass is still directly subscripted by
                        # # one or more child hints that have yet to "bubble
                        # # up" the class hierarchy (i.e., by replacing the
                        # # first unused type parameter transitively
                        # # subscripting this child pseudo-superclass),
                        # # "bubble down" the next unassigned child hint
                        # # directly subscripting this parent
                        # # pseudo-superclass into the "empty placeholder"
                        # # signified by this type parameter in this list of
                        # # child hints transitively subscripting this child
                        # # pseudo-superclass. <-- wat
                        #
                        # #FIXME: Excise us up, please. *sigh*
                        # # elif hint_base_parent_args_stack:
                        #     #FIXME: Excise us up, please. *sigh*
                        #     #FIXME: Preserve some of this commentary into
                        #     #comments below, please. *sigh*
                        #     # print(f'Bubbling base {hint_base} typevar {hint_base_arg_full} ->...')
                        #     # print(f'... {hint_base_parent_args_stack[-1]}!')
                        #     #
                        #     # # Pop the next unassigned child hint directly
                        #     # # subscripting this parent pseudo-superclass off
                        #     # # this stack and then bubble this child hint
                        #     # # down into the "empty placeholder" signified by
                        #     # # this type parameter in the list of child hints
                        #     # # transitively subscripting this child
                        #     # # pseudo-superclass.  # <-- WATWAT
                        #     # hint_base_arg_full_new = (  # pyright: ignore
                        #     # hint_base_args_full[hint_base_arg_full_index]) = (
                        #     #     hint_base_parent_args_stack.pop())  # type: ignore[assignment]
                        #
                        #     #FIXME: Comment us up, please. *sigh*
                        #     hint_base_arg_full_new = (  # pyright: ignore
                        #     hint_base_args_full[hint_base_arg_full_index]) = (
                        #         hint_base_parent_args_stack.pop())  # type: ignore[assignment]
                        #
                        #     #FIXME: Unclear if this is actually valuable here. *shrug*
                        #     # hint_base_parent_typearg_to_hint[hint_base_arg_full] = (  # type: ignore[index]
                        #     #     hint_base_arg_full_new)  # type: ignore[assignment]
                        #
                        #     # If this next unassigned child hint directly
                        #     # subscripting this parent pseudo-superclass is
                        #     # itself a type parameter, record that this
                        #     # child pseudo-superclass is now known to be
                        #     # subscripted by at least one type parameter.
                        #     if is_hint_pep484612646_typearg_unpacked(
                        #         hint_base_arg_full_new):  # pyright: ignore
                        #         # print(f'Recording pseudo {hint_base} typevarred args {hint_base_arg_full}...')
                        #         is_hint_base_arg_typearg = True
                        #
                        #     #FIXME: Preserve comment elsewhere. *sigh!*
                        #     #FIXME: Excise us up, please. *sigh*
                        #     # Else, the currently unassigned child hint
                        #     # directly subscripting this parent
                        #     # pseudo-superclass is *NOT* itself a type
                        #     # parameter. In this case, record that this
                        #     # child hint has now been "bubbled down" into
                        #     # this type parameter for subsequent lookup.
                        #     #
                        #     # Note that "bubbling down" a type parameter
                        #     # into another type parameter would be entirely
                        #     # pointless. Type parameters are only
                        #     # meaningfully replaceable with concrete hints.
                        #     # Moreover, doing so here would erroneously map
                        #     # this type parameter to this other type
                        #     # parameter in the "typearg_to_nontypearg" dictionary
                        #     # -- which would then inhibit this "if"
                        #     # conditional from subsequently bubbling down a
                        #     # concrete hint into this type parameter. <- omg
                        #     # else:
                        #     #     # print(f'Recording non-typevar {hint_base_arg_full} -> {hint_base_arg_full_new}...')
                        #     #     typearg_to_nontypearg[hint_base_arg_full] = (  # type: ignore[index]
                        #     #         hint_base_arg_full_new)  # type: ignore[assignment]
                        # # Else, all child hints directly subscripting this
                        # # parent pseudo-superclass have already been
                        # # "bubbled up" the class hierarchy. But this hint is
                        # # a type parameter! Record that this child
                        # # pseudo-superclass is now known to be subscripted
                        # # by at least one type parameter.
                        # else:
                        #     is_hint_base_arg_typearg = True
                        # #print(f'Bubbled up generic {hint} arg {hint_args[hint_args_index_curr]}...')
                        # #print(f'...into pseudo-superclass {hint_base} args {hint_base_args}!')
                    # Else, this hint is *NOT* a type parameter. In this
                    # case, preserve this hint and continue to the next.

                # Parent list of the zero or more child hints transitively
                # subscripting this parent pseudo-superclass of this child
                # pseudo-superclass.
                hint_base_parent_args_full = hint_base_parent_data[  # pyright: ignore
                    _HINT_BASES_INDEX_ARGS_FULL]

                # Extend this parent list with all child hints transitively
                # subscripting this child pseudo-superclass.
                hint_base_parent_args_full.extend(hint_base_args_full)  # pyright: ignore
                # print(f'Inspected generic {hint} pseudo-superclass {hint_base} args {hint_base_args}!')
            # Else, this pseudo-superclass is the passed root generic.
        # Else, this pseudo-superclass is transitively unsubscripted.

        # If searching for a target pseudo-superclass...
        if hint_base_target:
            # Unsubscripted generic underlying this possibly subscripted
            # pseudo-superclass generic. Strip this pseudo-superclass of
            # *ALL* child hints, allowing this unsubscripted current
            # pseudo-superclass to be compared against this
            # unsubscripted target pseudo-superclass.
            hint_base_type = get_hint_pep484585_generic_type(
                hint=hint_base,  # type: ignore[arg-type]
                exception_cls=exception_cls,
                exception_prefix=exception_prefix,
            )

            # If this pseudo-superclass is the desired target...
            if hint_base_type is hint_base_target:
                # If this target pseudo-superclass is no longer subscripted
                # by any type parameters requiring subsequent replacement by
                # concrete child hints, this target pseudo-superclass is
                # *ONLY* subscripted by concrete child hints. In this case,
                # immediately return a tuple of these hints.
                #
                # Note that:
                # * This efficiently short-circuits this recursion in the
                #   best case and is one of several reasons to prefer a
                #   non-recursive algorithm. This algorithm was initially
                #   implemented recursively (supposedly for simplicity);
                #   doing so introduced significant unforeseen complications
                #   by effectively preventing short-circuiting. After all, a
                #   recursive algorithm *CANNOT* efficiently short-circuit
                #   up out of a deeply nested recursive call stack --
                #   without inefficiently raising an exception, which is so
                #   inefficient as to defeat the point in most cases.
                # * This recursion *CANNOT* be short-circuited in the worst
                #   case, which occurs when the passed root generic is
                #   directly subscripted by a concrete child hint that will
                #   only be subsequently "bubbled down" into a type hint
                #   transitively subscripting this target pseudo-superclass
                #   *AFTER* this DFS recurses through the tree of all
                #   pseudo-superclasses and back up into this generic. In
                #   this worst case, the full dictionary of type parameter
                #   mappings and thus the list of child hints transitively
                #   subscripting this target pseudo-superclass is only
                #   decidable *AFTER* this DFS fully recurses out.
                #
                # Consider this torturous hierarchy, in which bubbling down
                # the child hint "complex" subscripting the root generic
                # "ListFloat[complex]" into the child type parameter "U"
                # subscripting the child pseudo-superclass "Generic[U]"
                # requires recursing through the full tree:
                #     >>> from typing import Generic
                #     >>> class ListTU(list[T], Generic[U]): pass
                #     >>> class ListFloat(ListTU[float]): pass
                #     >>> get_hint_pep484585_generic_args_full(
                #     ...     hint=ListFloat[complex],
                #     ...     hint_base_target=Generic[U],
                #     ... )
                #     (complex,)
                if not is_hint_base_arg_typearg:
                    return tuple(hint_base_args_full)
                # Else, this target pseudo-superclass is still subscripted
                # by one or more type parameters requiring subsequent
                # replacement by concrete child hints. In this case,
                # continue "bubbling down" child hints into these type
                # variables. Doing so enables final logic below to replace
                # these type parameters with these hints *AFTER* recursing
                # through the full entirety of this DFS.

                # List of zero or more child hints transitively subscripting
                # this target pseudo-superclass.
                hint_base_target_args_full = hint_base_args_full
                # print(f'Found target {hint_base} args {hint_base_args_full}!')
            # Else, this pseudo-superclass is *NOT* equal to this target.
        # Else, *NO* target pseudo-superclass is being searched for.

    # ....................{ RETURN                         }....................
    # List of the one or more full child type hints transitively subscripting
    # the passed generic, to be coerced into a tuple and returned.
    hint_args_full: ListHints = None  # type: ignore[assignment]

    # If the caller passed a target pseudo-superclass...
    if hint_base_target:
        # If the DFS above failed to find the list of zero or more child hints
        # transitively subscripting this target, this DFS failed to find this
        # target. Since this implies this target is *NOT* a pseudo-superclass of
        # this generic, raise an exception.
        if hint_base_target_args_full is None:
            raise exception_cls(
                f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
                f'pseudo-superclass target {repr(hint_base_target)} not found.'
            )
        # Else, this DFS found the list of zero or more child hints transitively
        # subscripting this target.

        # List of the zero or more child hints transitively subscripting this
        # target pseudo-superclass, to be coerced into a tuple and returned.
        hint_args_full = hint_base_target_args_full

        #FIXME: No idea, bro. Is this still relevant? Maybe. Maybe not. This
        #refactoring has gotten brutally out-of-hand, clearly. *sigh sigh sigh*
        #
        # # For the 0-based index of each child hint transitively subscripting
        # # this target pseudo-superclass and this hint...
        # for hint_arg_full_index, hint_arg_full in enumerate(hint_args_full):
        #     # If this hint is a type parameter...
        #     if is_hint_pep484612646_typearg_unpacked(hint_arg_full):
        #         # Either:
        #         # * If a child hint directly subscripting a sibling
        #         #   pseudo-superclass of this target pseudo-superclass has
        #         #   already been "bubbled down" into this type parameter,
        #         #   preserve that bubbling by re-bubbling up the same child hint
        #         #   back into this # type parameter. <-- lol
        #         # * If *NO* child hint directly subscripting a sibling
        #         #   pseudo-superclass of this target pseudo-superclass has
        #         #   already been "bubbled down" into this type parameter,
        #         #   preserve this type parameter as is.
        #         hint_args_full[hint_arg_full_index] = typearg_to_nontypearg.get(  # type: ignore[call-overload]
        #             hint_arg_full, hint_arg_full)  # type: ignore[arg-type]
        #     # Else, this hint is *NOT* a type parameter.
    # Else, the caller did *NOT* pass a target pseudo-superclass.
    else:
        # If the metadata describing the passed generic is still its initial
        # size, then the above DFS failed to expand this metadata with the
        # "_HINT_BASES_INDEX_ARGS_FULL" index accessed below. In turn, this
        # implies that the above DFS failed to recurse down into the child
        # pseudo-superclasses of this generic. However, by definition, *ALL*
        # generics subclass one or more pseudo-superclasses. The above DFS
        # should have recursed down into those pseudo-superclasses. In this
        # case, raise an exception.
        #
        # Note that this should *NEVER* occur.
        if len(hint_root_data) == _HINT_BASE_DATA_LEN_LEAF:  # pragma: no cover
            raise exception_cls(
                f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
                f'pseudo-superclasses not found.'
            )
        # Else, the above DFS expanded the metadata describing the passed
        # generic with the "_HINT_BASES_INDEX_ARGS_FULL" index accessed below.

        # List of the zero or more child hints transitively subscripting this
        # generic discovered by the above DFS.
        hint_args_full = hint_root_data[_HINT_BASES_INDEX_ARGS_FULL]  # type: ignore[assignment]

    # Return a tuple coerced from this list.
    return tuple(hint_args_full)

# ....................{ PRIVATE ~ hints                    }....................
#FIXME: Excise us up, please. *sigh*
# _HintBaseData = list[Union[Hint, ListHints, '_HintBaseData']]

#FIXME: Ideally, this would be annotated as ": Hint". Mypy likes that but
#pyright hates that. This is why we can't have good things.
#FIXME: Unconvinced this is right. This "Union[...]" fails to currently cover
#the full spectrum of all possible types of items of this list. *shrug*
_HintBaseData = list[Union[
    #FIXME: Document what all of these actually correspond to. Ugh! Ugh!
    Hint,
    Pep484612646TypeArgUnpackedToHint,
    '_HintBaseData',
]]
'''
PEP-compliant type hint matching each **unvisited pseudo-superclass** (i.e.,
item of the ``hint_bases`` fixed list local to the
:func:`.get_hint_pep484585_generic_args_full` getter, describing each
pseudo-superclass of the generic passed to that getter that has yet to be
internally visited by the depth-first search (DFS) performed by that getter).
'''


_HintBasesData = list[_HintBaseData]
'''
PEP-compliant type hint matching the ``hint_bases`` fixed list local to the
:func:`.get_hint_pep484585_generic_args_full` getter.
'''

# ....................{ PRIVATE ~ constants                }....................
# Iterator yielding the next integer incrementation starting at 0, to be safely
# deleted *AFTER* defining the following 0-based indices via this iterator.
__hint_bases_counter = count(start=0, step=1)


_HINT_BASES_INDEX_HINT = next(__hint_bases_counter)
'''
0-based index into each **pseudo-superclass metadata** (i.e., list describing a
transitive pseudo-superclass of the :pep:`484`- or :pep:`585`-compliant generic
passed to the :func:`.get_hint_pep484585_generic_args_full` getter) stored in
the ``hint_bases`` list local to that getter, providing the currently visited
pseudo-superclass itself.
'''


_HINT_BASES_INDEX_PARENT = next(__hint_bases_counter)
'''
0-based index into each **pseudo-superclass metadata** (i.e., list describing a
transitive pseudo-superclass of the :pep:`484`- or :pep:`585`-compliant generic
passed to the :func:`.get_hint_pep484585_generic_args_full` getter) stored in
the ``hint_bases`` list local to that getter, providing the currently visited
pseudo-superclass' **parent pseudo-superclass metadata** (i.e., list describing
the direct parent pseudo-superclass of this current pseudo-superclass).
'''


_HINT_BASE_DATA_LEN_LEAF = _HINT_BASES_INDEX_PARENT + 1
'''
**Leaf pseudo-superclass metadata length** (i.e., total number of sub-items of
each item describing a **leaf pseudo-superclass** (i.e., that either is not
user-defined by a third-party package *or* is user-defined by a third-party
package but has yet to be identified as such) of the ``hint_bases`` list local
to the :func:`.get_hint_pep484585_generic_args_full` getter).
'''


#FIXME: Revise docstring accordingly, please. *sigh*
_HINT_BASES_INDEX_TYPEARG_TO_HINT = next(__hint_bases_counter)
# _HINT_BASES_INDEX_ARGS_STACK = next(__hint_bases_counter)
'''
0-based index into each **pseudo-superclass metadata** (i.e., list describing a
transitive pseudo-superclass of the :pep:`484`- or :pep:`585`-compliant generic
passed to the :func:`.get_hint_pep484585_generic_args_full` getter) stored in
the ``hint_bases`` list local to that getter, providing the currently visited
pseudo-superclass' **direct child hint stack** (i.e., list of the zero or more
child hints directly subscripting this pseudo-superclass in reverse order,
embodying an efficiently poppable stack of these hints).

Note that a seemingly sensible alternative to this list would be to preserve
this as a tuple of child hints and additionally record:

* The currently indexed child hint of that tuple.
* The total number of child hints in that tuple.

Although trivial, doing so would necessitate additional space *and* time
consumption (e.g., to both assign and access this metadata). Since the average
Python statement is so slow, a one-liner producing a poppable stack minimizes
the number of Python statements and thus computational cost.
'''


_HINT_BASES_INDEX_ARGS_FULL = next(__hint_bases_counter)
'''
0-based index into each **pseudo-superclass metadata** (i.e., list describing a
transitive pseudo-superclass of the :pep:`484`- or :pep:`585`-compliant generic
passed to the :func:`.get_hint_pep484585_generic_args_full` getter) stored in
the ``hint_bases`` list local to that getter, providing the currently visited
pseudo-superclass' **transitive child hints** (i.e., list of the zero or more
child hints transitively subscripting this pseudo-superclass).
'''


# Delete the above counter for safety and sanity in equal measure.
del __hint_bases_counter
