#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module importation** utilities (i.e., functions
dynamically importing modules and/or attributes from modules).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeModuleUnimportableWarning
from beartype.roar._roarexc import _BeartypeUtilModuleException
from beartype._util.cache.utilcachecall import callable_cached
from importlib import import_module as importlib_import_module
from sys import modules as sys_modules
from types import ModuleType
from typing import Any, Optional, Type
from warnings import warn

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ IMPORTERS                         }....................
#FIXME: Preserved until requisite, which shouldn't be long.
#FIXME: Unit test us up.
# def import_module(
#     # Mandatory parameters.
#     module_name: str,
#
#     # Optional parameters.
#     exception_cls: Type[Exception] = _BeartypeUtilModuleException,
# ) -> ModuleType:
#     '''
#     Dynamically import and return the module, package, or C extension with the
#     passed fully-qualified name if importable *or* raise an exception
#     otherwise (i.e., if that module, package, or C extension is unimportable).
#
#     Parameters
#     ----------
#     module_name : str
#         Fully-qualified name of the module to be imported.
#     exception_cls : type
#         Type of exception to be raised by this function. Defaults to
#         :class:`_BeartypeUtilModuleException`.
#
#     Raises
#     ----------
#     exception_cls
#         If no module with this name exists.
#     Exception
#         If a module with this name exists *but* that module is unimportable
#         due to raising module-scoped exceptions at importation time. Since
#         modules may perform arbitrary Turing-complete logic at module scope,
#         callers should be prepared to handle *any* possible exception.
#     '''
#     assert isinstance(exception_cls, type), (
#         f'{repr(exception_cls)} not type.')
#
#     # Module with this name if this module is importable *OR* "None" otherwise.
#     module = import_module_or_none(module_name)
#
#     # If this module is unimportable, raise an exception.
#     if module is None:
#         raise exception_cls(
#             f'Module "{module_name}" not found.') from exception
#     # Else, this module is importable.
#
#     # Return this module.
#     return module


def import_module_or_none(module_name: str) -> Optional[ModuleType]:
    '''
    Dynamically import and return the module, package, or C extension with the
    passed fully-qualified name if importable *or* return ``None`` otherwise
    (i.e., if that module, package, or C extension is unimportable).

    For safety, this function also emits a non-fatal warning when that module,
    package, or C extension exists but is still unimportable (e.g., due to
    raising an exception at module scope).

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.

    Warns
    ----------
    BeartypeModuleUnimportableWarning
        If a module with this name exists *but* that module is unimportable
        due to raising module-scoped exceptions at importation time.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'

    # Module cached with "sys.modules" if this module has already been imported
    # elsewhere under the active Python interpreter *OR* "None" otherwise.
    module = sys_modules.get(module_name)

    # If this module has already been imported, return this cached module.
    if module is not None:
        return module
    # Else, this module has yet to be imported.

    # Attempt to dynamically import and return this module.
    try:
        return importlib_import_module(module_name)
    # If this module does *NOT* exist, return "None".
    except ModuleNotFoundError:
        pass
    # If this module exists but raises unexpected exceptions from module scope,
    # first emit a non-fatal warning notifying the user and then return "None".
    except Exception as exception:
        warn(
            (
                f'Ignoring module "{module_name}" importation exception '
                f'{exception.__class__.__name__}: {exception}'
            ),
            BeartypeModuleUnimportableWarning,
        )

    # Inform the caller this module is unimportable.
    return None

# ....................{ IMPORTERS ~ attr                  }....................
def import_module_attr(
    # Mandatory parameters.
    module_attr_name: str,

    # Optional parameters.
    module_attr_label: str = 'Module attribute',
    exception_cls: Type[Exception] = _BeartypeUtilModuleException,
) -> Any:
    '''
    Dynamically import and return the **module attribute** (i.e., object
    declared at module scope) with the passed fully-qualified name if
    importable *or* raise an exception otherwise.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be imported.
    module_attr_label : str
        Human-readable label prefixing this name in the exception message
        raised by this function. Defaults to ``"Module attribute"``.
    exception_cls : Type[Exception]
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

        * This name is syntactically invalid.
        * *No* module prefixed this name exists.
        * A module prefixed by this name exists *but* that module declares no
          attribute by this name.

    Warns
    ----------
    BeartypeModuleUnimportableWarning
        If a module prefixed by this name exists *but* that module is
        unimportable due to module-scoped side effects at importation time.

    See Also
    ----------
    :func:`import_module_attr_or_none`
        Further commentary.
    '''

    # Module attribute with this name if that module declares this attribute
    # *OR* "None" otherwise.
    module_attr = import_module_attr_or_none(
        module_attr_name=module_attr_name,
        module_attr_label=module_attr_label,
        exception_cls=exception_cls,
    )

    # If this module declares *NO* such attribute, raise an exception.
    if module_attr is None:
        raise exception_cls(
            f'{module_attr_label} "{module_attr_name}" unimportable.')

    # Else, return this attribute.
    return module_attr


def import_module_attr_or_none(
    # Mandatory parameters.
    module_attr_name: str,

    # Optional parameters.
    module_attr_label: str = 'Module attribute',
    exception_cls: Type[Exception] = _BeartypeUtilModuleException,
) -> Any:
    '''
    Dynamically import and return the **module attribute** (i.e., object
    declared at module scope) with the passed fully-qualified name if
    importable *or* return ``None`` otherwise.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be imported.
    module_attr_label : str
        Human-readable label prefixing this name in the exception message
        raised by this function. Defaults to ``"Module attribute"``.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`_BeartypeUtilModuleException`.

    Returns
    ----------
    object
        Either:

        * If *no* module prefixed this name exists, ``None``.
        * If a module prefixed by this name exists *but* that module declares
          no attribute by this name, ``None``.
        * Else, the module attribute with this fully-qualified name.

    Raises
    ----------
    exception_cls
        If this name is syntactically invalid.

    Warns
    ----------
    BeartypeModuleUnimportableWarning
        If a module with this name exists *but* that module is unimportable
        due to raising module-scoped exceptions at importation time.
    '''

    # Avoid circular import dependencies.
    from beartype._util.mod.utilmodtest import die_unless_module_attr_name

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

    # That module if importable *OR* "None" otherwise.
    module = import_module_or_none(module_name)

    # Return either...
    return (
        # If that module is importable, the module attribute with this name
        # if that module declares this attribute *OR* "None" otherwise;
        getattr(module, module_attr_basename, None)
        if module is not None else
        # Else, that module is unimportable. In this case, "None".
        None
    )

# ....................{ IMPORTERS ~ attr : typing         }....................
def import_module_typing_any_attr(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilModuleException,
) -> Any:
    '''
    Dynamically import and return the **typing attribute** (i.e., object
    declared at module scope by either the :mod:`typing` or
    :mod:`typing_extensions` modules) with the passed unqualified name if
    importable from one or more of these modules *or* raise an exception
    otherwise (i.e., if this attribute is *not* importable from these modules).

    This function is effectively memoized for efficiency.

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
    :exc:`exception_cls`
        If either:

        * This name is syntactically invalid.
        * Neither the :mod:`typing` nor :mod:`typing_extensions` modules
          declare an attribute with this name.

    Warns
    ----------
    BeartypeModuleUnimportableWarning
        If any of these modules raise module-scoped exceptions at importation
        time. That said, the :mod:`typing` and :mod:`typing_extensions` modules
        are scrupulously tested and thus unlikely to raise such exceptions.

    See Also
    ----------
    :func:`import_module_typing_any_attr_or_none`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.mod.utilmodtest import is_module

    # Attribute with this name imported from either the "typing" or
    # "typing_extensions" modules if one or more of these modules declare this
    # attribute *OR* "None" otherwise.
    #
    # Note that positional rather than keyword arguments are intentionally
    # passed to optimize memoization efficiency.
    typing_attr = import_module_typing_any_attr_or_none(
        typing_attr_basename, exception_cls)

    # If none of these modules declare this attribute...
    if typing_attr is None:
        # Substrings prefixing and suffixing exception messages raised below.
        EXCEPTION_PREFIX = (
            f'Typing attributes "typing.{typing_attr_basename}" and '
            f'"typing_extensions.{typing_attr_basename}" not found. '
        )
        EXCEPTION_SUFFIX = (
            'We apologize for the inconvenience and hope you had a '
            'great dev cycle flying with Air Beartype, '
            '"Your Grizzled Pal in the Friendly Skies."'
        )

        # If the "typing_extensions" module is importable, raise an
        # appropriate exception.
        if is_module('typing_extensions'):
            raise exception_cls(
                f'{EXCEPTION_PREFIX} Please either '
                f'(A) update the "typing_extensions" package or '
                f'(B) update to a newer Python version. {EXCEPTION_SUFFIX}'
            )
        # Else, the "typing_extensions" module is unimportable. In this
        # case, raise an appropriate exception.
        else:
            raise exception_cls(
                f'{EXCEPTION_PREFIX} Please either '
                f'(A) install the "typing_extensions" package or '
                f'(B) update to a newer Python version. {EXCEPTION_SUFFIX}'
            )
    # Else, one or more of these modules declare this attribute.

    # Return this attribute.
    return typing_attr


@callable_cached
def import_module_typing_any_attr_or_none(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilModuleException,
) -> Any:
    '''
    Dynamically import and return the **typing attribute** (i.e., object
    declared at module scope by either the :mod:`typing` or
    :mod:`typing_extensions` modules) with the passed unqualified name if
    importable from one or more of these modules *or* ``None`` otherwise
    otherwise (i.e., if this attribute is *not* importable from these modules).

    Specifically, this function (in order):

    #. If the official :mod:`typing` module bundled with the active Python
       interpreter declares that attribute, dynamically imports and returns
       that attribute from that module.
    #. Else if the third-party (albeit quasi-official) :mod:`typing_extensions`
       module requiring external installation under the active Python
       interpreter declares that attribute, dynamically imports and returns
       that attribute from that module.
    #. Else, returns ``None``.

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
    :exc:`exception_cls`
        If this name is syntactically invalid.

    Warns
    ----------
    BeartypeModuleUnimportableWarning
        If any of these modules raise module-scoped exceptions at importation
        time. That said, the :mod:`typing` and :mod:`typing_extensions` modules
        are scrupulously tested and thus unlikely to raise such exceptions.
    '''

    # Attribute with this name imported from the "typing" module if that module
    # declares this attribute *OR* "None" otherwise.
    typing_attr = import_module_typing_attr_or_none(
        typing_attr_basename=typing_attr_basename, exception_cls=exception_cls)

    # If the "typing" module does *NOT* declare this attribute...
    if typing_attr is None:
        # Attribute with this name imported from the "typing_extensions" module
        # if that module declares this attribute *OR* "None" otherwise.
        typing_attr = import_module_typingextensions_attr_or_none(
            typing_attr_basename=typing_attr_basename,
            exception_cls=exception_cls,
        )
    # Else, the "typing" module declares this attribute.

    # Return either this attribute if one or more of these modules declare this
    # attribute *OR* "None" otherwise.
    return typing_attr

# ....................{ IMPORTERS ~ attr : typing : module}....................
def import_module_typing_attr_or_none(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilModuleException,
) -> Any:
    '''
    The **typing attribute** (i.e., object declared at module scope by the
    :mod:`typing` module) with the passed unqualified name if importable from
    that module *or* ``None`` otherwise.

    Parameters
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from that module.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintPepException`.

    Returns
    ----------
    Any
        Either:

        * If the :mod:`typing` module declares an attribute with this name,
          that attribute.
        * Else, ``None``.

    Raises
    ----------
    exception_cls
        If this name is syntactically invalid.
    '''
    assert isinstance(typing_attr_basename, str), (
        f'{repr(typing_attr_basename)} not string.')

    # By the power of Greyskull!
    return import_module_attr_or_none(
        module_attr_name=f'typing.{typing_attr_basename}',
        module_attr_label='Typing attribute',
        exception_cls=exception_cls,
    )


def import_module_typingextensions_attr_or_none(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilModuleException,
) -> Any:
    '''
    The **typing attribute** (i.e., object declared at module scope by the
    :mod:`typing_extensions` module) with the passed unqualified name if
    importable from that module *or* ``None`` otherwise.

    Parameters
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from that module.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintPepException`.

    Returns
    ----------
    Any
        Either:

        * If the :mod:`typing_extension` module is both importable under the
          active Python interpreter *and* declares an attribute with this name,
          that attribute.
        * Else, ``None``.

    Raises
    ----------
    exception_cls
        If this name is syntactically invalid.
    '''
    assert isinstance(typing_attr_basename, str), (
        f'{repr(typing_attr_basename)} not string.')

    # When our powers combine!
    return import_module_attr_or_none(
        module_attr_name=f'typing_extensions.{typing_attr_basename}',
        module_attr_label='Typing attribute',
        exception_cls=exception_cls,
    )
