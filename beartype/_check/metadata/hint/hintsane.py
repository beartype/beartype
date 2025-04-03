#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype sanified type hint metadata dataclass** (i.e., class aggregating
*all* metadata returned by :mod:`beartype._check.convert.convsanify` functions).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: [SPACE] Memoize the HintSane.__new__() or __init__() constructors. In
#theory, we dimly recall already defining a caching metaclass somewhere in the
#codebase. Perhaps we can simply leverage that to get this trivially done?
#
#Note, however, that keyword arguments will be an issue. We currently
#instantiate "HintSane" objects throughout the codebase by passing keyword
#arguments -- which clearly conflict with memoization. That said, preserving
#keyword argument passing would be *EXTREMELY* beneficial here. Without keyword
#arguments, we lose the flexibility that keyword arguments enable -- especially
#with respect to adding new keyword arguments at some future date.
#
#Perhaps that aforementioned caching metaclass could be augmented to support
#keyword arguments? That would still be better than nothing.
#FIXME: When memoizing, only memoize *CONDITIONALLY.* Notably, there exist two
#common cases here:
#* Context-free "HintSane" instances are initialized with *ONLY* a "hint". They
#  lack contextual metadata and are thus context-free. Unsurprisingly,
#  context-free "HintSane" instances are readily memoizable.
#* Contextual "HintSane" instances are initialized with both a "hint" and one or
#  more supplemental parameters supplying contextual metadata (e.g.,
#  "recursable_hints", "typevar_to_hint"). They are *NOT* context-free. Ergo,
#  contextual "HintSane" instances are *NOT* readily memoizable. Don't even
#  bother wasting space or time attempting to do so.

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeDecorHintSanifyException
from beartype.typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._data.hint.datahintpep import (
    FrozenSetHints,
    Hint,
    TypeVarToHint,
)
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._data.kind.datakindset import FROZENSET_EMPTY
from beartype._util.kind.map.utilmapfrozen import FrozenDict
from beartype._util.utilobjmake import permute_object
from beartype._util.utilobject import (
    SENTINEL,
    Iota,
)

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please.
class HintSane(object):
    '''
    **Sanified type hint metadata** (i.e., immutable and thus hashable object
    encapsulating *all* metadata returned by
    :mod:`beartype._check.convert.convsanify` sanifiers after sanitizing a
    possibly PEP-noncompliant hint into a fully PEP-compliant hint).

    For efficiency, sanifiers only conditionally return this metadata for the
    proper subset of hints associated with this metadata; since most hints are
    *not* associated with this metadata, sanifiers typically only return a
    sanified type hint (rather than both that hint *and* this metadata).

    Caveats
    -------
    **Callers should avoid modifying this metadata.** For efficiency, this class
    does *not* explicitly prohibit modification of this metadata. Nonetheless,
    this class is implemented under the assumption that callers *never* modify
    this metadata. This metadata is effectively frozen. Any attempts to modify
    this metadata *will* induce nondeterminism throughout :mod:`beartype`,
    especially in memoized callables accepting and/or returning this metadata.

    Attributes
    ----------
    hint : Hint
        Type hint sanified (i.e., sanitized) from a possibly insane type hint
        into a hopefully sane type hint by a
        :mod:`beartype._check.convert.convsanify` function.
    recursable_hints : FrozenSetHints
        **Recursion guard** (i.e., frozen set of all transitive recursable
        parent hints (i.e., supporting recursion) of this hint). If the
        subsequently visited child hint subscripting this hint already resides
        in this recursion guard, that child hint has already been visited by
        prior iteration and is thus a recursive hint. Since recursive hints are
        valid (rather than constituting an unexpected error), the caller is
        expected to detect this use case and silently short-circuit infinite
        recursion by avoiding revisiting that already visited recursive hint.
    typevar_to_hint : TypeVarToHint
        **Type variable lookup table** (i.e., immutable dictionary mapping from
        the **type variables** (i.e., :pep:`484`-compliant
        :class:`typing.TypeVar` objects) originally parametrizing the origins of
        all transitive parent hints of this hint if any to the corresponding
        child hints subscripting those parent hints). This table enables
        :func:`beartype.beartype` to efficiently reduce a proper subset of type
        variables to non-type variables at decoration time, including:

        * :pep:`484`- or :pep:`585`-compliant **subscripted generics.** For
          example, this table enables runtime type-checkers to reduce the
          semantically useless pseudo-superclass ``list[T]`` to the
          semantically useful pseudo-superclass ``list[int]`` at decoration time
          in the following example:

          .. code-block:: python

             class MuhGeneric[T](list[T]): pass

             @beartype
             def muh_func(muh_arg: MuhGeneric[int]) -> None: pass

        * :pep:`695`-compliant **subscripted type aliases.** For example, this
          table enables runtime type-checkers to reduce the semantically useless
          type hint ``muh_type_alias[float]`` to the semantically useful type
          hint ``float | int`` at decoration time in the following example:

          .. code-block:: python

             type muh_type_alias[T] = T | int

             @beartype
             def muh_func(muh_arg: muh_type_alias[float]) -> None: pass
    _hash : int
        Hash identifying this object, precomputed for efficiency.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'hint',
        'recursable_hints',
        'typevar_to_hint',
        '_hash',
    )


    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        hint: Hint
        recursable_hints: FrozenSetHints
        typevar_to_hint: TypeVarToHint


    _INIT_PARAM_NAMES = frozenset((
        var_name
        for var_name in __slots__
        # Ignore private slotted instance variables defined above.
        if not var_name.startswith('_')
    ))
    '''
    Frozen set of the names of all parameters accepted by the :meth:`init`
    method, defined as the frozen set comprehension of all public slotted
    instance variables of this class.

    This frozen set enables efficient membership testing.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        hint: Hint,

        # Optional parameters.
        recursable_hints: FrozenSetHints = FROZENSET_EMPTY,
        typevar_to_hint: TypeVarToHint = FROZENDICT_EMPTY,
    ) -> None:
        '''
        Initialize this sanified type hint metadata with the passed parameters.

        Parameters
        ----------
        hint : Hint
            Type hint sanified (i.e., sanitized) from a possibly insane type
            hint into a hopefully sane type hint by a
            :mod:`beartype._check.convert.convsanify` function.
        recursable_hints : FrozenSetHints, optional
            **Recursion guard** (i.e., frozen set of all transitive recursable
            parent hints (i.e., supporting recursion) of this hint). Defaults to
            the empty frozen set.
        typevar_to_hint : TypeVarToHint, optional
            **Type variable lookup table** (i.e., immutable dictionary mapping
            from the **type variables** (i.e., :pep:`484`-compliant
            :class:`typing.TypeVar` objects) originally parametrizing the
            origins of all transitive parent hints of this hint if any to the
            corresponding child hints subscripting those parent hints). Defaults
            to the empty frozen dictionary.
        '''
        assert isinstance(recursable_hints, frozenset), (
            f'{repr(recursable_hints)} not frozen set.')
        assert isinstance(typevar_to_hint, FrozenDict), (
            f'{repr(typevar_to_hint)} not frozen dictionary.')

        # Classify all passed parameters as instance variables.
        self.hint = hint
        self.recursable_hints = recursable_hints
        self.typevar_to_hint = typevar_to_hint

        # Hash identifying this object, precomputed for efficiency.
        self._hash = hash((hint, recursable_hints, typevar_to_hint))

    # ..................{ DUNDERS                            }..................
    def __hash__(self) -> int:
        '''
        Hash identifying this sanified type hint metadata.

        Returns
        -------
        int
            This hash.
        '''

        return self._hash


    def __eq__(self, other: object) -> bool:
        '''
        :data:`True` only if this sanified type hint metadata is equal to the
        passed arbitrary object.

        Parameters
        ----------
        other : object
            Arbitrary object to be compared for equality against this metadata.

        Returns
        -------
        Union[bool, type(NotImplemented)]
            Either:

            * If this other object is also sanified type hint metadata, either:

              * If these metadatum share equal instance variables, :data:`True`.
              * Else, :data:`False`.

            * Else, :data:`NotImplemented`.
        '''

        # Return either...
        return (
            # If this other object is also sanified hint metadata, true only
            # if these metadatum share the same instance variables;
            (
                self.hint == other.hint and
                self.recursable_hints == other.recursable_hints and
                self.typevar_to_hint == other.typevar_to_hint
            )
            if isinstance(other, HintSane) else
            # Else, this other object is *NOT* also sanified hint metadata. In
            # this case, the standard singleton informing Python that this
            # equality comparator fails to support this comparison.
            NotImplemented  # type: ignore[return-value]
        )


    def __repr__(self) -> str:
        '''
        Machine-readable representation of this metadata.
        '''

        # If this metadata is the ignorable "HINT_IGNORABLE" singleton,
        # trivially return the unqualified basename of this singleton for
        # debuggability, disambiguity, and readability.
        if self is HINT_IGNORABLE:
            return 'HINT_IGNORABLE'
        # Else, this metadata is *NOT* the ignorable "HINT_IGNORABLE" singleton.

        # Represent this metadata with just the minimal subset of metadata
        # needed to reasonably describe this metadata.
        return (
            f'{self.__class__.__name__}('
            f'hint={repr(self.hint)}, '
            f'recursable_hints={repr(self.recursable_hints)}, '
            f'typevar_to_hint={repr(self.typevar_to_hint)}'
            f')'
        )

    # ..................{ PERMUTERS                          }..................
    def permute_sane(self, **kwargs) -> 'HintSane':
        '''
        Shallow copy of this metadata such that each passed keyword parameter
        overwrites the instance variable of the same name in this copy.

        Parameters
        ----------
        Keyword parameters of the same name and type as instance variables of
        this object (e.g., ``hint: Hint``, ``typevar_to_hint: TypeVarToHint``).

        Returns
        -------
        HintSane
            Shallow copy of this metadata such that each keyword parameter
            overwrites the instance variable of the same name in this copy.

        Raises
        ------
        _BeartypeDecorHintSanifyException
            If the name of any passed keyword parameter is *not* that of an
            existing instance variable of this object.
        '''

        # Set us up the permutation! Make your time!
        return permute_object(
            obj=self,
            init_arg_name_to_value=kwargs,
            init_arg_names=self._INIT_PARAM_NAMES,
            exception_cls=_BeartypeDecorHintSanifyException,
        )

# ....................{ GLOBALS                            }....................
HINT_IGNORABLE = HintSane(hint=Any)
'''
**Ignorable sanified type hint metadata** (i.e., singleton :class:`.HintSign`
instance to which *all* deeply or shallowly ignorable type hints are reduced by
:mod:`beartype._check.convert.convsanify` sanifiers).

This singleton enables callers to trivially differentiate ignorable from
unignorable hints. After sanification, if a hint is sanified to:

* Literally this singleton, then that hint is ignorable.
* Any other object, then that hint is unignorable.
'''

# ....................{ HINTS                              }....................
HintOrSane = Union[Hint, HintSane]
'''
PEP-compliant type hint matching either a type hint *or* **sanified type hint
metadata** (i.e., :class:`.HintSane` object).
'''

# ....................{ HINTS ~ container                  }....................
DictHintSaneToAny = Dict[HintSane, Any]
'''
PEP-compliant type hint matching a dictionary mapping from keys that are
**sanified type hint metadata** (i.e., :class:`.HintSane` objects) to arbitrary
objects.
'''


IterableHintSane = Iterable[HintSane]
'''
PEP-compliant type hint matching an iterable of zero or more **sanified type
hint metadata** (i.e., :class:`.HintSane` objects).
'''


ListHintOrSane = List[HintOrSane]
'''
PEP-compliant type hint matching a list of zero or more items, each of which is
either a type hint *or* **sanified type hint metadata** (i.e.,
:class:`.HintSane` object).
'''


ListHintSane = List[HintSane]
'''
PEP-compliant type hint matching a list of zero or more **sanified type hint
metadata** (i.e., :class:`.HintSane` objects).
'''


SetHintSane = Set[HintSane]
'''
PEP-compliant type hint matching a set of zero or more **sanified type hint
metadata** (i.e., :class:`.HintSane` objects).
'''


TupleHintSane = Tuple[HintSane, ...]
'''
PEP-compliant type hint matching a tuple of zero or more **sanified type hint
metadata** (i.e., :class:`.HintSane` objects).
'''

# ....................{ TESTERS                            }....................
#FIXME: Shift all of the following utility functions into a more appropriate
#submodule -- say:
#* Create a new "beartype._check.util" subpackage.
#* Shift existing the "beartype._check" subpackages and submodules into
#  "beartype._check.util": e.g.,
#  * Shift the "beartype._check.checkcache" subpackage to
#    "beartype._check.util.checkutilcache".
#  * Shift the "beartype._check.signature" subpackage to
#    "beartype._check.util.signature".
#* Create a new "beartype._check.util.checkutilrecursion" submodule.
#* Shift all of these utility functions into that submodule.

#FIXME: Unit test us up, please.
def is_hint_recursive(
    hint: Hint, hint_parent_sane: Optional[HintSane]) -> bool:
    '''
    :data:`True` only if the passed **recursable type hint** (i.e., type hint
    implicitly supporting recursion like, say, a :pep:`695`-compliant type
    alias) is actually **recursive** (i.e., has already been visited by the
    current breadth-first search (BFS) over all type hints transitively nested
    in some root type hint) with respect to the passed previously sanified
    metadata for the parent type hint of the passed type hint.

    Caveats
    -------
    **This tester assumes this hint to be hashable.** Although *most*
    PEP-compliant hints are hashable, some are not (e.g., :pep:`593`-compliant
    metahints annotated by unhashable objects like ``typing.Annotated[object,
    []]``). Callers that cannot guarantee this hint to be hashable should
    protect calls to this tester inside a ``try`` block explicitly catching the
    :exc:`TypeError` exception this tester raises when this hint is unhashable:

    .. code-block:: python

       # Attempt to test whether hint is recursive or not.
       try:
           if is_hint_recursive(hint=hint, hint_parent_sane=hint_parent_sane):
               pass
       # If doing so raises a "TypeError", this hint is unhashable and thus
       # inapplicable for hint recursion. In this case, ignore this hint.
       except TypeError:
           pass

    Parameters
    ----------
    hint : Hint
        Recursable type hint to be inspected.
    hint_parent_sane : Optional[HintSane]
        Either:

        * If this recursable type hint is a root type hint, :data:`None`.
        * Else, **sanified parent type hint metadata** (i.e., immutable and thus
          hashable object encapsulating *all* metadata previously returned by
          :mod:`beartype._check.convert.convsanify` sanifiers after sanitizing
          the possibly PEP-noncompliant parent hint of this hint into a fully
          PEP-compliant parent hint).

    Returns
    -------
    bool
        :data:`True` only if this recursable type hint is recursive.

    Raises
    ------
    TypeError
        If this hint is unhashable.
    '''
    assert isinstance(hint_parent_sane, NoneTypeOr[HintSane]), (
        f'{repr(hint_parent_sane)} neither sanified hint metadata nor "None".')

    # True only if...
    is_hint_recursive_state = (
        # This hint has a parent *AND*...
        hint_parent_sane is not None and
        # This hint is a transitive parent of itself.
        hint in hint_parent_sane.recursable_hints
    )
    # print(f'Hint {hint} with parent {hint_parent_sane} recursive? {is_hint_recursive_state}')

    # Return this boolean.
    return is_hint_recursive_state

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_hint_sane_recursable(
    # Mandatory parameters.
    hint_recursable: Hint,
    hint_parent_sane: Optional[HintSane],

    # Optional parameters.
    hint_nonrecursable: Union[Hint, Iota] = SENTINEL,
) -> HintSane:
    '''
    **Sanified type hint metadata** (i.e., :class:`.HintSane` object) safely
    encapsulating both the passed **recursable type hint** (i.e., type hint
    implicitly supporting recursion like, say, a :pep:`695`-compliant type
    alias) and the passed metadata encapsulating the previously sanified parent
    type hint of the passed type hint.

    This factory creates and returns metadata protecting this recursable type
    hint against infinite recursion. Notably, this factory adds this hint to the
    :attr:`HintSane.recursable_hints` instance variable of this metadata
    implementing the recursion guard for this hint.

    Parameters
    ----------
    hint_recursable : Hint
        Recursable type hint to be added to the
        :attr:`.HintSane.recursable_hints` frozen set of the returned metadata.
    hint_parent_sane : Optional[HintSane]
        Either:

        * If this recursable type hint is a root type hint, :data:`None`.
        * Else, **sanified parent type hint metadata** (i.e., immutable and thus
          hashable object encapsulating *all* metadata previously returned by
          :mod:`beartype._check.convert.convsanify` sanifiers after sanitizing
          the possibly PEP-noncompliant parent hint of this hint into a fully
          PEP-compliant parent hint).
    hint_nonrecursable : Union[Hint, Iota]
        Non-recursable type hint to be encapsulated if this type hint has both
        recursable and non-recursable forms describing this type hint. The
        distinction is as follows:

        * The recursable form of this type hint (passed as the mandatory
          ``hint_recursable`` parameter) is the variant of this hint that will
          be subsequently passed to the :func:`.is_hint_recursive` tester to
          detect whether this hint has already been recursively visited or not.
        * The non-recursable form of this type hint (passed as this optional
          ``hint_nonrecursable`` parameter) is the variant of this hint that
          will be encapsulated as the :attr:`.HintSane.hint` instance variable
          of the returned metadata. This non-recursable form is typically the
          post-sanified hint produced by sanifying the recursable form of the
          pre-sanified hint passed as the ``hint_recursable`` parameter.

        Defaults to the sentinel placeholder, in which case this parameter
        actually defaults to the passed ``hint_recursable`` parameter. This
        default suffices for the common case in which the recursable and
        non-recursable forms of a type hint are exactly the same.

    Returns
    -------
    HintSane
        Sanified metadata encapsulating both:

        * This recursable type hint.
        * This sanified parent type hint metadata.
    '''
    assert isinstance(hint_parent_sane, NoneTypeOr[HintSane]), (
        f'{repr(hint_parent_sane)} neither sanified hint metadata nor "None".')

    # Sanified metadata to be returned.
    hint_sane: HintSane = None  # type: ignore[assignment]

    # If the caller passed *NO* non-recursable form of this hint, default this
    # form to the passed recursable form of this hint.
    if hint_nonrecursable is SENTINEL:
        hint_nonrecursable = hint_recursable
    # Else, the caller passed a non-recursable form of this hint. Preserve this
    # form as is.

    # Recursion guard containing *ONLY* this pre-sanified unsubscripted hint
    # (which is what the initial recursion logic above will then subsequently
    # test against if this a recursive alias).
    recursable_hints = frozenset((hint_recursable,))

    # If this hint has *NO* parent, this is a root hint. In this case...
    if hint_parent_sane is None:
        # Metadata encapsulating this hint and recursion guard containing *ONLY*
        # this pre-sanified unsubscripted hint (which is what the initial
        # recursion logic above will then subsequently test against if this a
        # recursive alias).
        hint_sane = HintSane(
            hint=hint_nonrecursable, recursable_hints=recursable_hints)
    # Else, this hint has a parent. In this case...
    else:
        # If the parent hint is also associated with a recursion guard...
        if hint_parent_sane.recursable_hints:
            # Full recursion guard merging the guard associated this parent hint
            # with the guard containing only this child hint, efficiently
            # defined as...
            recursable_hints = (
                # The guard protecting all transitive parent hints of this hint
                # with...
                hint_parent_sane.recursable_hints |  # type: ignore[operator]
                # The guard protecting this hint. Note that the order of
                # operands in this "|" operation is insignificant.
                recursable_hints
            )
        # Else, the parent hint is associated with *NO* such guard.

        # Metadata encapsulating this hint and recursion guard, while
        # "cascading" any other metadata associated with this parent hint (e.g.,
        # type variable lookup table) down onto this child hint as well.
        hint_sane = hint_parent_sane.permute_sane(
            hint=hint_nonrecursable, recursable_hints=recursable_hints)

    # Return this underlying type hint.
    return hint_sane
