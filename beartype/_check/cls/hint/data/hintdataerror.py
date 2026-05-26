#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **exception-generating type hint dataclasses** (i.e., low-level classes
fabricating human-readable strings and associated metadata detailing why the
currently type-checked objects violate the type hints annotating those objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.hint.data.hintdataabc import HintDataABC
from beartype._check.cls.hint.hintsane import HintSane
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatyping import HintSignOrNoneOrSentinel
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

# ....................{ SUBCLASSES                         }....................
#FIXME: Unit test us up, please.
class HintDataError(HintDataABC):
    '''
    **Exception-generating type hint dataclass** (i.e., low-level class
    fabricating human-readable strings and associated metadata detailing why the
    currently type-checked object violates the type hint annotating that
    object).

    Instances of this lower-level dataclass are bound to the
    :attr:`beartype._check.cls.hint.tree.hinttreeerror.HintTreeError.hint_curr`
    instance variable of the higher-level parent
    :class:`beartype._check.cls.hint.tree.hinttreeerror.HintTreeError` dataclass
    iterating over all such instances for a given type hint tree.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        hint_sane: HintSane,

        # Optional parameters.
        hint_sign: HintSignOrNoneOrSentinel = SENTINEL,
    ) -> None:
        '''
        Initialize this exception-generating type hint metadata.

        Parameters
        ----------
        hint_sane : HintSane
            **Sanified type hint metadata** (i.e., immutable and thus hashable
            object encapsulating *all* metadata returned by
            :mod:`beartype._check.convert.convmain` sanifiers after sanitizing
            this possibly PEP-noncompliant hint into a fully PEP-compliant hint)
            describing the currently visited type hint.
        hint_sign : Union[Optional[HintSign], Iota], default: SENTINEL
            Either:

            * If this child hint is uniquely identified by a **non-default
              sign** (i.e., a singleton instance of the :class:`.HintSign` class
              *other* than the standard sign returned by the
              :func:`.get_hint_pep_sign_or_none` getter), this sign.
            * Else, the sentinel placeholder, in which case this parameter
              defaults to the **default sign** (i.e., the standard sign returned
              by the :func:`.get_hint_pep_sign_or_none` getter).

            Defaults to the sentinel placeholder. This parameter should
            typically *not* be passed. Almost all hints are uniquely identified
            by the default sign. A small subset of hints, however, concurrently
            satisfy the detection criteria for multiple signs and are thus
            identifiable with multiple signs. This parameter supports those
            hints by enabling callers to call this method multiple times with
            the same hint passed different signs.

            Prominent examples include:

            * :pep:`484`- and :pep:`585`-compliant unsubscripted generics --
              which, due to being user-defined types, may subclass another
              PEP-compliant :mod:`typing` superclass also identifiable by
              another sign. Prominent examples include:

              * **Generic typed dictionaries** identifiable as both the
                :data:`.HintSignPep484585GenericUnsubbed` sign *and* the
                :data:`HintSignTypedDict` sign for :pep:`589`-compliant typed
                dictionaries: e.g.,

                .. code-block:: python

                   from typing import Generic, TypedDict
                   class GenericTypedDict[T](TypedDict, Generic[T]):
                       generic_item: T

              * **Generic named tuples** identifiable as both the
                :data:`.HintSignPep484585GenericUnsubbed` sign *and* the
                :data:`HintSignNamedTuple` sign for :pep:`484`-compliant named
                tuples: e.g.,

                .. code-block:: python

                   from typing import Generic, NamedTuple
                   class GenericNamedTuple[T](NamedTuple, Generic[T]):
                       generic_item: T
        '''
        assert isinstance(hint_sane, HintSane), (
            f'{repr(hint_sane)} not sanified hint metadata.')

        # If the caller did *NOT* pass a non-default sign identifying this hint,
        # default this sign to the default sign identifying this hint.
        if hint_sign is SENTINEL:
            hint_sign = get_hint_pep_sign_or_none(hint_sane.hint)
        # Else, the caller passed a non-default sign identifying this hint. In
        # this case, preserve this sign as is.

        # Initialize our superclass with all passed parameters.
        super().__init__(hint_sane=hint_sane, hint_sign=hint_sign)  # type: ignore[arg-type]

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:
        '''
        Machine-readable representation of this metadata.
        '''

        # Represent this metadata with just the minimal subset of metadata
        # needed to reasonably describe this metadata.
        return (
            f'{self.__class__.__name__}('
            f'hint_sane={repr(self.hint_sane)}, '
            f'hint_sign={repr(self.hint_sign)}, '
            f')'
        )
