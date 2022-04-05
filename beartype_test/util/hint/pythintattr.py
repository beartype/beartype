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
    Iterable,
    Tuple,
)
from beartype._util.mod.utilmodimport import import_module_attr_or_none

# ....................{ PRIVATE                           }....................
_TYPING_MODULE_NAMES = (
    'beartype.typing',
    'typing',
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
    typing_module_names: Tuple[str] = _TYPING_MODULE_NAMES,
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
        import this attribute from. Defaults to :data:`_TYPING_MODULE_NAMES`.

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
