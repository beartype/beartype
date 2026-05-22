#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking type hint abstract base classes (ABCs)** (i.e.,
superclasses whose subclasses store metadata describing each iteration of a
recursive traversal over an abstract tree of child type hints transitively
subscripting a root type hint annotating an external objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import ABCMeta
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.cls.hint.hintsane import HintSane
from beartype._data.hint.sign.datahintsigncls import HintSign
from typing import (
    TYPE_CHECKING,
    Optional,
)

# ....................{ SUPERCLASSES                       }....................
#FIXME: Unit test us up, please.
class HintDataABC(metaclass=ABCMeta):
    '''
    **Type-checking type hint abstract base class (ABC)** (i.e., superclass
    whose subclasses store metadata describing each iteration of a recursive
    traversal over an abstract tree of child type hints transitively
    subscripting a root type hint annotating an external objects).

    Attributes
    ----------
    hint_sane : HintSane
        **Sanified type hint metadata** (i.e., immutable and thus hashable
        object encapsulating *all* metadata returned by
        :mod:`beartype._check.convert.convmain` sanifiers after sanitizing
        this possibly PEP-noncompliant hint into a fully PEP-compliant hint)
        describing the type hint currently visited by this BFS.
    hint_sign : Optional[HintSign]
        Either:

        * If this hint is PEP-compliant, the **sign** (i.e., singleton instance
          of the :class:`.HintSign` class) uniquely identifying this hint.
        * Else, :data:`None`.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'hint_sane',
        'hint_sign',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        hint_sane: HintSane
        hint_sign: Optional[HintSign]

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        hint_sane: HintSane,
        hint_sign: Optional[HintSign],
    ) -> None:
        '''
        Initialize this type-checking type hint metadata.

        Parameters
        ----------
        See the class docstring for a description of all passed parameters.
        '''
        assert isinstance(hint_sane, HintSane), (
            f'{repr(hint_sane)} not sanified hint metadata.')
        assert isinstance(hint_sign, NoneTypeOr[HintSign]), (
            f'{repr(hint_sign)} neither hint sign nor "None".')

        # Classify all passed parameters.
        self.hint_sane = hint_sane
        self.hint_sign = hint_sign
