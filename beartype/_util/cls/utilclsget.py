#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class getters** (i.e., low-level callables querying for various
properties of arbitrary classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilTypeException
from beartype._data.datatyping import (
    LexicalScope,
    TypeException,
)

# ....................{ VALIDATORS                         }....................
#FIXME: Unit test us up, please.
def get_type_locals(
    # Mandatory parameters.
    cls: type,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilTypeException,
) -> LexicalScope:
    '''
    **Local scope** (i.e., dictionary mapping from the name to value of each
    attribute directly declared by that class) for the passed class.

    Parameters
    ----------
    cls : type
        Class to be inspected.
    exception_cls : Type[Exception]
        Type of exception to be raised. Defaults to
        :exc:`_BeartypeUtilTypeException`.

    Returns
    ----------
    LexicalScope
        Local scope for this class.

    Raises
    ----------
    :exc:`exception_cls`
        If the next non-ignored frame following the last ignored frame is *not*
        the parent callable or module directly declaring the passed callable.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'

    #FIXME: Implement us up based on a code snippet residing at the top of the
    #"beartype._decor._pep.pep563" submodule, please.

    # Return the dictionary of class attributes already directly bundled with
    # this class.
    return cls.__dict__  # type: ignore[return-value]
