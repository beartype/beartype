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
from beartype.roar import (
    BeartypeDecorHintValuePepException,
    BeartypeDecorHintValuePep560Exception,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cache.list.utillistfixedpool import (
    SIZE_BIG, acquire_fixed_list, release_fixed_list)
from beartype._util.utilobj import (
    SENTINEL, get_object_type)
from typing import TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_TYPING_ATTRS_TYPEVAR = (TypeVar,)
'''
Tuple containing only the :class:`TypeVar` class.

The memoized :func:`get_hint_typing_attrs_untypevared_or_none` function returns
and thus internally caches this tuple when passed a type variable. To reduce
space consumption, this tuple is efficiently reused rather than inefficiently
recreated for each recall to that function passed a type variable.
'''

# ....................{ GETTERS ~ attrs                   }....................
#FIXME: To be genuinely useful during our breadth-first traversal of
#PEP-compliant type hints, this getter should probably be mildly refactored to
#return a dictionary mapping from each typing attribute to the original
#parametrized "typing" superclass associated with that attribute if the type
#hint is a user-defined subclass of one or more "typing" superclasses: e.g.,
#
#        >>> import typing
#        >>> from beartype._util.hint.pep.utilhintpeptest import get_hint_typing_attrs_untypevared_or_none
#        >>> T = typing.TypeVar('T')
#        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
#        # This is what this function currently returns.
#        >>> get_hint_typing_attrs_untypevared_or_none(Duplicity)
#        (typing.Iterable, typing.Container)
#        # This is what this function should return instead.
#        >>> get_hint_typing_attrs_untypevared_or_none(Duplicity)
#        {typing.Iterable: typing.Iterable[T],
#         typing.Container: typing.Container[T]}
#
#The latter is strongly preferable, as it preserves essential metadata required
#for code generation during breadth-first traversals.
#FIXME: Actually, we probably want to also refactor this getter to return a
#2-dictionary "{hint_typing_attr: hint}" when passed a user-defined class
#subclassing exactly one "typing" superclass: e.g.,
#
#        >>> import collections.abc, typing
#        >>> from beartype._util.hint.pep.utilhintpeptest import get_hint_typing_attrs_untypevared_or_none
#        >>> T = typing.TypeVar('T')
#        >>> class Genericity(collections.abc.Sized, typing.Generic[T]): pass
#        # This is what this function currently returns.
#        >>> get_hint_typing_attrs_untypevared_or_none(Genericity)
#        typing.Generic
#        # This is what this function should return instead.
#        >>> get_hint_typing_attrs_untypevared_or_none(Duplicity)
#        {typing.Generic: typing.Generic[T]}
#FIXME: Actually, rather than heavily refactor this function, we probably just
#want to copy-and-paste this function's implementation modified to suite the
#specific needs of our breadth-first traversal. Maybe. This function's current
#implementation is suitable for other needs (e.g.,
#die_unless_hint_pep_supported()) and should thus probably be preserved as is.

#FIXME: Refactor all callers to unconditionally expect a tuple.
@callable_cached
def get_hint_typing_attrs_untypevared_or_none(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotation',
) -> 'NoneTypeOr[object]':
    '''
    **Untypevared typing attribute(s)** (i.e., public attribute(s) of the
    :mod:`typing` module uniquely identifying the passed PEP-compliant type
    hint defined via the :mod:`typing` module but stripped of all type variable
    parametrization) associated with this class or object if any *or* ``None``
    otherwise.

    This getter function associates arbitrary PEP-compliant classes and objects
    with corresponding public attributes of the :mod:`typing` module, which
    effectively serve as unique pseudo-superclasses of those classes and
    objects. These attributes are typically *not* superclasses, as most actual
    :mod:`typing` superclasses are private, fragile, and prone to extreme
    alteration or even removal between major Python versions. Nonetheless,
    these attributes are sufficiently unique to enable callers to distinguish
    between numerous broad categories of :mod:`typing` behaviour and logic.

    This getter function is memoized for efficiency.

    Motivation
    ----------
    Both `PEP 484`_ and the :mod:`typing` module implementing `PEP 484`_ are
    functionally deficient with respect to their public APIs. Neither provide
    external callers any means of deciding the types of arbitrary `PEP
    484`_-compliant classes or objects. For example, there exists no standard
    means of identifying the parametrized subtype ``typing.List[int]`` as a
    parametrization of the unparameterized base type ``type.List``.

    Thus this function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    hint_label : Optional[str]
        Human-readable noun prefixing this object's representation in the
        exception message raised by this function. Defaults to 'Annotation'.

    Returns
    ----------
    NoneTypeOr[object]
        Either:

        * If this object is uniquely identified by:

          * One public attribute of the :mod:`typing` module, that attribute.
          * One or more public attributes of the :mod:`typing` module, a tuple
            listing these attributes in the same order (e.g., superclass order
            for user-defined types).

        * Else, ``None``.

    Raises
    ----------
    BeartypeDecorHintValuePep560Exception
        If this object is PEP-compliant but this function erroneously fails to
        decide the :mod:`typing` attributes associated with this object due to
        this object being a user-defined class subclassing one or more
        :mod:`typing` superclasses that either:

        * Fails to define the PEP-specific ``__orig_bases__`` dunder attribute.
        * Defines that attribute but that attribute describes either:

          * No :mod:`typing` attributes.
          * :data:`SIZE_BIG` or more :mod:`typing` attributes.

    Examples
    ----------

        >>> import typing
        >>> from beartype.cave import AnyType
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_typing_attrs_untypevared_or_none)
        >>> get_hint_typing_attrs_untypevared_or_none(AnyType)
        None
        >>> get_hint_typing_attrs_untypevared_or_none(typing.Any)
        (typing.Any,)
        >>> get_hint_typing_attrs_untypevared_or_none(typing.Union[str, typing.Sequence[int]])
        (typing.Union,)
        >>> get_hint_typing_attrs_untypevared_or_none(typing.Sequence[int])
        (typing.Sequence,)
        >>> T = typing.TypeVar('T')
        >>> get_hint_typing_attrs_untypevared_or_none(T)
        (typing.TypeVar,)
        >>> class Genericity(typing.Generic[T]): pass
        >>> get_hint_typing_attrs_untypevared_or_none(Genericity)
        (typing.Generic,)
        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
        >>> get_hint_typing_attrs_untypevared_or_none(Duplicity)
        (typing.Iterable, typing.Container)

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''
    assert isinstance(hint_label, str), (
        '{!r} not a string.'.format(hint_label))

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep

    # If this hint is *NOT* PEP-compliant, return "None".
    if not is_hint_pep(hint):
        return None
    # Else, this hint is PEP-compliant.

    # If this hint is a type variable, return a tuple containing only the type
    # of all such variables. Note that:
    #
    # * This condition is tested for first due to the efficiency of this test
    #   rather than due to an expectation of type variables being more common
    #   than other PEP 484 objects and types.
    # * Unlike most PEP 484 objects and types, the TypeVar.__repr__() dunder
    #   method insanely returns a string prefixed by "~" rather than "typing.".
    #   Notably:
    #      >>> from typing import TypeVar
    #      >>> repr(TypeVar('T'))
    #      ~T
    #   Of course, that brazenly violates Pythonic standards. __repr__() is
    #   generally assumed to return an evaluatable Python expression that,
    #   when evaluated, creates an object equal to the original object.
    #   Instead, this API was designed by incorrigible monkeys who profoundly
    #   hate the Python language. This is why we can't have sane things.
    if isinstance(hint, TypeVar):
        return _TYPING_ATTRS_TYPEVAR
    # Else, this hint is *NOT* a type variable.

    # Direct typing attribute associated with this hint if this hint is
    # directly defined by the "typing" module *OR* "None" otherwise.
    hint_direct_typing_attr = get_hint_direct_typing_attr_untypevared_or_none(
        hint)

    # If this attribute exists, return a tuple containing only this attribute.
    if hint_direct_typing_attr:
        return (hint_direct_typing_attr,)
    # Else, no such attribute exists. In this case, this hint is *NOT* directly
    # declared by the "typing" module. Since this hint is PEP-compliant, this
    # hint *MUST* necessarily be a user-defined class subclassing one or more
    # "typing" superclasses: e.g.,
    #
    #    # In a user-defined module...
    #    from typing import TypeVar, Generic
    #    T = TypeVar('T')
    #    class UserDefinedGeneric(Generic[T]): pass

    #FIXME: Stop doing this, please.
    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    hint_type = get_object_type(hint)

    # Original superclasses of this class before the "typing" module
    # destructively erased these superclasses if this class declares the
    # "typing"-specific "__orig_bases__" dunder attribute preserving these
    # original superclasses *OR* the sentinel placeholder otherwise.
    #
    # You are probably now agitatedly cogitating to yourself in the darkness:
    # "But @leycec: what do you mean 'destructively erased'? Surely no public
    # API defined by the Python stdlib would be so malicious as to silently
    # modify the tuple of base classes listed by a user-defined subclass?"
    #
    # Let me tell you what now. As we've established both above and elsewhere
    # throughout this codebase, PEP 484 and friends are fundamentally insane.
    # In this case, PEP 484 is insane by subjecting parametrized "typing" types
    # employed as base classes to "type erasure," because "it is common
    # practice in languages with generics (e.g. Java, TypeScript)." Since Java
    # and TypeScript are both terrible languages, blindly recapitulating bad
    # mistakes baked into those languages is an equally bad mistake. In this
    # case, "type erasure" means that the "typing" module intentionally
    # destroys runtime type information for nebulous and largely unjustifiable
    # reasons (i.e., Big Daddy Java and TypeScript do it, so it must be
    # unquestionably good).
    #
    # Specifically, the "typing" module intentionally munges all "typing" types
    # used as base classes in user-defined subclasses as follows:
    #
    # * All base classes whose origin is a builtin container (e.g.,
    #   "typing.List[T]") are reduced to that container (e.g., "list").
    # * All base classes derived from an abstract base class declared by the
    #   "collections.abc" subpackage (e.g., "typing.Iterable[T]") are reduced
    #   to that abstract base class (e.g., "collections.abc.Iterable").
    # * All surviving base classes that are parametrized (e.g.,
    #   "typing.Generic[S, T]") are stripped of that parametrization (e.g.,
    #   "typing.Generic").
    #
    # Since there exists no counterpart to the "typing.Generic" superclass,
    # the "typing" module preserves that superclass in unparametrized form.
    # All other superclasses are reduced to non-"typing" counterparts.
    #
    # The standard "__mro__" dunder attribute of user-defined subclasses with
    # one or more "typing" superclasses reflects this erasure, while thankfully
    # preserving the original tuple of user-defined superclasses for those
    # subclasses in a "typing"-specific "__orig_bases__" dunder attribute:
    # e.g.,
    #
    #     # This is type erasure.
    #     >>> UserDefinedGeneric.__mro__
    #     (list, collections.abc.Iterable, Generic)
    #     # This is type preservation.
    #     >>> UserDefinedGeneric.__orig_bases__
    #     (List[T], Iterable[T], Generic[T])
    #     # Guess which we prefer?
    #
    # Ergo, we ignore the useless standard "__mro__" tuple in favour of the
    # actually useful (albeit non-standard) "__orig_bases__" tuple.
    #
    # Welcome to "typing" hell, where even "typing" types lie broken and
    # misshapen on the killing floor of overzealous theorists.

    #FIXME: Sadly, this is optimistically naive. O.K., it's just broken. The
    #"__orig_bases__" dunder attribute doesn't actually compute the original
    #MRO; it just preserves the original bases as directly listed in this
    #subclass declaration. What we need, however, is the actual original MRO as
    #that subclass *WOULD* have had had "typing" not subjected it to malignant
    #type erasure. That's... non-trivial but feasible to compute, so let's do
    #that. Specifically, let's:
    #
    #* Define a new "beartype._util.pep.utilpep560" submodule:
    #  * Define a new get_superclasses_original() function with signature:
    #    @callablecached
    #    def get_superclasses_original(obj: object) -> frozenset
    #    This function intentionally does *NOT* bother returning a proper MRO.
    #    While we certainly could do so (e.g., by recursively replacing in the
    #    "__mro__" of this object all bases modified via type erasure with
    #    those listed in the "__orig_bases__" attribute of each superclass),
    #    doing so would both be highly non-trivial and overkill. All we really
    #    require is the set of all original superclasses of this class. Since
    #    PEP 560 is (of course) awful, it provides no API for obtaining any of
    #    this. Fortunately, this shouldn't be *TERRIBLY* hard. We just need to
    #    implement (wait for it) a breadth-first traversal using fixed lists.
    #    This might resemble:
    #    * If the type of the passed object does *NOT* have the
    #      "__orig_bases__" attribute defined, just:
    #      return frozenset(obj.__mro__)
    #    * Else:
    #      * Acquire a fixed list of sufficient size (e.g., 64). We probably
    #        want to make this a constant in "utilcachelistfixedpool" for reuse
    #        everywhere, as this is clearly becoming a common idiom.
    #      * Slice-assign "__orig_bases__" into this list.
    #      * Maintain two simple 0-based indices into this list:
    #        * "bases_index_curr", the current base being visited.
    #        * "bases_index_last", the end of this list also serving as the
    #          list position to insert newly discovered bases at.
    #      * Iterate over this list and keep slice-assigning from either
    #        "__orig_bases__" (if defined) or "__mro__" (otherwise) into
    #        "list[bases_index_last:len(__orig_bases__)]". Note that this has
    #        the unfortunate disadvantage of temporarily iterating over
    #        duplicates, but... *WHO CARES.* It still works and we subsequently
    #        eliminate duplicates at the end.
    #      * Return a frozenset of this list, thus implicitly eliminating
    #        duplicate superclasses.
    #FIXME: Actually, all we require here and above is a
    #get_hint_typing_supertypes() function. That's certainly related to the
    #algorithm defined above, except that we don't care above "__mro__"; we
    #only care about "__orig_bases__" and we need to explicitly weed out
    #non-"typing" supertypes given the algorithm defined below. So, we'll
    #initially just need an amalgam of the algorithms defined above and below.
    #Consider defining a new:
    #* "utilhintpeptest" submodule containing only testers.
    #* "utilhintpepget" submodule containing only getters.
    #Maintainability is paramount here, folks.
    hint_supertypes = getattr(hint_type, '__orig_bases__', SENTINEL)

    # If this user-defined subclass subclassing one or more "typing"
    # superclasses failed to preserve the original tuple of these superclasses
    # against type erasure, something has gone wrong. Raise us an exception!
    if hint_supertypes is SENTINEL:
        raise BeartypeDecorHintValuePepException(
            '{} PEP type {!r} subclasses no "typing" types.'.format(
                hint_label, hint))
    # Else, this subclass preserved this tuple against type erasure.

    # If this user-defined subclass subclassing more than the maximum number of
    # "typing" superclasses supported by this function, raise an exception.
    # This function internally reuses fixed lists of this size to efficiently
    # iterate these superclasses.
    if len(hint_supertypes) > SIZE_BIG:
        raise BeartypeDecorHintValuePepException(
            '{} PEP type {!r} subclasses more than {} "typing" types.'.format(
                hint_label,
                hint,
                SIZE_BIG))
    # Else, this user-defined subclass subclassing less than or equal to this
    # maximum number of "typing" superclasses supported by this function.

    # Fixed list of all typing attributes associated with this subclass.
    hint_typing_attrs = acquire_fixed_list(SIZE_BIG)

    # 0-based index of the current item of this list to insert the next typing
    # attribute discovered by iteration below at.
    hint_typing_attrs_index = 0

    # For each original superclass of this class...
    for hint_supertype in hint_supertypes:
        # Direct typing attribute associated with this superclass if any *OR*
        # "None" otherwise.
        hint_typing_attr = get_hint_direct_typing_attr_untypevared_or_none(hint_supertype)
        # print('hint supertype: {!r} -> {!r}'.format(hint_supertype, hint_direct_typing_attr))

        # If this attribute exists...
        if hint_typing_attr:
            # Insert this attribute at the current item of this list.
            hint_typing_attrs[hint_typing_attrs_index] = hint_typing_attr

            # Increment this index to the next item of this list.
            hint_typing_attrs_index += 1
        # Else, no such attribute exists.

    # Tuple sliced from the prefix of this list assigned to above.
    hint_typing_attrs_tuple = tuple(
        hint_typing_attrs[:hint_typing_attrs_index])

    # Release and nullify this list *AFTER* defining this tuple.
    release_fixed_list(hint_typing_attrs)
    del hint_typing_attrs

    # If this tuple is empty, raise an exception. By the above constraints,
    # this tuple should contain one or more typing attributes.
    if hint_typing_attrs_index == 0:
        raise BeartypeDecorHintValuePepException(
            '{} PEP type {!r} unassociated with "typing" types.'.format(
                hint_label, hint))
    # Else, this tuple is non-empty.

    # Else, this tuple contains ore or more typing attributes. In this case,
    # return this tuple as is.
    return hint_typing_attrs_tuple

# ....................{ GETTERS ~ attrs : direct          }....................
def get_hint_direct_typing_attr_untypevared_or_none(
    hint: object) -> 'NoneTypeOr[object]':
    '''
    **Untypevared direct typing attribute** (i.e., public attribute of the :mod:`typing`
    module directly identifying the passed `PEP 484`_-compliant class or object
    defined via the :mod:`typing` module *without* regard to any superclasses
    of this class or this object's class, stripped of all type variable
    parametrization) associated with this class or object if any *or* ``None``
    otherwise.

    This getter function is *only* intended to be called by the parent
    :func:`_get_hint_typing_attr_or_none` function.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    NoneTypeOr[object]
        Either:

        * If this object is directly identified by a public attribute of the
          :mod:`typing` module, that attribute.
        * Else, ``None``.
    '''

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

    # If this representation is prefixed by "typing.", this is a class or
    # object declared by the "typing" module. In this case...
    if typing_attr_name.startswith('typing.'):
        # Strip the now-harmful "typing." prefix from this representation.
        # Preserving this prefix would raise an "AttributeError" exception from
        # the subsequent call to the getattr() builtin.
        typing_attr_name = typing_attr_name[7:]  # hardcode us up the bomb

        # 0-based index of the first "[" delimiter in this representation if
        # any *OR* -1 otherwise.
        typing_attr_name_bracket_index = typing_attr_name.find('[')

        # If this representation contains such a delimiter, this is a
        # parametrized type hint. In this case, reduce this representation to
        # its unparametrized form by truncating the suffixing parametrization
        # from this representation (e.g., from
        # "typing.Union[str, typing.Sequence[int]]" to merely "typing.Union").
        #
        # Note that this is the common case and thus explicitly tested first.
        if typing_attr_name_bracket_index > 0:
            typing_attr_name = typing_attr_name[
                :typing_attr_name_bracket_index]
        # Else, this representation contains no such a delimiter and is thus
        # already unparametrized as desired. In this case, preserve this
        # representation as is.

        # Return the "typing" attribute with this name if any *OR* implicitly
        # raise an "AttributeError" exception. Since this is an unlikely edge
        # case, we avoid performing any deeper validation here.
        return getattr(typing, typing_attr_name)
    # Else, this hint is *NOT* a class or object declared by the "typing"
    # module.

    # Ergo, this hint is unassociated with a public "typing" attribute.
    return None

# ....................{ GETTERS ~ super                   }....................
#FIXME: Sadly, this is optimistically naive. O.K., it's just broken. The
#"__orig_bases__" dunder attribute doesn't actually compute the original
#MRO; it just preserves the original bases as directly listed in this
#subclass declaration. What we need, however, is the actual original MRO as
#that subclass *WOULD* have had had "typing" not subjected it to malignant
#type erasure. That's... non-trivial but feasible to compute, so let's do
#that. Specifically, let's:
#
#* Define a new "beartype._util.pep.utilpep560" submodule:
#  * Define a new get_superclasses_original() function with signature:
#    @callablecached
#    def get_superclasses_original(obj: object) -> frozenset
#    This function intentionally does *NOT* bother returning a proper MRO.
#    While we certainly could do so (e.g., by recursively replacing in the
#    "__mro__" of this object all bases modified via type erasure with
#    those listed in the "__orig_bases__" attribute of each superclass),
#    doing so would both be highly non-trivial and overkill. All we really
#    require is the set of all original superclasses of this class. Since
#    PEP 560 is (of course) awful, it provides no API for obtaining any of
#    this. Fortunately, this shouldn't be *TERRIBLY* hard. We just need to
#    implement (wait for it) a breadth-first traversal using fixed lists.
#    This might resemble:
#    * If the type of the passed object does *NOT* have the
#      "__orig_bases__" attribute defined, just:
#      return frozenset(obj.__mro__)
#    * Else:
#      * Acquire a fixed list of sufficient size (e.g., 64). We probably
#        want to make this a constant in "utilcachelistfixedpool" for reuse
#        everywhere, as this is clearly becoming a common idiom.
#      * Slice-assign "__orig_bases__" into this list.
#      * Maintain two simple 0-based indices into this list:
#        * "bases_index_curr", the current base being visited.
#        * "bases_index_last", the end of this list also serving as the
#          list position to insert newly discovered bases at.
#      * Iterate over this list and keep slice-assigning from either
#        "__orig_bases__" (if defined) or "__mro__" (otherwise) into
#        "list[bases_index_last:len(__orig_bases__)]". Note that this has
#        the unfortunate disadvantage of temporarily iterating over
#        duplicates, but... *WHO CARES.* It still works and we subsequently
#        eliminate duplicates at the end.
#      * Return a frozenset of this list, thus implicitly eliminating
#        duplicate superclasses.
#FIXME: Actually, all we require here and above is a
#get_hint_typing_supertypes() function. That's certainly related to the
#algorithm defined above, except that we don't care above "__mro__"; we
#only care about "__orig_bases__" and we need to explicitly weed out
#non-"typing" supertypes given the algorithm defined below. So, we'll
#initially just need an amalgam of the algorithms defined above and below.
#Consider defining a new:
#* "utilhintpeptest" submodule containing only testers.
#* "utilhintpepget" submodule containing only getters.
#Maintainability is paramount here, folks.

#FIXME: Call above and elsewhere.
#FIXME: Unit test us up.
@callable_cached
def get_hint_typing_super_attrs(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotation',
) -> tuple:
    '''
    Tuple of all **:mod:`typing` super attributes** (i.e., public attributes of
    the :mod:`typing` module originally listed as superclasses of the class of
    the passed object) of this object if any *or* the empty tuple otherwise
    (i.e., if that type listed *no* such superclasses).

    This getter function is memoized for efficiency.

    Motivation
    ----------
    `PEP 560`_ (i.e., "Core support for typing module and generic types)
    formalizes the ``__orig_bases__`` dunder attribute first informally
    introduced by the :mod:`typing` module's ad-hoc implementation of `PEP
    484`_. Tragically, `PEP 560`_ remains as unusable as `PEP 484`_. Ideally,
    `PEP 560`_ would have generalized the core intention of preserving each
    original user-specified subclass tuple of superclasses as a full-blown
    ``__orig_mro__`` dunder attribute listing the original method resolution
    order (MRO) of that subclass had that tuple *not* been modified.

    Naturally, `PEP 560`_ did no such thing. The original MRO remains
    obfuscated and effectively inaccessible. While computing that MRO would
    technically be feasible, doing so would also be highly non-trivial,
    expensive, and fragile.

    Thus this function, which "fills in the gaps" by implementing this
    laughably critical oversight with a comparable function retrieving *only*
    the tuple of original :mod:`typing`-specific superclasses of this object.

    Caveats
    -------
    **Tuples returned by this function typically do not contain actual types.**
    Because the :mod:`typing` module lies about literally everything, most
    public attributes of the :mod:`typing` module used as superclasses are
    *not* actually types but singleton objects devilishly masquerading as
    types. Most true :mod:`typing` superclasses are private, fragile, and prone
    to alteration or even removal between major Python versions. Ergo, this
    function is intentionally not named ``get_hint_typing_superclasses`` or
    ``get_hint_typing_bases``.

    **Tuples returned by this function may contain types parametrized by one or
    more type variables** (e.g., ``(typing.Container[T], typing.Sized[T])``).

    Parameters
    ----------
    hint : object
        Object to be inspected.
    hint_label : Optional[str]
        Human-readable noun prefixing this object's representation in the
        exception message raised by this function. Defaults to 'Annotation'.

    Returns
    ----------
    tuple
        Tuple of all :mod:`typing` superclasses of this object.

    Raises
    ----------
    BeartypeDecorHintValuePep560Exception
        If this object defines the ``__orig_bases__`` dunder attribute but that
        attribute transitively lists :data:`SIZE_BIG` or more :mod:`typing`
        attributes.

    Examples
    ----------

        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_typing_bases)
        >>> T = typing.TypeVar('T')
        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
        >>> get_hint_typing_bases(typing.Union[str, typing.Sequence[int]])
        ()
        >>> get_hint_typing_bases(Duplicity)
        (typing.Iterable[~T], typing.Container[~T])

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    .. _PEP 560:
       https://www.python.org/dev/peps/pep-0560
    '''
    assert isinstance(hint_label, str), (
        '{!r} not a string.'.format(hint_label))

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_typing

    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    hint_type = get_object_type(hint)

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

    # Tuple of all direct superclasses originally listed by this class prior to
    # PEP 484 type erasure if any *OR* the empty tuple otherwise.
    hint_bases = getattr(hint_type, '__orig_bases__', ())

    # If this class was *NOT* subject to type erasure, reduce to a noop.
    if not hint_bases:
        return hint_bases

    # Fixed list of all typing super attributes to be returned.
    super_attrs = acquire_fixed_list(SIZE_BIG)

    # 0-based index of the last item of this list.
    super_attrs_index = 0

    # For each direct original superclass of this class...
    for hint_base in hint_bases:
        # If this superclass is a typing attribute...
        if is_hint_typing(hint_base):
            # Avoid inserting this attribute into the "hint_orig_mro" list.
            # Most typing attributes are *NOT* actual classes and those that
            # are have no meaningful public superclass. Ergo, iteration
            # terminates with typing attributes.
            #
            # Insert this attribute at the current item of this list.
            super_attrs[super_attrs_index] = hint_base

            # Increment this index to the next item of this list.
            super_attrs_index += 1

            # If this class subclasses more than the maximum number of "typing"
            # attributes supported by this function, raise an exception.
            if super_attrs_index >= SIZE_BIG:
                raise BeartypeDecorHintValuePep560Exception(
                    '{} PEP type {!r} subclasses more than '
                    '{} "typing" types.'.format(
                        hint_label,
                        hint,
                        SIZE_BIG))

    # Tuple sliced from the prefix of this list assigned to above.
    super_attrs_tuple = tuple(super_attrs[:super_attrs_index])

    # Release and nullify this list *AFTER* defining this tuple.
    release_fixed_list(super_attrs)
    del super_attrs

    # Return this tuple as is.
    return super_attrs_tuple
