#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.
#
# --------------------( SYNOPSIS                           )--------------------
# File configuring this project for documentation by Sphinx.
#
# --------------------( SEE ALSO                           )--------------------
# * https://www.sphinx-doc.org/en/master/usage/configuration.html
#   List of all options supported in this file.

# ....................{ TODO                               }....................
#FIXME: [ICON] Define the "html_favicon" setting as well -- once we actually
#create a favicon, of course. *sigh*

#FIXME: [THEME] Consider generalizing our theme from the somewhat low-level
#"pydata-sphinx-theme" theme to the substantially higher-level
#"sphinx-book-theme". The latter is built in terms of the former, but layers on
#additional functionality for interactive Jupyter BinderHub-based cell content.
#That would be just fantastic, because we have so *UTTERLY* much "code-block"
#content distributed across our documentation; rendering that as interactive
#content that users could actually run would be a *HUGE* win. See also:
#    https://github.com/executablebooks/sphinx-book-theme

#FIXME: [EXTENSION] Add "sphinx-notfound-page" support to enable us to provide
#a sane 404 page for non-existent pages. In fact, we already appear to have a
#"404.rst" document. Well, isn't that noice. Because we can't be bothered to
#configure this at the moment, note that:
#* We've temporarily moved "404.rst" into the parent subdirectory, where it
#  has absolutely no effect (but at least does *NOT* induce fatal errors).
#* We'll need to move "404.rst" back into this subdirectory first.

# ....................{ IMPORTS ~ path                     }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Avoid importing from *ANY* package or module other than those
# provided by Python's standard library. Since Python's import path (i.e.,
# "sys.path") has yet to be properly established, imports from this project in
# particular are likely to fail under common edge cases.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Preliminary imports from Python's standard library required to establish the
# directory structure for this project.
import sys
from pathlib import Path

# ....................{ PRIVATE ~ path                     }....................
# High-level "Path" object encapsulating the absolute dirname of the directory
# containing the current Sphinx configuration file.
#
# Note that the comparable Path.absolute() method was neither documented nor
# tested before Python 3.11. See also this relevant StackOverflow answer:
#     https://stackoverflow.com/a/44569249/2809027
# Dismantled, this is:
#
# * ".resolve(...)", creating and returning a new high-level "Path" object
#   canonicalizing the relative dirname with which the original "Path" object
#   was instantiated into an absolute dirname.
# * "strict=True", raising a "FileNotFoundError" if this directory does *NOT*
#   exist.
_DOC_SRC_DIR = Path(__file__).parent.resolve(strict=True)

# High-level "Path" object encapsulating the absolute dirname of this project's
# root directory, containing:
# * The main directory implementing this project's Python package.
# * The test directory implementing this project's pytest test suite.
# * The documentation directory containing this configuration script.
# * The ".git/" subdirectory if this is the live GitHub-based version.
_ROOT_DIR = Path(_DOC_SRC_DIR / '../../').resolve(strict=True)

# Expose this project's top-level package directory to Python and thus Sphinx.
# Note that this is effectively required to avoid common edge cases. See also:
# * https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs
#   The "Make autodoc actually work" is the canonical writeup on this kludge.
sys.path.insert(0, str(_ROOT_DIR))
# print(f'sys.path (from "doc/source/conf.py"): {sys.path}')

# ....................{ IMPORTS                            }....................
# Sphinx defaults to hardcoding version specifiers. Since this is insane, we
# import our package-specific version specifier for reuse below. See also:
# * https://protips.readthedocs.io/git-tag-version.html
#   "Inferring Release Number from Git Tags", detailing a clever one-liner
#   harvesting this specifier from the most recent git tag.
from beartype.meta import (
    AUTHORS,
    COPYRIGHT,
    NAME,
    SPHINX_THEME_NAME,
    URL_CONDA,
    URL_LIBRARIES,
    URL_PYPI,
    URL_RTD,
    URL_REPO,
    URL_REPO_ORG_NAME,
    URL_REPO_BASENAME,
    VERSION,
)
from beartype.typing import Optional
from beartype._util.module.utilmodimport import import_module_attr
from beartype._util.module.utilmodtest import is_module
# from warnings import warn

# ....................{ PRIVATE ~ path : more              }....................
# High-level "Path" object encapsulating the absolute dirname of this project's
# top-level package directory, raising a "FileNotFoundError" if this directory
# does *NOT* exist.
#
# Note that this requires the "sys.path" global to be properly established above
# and *MUST* thus be deferred until after that.
_PACKAGE_DIR = (_ROOT_DIR / NAME).resolve(strict=True)

# Relative filename of our URI repository (i.e., hidden reStructuredText (reST)
# document defining common URI links in reST format, exposed to all other reST
# documents via the "rst_epilog" setting below).
_LINKS_FILENAME = str((_DOC_SRC_DIR / '_links.rst').resolve(strict=True))

# ....................{ CONSTANTS ~ sphinx                 }....................
# Sphinx-specific metadata programmatically published by this package.
project = NAME
author = AUTHORS
copyright = COPYRIGHT
release = VERSION
version = VERSION

# ....................{ SETTINGS                           }....................
# List of zero or more Sphinx-specific warning categories to be squelched (i.e.,
# suppressed, ignored).
suppress_warnings = [
    #FIXME: *THIS IS TERRIBLE.* Generally speaking, we do want Sphinx to inform
    #us about cross-referencing failures. Remove this hack entirely after Sphinx
    #resolves this open issue: https://github.com/sphinx-doc/sphinx/issues/4961
    # Squelch mostly ignorable warnings resembling:
    #     WARNING: more than one target found for cross-reference 'TypeHint':
    #     beartype.door._doorcls.TypeHint, beartype.door.TypeHint
    #
    # Sphinx currently emits *HUNDREDS* of these warnings against our
    # documentation. All of these warnings appear to be ignorable. Although we
    # could explicitly squelch *SOME* of these warnings by canonicalizing
    # relative to absolute references in docstrings, Sphinx emits still others
    # of these warnings when parsing PEP-compliant type hints via static
    # analysis. Since those hints are actual hints that *CANNOT* by definition
    # by canonicalized, our only recourse is to squelch warnings altogether.
    'ref.python',
]

# ....................{ SETTINGS ~ path                    }....................
# List of pathname patterns relative to this "doc/src/" subdirectory matching
# all files and directories to be ignored when finding source files. Note this
# list also affects the "html_static_path" and "html_extra_path" settings.
#
# Note that this global obsoletes the prior "unused_doc", which served a similar
# goal -- albeit in a less general-purpose manner.
exclude_patterns = [
    # Ignore our URI repository, which magical logic below dynamically includes
    # on all pages through the classic "rst_epilog" trick.
    '_links.rst',
]

# ....................{ SETTINGS ~ rst                     }....................
# String of arbitrary reStructuredText (reST) to be implicitly prepended to the
# contents of *ALL* reST documents rendered by this configuration, initialized
# to the empty string for safety.
rst_prolog = '''
.. tip::

   `Feed the bear <GitHub Sponsors_>`__! `Animals wearing jewelry
   <beadspace9_>`__! *What is even going on with this banner!?*
'''

# String of arbitrary reStructuredText (reST) to be implicitly appended to the
# contents of *ALL* reST documents rendered by this configuration, initialized
# to the empty string for safety.
rst_epilog = ''

# Append the contents of our URI repository file to this string, exposing the
# common URI links centralized in this file to all other reST documents.
#
# See also this StackOverflow answer strongly inspiring this implementation:
#     https://stackoverflow.com/a/61694897/2809027
with open(_LINKS_FILENAME, encoding='utf-8') as links_file:
    rst_epilog += links_file.read()
# print(f'rst_epilog: {rst_epilog}')

# ....................{ EXTENSIONS ~ mandatory             }....................
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    # ..................{ BUILTIN                            }..................
    # Builtin extensions unconditionally available under *ALL* reasonably
    # modern versions of Sphinx uniquely prefixed by "sphinx.ext.".

    #FIXME: Uncomment when enabling "autoapi" support, please. *sigh*
    # # Builtin extension enabling support for type hint introspection in API
    # # generation extensions (e.g., "autoapi", "autodoc").
    # #
    # # The third-party "autoapi" extension implicitly requires this extension to
    # # be enabled as a prerequisite for its own type hint introspection. We
    # # intentionally enable this extension despite *NOT* using "autodoc".
    # 'sphinx.ext.autodoc',

    # Builtin extension automatically creating one explicit globally
    # cross-referenceable target "{/document/basename}:{section_title}" for each
    # section titled "{section_title}" of each document residing at
    # "{/document/basename}". By default, Sphinx requires targets to be manually
    # prepended before all sections to be cross-referenced elsewhere. *facepalm*
    'sphinx.ext.autosectionlabel',

    # Builtin extension enabling attributes defined by the standard library
    # (e.g., the "typing" module, the "types.GenericAlias" type) to be
    # cross-referenced as a fallback when *NOT* already defined by this project.
    "sphinx.ext.intersphinx",

    # Builtin extension autogenerating reStructuredText documentation from
    # class, callable, and variable docstrings embedded in Python modules
    # formatted according to either NumPy or Google style.
    #
    # Note this effectively requires 'sphinx.ext.autodoc' to be listed as well.
    'sphinx.ext.napoleon',

    # Builtin extension rendering "math::" directives into HTML-only JavaScript
    # via the third-party MathJax library.
    'sphinx.ext.mathjax',

    # Builtin extension autogenerating reStructuredText documentation listing
    # each of this project's Python modules and linking external references to
    # those modules to these listings.
    'sphinx.ext.viewcode',

    # ..................{ THIRD-PARTY                        }..................
    # Third-party Sphinx extensions required to be externally installed. For
    # usability, this block should typically be empty. Third-party Sphinx
    # extensions should ideally be optionally enabled. See below.

    # Third-party "autoapi" Sphinx extension actively maintained by Read The
    # Docs (RTD) and an alternative to the builtin "autodoc" Sphinx extension.
    # "autoapi" is strongly preferable to "autodoc" in the modern context, as:
    # * "autodoc" dynamically imports *ALL* Python modules to be documented and
    #   thus executes *ALL* module-scoped code in those modules at documentation
    #   time, significantly complicating documentation time in the event of
    #   module-scoped code *NOT* expected to be executed at documentation time.
    #   Conversely, "autoapi" simply statically parses the same modules and thus
    #   entirely circumvents the arbitrary code execution "pain point."
    # * "autosummary" (another builtin Sphinx extension typically used to
    #   conjunction with "autodoc" to generate table of contents (TOC) entries)
    #   defaults to a silent noop; even when configured to generate non-empty
    #   content, however, "autosummary" fails to document class- or
    #   module-scoped attributes due to long-standing Sphinx limitations.
    #   Conversely, "autoapi" generates usable TOC entries out-of-the-box with
    #   *NO* configuration or kludges required.

    #FIXME: Temporarily disabled in a pell-mell rush to host our "README.rst"
    #file on RTD. Once we finish that laborious process, let's revisit
    #"autoapi". Doing so will prove non-trivial, as "autoapi" currently emits
    #~300 warnings -- some of which are ignorable, but most of which are not.
    # 'autoapi.extension',
]

# ....................{ EXTENSIONS ~ optional              }....................
# Third-party Sphinx extensions conditionally used if externally installed.

# ....................{ EXTENSIONS ~ optional : theme      }....................
# Fully-qualified name of the package providing the third-party Sphinx extension
# defining the custom HTML theme preferred by this documentation, globally
# substituting hyphens with underscores to produce a valid Python identifier.
_SPHINX_THEME_MODULE_NAME = SPHINX_THEME_NAME.replace('-', '_')

# If this package is importable under the active Python interpreter, enable this
# theme for improved HTML rendering.
if is_module(_SPHINX_THEME_MODULE_NAME):
    # Set the HTML theme to this package.
    #
    # Note that we do *NOT* do this, which non-theme extensions require:
    #     # Register the fully-qualified name of this extension.
    #     extensions.append(SPHINX_THEME_NAME)
    #
    # Why? Because doing so induces this exception from modern themes like Furo
    # and PyData:
    #     Extension error (furo):
    #     Handler <function _builder_inited at 0x7f9be7bf2040> for event
    #     'builder-inited' threw an exception (exception: Did you list 'furo' in
    #     the `extensions` in conf.py? If so, please remove it. Furo does not
    #     work with non-HTML builders and specifying it as an `html_theme` is
    #     sufficient.)
    html_theme = _SPHINX_THEME_MODULE_NAME

    #FIXME: *KLUDGE WARNING.* Revert this to just the following one-liner *AFTER*
    #successfully upgrading to the most recent stable release of the PyData theme:
    #    # Add any paths that contain templates here, relative to this directory.
    #    templates_path = ['_templates']

    # String version of the currently installed version of this theme.
    _SPHINX_THEME_MODULE_VERSION = import_module_attr(
        f'{_SPHINX_THEME_MODULE_NAME}.__version__')

    # If this version is that of a version known to supply the requisite Jinja2
    # functionality required by project-specific templates...
    if _SPHINX_THEME_MODULE_VERSION == '0.7.2':
        # Add any paths that contain templates here, relative to this directory.
        templates_path = ['_templates']
    # Else, silently ignore these templates. Attempting to use this templates
    # under any other version of this theme is likely to raise exceptions: e.g.,
    #     Theme error:
    #     An error happened in rendering the page api.
    #     Reason: UndefinedError("'generate_nav_html' is undefined")
# Else, this theme is unavailable. In this case, fallback to Sphinx's default
# HTML theme *AND*...
else:
    #FIXME: Convert this back into a warning by calling warn() *AFTER* deciding
    #how to do so safely. The core issue is that we convert warnings into
    #failures during testing; ergo, we need to install the Python package
    #providing this theme during testing. We can't be bothered at the moment.

    # Emit a non-fatal warning informing end users of this fallback.
    print(
        (
            f'WARNING: Optional Sphinx extension "{SPHINX_THEME_NAME}" '
            f'not found; falling back to default Sphinx HTML theme.'
        ),
    )

# ....................{ EXTENSIONS ~ optional : non-theme  }....................
#FIXME: Restore @beartype once working. For unknown reasons, ReadTheDocs (RTD)
#fails with non-human-readable exceptions *REMOTELY* when we attempt to decorate
#a function defined in this file by @beartype. We have tried in vain to
#replicate this locally (e.g., in our test_sphinx_docs_other() functional test).
#Until we can, attempting to resolve this is mostly an exercise in futility.
#FIXME: Actually, that test does now replicate this issue. Let's investigate
#further via that test when time permits, please.
#@beartype
def _register_extension_or_warn(
    # Mandatory parameters.
    extension_name: str,

    # Optional parameters.
    warning_message: Optional[str] = None,
) -> None:
    '''
    Register the extension with the passed package name if that package is
    importable under the active Python interpreter *or* print a non-fatal
    warning otherwise (i.e., if that package is unimportable).

    Parameters
    ----------
    extension_name : str
        Fully-qualified name of the package providing this extension.
    warning_message : Optional[str]
        Human-readable message to be printed when this package is unimportable.
        Defaults to :data:`None`, in which case a standard message is printed.
    '''

    # If this package is importable under the active Python interpreter, append
    # the name of this package to the list of all Sphinx extensions to enable.
    if is_module(extension_name):
        extensions.append(extension_name)
    # Else, this package is unimportable. In this case, print the passed
    # non-fatal warning message.
    else:
        # Substring unconditionally prefixing this warning message.
        WARNING_MESSAGE_PREFIX = (
            f'WARNING: Optional Sphinx extension "{extension_name}" not found.')

        # Replace this warning message with either...
        warning_message = (
            # If the caller passed a warning message, this message prefixed by
            # this substring;
            f'{WARNING_MESSAGE_PREFIX} {warning_message}'
            # Else, this prefix as is.
            if warning_message else
            WARNING_MESSAGE_PREFIX
        )

        # Print this warning message.
        print(warning_message)


#FIXME: Uncomment *AFTER* this extension resolves this currently open issue:
#    https://github.com/wpilibsuite/sphinxext-opengraph/issues/98
# # Register the third-party "sphinxext-opengraph" extension if available. This
# # extension autogenerates Open Graph metadata describing this documentation.
# # Social media and search engine giants commonly consume this metadata to
# # optimize both the ranking and presentation of links to this documentation.
# _register_extension_or_warn('sphinxext.opengraph')

# ....................{ EXTENSIONS ~ autodoc               }....................
# "autoapi.extension"-specific settings. See also:
#     https://sphinx-autoapi.readthedocs.io/en/latest/reference/config.html

# Machine-readable string identifying the software language to be documented.
autoapi_type = 'python'

# List of the relative or absolute dirnames of all input top-level package
# directories to be recursively documented for this project.
autoapi_dirs = [str(_PACKAGE_DIR)]

# Relative dirname of the output subdirectory to add generated API documentation
# files, relative to the subdirectory containing this file (i.e., "doc/src/").
autoapi_root = 'api'

# Instruct "autoapi" to...
autoapi_options = [
    # Document public documented attributes of modules and classes.
    'members',

    # Document public undocumented attributes of modules and classes. *gulp*
    'undoc-members',

    # Document dunder attributes of modules and classes. Although often
    # ignorable for documentation purposes, dunder attributes can be documented
    # with non-ignorable docstrings intended to be exposed as documentation.
    # This includes the public "beartype.door.TypeHint" class, whose
    # well-documented dunder methods benefit from exposure to users.
    'special-members',

    # List all superclasses of classes.
    'show-inheritance',

    # Include "autosummary" directives in generated module documentation.
    'show-module-summary',

    # List attributes imported from the same package.
    'imported-members',
]

#FIXME: Uncomment as needed to debug local "autoapi" issues.
# autoapi_keep_files = True

#FIXME: Consider customizing "autoapi" templates at some point. For now, the
#defaults suffice. See also this useful article on the subject:
#    https://bylr.info/articles/2022/05/10/api-doc-with-sphinx-autoapi/#setting-up-templates
#See also the official How-To at:
#    https://sphinx-autoapi.readthedocs.io/en/latest/how_to.html#how-to-customise-layout-through-templates

# ....................{ EXTENSIONS ~ autodoc               }....................
# "sphinx.ext.autodoc"-specific settings. See also:
#     https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

# Instruct API generation extensions (e.g., "autoapi", "autodoc") to globally
# append type hints annotating callable signatures to the parameters and returns
# they annotate in the content (i.e., descriptions) of those callables. Note
# this requires Sphinx >= 4.1.
#
# Since the third-party "autoapi" extension implicitly supports this setting, we
# intentionally define this setting despite *NOT* using "autodoc".
autodoc_typehints = 'both'

# ....................{ EXTENSIONS ~ autosectionlabel      }....................
# 'sphinx.ext.autosectionlabel'-specific settings. See also:
#     https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html

# Instruct "autosectionlabel" to uniquify created targets by prefixing section
# titles with document pathnames in these targets. By default, this extension
# ambiguously creates targets as section titles; that simplistic scheme fails
# when two or more documents share the same section titles, a common use case
# that's effectively infeasible to prohibit.
autosectionlabel_prefix_document = True

# ....................{ EXTENSIONS ~ intersphinx           }....................
# 'sphinx.ext.intersphinx'-specific settings. See also:
#     https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

# Dictionary mapping from the machine-readable name of each external project to
# search for references to otherwise missing references in reStructuredText
# (reST) documentation as a graceful fallback to a 2-tuple "(URI, inventory)",
# where "inventory" is typically ignorable and thus "None" for our purposes.
#
# Note that:
# * The keys of this dictionary may be used to unambiguously reference
#   attributes of that external project in reST documentation: e.g.,
#       # External link to Python's Comparison Manual.
#       external:python+ref:`comparison manual <comparisons>`
# * The contents of this dictionary are mostly derived from this popular
#   well-maintained Gist on the subject:
#   https://gist.github.com/bskinn/0e164963428d4b51017cebdb6cda5209
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy':  ('https://numpy.org/doc/stable', None),
    'pandas': ('https://pandas.pydata.org/docs', None),
    'scipy':  ('https://docs.scipy.org/doc/scipy', None),
}

# ....................{ EXTENSIONS ~ napoleon              }....................
# 'sphinx.ext.napoleon'-specific settings. See also:
#     https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

# Force Napolean to *ONLY* parse docstrings in the NumPy format used by this
# project. By default, Napolean attempts and often fails to permissively parse
# docstrings in both Google and NumPy formats.
napoleon_numpy_docstring = True
napoleon_google_docstring = False

# List of the names of all non-standard section headers (i.e., headers *NOT*
# already supported out-of-the-box by Napoleon) embedded in docstrings
# throughout this project. By default, Napolean silently ignores *ALL* content
# in non-standard section headers.
#
# See also:
# * This list of all standard section headers:
#   https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#docstring-sections
napoleon_custom_sections = [
    'Caveats',
    'Design',
    'Motivation',
    'Usage',
]

#FIXME: Experiment with enabling these non-default settings as well.
# napoleon_use_param = False
# napoleon_use_ivar = True

# ....................{ EXTENSIONS ~ pygments              }....................
#FIXME: Uncomment as desired. Let's see how the defaults do first, please.
# # Pygments style.
# pygments_style = "autumn"
# pygments_dark_style = "monokai"

# ....................{ LANG ~ python                      }....................
# Wrap Python callable and class signatures exceeding this maximum number of
# plaintext characters such that each parameter of those signatures is then
# delegated its own discrete line.
python_maximum_signature_line_length = 80

# ....................{ BUILD ~ html                       }....................
# Relative filename or URL of a small image (i.e., no wider than 200px) to be
# rendered in the upper left-hand corner of the sidebar for this theme.
html_logo = 'https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files;
# ergo, a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Dictionary mapping from the names of theme-specific options to those options.
html_context = {
    # ....................{ PYDATA                         }....................
    # HTML options specific to the "pydata-sphinx-theme" theme.

    # Default the current theme to dark rather than light. Embrace the darkness!
    'default_mode': 'dark',

    # ....................{ PYDATA ~ edit                  }....................
    # HTML options supporting the "use_edit_page_button" setting enabled below.

    'github_user': URL_REPO_ORG_NAME,
    'github_repo': URL_REPO_BASENAME,
    'github_version': 'main',
    'doc_path': 'doc/src',
}

# Dictionary mapping from the names of theme-specific options to those options.
# We have *NO* idea why Sphinx supports both this and the parallel
# "html_context" dictionary -- but it does. (Just pretend this isn't happening.)
html_theme_options = {
    # ....................{ PYDATA                         }....................
    # HTML options specific to the "pydata-sphinx-theme" theme.

    #FIXME: Add favicon support here, please. See also:
    #    https://pydata-sphinx-theme.readthedocs.io/en/v0.7.2/user_guide/configuring.html#adding-favicons

    # Announcement banner defined as a string of arbitrary HTML, temporarily
    # displayed at the top of each page until the user begins scrolling.
    'announcement': (
        '<p>'
        '<a href="https://github.com/sponsors/leycec">Feed the bear</a>! '
        '<a href="https://beadspace9.ca">Animals wearing jewelry</a>! '
        '<i>What is even going on with this banner!?</i>'
        '</p>'
    ),

    # List of one or more icon link descriptions. See also:
    # * Official theme-specific documentation for this setting:
    #   https://pydata-sphinx-theme.readthedocs.io/en/v0.7.2/user_guide/configuring.html#configure-icon-links
    # * Official search engine for icons published by the third-party
    #   "FontAwesome 5 Free" project and supported by this setting:
    #   https://fontawesome.com/icons?d=gallery&m=free
    #
    # Note that:
    # * This theme requires long-form FontAwesome styles (e.g., "fa-brand",
    #   "fa-solid") to be abbreviated to these three-letter abbreviations:
    #   * "fa-brand" -> "fab".
    #   * "fa-regular" -> "far".
    #   * "fa-solid" -> "fas".
    'icon_links': [
        {
            'name': 'GitHub',
            'url': URL_REPO,
            'icon': 'fab fa-github-square',
        },
        {
            'name': 'PyPI',
            'url': URL_PYPI,
            'icon': 'fab fa-python',
        },
        {
            'name': 'Anaconda',
            'url': URL_CONDA,
            'icon': 'far fa-circle',
        },
        {
            'name': 'Libraries.io',
            'url': URL_LIBRARIES,
            'icon': 'fas fa-chart-area',
        },
        {
            'name': 'ReadTheDocs',
            'url': URL_RTD,
            'icon': 'fas fa-book',
        },
    ],

    # Add an "Edit this Page" button to the secondary sidebar of each page,
    # enabling users to trivially submit an automated pull request (PR) politely
    # requesting modifications to the contents of that page.
    #
    # Note that enabling this also requires adding various URIs and paths to
    # the "html_context" global describing the remote host hosting this git
    # repository (e.g., GitHub).
    #
    # See also upstream documentation on this subject:
    #     https://pydata-sphinx-theme.readthedocs.io/en/latest/user_guide/source-buttons.html
    'use_edit_page_button': True,
}

#FIXME: This setting is currently undocumented but appears to internally govern
#the "n_links_before_dropdown" parameter passed to the
#generate_header_nav_html() function. Submit an issue requesting documentation!
#FIXME: As expected, this is ignored. Until resolved, let's try temporarily
#resolving this on our end by overriding the "navbar-nav.html" template. See:
#    https://github.com/pydata/pydata-sphinx-theme/blob/157c9ab2c93e755141e48d13b5f193c6169d9dd8/src/pydata_sphinx_theme/theme/pydata_sphinx_theme/components/navbar-nav.html#L8
#
#Issue, please!

# Increase the maximum number of links displayed by "pydata-sphinx-theme" in the
# top-most navigation bar. "pydata-sphinx-theme" displays all remaining links in
# a dropdown entitled "More" that, when clicked, vertically lists those links.
# "pydata-sphinx-theme" defaults this global to 5, which is insufficient for the
# larger number of links required for this documentation.
theme_header_links_before_dropdown = 10
