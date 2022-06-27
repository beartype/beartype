#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype metadata.**

This submodule exports global constants synopsizing this package -- including
versioning and dependencies.

Python Version
----------
For uniformity between this codebase and the ``setup.py`` setuptools script
importing this module, this module also validates the version of the active
Python 3 interpreter. An exception is raised if this version is insufficient.

As a tradeoff between backward compatibility, security, and maintainability,
this package strongly attempts to preserve compatibility with the first stable
release of the oldest version of CPython still under active development. Hence,
obsolete and insecure versions of CPython that have reached their official End
of Life (EoL) (e.g., Python 3.5) are explicitly unsupported.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To avoid accidental importation of optional runtime dependencies
# (e.g., "typing_extensions") at installation time *BEFORE* the current package
# manager has installed those dependencies, this module may *NOT* import from
# any submodules of the current package. This includes *ALL* "beartype._util"
# submodules, most of which import from "beartype.typing", which conditionally
# imports optional runtime dependencies under certain contexts.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To avoid race conditions during setuptools-based installation, this
# module may import *ONLY* from modules guaranteed to exist at the start of
# installation. This includes all standard Python and package modules but
# *NOT* third-party dependencies, which if currently uninstalled will only be
# installed at some later time in the installation.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import sys as _sys
from beartype.typing import Tuple as _Tuple

# ....................{ METADATA                           }....................
NAME = 'beartype'
'''
Human-readable package name.
'''


PACKAGE_NAME = NAME.lower()
'''
Fully-qualified name of the top-level Python package containing this submodule.
'''


LICENSE = 'MIT'
'''
Human-readable name of the license this package is licensed under.
'''

# ....................{ PYTHON ~ version                   }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: Changes to this section *MUST* be synchronized with:
# * Signs declared by the private
#   "beartype._data.hint.pep.datapepsign" submodule, which *MUST*
#   be synchronized against the "__all__" dunder list global of the "typing"
#   module bundled with the most recent CPython release.
# * Continuous integration test matrices, including:
#   * The top-level "tox.ini" file.
#   * The "jobs/tests/strategy/matrix/{tox-env,include/python-version}"
#     settings of the GitHub Actions-specific
#     ".github/workflows/python_test.yml" file.
# * Front-facing documentation (e.g., "README.rst", "doc/md/INSTALL.md").
#
# On bumping the minimum required version of Python, consider also documenting
# the justification for doing so in the "Python Version" section of this
# submodule's docstring above.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

PYTHON_VERSION_MIN = '3.7.0'
'''
Human-readable minimum version of Python required by this package as a
``.``-delimited string.

See Also
----------
"Python Version" section of this submodule's docstring for a detailed
justification of this constant's current value.
'''


PYTHON_VERSION_MINOR_MAX = 11
'''
Maximum minor stable version of this major version of Python currently released
(e.g., ``5`` if Python 3.5 is the most recent stable version of Python 3.x).
'''


def _convert_version_str_to_tuple(version_str: str) -> _Tuple[int, ...]:
    '''
    Convert the passed human-readable ``.``-delimited version string into a
    machine-readable version tuple of corresponding integers.
    '''
    assert isinstance(version_str, str), f'"{version_str}" not version string.'
    return tuple(int(version_part) for version_part in version_str.split('.'))


PYTHON_VERSION_MIN_PARTS = _convert_version_str_to_tuple(PYTHON_VERSION_MIN)
'''
Machine-readable minimum version of Python required by this package as a
tuple of integers.
'''


_PYTHON_VERSION_PARTS = _sys.version_info[:3]
'''
Machine-readable current version of the active Python interpreter as a
tuple of integers.
'''


# Validate the version of the active Python interpreter *BEFORE* subsequent
# code possibly depending on this version. Since this version should be
# validated both at setuptools-based install time and post-install runtime
# *AND* since this module is imported sufficiently early by both, stash this
# validation here to avoid duplication of this logic and hence the hardcoded
# Python version.
#
# The "sys" module exposes three version-related constants for this purpose:
#
# * "hexversion", an integer intended to be specified in an obscure (albeit
#   both efficient and dependable) hexadecimal format: e.g.,
#    >>> sys.hexversion
#    33883376
#    >>> '%x' % sys.hexversion
#    '20504f0'
# * "version", a human-readable string: e.g.,
#    >>> sys.version
#    2.5.2 (r252:60911, Jul 31 2008, 17:28:52)
#    [GCC 4.2.3 (Ubuntu 4.2.3-2ubuntu7)]
# * "version_info", a tuple of three or more integers *OR* strings: e.g.,
#    >>> sys.version_info
#    (2, 5, 2, 'final', 0)
#
# For sanity, this package will *NEVER* conditionally depend upon the
# string-formatted release type of the current Python version exposed via the
# fourth element of the "version_info" tuple. Since the first three elements of
# that tuple are guaranteed to be integers *AND* since a comparable 3-tuple of
# integers is declared above, comparing the former and latter yield the
# simplest and most reliable Python version test.
#
# Note that the nearly decade-old and officially accepted PEP 345 proposed a
# new field "requires_python" configured via a key-value pair passed to the
# call to setup() in "setup.py" (e.g., "requires_python = ['>=2.2.1'],"), that
# field has yet to be integrated into either disutils or setuputils. Hence,
# that field is validated manually in the typical way.
if _PYTHON_VERSION_PARTS < PYTHON_VERSION_MIN_PARTS:
    # Human-readable current version of Python. Ideally, "sys.version" would be
    # leveraged here instead; sadly, that string embeds significantly more than
    # merely a version and hence is inapplicable for real-world usage: e.g.,
    #
    #     >>> import sys
    #     >>> sys.version
    #     '3.6.5 (default, Oct 28 2018, 19:51:39) \n[GCC 7.3.0]'
    _PYTHON_VERSION = '.'.join(
        str(version_part) for version_part in _sys.version_info[:3])

    # Die ignominiously.
    raise RuntimeError(
        f'{NAME} requires at least Python {PYTHON_VERSION_MIN}, but '
        f'the active interpreter only targets Python {_PYTHON_VERSION}. '
        f'We feel unbearable sadness for you.'
    )

# ....................{ METADATA ~ version                 }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: When modifying the current version of this package below,
# consider adhering to the Semantic Versioning schema. Specifically, the
# version should consist of three "."-delimited integers
# "{major}.{minor}.{patch}", where:
#
# * "{major}" specifies the major version, incremented only when either:
#   * Breaking backward compatibility in this package's public API.
#   * Implementing headline-worthy functionality (e.g., a GUI). Technically,
#     this condition breaks the Semantic Versioning schema, which stipulates
#     that *ONLY* changes breaking backward compatibility warrant major bumps.
#     But this is the real world. In the real world, significant improvements
#     are rewarded with significant version changes.
#   In either case, the minor and patch versions both reset to 0.
# * "{minor}" specifies the minor version, incremented only when implementing
#   customary functionality in a manner preserving such compatibility. In this
#   case, the patch version resets to 0.
# * "{patch}" specifies the patch version, incremented only when correcting
#   outstanding issues in a manner preserving such compatibility.
#
# When in doubt, increment only the minor version and reset the patch version.
# For further details, see http://semver.org.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

VERSION = '0.11.0'
'''
Human-readable package version as a ``.``-delimited string.
'''


VERSION_PARTS = _convert_version_str_to_tuple(VERSION)
'''
Machine-readable package version as a tuple of integers.
'''

# ....................{ METADATA ~ synopsis                }....................
SYNOPSIS = 'Unbearably fast runtime type checking in pure Python.'
'''
Human-readable single-line synopsis of this package.

By PyPI design, this string must *not* span multiple lines or paragraphs.
'''

# ....................{ METADATA ~ authors                 }....................
AUTHOR_EMAIL = 'leycec@gmail.com'
'''
Email address of the principal corresponding author (i.e., the principal author
responding to public correspondence).
'''


AUTHORS = 'Cecil Curry, et al.'
'''
Human-readable list of all principal authors of this package as a
comma-delimited string.

For brevity, this string *only* lists authors explicitly assigned copyrights.
For the list of all contributors regardless of copyright assignment or
attribution, see the top-level ``AUTHORS.md`` file.
'''


COPYRIGHT = '2014-2022 Beartype authors'
'''
Legally binding copyright line excluding the license-specific prefix (e.g.,
``"Copyright (c)"``).

For brevity, this string *only* lists authors explicitly assigned copyrights.
For the list of all contributors regardless of copyright assignment or
attribution, see the top-level ``AUTHORS.md`` file.
'''

# ....................{ METADATA ~ urls                    }....................
URL_HOMEPAGE = 'https://github.com/beartype/beartype'
'''
URL of this package's homepage.
'''


URL_DOWNLOAD = f'{URL_HOMEPAGE}/archive/{VERSION}.tar.gz'
'''
URL of the source tarball for the current version of this package.

This URL assumes a tag whose name is ``v{VERSION}`` where ``{VERSION}`` is the
human-readable current version of this package (e.g., ``v0.4.0``) to exist.
Typically, no such tag exists for live versions of this package -- which
have yet to be stabilized and hence tagged. Hence, this URL is typically valid
*only* for previously released (rather than live) versions of this package.
'''


URL_ISSUES = f'{URL_HOMEPAGE}/issues'
'''
URL of this package's issue tracker.
'''


URL_RELEASES = f'{URL_HOMEPAGE}/releases'
'''
URL of this package's release list.
'''

# ....................{ METADATA ~ libs : runtime          }....................
_LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_NUMPY = '1.21.0'
'''
Minimum optional version of NumPy recommended for use with mod:`beartype`.

NumPy >= 1.21.0 first introduced the third-party PEP-noncompliant
:attr:`numpy.typing.NDArray` type hint supported by the
:func:`beartype.beartype` decorator.
'''


_LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_TYPING_EXTENSIONS = '3.10.0.0'
'''
Minimum optional version of the third-party :mod:`typing_extensions` package
recommended for use with mod:`beartype`.

:mod:`typing_extensions` >= 3.10.0.0 backports all :mod:`typing` attributes
unavailable under older Python interpreters supported by the
:func:`beartype.beartype` decorator.
'''


# Note that we intentionally omit NumPy here. If you want it, you're already
# using it; likewise, if you don't want it, you're *NOT* already using it.
LIBS_RUNTIME_OPTIONAL = (
    (
        f'typing_extensions >='
        f'{_LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_TYPING_EXTENSIONS}'
    ),
)
'''
Optional runtime package dependencies as a tuple of :mod:`setuptools`-specific
requirements strings of the format ``{project_name}
{comparison1}{version1},...,{comparisonN}{versionN}``, where:

* ``{project_name}`` is a :mod:`setuptools`-specific project name (e.g.,
  ``numpy``, ``scipy``).
* ``{comparison1}`` and ``{comparisonN}`` are :mod:`setuptools`-specific
  version comparison operators. As well as standard mathematical comparison
  operators (e.g., ``==``, ``>=``, ``<``), :mod:`setuptools` also supports the
  PEP 440-compliant "compatible release" operator ``~=`` more commonly denoted
  by ``^`` in modern package managers (e.g., poetry, npm); this operator
  enables forward compatibility with all future versions of this dependency
  known *not* to break backward compatibility, but should only be applied to
  dependencies strictly following the semantic versioning contract.
* ``{version1}`` and ``{version1}`` are arbitrary version strings (e.g.,
  ``2020.2.16``, ``0.75a2``).
'''

# ....................{ METADATA ~ libs : test : optional  }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Avoid constraining optional test-time dependencies to version
# ranges, which commonly fail for edge-case test environments -- including:
# * The oldest Python version still supported by @beartype, which typically is
#   *NOT* supported by newer versions of these dependencies.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
LIBS_TESTTIME_OPTIONAL = (
    # Require a reasonably recent version of mypy known to behave well. Less
    # recent versions are significantly deficient with respect to error
    # reporting and *MUST* thus be blacklisted.
    #
    # Note that PyPy currently fails to support mypy. See also this official
    # documentation discussing this regrettable incompatibility:
    #     https://mypy.readthedocs.io/en/stable/faq.html#does-it-run-on-pypy
    'mypy >=0.800; platform_python_implementation != "PyPy"',

    #FIXME: Consider dropping the 'and platform_python_implementation != "PyPy"'
    #clause now that "tox.ini" installs NumPy wheels from a third-party vendor
    #explicitly supporting PyPy.
    # Require NumPy. NumPy has become *EXTREMELY* non-trivial to install under
    # macOS with "pip", due to the conjunction of multiple issues. These
    # include:
    # * NumPy > 1.18.0, whose initial importation now implicitly detects
    #   whether the BLAS implementation NumPy was linked against is sane and
    #   raises a "RuntimeError" exception if that implementation is insane:
    #       RuntimeError: Polyfit sanity test emitted a warning, most
    #       likely due to using a buggy Accelerate backend. If you
    #       compiled yourself, more information is available at
    #       https://numpy.org/doc/stable/user/building.html#accelerated-blas-lapack-libraries
    #       Otherwise report this to the vendor that provided NumPy.
    #       RankWarning: Polyfit may be poorly conditioned
    # * Apple's blatantly broken multithreaded implementation of their
    #   "Accelerate" BLAS replacement, which neither NumPy nor "pip" have *ANY*
    #   semblance of control over.
    # * "pip" under PyPy, which for unknown reasons fails to properly install
    #   NumPy even when the "--force-reinstall" option is explicitly passed to
    #   "pip". Oddly, passing that option to "pip" under CPython resolves this
    #   issue -- which is why we only selectively disable NumPy installation
    #   under macOS + PyPy.
    #
    # See also this upstream NumPy issue:
    #     https://github.com/numpy/numpy/issues/15947
    'numpy; sys_platform != "darwin" and platform_python_implementation != "PyPy"',

    # Required by our optional "test_sphinx" functional test.
    'sphinx',

    # Required to exercise beartype validators and thus functionality requiring
    # beartype validators (e.g., "numpy.typing.NDArray" type hints) under
    # Python < 3.9.
    'typing_extensions; python_version < "3.9.0"',
)
'''
**Optional developer test-time package dependencies** (i.e., dependencies
recommended to test this package with :mod:`tox` as a developer at the command
line) as a tuple of :mod:`setuptools`-specific requirements strings of the
format ``{project_name} {comparison1}{version1},...,{comparisonN}{versionN}``.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''

# ....................{ METADATA ~ libs : test : mandatory }....................
LIBS_TESTTIME_MANDATORY_COVERAGE = (
    'coverage >=5.5',
)
'''
**Mandatory test-time coverage package dependencies** (i.e., dependencies
required to measure test coverage for this package) as a tuple of
:mod:`setuptools`-specific requirements strings of the format ``{project_name}
{comparison1}{version1},...,{comparisonN}{versionN}``.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''


# For completeness, install *ALL* optional test-time dependencies into *ALL*
# isolated virtual environments managed by "tox". Failure to list *ALL*
# optional test-time dependencies here commonly results in errors from mypy,
# which raises false positives on parsing "import" statements for currently
# uninstalled third-party packages (e.g., "import numpy as np").
LIBS_TESTTIME_MANDATORY_TOX = LIBS_TESTTIME_OPTIONAL + (
    'pytest >=4.0.0',
)
'''
**Mandatory tox test-time package dependencies** (i.e., dependencies required
to test this package under :mod:`tox`) as a tuple of :mod:`setuptools`-specific
requirements strings of the format ``{project_name}
{comparison1}{version1},...,{comparisonN}{versionN}``.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''


LIBS_TESTTIME_MANDATORY = (
    LIBS_TESTTIME_MANDATORY_COVERAGE +
    LIBS_TESTTIME_MANDATORY_TOX + (
        # A relatively modern version of tox is required.
        'tox >=3.20.1',
    )
)
'''
**Mandatory developer test-time package dependencies** (i.e., dependencies
required to test this package with :mod:`tox` as a developer at the command
line) as a tuple of :mod:`setuptools`-specific requirements strings of the
format ``{project_name} {comparison1}{version1},...,{comparisonN}{versionN}``.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''

# ....................{ METADATA ~ libs : doc              }....................
_LIB_DOCTIME_MANDATORY_VERSION_MINIMUM_SPHINX = '4.1.0'
'''
Human-readable minimum version as a ``.``-delimited string of :mod:`sphinx`
required to build package documentation.

Specifically, this project requires:

* :mod:sphinx` >= 4.1.0, which first supported the
  ``autodoc_typehints = 'both'`` option.
'''


_LIB_DOCTIME_MANDATORY_VERSION_MINIMUM_SPHINX_RTD_THEME = '0.5.1'
'''
Human-readable minimum version as a ``.``-delimited string of the **Read The
Docs (RTD)-flavoured Sphinx theme** (i.e., :mod:`sphinx_rtd_theme`) optionally
leveraged when building package documentation.
'''


LIBS_DOCTIME_MANDATORY = (
    f'sphinx >={_LIB_DOCTIME_MANDATORY_VERSION_MINIMUM_SPHINX}',
)
'''
**Mandatory developer documentation build-time package dependencies** (i.e.,
dependencies required to manually build documentation for this package as a
developer at the command line) as a tuple of :mod:`setuptools`-specific
requirements strings of the format ``{project_name}
{comparison1}{version1},...,{comparisonN}{versionN}``.

For flexibility, these dependencies are loosely relaxed to enable developers to
build with *any* versions satisfying at least the bare minimum. For the same
reason, optional documentation build-time package dependencies are omitted.
Since our documentation build system emits a non-fatal warning for each missing
optional dependency, omitting these optional dependencies here imposes no undue
hardships while improving usability.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''


LIBS_DOCTIME_MANDATORY_RTD = (
    f'sphinx =={_LIB_DOCTIME_MANDATORY_VERSION_MINIMUM_SPHINX}',
    (
        f'sphinx-rtd-theme '
        f'=={_LIB_DOCTIME_MANDATORY_VERSION_MINIMUM_SPHINX_RTD_THEME}'
    ),
)
'''
**Mandatory Read The Docs (RTD) documentation build-time package dependencies**
(i.e., dependencies required to automatically build documentation for this
package from the third-party RTD hosting service) as a tuple of
:mod:`setuptools`-specific requirements strings of the format ``{project_name}
{comparison1}{version1},...,{comparisonN}{versionN}``.

For consistency, these dependencies are strictly constrained to force RTD to
build against a single well-tested configuration known to work reliably.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''

# ....................{ METADATA ~ libs : dev              }....................
LIBS_DEVELOPER_MANDATORY = LIBS_TESTTIME_MANDATORY + LIBS_DOCTIME_MANDATORY
'''
**Mandatory developer package dependencies** (i.e., dependencies required to
develop and meaningfully contribute pull requests for this package) as a tuple
of :mod:`setuptools`-specific requirements strings of the format
``{project_name} {comparison1}{version1},...,{comparisonN}{versionN}``.

This tuple includes all mandatory test- and documentation build-time package
dependencies and is thus a convenient shorthand for those lower-level tuples.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''
