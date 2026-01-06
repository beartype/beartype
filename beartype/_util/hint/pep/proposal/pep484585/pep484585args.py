#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **child type hint getters**
(i.e., low-level callables generically retrieving child type hints subscripting
:pep:`484`- and :pep:`585`-compliant parent type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep585Exception
from beartype._data.typing.datatypingport import (
    Hint,
    HintOrTupleHints,
)

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_hint_pep484585_arg(hint: Hint, exception_prefix: str) -> Hint:
    '''
    Sole child hint subscripting the passed :pep:`484`- or :pep:`585`-compliant
    parent hint if this hint is subscripted by exactly one child hint *or* raise
    an exception otherwise (i.e., if this parent hint is either unsubscripted
    *or* subscripted by two or more child hints).

    This getter is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to
    an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Parent hint to be inspected.
    args_len : int
        Number of child hints expected to subscript this parent hint.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    -------
    Hint
        Sole child hint subscripting this parent hint.

    Raises
    ------
    BeartypeDecorHintPep585Exception
        If this hint is subscripted by an unexpected number of child hints.

    See Also
    --------
    :func:`.get_hint_pep484585_args`
        Further details.
    '''

    # Defer to this lower-level getter.
    return get_hint_pep484585_args(  # type: ignore[return-value]
        hint=hint, args_len=1, exception_prefix=exception_prefix)


#FIXME: Unit test us up, please.
def get_hint_pep484585_args(
    hint: Hint, args_len: int, exception_prefix: str) -> HintOrTupleHints:
    '''
    Single child hint *or* tuple of all child hints subscripting the passed
    :pep:`484`- or :pep:`585`-compliant parent hint if this hint is subscripted
    by exactly the passed number of child hints *or* raise an exception
    otherwise.

    This getter returns either:

    * If ``args_len == 1``, the single child hint subscripting this parent hint
      as a convenience to the caller.
    * Else, the tuple of all child hints subscripting this parent hint.

    This getter is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to
    an efficient one-liner.

    Caveats
    -------
    **This higher-level getter should always be called in lieu of directly
    accessing the low-level** ``__args__`` **dunder attribute,** which is
    typically *not* validated at runtime and thus should *not* be assumed to be
    sane. Although the :mod:`typing` module usually validates the arguments
    subscripting :pep:`484`-compliant type hints and thus the ``__args__``
    **dunder attribute at hint instantiation time, C-based CPython internals
    fail to similarly validate the arguments subscripting :pep:`585`-compliant
    type hints at any time:

    .. code-block:: python

        >>> import typing
        >>> typing.Type[str, bool]
        TypeError: Too many parameters for typing.Type; actual 2, expected 1
        >>> type[str, bool]
        type[str, bool]   # <-- when everything is okay, nothing is okay

    Parameters
    ----------
    hint : Hint
        Parent hint to be inspected.
    args_len : int
        Number of child hints expected to subscript this parent hint.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    -------
    HintOrTupleHints
        Either the sole child hint *or* tuple of all child hints subscripting
        this parent hint.

    Raises
    ------
    BeartypeDecorHintPep585Exception
        If this hint is subscripted by an unexpected number of child hints.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args_of_len

    # Defer to this lower-level getter.
    return get_hint_pep_args_of_len(
        hint=hint,
        args_len=args_len,
        exception_cls=BeartypeDecorHintPep585Exception,
        exception_prefix=exception_prefix,
    )
