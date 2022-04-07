#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Testing-specific **typing attribute utilities** (i.e., functions introspecting
attributes with arbitrary names dynamically imported from typing modules).
'''

# ....................{ IMPORTS                           }....................
from beartype.typing import (
    Any,
    Iterable,
    Tuple,
)
from beartype._util.mod.utilmodimport import import_module_attr_or_none

# ....................{ CONSTANTS                         }....................
TYPING_MODULE_NAMES_STANDARD = (
    'beartype.typing',
    'typing',
)
'''
Tuple of the fully-qualified names of all **standard typing modules** (i.e.,
modules whose public APIs *exactly* conform to that of the standard
:mod:`typing` module).

This tuple includes both the standard :mod:`typing` module and comparatively
more standard :mod:`beartype.typing` submodule while excluding the third-party
:mod:`typing_extensions` module, whose runtime behaviour often significantly
diverges in non-standard fashion from that of the aforementioned modules.
'''


TYPING_MODULE_NAMES_ALL = TYPING_MODULE_NAMES_STANDARD + (
    'typing_extensions',
)
'''
Tuple of the fully-qualified names of all quasi-standard typing modules.
'''

# ....................{ TESTERS                           }....................
def is_typing_attrs(typing_attr_basename: str) -> bool:
    '''
    ``True`` only if at least one quasi-standard typing module declares an
    attribute with the passed basename.

    Attributes
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be tested as existing in at least
        one typing module.

    Returns
    ----------
    bool
        ``True`` only if at least one quasi-standard typing module declares an
        attribute with this basename.
    '''
    assert isinstance(typing_attr_basename, str), (
        f'{typing_attr_basename} not string.')

    # Return true only if at least one typing module defines an attribute with
    # this name. Glory be to the obtuse generator comprehension expression!
    return bool(tuple(iter_typing_attrs(typing_attr_basename)))

# ....................{ ITERATORS                         }....................
def iter_typing_attrs(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    typing_module_names: Tuple[str] = TYPING_MODULE_NAMES_ALL,
) -> Iterable[object]:
    '''
    Generator iteratively yielding all attributes with the passed basename
    declared by the quasi-standard typing modules with the passed
    fully-qualified names, silently ignoring those modules failing to declare
    such an attribute.

    Attributes
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be dynamically imported from each
        typing module.
    typing_module_names: Tuple[str]
        Tuple of the fully-qualified names of all typing modules to dynamically
        import this attribute from. Defaults to
        :data:`TYPING_MODULE_NAMES_ALL`.

    Yields
    ----------
    object
        Each attribute with the passed basename declared by each typing module.
    '''
    assert isinstance(typing_attr_basename, str), (
        f'{typing_attr_basename} not string.')
    assert isinstance(typing_module_names, tuple), (
        f'{repr(typing_module_names)} not tuple.')
    assert typing_module_names, '"typing_module_names" empty.'
    assert all(
        isinstance(typing_attr_basename, str)
        for typing_attr_basename in typing_module_names
    ), f'One or more {typing_module_names} items not strings.'

    # For the fully-qualified name of each quasi-standard typing module...
    for typing_module_name in typing_module_names:
        # Attribute with this name dynamically imported from that module if
        # that module defines this attribute *OR* "None" otherwise.
        typing_attr = import_module_attr_or_none(
            module_attr_name=f'{typing_module_name}.{typing_attr_basename}',
            exception_prefix='Typing attribute ',
        )

        # If that module defines this attribute, yield this attribute.
        if typing_attr is not None:
            yield typing_attr
        # Else, that module fails to define this attribute. In this case,
        # silently continue to the next module.

# ....................{ IMPORTERS                         }....................
def import_typing_attr_or_none_safe(typing_attr_basename: str) -> Any:
    '''
    Dynamically import and return the **typing attribute** (i.e., object
    declared at module scope by either the :mod:`typing` or
    :mod:`typing_extensions` modules) with the passed unqualified name if
    importable from one or more of these modules *or* ``None`` otherwise
    otherwise (i.e., if this attribute is *not* importable from these modules).

    Caveats
    ----------
    **This higher-level wrapper should typically be called in lieu of the
    lower-level**
    :func:`beartype._util.mod.lib.utiltyping.import_typing_attr_or_none`
    **function.** Unlike the latter, this wrapper imports from the third-party
    :mod:`typing_extensions` module *only* if the version of that module is
    sufficiently new and thus satisfies test-time requirements.

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
    beartype.roar._roarexc._BeartypeUtilModuleException
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
    # from beartype._util.mod.utilmodimport import import_module_attr_or_none
    from beartype_test.util.mod.pytmodtest import is_package_typing_extensions
    # print(f'is_package_typing_extensions: {is_package_typing_extensions()}')

    # Return either...
    return (
        # If a reasonably recent version of the third-party "typing_extensions"
        # package is importable under the active Python interpreter, defer to
        # this higher-level importer possibly returning an attribute from that
        # package;
        import_typing_attr_or_none(typing_attr_basename)
        if is_package_typing_extensions() else
        # Else, either "typing_extensions" is unimportable or only an obsolete
        # version of "typing_extensions" is importable; in either case, avoid
        # possibly returning a possibly broken attribute from that package by
        # importing only from the official "typing" module.
        import_module_attr_or_none(f'typing.{typing_attr_basename}')
    )
