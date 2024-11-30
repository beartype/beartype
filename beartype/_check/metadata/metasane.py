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
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10

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
PEP-compliant type hint matching either a type hint *or* sanified type hint
metadata.
'''

# ....................{ GETTERS                            }....................
# def get_hint_sanified_tuple(
#     hint_or_data: HintOrHintSanifiedData) -> Tuple[Hint, TypeVarToHint]:
#     '''
#     2-tuple ``(hint, typevar_to_hint)`` unpacked from the passed ``hint``
#     parameter if that parameter is a :class:`.HintSanifiedData` object *or*
#     trivially referring to the passed ``hint`` and ``conf`` parameters otherwise
#     (i.e., if the passed ``hint`` parameter is *not* a
#     :class:`.HintSanifiedData` object).
#     '''
#
#     return (
#         (hint_data.hint, hint_data.conf)
#         if isinstance(hint_data, HintSanifiedData) else
#         (hint, conf)
#     )
