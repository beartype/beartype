#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module tester** (i.e., callables dynamically testing
modules and/or attributes in modules) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.meta import _convert_version_str_to_tuple
from beartype.roar._roarexc import _BeartypeUtilModuleException
from beartype._data.datatyping import TypeException
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8

# ....................{ VALIDATORS                         }....................
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
        Type of exception to be raised. Defaults to
        :class:`_BeartypeUtilModuleException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to something reasonably sane.

    Raises
    ----------
    :exc:`exception_cls`
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

    # Avoid circular import dependencies.
    from beartype._util.text.utiltextident import is_identifier

    # If this object is *NOT* a string, raise an exception.
    if not isinstance(module_attr_name, str):
        raise exception_cls(
            f'{exception_prefix}{repr(module_attr_name)} not string.')
    # Else, this object is a string.
    #
    # If this string contains *NO* "." characters and thus either is relative
    # to the calling subpackage or refers to a builtin object, raise an
    # exception.
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
    elif not is_identifier(module_attr_name):
        raise exception_cls(
            f'{exception_prefix}"{module_attr_name}" '
            f'syntactically invalid as module attribute name.'
        )
    # Else, this string is syntactically valid as a fully-qualified module
    # attribute name.

# ....................{ TESTERS                            }....................
def is_module(module_name: str) -> bool:
    '''
    ``True`` only if the module or C extension with the passed fully-qualified
    name is importable under the active Python interpreter.

    Caveats
    ----------
    **This tester dynamically imports this module as an unavoidable side effect
    of performing this test.**

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.

    Returns
    ----------
    bool
        ``True`` only if this module is importable.

    Warns
    ----------
    BeartypeModuleUnimportableWarning
        If a module with this name exists *but* that module is unimportable
        due to raising module-scoped exceptions at importation time.
    '''

    # Avoid circular import dependencies.
    from beartype._util.mod.utilmodimport import import_module_or_none

    # Module with this name if this module is importable *OR* "None" otherwise.
    module = import_module_or_none(module_name)

    # Return true only if this module is importable.
    return module is not None


#FIXME: Unit test us up against "setuptools", the only third-party package
#*BASICALLY* guaranteed to be importable.
def is_module_version_at_least(module_name: str, version_minimum: str) -> bool:
    '''
    ``True`` only if the module or C extension with the passed fully-qualified
    name is both importable under the active Python interpreter *and* at least
    as new as the passed version.

    Caveats
    ----------
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
    ----------
    bool
        ``True`` only if:

        * This module is importable.
        * This module's version is at least the passed version.

    Warns
    ----------
    BeartypeModuleUnimportableWarning
        If a module with this name exists *but* that module is unimportable
        due to raising module-scoped exceptions at importation time.
    '''

    # If it is *NOT* the case that...
    if not (
        # This module is importable *AND*...
        is_module(module_name) and
        # Either...
        (
            # The active Python interpreter targets Python >= 3.8 and thus
            # provides the "importlib.metadata" API required to portably
            # inspect module versions without requiring obsolete third-party
            # packages (e.g., "pkg_resources") *OR*...
            IS_PYTHON_AT_LEAST_3_8 or
            # The active Python interpreter targets Python < 3.8 but the
            # obsolete third-party package "pkg_resources" is importable...
            is_package('pkg_resources')
        )
    ):
    # Then this module is either unimportable *OR* no API capable of inspecting
    # module versions is importable. In either case, return false to avoid
    # returning false positives.
        return False
    assert isinstance(version_minimum, str), (
        f'{repr(version_minimum)} not string.')

    # If the active Python interpreter targets Python >= 3.8...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from importlib.metadata import version as get_module_version  # type: ignore[attr-defined]

        # Current version of this module installed under the active Python
        # interpreter if any *OR* raise an exception otherwise (which should
        # *NEVER* happen by prior logic testing this module to be importable).
        version_actual = get_module_version(module_name)

        # Tuples of version parts parsed from version strings.
        version_actual_parts  = _convert_version_str_to_tuple(version_actual)
        version_minimum_parts = _convert_version_str_to_tuple(version_minimum)

        # Return true only if this module's version satisfies this minimum.
        return version_actual_parts >= version_minimum_parts
    # Else, the active Python interpreter targets Python < 3.8 but the obsolete
    # third-party package "pkg_resources" is importable by the above logic. In
    # this case...
    else:
        # Defer imports from optional third-party dependencies.
        from pkg_resources import (
            DistributionNotFound,
            UnknownExtra,
            VersionConflict,
            get_distribution,
            parse_requirements,
        )

        # Setuptools-specific requirements string constraining this module.
        module_requirement_str = f'{module_name} >= {version_minimum}'

        # Setuptools-specific requirements object parsed from this string. Yes,
        # setuptools insanely requires this parsing to be performed through a
        # generator -- even when only parsing a single requirements string.
        module_requirement = None
        for module_requirement in parse_requirements(module_requirement_str):
            break

        # Attempt to...
        try:
            # Setuptools-specific object describing the current version of the
            # module satisfying this requirement if any *OR* "None" if this
            # requirement cannot be guaranteed to be unsatisfied.
            module_distribution = get_distribution(module_requirement)  # pyright: ignore[reportGeneralTypeIssues]
        # If setuptools fails to find this requirement, this does *NOT*
        # necessarily imply this requirement to be unimportable as a package.
        # Rather, this only implies this requirement was *NOT* installed as a
        # setuptools-managed egg. This requirement is still installable and
        # hence importable (e.g., by manually copying this requirement's
        # package into the "site-packages" subdirectory of the top-level
        # directory for this Python interpreter). However, does this edge-case
        # actually occur in reality? *YES.* PyInstaller-frozen applications
        # embed requirements without corresponding setuptools-managed eggs.
        # Hence, this edge-case *MUST* be handled.
        except DistributionNotFound:
            module_distribution = None
        # If setuptools fails to find the distribution-packaged version of this
        # requirement (e.g., due to having been editably installed with "sudo
        # python3 setup.py develop"), this version may still be manually
        # parseable from this requirement's package. Since setuptools fails to
        # raise an exception whose type is unique to this error condition, the
        # contents of this exception are parsed to distinguish this expected
        # error condition from other unexpected error conditions. In the former
        # case, a non-human-readable exception resembling the following is
        # raised:
        #     ValueError: "Missing 'Version:' header and/or PKG-INFO file",
        #     networkx [unknown version] (/home/leycec/py/networkx)
        except ValueError as version_missing:
            # If this exception was...
            if (
                # ...instantiated with two arguments...
                len(version_missing.args) == 2 and
                # ...whose second argument is suffixed by a string indicating
                # the version of this distribution to have been ignored rather
                # than recorded during installation...
                str(version_missing.args[1]).endswith(' [unknown version]')
            # ...this exception indicates an expected ignorable error
            # condition. Silently ignore this edge case.
            ):
                module_distribution = None
            # Else, this exception indicates an unexpected and thus unignorable
            # error condition.

            # Reraise this exception, please.
            raise
        # If setuptools found only requirements of insufficient version, all
        # currently installed versions of this module fail to satisfy this
        # requirement. In this case, immediately return false.
        except (UnknownExtra, VersionConflict):
            return False
        # If any other exception is raised, expose this exception as is.

        # Return true only if this requirement is satisfied.
        return module_distribution is not None

# ....................{ TESTERS ~ package                  }....................
#FIXME: Unit test us up, please.
def is_package(package_name: str) -> bool:
    '''
    ``True`` only if the package with the passed fully-qualified name is
    importable under the active Python interpreter.

    Caveats
    ----------
    **This tester dynamically imports this module as an unavoidable side effect
    of performing this test.**

    Parameters
    ----------
    package_name : str
        Fully-qualified name of the package to be imported.

    Returns
    ----------
    bool
        ``True`` only if this package is importable.

    Warns
    ----------
    :class:`BeartypeModuleUnimportableWarning`
        If a package with this name exists *but* that package is unimportable
        due to raising module-scoped exceptions from the top-level `__init__`
        submodule of this package at importation time.
    '''

    # Be the one liner you want to see in the world.
    return is_module(f'{package_name}.__init__')
