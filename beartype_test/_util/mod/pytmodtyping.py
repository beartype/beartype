#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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
    Union,
)
from beartype._util.mod.utilmodimport import import_module_attr_or_none
from beartype._data.mod.datamodtyping import TYPING_MODULE_NAMES
from collections.abc import Iterable as IterableABC
from warnings import warn

# ....................{ TESTERS                           }....................
def is_typing_attrs(typing_attr_basenames: Union[str, Iterable[str]]) -> bool:
    '''
    ``True`` only if at least one quasi-standard typing module declares an
    attribute with the passed basename.

    Attributes
    ----------
    typing_attr_basenames : Union[str, Iterable[str]]
        Unqualified name of the attribute to be tested as existing in at least
        one typing module.

    Returns
    ----------
    bool
        ``True`` only if at least one quasi-standard typing module declares an
        attribute with this basename.
    '''

    # Return true only if at least one typing module defines an attribute with
    # this name. Glory be to the obtuse generator comprehension expression!
    return bool(tuple(iter_typing_attrs(
        typing_attr_basenames=typing_attr_basenames,
        is_warn=False,
    )))

# ....................{ ITERATORS                         }....................
#FIXME: Generalize to also accept an iterable of typing attribute basenames.
def iter_typing_attrs(
    # Mandatory parameters.
    typing_attr_basenames: Union[str, Iterable[str]],

    # Optional parameters.
    is_warn: bool = False,
    typing_module_names: Iterable[str] = TYPING_MODULE_NAMES,
) -> Iterable[Union[object, Tuple[object]]]:
    '''
    Generator iteratively yielding all attributes with the passed basename
    declared by the quasi-standard typing modules with the passed
    fully-qualified names, silently ignoring those modules failing to declare
    such an attribute.

    Attributes
    ----------
    typing_attr_basenames : Union[str, Iterable[str]]
        Either:

        * Unqualified name of the attribute to be dynamically imported from
          each typing module, in which case either:

          * If the currently iterated typing module defines this attribute,
            this generator yields this attribute imported from that module.
          * Else, this generator silently ignores that module.
        * Iterable of one or more such names, in which case either:

          * If the currently iterated typing module defines *all* attributes,
            this generator yields a tuple whose items are these attributes
            imported from that module (in the same order).
          * Else, this generator silently ignores that module.
    is_warn : bool
        ``True`` only if emitting non-fatal warnings for typing modules failing
        to define all passed attributes. If ``typing_module_names`` is passed,
        this parameter should typically also be passed as ``True`` for safety.
        Defaults to ``False``.
    typing_module_names: Iterable[str]
        Iterable of the fully-qualified names of all typing modules to
        dynamically import this attribute from. Defaults to
        :data:`TYPING_MODULE_NAMES`.

    Yields
    ----------
    Union[object, Tuple[object]]
        Either:

        * If passed only an attribute basename, the attribute with that
          basename declared by each typing module.
        * If passed an iterable of one or more attribute basenames, a tuple
          whose items are the attributes with those basenames (in the same
          order) declared by each typing module.
    '''
    assert isinstance(is_warn, bool), f'{is_warn} not boolean.'
    assert isinstance(typing_attr_basenames, (str, IterableABC)), (
        f'{typing_attr_basenames} not string.')
    assert typing_attr_basenames, '"typing_attr_basenames" empty.'
    assert isinstance(typing_module_names, IterableABC), (
        f'{repr(typing_module_names)} not iterable.')
    assert typing_module_names, '"typing_module_names" empty.'
    assert all(
        isinstance(typing_module_name, str)
        for typing_module_name in typing_module_names
    ), f'One or more {typing_module_names} items not strings.'

    # If passed an attribute basename, pack this into a tuple containing only
    # this basename for ease of use.
    if isinstance(typing_attr_basenames, str):
        typing_attr_basenames = (typing_attr_basenames,)
    # Else, an iterable of attribute basenames was passed. In this case...
    else:
        assert all(
            isinstance(typing_attr_basename, str)
            for typing_attr_basename in typing_attr_basenames
        ), f'One or more {typing_attr_basenames} items not strings.'

    # List of all imported attributes to be yielded from each iteration of the
    # generator implicitly returned by this generator function.
    typing_attrs = []

    # For the fully-qualified name of each quasi-standard typing module...
    for typing_module_name in typing_module_names:
        # Clear this list *BEFORE* appending to this list below.
        typing_attrs.clear()

        # For the basename of each attribute to be imported from that module...
        for typing_attr_basename in typing_attr_basenames:
            # Fully-qualified name of this attribute declared by that module. 
            module_attr_name = f'{typing_module_name}.{typing_attr_basename}'

            # Attribute with this name dynamically imported from that module if
            # that module defines this attribute *OR* "None" otherwise.
            typing_attr = import_module_attr_or_none(
                module_attr_name=module_attr_name,
                exception_prefix=f'"{typing_module_name}" attribute ',
            )

            # If that module fails to declare even a single attribute...
            if typing_attr is None:
                # If emitting non-fatal warnings, do so.
                if is_warn:
                    warn(
                        f'Ignoring undefined typing attribute '
                        f'"{module_attr_name}"...'
                    )

                # Continue to the next module.
                break
            # Else, that module declares this attribute.

            # Append this attribute to this list.
            typing_attrs.append(typing_attr)
        # If that module declares *ALL* attributes...
        else:
            # If exactly one attribute name was passed, yield this attribute
            # as is (*WITHOUT* packing this attribute into a tuple).
            if len(typing_attrs) == 1:
                yield typing_attrs[0]
            # Else, two or more attribute names were passed. In this case,
            # yield these attributes as a tuple.
            else:
                yield tuple(typing_attrs)
        # Else, that module failed to declare one or more attributes. In this
        # case, silently continue to the next module.

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

    # Defer test-specific imports.
    from beartype._util.mod.lib.utiltyping import import_typing_attr_or_none
    # from beartype._util.mod.utilmodimport import import_module_attr_or_none
    from beartype_test._util.mod.pytmodtest import is_package_typing_extensions
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
