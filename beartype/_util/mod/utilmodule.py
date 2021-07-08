#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module utilities**.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import importlib
from beartype.roar._roarexc import _BeartypeUtilModuleException
from sys import modules as sys_modules
from types import ModuleType
from typing import Any, Optional, Type

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

# ....................{ GETTERS ~ object : name           }....................
def get_object_module_name(obj: object) -> str:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited name prefixed by the
    declaring package) of the module declaring the passed object if this
    object defines the ``__module__`` dunder instance variable *or* ``None``
    otherwise.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    str
        Fully-qualified name of the module declaring this object.

    Raises
    ----------
    _BeartypeUtilModuleException
        If this object does *not* define the ``__module__`` dunder instance
        variable.
    '''

    # Fully-qualified name of the module declaring this object if this object
    # defines the "__module__" dunder instance variable *OR* "None" otherwise.
    module_name = get_object_module_name_or_none(obj)

    # If this object defines *NO* "__module__" dunder instance variable, raise
    # an exception.
    if module_name is None:
        raise _BeartypeUtilModuleException(
            f'{repr(obj)} "__module__" dunder attribute undefined '
            f'(e.g., due to being neither class nor callable).'
        )
    # Else, this fully-qualified module name exists.

    # Return this name.
    return module_name


def get_object_module_name_or_none(obj: object) -> Optional[str]:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited name prefixed by the
    declaring package) of the module declaring the passed object if this object
    defines the ``__module__`` dunder instance variable *or* ``None``
    otherwise.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    Optional[str]
        Either:

        * Fully-qualified name of the module declaring this object if this
          object declares a ``__module__`` dunder attribute.
        * ``None`` otherwise.
    '''

    # Let it be, speaking one-liners of wisdom.
    return getattr(obj, '__module__', None)


def get_object_type_module_name_or_none(obj: object) -> Optional[str]:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited name prefixed by the
    declaring package) of the module declaring either the passed object if this
    object is a class *or* the class of this object otherwise (i.e., if this
    object is *not* a class) if this class declares the ``__module__`` dunder
    instance variable *or* ``None`` otherwise.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    Optional[str]
        Either:

        * Fully-qualified name of the module declaring the type of this object
          if this type declares a ``__module__`` dunder attribute.
        * ``None`` otherwise.
    '''

    # Avoid circular import dependencies.
    from beartype._util.utilobject import get_object_type_unless_type

    # Make it so, ensign.
    return get_object_module_name_or_none(get_object_type_unless_type(obj))

# ....................{ GETTERS ~ module : file           }....................
#FIXME: Unit test us up.
def get_module_filename(module: ModuleType) -> str:
    '''
    Absolute filename of the passed module if this module is physically defined
    on disk *or* raise an exception otherwise (i.e., if this module is
    abstractly defined in memory).

    Parameters
    ----------
    module : ModuleType
        Module to be inspected.

    Returns
    ----------
    str
        Absolute filename of this on-disk module.

    Raises
    ----------
    _BeartypeUtilModuleException
        If this module *only* resides in memory.
    '''

    # Absolute filename of this module if on-disk *OR* "None" otherwise.
    module_filename = get_module_filename_or_none(module)

    # If this module resides *ONLY* in memory, raise an exception.
    if module_filename is None:
        raise _BeartypeUtilModuleException(
            f'Module {repr(module)} not on disk.')
    # Else, this module resides on disk.

    # Return this filename.
    return module_filename


#FIXME: Unit test us up.
def get_module_filename_or_none(module: ModuleType) -> Optional[str]:
    '''
    Absolute filename of the passed module if this module is physically defined
    on disk *or* ``None`` otherwise (i.e., if this module is abstractly defined
    in memory).

    Parameters
    ----------
    module : ModuleType
        Module to be inspected.

    Returns
    ----------
    Optional[str]
        Either:

        * Absolute filename of this module if this module resides on disk.
        * ``None`` if this module *only* resides in memory.
    '''

    # Thus spake Onelinerthustra.
    return getattr(module, '__file__', None)

# ....................{ IMPORTERS                         }....................
def import_module(
    # Mandatory parameters.
    module_name: str,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilModuleException,
) -> ModuleType:
    '''
    Dynamically import and return the module, package, or C extension with the
    passed fully-qualified name if importable *or* raise an exception
    otherwise.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.
    exception_cls : type
        Type of exception to be raised by this function. Defaults to
        :class:`_BeartypeUtilModuleException`.

    Raises
    ----------
    exception_cls
        If no module with this name exists.
    Exception
        If a module with this name exists *but* this module is unimportable
        due to module-scoped side effects at importation time. Since modules
        may perform arbitrary Turing-complete logic from module scope, callers
        should be prepared to handle *any* possible exception that might arise.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'
    assert isinstance(exception_cls, type), (
        f'{repr(exception_cls)} not type.')

    # Attempt to dynamically import and return this module.
    try:
        return importlib.import_module(module_name)
    # If no module this this name exists, raise a beartype-specific exception
    # wrapping this beartype-agnostic exception to sanitize our public API,
    # particularly from the higher-level import_module_attr() function calling
    # this lower-level function and raising the same exception class under a
    # wider variety of fatal edge cases.
    except ModuleNotFoundError as exception:
        raise exception_cls(
            f'Module "{module_name}" not found.') from exception


def import_module_attr(
    # Mandatory parameters.
    module_attr_name: str,

    # Optional parameters.
    module_attr_label: str = 'Module attribute name',
    exception_cls:  type = _BeartypeUtilModuleException,
) -> Any:
    '''
    Dynamically import and return the **module attribute** (i.e., object
    declared at module scope by a module) with the passed fully-qualified name
    if importable *or* raise an exception otherwise.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be imported.
    module_attr_label : str
        Human-readable label prefixing this name in the exception message
        raised by this function. Defaults to ``"Module attribute name"``.
    exception_cls : type
        Type of exception to be raised by this function. Defaults to
        :class:`_BeartypeUtilModuleException`.

    Returns
    ----------
    object
        The module attribute with this fully-qualified name.

    Raises
    ----------
    exception_cls
        If either:

        * This name is *not* a syntactically valid fully-qualified module
          attribute name.
        * *No* module prefixed this name exists.
        * An importable module prefixed by this name exists *but* this module
          declares no attribute by this name.
    Exception
        If a module prefixed this name exists but this module is unimportable
        due to module-scoped side effects at importation time. Since modules
        may perform arbitrary Turing-complete logic from module scope, callers
        should be prepared to handle *any* possible exception that might arise.
    '''

    # If this object is *NOT* the fully-qualified syntactically valid name of a
    # module attribute that may or may not actually exist, raise an exception.
    die_unless_module_attr_name(
        module_attr_name=module_attr_name,
        module_attr_label=module_attr_label,
        exception_cls=exception_cls,
    )
    # Else, this object is the fully-qualified syntactically valid name of a
    # module attribute. In particular, this implies this name to contain one or
    # more "." delimiters.

    # Fully-qualified name of the module declaring this attribute *AND* the
    # unqualified name of this attribute relative to this module, efficiently
    # split from the passed name. By the prior validation, this split is
    # guaranteed to be safe.
    module_name, _, module_attr_basename = module_attr_name.rpartition('.')

    # Dynamically import this module.
    module = import_module(
        module_name=module_name, exception_cls=exception_cls)

    # Module attribute with this name if this module declares this attribute
    # *OR* "None" otherwise.
    module_attr = getattr(module, module_attr_basename, None)

    # If this module declares *NO* such attribute, raise an exception.
    if module_attr is None:
        raise exception_cls(
            f'{module_attr_label} '
            f'"{module_name}.{module_attr_name}" not found.'
        )

    # Else, return this attribute.
    return module_attr
