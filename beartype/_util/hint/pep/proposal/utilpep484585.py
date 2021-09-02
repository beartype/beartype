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
from beartype.roar import (
    BeartypeDecorHintForwardRefException,
    BeartypeDecorHintPep484585Exception,
    BeartypeDecorHintPep585Exception,
)
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignType,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.utilpep484 import (
    HINT_PEP484_FORWARDREF_TYPE,
    HINT_PEP484_TUPLE_EMPTY,
    get_hint_pep484_forwardref_type_basename,
    get_hint_pep484_generic_bases_unerased,
    is_hint_pep484_forwardref,
    is_hint_pep484_generic,
)
from beartype._util.hint.pep.proposal.utilpep585 import (
    HINT_PEP585_TUPLE_EMPTY,
    get_hint_pep585_generic_bases_unerased,
    is_hint_pep585_generic,
)
from beartype._util.mod.utilmodule import get_object_module_name
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
from typing import Any, Optional, Tuple, Union

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                             }....................
HINT_PEP484585_FORWARDREF_TYPES = (str, HINT_PEP484_FORWARDREF_TYPE)
'''
Tuple union of all PEP-compliant **forward reference types** (i.e.,
classes of all forward reference objects).

Specifically, this union contains:

* :class:`str`, the class of all :pep:`585`-compliant forward reference objects
  implicitly preserved by all :pep:`585`-compliant type hint factories when
  subscripted by a string.
* :class:`HINT_PEP484_FORWARDREF_TYPE`, the class of all :pep:`484`-compliant
  forward reference objects implicitly created by all :mod:`typing` type hint
  factories when subscripted by a string.

While :pep:`585`-compliant type hint factories preserve string-based forward
references as is, :mod:`typing` type hint factories coerce string-based forward
references into higher-level objects encapsulating those strings. The latter
approach is the demonstrably wrong approach, because encapsulating strings only
harms space and time complexity at runtime with *no* concomitant benefits.
'''

# ....................{ HINTS ~ private                   }....................
_HINT_PEP484585_SUBCLASS_ARGS_1_UNION: Any = (
    # If the active Python interpreter targets Python >= 3.7, include the sane
    # "typing.ForwardRef" type in this union;
    Union[type, str, HINT_PEP484_FORWARDREF_TYPE]
    if IS_PYTHON_AT_LEAST_3_7 else
    # Else, the active Python interpreter targets Python 3.6. In this case,
    # exclude the insane "typing._ForwardRef" type from this union. Naively
    # including that type here induces fatal runtime exceptions resembling:
    #     AttributeError: type object '_ForwardRef' has no attribute '_gorg'
    Union[type, str,]
)
'''
Union of the types of all permissible :pep:`484`- or :pep:`585`-compliant
**subclass type hint arguments** (i.e., PEP-compliant child type hints
subscripting (indexing) a subclass type hint).
'''


_HINT_PEP484585_SUBCLASS_ARGS_1_TYPES = (
    (type,) + HINT_PEP484585_FORWARDREF_TYPES)
'''
Tuple union of the types of all permissible :pep:`484`- or :pep:`585`-compliant
**subclass type hint arguments** (i.e., PEP-compliant child type hints
subscripting (indexing) a subclass type hint).
'''

# ....................{ VALIDATORS ~ kind : forwardref    }....................
def die_unless_hint_pep484585_forwardref(hint: object) -> None:
    '''
    Raise an exception unless the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **forward reference type hint** (i.e., object
    referring to a user-defined class that typically has yet to be defined).

    Parameters
    ----------
    hint : object
        Object to be validated.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this object is *not* a forward reference type hint.
    '''

    # If this is *NOT* a forward reference type hint, raise an exception.
    if not is_hint_pep484585_forwardref(hint):
        raise BeartypeDecorHintForwardRefException(
            f'Type hint {repr(hint)} not forward reference.')

# ....................{ TESTERS ~ kind : forwardref       }....................
def is_hint_pep484585_forwardref(hint: object) -> bool:
    '''
    ``True`` only if the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **forward reference type hint** (i.e., object
    referring to a user-defined class that typically has yet to be defined).

    Specifically, this tester returns ``True`` only if this object is either:

    * A string whose value is the syntactically valid name of a class.
    * An instance of the :class:`typing.ForwardRef` class. The :mod:`typing`
      module implicitly replaces all strings subscripting :mod:`typing` objects
      (e.g., the ``MuhType`` in ``List['MuhType']``) with
      :class:`typing.ForwardRef` instances containing those strings as instance
      variables, for nebulous reasons that make little justifiable sense but
      what you gonna do 'cause this is 2020. *Fight me.*

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a forward reference type hint.
    '''

    # Return true only if this hint is an instance of a PEP-compliant forward
    # reference superclass.
    return isinstance(hint, HINT_PEP484585_FORWARDREF_TYPES)

# ....................{ TESTERS ~ kind : generic          }....................
@callable_cached
def is_hint_pep484585_generic(hint: object) -> bool:
    '''
    ``True`` only if the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **generic** (i.e., class superficially subclassing at
    least one PEP-compliant type hint that is possibly *not* an actual class).

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
    ``True`` only if the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **empty fixed-length tuple type hint** (i.e., hint
    constraining objects to be the empty tuple).

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
        ``True`` only if this object is an empty fixed-length tuple hint.
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

# ....................{ GETTERS                           }....................
def get_hint_pep484585_args_1(
    # Mandatory parameters.
    hint: Any,

    # Optional parameters.
    hint_label: str = 'Annotated',
) -> object:
    '''
    Argument subscripting the passed :pep:`484`- or :pep:`585`-compliant
    **single-argument type hint** (i.e., hint semantically subscriptable
    (indexable) by exactly one argument).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This higher-level getter should always be called in lieu of directly
    accessing the low-level** ``__args__`` **dunder attribute,** which is
    typically *not* validated at runtime and thus should *not* be assumed to be
    sane. Although the :mod:`typing` module usually validates the arguments
    subscripting :pep:`484`-compliant type hints and thus the ``__args__``
    **dunder attribute at hint instantiation time, C-based CPython internals
    fail to similarly validate the arguments subscripting :pep:`585`-compliant
    type hints at any time:

        >>> import typing
        >>> typing.Type[str, bool]
        TypeError: Too many parameters for typing.Type; actual 2, expected 1
        >>> type[str, bool]
        type[str, bool]   # <-- when everything is okay, nothing is okay

    Parameters
    ----------
    hint : Any
        Object to be inspected.
    hint_label : str, optional
        Human-readable label prefixing this object's representation in
        exception messages. Defaults to ``"Annotated"``.

    Returns
    ----------
    type
        Superclass subscripting this subclass type hint.

    Raises
    ----------
    :exc:`BeartypeDecorHintPep585Exception`
        If this hint is subscripted by either:

        * *No* arguments.
        * Two or more arguments.
    '''

    # Tuple of all arguments subscripting this hint.
    hint_args = hint.__args__

    # If this hint was *NOT* subscripted by one argument, raise an exception.
    if len(hint_args) != 1:
        assert isinstance(hint_label, str), f'{hint_label} not string.'
        raise BeartypeDecorHintPep585Exception(
            f'{hint_label} PEP 585 type hint {repr(hint)} '
            f'not subscripted (indexed) by exactly one argument.'
        )

    # Return this argument as is.
    return hint_args[0]

# ....................{ GETTERS ~ kind : forwardref       }....................
#FIXME: Unit test against nested classes.
#FIXME: Validate that this forward reference string is *NOT* the empty string.
def get_hint_pep484585_forwardref_classname(hint: object) -> str:
    '''
    Possibly unqualified classname referred to by the passed :pep:`484`- or
    :pep:`585`-compliant **forward reference type hint** (i.e., object
    indirectly referring to a user-defined class that typically has yet to be
    defined).

    Specifically, this function returns:

    * If this hint is a :pep:`484`-compliant forward reference (i.e., instance
      of the :class:`typing.ForwardRef` class), the typically unqualified
      classname referred to by that reference. Although :pep:`484` only
      explicitly supports unqualified classnames as forward references, the
      :class:`typing.ForwardRef` class imposes *no* runtime constraints and
      thus implicitly supports both qualified and unqualified classnames.
    * If this hint is a :pep:`585`-compliant forward reference (i.e., string),
      this string as is referring to a possibly unqualified classname. Both
      :pep:`585` and :mod:`beartype` itself impose *no* runtime constraints and
      thus explicitly support both qualified and unqualified classnames.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Forward reference to be inspected.

    Returns
    ----------
    str
        Possibly unqualified classname referred to by this forward reference.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this forward reference is *not* actually a forward reference.

    See Also
    ----------
    :func:`get_hint_pep484585_forwardref_classname_relative_to_object`
        Getter returning fully-qualified forward reference classnames.
    '''

    # If this is *NOT* a forward reference type hint, raise an exception.
    die_unless_hint_pep484585_forwardref(hint)

    # Return either...
    return (
        # If this hint is a PEP 484-compliant forward reference, the typically
        # unqualified classname referred to by this reference.
        get_hint_pep484_forwardref_type_basename(hint)
        if is_hint_pep484_forwardref(hint) else
        # Else, this hint is a string. In this case, this string as is.
        hint
    )


#FIXME: Unit test against nested classes.
def get_hint_pep484585_forwardref_classname_relative_to_object(
    hint: object, obj: object) -> str:
    '''
    Fully-qualified classname referred to by the passed **forward reference
    type hint** (i.e., object indirectly referring to a user-defined class that
    typically has yet to be defined) canonicalized if this hint is unqualified
    relative to the module declaring the passed object (e.g., callable, class).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Forward reference to be canonicalized.
    obj : object
        Object to canonicalize the classname referred to by this forward
        reference if that classname is unqualified (i.e., relative).

    Returns
    ----------
    str
        Fully-qualified classname referred to by this forward reference
        relative to this callable.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this forward reference is *not* actually a forward reference.
    _BeartypeUtilModuleException
        If ``module_obj`` does *not* define the ``__module__`` dunder instance
        variable.

    See Also
    ----------
    :func:`get_hint_pep484585_forwardref_classname`
        Getter returning possibly unqualified forward reference classnames.
    '''

    # Possibly unqualified classname referred to by this forward reference.
    forwardref_classname = get_hint_pep484585_forwardref_classname(hint)

    # Return either...
    return (
        # If this classname contains one or more "." characters and is thus
        # already hopefully fully-qualified, this classname as is;
        forwardref_classname
        if '.' in forwardref_classname else
        # Else, the "."-delimited concatenation of the fully-qualified name of
        # the module declaring this class with this unqualified classname.
        f'{get_object_module_name(obj)}.{forwardref_classname}'
    )

# ....................{ GETTERS ~ kind : generic          }....................
@callable_cached
def get_hint_pep484585_generic_type_or_none(hint: object) -> Optional[type]:
    '''
    Either the passed :pep:`484`- or :pep:`585`-compliant **generic** (i.e.,
    class superficially subclassing at least one PEP-compliant type hint that
    is possibly *not* an actual class) if **unsubscripted** (i.e., indexed by
    *no* arguments or type variables), the unsubscripted generic underlying
    this generic if **subscripted** (i.e., indexed by one or more arguments
    and/or type variables), *or* ``None`` otherwise (i.e., if this hint is
    *not* a generic).

    Specifically, this getter returns:

    * If this hint both originates from an **origin type** (i.e.,
      non-:mod:`typing` class such that *all* objects satisfying this hint are
      instances of that class), that origin type.
    * Else if this hint is already a class, this hint as is.
    * Else, ``None``.

    This getter is memoized for efficiency.

    Caveats
    ----------
    **This getter returns false positives in edge cases.** That is, this getter
    returns non-``None`` values for both generics and non-generics. Callers
    *must* perform subsequent tests to distinguish these two cases.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Optional[type]
        Either:

        * If this hint is a generic, the class originating this generic.
        * Else, ``None``.

    See Also
    ----------
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


def get_hint_pep484585_generic_bases_unerased(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    #FIXME: Actually pass this parameter.
    hint_label: str = 'Annotated',
) -> Tuple[object, ...]:
    '''
    Tuple of all **unerased pseudo-superclasses** (i.e., PEP-compliant objects
    originally listed as superclasses prior to their implicit type erasure
    under :pep:`560`) of the passed :pep:`484`- or :pep:`585`-compliant
    **generic** (i.e., class superficially subclassing at least one
    PEP-compliant type hint that is possibly *not* an actual class) if this
    object is a generic *or* raise an exception otherwise (i.e., if this object
    is either not a class *or* is a class subclassing no non-class
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
    hint_label : str, optional
        Human-readable label prefixing this object's representation in
        exception messages. Defaults to ``"Annotated"``.

    Returns
    ----------
    Tuple[object]
        Tuple of the one or more unerased pseudo-superclasses of this generic.

    Raises
    ----------
    :exc:`BeartypeDecorHintPep484585Exception`
        If this hint is either:

        * Neither a :pep:`484`- nor :pep:`585`-compliant generic.
        * A :pep:`484`- nor :pep:`585`-compliant generic subclassing *no*
          pseudo-superclasses.

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

    #FIXME: Refactor get_hint_pep585_generic_bases_unerased() and
    #get_hint_pep484_generic_bases_unerased() to:
    #* Raise "BeartypeDecorHintPep484585Exception" instead.
    #* Accept an optional "hint_label" parameter, which we should pass here.

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
        raise BeartypeDecorHintPep484585Exception(
            f'{hint_label} PEP 484 or 585 generic {repr(hint)} '
            f'subclasses no superclasses.'
        )
    # Else, this generic subclasses one or more pseudo-superclasses.

    # Return this tuple of these pseudo-superclasses.
    return hint_pep_generic_bases_unerased

# ....................{ GETTERS ~ kind : subclass         }....................
def get_hint_pep484585_subclass_superclass(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotated',
) -> _HINT_PEP484585_SUBCLASS_ARGS_1_UNION:
    '''
    Superclass subscripting the passed :pep:`484`- or :pep:`585`-compliant
    **subclass type hint** (i.e., hint constraining objects to subclass some
    superclass).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    hint_label : str, optional
        Human-readable label prefixing this object's representation in
        exception messages. Defaults to ``"Annotated"``.

    Returns
    ----------
    _HINT_PEP484585_SUBCLASS_ARGS_1_UNION
        Argument subscripting this subclass type hint, guaranteed to be either:

        * A class.
        * A :pep:`484`-compliant forward reference to a class (i.e.,
          :class:`typing.ForwardRef` instance).
        * A :pep:`585`-compliant forward reference to a class (i.e., string).

    Raises
    ----------
    :exc:`BeartypeDecorHintPep484585Exception`
        If this hint is neither a :pep:`484`- nor :pep:`585`-compliant subclass
        type hint.
    :exc:`BeartypeDecorHintPep585Exception`
        If this hint is either:

        * A :pep:`585`-compliant subclass type hint subscripted by either:

          * *No* arguments.
          * Two or more arguments.

        * A :pep:`484`- or :pep:`585`-compliant subclass type hint subscripted
          by one argument that is *not* a class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign

    # If this is neither a PEP 484- nor PEP 585-compliant subclass type hint,
    # raise an exception.
    if get_hint_pep_sign(hint) is not HintSignType:
        raise BeartypeDecorHintPep484585Exception(
            f'{hint_label} type hint {repr(hint)} '
            f'not PEP 484 or 585 subclass type hint.'
        )
    # Else, this is either a PEP 484- or PEP 585-compliant subclass type hint.

    # Superclass this pith is expected to be a subclass of.
    hint_superclass = get_hint_pep484585_args_1(
        hint=hint, hint_label=hint_label)

    # If this superclass is neither a class nor forward reference to a class,
    # raise an exception.
    if not isinstance(hint_superclass, _HINT_PEP484585_SUBCLASS_ARGS_1_TYPES):
        raise BeartypeDecorHintPep585Exception(
            f'{hint_label} PEP 585 subclass type hint {repr(hint)} '
            f'argument {repr(hint_superclass)} neither '
            f'class nor forward reference to class.'
        )
    # Else, this superclass is either a class or forward reference to a class,

    # Return this superclass.
    return hint_superclass
