#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint sign getters** (i.e., low-level callables
uniquely identifying PEP-compliant type hints by singleton instances of the
:class:`.HintSign` class).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPepSignException
from beartype.typing import (
    Any,
    Optional,
)
from beartype._cave._cavefast import CallableOrClassTypes
from beartype._data.hint.datahinttyping import (
    TypeException,
)
from beartype._data.hint.pep.datapeprepr import (
    HINT_REPR_PREFIX_ARGS_0_OR_MORE_TO_SIGN,
    HINT_REPR_PREFIX_ARGS_1_OR_MORE_TO_SIGN,
    HINT_REPR_PREFIX_TRIE_ARGS_0_OR_MORE_TO_SIGN,
)
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsignmap import (
    HINT_MODULE_NAME_TO_HINT_BASENAME_TO_SIGN,
    HINT_MODULE_NAME_TO_TYPE_BASENAME_TO_SIGN,
)
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignPep484585GenericSubscripted,
    HintSignPep484585GenericUnsubscripted,
    HintSignNewType,
    HintSignTypedDict,
    HintSignPep585BuiltinSubscriptedUnknown,
    HintSignPep695TypeAliasSubscripted,
)
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
# from beartype._data.kind.datakindset import FROZENSET_EMPTY
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep484.pep484newtype import (
    is_hint_pep484_newtype_pre_python310)
from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
    is_hint_pep484585_generic_subbed,
    is_hint_pep484585_generic_unsubbed,
)
from beartype._util.hint.pep.proposal.pep484585.pep484585tuple import (
    get_hint_pep484585_sign_tuplefixed_or_same)
from beartype._util.hint.pep.proposal.pep484604 import (
    die_if_hint_pep604_inconsistent)
from beartype._util.hint.pep.proposal.pep585 import (
    is_hint_pep585_builtin_subbed)
from beartype._util.hint.pep.proposal.pep589 import is_hint_pep589
from beartype._util.hint.pep.proposal.pep695 import is_hint_pep695_subbed
from beartype._util.py.utilpyversion import IS_PYTHON_AT_MOST_3_9

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
        from beartype._util.hint.utilhinttest import die_as_hint_unsupported

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
        die_as_hint_unsupported(
            hint=hint,
            exception_prefix=exception_prefix,
            exception_cls=exception_cls,
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
    hint_type_basename_to_sign = HINT_MODULE_NAME_TO_TYPE_BASENAME_TO_SIGN.get(
        hint_type.__module__, FROZENDICT_EMPTY)

    # Sign identifying this hint if this hint is identifiable by its classname
    # *OR* "None" otherwise.
    hint_sign = hint_type_basename_to_sign.get(hint_type.__qualname__)
    # print(f'hint_type: {hint_type}')
    # print(f'hint_sign [by type]: {hint_sign}')

    # If this hint is identifiable by its classname, return this sign.
    if hint_sign:
        return hint_sign
    # Else, this hint is *NOT* identifiable by its classname.

    # ..................{ PHASE ~ (class|callable)           }..................
    # This phase attempts to map from the fully-qualified name of this hint if
    # this hint is either a type or callable to a sign identifying *ALL* hints
    # that are literally that type or callable.
    #
    # Note that most hints are *NOT* types or callables. Likewise, most objects
    # (and thus most hints) do *NOT* define the "__qualname__" dunder attribute
    # accessed by this phase. Although this phase is equally as fast as the
    # prior phase, this phase identifies only an extremely small subset of hints
    # that are all fairly uncommon. Ergo, this phase is performed early but
    # *NOT* first. Examples of hints that are types include:
    # * The PEP 484-compliant unsubscripted "typing.Generic" superclass.
    # * The PEP 544-compliant unsubscripted "typing.Protocol" superclass.

    # If this hint is either a type or callable, this hint necessarily defines
    # the "__qualname__" dunder attribute tested below. In this case...
    if isinstance(hint, CallableOrClassTypes):
        #FIXME: Is this actually the case? Do non-physical classes dynamically
        #defined at runtime actually define *BOTH* of these dunder attributes:
        #* "hint_type.__module__"?
        #* "hint_type.__qualname__"?

        # Dictionary mapping from the unqualified basenames of all
        # PEP-compliant hints that are types or callables residing in the
        # package defining this hint that are uniquely identifiable by those
        # types or callables to their identifying signs if that package is
        # recognized *OR* the empty dictionary otherwise (i.e., if the package
        # defining this hint is unrecognized).
        hint_basename_to_sign = HINT_MODULE_NAME_TO_HINT_BASENAME_TO_SIGN.get(
            hint.__module__, FROZENDICT_EMPTY)

        # Sign identifying this hint if this hint is identifiable by its
        # basename *OR* "None" otherwise.
        hint_sign = hint_basename_to_sign.get(hint.__qualname__)
        # print(f'hint: {hint}')
        # print(f'hint_sign [by self]: {hint_sign}')
        # print(f'lookup table: {HINT_MODULE_NAME_TO_HINT_BASENAME_TO_SIGN}')

        # If this hint is identifiable by its basename, return this sign.
        if hint_sign:
            return hint_sign
        # Else, this hint is *NOT* identifiable by its basename.
    # Else, this hint is neither a type nor callable.

    # ..................{ IMPORTS                            }..................
    # Avoid circular import dependencies.
    from beartype._util.hint.utilhintget import get_hint_repr

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
    # * "hint_repr_subbed", the "[" delimiter if this representation
    #   contains that delimiter *OR* the empty string otherwise.
    #
    # Note that the str.partition() method has been profiled to be the
    # optimally efficient means of parsing trivial prefixes like these.
    hint_repr_prefix, hint_repr_subbed, _ = hint_repr.partition('[')

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
    elif hint_repr_subbed:
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
    if is_hint_pep484585_generic_unsubbed(hint):
        return HintSignPep484585GenericUnsubscripted
    # Else, this hint is *NOT* a PEP 484- or 585-compliant unsubscripted
    # generic.
    #
    # If this hint is a PEP 484- or 585-compliant subscripted generic (i.e.,
    # object subscripted by one or more child type hints originating from a
    # user-defined class superficially subclassing at least one PEP 484- or
    # 585-compliant type hint), return that sign. See above for commentary.
    elif is_hint_pep484585_generic_subbed(hint):
        return HintSignPep484585GenericSubscripted
    # Else, this hint is *NOT* a PEP 484- or 585-compliant subscripted generic.

    #FIXME: Consider excising the is_hint_pep589() tester entirely. We meant
    #well... but, ultimately, the implementation is so convoluted that it's
    #better that we violate privacy encapsulation by detecting that the type of
    #this type is the private "typing._TypedDictMeta" metaclass instead. *shrug*
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
    if is_hint_pep585_builtin_subbed(hint):
        # If this hint is a PEP 695-compliant subscripted type alias (i.e.,
        # object created by subscripting an object created by a statement of the
        # form "type {alias_name}[{type_var}] = {alias_value}" by one or more
        # child type hints), return the corresponding sign.
        if is_hint_pep695_subbed(hint):
            return HintSignPep695TypeAliasSubscripted
        # Else, this hint is *NOT* a PEP 695-compliant subscripted type alias.

        # Return this ambiguous sign. This is a last-ditch fallback preferable
        # to merely returning "None", which conveys substantially less semantics
        # and would imply this object to be an isinstanceable class, which
        # subscripted builtin type hints are *NOT*. Examples include
        # "os.PathLike[...]" and "weakref.weakref[...]" type hints.
        return HintSignPep585BuiltinSubscriptedUnknown
    # Else, this hint is *NOT* an unrecognized subscripted builtin type hint.

    # ..................{ RETURN                             }..................
    # This hint *MUST* be a PEP-noncompliant albeit valid isinstanceable type,
    # which is actually the common case.

    # Return "None", informing the caller that this is an isinstanceable type.
    return None
