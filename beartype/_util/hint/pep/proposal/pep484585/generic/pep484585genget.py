#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **generic type hint
getters** (i.e., low-level callables generically introspecting various
properties common to both :pep:`484`- and :pep:`585`-compliant generic classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype._cave._cavefast import CallableOrClassTypes
from beartype._data.typing.datatyping import (
    FrozenSetStrs,
    TypeException,
)
from beartype._data.typing.datatypingport import (
    Hint,
    TupleHints,
)
from beartype._data.hint.sign.datahintsigncls import HintSign
from beartype._data.hint.sign.datahintsignmap import (
    HINT_MODULE_NAME_TO_HINT_BASE_EXTRINSIC_BASENAME_TO_SIGN)
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._util.hint.pep.proposal.pep484.pep484generic import (
    get_hint_pep484_generic_bases_unerased)
from beartype._util.hint.pep.proposal.pep585 import (
    get_hint_pep585_generic_bases_unerased,
    is_hint_pep585_generic,
)
from beartype._util.text.utiltextjoin import join_delimited_disjunction
from typing import Optional

# ....................{ GETTERS ~ base                     }....................
def get_hint_pep484585_generic_base_extrinsic_sign_or_none(
    # Mandatory parameters.
    hint_base: Hint,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> Optional[HintSign]:
    '''
    **Sign** (i.e., :data:`.HintSign` object) additionally identifying the
    passed **unerased pseudo-superclass** (i.e., PEP-compliant object originally
    declared as a transitive superclass prior to type erasure of some
    :pep:`484`- or :pep:`585`-compliant generic type) if this pseudo-superclass
    is extrinsically identifiable by a sign *or* :data:`None` otherwise (i.e.,
    if this pseudo-superclass is *not* extrinsically identifiable by a sign).

    This getter enables callers to distinguish extrinsic from intrinsic
    pseudo-superclasses. Notably, when passed:

    * An **intrinsic pseudo-superclass** (i.e., whose type-checking is
      intrinsically defined as a type hint such that all data required to
      type-check this pseudo-superclass is fully defined by this hint), this
      getter returns :data:`None`. This is the common case and, indeed, almost
      all cases. Examples include :pep:`484`- and :pep:`585`-compliant
      subscripted container type hints: e.g.,

      .. code-block:: pycon

         # The PEP 585-compliant "list[T]" pseudo-superclass is a valid hint
         # whose type-checking is intrinsic to this hint.
         >>> class GenericList[T](list[T]):
         ...     def generic_method(self, arg: T) -> T:
         ...         return arg

         # This pseudo-superclass has *NO* extrinsic sign.
         >>> get_hint_pep484585_generic_unsubbed_sign_extrinsic_or_none(
         ...     list[T])
         None

    * An **extrinsic pseudo-superclass (i.e., whose type-checking is
      extrinsically defined by this unsubscripted generic such that only the
      combination of this pseudo-superclass and this unsubscripted generic
      suffices to provide all data required to type-check this
      pseudo-superclass), the sign identifying this pseudo-superclass. Extrinsic
      pseudo-superclasses are *not* necessarily valid type hints, though some
      might be. Examples include:

      * **Generic named tuples** (i.e., types subclassing both the
        :pep:`484`-compliant :class:`typing.Generic` superclass *and* the
        :pep:`484`-compliant :class:`typing.NamedTuple` superclass): e.g.,

        .. code-block:: pycon

           # The PEP 484-compliant "NamedTuple" pseudo-superclass is *NOT* a
           # valid hint (due to being a function rather than a type) whose
           # type-checking is extrinsic to this hint.
           >>> from typing import Generic, NamedTuple
           >>> class GenericNamedTuple[T](NamedTuple, Generic[T]):
           ...     generic_item: T

           # This pseudo-superclass has an extrinsic sign.
           >>> get_hint_pep484585_generic_unsubbed_sign_extrinsic_or_none(
           ...     NamedTuple)
           HintSignNamedTuple

      * **Generic typed dictionaries** (i.e., types subclassing both the
        :pep:`484`-compliant :class:`typing.Generic` superclass *and* the
        :pep:`589`-compliant :class:`typing.TypedDict` superclass): e.g.,

        .. code-block:: pycon

           # The PEP 589-compliant "TypedDict" pseudo-superclass is a valid hint
           # (due to being a type) but whose type-checking is still extrinsic to
           # this hint.
           >>> from typing import Generic, TypedDict
           >>> class GenericTypedDict[T](TypedDict, Generic[T]):
           ...     generic_item: T

           # This pseudo-superclass has an extrinsic sign.
           >>> get_hint_pep484585_generic_unsubbed_sign_extrinsic_or_none(
           ...     TypedDict)
           HintSignTypedDict

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint_base : Hint
        Pseudo-superclass to be inspected.

    Returns
    -------
    Optional[HintSign]
        Either:

        * If this pseudo-superclass is extrinsic, the sign uniquely identifying
          this pseudo-superclass.
        * If this pseudo-superclass is intrinsic, :data:`None`.
    '''

    # ..................{ SYNOPSIS                           }..................
    # For efficiency, this tester identifies the sign of this pseudo-superclass
    # with multiple phases performed in descending order of average time
    # complexity (i.e., expected efficiency).
    #
    # Note that we intentionally avoid validating this pseudo-superclass to be a
    # PEP-compliant type hint (e.g., by calling the die_unless_hint_pep()
    # validator). Why? Because some pseudo-superclasses are *NOT* PEP-compliant
    # type hints in the global sense; they're only PEP-compliant when
    # contextually listed as a pseudo-superclass (e.g., the "typing.NamedTuple"
    # function, which is a function and thus invalid as a type hint).

    # ..................{ PHASE ~ (class|callable)           }..................
    # This phase attempts to map from the fully-qualified name of this
    # pseudo-superclass if this pseudo-superclass is either a type or callable
    # to a sign identifying *ALL* extrinsic pseudo-superclasss that are
    # literally that type or callable.

    # If this pseudo-superclass is either a type or callable, this
    # pseudo-superclass necessarily defines the "__qualname__" dunder attribute
    # tested below. In this case...
    if isinstance(hint_base, CallableOrClassTypes):
        #FIXME: Is this actually the case? Do non-physical classes dynamically
        #defined at runtime actually define *BOTH* of these dunder attributes:
        #* "pseudo-superclass_type.__module__"?
        #* "pseudo-superclass_type.__qualname__"?

        # Dictionary mapping from the unqualified basenames of all extrinsic
        # pseudo-superclasses that are types or callables residing in the
        # package defining this hint that are uniquely identifiable by those
        # types or callables to their identifying signs if that package is
        # recognized *OR* the empty dictionary otherwise (i.e., if the package
        # defining this pseudo-superclass is unrecognized).
        hint_base_extrinsic_basename_to_sign = (
            HINT_MODULE_NAME_TO_HINT_BASE_EXTRINSIC_BASENAME_TO_SIGN.get(
                hint_base.__module__, FROZENDICT_EMPTY))

        # Sign identifying this pseudo-superclass if this pseudo-superclass is
        # identifiable by its basename *OR* "None" otherwise.
        hint_base_extrinsic_sign = hint_base_extrinsic_basename_to_sign.get(
            hint_base.__qualname__)
        # print(f'pseudo-superclass: {pseudo-superclass}')
        # print(f'pseudo-superclass_sign [by self]: {pseudo-superclass_sign}')
        # print(f'lookup table: {HINT_MODULE_NAME_TO_HINT_BASENAME_TO_SIGN}')

        # If this pseudo-superclass is identifiable by its basename, return
        # this sign.
        if hint_base_extrinsic_sign:
            return hint_base_extrinsic_sign
        # Else, this pseudo-superclass is *NOT* identifiable by its basename.
    # Else, this pseudo-superclass is *NOT* a class.

    # ..................{ RETURN                             }..................
    # This pseudo-superclass *MUST* be intrinsic, which is the common case.

    # Return "None" to inform the caller this pseudo-superclass is intrinsic.
    return None

# ....................{ GETTERS ~ bases                    }....................
def get_hint_pep484585_generic_bases_unerased(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> TupleHints:
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
    **This getter should always be called in lieu of attempting to directly
    access the low-level** ``__orig_bases__`` **dunder instance variable.**
    Most PEP-compliant type hints fail to declare that variable, guaranteeing
    :class:`AttributeError` exceptions from all general-purpose logic
    attempting to directly access that variable. Thus this function, which
    "fills in the gaps" by implementing this oversight.

    **This getter returns tuples possibly containing a mixture of actual
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

        .. code-block:: pycon

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

        .. code-block:: pycon

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
    hint : Hint
        Generic type hint to be inspected.
    exception_cls : TypeException, default: BeartypeDecorHintPep484585Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    tuple[Hint, ...]
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
    .. code-block:: pycon

       >>> from beartype.typing import Container, Iterable, TypeVar
       >>> from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
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

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic_user)

    # ....................{ LOCALS                         }....................
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
            hint, exception_cls, exception_prefix)
    )

    # ....................{ RETURN                         }....................
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
    hint: Hint,
    module_names: FrozenSetStrs,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> type:
    '''
    Iteratively find and return the first **unerased superclass** (i.e.,
    unerased pseudo-superclass that is an actual superclass) transitively
    defined under the third-party package(s) or module(s) with the passed
    name(s) subclassed by the unsubscripted generic type underlying the passed
    :pep:`484`- or :pep:`585`-compliant **generic** (i.e., object that may *not*
    actually be a class despite subclassing at least one PEP-compliant type hint
    that also may *not* actually be a class).

    This finder is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Although doing so *would* dramatically
    improve the efficiency of this getter, doing so:

    * Would require all passed parameters be passed positionally, which becomes
      rather cumbersome given the number of requisite parameters.
    * Would require callers to pass a placeholder ``exception_prefix`` rather
      than the true ``exception_prefix``, which is typically context-dependent
      and thus *not* readily memoizable. Although feasible, doing so becomes
      rather cumbersome... yet again.
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
    hint : Hint
        Generic type hint to be inspected.
    module_names : frozenset[str]
        Frozen set of the fully-qualified names of all third-party packages and
        modules to find the first class in this generic type hint of.
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

       >>> from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
       ...     get_hint_pep484585_generic_base_in_module_first)

       # Reduce a Pandera type hint to the Pandas type it describes.
       >>> from pandera import DataFrameModel
       >>> from pandera.typing import DataFrame
       >>> class MuhModel(DataFrameModel): pass
       >>> get_hint_pep484585_generic_base_in_module_first(
       ...     hint=DataFrame[MuhModel], module_name='pandas', ...)
       <class 'pandas.DataFrame'>
    '''
    assert isinstance(module_names, frozenset), (
        f'{repr(module_names)} not frozen set.')
    assert all(
        isinstance(module_name, str) for module_name in module_names), (
        f'{repr(module_names)} not frozen set of strings.')

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.module.utilmodget import get_object_module_name_or_none

    # ....................{ LOCALS                         }....................
    # Either:
    # * If this generic is unsubscripted, this unsubscripted generic type as is.
    # * If this generic is subscripted, the unsubscripted generic type
    #   underlying this subscripted generic (e.g., the type
    #   "pandera.typing.pandas.DataFrame" given the type hint
    #   "pandera.typing.DataFrame[...]").
    hint_type = get_hint_pep484585_generic_unsubbed_type(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

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

    # ....................{ SEARCH                         }....................
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

        # If this module exists...
        if hint_base_module_name:
            # If this module is one of the passed modules, return this
            # superclass as is.
            if hint_base_module_name in module_names:
                # print(f'Found generic {repr(hint)} type {repr(hint_type)} "{module_name}" superclass {repr(hint_base)}!')
                return hint_base
            # Else, this module is *NOT* one of the passed modules. However,
            # this module could still be a transitive submodule of one of the
            # passed packages.

            # Fully-qualified name of the root package transitively defining
            # the submodule declaring this superclass (e.g., "polars" when
            # "hint_base_module_name" is "polars.dataframe").
            #
            # Note this has been profiled to be the fastest one-liner parsing
            # the first "."-suffixed substring from a "."-delimited string.
            hint_base_package_name = hint_base_module_name.partition('.')[0]

            # If this package is one of the passed packages, return this
            # superclass as is.
            if hint_base_package_name in module_names:
                # print(f'Found generic {repr(hint)} type {repr(hint_type)} "{module_name}" superclass {repr(hint_base)}!')
                return hint_base
            # Else, this package is *NOT* one of the passed packages.
        # Else, this module does *NOT* exist.
        #
        # In any case, silently continue to the next superclass.
    # Else, *NO* superclass of this generic resides in the desired module.

    # ....................{ RAISE                          }....................
    # Human-readable double-quoted disjunction of all passed module names (e.g.,
    # '"ibix", "pandas", or "polars"').
    module_names_quoted = join_delimited_disjunction(
        strs=module_names, is_double_quoted=True)

    # Raise an exception of the passed type.
    raise exception_cls(
        f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
        f'type {repr(hint_type)} subclasses no {module_names_quoted} type '
        f'(i.e., type with module name prefixed by {module_names_quoted} not '
        f'found in method resolution order (MRO) {repr(hint_type.__mro__)}).'
    )

# ....................{ GETTERS ~ type                     }....................
#FIXME: Unit test us up, please.
def get_hint_pep484585_generic_unsubbed_type(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> type:
    '''
    Either the passed :pep:`484`- or :pep:`585`-compliant **generic** (i.e.,
    class superficially subclassing at least one PEP-compliant type hint that is
    possibly *not* an actual class) if **unsubscripted** (i.e., indexed by *no*
    arguments or type parameters), the unsubscripted generic underlying this
    generic if **subscripted** (i.e., indexed by one or more child type hints
    and/or type parameters), *or* raise an exception otherwise (i.e., if this
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
    hint : Hint
        Generic type hint to be inspected.
    exception_cls : TypeException, default: BeartypeDecorHintPep484585Exception
        Type of exception to be raised. Defaults to
        :exc:`.BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

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
    :func:`.get_hint_pep484585_generic_unsubbed_type_or_none`
        Further details.
    '''

    # This hint if this hint is an unsubscripted generic, the unsubscripted
    # generic underlying this hint if this hint is a subscripted generic, *OR*
    # "None" if this hint is not a generic.
    hint_generic_type = get_hint_pep484585_generic_unsubbed_type_or_none(hint)

    # If this hint is *NOT* a generic, raise an exception.
    if hint_generic_type is None:
        raise exception_cls(
            f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
            f'not generic (i.e., originates from no isinstanceable class).'
        )
    # Else, this hint is a generic.

    # Return this class.
    return hint_generic_type


def get_hint_pep484585_generic_unsubbed_type_or_none(
    hint: Hint) -> Optional[type]:
    '''
    Either the passed :pep:`484`- or :pep:`585`-compliant **generic** (i.e.,
    class superficially subclassing at least one PEP-compliant type hint that is
    possibly *not* an actual class) if **unsubscripted** (i.e., indexed by *no*
    arguments or type parameters), the unsubscripted generic underlying this
    generic if **subscripted** (i.e., indexed by one or more child type hints
    and/or type parameters), *or* :data:`None` otherwise (i.e., if this hint is
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
    hint : Hint
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


#FIXME: Unit test us up, please.
def get_hint_pep484585_generic_unsubbed_type_isinstanceable(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> type:
    '''
    Either the passed :pep:`484`- or :pep:`585`-compliant **isinstanceable
    generic** (i.e., class superficially subclassing at least one PEP-compliant
    type hint that is possibly *not* an actual class such that this class may be
    passed as the second parameter to the :func:`isinstance` builtin) if
    **unsubscripted** (i.e., indexed by *no* arguments or type parameters), the
    unsubscripted isinstanceable generic underlying this generic if
    **subscripted** (i.e., indexed by one or more child type hints and/or type
    parameters), *or* raise an exception otherwise (i.e., if this hint is *not*
    a generic).

    Although most generics are isinstanceable, some are not. This getter enables
    callers to transparently support the subset of generics that are *not*
    implicitly isinstanceable.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Generic type hint to be inspected.
    exception_cls : TypeException, default: BeartypeDecorHintPep484585Exception
        Type of exception to be raised. Defaults to
        :exc:`.BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    type
        Isinstanceable class originating this generic.

    Raises
    ------
    exception_cls
        If this hint is *not* a generic.

    See Also
    --------
    :func:`.get_hint_pep484585_generic_unsubbed_type`
        Further details.
    '''

    # This hint if this hint is an unsubscripted generic, the unsubscripted
    # generic underlying this hint if this hint is a subscripted generic, *OR*
    # raise an exception if this hint is not a generic.
    hint_generic_type_isinstanceable = get_hint_pep484585_generic_unsubbed_type(
        hint)

    # If the metaclass of this generic bound the __call__() dunder method to a
    # type, *ALL* user-defined instances of this generic are necessarily
    # instances of that type rather than instances of this generic. In this
    # case, assume that type to be isinstanceable. Certainly, this generic
    # itself is unlikely to be isinstanceable. Why? Because of the following
    # PEP-compliant edge cases triggering this condition:
    #
    # * User-defined subclasses inheriting both the PEP 484-compliant
    #   "typing.Generic" superclass *AND* the PEP 589-compliant
    #   "typing.TypedDict" superclass, whose metaclass is the private
    #   "typing._TypedDictMeta" metaclass, which:
    #   * Explicitly prevents these user-defined subclasses from being passed as
    #     the second parameters to the isinstance() and issubclass() builtins.
    #   * Implements the typing._TypedDictMeta.__new__() constructor responsible
    #     for dynamically creating and returning these user-defined subclasses
    #     to forcefully monkey-patch the __call__() dunder method of these
    #     subclasses to refer to the builtin "dict" type. By default, the
    #     __call__() dunder method is bound to the type.__call__() method.
    #     Replacing that method with "dict" ensures that *ALL*
    #     "typing.TypedDict" instances are actually "dict" rather than
    #     "typing.TypedDict" instances.
    if isinstance(hint_generic_type_isinstanceable.__call__, type):  # pyright: ignore
        hint_generic_type_isinstanceable = hint.__call__  # pyright: ignore
        # print(f'generic {hint} hint.__call__ type detected: {hint_isinstanceable}')
    # Else, the metaclass of this generic did *NOT* bind the __call__() dunder
    # method to a type.

    # Return this isinstanceable class.
    return hint_generic_type_isinstanceable
