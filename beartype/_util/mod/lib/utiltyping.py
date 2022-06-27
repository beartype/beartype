#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **typing module** utilities (i.e., callables dynamically testing
and importing attributes declared at module scope by either the standard
:mod:`typing` or third-party :mod:`typing_extensions` modules).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilModuleException
from beartype.typing import Any
from beartype._util.cache.utilcachecall import callable_cached
from beartype._data.datatyping import TypeException

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_typing_attr(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
) -> bool:
    '''
    ``True`` only if a **typing attribute** (i.e., object declared at module
    scope by either the :mod:`typing` or :mod:`typing_extensions` modules) with
    the passed unqualified name is importable from one or more of these
    modules.

    This function is effectively memoized for efficiency.

    Parameters
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from a typing module.

    Returns
    ----------
    bool
        ``True`` only if the :mod:`typing` or :mod:`typing_extensions` modules
        declare an attribute with this name.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`_BeartypeUtilModuleException`.

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

    # Return true only if an attribute with this name is importable from either
    # the "typing" *OR* "typing_extensions" modules.
    #
    # Note that positional rather than keyword arguments are intentionally
    # passed to optimize memoization efficiency.
    return import_typing_attr_or_none(
        typing_attr_basename, exception_cls) is not None

# ....................{ IMPORTERS                          }....................
def import_typing_attr(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
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
        :class:`_BeartypeUtilModuleException`.

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
    typing_attr = import_typing_attr_or_none(
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


#FIXME: Unit test us up, please.
@callable_cached
def import_typing_attr_or_none(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
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
        :class:`_BeartypeUtilModuleException`.

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

    # Avoid circular import dependencies.
    from beartype._util.mod.utilmodimport import import_module_attr_or_none

    # Attribute with this name imported from the "typing" module if that module
    # declares this attribute *OR* "None" otherwise.
    typing_attr = import_module_attr_or_none(
        module_attr_name=f'typing.{typing_attr_basename}',
        exception_cls=exception_cls,
        exception_prefix='Typing attribute ',
    )

    # If the "typing" module does *NOT* declare this attribute...
    if typing_attr is None:
        # Attribute with this name imported from the "typing_extensions" module
        # if that module declares this attribute *OR* "None" otherwise.
        typing_attr = import_module_attr_or_none(
            module_attr_name=f'typing_extensions.{typing_attr_basename}',
            exception_cls=exception_cls,
            exception_prefix='Typing attribute ',
        )
    # Else, the "typing" module declares this attribute.

    # Return either this attribute if one or more of these modules declare this
    # attribute *OR* "None" otherwise.
    return typing_attr
