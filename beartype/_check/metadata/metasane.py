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
    Iterable,
    List,
    Set,
    Tuple,
    Union,
)
from beartype._data.hint.datahintpep import (
    Hint,
    TypeVarToHint,
)
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._util.kind.map.utilmapfrozen import FrozenDict
from beartype._util.utilobjmake import permute_object

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please.
class HintSanifiedData(object):
    '''
    **Beartype sanified type hint metadata** (i.e., immutable and thus hashable
    object encapsulating *all* metadata returned by
    :mod:`beartype._check.convert.convsanify` functions after sanitizing a
    possibly PEP-noncompliant type hint into a fully PEP-compliant type hint).

    For efficiency, these functions only conditionally return this metadata for
    the proper subset of type hints that actually modify this metadata; since
    most type hints do *not* modify this metadata, these functions typically
    only return the sanified type hint (rather than both that hint and all of
    this other ancillary metadata).

    Attributes
    ----------
    hint : Hint
        Type hint sanified (i.e., sanitized) from a possibly insane type hint
        into a hopefully sane type hint by a
        :mod:`beartype._check.convert.convsanify` function.
    typevar_to_hint : TypeVarToHint
        **Type variable lookup table** describing this type hint, defined as an
        immutable dictionary mapping from the :pep:`484`-compliant **type
        variables** (i.e., :class:`typing.TypeVar` objects) originally
        parametrizing the origin of this type hint if any to the corresponding
        child type hints subscripting this type hint.
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
        'typevar_to_hint',
        '_hash',
    )


    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        hint: Hint
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
        typevar_to_hint : TypeVarToHint, optional
            **Type variable lookup table** describing this type hint, defined as
            an immutable dictionary mapping from the :pep:`484`-compliant **type
            variables** (i.e., :class:`typing.TypeVar` objects) originally
            parametrizing the origin of this type hint if any to the
            corresponding child type hints subscripting this type hint. Defaults
            to the empty table.
        '''
        assert isinstance(typevar_to_hint, FrozenDict), (
            f'{repr(typevar_to_hint)} not frozen dictionary.')

        # Classify all passed parameters as instance variables.
        self.hint = hint
        self.typevar_to_hint = typevar_to_hint

        # Hash identifying this object, precomputed for efficiency.
        self._hash = hash((hint, typevar_to_hint))

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
                self.typevar_to_hint == other.typevar_to_hint
            )
            if isinstance(other, HintSanifiedData) else
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
            f'typevar_to_hint={repr(self.typevar_to_hint)}'
            f')'
        )

    # ..................{ PERMUTERS                          }..................
    def permute(self, **kwargs) -> 'HintSanifiedData':
        '''
        Shallow copy of this metadata such that each passed keyword parameter
        overwrites the instance variable of the same name in this copy.

        Parameters
        ----------
        Keyword parameters of the same name and type as instance variables of
        this object (e.g., ``hint: Hint``, ``typevar_to_hint: TypeVarToHint``).

        Returns
        -------
        HintSanifiedData
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

# ....................{ HINTS                              }....................
HintOrHintSanifiedData = Union[Hint, HintSanifiedData]
'''
PEP-compliant type hint matching either a type hint *or* **sanified type hint
metadata** (i.e., :class:`.HintSanifiedData` object).
'''


HintOrHintSanifiedDataUnpacked = Tuple[Hint, TypeVarToHint]
'''
PEP-compliant type hint matching a 2-tuple ``(hint, typevar_to_hint)`` as
returned by the :func:`.unpack_hint_or_sane` unpacker.
'''


IterableHintOrHintSanifiedData = Iterable[HintOrHintSanifiedData]
'''
PEP-compliant type hint matching an iterable of zero or more items, each of
which is either a type hint *or* **sanified type hint metadata** (i.e.,
:class:`.HintSanifiedData` object).
'''


ListHintOrHintSanifiedData = List[HintOrHintSanifiedData]
'''
PEP-compliant type hint matching a list of zero or more items, each of which is
either a type hint *or* **sanified type hint metadata** (i.e.,
:class:`.HintSanifiedData` object).
'''


SetHintOrHintSanifiedData = Set[HintOrHintSanifiedData]
'''
PEP-compliant type hint matching a set of zero or more items, each of which is
either a type hint *or* **sanified type hint metadata** (i.e.,
:class:`.HintSanifiedData` object).
'''


TupleHintOrHintSanifiedData = Tuple[HintOrHintSanifiedData, ...]
'''
PEP-compliant type hint matching a tuple of zero or more items, each of which is
either a type hint *or* **sanified type hint metadata** (i.e.,
:class:`.HintSanifiedData` object).
'''

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_hint_or_sane_hint(hint_or_sane: HintOrHintSanifiedData) -> Hint:
    '''
    Hint unpacked (i.e., coerced, converted) from the passed parameter.

    Caveats
    -------
    This getter effectively discards *all* supplementary metadata recorded with
    this parameter -- including any type variable lookup table associated with
    this child hint.

    Parameters
    ----------
    hint_or_sane : HintSanifiedData
        Either a type hint *or* **sanified type hint metadata** (i.e.,
        :class:`.HintSanifiedData` object) to be unpacked.

    Returns
    -------
    Hint
        Hint unpacked (i.e., coerced, converted) from this parameter.
    '''

    # Return the hint encapsulated by this metadata.
    return (
        hint_or_sane.hint
        if isinstance(hint_or_sane, HintSanifiedData) else
        hint_or_sane
    )

# ....................{ UNPACKERS                          }....................
#FIXME: Unit test us up, please.
def unpack_hint_or_sane(
    # Mandatory parameters.
    hint_or_sane: HintOrHintSanifiedData,

    # Optional parameters.
    typevar_to_hint: TypeVarToHint = FROZENDICT_EMPTY,
) -> HintOrHintSanifiedDataUnpacked:
    '''
    2-tuple ``(hint, typevar_to_hint)`` unpacked from the passed parameters.

    This low-level utility function "unpacks" (i.e., coerces, converts) the
    passed type hint and type variable lookup table.

    Parameters
    ----------
    hint_or_sane : HintSanifiedData
        Either a type hint *or* **sanified type hint metadata** (i.e.,
        :class:`.HintSanifiedData` object) to be unpacked.
    typevar_to_hint : TypeVarToHint
        **Type variable lookup table** (i.e., immutable dictionary mapping from
        the :pep:`484`-compliant **type variables** (i.e.,
        :class:`typing.TypeVar` objects) originally parametrizing the origins of
        all transitive parent hints of this hint to the corresponding child
        hints subscripting these parent hints). Defaults to
        :class:`.FROZENDICT_EMPTY`.

    Returns
    -------
    Tuple[Hint, TypeVarToHint]
        2-tuple ``(hint, typevar_to_hint)`` where:

        * ``hint`` is the hint encapsulated by the passed parameters.
        * ``typevar_to_hint`` is the type variable lookup table encapsulated by
          the passed parameters. If the pair of type variable lookup tables
          encapsulated by both the passed ``typevar_to_hint`` parameter *and*
          ``hint_or_sane.typevar_to_hint`` instance variable are non-empty, then
          this ``typevar_to_hint`` item of this 2-tuple is a new type variable
          lookup table efficiently merging this parameter and instance variable
          (in that order).
    '''
    assert isinstance(typevar_to_hint, FrozenDict), (
        f'{repr(typevar_to_hint)} not frozen dictionary.')

    # If reducing this hint generated supplementary metadata...
    if isinstance(hint_or_sane, HintSanifiedData):
        # This lower-level hint reduced from this higher-level hint.
        hint = hint_or_sane.hint

        # If reducing this hint generated a non-empty type variable lookup
        # table...
        if hint_or_sane.typevar_to_hint:
            # If the caller passed an empty type variable lookup table,
            # trivially replace the latter with the former.
            if not typevar_to_hint:
                typevar_to_hint = hint_or_sane.typevar_to_hint
            else:
                # Full type variable lookup table uniting...
                typevar_to_hint = (
                    # The type variable lookup table describing all
                    # transitive parent hints of this reduced hint *AND*...
                    typevar_to_hint |  # type: ignore[operator]
                    # The type variable lookup table describing this hint.
                    #
                    # Note that this table is intentionally the second
                    # rather than first operand of this "|" operation,
                    # efficiently ensuring that type variables mapped by
                    # this hint take precedence over type variables mapped
                    # by transitive parent hints of this hint.
                    hint_or_sane.typevar_to_hint
                )
        # Else, reducing this hint generated an empty type variable lookup
        # table. In this case, this table is ignorable.
    # Else, reducing this hint did *NOT* generate supplementary metadata. In
    # this case, preserve this reduced hint as is.
    else:
        hint = hint_or_sane

    # Return the 2-tuple containing this hint and type variable lookup table.
    return (hint, typevar_to_hint)
