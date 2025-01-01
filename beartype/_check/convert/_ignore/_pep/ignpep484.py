#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type hint ignorers** (i.e., low-level
callables detecting whether :pep:`484`-compliant type hints are ignorable or
not).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.metadata.metasane import (
    HintSanifiedData,
    HintOrHintSanifiedData,
    get_hint_or_sane_hint,
)
# from beartype._util.hint.pep.proposal.pep484.pep484newtype import (
#     get_hint_pep484_newtype_alias)

# ....................{ TESTERS                            }....................
#FIXME: Excise us up, please.
# def is_hint_pep484_newtype_ignorable(
#     hint_or_sane: HintOrHintSanifiedData) -> bool:
#     '''
#     :data:`True` only if the passed :pep:`484`-compliant **new type** (i.e.,
#     :obj:`typing.NewType`-based type alias) is ignorable.
#
#     This tester ignores the :obj:`typing.NewType` factory passed an ignorable
#     child hint. Unlike most :mod:`typing` constructs, that factory does *not*
#     cache the objects it returns: e.g.,
#
#     .. code-block:: pycon
#
#        >>> from typing import NewType
#        >>> NewType('TotallyNotAStr', str) is NewType('TotallyNotAStr', str)
#        False
#
#     Since this implies every call to ``NewType({same_name}, object)`` returns a
#     new closure, the *only* means of ignoring ignorable new type aliases is
#     dynamically within this function.
#
#     This tester is intentionally *not* memoized (e.g., by the
#     ``callable_cached`` decorator), as this tester is only safely callable by
#     the memoized parent
#     :func:`beartype._check.convert._ignore.ignhint.is_hint_ignorable` tester.
#
#     Parameters
#     ----------
#     hint_or_sane : HintOrHintSanifiedData
#         Either a type hint *or* **sanified type hint metadata** (i.e.,
#         :data:`.HintSanifiedData` object) to be inspected.
#
#     Returns
#     -------
#     bool
#         :data:`True` only if this :pep:`484`-compliant type hint is ignorable.
#     '''
#
#     # Avoid circular import dependencies.
#     from beartype._check.convert._ignore.ignhint import is_hint_ignorable
#
#     # Hint encapsulated by this metadata.
#     hint = get_hint_or_sane_hint(hint_or_sane)
#
#     # Child hint aliased by this PEP 484-compliant new type.
#     hint_or_sane_child = get_hint_pep484_newtype_alias(hint)
#
#     # If this hint is encapsulated by metadata...
#     if isinstance(hint_or_sane, HintSanifiedData):
#         # Encapsulate this child hint by the same metadata.
#         hint_or_sane_child = hint_or_sane.permute(hint=metahint_or_sane)
#     # Else, this hint is *NOT* encapsulated by metadata. In this case, preserve
#     # this metahint as is.
#
#     # Return true only if this hint aliases an ignorable child type hint.
#     return is_hint_ignorable(hint_or_sane_child)
