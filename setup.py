#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype installer.**

This submodule conforms to the standard :mod:`setuptools`-based "makefile"
format, instrumenting most high-level installation tasks for this package.
'''

# ....................{ TODO                              }....................
#FIXME: Generate documentation from the NumPy-style docstrings embedded
#throughout this codebase, presumably with Sphinx + napoleon.
#FIXME: Publish generated documentation to readthedocs.org.
#FIXME: Automate generation and publication of documentation in a manner
#synchronized with our stable release (and possibly CI) process.

# ....................{ KLUDGES                           }....................
# Explicitly register all files and subdirectories of the root directory
# containing this top-level "setup.py" script to be importable modules and
# packages (respectively) for the remainder of this Python process if this
# directory has yet to be registered.
#
# Technically, this should *NOT* be required. The current build framework
# (e.g., "pip", "setuptools") should implicitly guarantee this to be the case.
# Indeed, the "setuptools"-based "easy_install" script does just that.
# Unfortunately, "pip" >= 19.0.0 does *NOT* guarantee this to be the case for
# projects defining a "pyproject.toml" file -- which, increasingly, is all of
# them. Although "pip" purports to have resolved this upstream, current stable
# releases appear to suffer the same deficiencies. See also:
#     https://github.com/pypa/pip/issues/6163

# Isolate this kludge to a private function for safety.
def _register_dir() -> None:

    # Avert thy eyes, purist Pythonistas!
    import os, sys

    # Absolute dirname of this directory inspired by this StackOverflow answer:
    #     https://stackoverflow.com/a/8663557/2809027
    setup_dirname = os.path.dirname(os.path.realpath(__file__))

    # If the current PYTHONPATH does *NOT* already contain this directory...
    if setup_dirname not in sys.path:
        # Print this registration.
        print(
            'WARNING: Registering "setup.py" directory for importation under '
            'broken installer (e.g., pip >= 19.0.0)...',
            file=sys.stderr)
        # print('setup_dirname: {}\nsys.path: {!r}'.format(setup_dirname, sys.path))

        # Append this directory to the current PYTHONPATH.
        sys.path.append(setup_dirname)

# Kludge us up the bomb.
_register_dir()

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid race conditions during setuptools-based installation, this
# module may import *ONLY* from packages guaranteed to exist at the start of
# installation. This includes all standard Python and package submodules but
# *NOT* third-party dependencies, which if currently uninstalled will only be
# installed at some later time in the installation.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import setuptools
from beartype import meta

# ....................{ METADATA ~ seo                    }....................
_KEYWORDS = [
    'type checking',
    'type hints',
    'PEP 484',
]
'''
List of all lowercase alphabetic keywords synopsising this package.

These keywords may be arbitrarily selected so as to pretend to improve search
engine optimization (SEO). In actuality, they do absolutely nothing.
'''

# ....................{ METADATA ~ seo : classifiers      }....................
# To minimize desynchronization woes, all
# "Programming Language :: Python :: "-prefixed strings are dynamically
# appended to this list by the init() function below.
_CLASSIFIERS = [
    # PyPI-specific version type. The number specified here is a magic constant
    # with no relation to this package's version numbering scheme. *sigh*
    'Development Status :: 5 - Production/Stable',

    # Miscellaneous metadata.
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Software Development :: Code Generators',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Quality Assurance',
    'Typing :: Typed',
]
'''
List of all PyPI-specific trove classifier strings synopsizing this
package.

Each such string *must* be contain either two or three `` :: `` substrings
delimiting human-readable capitalized English words formally recognized by the
:mod:`distutils`-specific ``register`` command.

See Also
----------
https://pypi.org/classifiers
    Plaintext list of all trove classifier strings recognized by PyPI.
'''


def _sanitize_classifiers(
    python_version_min_parts: tuple,
    python_version_minor_max: int,
) -> list:
    '''
    List of all PyPI-specific trove classifier strings synopsizing this
    package, manufactured by appending classifiers synopsizing this
    package's support for Python major versions (e.g.,
    ``Programming Language :: Python :: 3.6``, a classifier implying this
    package to successfully run under Python 3.6) to the global list
    :data:`_CLASSIFIERS` of static classifiers.

    Parameters
    ----------
    python_version_min_parts : tuple
        Minimum fully-specified version of Python required by this package
        as a tuple of integers (e.g., ``(3, 5, 0)`` if this package
        requires at least Python 3.5.0).
    python_version_minor_max : int
        Maximum minor stable version of the current Python 3.x mainline (e.g.,
        ``9`` if Python 3.9 is the most recent stable version of Python 3.x).

    Returns
    ----------
    list
        List of all sanitized PyPI-specific trove classifier strings.
    '''
    assert isinstance(python_version_min_parts, tuple), (
        '"{}" not tuple.'.format(python_version_min_parts))
    assert isinstance(python_version_minor_max, int), (
        '"{}" not integer.'.format(python_version_minor_max))

    # Major version of Python required by this package.
    PYTHON_VERSION_MAJOR = python_version_min_parts[0]

    # List of classifiers to return, copied from the global list for safety.
    classifiers_sane = _CLASSIFIERS[:]

    # For each minor version of Python 3.x supported by this package,
    # formally classify this version as such.
    for python_version_minor in range(
        python_version_min_parts[1], python_version_minor_max + 1):
        classifiers_sane.append(
            'Programming Language :: Python :: {}.{}'.format(
                PYTHON_VERSION_MAJOR, python_version_minor,))
    # print('classifiers: {}'.format(_CLASSIFIERS))

    # Return this sanitized list of classifiers.
    return classifiers_sane

# ....................{ OPTIONS                           }....................
# Setuptools-specific options. Keywords not explicitly recognized by either
# setuptools or distutils must be added to the above dictionary instead.
_SETUP_OPTIONS = {
    # ..................{ CORE                              }..................
    # Self-explanatory metadata. Note that the following metadata keys are
    # instead specified by the "setup.cfg" file:
    #
    # * "license_file", for unknown reasons. We should probably reconsider.
    # * "long_description", since "setup.cfg" supports convenient
    #   "file: ${relative_filename}" syntax for transcluding the contents of
    #   arbitrary project-relative files into metadata values. Attempting to do
    #   so here would require safely opening this file with a context manager,
    #   reading the contents of this file into a local variable, and passing
    #   that variable's value as this metadata outside of that context. (Ugh.)
    'name':             meta.PACKAGE_NAME,
    'version':          meta.VERSION,
    'author':           meta.AUTHORS,
    'author_email':     meta.AUTHOR_EMAIL,
    'maintainer':       meta.AUTHORS,
    'maintainer_email': meta.AUTHOR_EMAIL,
    'description':      meta.SYNOPSIS,
    'url':              meta.URL_HOMEPAGE,
    'download_url':     meta.URL_DOWNLOAD,

    # ..................{ PYPI                              }..................
    # PyPi-specific meta.
    'classifiers': _sanitize_classifiers(
        python_version_min_parts=meta.PYTHON_VERSION_MIN_PARTS,
        python_version_minor_max=meta.PYTHON_VERSION_MINOR_MAX,
    ),
    'keywords': _KEYWORDS,
    'license': meta.LICENSE,

    # ..................{ DEPENDENCIES                      }..................
    # Python dependency.
    'python_requires': '>=' + meta.PYTHON_VERSION_MIN,

    # Mandatory runtime dependencies. This package intentionally requires no
    # such dependencies and hopefully never will.
    'install_requires': (),

    # Optional runtime dependencies. Whereas mandatory dependencies are defined
    # as sequences, optional dependencies are defined as a dictionary mapping
    # from an arbitrary alphanumeric word to a sequence containing one or more
    # such dependencies. Such dependencies are then installable via "pip" by
    # suffixing the name of this project by the "["- and "]"-delimited key
    # defined below whose value lists the dependencies to be installed (e.g.,
    # "sudo pip3 install betse[all]", installing both the package and all
    # mandatory and optional dependencies required by the package).
    'extras_require': {
        # All optional runtime dependencies.
        'all': meta.LIBS_RUNTIME_OPTIONAL,

        # All mandatory testing dependencies, copied from the "tests_require"
        # key below into an arbitrarily named extra. This is required *ONLY*
        # for integration with the top-level "tox.ini" file. See the "extras"
        # key in that file for further details.
        'test': meta.LIBS_TESTTIME_MANDATORY,
    },

    # Mandatory testing dependencies.
    'tests_require': meta.LIBS_TESTTIME_MANDATORY,

    # ..................{ PACKAGES                          }..................
    # List of the fully-qualified names of all Python packages (i.e.,
    # directories containing zero or more Python modules) to be installed,
    # including the top-level package and all subpackages of that package. This
    # thus excludes:
    #
    # * The top-level test package and all subpackages of this package, test
    #   functionality *NOT* intended to be installed with this package.
    # * "build", caching both setuptools metadata and a complete copy of this
    #   package, required only by a prior package installation.
    #
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # WARNING: This inspection intentionally omits subdirectories containing no
    # "__init__.py" file, despite the remainder of the Python ecosystem
    # commonly accepting such subdirectories as subpackages.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    'packages': setuptools.find_packages(exclude=(
        meta.PACKAGE_NAME + '_test',
        meta.PACKAGE_NAME + '_test.*',
        'build',
    )),
}
'''
Dictionary unpacked as keyword arguments into the subsequent call of the
:func:`setuptools.setup` function, signifying the set of all package-specific
:mod:`setuptools` options.
'''
# print('extras: {}'.format(setup_options['extras_require']))

# ....................{ SETUP                             }....................
setuptools.setup(**_SETUP_OPTIONS)
