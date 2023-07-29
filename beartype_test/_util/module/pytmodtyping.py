#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Testing-specific **typing attribute utilities** (i.e., functions introspecting
attributes with arbitrary names dynamically imported from typing modules).
'''

# ....................{ TODO                               }....................
#FIXME: Consider excising this submodule. Ideally, *ALL* functionality defined
#by this submodule should instead reside in the central
#"beartype._util.module.lib.utiltyping" submodule, which significantly overlaps
#with this submodule in harmful way. We appear to have duplicated work between
#these two submodules unknowingly, which is simply horrid. Gah! I cry at night.

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    Iterable,
    Union,
)
from beartype._util.module.utilmodimport import import_module_attr_or_none
from beartype._util.module.lib.utiltyping import iter_typing_attrs

# ....................{ TESTERS                            }....................
def is_typing_attrs(typing_attr_basenames: Union[str, Iterable[str]]) -> bool:
    '''
    :data:`True` only if at least one quasi-standard typing module declares an
    attribute with the passed basename.

    Attributes
    ----------
    typing_attr_basenames : Union[str, Iterable[str]]
        Unqualified name of the attribute to be tested as existing in at least
        one typing module.

    Returns
    ----------
    bool
        :data:`True` only if at least one quasi-standard typing module declares
        an attribute with this basename.
    '''

    # Return true only if at least one typing module defines an attribute with
    # this name. Glory be to the obtuse generator comprehension expression!
    return bool(tuple(iter_typing_attrs(
        typing_attr_basenames=typing_attr_basenames,
        is_warn=False,
    )))

# ....................{ IMPORTERS                          }....................
#FIXME: Is this still required? Seriously. Shouldn't "typing_extensions"
#*ALWAYS* be sufficiently new under remote CI? *sigh*
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
    :func:`beartype._util.module.lib.utiltyping.import_typing_attr_or_none`
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

    # Defer test-specific imports.
    from beartype._util.module.lib.utiltyping import import_typing_attr_or_none
    # from beartype._util.module.utilmodimport import import_module_attr_or_none
    from beartype_test._util.module.pytmodtest import is_package_typing_extensions
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
