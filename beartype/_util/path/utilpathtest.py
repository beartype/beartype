#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **path testers** (i.e., low-level callables testing various aspects
of on-disk files and directories and raising exceptions when those files and
directories fail to satisfy various constraints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilPathException
from beartype._data.hint.datahinttyping import (
    PathnameLike,
    PathnameLikeTuple,
    TypeException,
)
from pathlib import Path

# ....................{ RAISERS                            }....................
#FIXME: Unit test us up, please.
def die_unless_dir(
    # Mandatory parameters.
    dirname: PathnameLike,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilPathException,
) -> None:
    '''
    Raise an exception of the passed type if *no* directory with the passed
    dirname exists.

    Parameters
    ----------
    dirname : PathnameLike
        Dirname to be validated.
    exception_cls : Type[Exception], optional
        Type of the exception to be raised by this function. Defaults to
        :exc:`_BeartypeUtilPathException`.

    Raises
    ----------
    :exc:`exception_cls`
        If *no* directory with the passed dirname exists.
    '''

    # High-level "Path" object encapsulating this dirname.
    dirname_path = Path(dirname)

    # If either no path with this pathname exists *OR* a path with this pathname
    # exists but this path is not a directory...
    if not dirname_path.is_dir():
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')

        # If no path with this pathname exists, raise an appropriate exception.
        if not dirname_path.exists():
            raise exception_cls(f'Directory "{dirname_path}" not found.')
        # Else, a path with this pathname exists.

        # By elimination, a path with this pathname exists but this path is not
        # a directory. In this case, raise an appropriate exception.
        raise exception_cls(f'Path "{dirname_path}" not directory.')
    # Else, a directory with this dirname exists.
