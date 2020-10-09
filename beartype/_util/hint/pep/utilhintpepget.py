#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint getter utilities** (i.e., callables querying
arbitrary objects for attributes specific to PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype.roar import BeartypeDecorHintPepException
from beartype._util.cache.utilcachecall import callable_cached
from typing import Generic, TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ dunder                  }....................
def get_hint_pep_args(hint: object) -> tuple:
    '''
    Tuple of all **typing arguments** (i.e., subscripted objects of the passed
    PEP-compliant type hint listed by the caller at hint declaration time)
    if any *or* the empty tuple otherwise.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__args__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Either:

        * If this object defines an ``__args__`` dunder attribute, the value of
          that attribute.
        * Else, the empty tuple.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_args)
        >>> get_hint_pep_args(typing.Any)
        ()
        >>> get_hint_pep_args(typing.List[int, str, typing.Dict[str, str])
        (int, str, typing.Dict[str, str])
    '''

    #FIXME: Consider replacing with this more exacting test:
    #return getattr(hint, '__args__', ())) if is_hint_pep(hint) else ()

    # Return the value of the "__args__" dunder attribute on this object if
    # this object defines this attribute *OR* the empty tuple otherwise.
    return getattr(hint, '__args__', ())


def get_hint_pep_generic_bases(hint: object) -> tuple:
    '''
    Tuple of all **unerased pseudo-superclasses** (i.e., public attributes of
    the :mod:`typing` module originally listed as superclasses of the class of
    the passed PEP-compliant type hint prior to their implicit type erasure by
    that module) if this hint is a **generic** (i.e., PEP-compliant type hint
    whose class subclasses one or more public :mod:`typing`
    pseudo-superclasses) *or* the empty tuple otherwise (i.e., hint whose class
    does *not* subclass one or more public :mod:`typing` pseudo-superclasses).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__orig_bases__`` **dunder attribute.** Most public
    attributes of the :mod:`typing` module fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access that attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    **Tuples returned by this function typically do not contain actual types.**
    Because the :mod:`typing` module lies about literally everything, most
    public attributes of the :mod:`typing` module used as superclasses are
    *not* actually types but singleton objects devilishly masquerading as
    types. Most true :mod:`typing` superclasses are private, fragile, and prone
    to alteration or even removal between major Python versions. Ergo, this
    function is intentionally not named ``get_hint_pep_superclasses``.

    **Tuples returned by this function typically contain objects parametrized
    by type variables** (e.g., ``(typing.Container[T], typing.Sized[T])``).

    Motivation
    ----------
    `PEP 560`_ (i.e., "Core support for typing module and generic types)
    formalizes the ``__orig_bases__`` dunder attribute first informally
    introduced by the :mod:`typing` module's implementation of `PEP 484`_.
    Naturally, `PEP 560`_ remains as unusable as `PEP 484`_ itself. Ideally,
    `PEP 560`_ would have generalized the core intention of preserving each
    original user-specified subclass tuple of superclasses as a full-blown
    ``__orig_mro__`` dunder attribute listing the original method resolution
    order (MRO) of that subclass had that tuple *not* been modified.

    Naturally, `PEP 560`_ did no such thing. The original MRO remains
    obfuscated and effectively inaccessible. While computing that MRO would
    technically be feasible, doing so would also be highly non-trivial,
    expensive, and fragile. Instead, this function retrieves *only* the tuple
    of :mod:`typing`-specific pseudo-superclasses that this object's class
    originally attempted (but failed) to subclass.

    You are probably now agitatedly cogitating to yourself in the darkness:
    "But @leycec: what do you mean `PEP 560`_? Wasn't `PEP 560`_ released
    *after* `PEP 484`_? Surely no public API defined by the Python stdlib would
    be so malicious as to silently alter the tuple of base classes listed by a
    user-defined subclass?"

    As we've established both above and elsewhere throughout the codebase,
    everything developed for `PEP 484` -- including `PEP 560`_, which derives
    its entire raison d'etre from `PEP 484`_ -- are fundamentally insane. In
    this case, `PEP 484`_ is insane by subjecting parametrized :mod:`typing`
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
       reduced to that abstract base class (e.g.,
       ``collections.abc.Iterable``).
     * All surviving base classes that are parametrized (e.g.,
       ``typing.Generic[S, T]``) are stripped of that parametrization (e.g.,
       :class:`typing.Generic`).

     Since there exists no counterpart to the :class:`typing.Generic`
     superclass, the :mod:`typing` module preserves that superclass in
     unparametrized form. Naturally, this is useless, as an unparametrized
     :class:`typing.Generic` superclass conveys no meaningful type annotation.
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

    Ergo, we ignore the useless ``__mro__`` dunder attribute in favour of the
    actually useful ``__orig_bases__`` dunder attribute tuple. Welcome to
    :mod:`typing` hell, where even :mod:`typing` types lie broken and
    misshapen on the killing floor of overzealous theory-crafting purists.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Either:

        * If this object defines an ``__orig_bases__`` dunder attribute, the
          value of that attribute.
        * Else, the empty tuple.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_generic_bases)
        >>> T = typing.TypeVar('T')
        >>> class IterableContainer(typing.Iterable[T], typing.Container[T]):
        ...     pass
        >>> get_hint_pep_generic_bases(typing.Union[str, typing.List[int]])
        ()
        >>> get_hint_pep_typing_superobjects(IterableContainer)
        (typing.Iterable[~T], typing.Container[~T])
        >>> IterableContainer.__mro__
        (__main__.IterableContainer,
         collections.abc.Iterable,
         collections.abc.Container,
         typing.Generic,
         object)

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    .. _PEP 560:
       https://www.python.org/dev/peps/pep-0560
    '''

    #FIXME: This tuple appears to be implemented erroneously -- at least under
    #Python 3.7, anyway. Although this tuple is implemented correctly for the
    #common case of user-defined types directly subclassing "typing" types,
    #this tuple probably is *NOT* implemented correctly for the edge case of
    #user-defined types indirectly subclassing "typing" types: e.g.,
    #
    #    >>> import collections.abc, typing
    #    >>> T = typing.TypeVar('T')
    #    >>> class Direct(collections.abc.Sized, typing.Generic[T]): pass
    #    >>> Direct.__orig_bases__
    #    (collections.abc.Sized, typing.Generic[~T])
    #    >>> class Indirect(collections.abc.Container, Direct): pass
    #    >>> Indirect.__orig_bases__
    #    (collections.abc.Sized, typing.Generic[~T])
    #
    #*THAT'S COMPLETELY INSANE.* Clearly, their naive implementation failed to
    #account for actual real-world use cases.
    #
    #On the bright side, the current implementation prevents us from actually
    #having to perform a breadth-first traversal of all original superclasses
    #of this class in method resolution order (MRO). On the dark side, it's
    #pants-on-fire balls -- but there's not much we can do about that. *sigh*
    #
    #If we ever need to perform that breadth-first traversal, resurrect this:
    #
    #    # If this class was *NOT* subject to type erasure, reduce to a noop.
    #    if not hint_bases:
    #        return hint_bases
    #
    #    # Fixed list of all typing super attributes to be returned.
    #    superattrs = acquire_fixed_list(SIZE_BIG)
    #
    #    # 0-based index of the last item of this list.
    #    superattrs_index = 0
    #
    #    # Fixed list of all transitive superclasses originally listed by this
    #    # class iterated in method resolution order (MRO).
    #    hint_orig_mro = acquire_fixed_list(SIZE_BIG)
    #
    #    # 0-based indices of the current and last items of this list.
    #    hint_orig_mro_index_curr = 0
    #    hint_orig_mro_index_last = 0
    #
    #    # Initialize this list with the tuple of all direct superclasses of this
    #    # class, which iteration then expands to all transitive superclasses.
    #    hint_orig_mro[:len(hint_bases)] = hint_bases
    #
    #    # While the heat death of the universe has been temporarily forestalled...
    #    while (True):
    #        # Currently visited superclass of this class.
    #        hint_base = hint_orig_mro[hint_orig_mro_index_curr]
    #
    #        # If this superclass is a typing attribute...
    #        if is_hint_pep_typing(hint_base):
    #            # Avoid inserting this attribute into the "hint_orig_mro" list.
    #            # Most typing attributes are *NOT* actual classes and those that
    #            # are have no meaningful public superclass. Ergo, iteration
    #            # terminates with typing attributes.
    #            #
    #            # Insert this attribute at the current item of this list.
    #            superattrs[superattrs_index] = hint_base
    #
    #            # Increment this index to the next item of this list.
    #            superattrs_index += 1
    #
    #            # If this class subclasses more than the maximum number of "typing"
    #            # attributes supported by this function, raise an exception.
    #            if superattrs_index >= SIZE_BIG:
    #                raise BeartypeDecorHintPep560Exception(
    #                    '{} PEP type {!r} subclasses more than '
    #                    '{} "typing" types.'.format(
    #                        hint_label,
    #                        hint,
    #                        SIZE_BIG))
    #        # Else, this superclass is *NOT* a typing attribute. In this case...
    #        else:
    #            # Tuple of all direct superclasses originally listed by this class
    #            # prior to PEP 484 type erasure if any *OR* the empty tuple
    #            # otherwise.
    #            hint_base_bases = getattr(hint_base, '__orig_bases__')
    #
    #            #FIXME: Implement breadth-first traversal here.
    #
    #    # Tuple sliced from the prefix of this list assigned to above.
    #    superattrs_tuple = tuple(superattrs[:superattrs_index])
    #
    #    # Release and nullify this list *AFTER* defining this tuple.
    #    release_fixed_list(superattrs)
    #    del superattrs
    #
    #    # Return this tuple as is.
    #    return superattrs_tuple
    #
    #Also resurrect this docstring snippet:
    #
    #    Raises
    #    ----------
    #    BeartypeDecorHintPep560Exception
    #        If this object defines the ``__orig_bases__`` dunder attribute but that
    #        attribute transitively lists :data:`SIZE_BIG` or more :mod:`typing`
    #        attributes.
    #
    #Specifically:
    #  * Acquire a fixed list of sufficient size (e.g., 64). We probably want
    #    to make this a constant in "utilcachelistfixedpool" for reuse
    #    everywhere, as this is clearly becoming a common idiom.
    #  * Slice-assign "__orig_bases__" into this list.
    #  * Maintain two simple 0-based indices into this list:
    #    * "bases_index_curr", the current base being visited.
    #    * "bases_index_last", the end of this list also serving as the list
    #      position to insert newly discovered bases at.
    #  * Iterate over this list and keep slice-assigning from either
    #    "__orig_bases__" (if defined) or "__mro__" (otherwise) into
    #    "list[bases_index_last:len(__orig_bases__)]". Note that this has the
    #    unfortunate disadvantage of temporarily iterating over duplicates,
    #    but... *WHO CARES.* It still works and we subsequently
    #    eliminate duplicates at the end.
    #  * Return a frozenset of this list, thus implicitly eliminating
    #    duplicate superclasses.

    # Return the value of the "__orig_bases__" dunder attribute on this object
    # if this object defines this attribute *OR* the empty tuple otherwise.
    return getattr(hint, '__orig_bases__', ())


def get_hint_pep_typevars(hint: object) -> tuple:
    '''
    Tuple of all **unique type variables** (i.e., subscripted :class:`TypeVar`
    instances of the passed PEP-compliant type hint listed by the caller at
    hint declaration time ignoring duplicates) if any *or* the empty tuple
    otherwise.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__parameters__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Either:

        * If this object defines a ``__parameters__`` dunder attribute, the
          value of that attribute.
        * Else, the empty tuple.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_typevars)
        >>> S = typing.TypeVar('S')
        >>> T = typing.TypeVar('T')
        >>> get_hint_pep_typevars(typing.Any)
        ()
        >>> get_hint_pep_typevars(typing.List[T, int, S, str, T)
        (T, S)
    '''

    #FIXME: After dropping Python 3.6, drop the trailing "or ()". See below.
    #FIXME: Consider replacing with this more exacting test:
    #return getattr(hint, '__parameters__', ())) if is_hint_pep(hint) else ()

    # Value of the "__parameters__" dunder attribute on this object if this
    # object defines this attribute *OR* the empty tuple otherwise. Note that:
    #
    # * The "typing._GenericAlias.__parameters__" dunder attribute tested here
    #   is defined by the typing._collect_type_vars() function at subscription
    #   time. Yes, this is insane. Yes, this is PEP 484.
    # * This trivial test implicitly handles superclass parametrizations.
    #   Thankfully, the "typing" module percolates the "__parameters__" dunder
    #   attribute from "typing" pseudo-superclasses to user-defined subclasses
    #   during PEP 560-style type erasure. Finally: they did something right.
    # * The trailing "or ()" test is required to handle edge cases under the
    #   Python < 3.7.0 implementation of the "typing" module. Notably, under
    #   Python 3.6.11:
    #       >>> import typing as t
    #       >>> t.Union.__parameters__   # yes, this is total bullocks
    #       None
    return getattr(hint, '__parameters__', ()) or ()

# ....................{ GETTERS ~ attrs                   }....................
#FIXME: Does this getter *REALLY* need to detect type variables? We suspect the
#answer is "almost certainly not", as type variable detection should ideally
#occur outside the standard argumentless typing attribute logic path. Consider
#dropping the internal detection this getter performs for type variables.

@callable_cached
def get_hint_pep_typing_attr(hint: object) -> dict:
    '''
    **Argumentless** :mod:`typing` **attribute** (i.e., public attribute of the
    :mod:`typing` module uniquely identifying the passed PEP-compliant type
    hint, stripped of all subscripted arguments but *not* default type
    variables) identifying this hint if this hint is PEP-compliant *or* raise
    an exception otherwise (i.e., if this hint is *not* PEP-compliant).

    This getter function associates the passed hint with a public attribute of
    the :mod:`typing` module effectively acting as a superclass of this hint
    and thus uniquely identifying the "type" of this hint in the broadest sense
    of the term "type". These attributes are typically *not* actual types, as
    most actual :mod:`typing` types are private, fragile, and prone to extreme
    violation (or even removal) between major Python versions. Nonetheless,
    these attributes are sufficiently unique to enable callers to distinguish
    between numerous broad categories of :mod:`typing` behaviour and logic.

    Specifically, this function returns either:

    * If this hint is a **generic** (i.e., instance of the
      :class:`typing.Generic` abstract base class (ABC)),
      :class:`typing.Generic`.
    * Else if this hint is a **type variable** (i.e., instance of the concrete
      :class:`typing.TypeVar` class), :class:`typing.TypeVar`.
    * Else if this hint is **optional** (i.e., subscription of the
      :attr:`typing.Optional` attribute), :attr:`typing.Union`. The
      :mod:`typing` module implicitly reduces *all* subscriptions of the
      :attr:`typing.Optional` singleton by the corresponding
      :attr:`typing.Union` singleton subscripted by both that argument and
      ``type(None)``. Ergo, there effectively exists *no*
      :attr:`typing.Optional` attribute with respect to categorization.
    * Else, the argumentless :mod:`typing` attribute dynamically retrieved by
      inspecting this hint's **object representation** (i.e., the
      non-human-readable string returned by the :func:`repr` builtin).

    This getter function is memoized for efficiency.

    Motivation
    ----------
    Both `PEP 484`_ and the :mod:`typing` module implementing `PEP 484`_ are
    functionally deficient with respect to their public APIs. Neither provide
    external callers any means of deciding the categories of arbitrary
    PEP-compliant type hints. For example, there exists no general-purpose
    means of identifying a parametrized subtype (e.g., ``typing.List[int]``) as
    a parametrization of its unparameterized base type (e.g., ``type.List``).
    Thus this function, which "fills in the gaps" by implementing this
    oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    dict
        Argumentless** :mod:`typing` attribute uniquely identifying this hint.

    Raises
    ----------
    AttributeError
        If this object's representation is prefixed by the substring
        ``"typing."``, but the remainder of that representation up to but *not*
        including the first "[" character in that representation (e.g.,
        ``"Dict"`` for the object ``typing.Dict[str, Tuple[int, ...]]``) is
        *not* an attribute of the :mod:`typing` module.
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_typing_attr)
        >>> get_hint_pep_typing_attr(typing.Any)
        typing.Any
        >>> get_hint_pep_typing_attr(typing.Union[str, typing.Sequence[int]])
        typing.Union
        >>> T = typing.TypeVar('T')
        >>> get_hint_pep_typing_attr(T)
        typing.TypeVar
        >>> class Genericity(typing.Generic[T]): pass
        >>> get_hint_pep_typing_attr(Genericity)
        typing.Generic
        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
        >>> get_hint_pep_typing_attr(Duplicity)
        typing.Iterable

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpeptest import (
        die_unless_hint_pep,
        is_hint_pep_generic_user,
        is_hint_pep_typevar,
    )

    # If this hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(hint)
    # Else, this hint is PEP-compliant.

    # If this hint is a generic (i.e., user-defined class subclassing one or
    # more "typing" pseudo-superclasses), return the "typing.Generic" abstract
    # base class (ABC). this ABC, uniquely identifying *ALL* generics.
    #
    # Note that the "typing" module guarantees *ALL* generics to subclass this
    # ABC regardless of whether those generics originally did so explicitly.
    # How? By type erasure, of course, the malicious gift that keeps on giving:
    #     >>> import typing as t
    #     >>> class MuhList(t.List): pass
    #     >>> MuhList.__orig_bases__
    #     (typing.List)
    #     >>> MuhList.__mro__
    #     (__main__.MuhList, list, typing.Generic, object)
    #
    # Ergo, this ABC uniquely identifies *ALL* generics and thus serves as a
    # sufficient and complete argumentless "typing" attribute.
    #
    # Note that generics *CANNOT* be detected by the general-purpose logic
    # performed below, as the "typing.Generic" ABC does *NOT* define a
    # __repr__() dunder method returning a string prefixed by "typing.".
    if is_hint_pep_generic_user(hint):
        return Generic
    # Else, this hint is PEP-compliant but *NOT* a generic.
    #
    # Else if this hint is a type variable, return a dictionary constant
    # mapping from the common type of all such variables.
    #
    # Note that type variables *CANNOT* be detected by the general-purpose
    # logic performed below, as the TypeVar.__repr__() dunder method insanely
    # returns a string prefixed by the non-human-readable character "~" rather
    # than the module name "typing." -- unlike most "typing" objects:
    #      >>> import typing as t
    #      >>> repr(t.TypeVar('T'))
    #      ~T
    #
    # Of course, that brazenly violates Pythonic standards. __repr__() is
    # generally assumed to return an evaluatable Python expression that, when
    # evaluated, instantiates an object equal to the original object. Instead,
    # this API was designed by incorrigible monkeys who profoundly hate the
    # Python language. This is why we can't have sane things.
    #
    # Ergo, type variables require special-purpose handling and *CANNOT* be
    # handled by the general-purpose detection implemented below.
    elif is_hint_pep_typevar(hint):
        return TypeVar
    # Else, this hint is PEP-compliant but neither a generic nor type variable.

    # Machine-readable string representation of this hint also serving as the
    # fully-qualified name of the public "typing" attribute uniquely associated
    # with this hint (e.g., "typing.Tuple[str, ...]").
    #
    # Although the "typing" module provides *NO* sane public API, it does
    # reliably implement the __repr__() dunder method across most objects and
    # types to return a string prefixed "typing." regardless of Python version.
    # Ergo, this string is effectively the *ONLY* sane means of deciding which
    # broad category of behaviour an arbitrary PEP 484 type hint conforms to.
    typing_attr_name = repr(hint)

    # If this representation is *NOT* prefixed by "typing.", this hint does
    # *NOT* originate from the "typing" module and is thus *NOT* PEP-compliant.
    # But by the above validation, this hint is PEP-compliant. Since this
    # invokes a world-shattering paradox, raise an exception.
    if not typing_attr_name.startswith('typing.'):
        raise BeartypeDecorHintPepException(
            'PEP-compliant type hint {!r} '
            'representation "{}" not prefixed by "typing.".'.format(
                hint, typing_attr_name))

    # Strip the now-harmful "typing." prefix from this representation.
    # Preserving this prefix would raise an "AttributeError" exception from
    # the subsequent call to the getattr() builtin.
    typing_attr_name = typing_attr_name[7:]  # hardcode us up the bomb

    # 0-based index of the first "[" delimiter in this representation if
    # any *OR* -1 otherwise.
    typing_attr_name_bracket_index = typing_attr_name.find('[')

    # If this representation contains such a delimiter, this is a parametrized
    # type hint. In this case, reduce this representation to its unparametrized
    # form by truncating the suffixing parametrization from this representation
    # (e.g., from "typing.Union[str, typing.Sequence[int]]" to merely
    # "typing.Union").
    #
    # Note that this is the common case and thus explicitly tested first.
    if typing_attr_name_bracket_index > 0:
        typing_attr_name = typing_attr_name[
            :typing_attr_name_bracket_index]
    # Else, this representation contains no such delimiter and is thus already
    # unparametrized. In this case, preserve this representation as is.

    # Return the "typing" attribute with this name if any *OR* implicitly raise
    # an "AttributeError" exception. This is an unlikely edge case that will
    # probably only occur with intentionally malicious callers whose objects
    # override their __repr__() dunder methods to return strings prefixed by
    # "typing.". Ergo, we avoid performing any deeper validation here.
    return getattr(typing, typing_attr_name)
