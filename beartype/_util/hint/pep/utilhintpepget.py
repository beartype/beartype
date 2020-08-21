#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint getter utilities** (i.e., callables querying
arbitrary objects for attributes specific to PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Generalize get_hint_pep_typing_attrs_argless_to_args() to support
#parametrization of user-defined subclasses: e.g.,
#    class CustomSingleTypevared(typing.Generic[S, T]): pass
#    CustomSingleTypevared[int]
#
#Currently, get_hint_pep_typing_attrs_argless_to_args() only returns for that:
#    {typing.Generic: (S, T)}
#
#Instead, get_hint_pep_typing_attrs_argless_to_args() should probably return:
#    {typing.Generic: (S, T, int)}
#This assumes, of course, that that "int" is *NOT* intended to substitute for
#the "S" parametrization on the "typing.Generic" superclass -- which it very
#well might. In that case, we'd want to replace that "S" entirely with "int":
#    {typing.Generic: (int, T)}
#
#We'll need to research what PEP 484 claims about this. In either case, though:
#* If the user-defined subclass subclasses "typing.Generic", then the tuple
#  mapped from "typing.Generic" by get_hint_pep_typing_attrs_argless_to_args()
#  should be extended with the tuple of arguments on the passed subclass
#  (i.e., "get_hint_pep_args(hint)").
#* Else, get_hint_pep_typing_attrs_argless_to_args() should add a new mapping from
#  "typing.Generic" to the tuple of arguments on the passed subclass (i.e.,
#  "get_hint_pep_args(hint)").
#
#Note that this preserves the invariant that the
#get_hint_pep_typing_attrs_argless_to_args() getter only returns "typing"
#attributes while still conforming to PEP 484 nomenclature and semantics. Yeah!

# ....................{ IMPORTS                           }....................
import typing
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPep560Exception,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.utilobject import get_object_type
from typing import TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS ~ attrs                 }....................
_TYPING_ATTRS_ARGLESS_TO_ARGS_EMPTY = {}
'''
Empty dictionary constant.

The memoized :func:`get_hint_pep_typing_attrs_argless_to_args` function returns and
thus internally caches this dictionary when passed any object that is *not* a
PEP-compliant type hint. To reduce space consumption, this dictionary is
efficiently reused rather than inefficiently recreated for each recall to that
function passed such a hint.
'''


_TYPING_ATTRS_ARGLESS_TO_ARGS_TYPEVAR = {TypeVar: ()}
'''
Dictionary constant mapping only from the :class:`TypeVar` class to the empty
tuple.

The memoized :func:`get_hint_pep_typing_attrs_argless_to_args` function returns and
thus internally caches this dictionary when passed a type variable. To reduce
space consumption, this dictionary is efficiently reused rather than
inefficiently recreated for each recall to that function passed a type
variable.
'''

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
    logic attempting to directly access that attribute.

    Thus this function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    NoneTypeOr[tuple]
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
    logic attempting to directly access that attribute.

    Thus this function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    NoneTypeOr[tuple]
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

    #FIXME: Consider replacing with this more exacting test:
    #return getattr(hint, '__parameters__', ())) if is_hint_pep(hint) else ()

    # Return the value of the "__parameters__" dunder attribute on this object
    # if this object defines this attribute *OR* the empty tuple otherwise.
    return getattr(hint, '__parameters__', ())

# ....................{ GETTERS ~ attrs                   }....................
@callable_cached
def get_hint_pep_typing_attrs_argless_to_args(hint: object) -> dict:
    '''
    Dictionary mapping each **argumentless typing attribute** (i.e., public
    attribute of the :mod:`typing` module uniquely identifying the passed
    PEP-compliant type hint without arguments) of this hint if any to the tuple
    of those arguments *or* the empty dictionary otherwise.

    This getter function associates arbitrary objects with corresponding public
    attributes of the :mod:`typing` module effectively serving as unique
    pseudo-superclasses of those objects. These attributes are typically *not*
    actual superclasses, as most actual :mod:`typing` superclasses are private,
    fragile, and prone to extreme alteration (or even removal) between major
    Python versions. Nonetheless, these attributes are sufficiently unique to
    enable callers to distinguish between numerous broad categories of
    :mod:`typing` behaviour and logic.

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
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to 'Annotation'.

    Returns
    ----------
    dict
        Either:

        * If this object is uniquely identified by one or more public
          attributes of the :mod:`typing` module, a dictionary mapping these
          attributes without arguments to the tuple of those arguments (in
          method resolution order).
        * Else, the empty dictionary.

    Raises
    ----------
    BeartypeDecorHintPep560Exception
        If this object is a user-defined class subclassing no :mod:`typing`
        superclasses (e.g., due to having a ``__orig_bases__`` dunder attribute
        whose value is the empty tuple).

    Examples
    ----------

        >>> import typing
        >>> from beartype.cave import AnyType
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_typing_attrs_argless_to_args)
        >>> get_hint_pep_typing_attrs_argless_to_args(AnyType)
        {}
        >>> get_hint_pep_typing_attrs_argless_to_args(typing.Any)
        {typing.Any: ())
        >>> get_hint_pep_typing_attrs_argless_to_args(typing.Union[str, typing.Sequence[int]])
        {typing.Union: (str, typing.Sequence[int])}
        >>> get_hint_pep_typing_attrs_argless_to_args(typing.Sequence[int])
        {typing.Sequence: (int,)}
        >>> T = typing.TypeVar('T')
        >>> get_hint_pep_typing_attrs_argless_to_args(T)
        {typing.TypeVar: ()}
        >>> class Genericity(typing.Generic[T]): pass
        >>> get_hint_pep_typing_attrs_argless_to_args(Genericity)
        {typing.Generic: (T,)}
        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
        >>> get_hint_pep_typing_attrs_argless_to_args(Duplicity)
        {typing.Iterable: (T,), typing.Container: (T,)}

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep

    # If this hint is *NOT* PEP-compliant, return an empty dictionary constant.
    #
    # Note that a global constant rather than new empty dictionary is returned.
    # Why? Since dictionaries are mutable (unlike tuples), the empty dictionary
    # (unlike the empty tuple) is *NOT* a singleton object: e.g.,
    #     >>> () is ()
    #     True
    #     >>> {} is {}
    #     False
    # This common case thus efficiently recaches the same singleton object for
    # such hints, reducing the space costs of memoization.
    if not is_hint_pep(hint):
        return _TYPING_ATTRS_ARGLESS_TO_ARGS_EMPTY
    # Else, this hint is PEP-compliant.
    #
    # Else if this hint is a type variable, return a dictionary constant
    # mapping from the common type of all such variables. Note that:
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
    elif isinstance(hint, TypeVar):
        return _TYPING_ATTRS_ARGLESS_TO_ARGS_TYPEVAR
    # Else, this hint is PEP-compliant but *NOT* a type variable.

    # Direct argumentless typing attribute associated with this hint if this
    # hint is directly defined by the "typing" module *OR* "None" otherwise.
    hint_direct_typing_attr_argless = (
        _get_hint_pep_typing_bare_attr_argless_or_none(hint))

    # If this attribute exists, return a dictionary mapping from only this
    # attribute to the tuple of arguments specified on this hint.
    #
    # Doing so incurs a memoization space cost that could technically be
    # avoided by directly returning this attribute instead. Since doing so
    # would substantially increase implementation complexity (and thus
    # maintenance cost) in downstream callers, we accept this cost as the
    # unavoidable price of produce a sane API. *shrug*
    if hint_direct_typing_attr_argless is not None:
        return {hint_direct_typing_attr_argless: get_hint_pep_args(hint)}
    # Else, no such attribute exists. In this case, this hint is *NOT* directly
    # defined by the "typing" module. Since this hint is PEP-compliant, this
    # hint *MUST* necessarily be a user-defined class subclassing one or more
    # "typing" superclasses (e.g., "class CustomList(typing.List[int])").

    # Dictionary mapping each argumentless typing super attribute of this
    # subclass if any to the tuple of arguments specified on that attribute
    # *OR* the empty dictionary otherwise.
    hint_typing_superattrs_untypevared = (
        _get_hint_pep_typing_superattrs_argless_to_args(hint))

    # If this subclass failed to preserve its original tuple of "typing"
    # superclasses against "type erasure," raise an exception.
    if not hint_typing_superattrs_untypevared:
        raise BeartypeDecorHintPep560Exception(
            'PEP-compliant type hint {!r} '
            '"typing" superclasses erased.'.format(hint))

    # Else, this subclass preserved this tuple against type erasure. Return
    # this tuple as is.
    return hint_typing_superattrs_untypevared

# ....................{ PRIVATE ~ getters : attr          }....................
def _get_hint_pep_typing_bare_attr_argless(hint: object) -> (
    'NoneTypeOr[object]'):
    '''
    **Argumentless bare typing attribute** (i.e., public attribute of the
    :mod:`typing` module directly identifying the passed PEP-compliant type
    hint whose type is defined by that module without arguments and ignoring
    any superclasses of this object's class) associated with this hint if any
    *or* raise an exception otherwise.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient test.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Public attribute of the :mod:`typing` module directly identifying this
    object.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this object is *not* directly identified by a public attribute of
        the :mod:`typing` module.
    '''

    # Argumentless direct typing attribute associated with this object if any
    # *OR* "None" otherwise.
    hint_direct_typing_attr_argless = (
        _get_hint_pep_typing_bare_attr_argless_or_none(hint))

    # If this attribute exists, return this attribute.
    if hint_direct_typing_attr_argless is not None:
        return hint_direct_typing_attr_argless

    # Else, no such attribute exists. In this case, raise an exception.
    raise BeartypeDecorHintPepException(
        'PEP-compliant type hint {!r} '
        'associated with no "typing" type.'.format(hint))


@callable_cached
def _get_hint_pep_typing_bare_attr_argless_or_none(hint: object) -> (
    'NoneTypeOr[object]'):
    '''
    **Argumentless bare typing attribute** (i.e., public attribute of the
    :mod:`typing` module directly identifying the passed PEP-compliant type
    hint whose type is defined by that module without arguments and ignoring
    any superclasses of this object's class) associated with this hint if any
    *or* ``None`` otherwise.

    This getter function is memoized for efficiency.

    Caveats
    ----------
    **Call substantially faster and simpler**
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_typing` **tester
    function instead to simply decide whether an arbitrary object is defined by
    the** :mod:`typing` **module.** While this getter function can be called to
    decide that question as well, doing so would be gross overkill overly
    subject to fragile implementation details of that module.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    NoneTypeOr[object]
        Either:

        * If this object is directly identified by a public attribute of the
          :mod:`typing` module, that attribute without arguments.
        * Else, ``None``.

    Raises
    ----------
    AttributeError
        If this object's representation is prefixed by the substring
        ``typing.``, but the remainder of that representation up to but *not*
        including the first "[" character in that representation (e.g.,
        ``Dict`` for the hint ``typing.Dict[str, Tuple[int, ...]]``) is *not*
        an attribute of the :mod:`typing` module.
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
        typing_attr_name = typing_attr_name[7:]  # Hardcode us up the bomb.

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

# ....................{ PRIVATE ~ getters : super         }....................
@callable_cached
def _get_hint_pep_typing_superattrs_argless_to_args(hint: object) -> dict:
    '''
    Dictionary mapping each **argumentless typing super attribute** (i.e.,
    public attribute of the :mod:`typing` module originally listed as a
    superclass of the class of the passed PEP-compliant type hint without
    arguments) of this hint if any to the tuple of those arguments *or* the
    empty dictionary otherwise.

    This getter function is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    dict
        Either:

        * If the type of this object subclasses one or more superclasses
          uniquely identified by public attributes of the :mod:`typing` module,
          a dictionary mapping these attributes without arguments to the tuple
          of those arguments (in method resolution order).
        * Else, the empty dictionary.

    See Also
    ----------
    :func:`_get_hint_pep_typing_superattrs`
        Further details.
    '''

    # Tuple of all possibly parametrized typing super attributes of this object
    # if any *OR* the empty tuple otherwise.
    hint_typing_superattrs = _get_hint_pep_typing_superattrs(hint)

    # Return either...
    return (
        # If this object has *NO* such attributes, the empty dictionary;
        {} if not hint_typing_superattrs else
        # Else, the non-empty dictionary mapping...
        {
            # Each such attribute without arguments to...
            _get_hint_pep_typing_bare_attr_argless(hint_typing_superattr): (
                # The tuple of those arguments.
                get_hint_pep_args(hint_typing_superattr))
            for hint_typing_superattr in hint_typing_superattrs
        }
    )


@callable_cached
def _get_hint_pep_typing_superattrs(hint: object) -> tuple:
    '''
    Tuple of all **typing super attributes** (i.e., public attributes of the
    :mod:`typing` module originally listed as superclasses of the class of the
    passed PEP-compliant type hint) of this hint if this hint is a user-defined
    subclass *or* the empty tuple otherwise.

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
        >>> UserDefinedGeneric.__orig_bases__
        (List[T], Iterable[T], Generic[T])
        # Guess which we prefer?

    Ergo, we ignore the useless ``__mro__`` dunder attribute in favour of the
    actually useful ``__orig_bases__`` dunder attribute tuple. Welcome to
    :mod:`typing` hell, where even :mod:`typing` types lie broken and
    misshapen on the killing floor of overzealous purists.

    Caveats
    -------
    **Tuples returned by this function typically do not contain actual types.**
    Because the :mod:`typing` module lies about literally everything, most
    public attributes of the :mod:`typing` module used as superclasses are
    *not* actually types but singleton objects devilishly masquerading as
    types. Most true :mod:`typing` superclasses are private, fragile, and prone
    to alteration or even removal between major Python versions. Ergo, this
    function is intentionally not named ``get_hint_pep_typing_superclasses`` or
    ``_get_hint_pep_typing_superattrs``.

    **Tuples returned by this function may contain types parametrized by one or
    more type variables** (e.g., ``(typing.Container[T], typing.Sized[T])``).

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Either:

        * If the type of this object subclasses one or more superclasses
          uniquely identified by public attributes of the :mod:`typing` module,
          a tuple listing these attributes (in method resolution order).
        * Else, the empty tuple.

    Examples
    ----------

        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     _get_hint_pep_typing_superattrs)
        >>> T = typing.TypeVar('T')
        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
        >>> _get_hint_pep_typing_superattrs(
        ...     typing.Union[str, typing.Sequence[int]])
        ()
        >>> _get_hint_pep_typing_superattrs(Duplicity)
        (typing.Iterable[~T], typing.Container[~T])

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    .. _PEP 560:
       https://www.python.org/dev/peps/pep-0560
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_typing

    # If this hint is defined by the "typing" module rather than a user-defined
    # module, this hint is by definition *NOT* user-defined. In this case,
    # immediately return the empty tuple.
    if is_hint_pep_typing(hint):
        return ()

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

    # Tuple of all direct superclasses originally listed by this class prior to
    # PEP 484 type erasure if any *OR* the empty tuple otherwise.
    hint_bases = getattr(hint_type, '__orig_bases__', ())

    # Return either...
    return (
        # If this class was *NOT* subject to type erasure, the empty tuple;
        () if not hint_bases else
        # Else, the non-empty tuple of all direct original superclasses of this
        # subclass that are typing attributes.
        tuple(
            hint_base
            for hint_base in hint_bases
            if is_hint_pep_typing(hint_base)
        )
    )
