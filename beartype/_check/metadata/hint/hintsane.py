#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype sanified type hint metadata dataclass** (i.e., class aggregating
*all* metadata returned by :mod:`beartype._check.convert.convsanify` functions).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeDecorHintSanifyException
from beartype.typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Set,
    Tuple,
    Union,
)
from beartype._data.hint.datahintpep import (
    FrozenSetHints,
    Hint,
    TypeVarToHint,
)
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._data.kind.datakindset import FROZENSET_EMPTY
from beartype._util.kind.map.utilmapfrozen import FrozenDict
from beartype._util.utilobjmake import permute_object

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
        parent hints (i.e., supporting recursion) of this hint). If the a
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
    def permute(self, **kwargs) -> 'HintSane':
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
