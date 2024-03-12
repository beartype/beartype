#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **dual type hint utilities**
(i.e., callables generically applicable to both :pep:`484`- and
:pep:`585`-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep585Exception
from beartype.typing import Union
from beartype._util.hint.pep.proposal.pep484.utilpep484 import (
    HINT_PEP484_TUPLE_EMPTY)
from beartype._util.hint.pep.proposal.utilpep585 import (
    HINT_PEP585_TUPLE_EMPTY)

# ....................{ TESTERS ~ kind : tuple             }....................
def is_hint_pep484585_tuple_empty(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **empty fixed-length tuple type hint** (i.e., hint
    constraining objects to be the empty tuple).

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only called under fairly
    uncommon edge cases.

    Motivation
    ----------
    Since type variables are not themselves types but rather placeholders
    dynamically replaced with types by type checkers according to various
    arcane heuristics, both type variables and types parametrized by type
    variables warrant special-purpose handling.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is an empty fixed-length tuple hint.
    '''

    # Return true only if this hint resembles either the PEP 484- or
    # 585-compliant fixed-length empty tuple type hint. Since there only exist
    # two such hints *AND* comparison against these hints is mostly fast, this
    # test is efficient in the general case.
    #
    # Note that this test may also be inefficiently performed by explicitly
    # obtaining this hint's sign and then subjecting this hint to specific
    # tests conditionally depending on which sign and thus PEP this hint
    # complies with: e.g.,
    #     # Return true only if this hint is either...
    #     return true (
    #         # A PEP 585-compliant "tuple"-based hint subscripted by no
    #         # child hints *OR*...
    #         (
    #             hint.__origin__ is tuple and
    #             hint_childs_len == 0
    #         ) or
    #         # A PEP 484-compliant "typing.Tuple"-based hint subscripted
    #         # by exactly one child hint *AND* this child hint is the
    #         # empty tuple,..
    #         (
    #             hint.__origin__ is Tuple and
    #             hint_childs_len == 1 and
    #             hint_childs[0] == ()
    #         )
    #     )
    return (
        hint == HINT_PEP585_TUPLE_EMPTY or
        hint == HINT_PEP484_TUPLE_EMPTY
    )

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_hint_pep484585_args(
    hint: object, args_len: int, exception_prefix: str) -> object:
    '''
    Either the single argument or tuple of all arguments subscripting the passed
    :pep:`484`- or :pep:`585`-compliant type hint if this hint is subscripted by
    exactly the passed number of child type hints *or* raise an exception
    otherwise.

    This getter returns either:

    * If ``args_len == 1``, the single argument subscripting this hint as a
      convenience to the caller.
    * Else, the tuple of all arguments subscripting this hint.

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
    hint : Any
        Type hint to be inspected.
    args_len : int
        Number of child type hints expected to subscript this hint.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    -------
    Union[object, tuple]
        Either the single argument or tuple of all arguments subscripting this
        type hint.

    Raises
    ------
    BeartypeDecorHintPep585Exception
        If this hint is subscripted by an unexpected number of child type hints.
    '''
    assert isinstance(args_len, int), f'{repr(args_len)} not integer.'
    assert args_len >= 1, f'{args_len} < 0.'

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # Tuple of all arguments subscripting this hint.
    hint_args = get_hint_pep_args(hint)

    # If this hint is *NOT* subscripted by the expected number of child type
    # hints...
    if len(hint_args) != args_len:
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise an exception.
        raise BeartypeDecorHintPep585Exception(
            f'{exception_prefix}PEP 585 type hint {repr(hint)} '
            f'not subscripted (indexed) by {args_len} arguments (i.e., '
            f'subscripted by {len(hint_args)} != {args_len} arguments).'
        )
    # Else, this hint is subscripted by the expected number of child type hints.

    # Return either...
    return (
        # If this hint is subscripted by only child hint, this child hint;
        hint_args[0]
        if args_len == 1 else
        # Else, this tuple of arguments as is.
        hint_args
    )
