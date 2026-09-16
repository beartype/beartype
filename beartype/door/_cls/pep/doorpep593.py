#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) annotated type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`593`-compliant :attr:`typing.Annotated` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorabc import TypeHint
from beartype._data.typing.datatypingport import Hint
from beartype._util.hint.pep.proposal.pep593 import (
    get_hint_pep593_metadata,
    get_hint_pep593_metahint,
)
from contextlib import suppress

# ....................{ SUBCLASSES                         }....................
class AnnotatedTypeHint(TypeHint):
    '''
    **Annotated type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`593`-compliant :attr:`typing.Annotated` type hint).

    Attributes
    ----------
    _metadata : tuple[object]
        **Metadata** (i.e., tuple of zero or more arbitrary low-level
        caller-defined objects annotating this :attr:`typing.Annotated` type
        hint, equivalent to all remaining arguments subscripting this hint).
    _metahint_wrapper : TypeHint
        **Metahint wrapper** (i.e., :class:`TypeHint` instance wrapping the
        child type hint annotated by this parent :attr:`typing.Annotated` type
        hint, equivalent to the first argument subscripting this hint).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_metadata',
        '_metahint_wrapper',
    )

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint: Hint) -> None:

        # Initialize our superclass with all passed parameters.
        super().__init__(hint)

        # Tuple of the zero or more arbitrary caller-defined arguments following
        # the first argument subscripting this hint.
        self._metadata = get_hint_pep593_metadata(hint)

        # Wrapper wrapping the first argument subscripting this hint.
        self._metahint_wrapper = TypeHint(get_hint_pep593_metahint(hint))

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _is_args_ignorable(self) -> bool:

        # Unconditionally return false. The PEP 593-compliant "typing.Annotated"
        # type hint factory requires subscription by at least two child hints.
        # Ergo, even if the metahint (i.e., first child hint subscripting this
        # factory) is ignorable (e.g., "Annotated[object, ...]", the subsequent
        # metadata (i.e., all remaining child hints subscripting this factory)
        # are custom and thus unignorable.
        return False

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_equal(self, other: TypeHint) -> bool:

        # Return true only if...
        return (
            # That other hint is also a PEP 593-compliant "typing.Annotated"
            # hint *AND*...
            isinstance(other, AnnotatedTypeHint) and
            # The metahint (i.e., first child) of this annotated hint equals
            # the metahint (i.e., first child) of that annotated hint *AND*...
            self._metahint_wrapper == other._metahint_wrapper and
            # The metadata (i.e., all children except the first) of this
            # annotated hint equals the metadata of that annotated hint.
            _is_metadata_equal(self, other)
        )


    def _is_subhint_branch(self, branch: TypeHint) -> bool:

        # If that other hint is *NOT* also an annotated (e.g.,
        # "Annotated[list[int], 'meta'] <= list[int]"), ignore *ALL*
        # supplementary metadata subscripting this annotated hint by reducing to
        # testing that this annotated hint's metahint subhints that other hint.
        if not isinstance(branch, AnnotatedTypeHint):
            return self._metahint_wrapper.is_subhint(branch)
        # Else, that other hint is also an annotated hint.

        # Return true only if...
        return (
            # The metahint (i.e., first child) of this annotated hint subhints
            # the metahint (i.e., first child) of that annotated hint *AND*...
            self._metahint_wrapper <= branch._metahint_wrapper and
            # The metadata (i.e., all children except the first) of this
            # annotated hint equals the metadata of that annotated hint.
            #
            # Note that we intentionally avoid testing for a subhint relation
            # here (e.g., with the "<=" operator). Arbitrary caller-defined
            # objects are *MUCH* more likely to define a relevant equality
            # comparison than a relevant less-than-or-equal-to comparison.
            _is_metadata_equal(self, branch)
        )

# ....................{ PRIVATE ~ testers                  }....................
def _is_metadata_equal(
    this: AnnotatedTypeHint, that: AnnotatedTypeHint) -> bool:
    '''
    :data:`True` only if the **metadata** (i.e., all child hints subscripting a
    :pep:`593`-compliant :obj:`typing.Annotated` hint except the first such
    child hint) of the first passed :obj:`typing.Annotated` hint equals that of
    the second passed :obj:`typing.Annotated` hint.
    '''
    assert isinstance(this, AnnotatedTypeHint), (
        f'{repr(this)} not "AnnotatedTypeHint".')
    assert isinstance(that, AnnotatedTypeHint), (
        f'{repr(that)} not "AnnotatedTypeHint".')

    # If these hints are *NOT* annotated by the same number of objects,
    # immediately return false.
    #
    # Note that this is merely a negligible microoptimization. Why are we like
    # this? *sigh*
    if len(this._metadata) != len(that._metadata):
        return False
    # Else, these hints are annotated by the same number of objects.

    # Attempt to return true only if these hints are annotated by equivalent
    # objects.
    #
    # Note that the following iteration performs equality comparisons on
    # arbitrary caller-defined objects. Since these comparisons may raise
    # arbitrary caller-defined exceptions, we silently squelch any such
    # exceptions that arise by returning false below instead.
    with suppress(Exception):
        return this._metadata == that._metadata

    # Else, one or more objects annotating these hints are incomparable. So,
    # this hint *CANNOT* be a subhint of that hint. Return false.
    return False  # pragma: no cover
