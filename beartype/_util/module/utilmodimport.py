#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module importer** utilities (i.e., callables dynamically
importing modules and/or attributes from modules).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeModuleUnimportableWarning
from beartype.roar._roarexc import _BeartypeUtilModuleException
from beartype.typing import (
    Any,
    Optional,
)
from beartype._data.cls.datacls import TYPES_BUILTIN
from beartype._data.hint.datahinttyping import TypeException
from beartype._util.utilobject import SENTINEL
from importlib import import_module as importlib_import_module
from types import ModuleType
from warnings import warn

# ....................{ IMPORTERS                          }....................
#FIXME: Preserved until requisite, which shouldn't be long.
#FIXME: Unit test us up, please.
# def import_module(
#     # Mandatory parameters.
#     module_name: str,
#
#     # Optional parameters.
#     exception_cls: TypeException = _BeartypeUtilModuleException,
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
    passed fully-qualified name if importable *or* return :data:`None` otherwise
    (i.e., if that module, package, or C extension is unimportable).

    For safety, this function also emits a non-fatal warning when that module,
    package, or C extension exists but is still unimportable (e.g., due to
    raising an exception at module scope).

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.

    Returns
    -------
    Either:

    * If a module, package, or C extension with this fully-qualified name is
      importable, that module, package, or C extension.
    * Else, :data:`None`.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If a module with this name exists *but* that module is unimportable
        due to raising module-scoped exceptions at importation time.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodget import get_module_imported_or_none

    # Module cached with "sys.modules" if this module has already been imported
    # elsewhere under the active Python interpreter *OR* "None" otherwise.
    module = get_module_imported_or_none(module_name)

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
                f'Ignoring module "{module_name}" importation exception:\n'
                f'\t{exception.__class__.__name__}: {exception}'
            ),
            BeartypeModuleUnimportableWarning,
        )

    # Inform the caller that this module is unimportable.
    return None

# ....................{ IMPORTERS ~ attr                   }....................
def import_module_attr(
    # Mandatory parameters.
    module_attr_name: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
    exception_prefix: str = 'Module attribute ',
) -> Any:
    '''
    Dynamically import and return the **module attribute** (i.e., object
    declared at module scope) with the passed fully-qualified name if importable
    *or* raise an exception otherwise.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be imported.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`._BeartypeUtilModuleException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    object
        The module attribute with this fully-qualified name.

    Raises
    ------
    exception_cls
        If either:

        * This name is syntactically invalid.
        * *No* module prefixed this name exists.
        * A module prefixed by this name exists *but* that module declares no
          attribute by this name.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If a module prefixed by this name exists *but* that module is
        unimportable due to module-scoped side effects at importation time.

    See Also
    --------
    :func:`.import_module_attr_or_sentinel`
        Further commentary.
    '''

    # Module attribute with this name if that module declares this attribute
    # *OR* the sentinel placeholder otherwise.
    module_attr = import_module_attr_or_sentinel(
        module_attr_name=module_attr_name,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # If this module declares *NO* such attribute, raise an exception.
    if module_attr is SENTINEL:
        raise exception_cls(
            f'{exception_prefix}"{module_attr_name}" unimportable.')
    # Else, this module declares this attribute.

    # Else, return this attribute.
    return module_attr


def import_module_attr_or_sentinel(
    # Mandatory parameters.
    module_attr_name: str,

    # Optional parameters.
    is_import_builtin_type_fallback: bool = False,
    exception_cls: TypeException = _BeartypeUtilModuleException,
    exception_prefix: str = 'Module attribute ',
) -> Any:
    '''
    Dynamically import and return the **module attribute** (i.e., object
    declared at module scope) with the passed fully-qualified name if importable
    *or* the placeholder :data:`.SENTINEL` otherwise.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be imported.
    is_import_builtin_type_fallback : bool
        If this module attribute is unimportable *and* this boolean is:

        * :data:`True`, then fallback to attempting to import the unqualified
          basename of this attribute as a **builtin type** (i.e., globally
          accessible C-based type implicitly accessible from all scopes and thus
          requiring *no* explicit importation) from the standard :mod:`builtins`
          module. Builtins are globally accessible and could thus be considered
          to be globally "importable" from *any* module. This perspective is
          particularly useful when dynamically resolving relative forward
          references (e.g., ``typing.ForwardRef('int')``) in type-checking
          wrapper functions, which attempt to (in order):

          #. Resolve those references against the module defining the decorated
             callable and, failing that...
          #. Resolve those references against the standard :mod:`builtins`
             module and, failing that...
          #. Raise an exception.

        * :data:`False`, then avoid performing that fallback behaviour by simply
          returning :data:`.SENTINEL` immediately.

        Defaults to :data:`False` for safety.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`._BeartypeUtilModuleException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    object
        Either:

        * If *no* module prefixed this name exists, :data:`.SENTINEL`.
        * If a module prefixed by this name exists *but* that module declares
          no attribute by this name, :data:`.SENTINEL`.
        * Else, the module attribute with this fully-qualified name.

    Raises
    ------
    exception_cls
        If this name is syntactically invalid.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If a module prefixed by this name exists *but* that module is
        unimportable due to module-scoped side effects at importation time.
    '''
    assert isinstance(is_import_builtin_type_fallback, bool), (
        f'{repr(is_import_builtin_type_fallback)} not boolean.')

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodtest import die_unless_module_attr_name

    # If this object is *NOT* the fully-qualified syntactically valid name of a
    # module attribute that may or may not actually exist, raise an exception.
    die_unless_module_attr_name(
        module_attr_name=module_attr_name,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
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

    # If that module is unimportable, return "None".
    if module is None:
        return SENTINEL
    # Else, that module is importable.

    # Module attribute with this name if that module declares this attribute
    # *OR* the sentinel placeholder otherwise.
    module_attr = getattr(module, module_attr_basename, SENTINEL)

    #FIXME: Unit test us up, please.
    #FIXME: Comment us up, please.
    if (
        module_attr is SENTINEL and
        is_import_builtin_type_fallback
    ):
        module_attr = getattr(TYPES_BUILTIN, module_attr_basename, SENTINEL)

    # Return this module attribute.
    return module_attr



def import_module_attr_or_none(*args, **kwargs) -> Any:
    '''
    Dynamically import and return the **module attribute** (i.e., object
    declared at module scope) with the passed fully-qualified name if importable
    *or* :data:`None` otherwise.

    Caveats
    -------
    **This importer ambiguously returns false negatives in edge cases and is
    thus mildly unsafe.** Consider calling the unambiguous
    :func:`.import_module_attr_or_sentinel` importer instead. Why? Because this
    importer returns :data:`None` both when this attribute is unimportable *and*
    when this attribute is importable but has a value of :data:`None`.
    Nonetheless, this importer remains convenient for various use cases in which
    this distinction is mostly irrelevant.

    Parameters
    ----------
    All parameters are passed as is to the lower-level
    :func:`.import_module_attr_or_sentinel` importer.

    Returns
    -------
    object
        Either:

        * If *no* module prefixed this name exists, :data:`None`.
        * If a module prefixed by this name exists *but* that module declares
          no attribute by this name, :data:`None`.
        * Else, the module attribute with this fully-qualified name.

    Raises
    ------
    exception_cls
        If this name is syntactically invalid.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If a module prefixed by this name exists *but* that module is
        unimportable due to module-scoped side effects at importation time.
    '''

    # Module attribute with this name if that module declares this attribute
    # *OR* the sentinel placeholder otherwise.
    module_attr = import_module_attr_or_sentinel(*args, **kwargs)

    # Return either this attribute if importable *OR* "None" otherwise.
    return module_attr if module_attr is not SENTINEL else None
