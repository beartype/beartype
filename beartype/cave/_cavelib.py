#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype slow cave** (i.e., private subset of the public :mod:`beartype.cave`
subpackage profiled to *not* be efficiently importable at :mod:`beartype`
startup and thus *not* safely importable throughout the internal
:mod:`beartype` codebase).

This submodule currently imports from expensive third-party packages on
importation (e.g., :mod:`numpy`) despite :mod:`beartype` itself *never*
requiring those imports. Until resolved, that subpackage is considered tainted.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from argparse import (
    ArgumentParser,
    _SubParsersAction,
)
from beartype._cave._cavefast import (
    SequenceMutableType,
    SequenceType,
    StrType,
    UnavailableType,
    UnavailableTypes,
)
from typing import Tuple
from weakref import (
    ProxyTypes,
    ref,
)

# ....................{ TYPES ~ lib                       }....................
# Types conditionally dependent upon the importability of third-party
# dependencies. These types are subsequently redefined by try-except blocks
# below and initially default to "UnavailableType" for simple types.

# ....................{ TYPES ~ lib : numpy               }....................
# Conditionally redefined by the "TUPLES ~ init" subsection below.
_NumpyArrayType: type = UnavailableType
'''
Type of all **NumPy arrays** (i.e., instances of the concrete
:class:`numpy.ndarray` class implemented in low-level C and Fortran) if
:mod:`numpy` is importable *or* :class:`UnavailableType` otherwise (i.e., if
:mod:`numpy` is unimportable).
'''


# Conditionally redefined by the "TUPLES ~ init" subsection below.
_NumpyScalarType: type = UnavailableType
'''
Type of all **NumPy scalars** (i.e., instances of the abstract
:class:`numpy.generic` base class implemented in low-level C and Fortran) if
:mod:`numpy` is importable *or* :class:`UnavailableType` otherwise (i.e., if
:mod:`numpy` is unimportable).
'''

# ....................{ TYPES ~ stdlib : argparse         }....................
ArgParserType = ArgumentParser
'''
Type of argument parsers parsing all command-line arguments for either
top-level commands *or* subcommands of those commands.
'''


ArgSubparsersType = _SubParsersAction
'''
Type of argument subparser containers parsing subcommands for parent argument
parsers parsing either top-level commands *or* subcommands of those commands.
'''

# ....................{ TYPES ~ stdlib : weakref          }....................
WeakRefCType = ref
'''
Type of all **unproxied weak references** (i.e., callable objects yielding
strong references to their referred objects when called).

This type matches both the C-based :class:`weakref.ref` class *and* the
pure-Python :class:`weakref.WeakMethod` class, which subclasses the former.
'''
# ....................{ TUPLES ~ stdlib : weakref         }....................
WeakRefProxyCTypes = ProxyTypes
'''
Tuple of all **C-based weak reference proxy classes** (i.e., classes
implemented in low-level C whose instances are weak references to other
instances masquerading as those instances).

This tuple contains classes matching both callable and uncallable weak
reference proxies.
'''

# ....................{ TUPLES ~ version                  }....................
# Conditionally expanded by the "TUPLES ~ init" subsection below.
_VersionComparableTypes: Tuple[type, ...] = (tuple,)
'''
Tuple of all **comparable version types** (i.e., types suitable for use both as
parameters to callables accepting arbitrary version specifiers *and* as
operands to numeric operators comparing such specifiers) if
:mod:`pkg_resources` is importable *or* ``(tuple,)`` otherwise.

This is the proper subset of types listed by the :data:`_VersionTypes` tuple
that are directly comparable, thus excluding the :class:`str` type.
``.``-delimited version specifier strings are only indirectly comparable after
conversion to a comparable version type.

Caveats
----------
Note that all types listed by this tuple are *only* safely comparable with
versions of the same type. In particular, the types listed by the
:class:`_SetuptoolsVersionTypes` tuple do *not* necessarily support direct
comparison with either the :class:`tuple` *or* `class:`str` version types;
ironically, those types supported both under older but *not* newer versions of
:mod:`setuptools`. This is why we can't have good things.
'''

# ....................{ TUPLES ~ lib                      }....................
# Types conditionally dependent upon the importability of third-party
# dependencies. These types are subsequently redefined by try-except blocks
# below and initially default to "UnavailableTypes" for tuples of simple types.

# ....................{ TUPLES ~ lib : numpy              }....................
# Conditionally expanded by the "TUPLES ~ init" subsection below.
_SequenceOrNumpyArrayTypes: Tuple[type, ...] = (SequenceType,)
'''
Tuple of all **mutable** and **immutable sequence types** (i.e., both concrete
and structural subclasses of the abstract :class:`collections.abc.Sequence`
base class; reversible collections whose items are efficiently accessible but
*not* necessarily modifiable with 0-based integer-indexed lookup) as well as
the **NumPy array type** (i.e., :class:`numpy.ndarray`) if :mod:`numpy` is
importable.

The NumPy array type satisfies most but not all of the
:class:`collections.abc.Sequence` API and *must* thus be matched explicitly.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
:class:`SequenceType`
    Further details on the :class:`collections.abc.Sequence` mismatch.
'''


# Conditionally expanded by the "TUPLES ~ init" subsection below.
_SequenceMutableOrNumpyArrayTypes: Tuple[type, ...] = (SequenceMutableType,)
'''
Tuple of all **mutable sequence types** (i.e., both concrete and structural
subclasses of the abstract :class:`collections.abc.Sequence` base class;
reversible collections whose items are both efficiently accessible *and*
modifiable with 0-based integer-indexed lookup) as well as the the **NumPy
array type** (i.e., :class:`numpy.ndarray`) if :mod:`numpy` is importable.

The NumPy array type satisfies most but not all of the
:class:`collections.abc.MutableSequence` API and *must* thus be matched
explicitly.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
:class:`SequenceMutableType`
    Further details on the :class:`collections.abc.MutableSequence` mismatch.
'''

# ....................{ TUPLES ~ lib : setuptools         }....................
# Conditionally redefined by the "TUPLES ~ init" subsection below.
_SetuptoolsVersionTypes: Tuple[type, ...] = UnavailableTypes
'''
Tuple of all **:mod:`setuptools`-specific version types** (i.e., types
instantiated and returned by both the third-party
:func:`packaging.version.parse` *and* :func:`pkg_resources.parse_version`
functions bundled with :mod:`setuptools`) if :mod:`pkg_resources` is importable
*or* :data:`UnavailableTypes` otherwise (i.e., if :mod:`pkg_resources` is
unimportable).

This tuple matches these types if :mod:`pkg_resources` is importable:

* **Strict `PEP 440`_-compliant versions** (i.e., instances of the
  :class:`packaging.version.Version` or
  :class:`pkg_resources.packaging.version.Version` classes).
* **Less strict `PEP 440`_-noncompliant versions** (i.e., instances of the
  :class:`packaging.version.LegacyVersion` or
  :class:`pkg_resources.packaging.version.LegacyVersion` classes).

.. _PEP 440:
    https://www.python.org/dev/peps/pep-0440
'''

# ....................{ TUPLES ~ init                     }....................
# Conditionally define dependency-specific types.
#
# Since this submodule is often imported early in application startup, the
# importability of *ANY* dependency (mandatory or not) at the top level of this
# submodule remains undecided. Since subsequent logic in application startup is
# guaranteed to raise human-readable exceptions on missing mandatory
# dependencies, their absence here is ignorable.

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# If NumPy is importable...
try:
    import numpy as _numpy  # type: ignore

    # Define NumPy-specific types.
    _NumpyArrayType  = _numpy.ndarray
    _NumpyScalarType = _numpy.generic

    # Extend NumPy-agnostic types with NumPy-specific types.
    _SequenceOrNumpyArrayTypes        += (_NumpyArrayType,)
    _SequenceMutableOrNumpyArrayTypes += (_NumpyArrayType,)
# Else, NumPy is unimportable. We're done here, folks.
except:
    pass


# If setuptools is importable, conditionally define setuptools-specific types.
try:
    import pkg_resources as _pkg_resources  # type: ignore

    #FIXME: Now that "_pkg_resources.packaging.version.LegacyVersion" has been
    #deprecated, we need to refactor this up as follows:
    #* Define a new *PRIVATE* alias:
    #  _SetuptoolsVersionType = _pkg_resources.packaging.version.Version
    #  _VersionComparableTypes += (_SetuptoolsVersionType,)
    #  Exposing a "setuptools"-specific class was clearly a bad idea.
    #* Refactor "_SetuptoolsVersionTypes" to be deprecated by us, too. *shrug*

    # Define setuptools-specific types.
    _SetuptoolsVersionTypes = (_pkg_resources.packaging.version.Version,)  # type: ignore[attr-defined]
    _VersionComparableTypes += _SetuptoolsVersionTypes
# Else, setuptools is unimportable. While this should typically *NEVER* be the
# case, edge cases gonna edge case.
except:
    pass

# ....................{ TUPLES ~ post-init : version      }....................
_VersionTypes = (StrType,) + _VersionComparableTypes
'''
Tuple of all **version types** (i.e., types suitable for use as parameters to
callables accepting arbitrary version specifiers) if :mod:`pkg_resources` is
importable *or* ``(StrType, tuple,)`` otherwise.

This includes:

* :class:`StrType`, specifying versions in ``.``-delimited positive integer
  format (e.g., ``2.4.14.2.1.356.23``).
* :class:`tuple`, specifying versions as one or more positive integers (e.g.,
  ``(2, 4, 14, 2, 1, 356, 23)``),
* :class:`_SetuptoolsVersionTypes`, whose :mod:`setuptools`-specific types
  specify versions as instance variables convertible into both of the prior
  formats (e.g., ``_SetuptoolsVersionTypes[0]('2.4.14.2.1.356.23')``).
'''
