#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype.**

For PEP 8 compliance, this namespace exposes a subset of the metadata constants
provided by the top-level :mod:`meta` submodule commonly inspected by external
automation.
'''

# ....................{ TODO                              }....................
#FIXME: Consider significantly expanding the above module docstring, assuming
#Sphinx presents this module in its generated frontmatter.

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid race conditions during setuptools-based installation, this
# module may import *ONLY* from modules guaranteed to exist at the start of
# installation. This includes all standard Python and package submodules but
# *NOT* third-party dependencies, which if currently uninstalled will only be
# installed at some later time in the installation. Likewise, to avoid circular
# import dependencies, the top-level of this module should avoid importing
# package submodules where feasible.
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ IMPORTS                           }....................
# Publicize the private @beartype._decor.beartype decorator as
# @beartype.beartype, preserving all implementation details as private.
from beartype._decor.main import beartype

# For PEP 8 compliance, versions constants expected by external automation are
# imported under their PEP 8-mandated names.
from beartype.meta import VERSION as __version__
from beartype.meta import VERSION_PARTS as __version_info__

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


# Intentionally defined last, as nobody wants to stumble into a full-bore rant
# first thing in the morning.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']
'''
Special list global referencing a single attribute guaranteed *not* to exist.

The definition of this global effectively prohibits star imports from this
submodule into downstream modules by raising an :class:`AttributeError`
exception on the first attempt to do so: e.g.,

.. code::

   >>> from beartype import *
   AttributeError: module 'beartype' has no attribute 'STAR_IMPORTS_CONSIDERED_HARMFUL'

All package submodules intentionally define similar ``__all__`` list globals.
Why? Because ``__all__`` is antithetical to sane API design and facilitates
antipatterns across the Python ecosystem, including well-known harms associated
with star imports and lesser-known harms associated with the artificial notion
of an ``__all__``-driven "virtual public API:" to wit,

* **Competing standards.** Thanks to ``__all__``, Python now provides two
  conflicting conceptions of what constitutes the public API for a package or
  module:

  * The **conventional public API.** By convention, all module- and
    class-scoped attributes *not* prefixed by ``_`` are public and thus
    comprise the public API. Indeed, the standard interpretation of star
    imports for packages and modules defining *no* ``__all__`` list globals is
    exactly this.
  * The **virtual public API.** By mandate, all module-scoped attributes
    explicitly listed by the ``__all__`` global are public and thus *also*
    comprise the public API. Consider the worst case of a module artificially
    constructing this global to list all private module-scoped attributes
    prefixed by ``_``; then the intersection of the conventional and virtual
    public APIs for that module would be the empty list and these two competing
    standards would be the list negations of one another. Ergo, the virtual
    public API has no meaningful relation to the conventional public API or any
    public attributes actually defined by any package or module.

  These conflicting notions are evidenced no more strongly than throughout the
  Python stdlib itself. Some stdlib modules ignore all notions of a public or
  private API altogether (e.g., the :mod:`inspect` module, which
  unconditionally introspects all attributes of various types regardless of
  nomenclature or listing in ``__all__``); others respect only the conventional
  public API (e.g., the :mod:`xmlrpc` package, whose server implementation
  ignores ``_``-prefixed methods); still others respect only the virtual public
  API (e.g., the :mod:`pickletools` module, which conditionally introspects the
  :mod:`pickle` module via its ``__all__`` list global); still others respect
  either depending on context with bizarre exceptions (e.g., the :mod:`pydoc`
  module, which ignores attributes excluded from ``__all__`` for packages and
  modules defining ``__all__`` and otherwise ignores ``_``-prefixed attributes
  excluding :class:`collections.namedtuple` instances, which are considered
  public because... reasons).

  Which of these conflicted interpretations is correct? None and all of them,
  since there is no correct interpretation. This is bad. This is even badder
  for packages contractually adhering to `semver (i.e., semantic versioning)
  <semver_>`__, despite there existing no uniform agreement in the Python
  community as to what constitutes a "public Python API."
* **Turing completeness.** Technically, both the conventional and virtual
  public APIs are defined only dynamically at runtime by the current
  Turing-complete Python interpreter. Pragmatically, the conventional public
  API is usually declared statically; those conventional public APIs that do
  conditionally declare public attributes (e.g., to circumvent platform
  portability concerns) often go to great and agonizing pains to declare a
  uniform API with stubs raising exceptions on undefined edge cases. Deciding
  the conventional public API for a package or module is thus usually trivial.
  However, deciding the virtual public API for the same package or module is
  often non-trivial or even infeasible. While many packages and modules
  statically define ``__all__`` to be a simple context-independent list, others
  dynamically append and extend ``__all__`` with context-dependent list
  operations mystically depending on heterogeneous context *not* decidable at
  authoring time -- including obscure incantations such as the active platform,
  flags and options enabled at compilation time for the active Python
  interpreter and C extensions, the conjunction of celestial bodies in
  accordance with astrological scripture, and abject horrors like dynamically
  extending the ``__all__`` exported from one submodule with the ``__all__``
  exported from another not under the control of the author of the first.
  (``__all__`` gonna ``__all__``, bro.)
* **Extrinsic cognitive load.** To decide what constitutes the "public API" for
  any given package or module, rational decision-making humans supposedly
  submit to a sadistic heuristic resembling the following:

  * Does the package in question define a non-empty ``__init__`` submodule
    defining a non-empty ``__all__`` list global? If so, the attributes listed
    by this global comprise that package's public API. Since ``__all__`` is
    defined only at runtime by a Turing-complete interpreter, however,
    deciding these attributes is itself a Turing-complete problem.
  * Else, all non-underscored attributes comprise that package's public API.
    Since these attributes are also defined only at runtime by a
    Turing-complete interpreter, deciding these attributes is again a
    Turing-complete problem -- albeit typically less so. (See above.)

* **Redundancy.** ``__all__`` violates the DRY (Don't Repeat Yourself)
  principle, thus inviting accidental desynchronization and omissions between
  the conventional and virtual public APIs for a package or module. This leads
  directly to...
* **Fragility.** By definition, accidentally excluding a public attribute from
  the conventional public API is infeasible; either an attribute is public by
  convention or it isn't. Conversely, accidentally omitting a public attribute
  from the virtual public API is a trivial and all-too-common mishap. Numerous
  stdlib packages and modules do so. This includes the pivotal :mod:`socket`
  module, whose implementation in the Python 3.6.x series accidentally excludes
  the public :func:`socket.socketpair` function from ``__all__`` if and only if
  the private :mod:`_socket` C extension also defines the same function -- a
  condition with no reasonable justification. Or *is* there? Dare mo shiranai.
* **Inconsistency.** Various modules and packages that declare ``__all__``
  randomly exclude public attributes for spurious and frankly indefensible
  reasons. This includes the stdlib :mod:`typing` module, whose preamble reads:

      The pseudo-submodules 're' and 'io' are part of the public
      namespace, but excluded from __all__ because they might stomp on
      legitimate imports of those modules.

  This is the worst of all possible worlds. A package or module either:

  * Leave ``__all__`` undefined (as most packages and modules do).
  * Prohibit ``__all__`` (as :mod:`beartype` does).
  * Define ``__all__`` in a self-consistent manner conforming to
    well-established semantics, conventions, and expectations.

* **Nonconsensus.** No consensus exists amongst either stdlib developers or the
  Python community as a whole as to the interpretation of ``__all__``.
  Third-party authors usually ignore ``__all__`` with respect to its role in
  declaring a virtual public API, instead treating ``__all__`` as a means of
  restricting star imports to some well-defined subset of public attributes.
  This includes SciPy, whose :attr:`scipy.__init__.__all__` list global
  excludes most public subpackages of interest (e.g., :mod:`scipy.linalg`, a
  subpackage of linear algebra routines) while paradoxically including some
  public subpackages of little to no interest (e.g., :attr:`scipy.test`, a unit
  test scaffold commonly run only by developers and maintainers).
* **Infeasibility.** We have established that no two packages or modules
  (including both stdlib and third-party) agree as to the usage of ``__all__``.
  Respecting the virtual public API would require authors to ignore public
  attributes omitted from ``__all__``, including those omitted by either
  accident or due to conflicting interpretations of ``__all__``. Since this is
  pragmatically infeasible *and* since upstream packages cannot reasonably
  prohibit downstream packages from importing public attributes either
  accidentally or intentionally excluded from ``__all__``, most authors
  justifiably ignore ``__all__``. (*So should you.*)
* **Insufficiency.** The ``__all__`` list global only applies to module-scoped
  attributes; there exists no comparable special attribute for classes with
  which to define a comparable "virtual public class API." Whereas the
  conventional public API uniformly applies to *all* attributes regardless of
  scoping, the virtual public API only applies to module-scoped attributes -- a
  narrower and less broadly applicable use case.
* **Unnecessity.** The conventional public API already exists. The virtual
  public API offers no tangible benefits over the conventional public API while0
  offering all the above harms. Under any rational assessment, the virtual
  public API can only be "considered harmful."

.. _semver:
    https://semver.org
'''
