#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module utilities**.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeUtilModuleException
from types import ModuleType
from typing import Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

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
