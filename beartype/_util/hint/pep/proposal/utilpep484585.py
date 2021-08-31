#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **dual type hint utilities**
(i.e., utility functions generically applicable to both :pep:`484`- and
:pep:`585`-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPepException
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.utilpep484 import (
    HINT_PEP484_TUPLE_EMPTY,
    get_hint_pep484_generic_bases_unerased,
    is_hint_pep484_generic,
)
from beartype._util.hint.pep.proposal.utilpep585 import (
    HINT_PEP585_TUPLE_EMPTY,
    get_hint_pep585_generic_bases_unerased,
    is_hint_pep585_generic,
)
from typing import Tuple

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ kind : generic          }....................
def get_hint_pep484585_generic_bases_unerased(
    hint: object) -> Tuple[object, ...]:
    '''
    Tuple of all **unerased pseudo-superclasses** (i.e., PEP-compliant objects
    originally listed as superclasses prior to their implicit type erasure
    under :pep:`560`) of the passed PEP-compliant **generic** (i.e., class
    superficially subclassing at least one non-class PEP-compliant object) if
    this object is a generic *or* raise an exception otherwise (i.e., if this
    object is either not a class *or* is a class subclassing no non-class
    PEP-compliant objects).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__orig_bases__`` **dunder instance variable.**
    Most PEP-compliant type hints fail to declare that variable, guaranteeing
    :class:`AttributeError` exceptions from all general-purpose logic
    attempting to directly access that variable. Thus this function, which
    "fills in the gaps" by implementing this oversight.

    **This function returns tuples possibly containing a mixture of actual
    superclasses and pseudo-superclasses superficially masquerading as actual
    superclasses subscripted by one or more PEP-compliant child hints,**
    including type variables (e.g., ``(typing.Iterable[T], typing.Sized[T])``).
    In particular, most public attributes of the :mod:`typing` module used as
    superclasses are *not* actually types but singleton objects devilishly
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

    Naturally, :pep:`560` did no such thing. The original MRO remains
    obfuscated and effectively inaccessible. While computing that MRO would
    technically be feasible, doing so would also be highly non-trivial,
    expensive, and fragile. Instead, this function retrieves *only* the tuple
    of :mod:`typing`-specific pseudo-superclasses that this object's class
    originally attempted (but failed) to subclass.

    You are probably now agitatedly cogitating to yourself in the darkness:
    "But @leycec: what do you mean :pep:`560`? Wasn't :pep:`560` released
    *after* :pep:`484`? Surely no public API defined by the Python stdlib would
    be so malicious as to silently alter the tuple of base classes listed by a
    user-defined subclass?"

    As we've established both above and elsewhere throughout the codebase,
    everything developed for `PEP 484` -- including :pep:`560`, which derives
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
      ``typing.List[T]``) are reduced to that container (e.g.,
      :class:`list`).
    * All base classes derived from an abstract base class declared by the
      :mod:`collections.abc` subpackage (e.g., ``typing.Iterable[T]``) are
      reduced to that abstract base class (e.g.,
      ``collections.abc.Iterable``).
    * All surviving base classes that are parametrized (e.g.,
      ``typing.Generic[S, T]``) are stripped of that parametrization (e.g.,
      :class:`typing.Generic`).

    Since there exists no counterpart to the :class:`typing.Generic`
    superclass, the :mod:`typing` module preserves that superclass in
    unparametrized form. Naturally, this is useless, as an unparametrized
    :class:`typing.Generic` superclass conveys no meaningful type information.
    All other superclasses are reduced to their non-:mod:`typing`
    counterparts: e.g.,

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

    So, we prefer the generally useful ``__orig_bases__`` dunder tuple over
    the generally useless ``__mro__`` dunder tuple. Note, however, that the
    latter *is* still occasionally useful and thus occasionally returned by
    this getter. For inexplicable reasons, **single-inherited protocols**
    (i.e., classes directly subclassing *only* the :pep:`544`-compliant
    :attr:`typing.Protocol` abstract base class (ABC)) are *not* subject to
    type erasure and thus constitute a notable exception to this heuristic:

        .. code-block:: python

        >>> from typing import Protocol
        >>> class UserDefinedProtocol(Protocol): pass
        >>> UserDefinedProtocol.__mro__
        (__main__.UserDefinedProtocol, typing.Protocol, typing.Generic, object)
        >>> UserDefinedProtocol.__orig_bases__
        AttributeError: type object 'UserDefinedProtocol' has no attribute
        '__orig_bases__'

    Welcome to :mod:`typing` hell, where even :mod:`typing` types lie broken
    and misshapen on the killing floor of overzealous theory-crafting purists.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Tuple[object]
        Tuple of the one or more unerased pseudo-superclasses of this
        PEP-compliant generic.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this hint is either:

        * *Not* a PEP-compliant generic.
        * Is a PEP-compliant generic subclassing *no* pseudo-superclasses.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilpepget import (
        ...     get_hint_pep484585_generic_bases_unerased)
        >>> get_hint_pep484585_generic_bases_unerased(
        ...     typing.Union[str, typing.List[int]])
        ()
        >>> T = typing.TypeVar('T')
        >>> class MuhIterable(typing.Iterable[T], typing.Container[T]): pass
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
        get_hint_pep585_generic_bases_unerased(hint)
        if is_hint_pep585_generic(hint) else
        # Else, this *MUST* be a PEP 484-compliant generic. In this case, all
        # unerased pseudo-superclasses of this PEP 484-compliant generic.
        get_hint_pep484_generic_bases_unerased(hint)
    )

    # If this generic subclasses *NO* pseudo-superclass, raise an exception.
    #
    # Note this should have already been guaranteed on our behalf by:
    # * If this generic is PEP 484-compliant, the "typing" module.
    # * If this generic is PEP 585-compliant, CPython or PyPy itself.
    if not hint_pep_generic_bases_unerased:
        raise BeartypeDecorHintPepException(
            f'Generic type hint {repr(hint)} subclasses no superclasses.')
    # Else, this generic subclasses one or more pseudo-superclasses.

    # Return this tuple of these pseudo-superclasses.
    return hint_pep_generic_bases_unerased

# ....................{ TESTERS ~ kind : generic          }....................
@callable_cached
def is_hint_pep484585_generic(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **generic** (i.e., class
    superficially subclassing at least one PEP-compliant type hint that is
    possibly *not* an actual class).

    Specifically, this tester returns ``True`` only if this object is a class
    that is either:

    * A :pep:`585`-compliant generic as tested by the lower-level
      :func:`is_hint_pep585_generic` function.
    * A :pep:`484`-compliant generic as tested by the lower-level
      :func:`is_hint_pep484_generic` function.

    This tester is memoized for efficiency. Although the implementation
    trivially reduces to a one-liner, constant factors associated with that
    one-liner are non-negligible. Moreover, this tester is called frequently
    enough to warrant its reduction to an efficient lookup.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a generic.

    See Also
    ----------
    :func:`is_hint_pep_typevared`
        Commentary on the relation between generics and parametrized hints.
    '''

    # Return true only if this hint is...
    return (
        # A PEP 484-compliant generic. Note this test trivially reduces to
        # an O(1) operation and is thus tested first.
        is_hint_pep484_generic(hint) or
        # A PEP 585-compliant generic. Note this test is O(n) in n the
        # number of pseudo-superclasses originally subclassed by this
        # generic and is thus tested last.
        is_hint_pep585_generic(hint)
    )

# ....................{ TESTERS ~ kind : tuple            }....................
def is_hint_pep484585_tuple_empty(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a PEP-compliant **empty fixed-length
    tuple hint** (i.e., PEP-compliant type hint constraining piths to be the
    empty tuple).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as this tester is only called under
    fairly uncommon edge cases.

    Motivation
    ----------
    Since type variables are not themselves types but rather placeholders
    dynamically replaced with types by type checkers according to various
    arcane heuristics, both type variables and types parametrized by type
    variables warrant special-purpose handling.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a type variable.
    '''

    # Return true only if this hint resembles either the PEP 484- or
    # 585-compliant fixed-length empty tuple type hint. Since there only exist
    # two such hints *AND* comparison against these hints is mostly fast, this
    # test is efficient in the general case.
    #
    # Note that this test may also be inefficiently performed by explicitly
    # obtaining this hint's sign and then subjecting this hint to specific
    # tests conditionally depending on which sign and thus PEP this hint
    # complies with: e.g.,
    #     # Return true only if this hint is either...
    #     return true (
    #         # A PEP 585-compliant "tuple"-based hint subscripted by no
    #         # child hints *OR*...
    #         (
    #             hint.__origin__ is tuple and
    #             hint_childs_len == 0
    #         ) or
    #         # A PEP 484-compliant "typing.Tuple"-based hint subscripted
    #         # by exactly one child hint *AND* this child hint is the
    #         # empty tuple,..
    #         (
    #             hint.__origin__ is Tuple and
    #             hint_childs_len == 1 and
    #             hint_childs[0] == ()
    #         )
    #     )
    return (
        hint == HINT_PEP585_TUPLE_EMPTY or
        hint == HINT_PEP484_TUPLE_EMPTY
    )
