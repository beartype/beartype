#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **exception getters** (i.e., low-level callables retrieving
metadata associated with various types of exceptions).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
# from beartype.typing import Type

# ....................{ GETTERS                            }....................
def get_name_error_attr_name(name_error: NameError) -> str:
    '''
    Unqualified basename of the non-existent attribute referenced by the passed
    :class:`NameError` exception.

    Parameters
    ----------
    name_error : NameError
        :class:`NameError` exception to be inspected.

    Returns
    -------
    str
        Unqualified basename of this non-existent attribute.

    Examples
    --------
    .. code-block:: pycon

       >>> from beartype._util.error.utilerrorget import (
       ...     get_name_error_attr_name)
       >>> try:
       ...     undefined_attr
       ... except NameError as name_error:
       ...     print(get_name_error_attr_name(name_error))
       ...     print(name_error)
       undefined_attr
       name 'undefined_attr' is not defined
    '''
    assert isinstance(name_error, NameError), (
        f'{repr(name_error)} not "NameError" exception.')

    # Message associated with this name error.
    name_error_message = str(name_error)

    # Unqualified basename of the non-existent attribute referenced by this
    # message, initialized to the suffix of this message preceding the prefixing
    # "name '" prefix.
    attr_name = name_error_message[_NAME_ERROR_ATTR_NAME_START_INDEX:]

    # 0-based index of the next character following the last character in this
    # basename, defined as that of the remaining single quote delimiter in this
    # message.
    _NAME_ERROR_ATTR_NAME_END_INDEX = attr_name.index("'")

    # Strip the ignorable suffix from this basename.
    attr_name = attr_name[:_NAME_ERROR_ATTR_NAME_END_INDEX]

    # Return this basename.
    return attr_name

# ....................{ PRIVATE ~ globals                  }....................
_NAME_ERROR_ATTR_NAME_START_INDEX = len("name '")
'''
0-based index of the first character of the unqualified basename of the
non-existent attribute referenced in the messages of all :class:`NameError`
exceptions, defined as that of the first character following the``"name '"``
substring unconditionally prefixing these messages.
'''
