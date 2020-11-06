#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype Python module utilities.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import importlib
from beartype.roar import BeartypeUtilModuleException

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                          }....................
MODULE_NAME_BUILTINS = 'builtins'
'''
Fully-qualified name of the module declaring all **builtins** (i.e., objects
defined by the standard :mod:`builtins` module and thus globally available by
default *without* requiring explicit importation).
'''


MODULE_NAME_BUILTINS_DOTTED = f'{MODULE_NAME_BUILTINS}.'
'''
Fully-qualified name of the module declaring all builtins followed by a ``.``,
defined purely as a trivial optimization for the frequently accessed
:class:`beartype._decor._typistry.Beartypistry.__setitem__` dunder method.
'''

# ....................{ IMPORTERS                         }....................
def import_module(module_name: str) -> 'ModuleType':
    '''
    Dynamically import and return the module, package, or C extension with the
    passed fully-qualified name if importable *or* raise an exception
    otherwise.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.

    Raises
    ----------
    BeartypeUtilModuleException
        If no module with this name exists.
    Exception
        If a module with this name exists *but* this module is unimportable
        due to module-scoped side effects at importation time. Since modules
        may perform arbitrary Turing-complete logic from module scope, callers
        should be prepared to handle *any* possible exception that might arise.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'

    # Attempt to dynamically import and return this module.
    try:
        return importlib.import_module(module_name)
    # If no module this this name exists, raise a beartype-specific exception
    # wrapping this beartype-agnostic exception to sanitize our public API,
    # particularly from the higher-level import_module_attr() function calling
    # this lower-level function and raising the same exception class under a
    # wider variety of fatal edge cases.
    except ModuleNotFoundError as exception:
        raise BeartypeUtilModuleException(
            f'Module "{module_name}" not found.') from exception


#FIXME: Unit test us up.
def import_module_attr(module_attr_name: str) -> object:
    '''
    Dynamically import and return the **module attribute** (i.e., object
    declared at module scope by a module) with the passed fully-qualified name
    if importable *or* raise an exception otherwise.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be imported.

    Returns
    ----------
    object
        The module attribute with this fully-qualified name.

    Raises
    ----------
    BeartypeUtilModuleException
        If either:

        * This name contains *no* ``.`` characters and thus either:

          * Is relative to the calling subpackage and thus *not*
            fully-qualified (e.g., ``muh_submodule``).
          * Refers to a builtin object (e.g., ``str``). While technically
            fully-qualified, the names of builtin objects are *not* explicitly
            importable as is. Since these builtin objects are implicitly
            imported everywhere, there exists *no* demonstrable reason to even
            attempt to import them anywhere.

        * *No* module prefixed this name exists.
        * An importable module prefixed by this name exists *but* this module
          declares no attribute by this name.
    Exception
        If a module prefixed this name exists but this module is unimportable
        due to module-scoped side effects at importation time. Since modules
        may perform arbitrary Turing-complete logic from module scope, callers
        should be prepared to handle *any* possible exception that might arise.
    '''
    assert isinstance(module_attr_name, str), (
        f'{repr(module_attr_name)} not string.')

    # If this name contains *NO* "." characters and thus either is relative to
    # the calling subpackage or refers to a builtin object, raise an exception.
    if '.' not in module_attr_name:
        raise BeartypeUtilModuleException(
            f'Module attribute "{module_attr_name}" '
            f'relative or refers to builtin object '
            f'(i.e., due to containing no "." characters).'
        )
    # Else, this name contains one or more "." characters and is thus
    # fully-qualified.

    # Fully-qualified name of the module declaring this attribute *AND* the
    # unqualified name of this attribute relative to this module, efficiently
    # split from the passed name. By the prior validation, this split is
    # guaranteed to be safe.
    #
    # Note that, in general, the str.rsplit() method is *NOT* necessarily safe.
    # Specifically, that method silently returns a 1-list containing the
    # subject string when that string fails to contain the passed substring
    # rather than raising a fatal exception or emitting a non-fatal warning:
    #     >>> 'wtfguido'.rsplit('.', maxsplit=1)
    #     ['wtfguido']     # <------ this is balls, folks.
    module_name, module_attr_basename = module_attr_name.rsplit(
        '.', maxsplit=1)

    # Dynamically import this module.
    module = import_module(module_name)

    # Module attribute with this name if this module declares this attribute
    # *OR* "None" otherwise.
    module_attr = getattr(module, module_attr_basename)

    # If this module declares *NO* such attribute, raise an exception.
    if module_attr is None:
        raise BeartypeUtilModuleException(
            f'Module attribute "{module_attr_name}" not found.')

    # Else, return this attribute.
    return module_attr