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
from beartype.roar import _BeartypeUtilModuleException

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

# ....................{ VALIDATORS                        }....................
def die_unless_module_attr_name(
    # Mandatory parameters.
    module_attr_name: str,

    # Optional parameters.
    exception_label: 'Optional[str]' = 'Module attribute name',
    exception_cls:   'Optional[type]' = _BeartypeUtilModuleException,
) -> object:
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
    exception_label : Optional[str]
        Human-readable label prefixing this name in the exception message
        raised by this function. Defaults to ``"Module attribute name"``.
    exception_cls : Optional[type]
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
    assert isinstance(exception_label, str), (
        f'{repr(exception_label)} not string.')
    assert isinstance(exception_cls, type), (
        f'{repr(exception_cls)} not type.')

    # Avoid circular import dependencies.
    from beartype._util.py.utilpyidentifier import is_identifiers_joined

    # If this object is *NOT* a string, raise an exception.
    if not isinstance(module_attr_name, str):
        raise exception_cls(
            f'{exception_label} {repr(module_attr_name)} not string.')
    # Else, this object is a string.
    #
    # If this string contains *NO* "." characters and thus either is relative
    # to the calling subpackage or refers to a builtin object, raise an
    # exception.
    elif '.' not in module_attr_name:
        raise exception_cls(
            f'{exception_label} "{module_attr_name}" '
            f'relative or refers to builtin object '
            f'(i.e., due to containing no "." characters).'
        )
    # Else, this string contains one or more "." characters and is thus the
    # fully-qualified name of a non-builtin type.
    #
    # If this string is syntactically invalid as a fully-qualified module
    # attribute name, raise an exception.
    elif not is_identifiers_joined(module_attr_name):
        raise exception_cls(
            f'{exception_label} "{module_attr_name}" '
            f'syntactically invalid as module attribute name.'
        )
    # Else, this string is syntactically valid as a fully-qualified module
    # attribute name.

# ....................{ GETTERS ~ name                    }....................
def get_object_module_name(obj: object) -> 'Optional[str]':
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
    Optional[str]
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


def get_object_module_name_or_none(obj: object) -> 'Optional[str]':
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
    Optional[str]
        Either:

        * Fully-qualified name of the module declaring this object if this
          object declares a ``__module__`` dunder attribute.
        * ``None`` otherwise.
    '''

    # Let it be, speaking one-liners of wisdom.
    return getattr(obj, '__module__', None)


def get_object_class_module_name_or_none(obj: object) -> 'Optional[str]':
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
    from beartype._util.utilobject import get_object_class_unless_class

    # Make it so, ensign.
    return get_object_module_name_or_none(get_object_class_unless_class(obj))

# ....................{ GETTERS ~ attr : name             }....................
def get_module_attr_name_relative_to_obj(
    obj: object, module_attr_name: str) -> str:
    '''
    **Fully-qualified module attribute name** (i.e., ``.``-delimited name
    prefixed by the declaring module) canonicalized by concatenating the
    fully-qualified name of the module declaring the passed object with the
    passed unqualified basename if this basename is unqualified (i.e., contains
    *no* ``.`` characters) *or* this basename as is otherwise (i.e., if this
    basename is already fully qualified).

    Specifically, this function:

    * If the passed ``module_attr_name`` is already fully-qualified (i.e.,
      contains one or more ``.`` characters), returns this string as is.
    * Else if the passed ``module_obj`` does *not* define the ``__module__``
      dunder attribute whose value is the fully-qualified name of the module
      declaring this object, raise an exception. Note that most objects do
      *not* define this attribute. Those that do include:

      * Classes.
      * Callables (e.g., functions, methods).

    * Else, returns ``f'{module_obj.__module__}.{module_attr_name}``.

    Parameters
    ----------
    obj : object
        Object to canonicalize the passed unqualified basename relative to.
    module_attr_name : str
        Unqualified basename to be canonicalized relative to the module
        declaring this object.

    Returns
    ----------
    str
        Fully-qualified name of this module attribute.

    Raises
    ----------
    _BeartypeUtilModuleException
        If ``module_obj`` does *not* define the ``__module__`` dunder instance
        variable.
    '''
    assert isinstance(module_attr_name, str), (
        f'{repr(module_attr_name)} not string.')

    # Return either...
    return (
        # If this name contains one or more "." characters and is thus already
        # fully-qualified, this name as is.
        module_attr_name
        if '.' in module_attr_name else
        # Else, the "."-delimited concatenation of the fully-qualified name of
        # the module declaring this object with this unqualified basename.
        f'{get_object_module_name(obj)}.{module_attr_name}'
    )

# ....................{ IMPORTERS                         }....................
def import_module(
    # Mandatory parameters.
    module_name: str,

    # Optional parameters.
    exception_cls:   'Optional[type]' = _BeartypeUtilModuleException,
) -> 'ModuleType':
    '''
    Dynamically import and return the module, package, or C extension with the
    passed fully-qualified name if importable *or* raise an exception
    otherwise.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.
    exception_cls : Optional[type]
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
    exception_label: 'Optional[str]' = 'Module attribute name',
    exception_cls:   'Optional[type]' = _BeartypeUtilModuleException,
) -> object:
    '''
    Dynamically import and return the **module attribute** (i.e., object
    declared at module scope by a module) with the passed fully-qualified name
    if importable *or* raise an exception otherwise.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be imported.
    exception_label : Optional[str]
        Human-readable label prefixing this name in the exception message
        raised by this function. Defaults to ``"Module attribute name"``.
    exception_cls : Optional[type]
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
        exception_label=exception_label,
        exception_cls=exception_cls,
    )
    # Else, this object is the fully-qualified syntactically valid name of a
    # module attribute. In particular, this implies this name to contain one or
    # more "." delimiters.

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
    module = import_module(
        module_name=module_name,
        exception_cls=exception_cls,
    )

    # Module attribute with this name if this module declares this attribute
    # *OR* "None" otherwise.
    module_attr = getattr(module, module_attr_basename, None)

    # If this module declares *NO* such attribute, raise an exception.
    if module_attr is None:
        raise exception_cls(
            f'{exception_label} "{module_attr_name}" not found.')

    # Else, return this attribute.
    return module_attr
