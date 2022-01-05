#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Test-specific **Python module importation** utilities.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from typing import Any

# ....................{ IMPORTERS ~ typing                }....................
def import_module_typing_any_attr_or_none_safe(
    typing_attr_basename: str) -> Any:
    '''
    Dynamically import and return the **typing attribute** (i.e., object
    declared at module scope by either the :mod:`typing` or
    :mod:`typing_extensions` modules) with the passed unqualified name if
    importable from one or more of these modules *or* ``None`` otherwise
    otherwise (i.e., if this attribute is *not* importable from these modules).

    Parameters
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from a typing module.

    Returns
    ----------
    object
        Attribute with this name dynamically imported from a typing module.

    Raises
    ----------
    :exc:`beartype.roar._roarexc._BeartypeUtilModuleException`
        If this name is syntactically invalid.

    Warns
    ----------
    BeartypeModuleUnimportableWarning
        If any of these modules raise module-scoped exceptions at importation
        time. That said, the :mod:`typing` and :mod:`typing_extensions` modules
        are scrupulously tested and thus unlikely to raise such exceptions.
    '''

    # Defer heavyweight imports.
    from beartype._util.mod.lib.utiltyping import import_typing_attr_or_none
    from beartype._util.mod.utilmodimport import import_module_attr_or_none
    from beartype_test.util.mod.pytmodtest import is_package_typing_extensions
    # print(f'is_package_typing_extensions: {is_package_typing_extensions()}')

    # Return either...
    return (
        # If a reasonably recent version of the third-party "typing_extensions"
        # package is importable under the active Python interpreter, defer to
        # the higher-level import_module_typing_any_attr_or_none() importer
        # possibly returning an attribute from that package;
        import_typing_attr_or_none(typing_attr_basename)
        if is_package_typing_extensions() else
        # Else, either "typing_extensions" is unimportable or only an obsolete
        # version of "typing_extensions" is importable; in either case, avoid
        # possibly returning a possibly broken attribute from that package by
        # importing only from the official "typing" module.
        import_module_attr_or_none(f'typing.{typing_attr_basename}')
    )
