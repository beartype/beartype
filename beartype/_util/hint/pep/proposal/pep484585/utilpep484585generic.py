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
    # Sequence,
    # Tuple,
    Union,
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
    SequenceHints,
    # SetHints,
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

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        get_hint_pep_sign_or_none,
    )

    # ....................{ PREAMBLE                       }....................
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

    # ....................{ LOCALS                         }....................
    # Metadata describing the passed generic, used to seed the depth-first
    # search (DFS) below with the first pseudo-superclass to be visited.
    hint_root_data = [
        # This generic.
        hint,

        # Metadata describing the direct parent pseudo-superclass of this
        # generic. By definition, this generic is the root of this n-ary tree
        # and thus has *NO* parent (either direct or indirect).
        None,
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
    hint_bases_data: _HintBasesData = [hint_root_data]

    # ....................{ SEARCH                         }....................
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
        # of this pseudo-superclass.
        is_hint_base_leaf = len(hint_base_data) == _HINT_BASE_DATA_LEN_LEAF

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
            is_hint_pep484585_generic_user(hint_base)
        # Then this DFS is currently recursing down into the child
        # pseudo-superclasses of this pseudo-superclass. In this case...
        ):
            # Expand the metadata describing this pseudo-superclass from its
            # current 2-list "(hint, hint_super_data)" into the expanded 4-list
            # "(hint, hint_super_data, hint_args_stack, hint_args_full)".
            # Specifically, append (in order):
            # * Poppable stack of the zero or more child hints directly
            #   subscripting this child pseudo-superclass.
            # * List of the zero or more child hints transitively subscripting
            #   this child pseudo-superclass.
            hint_base_data.append(make_stack(get_hint_pep_args(hint_base)))
            hint_base_data.append([])

            # Tuple of the one or more child pseudo-superclasses of this
            # pseudo-superclass.
            # print(f'Introspecting generic {hint} unerased bases...')
            hint_child_bases = get_hint_pep484585_generic_bases_unerased(
                hint=hint_base,
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
        # Else, either:
        # * This DFS has already visited this pseudo-superclass *OR*...
        # * This pseudo-superclass is a "terminal" leaf generic *OR*...
        # * This pseudo-superclass is *NOT* a generic.
        #
        # In any case, this DFS should *NOT* recurse (back) down into this
        # pseudo-superclass. Therefore, this DFS is currently recursing back up
        # out of this pseudo-superclass into its parent pseudo-superclass.
        else:
            # Pop this pseudo-superclass off this stack.
            hint_bases_data.pop()
            # print(f'Resuming generic {hint} pseudo-superclass {hint_base} args {hint_base_args}...')

            # Sequence of the zero or more child hints subscripting this
            # pseudo-superclass, defined as either...
            hint_base_args: SequenceHints = (  # pyright: ignore
                # If this is a terminal leaf pseudo-superclass, the tuple of
                # zero or more child hints directly subscripting this
                # pseudo-superclass. Why? Because this pseudo-superclass has
                # *NO* child pseudo-superclass to recurse down into. If this
                # pseudo-superclass had one or more child pseudo-superclasses to
                # recurse down into, then those child pseudo-superclasses would
                # have defined the "hint_base_data[_HINT_BASES_INDEX_ARGS_FULL]"
                # list accessed by the next branch, providing the list of zero
                # or more child hints transitively subscripting this
                # pseudo-superclass. Although that list remains undefined, the
                # tuple of zero or more child hints directly subscripting this
                # pseudo-superclass is semantically equivalent to what that list
                # would have been (had that list actually been defined).
                get_hint_pep_args(hint_base)
                if is_hint_base_leaf else
                # Else, this is *NOT* a terminal leaf pseudo-superclass. In this
                # case, the list of zero or more child hints transitively
                # subscripting this pseudo-superclass previously defined by
                # child pseudo-superclasses of this pseudo-superclass in
                # lower-level recursion.
                hint_base_data[_HINT_BASES_INDEX_ARGS_FULL]
            )

            # If this pseudo-superclass is transitively subscripted by
            # at least one child hint...
            if hint_base_args:
                # Metadata describing the direct parent pseudo-superclass of
                # this pseudo-superclass.
                hint_base_super_data = hint_base_data[_HINT_BASES_INDEX_PARENT]
                # print(f'Resuming generic {hint} pseudo-superclass {hint_base} args {hint_base_args}...')

                # If this pseudo-superclass has a parent pseudo-superclass
                # (i.e., this pseudo-superclass is *NOT* the passed root generic
                # and is thus a transitive child of this generic)...
                if hint_base_super_data:
                    # Poppable stack of the zero or more child hints directly
                    # subscripting this parent pseudo-superclass.
                    hint_base_super_args_stack = hint_base_super_data[  # pyright: ignore
                        _HINT_BASES_INDEX_ARGS_STACK]

                    # If this parent pseudo-superclass of this pseudo-superclass
                    # is still directly subscripted by one or more child hints
                    # that have yet to "bubble up" the class hierarchy (i.e., by
                    # replacing the first unused type variable transitively
                    # subscripting this child pseudo-superclass)...
                    if hint_base_super_args_stack:
                        # For the 0-based index of each child hint transitively
                        # subscripting this pseudo-superclass and this hint...
                        for hint_base_arg_index, hint_base_arg in (
                            enumerate(hint_base_args)):
                            # Sign uniquely identifying this child hint
                            # transitively subscripting this pseudo-superclass
                            # if any *OR* "None" (i.e., if this child hint is a
                            # simple type).
                            hint_base_arg_sign = get_hint_pep_sign_or_none(
                                hint_base_arg)

                            # If this hint is a type variable...
                            if hint_base_arg_sign is HintSignTypeVar:
                                # If the sequence of zero or more child hints
                                # subscripting this pseudo-superclass is still
                                # an unmodifiable tuple, coerce this sequence
                                # into a modifiable list.
                                #
                                # Note that this is a trivial microoptimization.
                                # This could have been streamlined by
                                # unconditionally coercing the call to
                                # "get_hint_pep_args(hint_base)" above into a
                                # list. However, doing so would incur
                                # unnecessary costs in various common cases.
                                if hint_base_args.__class__ is tuple:
                                    hint_base_args = list(hint_base_args)
                                # Else, this sequence is already a list.
                                #
                                # In either case, this sequence is now a list.

                                # "Bubble up" the currently unassigned child
                                # hint directly subscripting this parent
                                # pseudo-superclass into the "empty placeholder"
                                # signified by this type variable in this list
                                # of child hints transitively subscripting this
                                # pseudo-superclass.   <-- lolwat
                                hint_base_args[hint_base_arg_index] = (  # type: ignore[index]
                                    hint_base_super_args_stack.pop())  # pyright: ignore
                                # print(f'Bubbled up generic {hint} arg {hint_args[hint_args_index_curr]}...')
                                # print(f'...into pseudo-superclass {hint_base} args {hint_base_args}!')

                                # If all child hints directly subscripting this
                                # parent pseudo-superclass have now been bubbled
                                # up, halt this nested iteration.
                                if not hint_base_super_args_stack:
                                    break
                                # Else, one or more child hints directly
                                # subscripting this parent pseudo-superclass
                                # have yet to be bubbled up. In this case,
                                # continue to the next such hint.
                            # Else, this hint is *NOT* a type variable. In this
                            # case, preserve this hint and continue to the next.
                    # Else, all child hints directly subscripting this parent
                    # pseudo-superclass of this pseudo-superclass have already
                    # been "bubbled up" the class hierarchy.

                    # Parent list of the zero or more child hints transitively
                    # subscripting this parent pseudo-superclass of this
                    # pseudo-superclass.
                    hint_base_super_args_full = hint_base_super_data[  # pyright: ignore
                        _HINT_BASES_INDEX_ARGS_FULL]

                    # Append to this parent list this child list of all child
                    # hints transitively subscripting this pseudo-superclass.
                    hint_base_super_args_full.extend(hint_base_args)  # pyright: ignore
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
                    hint=hint_base,
                    exception_cls=exception_cls,
                    exception_prefix=exception_prefix,
                )

                # If this pseudo-superclass is equal to this target, return the
                # list of the zero or more child hints transitively subscripting
                # this target pseudo-superclass, coerced into a tuple.
                #
                # This logic short-circuits this recursion and is one of several
                # reasons to prefer a non-recursive algorithm. This algorithm
                # was initially implemented recursively (supposedly for
                # simplicity); doing so introduced significant unforeseen
                # complications by effectively preventing short-circuiting.
                # After all, a recursive algorithm cannot short-circuit up out
                # of a deeply nested recursive call stack.
                if hint_base_type == hint_base_target:
                    return tuple(hint_base_args)
                # Else, this pseudo-superclass is *NOT* equal to this target.
            # Else, *NO* target pseudo-superclass is being searched for.

    # ....................{ RETURN                         }....................
    # If the caller passed a target pseudo-superclass, that target *CANNOT* be a
    # pseudo-superclass of this generic. Why? Because if that target had been a
    # pseudo-superclass of this generic, then the above DFS would have found
    # that target and immediately returned the desired list on doing so.
    # However, that DFS failed to return and thus find that target. In this
    # case, raise an exception.
    if hint_base_target:
        raise exception_cls(
            f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
            f'pseudo-superclass target {repr(hint_base_target)} not found.'
        )
    # Else, the caller did *NOT* pass a target pseudo-superclass.
    #
    # If the metadata describing the passed generic is still its initial size,
    # then the above DFS failed to expand this metadata with the
    # "_HINT_BASES_INDEX_ARGS_FULL" index accessed below. In turn, this implies
    # that the above DFS failed to recurse down into the child
    # pseudo-superclasses of this generic. However, by definition, *ALL*
    # generics subclass one or more pseudo-superclasses. The above DFS should
    # have recursed down into those pseudo-superclasses. In this case, raise an
    # exception.
    #
    # Note that this should *NEVER* occur.
    elif len(hint_root_data) == _HINT_BASE_DATA_LEN_LEAF:  # pragma: no cover
        raise exception_cls(
            f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
            f'pseudo-superclasses not found.'
        )
    # Else, the above DFS expanded the metadata describing the passed generic
    # with the "_HINT_BASES_INDEX_ARGS_FULL" index accessed below.

    # List of the zero or more child hints transitively subscripting this
    # generic discovered by the above DFS.
    hint_root_args_full = hint_root_data[_HINT_BASES_INDEX_ARGS_FULL]

    # Return this list coerced into a tuple.
    return tuple(hint_root_args_full)  # type: ignore[arg-type]


#FIXME: Ideally, all of the below should themselves be annotated as ": Hint".
#Mypy likes that but pyright hates that. This is why we can't have good things.
_HintBaseData = List[Union[Hint, ListHints, '_HintBaseData']]
'''
PEP-compliant type hint matching each **unvisited pseudo-superclass** (i.e.,
item of the ``hint_bases`` fixed list local to the
:func:`.get_hint_pep484585_generic_args_full` getter, describing each
pseudo-superclass of the generic passed to that getter that has yet to be
internally visited by the depth-first search (DFS) performed by that getter).
'''


_HintBasesData = List[_HintBaseData]
'''
PEP-compliant type hint matching the ``hint_bases`` fixed list local to the
:func:`.get_hint_pep484585_generic_args_full` getter.
'''


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


_HINT_BASES_INDEX_ARGS_STACK = next(__hint_bases_counter)
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
the number of Python statements and thus the computational cost.
'''


_HINT_BASE_DATA_LEN_LEAF = _HINT_BASES_INDEX_ARGS_STACK
'''
**Leaf pseudo-superclass metadata length** (i.e., total number of sub-items of
each item describing a **leaf pseudo-superclass** (i.e., that either is not
user-defined by a third-party package *or* is user-defined by a third-party
package but has yet to be identified as such) of the ``hint_bases`` list local
to the :func:`.get_hint_pep484585_generic_args_full` getter).
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
