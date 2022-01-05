#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module deprecation** utilities (i.e., callables
deprecating arbitrary module attributes in a reusable fashion).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid circular import dependencies, avoid importing from *ANY*
# package-specific submodule either here or in the body of any callable defined
# by this submodule. This submodule is typically called from the "__init__"
# submodules of public subpackages.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._util.utilobject import SENTINEL
from typing import Dict
from warnings import warn

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ IMPORTERS                         }....................
def deprecate_module_attr(
    attr_deprecated_name: str,
    attr_deprecated_name_to_nondeprecated_name: Dict[str, str],
    attr_nondeprecated_name_to_value: Dict[str, object],
) -> object:
    '''
    Dynamically retrieve a deprecated attribute with the passed unqualified
    name mapped by the passed dictionary to a corresponding non-deprecated
    attribute from the submodule with the passed dictionary of globally scoped
    attributes and emit a non-fatal deprecation warning on each
    such retrieval if that submodule defines this attribute *or* raise an
    exception otherwise.

    This function is intended to be called by :pep:`562`-compliant globally
    scoped ``__getattr__()`` dunder functions, which the Python interpreter
    implicitly calls under Python >= 3.7 *after* failing to directly retrieve
    an explicit attribute with this name from that submodule.

    Parameters
    ----------
    attr_deprecated_name : str
        Unqualified name of the deprecated attribute to be retrieved.
    attr_deprecated_name_to_nondeprecated_name : Dict[str, str]
        Dictionary mapping from the unqualified name of each deprecated
        attribute retrieved by this function to either:

        * If that submodule defines a corresponding non-deprecated attribute,
          the unqualified name of that attribute.
        * If that submodule is deprecating that attribute *without* defining a
          corresponding non-deprecated attribute, ``None``.
    attr_nondeprecated_name_to_value : Dict[str, object]
        Dictionary mapping from the unqualified name to value of each
        module-scoped attribute defined by the caller's submodule, typically
        passed as the ``globals()`` builtin. This function intentionally does
        *not* implicitly inspect this dictionary from the call stack, as call
        stack inspection is non-portable under Python.

    Returns
    ----------
    object
        Value of this deprecated attribute.

    Warns
    ----------
    :class:`DeprecationWarning`
        If this attribute is deprecated.

    Raises
    ----------
    :exc:`AttributeError`
        If this attribute is unrecognized and thus erroneous.

    See Also
    ----------
    https://www.python.org/dev/peps/pep-0562/#id8
        :pep:`562`-compliant dunder function inspiring this implementation.
    '''
    assert isinstance(attr_deprecated_name, str), (
        f'{repr(attr_deprecated_name)} not string.')
    assert isinstance(attr_deprecated_name_to_nondeprecated_name, dict), (
        f'{repr(attr_deprecated_name_to_nondeprecated_name)} not dictionary.')
    assert isinstance(attr_nondeprecated_name_to_value, dict), (
        f'{repr(attr_nondeprecated_name_to_value)} not dictionary.')

    # Fully-qualified name of the caller's submodule. Since all physical
    # submodules (i.e., those defined on-disk) define this dunder attribute
    # *AND* this function is only ever called by such submodules, this
    # attribute is effectively guaranteed to exist.
    MODULE_NAME = attr_nondeprecated_name_to_value['__name__']

    # Unqualified name of the non-deprecated attribute originating this
    # deprecated attribute if this attribute is deprecated *OR* the sentinel.
    attr_nondeprecated_name = attr_deprecated_name_to_nondeprecated_name.get(
        attr_deprecated_name, SENTINEL)

    # If this attribute is deprecated...
    if attr_nondeprecated_name is not SENTINEL:
        assert isinstance(attr_nondeprecated_name, str), (
            f'{repr(attr_nondeprecated_name)} not string.')

        # Value of the non-deprecated attribute originating this deprecated
        # attribute if the former exists *OR* the sentintel.
        attr_nondeprecated_value = attr_nondeprecated_name_to_value.get(
            attr_nondeprecated_name, SENTINEL)

        # If that module fails to define this non-deprecated attribute, raise
        # an exception. Note this should *NEVER* happen but surely will.
        if attr_nondeprecated_value is SENTINEL:
            raise AttributeError(
                f'Deprecated attribute '
                f'"{attr_deprecated_name}" in submodule "{MODULE_NAME}" '
                f'originates from missing non-deprecated attribute '
                f'"{attr_nondeprecated_name}" not defined by that submodule.'
            )
        # Else, that module defines this non-deprecated attribute.

        # Substring suffixing the warning message emitted below.
        warning_suffix = ''

        # If this deprecated attribute originates from a public non-deprecated
        # attribute, inform users of the existence of the latter.
        if not attr_nondeprecated_name.startswith('_'):
            warning_suffix = (
                f' Please globally replace all references to this '
                f'attribute with its non-deprecated equivalent '
                f'"{attr_nondeprecated_name}" from the same submodule.'
            )
        # Else, this deprecated attribute originates from a private
        # non-deprecated attribute. In this case, avoid informing users of the
        # existence of the latter.

        # Emit a non-fatal warning of the standard "DeprecationWarning"
        # category, which CPython filters (ignores) by default.
        #
        # Note that we intentionally do *NOT* emit a non-fatal warning of our
        # non-standard "BeartypeDecorHintPepDeprecationWarning" category, which
        # applies *ONLY* to PEP-compliant type hint deprecations.
        warn(
            (
                f'Deprecated attribute '
                f'"{attr_deprecated_name}" in submodule "{MODULE_NAME}" '
                f'scheduled for removal under a future release.'
                f'{warning_suffix}'
            ),
            DeprecationWarning,
        )

        # Return the value of this deprecated attribute.
        return attr_nondeprecated_value
    # Else, this attribute is *NOT* deprecated. Since Python called this dunder
    # function, this attribute is undefined and thus erroneous.

    # Raise the same exception raised by Python on accessing a non-existent
    # attribute of a module *NOT* defining this dunder function.
    raise AttributeError(
        f"module '{MODULE_NAME}' has no attribute '{attr_deprecated_name}'")
