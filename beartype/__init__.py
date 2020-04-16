#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
Top-level package namespace.

For PEP 8 compliance, this namespace exposes a subset of the metadata constants
provided by the top-level :mod:`meta` submodule commonly inspected by external
automation.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid race conditions during setuptools-based installation, this
# module may import *ONLY* from modules guaranteed to exist at the start of
# installation. This includes all standard Python and package submodules but
# *NOT* third-party dependencies, which if currently uninstalled will only be
# installed at some later time in the installation. Likewise, to avoid circular
# import dependencies, the top-level of this module should avoid importing
# package submodules where feasible.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ IMPORTS                           }....................
# For PEP 8 compliance, versions constants expected by external automation are
# imported under their PEP 8-mandated names.
from beartype.meta import VERSION as __version__
from beartype.meta import VERSION_PARTS as __version_info__

# ....................{ IMPORTS ~ __all__                 }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: This submodule (and indeed all submodules of this package)
# intentionally defines the "__all__" list global to reference a single
# attribute guaranteed *NOT* to exist, effectively prohibiting star imports
# from this submodule in downstream modules by raising an "AttributeError"
# exception on the first attempt to do so: e.g.,
#     >>> from beartype import *
#     AttributeError: module 'beartype' has no attribute 'STAR_IMPORTS_CONSIDERED_HARMFUL'
# Why? Because "__all__" is antithetical to sane API design and facilitates
# antipatterns across the Python ecosystem, including well-known harms
# associated with star imports and lesser-known harms associated with the
# artificial notion of an "__all__"-driven "virtual public API:" e.g.,
# * Non-orthogonality. Thanks to "__all__", Python now offers two conflicting
#   conceptions of the public API for a module or package:
#   * The conventional public API. By convention, attributes *NOT* prefixed by
#     "_" are public and thus comprise the public API. Indeed, the standard
#     interpretation of star imports for packages and modules defining *NO*
#     "__all__" list globals is exactly that.
#   * The virtual public API specified by "__all__". This API has no meaningful
#     relation to the conventional public API or, in fact, any attributes
#     actually defined by that package or module. Since upstream packages
#     cannot reasonably prohibit downstream packages from importing public
#     attributes accidentally or intentionally excluded from "__all__",.
#   These conflicting notions are evidenced no more strongly than throughout
#   the Python stdlib itself. Some stdlib modules ignore all notion of a public
#   or private API altogether (e.g., the "inspect" module, which
#   unconditionally introspects all attributes of various types regardless of
#   nomenclature or listing in "__all__"); others respect only the conventional
#   public API (e.g., the "xmlrpc" package, whose server implementation ignores
#   "_"-prefixed methods); still others respect only the virtual public API
#   (e.g., the "pickletools" module, which conditionally introspects the
#   "pickle" module via its "__all__" list global); still others respect either
#   depending on context with bizarre exceptions (e.g., the "pydoc" module,
#   which ignores attributes excluded from "__all__" for packages and modules
#   defining "__all__" and otherwise ignores "_"-prefixed attributes excluding
#    "namedtuple" instances, which are considered public because... reasons).
#   Which of these conflicting interpretations is correct? None and all of
#   them, of course, because there *IS* no correct interpretation. This is bad.
#   This is even badder for packages contractually adhering to semver (i.e.,
#   semantic versioning), despite there existing no uniform agreement in the
#   Python community of what constitutes a "public Python API."
# * Turing completeness. Technically, both the conventional and virtual public
#   APIs are defined only dynamically at runtime by the current Turing-complete
#   Python interpreter. Pragmatically, the conventional public API is usually
#   declared statically; those conventional public APIs that do conditionally
#   declare attributes (e.g., to circumvent platform non-portability) usually
#   go to great lengths to declare a uniform API with stubs raising exceptions
#   on edge cases (e.g., Microsoft Windows). Thus, deciding the conventional
#   public API for any package or module is usually trivial. In contrast,
#   deciding the virtual public API for the same package or module is often
#   non-trivial and occasionally infeasible. While some modules and packages
#   unconditionally declare "__all__" to be a predefined list, others
#   conditionally append and extend "__all__" into a contextually declared list
#   mystically depending on heterogeneous context *NOT* resolvable at authoring
#   time. This includes obscure incantations like the current platform, flags
#   and options enabled at compilation time for C extensions and the active
#   Python interpreter, the conjunction of celestial bodies in accordance with
#   astrological scripture, and abject horrors like dynamically extending the
#   "__all__" exported from one submodule with the "__all__" exported from
#   another submodule not under the direct control of the author of the first.
#   ("__all__" gonna "__all__", bro.)
# * Extraneous cognitive load. To decide what constitutes the "public API" for
#   any given package or module, rational decision-making humans supposedly
#   submit to a sadistic heuristic resembling the following:
#   * Does the package in question define a non-empty "__init__" submodule
#     defining a non-empty "__all__" list global? If so, the attributes listed
#     by this global comprise that package's public API. Since "__all__" is
#     defined only at runtime by a Turing-complete interpreter, however,
#     deciding these attributes is itself a Turing-complete problem.
#   * Else, all non-underscored attributes comprise that package's public API.
#     Since these attributes are also defined only at runtime by a
#     Turing-complete interpreter, deciding these attributes is again a
#     Turing-complete problem -- albeit typically less so. (See above.)
# * Redundancy. "__all__" violates the DRY (Don't Repeat Yourself) principle,
#   thus inviting accidental desynchronization and omissions between the
#   conventional and virtual public APIs for a package or module, leading to...
# * Fragility. By definition, accidentally omitting a public attribute from the
#   conventional public API is infeasible; either an attribute is public by
#   convention or it isn't. However, accidentally omitting a public attribute
#   from the virtual public API is a trivial and all-too-common mishap.
#   Numerous stdlib packages and modules do so. This includes the pivotal
#   "socket" module, whose implementation in the Python 3.6.x series seems to
#   accidentally exclude the public socketpair() function from "__all__" if and
#   only if the private "_socket" C extension also defines the same function --
#   which fundamentally makes no sense at all. (Or does it? Dare mo shiranai.)
# * Inconsistency. Numerous modules and packages explicitly declaring "__all__"
#   randomly exclude public attributes from their virtual public API for
#   spurious and frankly indefensible reasons. This includes the crucial
#   "typing" module, whose preamble reads:
#       The pseudo-submodules 're' and 'io' are part of the public
#       namespace, but excluded from __all__ because they might stomp on
#       legitimate imports of those modules.
#   This is the worst of all possible worlds. A module or package should either
#   ignore "__all__" (as most modules do), prohibit "__all__" (as this
#   package does), or declare a self-consistent "__all__" conforming to sane
#   expectations. By the Gods, "__all__" must die and its death must come soon.
# * Nonconsensus. No consensus exists amongst either stdlib developers or the
#   Python community as a whole as to the interpretation of "__all__".
#   Third-party authors conventionally ignore "__all__" with respect to its
#   role in defining a virtual public API, instead treating "__all__" as merely
#   a means of restricting star imports to some well-defined subset of
#   conventional public attributes. This includes SciPy, which excludes most
#   conventional public subpackages of interest while paradoxically including
#   other public subpackages of little to no interest (e.g., "scipy.test", a
#   unit test scaffold commonly run only by developers and maintainers).
# * Infeasibility. We have established that no two packages or modules
#   (including both stdlib and third-party) agree as to the usage of "__all__".
#   Respecting the virtual public API would require authors to ignore public
#   attributes omitted from "__all__", including those omitted by either
#   accident or due to conflicting interpretations of "__all__". Since this is
#   pragmatically infeasible, most authors justifiably ignore "__all__". So
#   should you.
# * Unnecessary. The conventional public API already exists. The virtual public
#   API offers no tangible benefits over the conventional public API and,
#   indeed, offers all of the above harms. Under any rational assessment, the
#   virtual public API can only be "considered harmful."
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ GLOBALS                           }....................
# Document all global variables imported into this namespace above.

__version__
'''
Human-readable package version as a ``.``-delimited string.

For PEP 8 compliance, this specifier has the canonical name ``__version__``
rather than that of a typical global (e.g., ``VERSION_STR``).
'''


__version_info__
'''
Machine-readable package version as a tuple of integers.

For PEP 8 compliance, this specifier has the canonical name
``__version_info__`` rather than that of a typical global (e.g.,
``VERSION_PARTS``).
'''
