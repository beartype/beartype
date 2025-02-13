#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint getter utilities** (i.e., callables
querying arbitrary objects for attributes specific to PEP-compliant type
hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.meta import URL_ISSUES
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepSignException,
)
from beartype.roar._roarexc import _BeartypeUtilTypeException
from beartype.typing import (
    Any,
    Optional,
)
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.datahinttyping import (
    # HintSignTrie,
    TypeException,
)
from beartype._data.hint.pep.datapeprepr import (
    HINT_REPR_PREFIX_ARGS_0_OR_MORE_TO_SIGN,
    HINT_REPR_PREFIX_ARGS_1_OR_MORE_TO_SIGN,
    HINT_REPR_PREFIX_TRIE_ARGS_0_OR_MORE_TO_SIGN,
    HINT_MODULE_NAME_TO_TYPE_BASENAME_TO_SIGN,
)
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignPep484585GenericSubscripted,
    HintSignPep484585GenericUnsubscripted,
    HintSignNewType,
    HintSignTypedDict,
    HintSignPep585BuiltinSubscriptedUnknown,
    HintSignPep695TypeAliasSubscripted,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
)
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep484.pep484newtype import (
    is_hint_pep484_newtype_pre_python310)
from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
    is_hint_pep484585_generic_subscripted,
    is_hint_pep484585_generic_unsubscripted,
)
from beartype._util.hint.pep.proposal.pep484585.pep484585tuple import (
    get_hint_pep484585_sign_tuplefixed_or_same)
from beartype._util.hint.pep.proposal.pep484604 import (
    die_if_hint_pep604_inconsistent)
from beartype._util.hint.pep.proposal.pep585 import (
    get_hint_pep585_generic_typevars,
    is_hint_pep585_builtin_subscripted,
    is_hint_pep585_generic_unsubscripted,
)
from beartype._util.hint.pep.proposal.pep589 import is_hint_pep589
from beartype._util.hint.pep.proposal.pep695 import is_hint_pep695_subscripted
from beartype._util.py.utilpyversion import IS_PYTHON_AT_MOST_3_9
from beartype._data.hint.datahinttyping import TupleTypeVars

# ....................{ GETTERS ~ args                     }....................
def get_hint_pep_args(hint: object) -> tuple:
    '''
    Tuple of the zero or more **child type hints** subscripting (indexing) the
    passed PEP-compliant type hint if this hint was subscripted *or* the empty
    tuple otherwise (i.e., if this hint is unsubscripted and is thus either an
    unsubscriptable type hint *or* a subscriptable type hint factory that is
    unsubscripted).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This getter should always be called in lieu of attempting to directly
    access the low-level** ``__args__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    **This getter lies rarely due to subscription erasure** (i.e., the malicious
    destruction of child type hints by parent type hint factories at
    subscription time). Callers should *not* assume that the objects originally
    subscripting this hint are still accessible. Although *most* hints preserve
    their subscripted objects over their lifetimes, a small subset of edge-case
    hints erase those objects at subscription time. This includes:

    * :pep:`585`-compliant empty tuple type hints (i.e., ``tuple[()]``), which
      despite being explicitly subscripted erroneously erase that subscription
      at subscription time. This does *not* extend to :pep:`484`-compliant
      empty tuple type hints (i.e., ``typing.Tuple[()]``), which correctly
      preserve that subscripted empty tuple.

    **This getter lies less than the comparable**
    :func:`.get_hint_pep_typevars` **getter.** Whereas
    :func:`.get_hint_pep_typevars` synthetically propagates type variables from
    child to parent type hints (rather than preserving the literal type
    variables subscripting this type hint), this getter preserves the literal
    arguments subscripting this type hint if any. Notable cases where the two
    differ include:

    * Generic classes subclassing pseudo-superclasses subscripted by one or
      more type variables (e.g., ``class MuhGeneric(Generic[S, T])``).
    * Unions subscripted by one or more child type hints subscripted by one or
      more type variables (e.g., ``Union[str, Iterable[Tuple[S, T]]]``).

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be inspected.

    Returns
    -------
    tuple
        Either:

        * If this hint defines an ``__args__`` dunder attribute, the value of
          that attribute.
        * Else, the empty tuple.

    Examples
    --------
    .. code-block:: pycon

       >>> import typing
       >>> from beartype._util.hint.pep.utilpepget import (
       ...     get_hint_pep_args)
       >>> get_hint_pep_args(typing.Any)
       ()
       >>> get_hint_pep_args(typing.List[int, str, typing.Dict[str, str]])
       (int, str, typing.Dict[str, str])
    '''

    # Tuple of the zero or more child type hints subscripting this hint if
    # this hint defines of the "__args__" dunder attribute *OR* "None"
    # otherwise (i.e., if this hint fails to define this attribute).
    hint_args = getattr(hint, '__args__', None)

    # If this hint does *NOT* define this attribute, return the empty tuple.
    if hint_args is None:
        return ()
    # Else, this hint defines this attribute.
    #
    # If this hint is subscripted by zero child type hints, this hint only
    # superficially appears to be unsubscripted but was actually subscripted
    # by the empty tuple (e.g., "tuple[()]", "typing.Tuple[()]"). Why?
    # Because:
    # * Python 3.11 made the unfortunate decision of ambiguously conflating
    #   unsubscripted type hints (e.g., "tuple", "typing.Tuple") with type
    #   hints subscripted by the empty tuple, preventing downstream
    #   consumers from reliably distinguishing these two orthogonal cases.
    # * Python 3.9 made a similar decision but constrained to only PEP
    #   585-compliant empty tuple type hints (i.e., "tuple[()]"). PEP
    #   484-compliant empty tuple type hints (i.e., "typing.Tuple[()]")
    #   continued to correctly declare an "__args__" dunder attribute of
    #   "((),)" until Python 3.11.
    #
    # Disambiguate these two cases on behalf of callers by returning a
    # 1-tuple containing only the empty tuple (i.e., "((),)") rather than
    # returning the empty tuple (i.e., "()").
    elif not hint_args:
        return _HINT_ARGS_EMPTY_TUPLE
    # Else, this hint is either subscripted *OR* is unsubscripted but not
    # PEP 585-compliant.

    # In this case, return this tuple as is.
    return hint_args


# ....................{ GETTERS ~ typevars                 }....................
def get_hint_pep_typevars(hint: Hint) -> TupleTypeVars:
    '''
    Tuple of all **unique type variables** (i.e., subscripted :class:`TypeVar`
    instances of the passed PEP-compliant type hint listed by the caller at
    hint declaration time ignoring duplicates) if any *or* the empty tuple
    otherwise.

    This getter correctly handles both:

    * **Direct parametrizations** (i.e., cases in which this object itself is
      directly parametrized by type variables).
    * **Superclass parametrizations** (i.e., cases in which this object is
      indirectly parametrized by one or more superclasses of its class being
      directly parametrized by type variables).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__parameters__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    **Generics** (i.e., PEP-compliant type hints whose classes subclass one or
    more public :mod:`typing` pseudo-superclasses) are often but *not* always
    typevared. For example, consider the untypevared generic:

    .. code-block:: pycon

       >>> from typing import List
       >>> class UntypevaredGeneric(List[int]): pass
       >>> UntypevaredGeneric.__mro__
       (__main__.UntypevaredGeneric, list, typing.Generic, object)
       >>> UntypevaredGeneric.__parameters__
       ()

    Likewise, typevared hints are often but *not* always generic. For example,
    consider the typevared non-generic:

    .. code-block:: pycon

       >>> from typing import List, TypeVar
       >>> TypevaredNongeneric = List[TypeVar('T')]
       >>> type(TypevaredNongeneric).__mro__
       (typing._GenericAlias, typing._Final, object)
       >>> TypevaredNongeneric.__parameters__
       (~T,)

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    Tuple[TypeVar, ...]
        Either:

        * If this object defines a ``__parameters__`` dunder attribute, the
          value of that attribute.
        * Else, the empty tuple.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a PEP-compliant type hint
        parametrized by one or more type variables.

    Examples
    --------
    .. code-block:: pycon

       >>> import typing
       >>> from beartype._util.hint.pep.utilpepget import (
       ...     get_hint_pep_typevars)

       >>> S = typing.TypeVar('S')
       >>> T = typing.TypeVar('T')
       >>> class UserList(typing.List[T]): pass

       >>> get_hint_pep_typevars(typing.Any)
       ()
       >>> get_hint_pep_typevars(typing.List[int])
       ()
       >>> get_hint_pep_typevars(typing.List[T])
       (T)
       >>> get_hint_pep_typevars(UserList)
       (T)
       >>> get_hint_pep_typevars(typing.List[T, int, S, str, T])
       (T, S)
    '''

    # Value of the "__parameters__" dunder attribute on this object if this
    # object defines this attribute (e.g., is *NOT* a PEP 585-compliant
    # unsubscripted generic) *OR* "None" otherwise (e.g., is such a generic).
    hint_pep_typevars = getattr(hint, '__parameters__', None)

    # If this object defines *NO* such attribute, synthetically reconstruct
    # this attribute for PEP 585-compliant unsubscripted generics. Notably...
    if hint_pep_typevars is None:
        # Reconstruct this attribute as either...
        hint_pep_typevars = (
            # If this hint is a PEP 585-compliant unsubscripted generic, the
            # tuple of all type variables parametrizing all pseudo-superclasses
            # of this generic;
            get_hint_pep585_generic_typevars(hint)
            if is_hint_pep585_generic_unsubscripted(hint) else
            # Else, this hint is *NOT* a PEP 585-compliant unsubscripted
            # generic. In this case, the empty tuple.
            ()
        )
    # Else, this object defines this attribute.

    # Return this attribute.
    return hint_pep_typevars

# ....................{ GETTERS ~ sign                     }....................
def get_hint_pep_sign(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPepSignException,
    exception_prefix: str = '',
) -> HintSign:
    '''
    **Sign** (i.e., :class:`HintSign` instance) uniquely identifying the passed
    PEP-compliant type hint if PEP-compliant *or* raise an exception otherwise
    (i.e., if this hint is *not* PEP-compliant).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPepSignException`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    dict
        Sign uniquely identifying this hint.

    Raises
    ------
    exception_cls
        If this hint is either:

        * PEP-compliant but *not* uniquely identifiable by a sign.
        * PEP-noncompliant.
        * *Not* a hint (i.e., neither PEP-compliant nor -noncompliant).

    See Also
    --------
    :func:`.get_hint_pep_sign_or_none`
        Further details.
    '''

    # Sign uniquely identifying this hint if recognized *OR* "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # If this hint is unrecognized...
    if hint_sign is None:
        assert isinstance(exception_cls, type), (
            f'{exception_cls} not exception type.')
        assert isinstance(exception_prefix, str), (
            f'{exception_prefix} not string.')

        # Avoid circular import dependencies.
        from beartype._util.hint.nonpep.utilnonpeptest import die_if_hint_nonpep

        # If this hint is PEP-noncompliant, raise an exception.
        die_if_hint_nonpep(
            hint=hint,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
        # Else, this hint is *NOT* PEP-noncompliant. Since this hint was
        # unrecognized, this hint *MUST* necessarily be a PEP-compliant type
        # hint currently unsupported by the @beartype decorator.

        # Raise an exception indicating this.
        #
        # Note that we intentionally avoid calling the
        # die_if_hint_pep_unsupported() function here, which calls the
        # is_hint_pep_supported() function, which calls this function.
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} '
            f'currently unsupported by beartype. '
            f'You suddenly feel encouraged to submit a feature request '
            f'for this hint to our friendly issue tracker at:\n'
            f'\t{URL_ISSUES}'
        )
    # Else, this hint is recognized.

    # Return the sign uniquely identifying this hint.
    return hint_sign


#FIXME: Revise us up the docstring, most of which is now obsolete.
@callable_cached
def get_hint_pep_sign_or_none(hint: Any) -> Optional[HintSign]:
    '''
    **Sign** (i.e., :class:`HintSign` instance) uniquely identifying the passed
    PEP-compliant type hint if PEP-compliant *or* :data:`None` otherwise (i.e.,
    if this hint is *not* PEP-compliant).

    This getter function associates the passed hint with a public attribute of
    the :mod:`typing` module effectively acting as a superclass of this hint
    and thus uniquely identifying the "type" of this hint in the broadest sense
    of the term "type". These attributes are typically *not* actual types, as
    most actual :mod:`typing` types are private, fragile, and prone to extreme
    violation (or even removal) between major Python versions. Nonetheless,
    these attributes are sufficiently unique to enable callers to distinguish
    between numerous broad categories of :mod:`typing` behaviour and logic.

    Specifically, if this hint is:

    * A :pep:`585`-compliant **builtin** (e.g., C-based type
      hint instantiated by subscripting either a concrete builtin container
      class like :class:`list` or :class:`tuple` *or* an abstract base class
      (ABC) declared by the :mod:`collections.abc` submodule like
      :class:`collections.abc.Iterable` or :class:`collections.abc.Sequence`),
      this function returns ::class:`beartype.cave.HintGenericSubscriptedType`.
    * A **generic** (i.e., subclass of the :class:`typing.Generic` abstract
      base class (ABC)), this function returns
      :class:`HintSignPep484585GenericUnsubscripted`. Note this includes
      :pep:`544`-compliant **protocols** (i.e., subclasses of the
      :class:`typing.Protocol` ABC), which implicitly subclass the
      :class:`typing.Generic` ABC as well.
    * A **forward reference** (i.e., string or instance of the concrete
      :class:`typing.ForwardRef` class), this function returns
      :class:`HintSignTypeVar`.
    * A **type variable** (i.e., instance of the concrete
      :class:`typing.TypeVar` class), this function returns
      :class:`HintSignTypeVar`.
    * Any other class, this function returns that class as is.
    * Anything else, this function returns the unsubscripted :mod:`typing`
      attribute dynamically retrieved by inspecting this hint's **object
      representation** (i.e., the non-human-readable string returned by the
      :func:`repr` builtin).

    This getter is memoized for efficiency.

    Motivation
    ----------
    Both :pep:`484` and the :mod:`typing` module implementing :pep:`484` are
    functionally deficient with respect to their public APIs. Neither provide
    external callers any means of deciding the categories of arbitrary
    PEP-compliant type hints. For example, there exists no general-purpose
    means of identifying a parametrized subtype (e.g., ``typing.List[int]``) as
    a parametrization of its unparameterized base type (e.g.,
    :obj:`typing.List`). Thus this function, which "fills in the gaps" by
    implementing this oversight.

    Parameters
    ----------
    hint : Any
        Type hint to be inspected.

    Returns
    -------
    Optional[HintSign]
        Either:

        * If this hint is PEP-compliant, a sign uniquely identifying this hint.
        * If this hint is PEP-noncompliant, :data:`None`.

    Examples
    --------
    .. code-block:: pycon

       >>> import typing
       >>> from beartype._util.hint.pep.utilpepget import (
       ...     get_hint_pep_sign_or_none)

       >>> get_hint_pep_sign_or_none(typing.Any)
       typing.Any
       >>> get_hint_pep_sign_or_none(typing.Union[str, typing.Sequence[int]])
       typing.Union

       >>> T = typing.TypeVar('T')
       >>> get_hint_pep_sign_or_none(T)
       HintSignTypeVar

       >>> class Genericity(typing.Generic[T]): pass
       >>> get_hint_pep_sign_or_none(Genericity)
       HintSignPep484585GenericUnsubscripted

       >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
       >>> get_hint_pep_sign_or_none(Duplicity)
       HintSignPep484585GenericUnsubscripted
    '''

    # ..................{ IMPORTS                            }..................
    # Avoid circular import dependencies.
    from beartype._util.hint.utilhintget import get_hint_repr

    # ..................{ SYNOPSIS                           }..................
    # For efficiency, this tester identifies the sign of this type hint with
    # multiple phases performed in descending order of average time complexity
    # (i.e., expected efficiency).
    #
    # Note that we intentionally avoid validating this type hint to be
    # PEP-compliant (e.g., by calling the die_unless_hint_pep() validator).
    # Why? Because this getter is the lowest-level hint validation function
    # underlying all higher-level hint validation functions! Calling the latter
    # here would thus induce infinite recursion, which would be very bad.

    # ..................{ PHASE ~ classname                  }..................
    # This phase attempts to map from the fully-qualified classname of this
    # hint to a sign identifying *ALL* hints that are instances of that class.
    #
    # Since the "object.__class__.__qualname__" attribute is both guaranteed to
    # exist and be efficiently accessible for all hints, this phase is the
    # fastest and thus performed first. Although this phase identifies only a
    # small subset of hints, those hints are extremely common.
    #
    # More importantly, some of these classes are implemented as maliciously
    # masquerading as other classes entirely -- including __repr__() methods
    # synthesizing erroneous machine-readable representations. To avoid false
    # positives, this phase *MUST* thus be performed before repr()-based tests
    # regardless of efficiency concerns: e.g.,
    #     # Under Python >= 3.10:
    #     >>> import typing
    #     >>> bad_guy_type_hint = typing.NewType('List', bool)
    #     >>> bad_guy_type_hint.__module__ = 'typing'
    #     >>> repr(bad_guy_type_hint)
    #     typing.List   # <---- this is genuine bollocks
    #
    # Likewise, some of these classes define __repr__() methods prefixed by the
    # machine-readable representations of their children. Again, to avoid false
    # positives, this phase *MUST* thus be performed before repr()-based tests
    # regardless of efficiency concerns: e.g.,
    #     # Under Python >= 3.10:
    #     >>> repr(tuple[str, ...] | bool)
    #     tuple[str, ...] | bool  # <---- this is fine but *NOT* a tuple!

    # Class of this hint.
    hint_type = hint.__class__

    #FIXME: Is this actually the case? Do non-physical classes dynamically
    #defined at runtime actually define *BOTH* of these dunder attributes:
    #* "hint_type.__module__"?
    #* "hint_type.__qualname__"?
    # Dictionary mapping from the unqualified basenames of the types of all
    # PEP-compliant hints residing in the package defining this hint that are
    # uniquely identifiable by those types to their identifying signs if that
    # package is recognized *OR* the empty dictionary otherwise (i.e., if the
    # package defining this hint is unrecognized).
    hint_type_name_to_sign = HINT_MODULE_NAME_TO_TYPE_BASENAME_TO_SIGN.get(
        hint_type.__module__, FROZENDICT_EMPTY)

    # Sign identifying this hint if this hint is identifiable by its classname
    # *OR* "None" otherwise.
    hint_sign = hint_type_name_to_sign.get(hint_type.__qualname__)
    # print(f'hint_type: {hint_type}')
    # print(f'hint_sign [by type]: {hint_sign}')

    # If this hint is identifiable by its classname, return this sign.
    if hint_sign:
        return hint_sign
    # Else, this hint is *NOT* identifiable by its classname.

    # ..................{ PHASE ~ repr : str                 }..................
    # This phase attempts to map from the unsubscripted machine-readable
    # representation of this hint to a sign identifying *ALL* hints of that
    # representation.
    #
    # Since doing so requires both calling the repr() builtin on this hint
    # *AND* munging the string returned by that builtin, this phase is
    # significantly slower than the prior phase and thus *NOT* performed first.
    # Although slow, this phase identifies the largest subset of hints.

    # Machine-readable representation of this hint.
    hint_repr = get_hint_repr(hint)

    # Parse this representation into:
    # * "hint_repr_prefix", the substring of this representation preceding the
    #   first "[" delimiter if this representation contains that delimiter *OR*
    #   this representation as is otherwise.
    # * "hint_repr_subscripted", the "[" delimiter if this representation
    #   contains that delimiter *OR* the empty string otherwise.
    #
    # Note that the str.partition() method has been profiled to be the
    # optimally efficient means of parsing trivial prefixes like these.
    hint_repr_prefix, hint_repr_subscripted, _ = hint_repr.partition('[')

    # Sign identifying this possibly unsubscripted hint if this hint is
    # identifiable by its possibly unsubscripted representation *OR* "None".
    hint_sign = HINT_REPR_PREFIX_ARGS_0_OR_MORE_TO_SIGN.get(hint_repr_prefix)

    # If this hint is identifiable by its possibly unsubscripted representation,
    # return this sign.
    if hint_sign:
        # print(f'hint: {hint}; sign: {hint_sign}')
        # Return this sign as is if this is any sign other than the ambiguous
        # "HintSignTuple" sign *OR* reassign this sign to the unambiguous
        # "HintSignTupleFixed" sign if this is a fixed-length tuple hint.
        return get_hint_pep484585_sign_tuplefixed_or_same(
            hint=hint, hint_sign=hint_sign)
    # Else, this hint is *NOT* identifiable by its possibly unsubscripted
    # representation.
    #
    # If this representation (and thus this hint) is subscripted...
    elif hint_repr_subscripted:
        # Sign identifying this necessarily subscripted hint if this hint is
        # identifiable by its necessarily subscripted representation *OR*
        # "None" otherwise.
        hint_sign = HINT_REPR_PREFIX_ARGS_1_OR_MORE_TO_SIGN.get(
            hint_repr_prefix)

        # If this hint is identifiable by its necessarily subscripted
        # representation...
        if hint_sign:
            # Return this sign as is if this is any sign other than the
            # ambiguous "HintSignTuple" sign *OR* reassign this sign to the
            # unambiguous "HintSignTupleFixed" sign if this is a fixed-length
            # tuple hint.
            return get_hint_pep484585_sign_tuplefixed_or_same(
                hint=hint, hint_sign=hint_sign)
        # Else, this hint is *NOT* identifiable by its necessarily subscripted
        # representation.
    # Else, this representation (and thus this hint) is unsubscripted.

    # ..................{ PHASE ~ repr : trie                }..................
    # This phase attempts to (in order):
    #
    # 1. Split the unsubscripted machine-readable representation of this hint on
    #    the "." delimiter into an iterable of module names.
    # 2. Iteratively look up each such module name in a trie mapping from these
    #    names to a sign identifying *ALL* hints in that module.
    #
    # Note that:
    # * This phase is principally intended to ignore PEP-noncompliant type hints
    #   defined by third-party packages in an efficient and robust manner. Well,
    #   reasonably efficient and robust anyway. *sigh*
    # * This phase must be performed *BEFORE* the subsequent phase that detects
    #   generics. Generics defined in modules mapped by tries should
    #   preferentially be identified as their module-specific signs rather than
    #   as generics. (See the prior note.)
    #
    # Since doing so requires splitting a string and iterating over substrings,
    # this phase is significantly slower than prior phases and thus performed
    # almost last. Since this phase identifies an extremely small subset of
    # hints, efficiency is (mostly) incidental.

    # Iterable of module names split from the unsubscripted machine-readable
    # representation of this hint. For example, doing so splits
    # 'pandera.typing.DataFrame[DataFrameSchema()]' into
    # '("pandera", "typing", "DataFrame",)'.
    hint_repr_module_names = hint_repr_prefix.split('.')

    # Possibly nested trie describing the current module name in this iterable.
    hint_repr_module_name_trie = HINT_REPR_PREFIX_TRIE_ARGS_0_OR_MORE_TO_SIGN

    # For each module name in this iterable...
    for hint_repr_module_name in hint_repr_module_names:
        # Possibly nested trie describing this module name in this iterable.
        hint_repr_module_name_trie = hint_repr_module_name_trie.get(  # type: ignore
            hint_repr_module_name)

        # If this trie does *NOT* exist, this module is *NOT* mapped to a sign.
        # In this case, immediately halt iteration.
        if hint_repr_module_name_trie is None:
            break
        # Else, this trie exists. In this case, this module *MIGHT* be mapped to
        # a sign. Further inspection is required, however.
        #
        # If this trie is actually a target sign, this module maps to this sign.
        # In this case, return this sign.
        elif hint_repr_module_name_trie.__class__ is HintSign:
            return hint_repr_module_name_trie  # type: ignore[return-value]
        # Else, this trie is another nested trie. In this case, continue
        # iterating deeper into this trie.
    # Else, this hint is *NOT* identified by a trie of module names.

    # ..................{ PHASE ~ manual                     }..................
    # This phase attempts to manually identify the signs of all hints *NOT*
    # efficiently identifiably by the prior phases.
    #
    # For minor efficiency gains, the following tests are intentionally ordered
    # in descending likelihood of a match.

    # If this hint is a PEP 484- or 585-compliant unsubscripted generic (i.e.,
    # user-defined class superficially subclassing at least one PEP 484- or
    # 585-compliant type hint), return that sign. However, note that:
    # * Generics *CANNOT* be detected by the general-purpose logic performed
    #   above, as the "typing.Generic" ABC does *NOT* define a __repr__()
    #   dunder method returning a string prefixed by the "typing." substring.
    #   Ergo, we necessarily detect generics with an explicit test instead.
    # * *ALL* PEP 484-compliant generics and PEP 544-compliant protocols are
    #   guaranteed by the "typing" module to subclass this ABC regardless of
    #   whether those generics originally did so explicitly. How? By type
    #   erasure, the gift that keeps on giving:
    #     >>> import typing as t
    #     >>> class MuhList(t.List): pass
    #     >>> MuhList.__orig_bases__
    #     (typing.List)
    #     >>> MuhList.__mro__
    #     (__main__.MuhList, list, typing.Generic, object)
    # * *NO* PEP 585-compliant generics subclass this ABC unless those generics
    #   are also either PEP 484- or 544-compliant. Indeed, PEP 585-compliant
    #   generics subclass *NO* common superclass.
    # * Generics are *NOT* necessarily classes, despite originally being
    #   declared as classes. Although *MOST* generics are classes, some are
    #   shockingly *NOT*: e.g.,
    #       >>> from typing import Generic, TypeVar
    #       >>> S = TypeVar('S')
    #       >>> T = TypeVar('T')
    #       >>> class MuhGeneric(Generic[S, T]): pass
    #       >>> non_class_generic = MuhGeneric[S, T]
    #       >>> isinstance(non_class_generic, type)
    #       False
    #
    # Ergo, the "typing.Generic" ABC uniquely identifies many but *NOT* all
    # generics. While non-ideal, the failure of PEP 585-compliant generics to
    # subclass a common superclass leaves us with little alternative.
    if is_hint_pep484585_generic_unsubscripted(hint):
        return HintSignPep484585GenericUnsubscripted
    # Else, this hint is *NOT* a PEP 484- or 585-compliant unsubscripted
    # generic.
    #
    # If this hint is a PEP 484- or 585-compliant subscripted generic (i.e.,
    # object subscripted by one or more child type hints originating from a
    # user-defined class superficially subclassing at least one PEP 484- or
    # 585-compliant type hint), return that sign. See above for commentary.
    elif is_hint_pep484585_generic_subscripted(hint):
        return HintSignPep484585GenericSubscripted
    # Else, this hint is *NOT* a PEP 484- or 585-compliant subscripted generic.
    #
    # If this hint is a PEP 589-compliant typed dictionary, return that sign.
    elif is_hint_pep589(hint):
        return HintSignTypedDict
    # Else, this hint is *NOT* a PEP 589-compliant typed dictionary.
    #
    # If the active Python interpreter targets Python < 3.10 (and thus defines
    # PEP 484-compliant "NewType" type hints as closures returned by that
    # function that are sufficiently dissimilar from all other type hints to
    # require unique detection) *AND* this hint is such a hint, return the
    # corresponding sign.
    #
    # Note that these hints *CANNOT* be detected by the general-purpose logic
    # performed above, as the __repr__() dunder methods of the closures created
    # and returned by the NewType() closure factory function return a standard
    # representation rather than a string prefixed by "typing.": e.g.,
    #     >>> import typing as t
    #     >>> repr(t.NewType('FakeStr', str))
    #     '<function NewType.<locals>.new_type at 0x7fca39388050>'
    elif IS_PYTHON_AT_MOST_3_9 and is_hint_pep484_newtype_pre_python310(hint):
        return HintSignNewType

    # ..................{ ERROR                              }..................
    # Else, this hint is unrecognized. In this case, this hint is of unknown
    # third-party origin and provenance.

    # If this hint is inconsistent with respect to PEP 604-style new unions,
    # raise an exception. Although awkward, this is ultimately the ideal context
    # for this validation. Why? Because this validation:
    # * *ONLY* applies to hints permissible as items of PEP 604-compliant new
    #   unions; this means classes and subscripted builtins. If this hint is
    #   identifiable by its classname, this hint is neither a class *NOR* a
    #   subscripted builtin. Since this hint is *NOT* identifiable by its
    #   classname, however, this hint could still be either a class *OR*
    #   subscripted builtin. It's best not to ask.
    # * Does *NOT* apply to well-known type hints detected above (e.g., those
    #   produced by Python itself, the standard library, and well-known
    #   third-party type hint factories), which are all guaranteed to be
    #   consistent with respect to PEP 604.
    die_if_hint_pep604_inconsistent(hint)
    # Else, this hint is consistent with respect to PEP 604-style new unions.

    #FIXME: Unit test us up, please.
    # If this hint is an unrecognized subscripted builtin type hint (i.e.,
    # C-based type hint instantiated by subscripting a pure-Python origin class
    # unrecognized by @beartype and thus PEP-noncompliant)...
    if is_hint_pep585_builtin_subscripted(hint):
        # If this hint is a PEP 695-compliant subscripted type alias (i.e.,
        # object created by subscripting an object created by a statement of the
        # form "type {alias_name}[{type_var}] = {alias_value}" by one or more
        # child type hints), return the corresponding sign.
        if is_hint_pep695_subscripted(hint):
            return HintSignPep695TypeAliasSubscripted
        # Else, this hint is *NOT* a PEP 695-compliant subscripted type alias.

        # Return this ambiguous sign. This is a last-ditch fallback preferable
        # to merely returning "None", which conveys substantially less semantics
        # and would imply this object to be an isinstanceable class, which
        # subscripted builtin type hints are *NOT*. Examples include
        # "os.PathLike[...]" and "weakref.weakref[...]" type hints.
        return HintSignPep585BuiltinSubscriptedUnknown
    # Else, this hint is *NOT* an unrecognized subscripted builtin type hint.

    # Return "None".
    return None

# ....................{ GETTERS ~ origin                   }....................
def get_hint_pep_origin(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    #FIXME: This should probably be a new "BeartypeDecorHintPepOriginException"
    #type, instead. But it's unclear whether users will even ever see this
    #exception. So, for now, laziness prevails. Huzzah! *sigh*
    exception_cls: TypeException = _BeartypeUtilTypeException,
    exception_prefix: str = '',
) -> Hint:
    '''
    **Unsafe origin object** (i.e., arbitrary object originating the passed
    PEP-compliant type hint but *not* necessarily an isinstanceable class such
    that all objects satisfying this hint are instances of this class)
    originating this hint if this hint originates from an origin *or*
    raise an exception otherwise (i.e., if this hint originates from *no*
    origin).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilTypeException`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    Optional[Hint]
        Either:

        * If this hint originates from an arbitrary object, that object.
        * Else, :data:`None`.
    '''

    # Origin originating this hint if any *OR* "None" otherwise.
    hint_origin = get_hint_pep_origin_or_none(hint)

    # If this hint does *NOT* originate from anything, raise an exception.
    if hint_origin is None:
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} '
            f'originates from no other object.'
        )
    # Else, this hint originates from something.

    # Return that something.
    return hint_origin


def get_hint_pep_origin_or_none(hint: Hint) -> Optional[Hint]:
    '''
    **Unsafe origin object** (i.e., arbitrary object originating the passed
    PEP-compliant type hint but *not* necessarily an isinstanceable class such
    that all objects satisfying this hint are instances of this class)
    originating this hint if this hint originates from an origin *or*
    :data:`None` otherwise (i.e., if this hint originates from *no* origin).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **The high-level** :func:`get_hint_pep_origin_type_isinstanceable` getter
    should always be called in lieu of this low-level function.** Whereas the
    former is guaranteed to return either an isinstanceable class or
    :data:`None`, this getter enjoys no such guarantees and instead returns an
    arbitrary object that may or may not actually be an instanceable class.

    If this getter *must* be called, **this getter should always be called in
    lieu of attempting to directly access the low-level** ``__origin__``
    **dunder attribute.** Various :mod:`typing` objects either fail to define
    this attribute or define this attribute non-orthogonally, including objects:

    * Failing to define this attribute altogether (e.g., :attr:`typing.Any`,
      :attr:`typing.NoReturn`).
    * Defining this attribute to be their unsubscripted :mod:`typing` type hint
      factories (e.g., :attr:`typing.Optional`, :attr:`typing.Union`).
    * Defining this attribute to be their actual origin types.

    Since the :mod:`typing` module neither guarantees the existence of this
    attribute nor imposes a uniform semantic on this attribute when defined,
    that attribute is *not* safely directly accessible. Thus this getter, which
    "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    Optional[Hint]
        Either:

        * If this hint originates from an arbitrary object, that object.
        * Else, :data:`None`.

    Examples
    --------
    .. code-block:: pycon

       >>> import typing
       >>> from beartype._util.hint.pep.utilpepget import (
       ...     get_hint_pep_origin_or_none)

       # This is sane.
       >>> get_hint_pep_origin_or_none(typing.List)
       list
       >>> get_hint_pep_origin_or_none(typing.List[int])
       list
       >>> get_hint_pep_origin_or_none(typing.Union)
       None
       >>> get_hint_pep_origin_or_none(typing.Union[int])
       None

       # This is insane.
       >>> get_hint_pep_origin_or_none(typing.Union[int, str])
       Union

       # This is crazy.
       >>> typing.Union.__origin__
       AttributeError: '_SpecialForm' object has no attribute '__origin__'

       # This is balls crazy.
       >>> typing.Union[int].__origin__
       AttributeError: type object 'int' has no attribute '__origin__'

       # This is balls cray-cray -- the ultimate evolution of crazy.
       >>> typing.Union[int, str].__origin__
       typing.Union
    '''

    # Return this hint's origin object if any *OR* "None" otherwise.
    return getattr(hint, '__origin__', None)

# ....................{ GETTERS ~ origin : type            }....................
#FIXME: Unit test us up, please.
def get_hint_pep_origin_type(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    #FIXME: This should probably be a new "BeartypeDecorHintPepOriginException"
    #type, instead. But it's unclear whether users will even ever see this
    #exception. So, for now, laziness prevails. Huzzah! *sigh*
    exception_cls: TypeException = _BeartypeUtilTypeException,
    exception_prefix: str = '',
) -> type:
    '''
    **Origin type** (i.e., class such that *all* objects satisfying the passed
    PEP-compliant type hint are instances of this class) originating this hint
    if this hint originates from such a type *or* raise an exception otherwise
    (i.e., if this hint originates from *no* such type).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilTypeException`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    type
        Type originating this hint.

    Raises
    ------
    exception_cls
        If this hint either:

        * Does *not* originate from another object.
        * Originates from an object that is *not* a type.

    See Also
    --------
    :func:`.get_hint_pep_origin_or_none`
        Further details.
    '''

    # Origin type originating this hint if any *OR* "None" otherwise.
    hint_origin = get_hint_pep_origin_type_or_none(hint)

    # If *NO* origin type originates this hint...
    if hint_origin is None:
        assert isinstance(exception_cls, type), (
            f'{exception_cls} not exception type.')
        assert isinstance(exception_prefix, str), (
            f'{exception_prefix} not string.')

        # Origin non-type originating this hint if any *OR* "None" otherwise.
        hint_origin_nontype = get_hint_pep_origin_or_none(hint)

        # If this hint does *NOT* originate from another object, raise an
        # appropriate exception.
        if hint_origin_nontype is None:
            raise exception_cls(
                f'{exception_prefix}type hint {repr(hint)} '
                f'originates from no other object.'
            )
        # Else, this hint originates from another object. By definition, this
        # object *CANNOT* be a type.

        # Raise an appropriate exception.
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} '
            f'originates from non-type {repr(hint_origin_nontype)}.'
        )
    # Else, this origin type originates this hint.

    # Return this origin type.
    return hint_origin


#FIXME: Unit test us up, please.
def get_hint_pep_origin_type_or_none(
    # Mandatory parameters.
    hint: Any,

    # Optional parameters.
    is_self_fallback: bool = False,
) -> Optional[type]:
    '''
    **Origin type** (i.e., class such that *all* objects satisfying the passed
    PEP-compliant type hint are instances of this class) originating this hint
    if this hint originates from such a type *or* :data:`None` otherwise (i.e.,
    if this hint originates from *no* such type).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This high-level getter should always be called in lieu of either calling
    the low-level** :func:`.get_hint_pep_origin_or_none` **getter or attempting
    to directly access the low-level** ``__origin__`` **dunder attribute.**

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    is_self_fallback : bool = False
        :data:`True` only if returning the passed hint as a last-ditch fallback
        when this hint is a type defining the ``__origin__`` dunder attribute to
        be a non-type. Equivalently, if the passed hint is such a hint *and*
        this parameter is:

        * :data:`True`, this getter returns this hint as is.
        * :data:`False`, this getter returns :data:`None`.

        Defaults to :data:`False`. Explicit is better than implicit.

    Returns
    -------
    Optional[type]
        Either:

        * If this hint originates from a type, that type.
        * Else, :data:`None`.

    See Also
    --------
    :func:`.get_hint_pep_origin_or_none`
        Further details.
    '''
    assert isinstance(is_self_fallback, bool), (
        f'{repr(is_self_fallback)} not boolean.')

    # Unsafe origin type originating this hint if any *OR* "None" otherwise,
    # initialized to the arbitrary object set as the "hint.__origin__" dunder
    # attribute if this hint defines that attribute.
    hint_origin: Optional[type] = get_hint_pep_origin_or_none(hint)  # type: ignore[assignment]

    #FIXME: Unit test this up, please. *shrug*
    # If this origin is *NOT* a type...
    #
    # Ideally, this attribute would *ALWAYS* be a type for all possible
    # PEP-compliant type hints. For unknown reasons, type hint factories defined
    # by the standard "typing" module often set their origins to those same type
    # hint factories, despite those factories *NOT* being types. Why? Frankly,
    # we have no idea and neither does anyone else. Behold, true horror:
    #    >>> import typing
    #    >>> typing.Literal[1, 2].__origin__
    #    typing.Literal  # <-- do you even know what you are doing, python?
    #    >>> typing.Optional[int].__origin__
    #    typing.Union  # <-- wut? this is insane, python.
    if not isinstance(hint_origin, type):
        # Default this origin type to either...
        hint_origin = (
            # If...
            hint if (
                # The caller requests the "self" fallback logic *AND*...
                is_self_fallback and
                # This hint is itself a type, this hint could be euphemistically
                # said to originate from "itself." Fallback to this hint itself.
                # Look. Just go with it. We wave our hands in the air
                isinstance(hint, type)
            ) else
            # Else, either the caller did not request the "self" fallback logic
            # *OR* this hint is not a type. In either case, fallback to "None".
            None
        )
    # Else, this origin is a type.

    # Return this origin type.
    return hint_origin


def get_hint_pep_origin_type_isinstanceable(hint: Hint) -> type:
    '''
    **Isinstanceable origin type** (i.e., class passable as the second argument
    to the :func:`isinstance` builtin such that *all* objects satisfying the
    passed PEP-compliant type hint are instances of this class) originating
    this hint if this hint originates from such a type *or* raise an exception
    otherwise (i.e., if this hint does *not* originate from such a type).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    type
        Standard origin type originating this hint.

    Raises
    ------
    BeartypeDecorHintPepException
        If this hint does *not* originate from a standard origin type.

    See Also
    --------
    :func:`get_hint_pep_origin_type_isinstanceable_or_none`
        Related getter.
    '''

    # Origin type originating this object if any *OR* "None" otherwise.
    hint_origin_type = get_hint_pep_origin_type_isinstanceable_or_none(hint)

    # If this type does *NOT* exist, raise an exception.
    if hint_origin_type is None:
        raise BeartypeDecorHintPepException(
            f'Type hint {repr(hint)} not isinstanceable (i.e., does not '
            f'originate from isinstanceable class).'
        )
    # Else, this type exists.

    # Return this type.
    return hint_origin_type


def get_hint_pep_origin_type_isinstanceable_or_none(
    hint: Hint) -> Optional[type]:
    '''
    **Standard origin type** (i.e., isinstanceable class declared by Python's
    standard library such that *all* objects satisfying the passed
    PEP-compliant type hint are instances of this class) originating this hint
    if this hint originates from such a type *or* :data:`None` otherwise (i.e.,
    if this hint does *not* originate from such a type).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This high-level getter should always be called in lieu of the low-level**
    :func:`get_hint_pep_origin_or_none` **getter or attempting to
    directly access the low-level** ``__origin__`` **dunder attribute.**

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    Optional[type]
        Either:

        * If this hint originates from a standard origin type, that type.
        * Else, :data:`None`.

    See Also
    --------
    :func:`get_hint_pep_origin_type_isinstanceable`
        Related getter.
    :func:`get_hint_pep_origin_or_none`
        Further details.
    '''

    # Sign uniquely identifying this hint if any *OR* "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # Return either...
    return (
        # If this sign originates from an origin type, that type;
        get_hint_pep_origin_or_none(hint)  # pyright: ignore
        if hint_sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE else
        # Else, "None".
        None
    )

# ....................{ PRIVATE ~ args                     }....................
#FIXME: Shift into the "beartype._data.hint" subpackage somewhere, please.
_HINT_ARGS_EMPTY_TUPLE = ((),)
'''
Tuple containing only the empty tuple, to be returned from the
:func:`get_hint_pep_args` getter when passed either:

* A :pep:`585`-compliant type hint subscripted by the empty tuple (e.g.,
  ``tuple[()]``).
* A :pep:`484`-compliant type hint subscripted by the empty tuple (e.g.,
  ``typing.Tuple[()]``) under Python >= 3.11, which applied the :pep:`585`
  approach throughout the :mod:`typing` module.
'''
