#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype sanified type hint metadata dataclass** (i.e., class aggregating
*all* metadata returned by :mod:`beartype._check.convert.convsanify` functions).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    TYPE_CHECKING,
    Tuple,
    Union,
)
from beartype._data.hint.datahintpep import (
    Hint,
    TypeVarToHint,
)
from beartype._util.kind.map.utilmapfrozen import (
    FROZEN_DICT_EMPTY,
    FrozenDict,
)

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
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'hint',
        'typevar_to_hint',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        hint: Hint
        typevar_to_hint: TypeVarToHint

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        hint: Hint,

        # Optional parameters.
        typevar_to_hint: TypeVarToHint = FROZEN_DICT_EMPTY,
    ) -> None:
        '''
        Initialize this metadata with the passed parameters.

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

# ....................{ HINTS                              }....................
HintOrHintSanifiedData = Union[Hint, HintSanifiedData]
'''
PEP-compliant type hint matching either a type hint *or* **sanified type hint
metadata** (i.e., :class:`.HintSanifiedData` object).
'''


HintOrHintSanifiedDataUnpacked = Tuple[Hint, TypeVarToHint]
'''
PEP-compliant type hint matching a 2-tuple ``(hint, typevar_to_hint)`` as
returned by the :func:`.unpack_hint_or_data` unpacker.
'''

# ....................{ UNPACKERS                          }....................
#FIXME: Unit test us up, please.
def unpack_hint_or_data(
    # Mandatory parameters.
    hint_or_data: HintOrHintSanifiedData,

    # Optional parameters.
    typevar_to_hint: TypeVarToHint = FROZEN_DICT_EMPTY,
) -> HintOrHintSanifiedDataUnpacked:
    '''
    2-tuple ``(hint, typevar_to_hint)`` unpacked from the passed parameters.

    This low-level utility function "unpacks" (i.e., coerces, converts) the
    passed type hint and type variable lookup table.

    Parameters
    ----------
    hint_or_data : HintSanifiedData
        Either a type hint *or* **sanified type hint metadata** (i.e.,
        :class:`.HintSanifiedData` object) to be unpacked.
    typevar_to_hint : TypeVarToHint
        **Type variable lookup table** (i.e., immutable dictionary mapping from
        the :pep:`484`-compliant **type variables** (i.e.,
        :class:`typing.TypeVar` objects) originally parametrizing the origins of
        all transitive parent hints of this hint to the corresponding child
        hints subscripting these parent hints). Defaults to
        :class:`.FROZEN_DICT_EMPTY`.

    Returns
    -------
    Tuple[Hint, TypeVarToHint]
        2-tuple ``(hint, typevar_to_hint)`` where:

        * ``hint`` is the hint encapsulated by the passed parameters.
        * ``typevar_to_hint`` is the type variable lookup table encapsulated by
          the passed parameters. If the pair of type variable lookup tables
          encapsulated by both the passed ``typevar_to_hint`` parameter *and*
          ``hint_or_data.typevar_to_hint`` instance variable are non-empty, then
          this ``typevar_to_hint`` item of this 2-tuple is a new type variable
          lookup table efficiently merging this parameter and instance variable
          (in that order).
    '''
    assert isinstance(typevar_to_hint, FrozenDict), (
        f'{repr(typevar_to_hint)} not frozen dictionary.')

    # If reducing this hint generated supplementary metadata...
    if isinstance(hint_or_data, HintSanifiedData):
        # This lower-level hint reduced from this higher-level hint.
        hint = hint_or_data.hint

        # If reducing this hint generated a non-empty type variable lookup
        # table...
        if hint_or_data.typevar_to_hint:
            # If the caller passed an empty type variable lookup table,
            # trivially replace the latter with the former.
            if not typevar_to_hint:
                typevar_to_hint = hint_or_data.typevar_to_hint
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
                    hint_or_data.typevar_to_hint
                )
        # Else, reducing this hint generated an empty type variable lookup
        # table. In this case, this table is ignorable.
    # Else, reducing this hint did *NOT* generate supplementary metadata. In
    # this case, preserve this reduced hint as is.
    else:
        hint = hint_or_data

    # Return the 2-tuple containing this hint and type variable lookup table.
    return (hint, typevar_to_hint)
