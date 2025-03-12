#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant **testers** (i.e., low-level callables testing
various properties of dataclasses standardized by :pep:`557`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.datahinttyping import DictStrToAny
from dataclasses import (  # type: ignore[attr-defined]
    # Public attributes of the "dataclasses" module.
    is_dataclass,

    # Private attributes of the "dataclasses" module. Although non-ideal, the
    # extreme non-triviality of this module leaves us little choice. *shrug*
    _PARAMS,  # pyright: ignore
)

# ....................{ TESTERS                            }....................
def is_type_pep557_dataclass(cls: type) -> bool:
    '''
    :data:`True` only if the passed class is a **dataclass** (i.e.,
    :pep:`557`-compliant class decorated by the standard
    :func:`dataclasses.dataclass` decorator).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this class is a dataclass.

    Raises
    ------
    _BeartypeUtilTypeException
        If this object is *not* a class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclstest import die_unless_type

    # If this object is *NOT* a type, raise an exception.
    die_unless_type(cls)
    # Else, this object is a type.

    # Return true only if this type is a dataclass.
    #
    # Note that the is_dataclass() tester was intentionally implemented
    # ambiguously to return true for both actual dataclasses *AND*
    # instances of dataclasses. Since the prior validation omits the
    # latter, this call unambiguously returns true *ONLY* if this object is
    # an actual dataclass. (Dodged a misfired bullet there, folks.)
    return is_dataclass(cls)

# ....................{ GETTERS                            }....................
#FIXME: Implement us up, please.
#FIXME: Unit test us up, please.
def get_pep557_dataclass_kwargs(datacls: type) -> DictStrToAny:
    '''
    Dictionary of all keyword arguments originally passed to the
    :pep:`557`-compliant :func:`dataclasses.dataclass` decorator decorating the
    passed dataclass.

    Parameters
    ----------
    datacls: type
        Dataclass to be inspected.

    Returns
    -------
    DictStrToAny
        Keyword arguments originally configuring this dataclass.
    '''

    #FIXME: Insufficient. Also:
    #* Define a new die_unless_pep557_dataclass() raiser, please.
    #* Call that raiser here first, please.
    dataclass_kwargs = getattr(datacls, _PARAMS)
    return dataclass_kwargs
