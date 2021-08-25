#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **unmemoized class tester** (i.e., unmemoized and thus efficient
callable testing various properties of arbitrary classes) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilTypeException
from beartype._data.cls.datacls import TYPES_BUILTIN_FAKE
from beartype._data.mod.datamod import BUILTINS_MODULE_NAME
from typing import Type

# ....................{ VALIDATORS                        }....................
def die_unless_type(
    # Mandatory parameters.
    cls: object,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilTypeException,
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is a class.

    Parameters
    ----------
    cls : object
        Object to be validated.
    exception_cls : Type[Exception]
        Type of exception to be raised. Defaults to
        :exc:`_BeartypeUtilTypeException`.

    Raises
    ----------
    exception_cls
        If this object is *not* a class.
    '''

    # If this object is *NOT* a class, raise an exception.
    if not isinstance(cls, type):
        assert isinstance(exception_cls, type), (
            'f{repr(exception_cls)} not exception class.')
        raise exception_cls(f'{repr(cls)} not class.')

# ....................{ TESTERS ~ builtin                 }....................
def is_type_builtin(cls: type) -> bool:
    '''
    ``True`` only if the passed class is **builtin** (i.e., globally accessible
    C-based type requiring *no* explicit importation).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this class is builtin.

    Raises
    ----------
    _BeartypeUtilTypeException
        If this object is *not* a class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.mod.utilmodule import (
        get_object_type_module_name_or_none)

    # If this object is *NOT* a type, raise an exception.
    die_unless_type(cls)
    # Else, this object is a type.

    # If this type is a fake builtin (i.e., type that is *NOT* builtin but
    # erroneously masquerading as being builtin), this type is *NOT* a builtin.
    # In this case, silently reject this type.
    if cls in TYPES_BUILTIN_FAKE:
        return False
    # Else, this type is *NOT* a fake builtin.

    # Fully-qualified name of the module defining this type if this type is
    # defined by a module *OR* "None" otherwise (i.e., if this type is
    # dynamically defined in-memory).
    cls_module_name = get_object_type_module_name_or_none(cls)

    # This return true only if this name is that of the "builtins" module
    # declaring all builtin types.
    return cls_module_name == BUILTINS_MODULE_NAME
