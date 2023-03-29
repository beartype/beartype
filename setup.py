#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype installer.**

This submodule conforms to the standard :mod:`setuptools`-based "makefile"
format, instrumenting most high-level installation tasks for this package.
'''

# ....................{ TODO                               }....................
#FIXME: Strongly consider migrating to Hatch:
#    https://hatch.pypa.io
#We can't *STAND* poetry, but Hatch looks to be another breed entirely.
#Crucially, PyPA itself has officially adopted Hatch (which is a huge boost),
#Hatch supports dynamic retrieval of version specifiers from Python modules,
#support for PEPs denigrated by poetry authors, and probably much more.
#Basically, Hatch looks like everything we wish poetry was.

# ....................{ KLUDGES ~ path                     }....................
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

# ....................{ KLUDGES ~ init                     }....................
# Explicitly notify the "beartype.__init__" submodule that it is being imported
# at install time from this script. Doing so prevents that submodule from
# implicitly importing from *ANY* "beartype" submodule other than the
# "beartype.meta" submodule, which is the *ONLY* "beartype" submodule guaranteed
# by sheer force of will to be safely importable at install time. All other
# "beartype" submodules should be assumed to be unsafe to import below due to
# potentially importing one or more optional runtime dependencies yet to be
# installed (e.g., the third-party "typing_extensions" package).
#
# Naturally, there exist a countably infinite number of ways to notify the
# "beartype.__init__" submodule that it is being imported at install time. To
# minimize the likelihood of a conflict with other Python subsystems or
# interpreters, we intentionally do *NOT*:
# * Monkey-patch a module or package in the standard library.
# * Detect this script in a stack frame on the call stack.
#
# Instead, we dynamically populate the standard "sys.modules" list of all
# previously imported modules with a fake beartype-specific module. The
# "beartype.__init__" submodule then decides whether to implicitly import from
# potentially unsafe "beartype" submodules by detecting that fake module.

# Isolate this kludge to a private function for safety.
def _notify_beartype() -> None:

    # The acid: it burns more than I expected.
    from sys import modules
    from types import ModuleType

    # Dynamically create a new fake module. Look. Just do it.
    fake_module = ModuleType('beartype.__is_installing__', 'This is horrible.')

    # Dynamically register the fake module. Don't look like that.
    modules['beartype.__is_installing__'] = fake_module

# Setuptools made us do it.
_notify_beartype()

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid race conditions during setuptools-based installation, this
# module may import *ONLY* from packages guaranteed to exist at the start of
# installation. This includes all standard Python and package submodules but
# *NOT* third-party dependencies, which if currently uninstalled will only be
# installed at some later time in the installation.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import setuptools
from beartype import meta

# ....................{ METADATA ~ seo                     }....................
_KEYWORDS = [
    'type checking',
    'type hints',
    'PEP 483',
    'PEP 484',
    'PEP 544',
    'PEP 563',
    'PEP 585',
    'PEP 586',
    'PEP 589',
    'PEP 593',
    'PEP 604',
    'PEP 3141',
]
'''
List of all lowercase alphabetic keywords synopsising this package.

These keywords may be arbitrarily selected so as to pretend to improve search
engine optimization (SEO). In actuality, they do absolutely nothing.
'''

# ....................{ METADATA ~ seo : classifiers       }....................
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
List of all PyPI-specific trove classifier strings synopsizing this project.

Each such string *must* contain either two or three ``" :: "`` substrings
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
        f'"{python_version_min_parts}" not tuple.')
    assert isinstance(python_version_minor_max, int), (
        f'"{python_version_minor_max}" not integer.')

    # Major version of Python required by this package.
    PYTHON_VERSION_MAJOR = python_version_min_parts[0]

    # List of classifiers to return, copied from the global list for safety.
    classifiers_sane = _CLASSIFIERS[:]

    # For each minor version of Python 3.x supported by this package,
    # formally classify this version as such.
    for python_version_minor in range(
        python_version_min_parts[1], python_version_minor_max + 1):
        classifiers_sane.append(
            f'Programming Language :: Python :: '
            f'{PYTHON_VERSION_MAJOR}.{python_version_minor}'
        )
    # print('classifiers: {}'.format(_CLASSIFIERS))

    # Return this sanitized list of classifiers.
    return classifiers_sane

# ....................{ OPTIONS                            }....................
# Setuptools-specific options. Keywords not explicitly recognized by either
# setuptools or distutils must be added to the above dictionary instead.
_SETUP_OPTIONS = {
    # ..................{ CORE                               }..................
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
    'description':      meta.SYNOPSIS,

    # ..................{ AUTHORS                            }..................
    'author':           meta.AUTHORS,
    'author_email':     meta.AUTHOR_EMAIL,
    'maintainer':       meta.AUTHORS,
    'maintainer_email': meta.AUTHOR_EMAIL,

    # ..................{ URLS                               }..................
    'url':              meta.URL_HOMEPAGE,
    'download_url':     meta.URL_DOWNLOAD,

    # Dictionary mapping from arbitrary human-readable terse names describing
    # various package-related URLs to those URLs.
    'project_urls': {
        'Documentation': meta.URL_HOMEPAGE,
        'Source':        meta.URL_REPO,
        'Issues':        meta.URL_ISSUES,
        'Forums':        meta.URL_FORUMS,
        'Releases':      meta.URL_RELEASES,
    },

    # ..................{ PYPI                               }..................
    # PyPi-specific meta.
    'classifiers': _sanitize_classifiers(
        python_version_min_parts=meta.PYTHON_VERSION_MIN_PARTS,
        python_version_minor_max=meta.PYTHON_VERSION_MINOR_MAX,
    ),
    'keywords': _KEYWORDS,
    'license': meta.LICENSE,

    # ..................{ DEPENDENCIES                       }..................
    # Python dependency.
    'python_requires': f'>={meta.PYTHON_VERSION_MIN}',

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

        # All mandatory developer dependencies (including all mandatory test-
        # and documentation build-time dependencies) as referenced from
        # external project documentation for developers.
        'dev': meta.LIBS_DEVELOPER_MANDATORY,

        # All mandatory Read The Docs (RTD)-specific documentation build-time
        # dependencies an arbitrarily named extra. This is required *ONLY*
        # for integration with the top-level ".readthedocs.yml" file. See the
        # "python" key in that file for further details.
        'doc-rtd': meta.LIBS_DOCTIME_MANDATORY_RTD,

        # All mandatory tox-specific testing dependencies, copied from the
        # "tests_require" key below into an arbitrarily named extra. This is
        # required *ONLY* for integration with the top-level "tox.ini" file.
        # See the "extras" key in that file for further details.
        'test-tox': meta.LIBS_TESTTIME_MANDATORY_TOX,

        # All mandatory coverage-specific testing dependencies as an
        # arbitrarily named extra, required *ONLY* for integration with the
        # top-level "tox.ini" file. See the "extras" key in that file.
        'test-tox-coverage': meta.LIBS_TESTTIME_MANDATORY_COVERAGE,
    },

    # Mandatory testing dependencies.
    'tests_require': meta.LIBS_TESTTIME_MANDATORY_TOX,

    # ..................{ PACKAGES                           }..................
    # List of the fully-qualified names of all Python packages (i.e.,
    # directories containing zero or more Python modules) to be installed,
    # including the top-level package and all subpackages of that package. This
    # thus excludes:
    #
    # * The top-level test package and all subpackages of that package,
    #   defining only test functionality *NOT* intended to be installed with
    #   this package.
    # * "build", caching both setuptools metadata and a complete copy of this
    #   package, required only by a prior package installation.
    #
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # WARNING: This inspection intentionally omits subdirectories containing no
    # "__init__.py" file, despite the remainder of the Python ecosystem
    # commonly accepting such subdirectories as subpackages.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    'packages': setuptools.find_packages(exclude=(
        f'{meta.PACKAGE_NAME}_test',
        f'{meta.PACKAGE_NAME}_test.*',
        'build',
    )),

    # ..................{ PACKAGES ~ data                    }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: *ALL DATA FILES TO BE INSTALLED MUST BE EXPLICITLY MATCHED IN
    # THE TOP-LEVEL "MANIFEST.in" FILE.*
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #
    # Install all data files (i.e., non-Python files) embedded in the Python
    # package tree for this project which are also explicitly matched by the
    # top-level "MANIFEST.in" file.
    #
    # Unlike Python packages, undesirable data files are includable and
    # excludable from installation *ONLY* via the external "MANIFEST.in" file.
    # This is terrible, of course. (Did you expect otherwise?)
    #
    # Data files are *NOT* Python modules and hence should *NOT* be embedded in
    # the Python package tree. Sadly, the "data_files" key supported by
    # setuptools for this purpose is *NOT* cross-platform-portable and is thus
    # inherently broken. Why? Because that key either requires usage of
    # absolute paths *OR* relative paths relative to absolute paths defined by
    # "setup.cfg"; in either case, those paths are absolute. While the current
    # platform could be detected and the corresponding absolute path embedded
    # in 'data_files', that implementation would be inherently fragile. (That's
    # bad.) In lieu of sane setuptools support, we defer to the methodology
    # employed by everyone. Setuptools, your death is coming.
    #
    # See also:
    # * "Data Files Support", official documentation for this abomination at:
    #   https://setuptools.readthedocs.io/en/latest/userguide/datafiles.html
    'include_package_data': True,

    # Install to an uncompressed directory rather than a compressed archive.
    #
    # While nothing technically precludes the latter, doing so substantially
    # complicates runtime access of data files compressed into this archive
    # (e.g., with the pkg_resources.resource_filename() function). How so? By
    # decompressing this archive's contents into a temporary directory on
    # program startup and removing these contents on program shutdown. Since
    # there exists no guarantee this removal will actually be performed (e.g.,
    # due to preemptive SIGKILLs), compressed archives are inherently fragile.
    #
    # Note that MyPy requires upstream PEP 561-compliant dependencies (like
    # this project) to explicitly prohibit archival. See also:
    #     https://mypy.readthedocs.io/en/stable/installed_packages.html
    'zip_safe': False,
}
'''
Dictionary unpacked as keyword arguments into the subsequent call of the
:func:`setuptools.setup` function, signifying the set of all package-specific
:mod:`setuptools` options.
'''
# print('extras: {}'.format(setup_options['extras_require']))

# ....................{ SETUP                              }....................
setuptools.setup(**_SETUP_OPTIONS)
