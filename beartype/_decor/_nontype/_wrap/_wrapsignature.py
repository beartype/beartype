#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''Missing-argument errors for callable-specific wrapper signatures.'''

from beartype._util.func.arg.utilfuncargiter import ArgKind
from collections.abc import Callable


def die_if_args_missing(
    func: Callable,
    args_meta: tuple[tuple[ArgKind, str], ...],
    args_values: tuple[object, ...],
    sentinel: object,
) -> None:
    '''
    Raise a native-style :class:`TypeError` for omitted required arguments.

    Called only on the error path, before type checks or the wrapped body run.
    Requiredness is determined from live defaults, including bound methods.
    '''
    defaults = func.__defaults__ or ()  # type: ignore[attr-defined]
    kwdefaults = func.__kwdefaults__ or {}  # type: ignore[attr-defined]
    positional_count = sum(
        kind in (ArgKind.POSITIONAL_ONLY, ArgKind.POSITIONAL_OR_KEYWORD)
        for kind, _ in args_meta)
    positional_index = 0
    missing_positional = []
    missing_keyword = []
    for (kind, name), value in zip(args_meta, args_values):
        if kind in (ArgKind.POSITIONAL_ONLY, ArgKind.POSITIONAL_OR_KEYWORD):
            if value is sentinel and len(defaults) < (
                positional_count - positional_index
            ):
                missing_positional.append(name)
            positional_index += 1
        elif kind is ArgKind.KEYWORD_ONLY:
            if value is sentinel and name not in kwdefaults:
                missing_keyword.append(name)

    # Python reports missing positional arguments before keyword-only ones.
    missing = missing_positional or missing_keyword
    if missing:
        names = [repr(name) for name in missing]
        names_repr = (
            names[0] if len(names) == 1 else
            ' and '.join(names) if len(names) == 2 else
            f'{", ".join(names[:-1])}, and {names[-1]}'
        )
        kind_repr = 'positional' if missing_positional else 'keyword-only'
        plural = '' if len(missing) == 1 else 's'
        raise TypeError(
            f'{func.__qualname__}() missing {len(missing)} required '
            f'{kind_repr} argument{plural}: {names_repr}')
