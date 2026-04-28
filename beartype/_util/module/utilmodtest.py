#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module tester** (i.e., callables dynamically testing
modules and/or attributes in modules) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeModuleUnimportableWarning
from beartype.roar._roarexc import _BeartypeUtilModuleException
from beartype.typing import Optional
from beartype._cave._cavefast import ModuleType
from beartype._data.typing.datatyping import TypeException
from beartype._util.error.utilerrwarn import issue_warning
from beartype._util.text.utiltextidentifier import die_unless_identifier
from beartype._util.text.utiltextversion import convert_str_version_to_tuple
from importlib.metadata import version as get_module_version  # type: ignore[attr-defined]

# ....................{ RAISERS                            }....................
#FIXME: Excise us up. This function is no longer called anywhere. *sigh*
def die_unless_module_attr_name(
    # Mandatory parameters.
    module_attr_name: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
    exception_prefix: str = 'Module attribute name ',
) -> None:
    '''
    Raise an exception unless the passed string is the fully-qualified
    syntactically valid name of a **module attribute** (i.e., object declared
    at module scope by a module) that may or may not actually exist.

    This validator does *not* validate this attribute to actually exist -- only
    that the name of this attribute is syntactically valid.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be validated.
    exception_cls : type, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilModuleException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to something reasonably sane.

    Raises
    ------
    exception_cls
        If either:

        * This name is *not* a string.
        * This name is a string containing either:

          * *No* ``.`` characters and thus either:

            * Is relative to the calling subpackage and thus *not*
              fully-qualified (e.g., ``muh_submodule``).
            * Refers to a builtin object (e.g., ``str``). While technically
              fully-qualified, the names of builtin objects are *not*
              explicitly importable as is. Since these builtin objects are
              implicitly imported everywhere, there exists *no* demonstrable
              reason to even attempt to import them anywhere.

          * One or more ``.`` characters but syntactically invalid as an
            identifier (e.g., ``0h!muh?G0d.``).
    '''
    assert isinstance(exception_cls, type), f'{repr(exception_cls)} not type.'
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # If this object is *NOT* a string, raise an exception.
    if not isinstance(module_attr_name, str):
        raise exception_cls(
            f'{exception_prefix}{repr(module_attr_name)} not string.')
    # Else, this object is a string.
    #
    # If this string contains *NO* "." characters and thus either is relative to
    # the calling subpackage or refers to a builtin object, raise an exception.
    elif '.' not in module_attr_name:
        raise exception_cls(
            f'{exception_prefix}"{module_attr_name}" '
            f'relative or refers to builtin object '
            f'(i.e., due to containing no "." characters).'
        )
    # Else, this string contains one or more "." characters and is thus the
    # fully-qualified name of a non-builtin type.
    #
    # If this string is syntactically invalid as a fully-qualified module
    # attribute name, raise an exception.
    else:
        die_unless_identifier(
            text=module_attr_name,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
    # Else, this string is syntactically valid as a fully-qualified module
    # attribute name.

# ....................{ TESTERS                            }....................
def is_module(
    # Mandatory parameters.
    module_name: str,

    # Optional parameters.
    is_ignore_import_exception: bool = False,
    exception_cls: TypeException = _BeartypeUtilModuleException,
    exception_prefix: str = 'Module ',
) -> bool:
    '''
    :data:`True` only if the module or C extension with the passed
    fully-qualified name is importable under the active Python interpreter.

    This tester is intentionally *not* memoized (e.g., by ``@callable_cached``),
    as the importability of modules can dynamically change throughout the
    lifetime of this interpreter in response to dynamic module creation and
    deletion as well as modification to low-level :mod:`importlib` machinery.

    Caveats
    -------
    **This tester dynamically imports this module as an unavoidable side effect
    of performing this test.** Nonetheless, this tester is intentionally
    implemented to be as safe as feasible if this module is only **partially
    initialized** (i.e., if this module is currently still being imported and
    thus has yet to be fully initialized).

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.
    is_ignore_import_exception : bool, default: False
        Either:

        * If :data:`True`, this tester silently catches and ignores *any*
          exception raised as a side effect by the importation of this module.
        * If :data:`False`, this tester catches and coerces *any* otherwise
          fatal exception raised as a side effect by the importation of this
          module into a non-fatal warning.

        Defaults to :data:`False` for safety.
    exception_cls : type[Exception], default: _BeartypeUtilModuleException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilModuleException`.
    exception_prefix : str, default: "Module "
        Human-readable substring prefixing raised exception messages. Defaults
        to a reasonably sensible prefix.

    Returns
    -------
    bool
        :data:`True` only if this module is importable.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If a module with this name exists *but* that module is unimportable due
        to raising module-scoped exceptions at importation time.
    '''
    assert isinstance(is_ignore_import_exception, bool), (
        f'{repr(is_ignore_import_exception)} not boolean.')

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    # from beartype._util.module.utilmodget import get_module_imported_or_none
    # from beartype._util.module.utilmodimport import importlib_import_module
    from beartype._util.module.utilmodimport import import_module_or_none

    # ....................{ LOCALS                         }....................
    # Module with this name if this module is importable *OR* "None" otherwise.
    module: Optional[ModuleType] = None

    # Exception raised by importing this module below if any *OR* "None".
    import_exception: Optional[Exception] = None

    # ....................{ IMPORT                         }....................
    # Attempt to dynamically import this module.
    try:
        module = import_module_or_none(
            module_name=module_name,
            # Avoid coercing import-time exceptions into warnings. Why? So that
            # we can detect and handle the ignorable standard "ImportError"
            # exception whose message implies this module to be importable but
            # only currently partially initialized below.
            is_warn_import_exception=False,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

        # Return true only if this module is importable.
        return module is not None
    # If doing so raises a standard "ImportError" exception possibly implying
    # this module to be importable but only currently partially initialized...
    except ImportError as exception:
        # Message raised by this exception.
        exception_message = str(exception)

        # If this message claims this module to be only currently partially
        # initialized, charitably assume this module to be subsequently fully
        # initialized and thus importable by immediately returning true.
        if "' from partially initialized module '" in exception_message:
            # print(f'Ignoring partially initialized module "{module_name}"!')
            return True
        # Else, this message does *NOT* claim this module to be only currently
        # partially initialized.

        # Note this fact.
        import_exception = exception
    # If doing so raises any other exception, note this fact.
    except Exception as exception:
        import_exception = exception
    # Since the above "try:" block did *NOT* return, an exception was raised.

    # If the caller requests we *NOT* ignore this exception, coerce this fatal
    # exception into a non-fatal warning.
    if not is_ignore_import_exception:
        issue_warning(
            warning_cls=BeartypeModuleUnimportableWarning,
            message=(
                f'Ignoring module "{module_name}" importation exception:'
                f'\n\t{import_exception.__class__.__name__}: {import_exception}'
            ),
        )
    # Else, the caller requests we ignore this exception. Do so! \o/

    # ....................{ RETURN                         }....................
    # Return false as a fallback.
    return False


#FIXME: Unit test us up against @beartype itself, the only third-party package
#guaranteed to be importable.
def is_module_version_at_least(module_name: str, version_minimum: str) -> bool:
    '''
    :data:`True` only if the module or C extension with the passed
    fully-qualified name is both importable under the active Python interpreter
    *and* at least as new as the passed version.

    This tester is intentionally *not* memoized (e.g., by ``@callable_cached``),
    as the importability of modules can dynamically change throughout the
    lifetime of this interpreter in response to dynamic module creation and
    deletion as well as modification to low-level :mod:`importlib` machinery.

    Caveats
    -------
    **This tester dynamically imports this module as an unavoidable side effect
    of performing this test.**

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.
    version_minimum : str
        Minimum version to test this module against as a dot-delimited
        :pep:`440`-compliant version specifier (e.g., ``42.42.42rc42.post42``).

    Returns
    -------
    bool
        :data:`True` only if:

        * This module is importable.
        * This module's version is at least the passed version.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If a module with this name exists *but* that module is unimportable due
        to raising module-scoped exceptions at importation time.
    '''
    assert isinstance(version_minimum, str), (
        f'{repr(version_minimum)} not string.')

    # If this module is unimportable, return false immediately.
    if not is_module(module_name):
        return False
    # Else, this module is importable.

    # Current version of this module installed under the active Python
    # interpreter if any *OR* raise an exception otherwise (which should
    # *NEVER* happen by prior logic testing this module to be importable).
    version_actual = get_module_version(module_name)

    # Tuples of version parts parsed from version strings.
    version_actual_parts  = convert_str_version_to_tuple(version_actual)
    version_minimum_parts = convert_str_version_to_tuple(version_minimum)

    # Return true only if this module's version satisfies this minimum.
    return version_actual_parts >= version_minimum_parts

# ....................{ TESTERS ~ package                  }....................
#FIXME: Unit test us up, please.
def is_package(package_name: str, **kwargs) -> bool:
    '''
    :data:`True` only if the package with the passed fully-qualified name is
    importable under the active Python interpreter.

    Caveats
    -------
    **This tester dynamically imports this module as an unavoidable side effect
    of performing this test.**

    Parameters
    ----------
    package_name : str
        Fully-qualified name of the package to be imported.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.is_module` tester.

    Returns
    -------
    bool
        :data:`True` only if this package is importable.

    Warns
    -----
    BeartypeModuleUnimportableWarning
        If a package with this name exists *but* that package is unimportable
        due to raising module-scoped exceptions from the top-level ``__init__``
        submodule of this package at importation time.
    '''

    # Be the one liner you want to see in the world.
    return is_module(f'{package_name}.__init__', **kwargs)
