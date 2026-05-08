#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype metaverse** (e.g., submodule exporting scalar global constants safely
describing this package *without* requiring first- or third-party imports from
potentially unsafe external packages or modules residing outside the main
:mod:`beartype` codebase).

This private submodule is imported by the public :mod:`beartype.meta` submodule.
Why? Because that submodule unsafely imports from other packages and modules
(e.g., the standard :mod:`importlib.metadata` submodule), where "unsafely" means
"is well-known to accidentally trigger import cycles in obscure edge cases that
nonetheless arise with disturbing alacrity in real-world production end user
code." Isolating those unsafe imports to that public :mod:`beartype.meta`
submodule empowers the :mod:`beartype` codebase to preferentially import from
this safer private submodule *without* accidentally triggering fragile safety
mechanisms like the recursion guard in the
:meth:`beartype.claw._importlib._clawimpload.BeartypeSourceFileLoader.get_code`
method.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Avoid importing from *ANY* first- or third-party package or module.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._util.text.utiltextversion import (
    convert_str_version_to_tuple as _convert_str_version_to_tuple)

# ....................{ METADATA                           }....................
NAME = 'beartype'
'''
Human-readable package name.
'''


# Ideally, this metadata would be parsed from the "_package_metadata" dictionary
# introspected below. Sadly, this metadata has yet to be standardized. The
# closest approximation is the "_package_metadata['License']" key, which
# provides the contents of the top-level "LICENSE" file rather than the name of
# the license licensing this package. It is what it is. It is sucky. *sigh*
LICENSE = 'MIT'
'''
Human-readable name of the license this package is licensed under.
'''

# ....................{ METADATA ~ package                 }....................
PACKAGE_NAME = NAME
'''
Fully-qualified name of the top-level Python package containing this submodule.
'''


PACKAGE_TEST_NAME = f'{PACKAGE_NAME}_test'
'''
Fully-qualified name of the top-level Python package testing this project.
'''

# ....................{ METADATA ~ version                 }....................
VERSION = '0.23.0'
'''
Human-readable package version as a ``.``-delimited string.
'''


VERSION_PARTS = _convert_str_version_to_tuple(VERSION)
'''
Machine-readable package version as a tuple of integers.
'''

# ....................{ METADATA ~ authors                 }....................
AUTHORS = 'Cecil Curry, et al.'
'''
Human-readable list of all principal authors of this package as a
comma-delimited string.

For brevity, this string *only* lists authors explicitly assigned copyrights.
For the list of all contributors regardless of copyright assignment or
attribution, see the `contributors graph`_ for this project.

.. _contributors graph:
   https://github.com/beartype/beartype/graphs/contributors
'''


COPYRIGHT = '2014-2026 Beartype authors'
'''
Legally binding copyright line excluding the license-specific prefix (e.g.,
``"Copyright (c)"``).

For brevity, this string *only* lists authors explicitly assigned copyrights.
For the list of all contributors regardless of copyright assignment or
attribution, see the `contributors graph`_ for this project.

.. _contributors graph:
   https://github.com/beartype/beartype/graphs/contributors
'''

# ....................{ METADATA ~ urls                    }....................
# Although feasible, parsing URLs from "_package_metadata" is non-trivial.
# Rather than break our body over something nobody cares about, violate the DRY
# (Don't Repeat Yourself) principle by repeating various URLs already specified
# in our top-level "pyproject.toml" file.

URL_BLUESKY = 'https://leycec.bsky.social'
'''
URL of this project's entry on **Bluesky** (i.e., popular third-party social
media site, leveraged by project maintainers to publicly announce new releases
and associated news).
'''


URL_CONDA = f'https://anaconda.org/conda-forge/{PACKAGE_NAME}'
'''
URL of this project's entry on **Anaconda** (i.e., alternate third-party Python
package repository utilized by the Anaconda Python distribution).
'''


URL_LIBRARIES = f'https://libraries.io/pypi/{PACKAGE_NAME}'
'''
URL of this project's entry on **Libraries.io** (i.e., third-party open-source
package registrar associated with the Tidelift open-source funding agency).
'''


URL_PYPI = f'https://pypi.org/project/{PACKAGE_NAME}'
'''
URL of this project's entry on **PyPI** (i.e., official Python package
repository, also colloquially known as the "cheeseshop").
'''


URL_RTD = f'https://readthedocs.org/projects/{PACKAGE_NAME}'
'''
URL of this project's entry on **ReadTheDocs (RTD)** (i.e., popular Python
documentation host, shockingly hosting this project's documentation).
'''


URL_ZULIP = 'https://beartype.zulipchat.com'
'''
URL of this project's entry on **Zulip** (i.e., popular third-party real-time
chat site, leveraged by project maintainers to publicly communicate with the
project userbase).
'''

# ....................{ METADATA ~ urls : docs             }....................
URL_HOMEPAGE = f'https://{PACKAGE_NAME}.readthedocs.io'
'''
URL of this project's homepage.
'''


URL_PEP585_DEPRECATIONS = (
    f'{URL_HOMEPAGE}/en/latest/api_roar/#pep-585-deprecations')
'''
URL documenting :pep:`585` deprecations of :pep:`484` type hints.
'''

# ....................{ METADATA ~ urls : repo             }....................
URL_REPO_ORG_NAME = PACKAGE_NAME
'''
Name of the **organization** (i.e., parent group or user principally responsible
for maintaining this project, indicated as the second-to-last trailing
subdirectory component) of the URL of this project's git repository.
'''


URL_REPO_BASENAME = PACKAGE_NAME
'''
**Basename** (i.e., trailing subdirectory component) of the URL of this
project's git repository.
'''


URL_REPO = f'https://github.com/{URL_REPO_ORG_NAME}/{URL_REPO_BASENAME}'
'''
URL of this project's git repository.
'''


URL_DOWNLOAD = f'{URL_REPO}/archive/{VERSION}.tar.gz'
'''
URL of the source tarball for the current version of this project.

This URL assumes a tag whose name is ``v{VERSION}`` where ``{VERSION}`` is the
human-readable current version of this project (e.g., ``v0.4.0``) to exist.
Typically, no such tag exists for live versions of this project -- which
have yet to be stabilized and hence tagged. Hence, this URL is typically valid
*only* for previously released (rather than live) versions of this project.
'''


URL_FORUMS = f'{URL_REPO}/discussions'
'''
URL of this project's user forums.
'''


URL_ISSUES = f'{URL_REPO}/issues'
'''
URL of this project's issue tracker.
'''


URL_RELEASES = f'{URL_REPO}/releases'
'''
URL of this project's release list.
'''

# ....................{ METADATA ~ dependency : names      }....................
#FIXME: Switch! So, "pydata-sphinx-theme" is ostensibly *MOSTLY* great. However,
#there are numerous obvious eccentricities in "pydata-sphinx-theme" that we
#strongly disagree with -- especially that theme's oddball division in TOC
#heading levels between the top and left sidebars.
#
#Enter "sphinx-book-theme", stage left. "sphinx-book-theme" is based on
#"pydata-sphinx-theme", but entirely dispenses with all of the obvious
#eccentricities that hamper usage of "pydata-sphinx-theme". We no longer have
#adequate time to maintain custom documentation CSS against the moving target
#that is "pydata-sphinx-theme". Ergo, we should instead let "sphinx-book-theme"
#do all of that heavy lifting for us. Doing so will enable us to:
#* Lift the horrifying constraint above on a maximum Sphinx version. *gulp*
#* Substantially simplify our Sphinx configuration. Notably, the entire fragile
#  "doc/src/_templates/" subdirectory should be *ENTIRELY* excised away.
#
#Please transition to "sphinx-book-theme" as time permits.

# Note that documentation-time functionality in the Sphinx-specific
# "doc/src/conf.py" script imports this private string global. *shrug*
SPHINX_THEME_NAME = 'pydata-sphinx-theme'
'''
Name of the third-party Sphinx extension providing the custom HTML theme
preferred by this documentation.

See Also
--------
pyproject.toml
    Further discussion in the ``doc-rtd`` key of our top-level
    ``pyproject.toml`` file.
'''

# ....................{ METADATA ~ dependency : versions   }....................
# Note that test-time functionality imports this private string global. *shrug*
LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_NUMPY = '1.21.0'
'''
Minimum optional version of NumPy recommended for use with this project.

NumPy >= 1.21.0 first introduced the third-party PEP-noncompliant
:attr:`numpy.typing.NDArray` type hint supported by the
:func:`beartype.beartype` decorator.
'''


# Note that test-time functionality imports this private string global. *shrug*
LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_TYPING_EXTENSIONS = '3.10.0.0'
'''
Minimum optional version of the third-party :mod:`typing_extensions` package
recommended for use with this project.

:mod:`typing_extensions` >= 3.10.0.0 backports all :mod:`typing` attributes
unavailable under older Python interpreters supported by the
:func:`beartype.beartype` decorator.
'''
