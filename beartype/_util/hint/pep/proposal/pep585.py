#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`585`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep585Exception
from beartype._cave._cavefast import HintGenericSubscriptedType
from beartype._data.typing.datatypingport import (
    Hint,
    TupleHints,
)
from beartype._data.typing.datatyping import (
    TupleTypeVars,
    TypeException,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.kind.maplike.utilmapset import update_mapping_keys
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
from typing import (
    # Optional,
    TypeVar,
)

# ....................{ HINTS                              }....................
HINT_PEP585_TUPLE_EMPTY = tuple[()]
'''
:pep:`585`-compliant empty fixed-length tuple type hint.
'''

# ....................{ RAISERS                            }....................
def die_unless_hint_pep585_generic(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep585Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a :pep:`585`-compliant
    **generic** (i.e., either a type originally subclassing at least one
    subscripted :pep:`585`-compliant pseudo-superclass *or* an object
    subscripted by one or more child type hints originating from such a type).

    This raiser raises an exception unless this object is either a subscripted
    or unsubscripted :pep:`585`-compliant generic.

    Parameters
    ----------
    hint : Hint
        Object to be validated.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Raises
    ------
    exception_cls
        If this object is *not* a :pep:`585`-compliant generic.
    '''

    # If this object is *NOT* a PEP 585-compliant generic, raise an exception.
    if not is_hint_pep585_generic(hint):
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not PEP 585 generic.')
    # Else, this object is a PEP 585-compliant generic.

# ....................{ TESTERS                            }....................
def is_hint_pep585_builtin_subbed(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed object is a :pep:`585`-compliant
    **subscripted builtin type hint** (i.e., C-based type hint instantiated by
    subscripting either a concrete builtin container class like :class:`list` or
    :class:`tuple` *or* an abstract base class (ABC) declared by the
    :mod:`collections.abc` submodule like :class:`collections.abc.Iterable` or
    :class:`collections.abc.Sequence`).

    This tester additionally returns :data:`True` for third-party type hints
    whose types subclass the :class:`types.GenericAlias` superclass, including:

    * ``numpy.typing.NDArray[...]`` type hints.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This tester returns** :data:`False` for :pep:`585`-compliant generics,
    which fail to satisfy the same API as all other :pep:`585`-compliant type
    hints. Why? Because :pep:`560`-type erasure erases the low-level superclass
    detected by this tester on :pep:`585`-compliant generics immediately after
    those generics are declared, preventing their subsequent detection as
    :pep:`585`-compliant. Instead, :pep:`585`-compliant generics are only
    detectable by calling either:

    * The high-level PEP-agnostic
      :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep484585_generic`
      tester.
    * The low-level :pep:`585`-specific :func:`.is_hint_pep585_generic` tester.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`585`-compliant type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic)

    # Return true only if this hint...
    return (
        # Is either a PEP 484- or -585-compliant subscripted generic or
        # PEP 585-compliant builtin *AND*...
        isinstance(hint, HintGenericSubscriptedType) and
        # Is *NOT* a PEP 484- or -585-compliant subscripted generic.
        not is_hint_pep484585_generic(hint)  # pyright: ignore
    )


def is_hint_pep585_generic(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed object is a :pep:`585`-compliant **generic**
    (i.e., either a type originally subclassing at least one subscripted
    :pep:`585`-compliant pseudo-superclass *or* an object subscripted by one or
    more child type hints originating from such a type).

    This tester returns :data:`True` if this object is either a subscripted or
    unsubscripted :pep:`585`-compliant generic.

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`585`-compliant generic.
    '''

    # Return true only if object is either...
    return (
        # A PEP 585-compliant unsubscripted generic *OR*...
        is_hint_pep585_generic_unsubbed(hint) or
        # A PEP 585-compliant subscripted generic.
        is_hint_pep585_generic_subbed(hint)
    )


#FIXME: Unit test us up, please.
def is_hint_pep585_generic_subbed(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed object is a :pep:`585`-compliant
    **subscripted generic** (i.e., object subscripted by one or more child type
    hints originating from a type originally subclassing at least one
    subscripted :pep:`585`-compliant pseudo-superclass).

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`585`-compliant subscripted
        generic.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_origin_or_none)

    # Arbitrary object originating this hint if any *OR* "None" otherwise.
    hint_origin = get_hint_pep_origin_or_none(hint)

    # Return true only if...
    return (
        # An object originates this hint *AND*...
        hint_origin is not None and
        # This origin object is an unsubscripted generic type, which would then
        # imply this hint to be a subscripted generic. If this strikes you as
        # insane, you're not alone.
        is_hint_pep585_generic_unsubbed(hint_origin)
    )


#FIXME: Unit test us up, please.
@callable_cached
def is_hint_pep585_generic_unsubbed(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed object is a :pep:`585`-compliant
    **unsubscripted generic** (i.e., type originally subclassing at least one
    subscripted :pep:`585`-compliant pseudo-superclass).

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`585`-compliant unsubscripted
        generic.
    '''

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args
    from beartype._util.hint.pep.proposal.pep560 import (
        is_hint_pep560,
        iter_hint_pep560_bases_unerased,
    )

    # ....................{ NOOP                           }....................
    # If it is *NOT* the case that...
    if not (
        # This hint is a type *AND*...
        isinstance(hint, type) and
        # This type is PEP 560-compliant (i.e., defines the "__orig_bases__"
        # dunder attribute) and thus subclasses one or more erased
        # pseudo-superclasses *AND*...
        is_hint_pep560(hint) and
        # Either...
        (
            # The active Python interpreter targets Python >= 3.11 *OR*...
            IS_PYTHON_AT_LEAST_3_11 or
            # The active Python interpreter targets Python <= 3.10. In this
            # case, a simple subclass test does *NOT* suffice to detect a PEP
            # 585-compliant unsubscripted generic. Why? Because Python <=
            # 3.10 implements PEP 585-compliant subscripted generics as types!
            # But PEP 585-compliant unsubscripted generics are also types! Lo:
            #     $ python3.10
            #     >>> class MuhGeneric(list): pass
            #     >>> isinstance(MuhGeneric, type)
            #     True  # <-- good
            #     >>> isinstance(MuhGeneric[str], type)
            #     True  # <-- *BAD*
            #
            #     $ python3.11
            #     >>> class MuhGeneric(list): pass
            #     >>> isinstance(MuhGeneric, type)
            #     True  # <-- good
            #     >>> isinstance(MuhGeneric[str], type)
            #     False  # <-- good
            #
            # Disambiguating this edge case requires also detecting whether
            # this PEP 484-compliant generic is subscripted by one or more
            # child hints.
            #
            # This PEP 484-compliant generic is unsubscripted.
            not get_hint_pep_args(hint)
        )
    # Then this hint *CANNOT* be a PEP 585-compliant unsubscripted generic. In
    # this case, return false immediately.
    ):
        return False
    # Else, this hint is a PEP 560-compliant type subclassing one or more
    # pseudo-superclasses. Since this type *COULD* be a PEP 585-compliant
    # unsubscripted generic, continue testing.

    # ....................{ SEARCH                         }....................
    #FIXME: [SPEED] Optimize into a "while" loop. *sigh*
    # For each transitive pseudo-superclass of this PEP 560-compliant hint...
    #
    # Unsurprisingly, PEP 585-compliant generics have absolutely *NO*
    # commonality with PEP 484-compliant generics. While the latter are
    # trivially detectable as subclassing "typing.Generic" after type erasure,
    # the former are *NOT*. The only means of deterministically deciding whether
    # or not a hint is a PEP 585-compliant generic is if:
    # * That class defines both the __class_getitem__() dunder method *AND* the
    #   "__orig_bases__" instance variable. Note that this condition in and of
    #   itself is insufficient to decide PEP 585-compliance as a generic. Why?
    #   Because these dunder attributes have been standardized under various
    #   PEPs and may thus be implemented by *ANY* arbitrary classes.
    # * The "__orig_bases__" instance variable is a non-empty tuple.
    # * One or more objects listed in that tuple are PEP 585-compliant C-based
    #   subscripted generics (e.g., "list[str]").
    #
    # Note we could technically also test that this hint defines the
    # __class_getitem__() dunder method. Since that test would *NOT* suffice to
    # ensure that this hint is a PEP 585-compliant generic, however, there
    # exists little benefit to doing so.
    for hint_base in iter_hint_pep560_bases_unerased(hint):
        # If this transitive pseudo-superclass is itself a PEP 585-compliant
        # subscripted generic (e.g., "list[str]"), the passed hint transitively
        # subclasses a PEP 585-compliant generic. By transitivity, this hint
        # *MUST* be a PEP 585-compliant generic as well. Return true!
        if is_hint_pep585_builtin_subbed(hint_base):
            return True
        # Else, this pseudo-superclass is *NOT* a PEP 585-compliant subscripted
        # generic. In this case, continue to the next pseudo-superclass.

    # ....................{ RETURN                         }....................
    # Since *NO* such pseudo-superclasses are PEP 585-compliant subscripted
    # generics, this hint is *NOT* a PEP 585-compliant generic. In this case,
    # return false.
    return False

# ....................{ GETTERS                            }....................
def get_hint_pep585_generic_bases_unerased(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep585Exception,
    exception_prefix: str = '',
) -> TupleHints:
    '''
    Tuple of all unerased :pep:`585`-compliant **pseudo-superclasses** (i.e.,
    :mod:`typing` objects originally listed as superclasses prior to their
    implicit type erasure under :pep:`560`) of the passed :pep:`585`-compliant
    **generic** (i.e., class subclassing at least one non-class
    :pep:`585`-compliant object).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    Tuple[Hint, ...]
        Tuple of the one or more unerased pseudo-superclasses of this
        :pep:`585`-compliant generic.

    Raises
    ------
    exception_cls
        If this hint is *not* a :pep:`585`-compliant generic.

    See Also
    --------
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget.get_hint_pep484585_generic_bases_unerased`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_unsubbed_type_or_none)

    # If this hint is *NOT* a class, reduce this hint to the object originating
    # this hint if any. See the is_hint_pep484_generic() tester for details.
    hint = get_hint_pep484585_generic_unsubbed_type_or_none(hint)  # type: ignore[assignment]

    # If this hint is *NOT* a PEP 585-compliant generic, raise an exception.
    die_unless_hint_pep585_generic(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this hint is a PEP 585-compliant generic.

    # Return the tuple of all unerased pseudo-superclasses of this generic.
    # While the "__orig_bases__" dunder instance variable is *NOT* guaranteed
    # to exist for PEP 484-compliant generic types, this variable is guaranteed
    # to exist for PEP 585-compliant generic types. Thanks for small favours.
    return hint.__orig_bases__  # pyright: ignore


@callable_cached
def get_hint_pep585_generic_typeargs_packed(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    is_unsub: bool = False,
    exception_cls: TypeException = BeartypeDecorHintPep585Exception,
    exception_prefix: str = '',
) -> TupleTypeVars:
    '''
    Tuple of the one or more **unique transitive packed type parameters** (i.e.,
    :pep:`484`-compliant type variables, :pep:`612`-compliant parameter
    specifications, or :pep:`646`-compliant type variable tuples uniquely
    parametrizing both the passed :pep:`585`-compliant generic *and* all
    pseudo-superclasses of this generic originally specified at the time these
    generics were declared, ignoring duplicates) if this hint is a generic and
    thus necessarily parametrized by one or more such type parameters *or* the
    empty tuple otherwise (i.e., if this hint is *not* a generic and is thus
    unparametrized).

    This getter is memoized for efficiency.

    Motivation
    ----------
    This getter mimics the behaviour of the ``__parameters__`` dunder attributes
    for :pep:`484`-compliant generics, whose values similarly collect the tuples
    of all unique type parameters originally parametrizing those generics. Alas,
    the current implementation of :pep:`585` under at least Python 3.9—3.15 is
    fundamentally broken with respect to parametrized generics. While
    :pep:`484`-compliant generics properly propagate type parameters from
    pseudo-superclasses to subclasses, :pep:`585` fails to do so. This getter
    "fills in the gaps" by recovering these type parameters from parametrized
    :pep:`585`-compliant generics by iteratively constructing a new tuple from
    the type parameters parametrizing all pseudo-superclasses of this generic.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.
    is_unsub : bool, default: False
        If this hint is a **subscripted generic** (i.e., object subscripted by
        one or more child hints originating from a type originally subclassing
        at least one subscripted :pep:`585`-compliant generic pseudo-superclass)
        *and* the caller requests that this generic be stripped of all
        subscripting child hints, reduce this subscripted generic to the
        unsubscripted generic underlying this subscripted generic. See also the
        parameter of the same name accepted by the higher-level
        :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_typeargs_packed`
        getter for further discussion.
    exception_cls : TypeException, default: BeartypeDecorHintPep585Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep585Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    tuple[TypeVar, ...]
        Either:

        * If this :pep:`585`-compliant generic is:

          * Subscripted, the empty tuple. This mirrors the behaviour of the
            ``__parameters__`` dunder attribute defined on :pep:`484`-compliant
            subscripted generics, which is *always* set to the empty tuple.
          * Unsubscripted, the tuple of all unique type parameters parametrizing
            this unsubscripted generic

        * Else, the empty tuple.

    Raises
    ------
    BeartypeDecorHintPep585Exception
        If this hint is *not* a :pep:`585`-compliant generic.
    '''
    assert isinstance(is_unsub, bool), f'{repr(is_unsub)} not boolean.'
    # print(f'Getting PEP 585 generic {hint} typevars...')

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: The PEP 484-compliant "__parameters__" dunder attribute
    # unconditionally correctly defined for *ALL* PEP 484-compliant generics is
    # only conditionally defined for a subset of PEP 585-compliant generics.
    # When conditionally defined for a given PEP 585-compliant generic, however,
    # the value of the "__parameters__" dunder attribute is frequently
    # incorrect. In other words, the "__parameters__" dunder attribute is
    # fundamentally unreliable and *MUST* thus be unconditionally ignored for
    # *ALL* PEP 585-compliant generics. This getter circumvents this
    # unreliability by effectively dynamically deciding what the value of the
    # "__parameters__" dunder attribute should have been for the passed PEP
    # 585-compliant generic had Python correctly defined that attribute. *UGH*.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_unsubbed_type)
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        get_hint_pep_typeargs_packed,
    )

    # ....................{ VALIDATE                       }....................
    # If this hint is *NOT* a PEP 585-compliant generic, raise an exception.
    die_unless_hint_pep585_generic(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this hint is a PEP 585-compliant generic.

    # ....................{ LOCALS                         }....................
    # Current number of unbound type parameters (i.e., type parameters that have
    # yet to be assigned a corresponding child hint subscripting a transitive
    # pseudo-superclass of the passed generic, possibly including that generic)
    # that remain to be assigned such child hints by iteration performed below.
    hint_typeargs_unbound_remaining: int = 0

    # ....................{ UNSUBSCRIPT                    }....................
    # If this hint is a PEP 585-compliant subscripted generic...
    if is_hint_pep585_generic_subbed(hint):
        # PEP 585-compliant unsubscripted generic underlying this subscripted
        # generic.
        hint_unsubbed = get_hint_pep484585_generic_unsubbed_type(hint)

        # If the caller requested that this subscripted generic be stripped of
        # all subscripting child hints, reduce this subscripted generic to this
        # unsubscripted generic. See also get_hint_pep_typeargs_packed().
        if is_unsub:
            hint = hint_unsubbed
        # Else, the caller did *NOT* request that this subscripted generic be
        # stripped of all subscripting child hints. In this case...
        else:
            # Number of child hints subscripting this subscripted generic.
            hint_childs_len = len(get_hint_pep_args(hint))
            # print(f'hint_childs_len: {hint_childs_len}')

            # Possibly erroneous tuple of the zero or more unbound transitive
            # packed type variables that Python (possibly erroneously) claims
            # parametrize this subscripted generic.
            #
            # Python defines this tuple correctly for *MOST* use cases. Indeed,
            # Python defines this tuple incorrectly *ONLY* for the valid use
            # case of partially subscripted generics (i.e., generics subscripted
            # by fewer child hints than the number of unbound type parameters
            # parametrizing the *UNSUBSCRIPTED* forms of those generics). For
            # partially subscripted generics, Python erroneously defines the
            # "__parameters__" dunder attribute to be the empty tuple rather
            # than correctly defining this attribute to be the non-empty tuple
            # of all bound type parameters assigned some child hint subscripting
            # this partially subscripted generic: e.g.,
            #     >>> from collections.abc import Sequence
            #     >>> from typing import Generic, TypeVar
            #
            #     # Define two PEP 484-compliant unconstrained type variables.
            #     >>> T = TypeVar('T')
            #     >>> U = TypeVar('U')
            #
            #     # PEP 484-compliant generic parametrized by a single
            #     # PEP 484-compliant type variable.
            #     >>> class Pep484GenericT(Generic[T]): ...
            #
            #     # PEP 484- and 585-compliant generic subclassing both:
            #     # * That PEP 484-compliant generic, parametrized by the same
            #     #   type variable.
            #     # * A PEP 585-compliant abstract base class (ABC) parametrized
            #     #   by a new type variable.
            #     >>> class Pep484585GenericTSequenceU(
            #     ...     list[bool], Pep484GenericT[T], Sequence[U]): ...
            #
            #     # Show that Python correctly defines the "__parameters__"
            #     # dunder attribute for this unsubscripted generic.
            #     >>> Pep484585GenericTSequenceU.__parameters__)
            #     (~T, ~U)  # <-- good
            #
            #     # Show that Python erroneously defines the "__parameters__"
            #     # dunder attribute for this partially subscripted generic to
            #     # be the empty tuple rather than the non-empty tuple "(~U)".
            #     >>> Pep484585GenericTSequenceU[float].__parameters__)
            #     ()  # <-------- *BAD* wtf, Python!? should be "(~U)"
            hint_typeargs_unbound = getattr(hint, '__parameters__', ())
            # print(f'Peeked PEP 585 unsubscripted generic {hint} params {hint_typeargs_unbound}...')

            # If Python claims this subscripted generic to be parametrized by
            # one or more unbound type parameters, this claim appears to be
            # accurate (or accurate enough in the sense that we have yet to
            # receive an issue from a user encountering a real-world
            # counterexample). In this case, return this tuple as is.
            if hint_typeargs_unbound:
                return hint_typeargs_unbound
            # Else, Python (possibly erroneously) claims this subscripted
            # generic to be parametrized by *NO* unbound type parameters. As
            # shown above, this claim is usually true for the common case while
            # *NEVER* being true for the uncommon case of a partially
            # subscripted generic. Since this claim is thus untrustworthy, we
            # have *NO* recourse but to ignore this claim and manually compute
            # the value of the correct "__parameters__" dunder attribute below.

            # Initial number of unbound type parameters that remain to be
            # assigned child hints subscripting transitive pseudo-superclasses
            # of this generic by iteration performed below, initialized to the
            # number of child hints directly subscripting this generic.
            hint_typeargs_unbound_remaining = hint_childs_len
    # Else, this hint is *NOT* a PEP 585-compliant subscripted generic. In this
    # case, this hint *MUST* be a PEP 585-compliant unsubscripted generic.
    # Preserve this unsubscripted generic as is.

    # ....................{ RECURSE                        }....................
    # Tuple of all pseudo-superclasses of this unsubscripted generic.
    hint_bases = get_hint_pep585_generic_bases_unerased(hint)

    #FIXME: [SPEED] Optimize away garbage collection by calling
    #acquire_instance() and release_instance() instead, please. *sigh*
    # Dictionary mapping from all type parameters parametrizing these
    # pseudo-superclasses to the "None" singleton, thus preserving the ordering
    # of these type parameters while yet discarding duplicate type parameters
    # parametrizing multiple pseudo-superclasses.
    #
    # Note that:
    # * A dictionary rather than set is intentionally leveraged. Why? Ordering.
    #   Order of type parameters is *EXTREMELY* significant (e.g., when mapping
    #   type parameters to child hints in a type parameter lookup table).
    #   Whereas dictionaries preserve insertion order as of Python >= 3.7, sets
    #   currently do *NOT*. Since this algorithm *ONLY* employs a dictionary to
    #   preserve insertion order, the values of this dictionary are irrelevant
    #   and thus unconditionally set to the "None" singleton. I sigh so hard.
    # * The following inefficient iteration *CANNOT* be trivially reduced to a
    #   dictionary comprehension, as each get_hint_pep_typeargs_packed() call
    #   returns a tuple of type parameters rather than a single type parameter
    #   to be added to this dictionary.
    hint_typeargs_to_none: dict[TypeVar, None] = dict()

    #FIXME: [SPEED] Optimize into a "while" loop, please. *sigh*
    #FIXME: *LOL*. This recursion is super-slow, clunky, and almost certainly
    #involves a great deal of recomputation. The only thing that makes any of
    #this bearable is that this *DOES* appear to compute the correct tuple --
    #which, ultimately, is all that matters. Thus, we sigh and silently ignore
    #something no one cares about for another year. **SIGH**
    #
    #A dramatically more efficient approach would be to:
    #* First:
    #  * Inline the body of this low-level
    #    get_hint_pep585_generic_typeargs_packed() getter directly inside the
    #    body of the high-level get_hint_typeargs_packed() getter. Doing so
    #    enables newer Python interpreters to trivially optimize this recursion
    #    with standard tail recursion optimizations. Doing so is also an
    #    essential step to reimplementing this recursion with iteration.
    #  * Decorate get_hint_typeargs_packed() by @callable_cached. Essential!
    #  * Excise up this obsolete get_hint_pep585_generic_typeargs_packed()
    #    getter at that point, including the corresponding unit test (which has
    #    already been subsumed by the more robust
    #    test_get_hint_typeargs_packed() unit test, thankfully).
    #* Next:
    #  * Reimplement this recursion inside get_hint_typeargs_packed() with
    #    "while" loop-based iteration. Non-trivial, of course -- but the big
    #    efficiency gains usually are. *shrug*

    # For each such pseudo-superclass...
    for hint_base in hint_bases:
        # Tuple of the zero or more unbound type parameters parametrizing this
        # pseudo-superclass.
        hint_base_typeargs = get_hint_pep_typeargs_packed(
            hint=hint_base,
            # Preserve the typically undesirable value of the low-level
            # "__parameters__" dunder attribute defined on this
            # pseudo-superclass (if any) rather than evaluating that attribute
            # after stripping any child hints subscripting this
            # pseudo-superclass. Why? Because the latter approach would
            # erroneously return both:
            # * Unbound type parameters (i.e., type parameters that have yet to
            #   be bound to a child hint subscripting this pseudo-superclass).
            # * Bound type parameters (i.e., type parameters that have already
            #   been bound to a child hint subscripting this pseudo-superclass).
            #
            # The former approach returns *ONLY* unbound parameters, which is
            # *ALWAYS* what the caller wants (regardless of whether the caller
            # passed "is_unsub=True" or not, as that passed parameter is *ONLY*
            # intended to unsubscript the passed generic itself).
            is_unsub=False,
        )

        #FIXME: Comment us up, please. *sigh*
        #FIXME: As we iteratively discover each unbound type variable here,
        #we semantically (but not actually) "bind" that unbound type variable by:
        #* Popping the top child hint subscripting this subscripted generic off this
        #  list, effectively mimicing the action of "binding" this child hint to
        #  this unbound type variable.
        #* Silently ignore this type variable, which is now bound and thus no longer
        #  suitable for returning in the tuple of all unbound type variables
        #  parametrizing this subscripted generic.

        # If...
        if (
            # One or more unbound type parameters remain to be assigned
            # corresponding child hints subscripting transitive
            # pseudo-superclasses of this generic *AND*...
            hint_typeargs_unbound_remaining and
            # This pseudo-superclass is transitively parametrized by one or more
            # unbound type parameters...
            hint_base_typeargs
        ):
        # Then greedily assign as many of these unbound type parameters as
        # possible that transitively parametrize this pseudo-superclass. For
        # efficiency, we avoid doing so in actuality. We only semantically (but
        # *NOT* actually) assign these unbound type parameters through trivial
        # numerical bookkeeping.
            # Number of unbound type parameters transitively parametrizing this
            # pseudo-superclass of the passed subscripted generic.
            hint_base_typeargs_len = len(hint_base_typeargs)

            # If the number of unbound type parameters that remain to be
            # assigned corresponding child hints subscripting transitive
            # pseudo-superclasses of this generic is less than or equal to the
            # number of unbound type parameters transitively parametrizing this
            # pseudo-superclass, then *ALL* of these remaining unbound type
            # parameters can now be greedily assigned. In this case...
            if hint_typeargs_unbound_remaining <= hint_base_typeargs_len:
                # Remove as many unbound type parameters (that remain to be
                # assigned corresponding child hints subscripting transitive
                # pseudo-superclasses of this generic) from the front of the
                # tuple of all unbound type parameters transitively
                # parametrizing this pseudo-superclass, effectively mimicking
                # the action of assigning these removed type parameters to
                # corresponding child hints. Since type parameters are greedily
                # assigned in a first-come first-serve manner, we intentionally
                # remove these type parameters from the front rather than back
                # of this tuple. These previously unbound type parameters have
                # now been (semantically, at least) assigned and are no longer
                # suitable for returning as unbound type parameters.
                hint_base_typeargs = hint_base_typeargs[
                    hint_typeargs_unbound_remaining:]

                # Record that all previously unbound type parameters that once
                # remained to be assigned corresponding child hints subscripting
                # transitive pseudo-superclasses of this generic have now been
                # completely assigned and are thus bound rather than unbound.
                hint_typeargs_unbound_remaining = 0
            # Else, the number of unbound type parameters that remain to be
            # assigned corresponding child hints subscripting transitive
            # pseudo-superclasses of this generic is greater than the number of
            # unbound type parameters transitively parametrizing this
            # pseudo-superclass. This implies that one or more of these
            # remaining unbound type parameters will still remain unassigned
            # even after greedily assigning as many of the unbound type
            # parameters transitively parametrizing this pseudo-superclass as
            # possible. In this case...
            else:
                # Record that *ALL* previously unbound type parameters
                # transitively parametrizing this pseudo-superclass have now
                # been (semantically, at least) assigned and are no longer
                # suitable for returning as unbound type parameters.
                hint_base_typeargs = ()

                # Reduce the number of unbound type parameters that remain to be
                # assigned corresponding child hints subscripting transitive
                # pseudo-superclasses of this generic by the total number of
                # previously unbound type parameters transitively parametrizing
                # this pseudo-superclass, *ALL* of which have now been assigned.
                hint_typeargs_unbound_remaining -= hint_base_typeargs_len

        # Efficiently add these still unbound type parameters transitively
        # parametrizing this pseudo-superclass as new keys of this dictionary.
        # print(f'hint_base_typeargs: {hint_base} [{get_hint_pep_typeargs_packed(hint_base)}]')
        update_mapping_keys(hint_typeargs_to_none, hint_base_typeargs)

    # ....................{ RETURN                         }....................
    # Tuple to be returned, coerced from the keys of this dictionary.
    hint_typeargs = tuple(hint_typeargs_to_none.keys())
    # print(f'Got PEP 585 generic {hint} typevars {hint_typeargs}...')

    # Return a tuple coerced from the keys of this dictionary.
    return hint_typeargs
