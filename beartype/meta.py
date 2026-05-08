#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype metadata.**

This submodule exports global constants synopsizing this package -- including
versioning and dependencies.

For uniformity between this package and the ``pyproject.toml`` file describing
the installation of this package, this submodule also validates the version of
the active Python interpreter. An exception is raised if this version is
insufficient.

As a tradeoff between backward compatibility, security, and maintainability,
this package strongly attempts to preserve compatibility with the first stable
release of the oldest version of CPython still under active development. Hence,
obsolete and insecure versions of CPython that have reached their official End
of Life (EoL) (e.g., Python 3.5) are explicitly unsupported.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import sys as _sys
from beartype._metaverse import (
    AUTHORS as AUTHORS,
    COPYRIGHT as COPYRIGHT,
    NAME as NAME,
    LICENSE as LICENSE,
    PACKAGE_NAME as PACKAGE_NAME,
    PACKAGE_TEST_NAME as PACKAGE_TEST_NAME,
    SPHINX_THEME_NAME as SPHINX_THEME_NAME,
    URL_BLUESKY as URL_BLUESKY,
    URL_CONDA as URL_CONDA,
    URL_LIBRARIES as URL_LIBRARIES,
    URL_PYPI as URL_PYPI,
    URL_RTD as URL_RTD,
    URL_ZULIP as URL_ZULIP,
    URL_HOMEPAGE as URL_HOMEPAGE,
    URL_PEP585_DEPRECATIONS as URL_PEP585_DEPRECATIONS,
    URL_REPO_ORG_NAME as URL_REPO_ORG_NAME,
    URL_REPO_BASENAME as URL_REPO_BASENAME,
    URL_REPO as URL_REPO,
    URL_DOWNLOAD as URL_DOWNLOAD,
    URL_FORUMS as URL_FORUMS,
    URL_ISSUES as URL_ISSUES,
    URL_RELEASES as URL_RELEASES,
    VERSION as VERSION,
    VERSION_PARTS as VERSION_PARTS,
)
from beartype._util.text.utiltextversion import (
    convert_str_version_to_tuple as _convert_str_version_to_tuple)
from importlib.metadata import metadata as _get_package_metadata
from typing import (
    TYPE_CHECKING,  # <-- *MUST* be import as "TYPE_CHECKING" or mypy ignores it
    Optional as _Optional,
)

# ....................{ METADATA                           }....................
# If performing static type-checking, define a fake "_package_metadata"
# dictionary as a crude means of informing the static type-checker of the
# expected type of this dictionary. While awful, this is (probably) the least
# awful approach. All alternatives invite deprecation concerns.
if TYPE_CHECKING:
    _package_metadata = {'Requires-Python': '>=3.9'}
# Else, static type-checking is *NOT* being performed. In this case...
else:
    # Dictionary mapping from the name to value of all core packaging metadata
    # with which this package was installed under the active Python interpreter.
    #
    # See also the "Core metadata specifications," which standardizes the names
    # and values of this metadata via the PEP process:
    #     https://packaging.python.org/en/latest/specifications/core-metadata
    #
    # First, attempt to introspect this metadata from the physical (i.e.,
    # on-disk) distribution describing this package.
    try:
        _package_metadata = _get_package_metadata(NAME)
    # If doing so fails for *ANY* reason whatsoever, silently ignore this
    # failure by falling back to a default dictionary permissively mapping the
    # names of this metadata to the placeholder "None".
    #
    # Note that this edge case occurs in common use cases that compile,
    # transpile, or freeze this package. Downstream consumers of this submodule
    # *MUST* thus explicitly detect imported globals whose values are "None" and
    # react nicely.
    except Exception:
        from collections import defaultdict as _defaultdict
        _package_metadata = _defaultdict(lambda: None)

# ....................{ PYTHON ~ version                   }....................
def _convert_requires_python_to_version_min(requires_python: str) -> str:
    '''
    Convert the passed :pep:`621`-compliant Python version requirements string
    into a human-readable ``.``-delimited version string (e.g., from
    ``'requires-python = ">=3.10,!=3.14rc1,!=3.14rc2"'`` to ``"3.10"``).

    Parameters
    ----------
    requires_python : str
        Python version requirements string to be converted.

    Returns
    -------
    str
        Python version string converted from this requirements string.
    '''

    # 0-based index of two characters past the first ">=" substring in this
    # version specifier, thus ignoring the ignorable ">=" delimiter.
    python_version_min_index_ge_first = requires_python.index('>=') + 2

    # 0-based index of the first ignorable character in this version specifier
    # following this first ">=" substring if this specifier contains such a
    # character *OR* -1 otherwise. Specifiers may contain optional ","-delimited
    # constraints additionally constraining this minimum version. For example,
    # this specifier blacklists various release candidates known to behave
    # problematically:
    #     requires-python = ">=3.10,!=3.14rc1,!=3.14rc2"
    #
    # Although feasible, validating these optional constraints is non-trivial.
    # Frankly, it's *NOT* worth the excruciating effort at the moment. We are
    # *NOT* building a full-blown Python version validator here. Ergo, we
    # instead ignore these optional constraints.
    python_version_min_index_ignorable_first = requires_python.find(
        ',', python_version_min_index_ge_first)

    # Version string to be returned, defined as the value of "Requires-Python"
    # key stripped of its ">=" prefix. Notably, the value of this key is the
    # value of the "requires-python" key in the "pyproject.toml" file: e.g.,
    #     requires-python = ">=3.8"
    #
    # Since the latter is guaranteed to be prefixed by the substring ">=" of
    # length 2, removing this prefix from this string yields the minimum version
    # of Python required by this package as a "."-delimited string. Phew!
    #
    # If this version specifier contains one or more optional constraints,
    # ignore those constraints.
    if python_version_min_index_ignorable_first >= 1:
        python_version_min = requires_python[
            python_version_min_index_ge_first:
            python_version_min_index_ignorable_first - 1
        ]
    # Else, this version specifier contains *NO* optional constraints.
    else:
        python_version_min = requires_python[
            python_version_min_index_ge_first:]
    # print(f'python_version_min: {python_version_min}')
    # print(f'python_version_min_index_ge_first: {python_version_min_index_ge_first}')
    # print(f'python_version_min_index_ignorable_first: {python_version_min_index_ignorable_first}')

    # Return this version specifier.
    return python_version_min


PYTHON_VERSION_MIN: _Optional[str] = (
    # If this package distribution defines the "Requires-Python" key, the value
    # of this key stripped of its ">=" prefix. Notably, the value of this key is
    # the value of the "requires-python" key in the "pyproject.toml" file: e.g.,
    #     requires-python = ">=3.8"
    #
    # Since the latter is guaranteed to be prefixed by the substring ">=" of
    # length 2, removing this prefix from this string yields the minimum version
    # of Python required by this package as a "."-delimited string. Phew!
    _convert_requires_python_to_version_min(
        _package_metadata['Requires-Python'])
    if _package_metadata['Requires-Python'] else
    # Else, this package distribution fails to define this key. In this case,
    # fallback to "None".
    None
)
'''
Human-readable minimum version of Python required by this package as a
``.``-delimited string if this package distribution provides this metadata *or*
:data:`None` otherwise (i.e., if this package distribution fails to provide this
metadata).
'''


PYTHON_VERSION_MIN_PARTS = (
    # If this package distribution defines the "Requires-Python" key, the value
    # of this key stripped of its ">=" prefix and coerced into a tuple of
    # integers.
    _convert_str_version_to_tuple(PYTHON_VERSION_MIN)
    if PYTHON_VERSION_MIN is not None else
    # Else, this package distribution fails to define this key. In this case,
    # fallback to "None".
    None
)
'''
Machine-readable minimum version of Python required by this package as a
tuple of integers if this package distribution provides this metadata *or*
:data:`None` otherwise (i.e., if this package distribution fails to provide this
metadata).
'''

# ....................{ METADATA ~ synopsis                }....................
SYNOPSIS: _Optional[str] = _package_metadata['Summary']
'''
Human-readable single-line synopsis of this package.

By PyPI design, this string must *not* span multiple lines or paragraphs.
'''

# ....................{ METADATA ~ authors                 }....................
AUTHOR_EMAIL: _Optional[str] = _package_metadata['Author-email']
'''
Email address of the principal corresponding author (i.e., the principal author
responding to public correspondence).
'''

# ....................{ PRIVATE ~ callables                }....................
def _init() -> None:
    '''
    Initialize this submodule.

    This initializer validates that the active Python interpreter satisfies the
    minimum Python version required by this project, as published by the
    ``requires-python`` key of the top-level ``pyproject.toml`` file.
    '''

    # Defer function-specific imports for safety.
    from sys import version_info

    # If this physical distribution installed with this package defines the
    # "Requires-Python" key underlying the "PYTHON_VERSION_MIN" string constant,
    # validate the version of the active Python interpreter *BEFORE* subsequent
    # logic possibly depending on this version. Specifically...
    if PYTHON_VERSION_MIN is not None:
        # Machine-readable current version of the active Python interpreter as a
        # tuple of integers.
        _PYTHON_VERSION_PARTS = version_info[:3]

        # If the active Python interpreter fails to satisfy minimum
        # requirements, raise an exception. Note that the "sys" module
        # publicizes three version-related constants for this purpose:
        # * "hexversion", an integer intended to be specified in an obscure
        #   (albeit both efficient and dependable) hexadecimal format: e.g.,
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
        # string-formatted release type of the current Python version exposed
        # via the fourth element of the "version_info" tuple. Since the first
        # three elements of that tuple are guaranteed to be integers *AND* since
        # a comparable 3-tuple of integers is declared above, comparing the
        # former and latter yield the simplest and most reliable Python version
        # test.
        if _PYTHON_VERSION_PARTS < PYTHON_VERSION_MIN_PARTS:  # type: ignore[operator]
            # Human-readable current version of Python. Ideally, "sys.version"
            # would be used here; sadly, that string embeds significantly more
            # than merely a version and hence is inapplicable: e.g.,
            #     >>> import sys
            #     >>> sys.version
            #     '3.6.5 (default, Oct 28 2018, 19:51:39) \n[GCC 7.3.0]'
            _PYTHON_VERSION = '.'.join(
                str(version_part) for version_part in _PYTHON_VERSION_PARTS)

            # Die ignominiously.
            raise RuntimeError(
                f'Beartype requires at least Python {PYTHON_VERSION_MIN}, but '
                f'the active interpreter only targets Python {_PYTHON_VERSION}. '
                f'We feel unbearable sadness for you.'
            )
        # Else, the active Python interpreter satisfies minimum requirements.
    # Else, this physical distribution installed with this package fails to
    # define the "Requires-Python" key underlying the "PYTHON_VERSION_MIN"
    # string constant.
    #
    # Note that this edge case occurs in common use cases that compile,
    # transpile, or freeze this package. While non-ideal, assume that the user
    # knows what the user is doing by assuming the active Python satisfies
    # minimum requirements. Userbase: if you break it, you bought it.


# Initialize this submodule.
_init()
