#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint getter utilities** (i.e., callables
querying arbitrary objects for attributes specific to PEP-compliant type
hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype.meta import URL_ISSUES
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepSignException,
)
from beartype._cave._cavefast import HintGenericSubscriptedType
from beartype._data.hint.pep.datapeprepr import (
    HINT_REPR_PREFIX_ARGS_0_OR_MORE_TO_SIGN,
    HINT_REPR_PREFIX_ARGS_1_OR_MORE_TO_SIGN,
    HINT_TYPE_NAME_TO_SIGN,
)
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignGeneric,
    HintSignNewType,
    HintSignTypedDict,
    HintSignTypeVar,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep484.utilpep484newtype import (
    is_hint_pep484_newtype_pre_python310)
from beartype._util.hint.pep.proposal.utilpep585 import (
    get_hint_pep585_generic_typevars,
    is_hint_pep585_generic,
)
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_MOST_3_9,
    IS_PYTHON_AT_LEAST_3_9,
    IS_PYTHON_AT_LEAST_3_7,
)
from beartype._data.datatyping import TupleTypes
from typing import Any, Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ args                    }....................
# If the active Python interpreter targets Python >= 3.9, implement this
# getter to directly access the "__args__" dunder attribute.
if IS_PYTHON_AT_LEAST_3_9:
    _HINT_PEP585_ARGS_EMPTY_TUPLE = ((),)
    '''
    Tuple containing only the empty tuple, to be returned from the
    :func:`get_hint_pep_args` getter when passed a :pep:`585`-compliant type
    hint subscripted by the empty tuple (e.g., ``tuple[()]``).
    '''


    def get_hint_pep_args(hint: object) -> tuple:

        # Return the value of the "__args__" dunder attribute if this hint
        # defines this attribute *OR* the empty tuple otherwise.
        hint_args = getattr(hint, '__args__', ())

        # Return either...
        return (
            # If this hint appears to be unsubscripted but is PEP
            # 585-compliant, then this hint *WAS* actually subscripted by the
            # empty tuple (e.g., "tuple[()]"). For unknown reasons, the
            # "HintGenericSubscriptedType" superclass erroneously reduces the
            # empty tuple subscripting such hints to... literally nothing.
            # Since doing so violates orthogonality with equivalent PEP
            # 484-compliant type hints that do correctly preserve their
            # arguments (e.g., "Tuple[()]"), we silently coerce PEP
            # 585-compliant type hints to behave like PEP 484-compliant type
            # hints by returning a tuple containing only the empty tuple.
            _HINT_PEP585_ARGS_EMPTY_TUPLE
            if (
                not hint_args and isinstance(hint, HintGenericSubscriptedType)
            ) else
            # Else, return this tuple as is.
            hint_args
        )
# Else if the active Python interpreter targets Python >= 3.7, implement this
# getter to directly access the "__args__" dunder attribute.
elif IS_PYTHON_AT_LEAST_3_7:
    def get_hint_pep_args(hint: object) -> tuple:

        # Return the value of the "__args__" dunder attribute if this hint
        # defines this attribute *OR* the empty tuple otherwise.
        return getattr(hint, '__args__', ())
#FIXME: Drop this like hot lead after dropping Python 3.6 support.
# Else, the active Python interpreter targets Python 3.6. In this case...
#
# Gods... this is horrible. Thanks for nuthin', Python 3.6.
else:
    def get_hint_pep_args(hint: object) -> tuple:

        # If this hint is a poorly designed Python 3.6-specific "type alias",
        # this hint is a subscription of either the "typing.Match" or
        # "typing.Pattern" objects. In this case, this hint declares a
        # non-standard "type_var" instance variable whose value is either
        # "typing.AnyStr", "str", or "bytes". Create and return a new 1-tuple
        # containing only the value of this variable.
        if isinstance(hint, typing._TypeAlias):  # type: ignore[attr-defined]
            return (hint.type_var,)

        # Return the value of the "__args__" dunder attribute if this hint
        # defines this attribute *OR* the empty tuple otherwise.
        #
        # Note this hint is a poorly designed Python 3.6-specific "generic
        # meta." In this case, this hint declares the standard "__args__"
        # dunder attribute in a non-standard way. Specifically, the trailing
        # "or ()" test below is needed to handle undocumented edge cases under
        # the Python 3.6-specific "typing" implementation:
        #     >>> import typing as t
        #     >>> t.Tuple.__args__   # yes, this is total bullocks
        #     None
        return getattr(hint, '__args__', ()) or ()

# Document this function regardless of implementation details above.
get_hint_pep_args.__doc__ = '''
    Tuple of all **typing arguments** (i.e., subscripted objects of the passed
    PEP-compliant type hint listed by the caller at hint declaration time)
    if any *or* the empty tuple otherwise.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This getter should always be called in lieu of attempting to directly
    access the low-level** ``__args__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    **This getter never lies, unlike the comparable**
    :func:`get_hint_pep_typevars` **getter.** Whereas
    :func:`get_hint_pep_typevars` synthetically propagates type variables from
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
    ----------
    tuple
        Either:

        * If this hint defines an ``__args__`` dunder attribute, the value of
          that attribute.
        * Else, the empty tuple.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilpepget import (
        ...     get_hint_pep_args)
        >>> get_hint_pep_args(typing.Any)
        ()
        >>> get_hint_pep_args(typing.List[int, str, typing.Dict[str, str]])
        (int, str, typing.Dict[str, str])
    '''

# ....................{ GETTERS ~ typevars                }....................
# If the active Python interpreter targets Python >= 3.9, implement this
# function to either directly access the "__parameters__" dunder attribute for
# type hints that are not PEP 585-compliant generics *OR* to synthetically
# reconstruct that attribute for PEP 585-compliant generics. *sigh*
if IS_PYTHON_AT_LEAST_3_9:
    def get_hint_pep_typevars(hint: object) -> TupleTypes:

        # Value of the "__parameters__" dunder attribute on this object if this
        # object defines this attribute *OR* "None" otherwise.
        hint_pep_typevars = getattr(hint, '__parameters__', None)

        # If this object defines *NO* such attribute...
        if hint_pep_typevars is None:
            # Return either...
            return (
                # If this hint is a PEP 585-compliant generic, the tuple of all
                # typevars declared on pseudo-superclasses of this generic.
                get_hint_pep585_generic_typevars(hint)
                if is_hint_pep585_generic(hint) else
                # Else, the empty tuple.
                ()
            )
        # Else, this object defines this attribute.

        # Return this attribute.
        return hint_pep_typevars
# Else if the active Python interpreter targets Python >= 3.7, implement
# this function to directly access the "__parameters__" dunder attribute.
elif IS_PYTHON_AT_LEAST_3_7:
    def get_hint_pep_typevars(hint: object) -> TupleTypes:

        # Value of the "__parameters__" dunder attribute on this object if this
        # object defines this attribute *OR* the empty tuple otherwise. Note:
        # * The "typing._GenericAlias.__parameters__" dunder attribute tested
        #   here is defined by the typing._collect_type_vars() function at
        #   subscription time. Yes, this is insane. Yes, this is PEP 484.
        # * This trivial test implicitly handles superclass parametrizations.
        #   Thankfully, the "typing" module percolates the "__parameters__"
        #   dunder attribute from "typing" pseudo-superclasses to user-defined
        #   subclasses during PEP 560-style type erasure. Finally: they did
        #   something slightly right.
        return getattr(hint, '__parameters__', ())
#FIXME: Drop this like hot lead after dropping Python 3.6 support.
# Else, the active Python interpreter targets Python 3.6. In this case...
#
# Gods... this is horrible. Thanks for nuthin', Python 3.6.
else:
    def get_hint_pep_typevars(hint: object) -> TupleTypes:

        # If this hint is a poorly designed Python 3.6-specific "type alias",
        # this hint is a subscription of either the "typing.Match" or
        # "typing.Pattern" objects. In this case, this hint declares a
        # non-standard "type_var" instance variable whose value is either
        # "typing.AnyStr", "str", or "bytes". Since only the former is an
        # actual type variable, however, we further test that condition.
        if isinstance(hint, typing._TypeAlias):  # type: ignore[attr-defined]
            # Sign uniquely identifying this hint if any *OR* "None" otherwise.
            hint_sign = get_hint_pep_sign_or_none(hint.type_var)

            # If this value is a type variable, return a new 1-tuple containing
            # only this type variable.
            if hint_sign is HintSignTypeVar:
                return (hint.type_var,)
            # Else, this value is *NOT* a type variable. In this case, return
            # the empty tuple.
            else:
                return ()

        # Else, this hint is a poorly designed Python 3.6-specific "generic
        # meta." In this case, this hint declares the standard
        # "__parameters__" dunder instance variable in a non-standard way.
        # Specifically, the trailing "or ()" test below is needed to handle
        # undocumented edge cases under the Python 3.6-specific implementation
        # of the "typing" module:
        #       >>> import typing as t
        #       >>> t.Union.__parameters__   # yes, this is total bullocks
        #       None
        return getattr(hint, '__parameters__', ()) or ()


# Document this function regardless of implementation details above.
get_hint_pep_typevars.__doc__ = '''
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
    Tuple[TypeVar, ...]
        Either:

        * If this object defines a ``__parameters__`` dunder attribute, the
          value of that attribute.
        * Else, the empty tuple.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilpepget import (
        ...     get_hint_pep_typevars)
        >>> S = typing.TypeVar('S')
        >>> T = typing.TypeVar('T')
        >>> get_hint_pep_typevars(typing.Any)
        ()
        >>> get_hint_pep_typevars(typing.List[T, int, S, str, T)
        (T, S)
    '''

# ....................{ GETTERS ~ sign                    }....................
def get_hint_pep_sign(hint: Any) -> HintSign:
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

    Returns
    ----------
    dict
        Sign uniquely identifying this hint.

    Raises
    ----------
    BeartypeDecorHintPepSignException
        If this hint is either:

        * PEP-compliant but *not* uniquely identifiable by a sign.
        * PEP-noncompliant.
        * *Not* a hint (i.e., neither PEP-compliant nor -noncompliant).

    See Also
    ----------
    :func:`get_hint_pep_sign_or_none`
        Further details.
    '''

    # Sign uniquely identifying this hint if recognized *OR* "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # If this hint is unrecognized...
    if hint_sign is None:
        # Avoid circular import dependencies.
        from beartype._util.hint.nonpep.utilnonpeptest import (
            die_if_hint_nonpep)

        # If this hint is PEP-noncompliant, raise an exception.
        die_if_hint_nonpep(
            hint=hint, exception_cls=BeartypeDecorHintPepSignException)
        # Else, this hint is *NOT* PEP-noncompliant. Since this hint was
        # unrecognized, this hint *MUST* necessarily be a PEP-compliant type
        # hint currently unsupported by the @beartype decorator.

        # Raise an exception indicating this.
        #
        # Note that we intentionally avoid calling the
        # die_if_hint_pep_unsupported() function here, which calls the
        # is_hint_pep_supported() function, which calls this function.
        raise BeartypeDecorHintPepSignException(
            f'Type hint {repr(hint)} currently unsupported by beartype. '
            f'You suddenly feel encouraged to submit '
            f'a feature request for this hint to our '
            f'friendly issue tracker at:\n\t{URL_ISSUES}'
        )
    # Else, this hint is recognized.

    # Return the sign uniquely identifying this hint.
    return hint_sign


#FIXME: Revise us up the docstring, most of which is now obsolete.
#FIXME: Refactor as follows:
#* Remove all now-unused "beartype._util.hint.pep.*" testers. Thanks to this
#  dramatically simpler approach, we no longer require the excessive glut of
#  PEP-specific testers we previously required.
@callable_cached
def get_hint_pep_sign_or_none(hint: Any) -> Optional[HintSign]:
    '''
    **Sign** (i.e., :class:`HintSign` instance) uniquely identifying the passed
    PEP-compliant type hint if PEP-compliant *or* ``None`` otherwise (i.e., if
    this hint is *not* PEP-compliant).

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
      base class (ABC)), this function returns :class:`HintSignGeneric`. Note
      this includes :pep:`544`-compliant **protocols** (i.e., subclasses of the
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
    a parametrization of its unparameterized base type (e.g., ``type.List``).
    Thus this function, which "fills in the gaps" by implementing this
    oversight.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.

    Returns
    ----------
    dict
        Sign uniquely identifying this hint.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this hint is *not* PEP-compliant.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilpepget import (
        ...     get_hint_pep_sign)
        >>> get_hint_pep_sign(typing.Any)
        typing.Any
        >>> get_hint_pep_sign(typing.Union[str, typing.Sequence[int]])
        typing.Union
        >>> T = typing.TypeVar('T')
        >>> get_hint_pep_sign(T)
        HintSignTypeVar
        >>> class Genericity(typing.Generic[T]): pass
        >>> get_hint_pep_sign(Genericity)
        HintSignGeneric
        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
        >>> get_hint_pep_sign(Duplicity)
        typing.Iterable
    '''

    # For efficiency, this tester identifies the sign of this type hint with
    # multiple phases performed in ascending order of average time complexity.
    #
    # Note that we intentionally avoid validating this type hint to be
    # PEP-compliant (e.g., by calling the die_unless_hint_pep() validator).
    # Why? Because this getter is the lowest-level hint validation function
    # underlying all higher-level hint validation functions! Calling the latter
    # here would thus induce infinite recursion, which would be very bad.
    #
    # ..................{ PHASE ~ classname                 }..................
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
    #defined at runtime actually define these dunder attributes as well?
    # Fully-qualified name of this class. Note that *ALL* classes are
    # guaranteed to define the dunder attributes accessed here.
    hint_type_name = f'{hint_type.__module__}.{hint_type.__qualname__}'

    # Sign identifying this hint if this hint is identifiable by its classname
    # *OR* "None" otherwise.
    hint_sign = HINT_TYPE_NAME_TO_SIGN.get(hint_type_name)

    # If this hint is identifiable by its classname, return this sign.
    if hint_sign is not None:
        return hint_sign
    # Else, this hint is *NOT* identifiable by its classname.

    # ..................{ PHASE ~ repr                      }..................
    # This phase attempts to map from the unsubscripted machine-readable
    # representation of this hint to a sign identifying *ALL* hints of that
    # representation.
    #
    # Since doing so requires both calling the repr() builtin on this hint
    # *AND* munging the string returned by that builtin, this phase is
    # significantly slower than the prior phase and thus *NOT* performed first.
    # Although slow, this phase identifies the largest subset of hints.

    # Parse the machine-readable representation of this hint into:
    # * "hint_repr_prefix", the substring of this representation preceding the
    #   first "[" delimiter if this representation contains that delimiter *OR*
    #   this representation as is otherwise.
    # * "hint_repr_subscripted", the "[" delimiter if this representation
    #   contains that delimiter *OR* the empty string otherwise.
    #
    # Note that the str.partition() method has been profiled to be the
    # optimally efficient means of parsing trivial prefixes like these.
    hint_repr_prefix, hint_repr_subscripted, _ = repr(hint).partition('[')

    # Sign identifying this possibly unsubscripted hint if this hint is
    # identifiable by its possibly unsubscripted representation *OR* "None"
    # otherwise.
    hint_sign = HINT_REPR_PREFIX_ARGS_0_OR_MORE_TO_SIGN.get(hint_repr_prefix)

    # If this hint is identifiable by its possibly unsubscripted
    # representation, return this sign.
    if hint_sign is not None:
        return hint_sign
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
        # representation, return this sign.
        if hint_sign is not None:
            return hint_sign
        # Else, this hint is *NOT* identifiable by its necessarily subscripted
        # representation.
    # Else, this representation (and thus this hint) is unsubscripted.

    # ..................{ PHASE ~ manual                    }..................
    # This phase attempts to manually identify the signs of all hints *NOT*
    # efficiently identifiably by the prior phases.
    #
    # For minor efficiency gains, the following tests are intentionally ordered
    # in descending likelihood of a match.

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
        is_hint_pep484585_generic)
    from beartype._util.hint.pep.proposal.utilpep589 import is_hint_pep589

    # If this hint is a PEP 484- or 585-compliant generic (i.e., user-defined
    # class superficially subclassing at least one PEP 484- or 585-compliant
    # type hint), return that sign. However, note that:
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
    # generics. While non-ideal, the failure of PEP 585-compliant generics
    # to subclass a common superclass leaves us with little alternative.
    if is_hint_pep484585_generic(hint):
        return HintSignGeneric
    # Else, this hint is *NOT* a PEP 484- or 585-compliant generic.
    #
    # If this hint is a PEP 589-compliant typed dictionary, return that sign.
    elif is_hint_pep589(hint):
        return HintSignTypedDict
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

    # ..................{ ERROR                             }..................
    # Else, this hint is unrecognized. In this case, return "None".
    return None

# ....................{ GETTERS ~ origin                  }....................
# If the active Python interpreter targets at least Python >= 3.7, implement
# this function to access the standard "__origin__" dunder instance variable
# whose value is the origin type originating this hint.
if IS_PYTHON_AT_LEAST_3_7:
    def get_hint_pep_origin_or_none(hint: Any) -> Optional[Any]:

        # Return this hint's origin object if any *OR* "None" otherwise.
        return getattr(hint, '__origin__', None)

#FIXME: Drop this like hot lead after dropping Python 3.6 support.
# Else, the active Python interpreter targets Python 3.6. In this case...
#
# Gods... this is horrible. Thanks for nuthin', Python 3.6.
else:
    from beartype._util.utilobject import SENTINEL

    def get_hint_pep_origin_or_none(hint: Any) -> Optional[Any]:

        # If this hint is a poorly designed Python 3.6-specific "type
        # alias", this hint is a subscription of either the "typing.Match"
        # or "typing.Pattern" objects. In this case, this hint declares a
        # non-standard "impl_type" instance variable whose value is either
        # the "re.Match" or "re.Pattern" class. Return that class.
        if isinstance(hint, typing._TypeAlias):  # type: ignore[attr-defined]
            return hint.impl_type

        # This hint's origin object if any *OR* "None" otherwise.
        #
        # If this hint is a poorly designed Python 3.6-specific "generic meta,"
        # this hint declares a non-standard "__extra__" dunder instance
        # variable whose value is the origin object originating this hint. The
        # "__origin__" dunder instance variable *DOES* exist under Python 3.6
        # but is typically the identity class referring to the same "typing"
        # singleton (e.g., "typing.List" for "typing.List[int]") rather than
        # the origin type (e.g., "list" for "typing.List[int]") and is thus
        # completely useless for everything.
        #
        # Note that we intentionally avoid defaulting "hint_extra" to "None"
        # if that attribute is undefined. Under Python 3.6, user-defined PEP
        # 484-compliant generics define:
        # * "hint.__extra__" to be "None".
        # * "hint.__origin__" to be the desired origin.
        #
        # Altogether, this means we *MUST* distinguish these two cases with a
        # sentinel placeholder that is explicitly *NOT* "None".
        #
        # Welcome to Typing Hell. We hope you really enjoy pain, because... I
        # mean, just look around.
        hint_extra = getattr(hint, '__extra__', SENTINEL)
        return (
            hint_extra
            if hint_extra is not None else
            getattr(hint, '__origin__', None)
        )

# Document this function regardless of implementation details above.
get_hint_pep_origin_or_none.__doc__ = '''
    **Unsafe origin object** (i.e., arbitrary object possibly related to the
    passed PEP-compliant type hint but *not* necessarily a non-:mod:`typing`
    class such that *all* objects satisfying this hint are instances of this
    class) originating this hint if this hint originates from an object *or*
    ``None`` otherwise (i.e., if this hint originates from *no* such object).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **The high-level** :func:`get_hint_pep_type_isinstanceable_or_none`
    function should always be called in lieu of this low-level function.**
    Whereas the former is guaranteed to return either a class or ``None``, this
    function enjoys no such guarantees and instead returns what the caller can
    only safely assume to be an arbitrary object.

    If this function *must* be called, **this function should always be called
    in lieu of attempting to directly access the low-level** ``__origin__``
    **dunder attribute.** That attribute is defined non-orthogonally by various
    singleton objects in the :mod:`typing` module, including:

    * Objects failing to define this attribute (e.g., :attr:`typing.Any`,
      :attr:`typing.NoReturn`).
    * Objects defining this attribute to be their unsubscripted :mod:`typing`
      object (e.g., :attr:`typing.Optional`, :attr:`typing.Union`).
    * Objects defining this attribute to be their origin type.

    Since the :mod:`typing` module neither guarantees the existence of this
    attribute nor imposes a uniform semantic on this attribute when defined,
    that attribute is *not* safely directly accessible. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Optional[Any]
        Either:

        * If this hint originates from an arbitrary object, that object.
        * Else, ``None``.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilpepget import (
        ...     get_hint_pep_origin_type_unsafe_or_none)
        # This is sane.
        >>> get_hint_pep_origin_type_unsafe_or_none(typing.List)
        list
        >>> get_hint_pep_origin_type_unsafe_or_none(typing.List[int])
        list
        >>> get_hint_pep_origin_type_unsafe_or_none(typing.Union)
        None
        >>> get_hint_pep_origin_type_unsafe_or_none(typing.Union[int])
        None
        # This is insane.
        >>> get_hint_pep_origin_type_unsafe_or_none(typing.Union[int, str])
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

# ....................{ GETTERS ~ origin : type           }....................
def get_hint_pep_origin_type_isinstanceable(hint: object) -> type:
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
    hint : object
        Object to be inspected.

    Returns
    ----------
    type
        Standard origin type originating this hint.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this hint does *not* originate from a standard origin type.

    See Also
    ----------
    :func:`get_hint_pep_type_isinstanceable_or_none`
        Related getter.
    '''

    # Origin type originating this object if any *OR* "None" otherwise.
    hint_origin_type = get_hint_pep_type_isinstanceable_or_none(hint)

    # If this type does *NOT* exist, raise an exception.
    if hint_origin_type is None:
        raise BeartypeDecorHintPepException(
            f'Type hint {repr(hint)} not isinstanceable (i.e., does not '
            f'originate from isinstanceable class).'
        )
    # Else, this type exists.

    # Return this type.
    return hint_origin_type


def get_hint_pep_type_isinstanceable_or_none(
    hint: Any) -> Optional[type]:
    '''
    **Standard origin type** (i.e., isinstanceable class declared by Python's
    standard library such that *all* objects satisfying the passed
    PEP-compliant type hint are instances of this class) originating this hint
    if this hint originates from such a type *or* ``None`` otherwise (i.e., if
    this hint does *not* originate from such a type).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This high-level getter should always be called in lieu of the low-level**
    :func:`get_hint_pep_origin_or_none` **getter or attempting to
    directly access the low-level** ``__origin__`` **dunder attribute.**

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Optional[type]
        Either:

        * If this hint originates from a standard origin type, that type.
        * Else, ``None``.

    See Also
    ----------
    :func:`get_hint_pep_origin_type_isinstanceable`
        Related getter.
    :func:`get_hint_pep_origin_or_none`
        Further details.
    '''

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    # Return either...
    return (
        # If this sign originates from an origin type, that type;
        get_hint_pep_origin_or_none(hint)
        if hint_sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE else
        # Else, "None".
        None
    )
