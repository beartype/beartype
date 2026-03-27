#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **core reducers** (i.e., low-level callables
converting :pep:`484`-compliant type hints not requiring significant special
handling to lower-level type hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.meta import URL_PEP585_DEPRECATIONS
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from beartype._cave._cavefast import NoneType
from beartype._check.metadata.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintSane,
)
from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.hint.datahintrepr import (
    HINTS_PEP484_REPR_PREFIX_DEPRECATED)
from beartype._data.typing.datatypingport import Hint
# from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.error.utilerrwarn import issue_warning
from beartype._util.hint.utilhintget import get_hint_repr
from typing import NoReturn

# ....................{ REDUCERS ~ deprecated              }....................
#FIXME: Should probably be cached as described in the docstring below. Sadly, we
#lack the time and motivation to fix the tests that break as a result of doing
#so. Guh! It's so sad.
# @callable_cached
def reduce_hint_pep484_deprecated(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    exception_prefix: str = EXCEPTION_PLACEHOLDER,
) -> Hint:
    '''
    Preserve the passed :pep:`484`-compliant hint as is while conditionally
    emitting a non-fatal deprecation warning if this hint is deprecated (e.g.,
    due to having been obsoleted by an equivalent :pep:`585`-compliant hint).

    This reducer is intentionally memoized to emit only one such warning for
    each hint. Specifically, this reducer:

    * Issues this deprecation warning for only the *first* instance of this
      hint. When subsequently passed the same hint, this reducer avoids
      uselessly re-issuing the same warning by silently reducing to a noop.
    * Issues an explanatory preamble prefixing this deprecating warning for
      *only* the first hint passed to this function. When subsequently passed
      *any* other hint, this reducer avoids uselessly re-issuing the same
      preamble by instead issuing a truncated deprecation warning containing
      "Just the QA facts, mam!"

    Parameters
    ----------
    hint : Hint
        Type hint to be reduced.
    exception_prefix : str, default: EXCEPTION_PLACEHOLDER
        Human-readable substring prefixing raised exception messages. Defaults
        to :data:`.EXCEPTION_PLACEHOLDER`.

    Returns
    -------
    Hint
        This hint unmodified.

    Warns
    -----
    BeartypeDecorHintPep585DeprecationWarning
        If this is a :pep:`484`-compliant type hint deprecated by :pep:`585`.
    '''
    # print(f'Testing PEP 484 type hint {repr(hint)} for PEP 585 deprecation...')
    # print(f'{HINTS_PEP484_REPR_PREFIX_DEPRECATED}')

    # Machine-readable representation of this hint.
    hint_repr = get_hint_repr(hint)

    # Substring of the machine-readable representation of this hint preceding
    # the first "[" delimiter if this representation contains that delimiter
    # *OR* this representation as is otherwise.
    #
    # Note that the str.partition() method has been profiled to be the optimally
    # efficient means of parsing trivial prefixes.
    hint_repr_bare = hint_repr.partition('[')[0]

    # If this hint is a PEP 484-compliant type hint originating from an origin
    # type (e.g., "typing.List[int]"), this hint has been deprecated by the
    # equivalent PEP 585-compliant type hint (e.g., "list[int]"). In this
    # case...
    if hint_repr_bare in HINTS_PEP484_REPR_PREFIX_DEPRECATED:
        # Warning message to be emitted.
        warning_message = (
            f'{EXCEPTION_PLACEHOLDER}'
            f'PEP 484 type hint {repr(hint)} deprecated by PEP 585.'
        )

        # Permit this global to be locally re-assigned to below.
        global _IS_ISSUED_HINT_PEP484_DEPRECATION_PREAMBLE

        # If this reducer has yet to be called and thus has yet to issue a
        # verbose explanatory preamble prefixing the first deprecation warning
        # issued by this reducer...
        if not _IS_ISSUED_HINT_PEP484_DEPRECATION_PREAMBLE:
            # Prefix this message by this preamble.
            warning_message += (
                f' This hint may be removed at some unspecified future date. '
                f'CPython "typing" devs whose spaghetti code you depend on '
                f'originally intended to schedule this hint for removal after '
                f'releasing Python 3.14 on October 7th, 2025. '
                f'But... uhh, you may have noticed. '
                f'2025 was a billion years ago. '
                f'Nothing happened. Nothing got removed or even scheduled for '
                f'removal. How lucky does your CI feel today? '
                f'If the answer is anything except '
                f'"Super-lucky, thanks for asking!", either:\n'
                f'* Import this hint from "beartype.typing" rather than '
                f'"typing".\n'
                f'* Globally silence this warning by adding to your '
                f'top-level "{{muh_package}}.__init__" submodule:\n'
                f'\tfrom beartype.roar import BeartypeDecorHintPep585DeprecationWarning\n'
                f'\tfrom warnings import filterwarnings\n'
                f'\tfilterwarnings(action="ignore", category=BeartypeDecorHintPep585DeprecationWarning)\n'
                f'\n'
                f'See also: {URL_PEP585_DEPRECATIONS}'
            )

            # Avoid doing so again for the remainder of this Python process.
            _IS_ISSUED_HINT_PEP484_DEPRECATION_PREAMBLE = True
        # Else, this reducer has been called at least once and has thus already
        # issued a verbose explanatory preamble prefixing the first deprecation
        # warning issued by this reducer. Avoid doing so again for sanity.

        # Emit this message as a PEP 585-specific deprecation warning.
        issue_warning(
            message=warning_message,
            cls=BeartypeDecorHintPep585DeprecationWarning,
        )
    # Else, this hint is *NOT* deprecated. In this case, reduce to a noop.

    # Preserve this hint as is, regardless of deprecation.
    return hint

# ....................{ REDUCERS ~ singleton               }....................
def reduce_hint_pep484_any(hint: Hint) -> HintSane:
    '''
    Reduce the passed :pep:`484`-compliant :obj:`typing.Any` type hint singleton
    to the ignorable :data:`.HINT_SANE_IGNORABLE` singleton.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        :obj:`typing.Any` hint singleton to be reduced.

    Returns
    -------
    HintSane
        Ignorable :data:`.HINT_SANE_IGNORABLE` singleton.
    '''

    # Unconditionally ignore the "Any" hint singleton.
    return HINT_SANE_IGNORABLE


def reduce_hint_pep484_never(hint: Hint) -> Hint:
    '''
    Reduce the passed PEP-noncompliant :obj:`typing.Never` type hint singleton
    to the :pep:`484`-compliant :obj:`typing.NoReturn` type hint singleton.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        :obj:`typing.Never` hint singleton to be reduced.

    Returns
    -------
    Hint
        :pep:`484`-compliant :obj:`typing.NoReturn` hint singleton.
    '''

    # Unconditionally return the PEP 484-compliant "NoReturn" hint singleton.
    return NoReturn


# Note that this reducer is intentionally typed as returning "type" rather than
# "NoneType". While the former would certainly be preferable, mypy erroneously
# emits false positives when this reducer is typed as returning "NoneType":
#     beartype._util.hint.pep.proposal.pep484.pep484.py:190: error: Variable
#     "beartype._cave._cavefast.NoneType" is not valid as a type [valid-type]
def reduce_hint_pep484_none(hint: Hint) -> type:
    '''
    Reduce the passed :pep:`484`-compliant :data:`None` singleton to the type of
    :data:`None` (i.e., the builtin :class:`types.NoneType` class).

    While *not* explicitly defined by the :mod:`typing` module, :pep:`484`
    explicitly supports this singleton:

        When used in a type hint, the expression :data:`None` is considered
        equivalent to ``type(None)``.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        :data:`None` hint to be reduced.

    Returns
    -------
    type[NoneType]
        Type of the :data:`None` singleton.
    '''
    assert hint is None, f'Type hint {hint} not "None" singleton.'

    # Unconditionally return the type of the "None" singleton.
    return NoneType

# ....................{ PRIVATE ~ globals                  }....................
_IS_ISSUED_HINT_PEP484_DEPRECATION_PREAMBLE = False
'''
:data:`True` only if the :func:`._issue_hint_pep484_deprecation` function has
been called at least once and thus already issued a verbose explanatory preamble
prefixing the first deprecation warning issued by that function.

Note that this global boolean is intentionally non-thread-safe, as thread-safety
is irrelevant with respect to deprecation warning messages. In the worst case,
two or more competing threads will race to prefix deprecations by the same
verbose explanatory preamble. So? Exactly. It's a non-issue, yo.
'''
