#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module tester** utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import importlib
from beartype.meta import _convert_version_str_to_tuple
from beartype.roar._roarexc import _BeartypeUtilModuleException
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from sys import modules as sys_modules
from typing import Type

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ VALIDATORS                        }....................
def die_unless_module_attr_name(
    # Mandatory parameters.
    module_attr_name: str,

    # Optional parameters.
    module_attr_label: str = 'Module attribute name',
    exception_cls: Type[Exception] = _BeartypeUtilModuleException,
) -> None:
    '''
    Raise an exception unless the passed string is the fully-qualified
    syntactically valid name of a **module attribute** (i.e., object declared
    at module scope by a module) that may or may not actually exist.

    This validator does *not* validate this attribute to actually exist -- only
    that the name of this attribute is syntactically valid.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be validated.
    module_attr_label : str
        Human-readable label prefixing this name in the exception message
        raised by this function. Defaults to ``"Module attribute name"``.
    exception_cls : type
        Type of exception to be raised by this function. Defaults to
        :class:`_BeartypeUtilModuleException`.

    Raises
    ----------
    exception_cls
        If either:

        * This name is *not* a string.
        * This name is a string containing either:

          * *No* ``.`` characters and thus either:

            * Is relative to the calling subpackage and thus *not*
              fully-qualified (e.g., ``muh_submodule``).
            * Refers to a builtin object (e.g., ``str``). While technically
              fully-qualified, the names of builtin objects are *not*
              explicitly importable as is. Since these builtin objects are
              implicitly imported everywhere, there exists *no* demonstrable
              reason to even attempt to import them anywhere.

          * One or more ``.`` characters but syntactically invalid as a
            classname (e.g., ``0h!muh?G0d.``).
    '''
    assert isinstance(module_attr_label, str), (
        f'{repr(module_attr_label)} not string.')
    assert isinstance(exception_cls, type), (
        f'{repr(exception_cls)} not type.')

    # Avoid circular import dependencies.
    from beartype._util.text.utiltextidentifier import is_identifier

    # If this object is *NOT* a string, raise an exception.
    if not isinstance(module_attr_name, str):
        raise exception_cls(
            f'{module_attr_label} {repr(module_attr_name)} not string.')
    # Else, this object is a string.
    #
    # If this string contains *NO* "." characters and thus either is relative
    # to the calling subpackage or refers to a builtin object, raise an
    # exception.
    elif '.' not in module_attr_name:
        raise exception_cls(
            f'{module_attr_label} "{module_attr_name}" '
            f'relative or refers to builtin object '
            f'(i.e., due to containing no "." characters).'
        )
    # Else, this string contains one or more "." characters and is thus the
    # fully-qualified name of a non-builtin type.
    #
    # If this string is syntactically invalid as a fully-qualified module
    # attribute name, raise an exception.
    elif not is_identifier(module_attr_name):
        raise exception_cls(
            f'{module_attr_label} "{module_attr_name}" '
            f'syntactically invalid as module attribute name.'
        )
    # Else, this string is syntactically valid as a fully-qualified module
    # attribute name.

# ....................{ TESTERS                           }....................
def is_module(module_name: str) -> bool:
    '''
    ``True`` only if the module, package, or C extension with the passed
    fully-qualified name is importable under the active Python interpreter.

    Caveats
    ----------
    **This tester dynamically imports this module as an unavoidable side effect
    of performing this test.**

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.

    Returns
    ----------
    bool
        ``True`` only if this module is importable.

    Raises
    ----------
    Exception
        If a module with this name exists *but* this module is unimportable
        due to module-scoped side effects at importation time. Since modules
        may perform arbitrary Turing-complete logic from module scope, callers
        should be prepared to handle *any* possible exception that might arise.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'

    # If this module has already been imported, return true.
    if module_name in sys_modules:
        return True
    # Else, this module has yet to be imported.

    # Attempt to...
    try:
        # Dynamically import this module.
        importlib.import_module(module_name)

        # Return true, since this importation succeeded.
        return True
    # If no module this this name exists, return false.
    except ModuleNotFoundError:
        return False
    # If any other exception was raised, silently permit that exception to
    # unwind the call stack.


#FIXME: Unit test us up against "setuptools", the only third-party package
#*BASICALLY* guaranteed to be importable.
def is_module_version_at_least(module_name: str, version_minimum: str) -> bool:
    '''
    ``True`` only if the module, package, or C extension with the passed
    fully-qualified name is both importable under the active Python interpreter
    *and* at least as new as the passed version.

    Caveats
    ----------
    **This tester dynamically imports this module as an unavoidable side effect
    of performing this test.**

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.
    version_minimum: str
        Minimum version to test this module against as a dot-delimited
        :pep:`440`-compliant version specifier (e.g., ``42.42.42rc42.post42``).

    Returns
    ----------
    bool
        ``True`` only if:

        * This module is importable.
        * This module's version is at least the passed version.

    Raises
    ----------
    Exception
        If a module with this name exists *but* this module is unimportable
        due to module-scoped side effects at importation time. Since modules
        may perform arbitrary Turing-complete logic from module scope, callers
        should be prepared to handle *any* possible exception that might arise.
    '''

    # If it is *NOT* the case that...
    if not (
        # This module is importable *AND*...
        is_module(module_name) and
        # The active Python interpreter targets Python >= 3.8 and thus provides
        # the "importlib.metadata" API required to portably inspect module
        # versions *WITHOUT* requiring obsolete third-party APIs (e.g.,
        # "pkg_resources")...
        IS_PYTHON_AT_LEAST_3_8
    ):
    # Then this module is either unimportable *OR* the active Python
    # interpreter targets Python < 3.8 and thus fails to provide that API.
    # In either case, return false to avoid returning false positives.
        return False
    assert isinstance(version_minimum, str), (
        f'{repr(version_minimum)} not string.')

    # Defer version-specific imports.
    from importlib.metadata import version as get_module_version  # type: ignore[attr-defined]

    # Current version of this module installed under the active Python
    # interpreter if any *OR* raise an exception otherwise (which should
    # *NEVER* happen by prior logic validating this module to be importable).
    version_actual = get_module_version(module_name)

    # Tuples of version specifier parts parsed from version specifier strings.
    version_actual_parts  = _convert_version_str_to_tuple(version_actual)
    version_minimum_parts = _convert_version_str_to_tuple(version_minimum)

    # Return true only if this module's current version satisfies this minimum.
    return version_actual_parts >= version_minimum_parts
