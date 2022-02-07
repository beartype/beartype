#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype cave.**

This submodule collects common types (e.g., :class:`NoneType`, the type of the
``None`` singleton) and tuples of common types (e.g., :data:`CallableTypes`, a
tuple of the types of all callable objects).

PEP 484
----------
This module is intentionally *not* compliant with the :pep:`484` standard
implemented by the stdlib :mod:`typing` module, which formalizes type hinting
annotations with a catalogue of generic classes and metaclasses applicable to
common use cases. :mod:`typing` enables end users to enforce contractual
guarantees over the contents of arbitrarily complex data structures with the
assistance of third-party static type checkers (e.g., :mod:`mypy`,
:mod:`pyre`), runtime type checkers (e.g., :mod:`beartype`, :mod:`typeguard`),
and integrated development environments (e.g., PyCharm).

Genericity comes at a cost, though. Deeply type checking a container containing
``n`` items, for example, requires type checking both that container itself
non-recursively *and* each item in that container recursively. Doing so has
time complexity ``O(N)`` for ``N >= n`` the total number of items transitively
contained in this container (i.e., items directly contained in this container
*and* items directly contained in containers contained in this container).
While the cost of this operation can be paid either statically *or* amortized
at runtime over all calls to annotated callables accepting that container, the
underlying cost itself remains the same.

By compare, this module only contains standard Python classes and tuples of
such classes intended to be passed as is to the C-based :func:`isinstance`
builtin and APIs expressed in terms of that builtin (e.g., :mod:`beartype`).
This module only enables end users to enforce contractual guarantees over the
types but *not* contents of arbitrarily complex data structures. This
intentional tradeoff maximizes runtime performance at a cost of ignoring the
types of items contained in containers.

In summary:

=====================  ====================  ====================================
feature set            :mod:`beartype.cave`  :mod:`typing`
=====================  ====================  ====================================
type checking          **shallow**           **deep**
type check items?      **no**                **yes**
:pep:`484`-compliant?  **no**                **yes**
time complexity        ``O(1)``              ``O(N)``
performance            stupid fast           *much* less stupid fast
implementation         C-based builtin call  pure-Python (meta)class method calls
low-level primitive    :func:`isinstance`    :mod:`typing.TypingMeta`
=====================  ====================  ====================================
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: *NEVER IMPORT FROM THIS SUBPACKAGE FROM WITHIN BEARTYPE ITSELF.*
# This subpackage currently imports from expensive third-party packages on
# importation (e.g., NumPy) despite beartype itself *NEVER* requiring those
# imports. Until resolved, this subpackage is considered tainted.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To prevent "mypy --no-implicit-reexport" from raising literally
# hundreds of errors at static analysis time, *ALL* public attributes *MUST* be
# explicitly reimported under the same names with "{exception_name} as
# {exception_name}" syntax rather than merely "{exception_name}". Yes, this is
# ludicrous. Yes, this is mypy. For posterity, these failures resemble:
#     beartype/_cave/_cavefast.py:47: error: Module "beartype.roar" does not
#     explicitly export attribute "BeartypeCallUnavailableTypeException";
#     implicit reexport disabled  [attr-defined]
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from beartype.cave._cavelib import (
    # Types.
    ArgParserType as ArgParserType,
    ArgSubparsersType as ArgSubparsersType,
    WeakRefCType as WeakRefCType,

    # Type tuples.
    WeakRefProxyCTypes as WeakRefProxyCTypes,

    # Deprecated types and type tuples.
    _NumpyArrayType,
    _NumpyScalarType,
    _SequenceMutableOrNumpyArrayTypes,
    _SequenceOrNumpyArrayTypes,
    _SetuptoolsVersionTypes,
    _VersionComparableTypes,
    _VersionTypes,
)
from beartype._cave._caveabc import (
    BoolType as BoolType,
)
from beartype._cave._cavefast import (
    # Types.
    AnyType as AnyType,
    AsyncCoroutineCType as AsyncCoroutineCType,
    AsyncGeneratorCType as AsyncGeneratorCType,
    CallableCodeObjectType as CallableCodeObjectType,
    CallablePartialType as CallablePartialType,
    ClassType as ClassType,
    CollectionType as CollectionType,
    ContainerType as ContainerType,
    EllipsisType as EllipsisType,
    EnumType as EnumType,
    EnumMemberType as EnumMemberType,
    FileType as FileType,
    FunctionType as FunctionType,
    FunctionOrMethodCType as FunctionOrMethodCType,
    GeneratorCType as GeneratorCType,
    GeneratorType as GeneratorType,
    HashableType as HashableType,
    HintGenericSubscriptedType as HintGenericSubscriptedType,
    IntOrFloatType as IntOrFloatType,
    IntType as IntType,
    IterableType as IterableType,
    IteratorType as IteratorType,
    MappingMutableType as MappingMutableType,
    MappingType as MappingType,
    MethodBoundInstanceDunderCType as MethodBoundInstanceDunderCType,
    MethodBoundInstanceOrClassType as MethodBoundInstanceOrClassType,
    MethodDecoratorClassType as MethodDecoratorClassType,
    MethodDecoratorPropertyType as MethodDecoratorPropertyType,
    MethodDecoratorStaticType as MethodDecoratorStaticType,
    MethodUnboundClassCType as MethodUnboundClassCType,
    MethodUnboundInstanceDunderCType as MethodUnboundInstanceDunderCType,
    MethodUnboundInstanceNondunderCType as MethodUnboundInstanceNondunderCType,
    ModuleType as ModuleType,
    NoneType as NoneType,
    NotImplementedType as NotImplementedType,
    NumberRealType as NumberRealType,
    NumberType as NumberType,
    SizedType as SizedType,
    QueueType as QueueType,
    RegexCompiledType as RegexCompiledType,
    RegexMatchType as RegexMatchType,
    SetType as SetType,
    SequenceMutableType as SequenceMutableType,
    SequenceType as SequenceType,
    StrType as StrType,
    UnavailableType as UnavailableType,

    # Type tuples.
    AsyncCTypes as AsyncCTypes,
    BoolOrNumberTypes as BoolOrNumberTypes,
    CallableCTypes as CallableCTypes,
    CallableOrClassTypes as CallableOrClassTypes,
    CallableOrStrTypes as CallableOrStrTypes,
    CallableTypes as CallableTypes,
    DecoratorTypes as DecoratorTypes,
    FunctionTypes as FunctionTypes,
    ModuleOrStrTypes as ModuleOrStrTypes,
    MethodBoundTypes as MethodBoundTypes,
    MethodDecoratorBuiltinTypes as MethodDecoratorBuiltinTypes,
    MethodUnboundTypes as MethodUnboundTypes,
    MethodTypes as MethodTypes,
    MappingOrSequenceTypes as MappingOrSequenceTypes,
    ModuleOrSequenceTypes as ModuleOrSequenceTypes,
    NumberOrIterableTypes as NumberOrIterableTypes,
    NumberOrSequenceTypes as NumberOrSequenceTypes,
    RegexTypes as RegexTypes,
    ScalarTypes as ScalarTypes,
    TestableTypes as TestableTypes,
    UnavailableTypes as UnavailableTypes,
)
from beartype._cave._cavemap import (
    NoneTypeOr as NoneTypeOr,
)

# ....................{ DEPRECATIONS                      }....................
def __getattr__(attr_deprecated_name: str) -> object:
    '''
    Dynamically retrieve a deprecated attribute with the passed unqualified
    name from this submodule and emit a non-fatal deprecation warning on each
    such retrieval if this submodule defines this attribute *or* raise an
    exception otherwise.

    The Python interpreter implicitly calls this :pep:`562`-compliant module
    dunder function under Python >= 3.7 *after* failing to directly retrieve an
    explicit attribute with this name from this submodule.

    Parameters
    ----------
    attr_deprecated_name : str
        Unqualified name of the deprecated attribute to be retrieved.

    Returns
    ----------
    object
        Value of this deprecated attribute.

    Warns
    ----------
    :class:`DeprecationWarning`
        If this attribute is deprecated.

    Raises
    ----------
    :exc:`AttributeError`
        If this attribute is unrecognized and thus erroneous.
    '''

    # Isolate imports to avoid polluting the module namespace.
    from beartype._util.mod.utilmoddeprecate import deprecate_module_attr

    # Return the value of this deprecated attribute and emit a warning.
    return deprecate_module_attr(
        attr_deprecated_name=attr_deprecated_name,
        attr_deprecated_name_to_nondeprecated_name={
            'HintPep585Type': 'HintGenericSubscriptedType',
            'NumpyArrayType': '_NumpyArrayType',
            'NumpyScalarType': '_NumpyScalarType',
            'SequenceOrNumpyArrayTypes': '_SequenceOrNumpyArrayTypes',
            'SequenceMutableOrNumpyArrayTypes': (
                '_SequenceMutableOrNumpyArrayTypes'),
            'SetuptoolsVersionTypes': '_SetuptoolsVersionTypes',
            'VersionComparableTypes': '_VersionComparableTypes',
            'VersionTypes': '_VersionTypes',
        },
        attr_nondeprecated_name_to_value=globals(),
    )

# ....................{ DUNDERS                           }....................
# Intentionally defined last, as nobody wants to stumble into a full-bore rant
# first thing in the morning.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']
'''
Special list global referencing a single attribute guaranteed *not* to exist.

The definition of this global effectively prohibits star imports from this
submodule into downstream modules by raising an :class:`AttributeError`
exception on the first attempt to do so: e.g.,

.. code-block:: shell-session

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
