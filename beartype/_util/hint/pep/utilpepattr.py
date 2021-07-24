#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint attribute** (i.e., attribute usable for creating
PEP-compliant type hints in a safe, non-deprecated manner regardless of the
Python version targeted by the active Python interpreter) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPepException
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.mod.utilmodule import (
    import_module_attr_or_none,
    is_module,
)
from beartype._util.utilobject import SENTINEL
from typing import Any, Type

# ....................{ ATTRS                             }....................
# Signs conditionally dependent on the major version of Python targeted by
# the active Python interpreter, initialized to a sentinel guaranteed to
# *NEVER* match.

# Initialized below.
HINT_ATTR_LIST: Any = SENTINEL
'''
**List sign** (i.e., arbitrary object uniquely identifying PEP-compliant list
type hints) importable under the active Python interpreter.
'''


# Initialized below.
HINT_ATTR_TUPLE: Any = SENTINEL
'''
**Tuple sign** (i.e., arbitrary object uniquely identifying PEP-compliant tuple
type hints) importable under the active Python interpreter.
'''

# ....................{ IMPORTERS                         }....................
@callable_cached
def import_typing_attr(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: Type[Exception] = BeartypeDecorHintPepException,
) -> Any:
    '''
    Dynamically import and return the **typing attribute** (i.e., object
    declared at module scope by either the :mod:`typing` or
    :mod:`typing_extensions` modules) with the passed unqualified name if
    importable from one or more of those modules *or* raise an exception
    otherwise.

    Specifically, this function (in order):

    #. If the official :mod:`typing` module bundled with the active Python
       interpreter declares that attribute, dynamically imports and returns
       that attribute from that module.
    #. Else if the third-party (albeit quasi-official) :mod:`typing_extensions`
       module requiring external installation under the active Python
       interpreter declares that attribute, dynamically imports and returns
       that attribute from that module.
    #. Else, raises a human-readable exception.

    This function is memoized for efficiency.

    Parameters
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from a typing module.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintPepException`.

    Returns
    ----------
    object
        Attribute with this name dynamically imported from a typing module.

    Raises
    ----------
    exception_cls
        If either:

        * This name is *not* a syntactically valid attribute name.
        * Neither the :mod:`typing` nor :mod:`typing_extensions` modules
          declare an attribute with this name.
    Exception
        If a module prefixed by this name exists but that module is
        unimportable due to module-scoped side effects at importation time.
        Modules may perform arbitrary Turing-complete logic from module scope;
        callers should be prepared to handle *any* possible exception. That
        said, the :mod:`typing` and :mod:`typing_extensions` modules are
        scrupulously tested and thus unlikely to raise exceptions on initial
        importation.
    '''

    # Attribute with this name imported from the "typing" module if that module
    # declares this attribute *OR* "None" otherwise.
    typing_attr = import_module_attr_or_none(
        module_attr_name=f'typing.{typing_attr_basename}',
        module_attr_label='Typing attribute',
        exception_cls=exception_cls,
    )

    # If the "typing" module does *NOT* declare this attribute...
    if typing_attr is None:
        # Attribute with this name imported from the "typing_extensions" module
        # if that module declares this attribute *OR* "None" otherwise.
        typing_attr = import_module_attr_or_none(
            module_attr_name=f'typing_extensions.{typing_attr_basename}',
            module_attr_label='Typing attribute',
            exception_cls=exception_cls,
        )

        # If the "typing_extensions" module also does *NOT* declare this
        # attribute...
        if typing_attr is None:
            # If the "typing_extensions" module is importable, raise an
            # appropriate exception.
            if is_module('typing_extensions'):
                raise exception_cls(
                    f'Typing attributes "typing.{typing_attr_basename}" and '
                    f'"typing_extensions.{typing_attr_basename}" not found. '
                    f'Please update the currently installed version of the '
                    f'"typing_extensions" package and try again. '
                    f'We apologize for this inconvenience and hope you had a '
                    f'great day flying with Air Beartype, "Your Grizzled Pal '
                    f'in the Friendly Skies."'
                )
            # Else, the "typing_extensions" module is unimportable. In this
            # case, raise an appropriate exception.
            else:
                raise exception_cls(
                    f'Typing attributes "typing.{typing_attr_basename}" and '
                    f'"typing_extensions.{typing_attr_basename}" not found. '
                    f'Please install the "typing_extensions" package and try '
                    f'again. We apologize for this inconvenience and hope you '
                    f'had a great day flying with Air Beartype, "Your '
                    f'Grizzled Pal in the Friendly Skies."'
                )
        # Else, the "typing_extensions" module declares this attribute.
    # Else, the "typing" module declares this attribute.

    # Return this attribute.
    return typing_attr

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Permit redefinition of these globals below.
    global HINT_ATTR_LIST, HINT_ATTR_TUPLE

    # Defer initialization-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

    # If the active Python interpreter targets at least Python >= 3.9...
    if IS_PYTHON_AT_LEAST_3_9:
        # Initialize PEP 585-compliant types.
        HINT_ATTR_LIST = list
        HINT_ATTR_TUPLE = tuple
    # Else...
    else:
        from typing import List, Tuple

        # Default PEP 585-compliant types unavailable under this interpreter to
        # corresponding albeit deprecated "typing" singletons.
        HINT_ATTR_LIST = List
        HINT_ATTR_TUPLE = Tuple

# Initialize this submodule.
_init()
