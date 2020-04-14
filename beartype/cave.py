#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

# ....................{ METADATA                          }....................
'''
**Beartype cave.**

This submodule collects common types (e.g., :class:`NoneType`, the type of the
``None`` singleton) and tuples of common types (e.g., :data:`CallableTypes`, a
tuple of the types of all callable objects).

PEP 484
----------
This module is intentionally *not* compliant with the `PEP 484`_ standard
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
`PEP 484`_-compliant?  **no**                **yes**
time complexity        ``O(1)``              ``O(N)``
performance            stupid fast           *much* less stupid fast
implementation         C-based builtin call  pure-Python (meta)class method calls
low-level primitive    :func:`isinstance`    :mod:`typing.TypingMeta`
=====================  ====================  ====================================

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

#FIXME: Define a new "TypingType" or "Pep484Type" type rooted at either the
#"typing.TypingMeta" metaclass or "typing._TypingBase" superclass. Obviously,
#we currently have no means of type-checking metaclasses... but the latter is
#explicitly private. Ergo, all roads lead to Hell.
#FIXME: Use this new type in the @beartype decorator to raise exceptions when
#passed such a type, which we currently do *NOT* support. This is critical, as
#users *MUST* be explicitly informed of this deficiency.

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely ""from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#FIXME: To avoid polluting the module namespace, we want to either isolate
#these importations to a private callable *OR* delete them at the very end of
#this module. As the latter approach is both more fragile and inefficient, the
#former approach seems substantially more intelligent.
#FIXME: Actually, just import everything needed under "_"-prefixed names (e.g.,
#"from argparse import ArgumentParser as _ArgumentParser"). Problem solved! :p

import functools, pkg_resources, re
from argparse import _SubParsersAction
from argparse import ArgumentParser as _ArgumentParser
from collections import deque as _deque
from collections.abc import (
    Container,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Sequence,
    Set,
    Sized,
)
from enum import Enum, EnumMeta
from io import IOBase
from pkg_resources import Distribution
from weakref import ref, CallableProxyType, ProxyType, WeakMethod

# Import the following types as is into the namespace of this submodule,
# permitting callers to reference these types conveniently. Since the
# nomenclature of these types is already consistent with that used by types
# declared below (namely, both CamelCase and suffixed by "Type"), these types
# are used as is rather than aliased to synonymous types below.
#
# Note that the "LambdaType" is intentionally *NOT* imported. Why? Because that
# type is exactly synonymous with "FunctionType", implying lambdas are
# indistinguishable from functions. To curtail confusion elsewhere and, in
# particular, to prevent functions from being misidentified as lambdas, all
# lambdas are currently misidentified as functions. This is the lesser of
# multiple evils, we're afraid.
from types import (
    BuiltinFunctionType,
    BuiltinMethodType,
    FunctionType,
    GeneratorType,  # "GeneratorType" is imported from this submodule as is.
    MethodType,
    ModuleType,
)

# ....................{ TYPES                             }....................
ClassType = type
'''
Type of all types.
'''


FileType = IOBase
'''
Abstract base class implemented by *all* **file-like objects** (i.e., objects
implementing the standard ``read()`` and ``write()`` methods).

This class is a synonym of the `io.IOBase` class, provided merely as a
convenience to callers preferring to avoid importing that class.
'''


NoneType = type(None)
'''
Type of the ``None`` singleton.

Curiously, although the type of the ``None`` object is a class object whose
``__name__`` attribute is ``NoneType``, there exists no globally accessible
class by that name. To circumvents this obvious oversight, this global globally
exposes this class.

This class is principally useful for annotating both:

* Callable parameters accepting ``None`` as a valid value.
* Callables returning ``None`` as a valid value.

Note that, for obscure and uninteresting reasons, the standard :mod:`types`
module defined the same type with the same name under Python 2.x but _not_ 3.x.
Depressingly, this type must now be manually redefined everywhere.
'''

# ....................{ TYPES ~ arg                       }....................
ArgParserType = _ArgumentParser
'''
Type of argument parsers parsing all command-line arguments for either
top-level commands *or* subcommands of those commands.

This class is a synonym of the :class:`argparse.ArgumentParser` class,
permitting callers to avoid importing that class.
'''


ArgSubparsersType = _SubParsersAction
'''
Type of argument subparser containers parsing subcommands for parent argument
parsers parsing either top-level commands *or* subcommands of those commands.

This class is a synonym of the :class:`argparse._SubParsersAction` class,
permitting callers to avoid importing that private class.
'''

# ....................{ TYPES ~ callable                  }....................
CallablePartialType = functools.partial
'''
Type of all **partial callables** (i.e., callables dynamically produced by the
function-like :class:`functools.partial` class).
'''


ClassMethodType = classmethod
'''
Type of all **class methods** (i.e., methods bound to a class rather than an
instance of a class and implicitly passed that class as their first parameter).
'''


# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.MethodDescriptorType" object, this is of no benefit to older
# versions of Python. Ergo, the type of an arbitrary method descriptor
# guaranteed to *ALWAYS* exist is obtained instead.
MethodDescriptorType = type(str.upper)
'''
Type of all **method descriptors** (i.e., unbound functions accessed as class
rather than instance attributes).

Note that, despite being unbound, method descriptors remain callable (e.g., by
explicitly passing the intended ``self`` object as the first parameter).
'''


# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.MethodWrapperType" object, this is of no benefit to older
# versions of Python. Ergo, the type of an arbitrary method wrapper guaranteed
# to *ALWAYS* exist is obtained instead.
MethodWrapperType = type(''.__add__)
'''
Type of all **method wrappers** (i.e., bound special methods of a small subset
of builtin types).
'''


PropertyType = property
'''
Type of all **property methods** (i.e., methods decorated by the builtin
:class:`property` class decorator).
'''


# Since Python appears to expose no explicit slot wrapper type via any standard
# module (e.g., "types", "collections.abc"), the type of an arbitrary slot
# wrapper guaranteed to *ALWAYS* exist is obtained instead.
SlotWrapperType = type(str.__len__)
'''
Type of all **slot wrappers** (i.e., C-based unbound methods accessed as class
rather than instance attributes).

Note that, despite being unbound, slot wrappers remain callable (e.g., by
explicitly passing the intended ``self`` object as the first parameter).
'''


StaticMethodType = staticmethod
'''
Type of all **static methods** (i.e., methods bound to a class rather than an
instance of a class but *not* implicitly passed that class as their first
parameter, unlike class methods).
'''

# ....................{ TYPES ~ callable : weakref        }....................
WeakRefStandardType = ref
'''
Type of all **unproxied general-purpose weak references** (i.e., callable
objects yielding a strong reference to their referred object when called).
'''


WeakRefBoundMethodType = WeakMethod
'''
Type of all **unproxied bound method weak references** (i.e., callable
objects yielding a strong reference to their referred bound method when
called).
'''

# ....................{ TYPES ~ container                 }....................
IteratorType = Iterator
'''
Abstract interface implemented by all **iterators** (i.e., objects implementing
the standard ``__iter__()`` and ``__next__()`` methods, typically iterating
over an associated container).

This class is a synonym of the `collections.abc.Iterator` class, provided
merely as a convenience to callers preferring to avoid importing that class.
'''


QueueType = _deque
'''
Concrete type of the only available queue implementation in Python's stdlib.

This class is a synonym of the :class:`collections.deque` class, provided
merely as a convenience to callers preferring to avoid importing that class.

Caveats
----------
Since the :class:`collections.abc` subpackage currently provides no
corresponding abstract interface to formalize queue types, this type applies
*only* to the standard double-ended queue implementation.
'''


SetType = Set
'''
Abstract interface implemented by all **set-like containers** (i.e., containers
guaranteeing uniqueness across all items in these containers), including both
the standard :class:`set` and :class:`frozenset` types *and* the types of the
:class:`dict`-specific views returned by the :meth:`dict.items` and
:meth:`dict.keys` (but *not* :meth:`dict.values`) methods.

This class is a synonym of the :class:`collections.abc.Set` class, provided
merely as a convenience to callers preferring to avoid importing that class.
'''


SizedType = Sized
'''
Abstract interface implemented by all containers defining the special
``__len__()`` method internally called by the :func:`len` builtin.

This class is a synonym of the `collections.abc.Sized` class, provided merely
as a convenience to callers preferring to avoid importing that class.
'''

# ....................{ TYPES ~ container : mapping       }....................
HashableType = Hashable
'''
Abstract interface implemented by all **hashables** (i.e., objects implementing
the standard ``__hash__()`` method required by all dictionary keys).

This class is a synonym of the `collections.abc.Hashable` class, provided
merely as a convenience to callers preferring to avoid importing that class.
'''


MappingType = Mapping
'''
Abstract interface implemented by all dictionary-like objects, both mutable and
immutable.

This class is a synonym of the `collections.abc.Mapping` class, provided merely
as a convenience to callers preferring to avoid importing that class.
'''


MappingMutableType = MutableMapping
'''
Abstract interface implemented by all mutable dictionary-like objects.

This class is a synonym of the `collections.abc.MutableMapping` class, provided
merely as a convenience to callers preferring to avoid importing that class.
'''

# ....................{ TYPES ~ enum                      }....................
# Enumeration types sufficiently obscure to warrant formalization here.

EnumType = EnumMeta
'''
Metaclass of all **enumeration types** (i.e., classes containing all
enumeration members comprising those enumerations).

This class is a synonym of the :class:`enum.EnumMeta` class, permitting callers
to avoid importing that class.

Motivation
----------
This type is widely used throughout the codebase to validate callable
parameters to be enumerations. In recognition of its popularity, this type is
intentionally named ``EnumType`` rather than ``EnumMetaType``. While the latter
*would* technically be less ambiguous, the former has the advantage of inviting
correctness throughout the codebase -- a less abundant resource.

Why? Because *all* enumeration types are instances of this type rather than the
:class:`Enum` class despite being superficially defined as instances of the
:class:`Enum` class. Thanks to metaclass abuse, enumeration types do *not*
adhere to standard Pythonic semantics. Notably, the following non-standard
invariants hold across *all* enumerations:

    >>> from betse.util.type.types import (
    ...     EnumType, EnumClassType, EnumMemberType, ClassType)
    >>> enum_type = EnumClassType(
    ...     'Gyre', ('The', 'falcon', 'cannot', 'hear', 'the', 'falconer'))
    >>> isinstance(enum_type, EnumType)
    True
    >>> isinstance(enum_type, EnumClassType)
    False
    >>> isinstance(enum_type, ClassType)
    True
    >>> isinstance(enum_type.falcon, EnumType)
    False
    >>> isinstance(enum_type.falcon, EnumMemberType)
    True
    >>> isinstance(enum_type.falcon, ClassType)
    False
'''


EnumClassType = Enum
'''
Abstract base class of all **enumeration types** (i.e., classes containing all
enumeration members comprising those enumerations).

This class is a synonym of the :class:`enum.Enum` class, permitting callers to
avoid importing that class.

See Also
----------
:class:`EnumType`
    Further details.
'''


EnumMemberType = Enum
'''
Abstract base class implemented by all **enumeration members** (i.e.,
alternative choices comprising their parent enumerations).

This class is a synonym of the :class:`enum.Enum` class, permitting callers
to avoid importing that class.

Caveats
----------
When type checking callable parameters, this class should *only* be referenced
where the callable permissively accepts any enumeration member type rather than
a specific enumeration member type. In the latter case, that type is simply
that enumeration's type and should be directly referenced as such: e.g.,

    >>> from betse.util.type.enums import make_enum
    >>> from betse.util.type.types import type_check
    >>> EndymionType = make_enum(
    ...     class_name='EndymionType', member_names=('BEAUTY', 'JOY',))
    >>> @type_check
    ... def our_feet_were_soft_in_flowers(superlative: EndymionType) -> str:
    ...     return str(superlative).lower()
'''

# ....................{ TUPLES                            }....................
ModuleOrStrTypes = (str, ModuleType)
'''
Tuple of both the module *and* string type.
'''


CheckableMemberTypes = (ClassType, str)
'''
Tuple of all **checkable member types** (i.e., types suitable for use as the
members of function annotations type-checked via the :func:`type_check`
decorator).
'''


TestableTypes = (ClassType, tuple)
'''
Tuple of all **testable types** (i.e., types suitable for use as the second
parameter passed to the :func:`isinstance` and :func:`issubclass` builtins).
'''

# ....................{ TUPLES ~ callable                 }....................
BoundMethodTypes = (MethodType, ClassMethodType, StaticMethodType)
'''
Tuple of all **bound method classes** (i.e., classes whose instances are
callable objects bound to either a class or instance of a class).
'''


CallableTypes = (
    BuiltinFunctionType,
    BuiltinMethodType,
    FunctionType,
    MethodType,
    MethodDescriptorType,
    MethodWrapperType,
    SlotWrapperType,
)
'''
Tuple of all **callable classes** (i.e., classes whose instances are callable
objects, including both built-in and user-defined functions, lambdas, methods,
and method descriptors).
'''


CallableOrStrTypes = CallableTypes + (str,)
'''
Tuple of all callable classes *and* the string type.
'''


ClassBoundMethodTypes = (ClassMethodType, StaticMethodType)
'''
Tuple of all **class-bound method classes** (i.e., classes whose instances are
callable objects bound to a class rather than instance of a class).
'''


DecoratorTypes = CallableTypes + (ClassType,)
'''
Tuple of all **decorator types** (i.e., both callable classes *and* the type of
those classes).

Motivation
----------
Since classes themselves may be callable (e.g., by defining the special
``__call__`` method), this tuple is the set of all possible callable types. In
particular, this tuple describes all types permissible for use as decorators.

Since most classes are *not* callable, however, this tuple may yield false
positives when used to validate types. Caveat emptor.
'''


FunctionTypes = (BuiltinFunctionType, FunctionType,)
'''
Tuple of all **function classes** (i.e., classes whose instances are either
built-in or user-defined functions).
'''


MethodTypes = (BuiltinMethodType, MethodType,)
'''
Tuple of all **method classes** (i.e., classes whose instances are either
built-in or user-defined methods).
'''

# ....................{ TUPLES ~ container                }....................
# Note that most tuples of container base classes are defined in the "lib"
# subsection below, due to conditionally containing classes from third-party
# dependencies. Tuples defined here only contain classes from Python's stdlib.

SequenceStandardTypes = (list, tuple)
'''
Tuple of all **standard container base classes** (i.e., classes defined by
Python's stdlib and hence guaranteed to exist) both conforming to *and*
subclassing the canonical :class:`collections.abc.Sequence` API.

See Also
----------
:class:`SequenceTypes`
    Further details.
'''

# ....................{ TUPLES ~ version                  }....................
VersionSetuptoolsTypes = (
    # PEP 440-compliant version type.
    pkg_resources.packaging.version.Version,
    # PEP 440-uncompliant version type.
    pkg_resources.packaging.version.LegacyVersion,
)
'''
Tuple of all :mod:`setuptools`-specific version types (i.e., types instantiated
and returned by the stable :func:`pkg_resources.parse_version` function bundled
with :mod:`setuptools`).
'''


VersionComparableTypes = (tuple,) + VersionSetuptoolsTypes
'''
Tuple of all **comparable version types** (i.e., types suitable for use both as
parameters to callables accepting arbitrary version specifiers *and* as
operands to numeric operators comparing such specifiers).

This is the proper subset of types listed by the :data:`VersionTypes` tuple
that are directly comparable, thus excluding the :class:`str` type.
``.``-delimited version specifier strings are only indirectly comparable after
conversion to a comparable version type (e.g., by calling the
:func:`betse.util.type.numeric.version.to_comparable` function).

Caveats
----------
Note that all types listed by this tuple are *only* safely comparable with
versions of the same type. In particular, the :class:`VersionSetuptoolsTypes`
type does *not* necessarily support direct comparison with either the
:class:`tuple` *or* `class:`str` version types; tragically, this type supported
both under older but *not* newer versions of :mod:`setuptools`. *shakes fist*
'''


VersionTypes = (str,) + VersionComparableTypes
'''
Tuple of all **version types** (i.e., types suitable for use as parameters to
callables accepting arbitrary version specifiers, notably those implemented
by the :mod:`betse.util.type.numeric.version` submodule).

This includes:

* :class:`str`, specifying versions in ``.``-delimited positive integer format
  (e.g., ``2.4.14.2.1.356.23``).
* :class:`tuple`, specifying versions as one or more positive integers (e.g.,
  ``(2, 4, 14, 2, 1, 356, 23)``),
* :class:`VersionSetuptoolsTypes`, specifying versions as instance variables
  convertible into both of the prior formats (e.g.,
  ``VersionSetuptoolsTypes('2.4.14.2.1.356.23')``).
'''

# ....................{ TUPLES ~ weakref                  }....................
WeakRefProxyTypes = (CallableProxyType, ProxyType)
'''
Tuple of all **weak reference proxy classes** (i.e., classes whose instances
are weak references to other instances masquerading as those instances).

This tuple contains classes matching both callable and uncallable weak
reference proxies.
'''


WeakRefTypes = (WeakRefStandardType, WeakRefBoundMethodType)
'''
Tuple of all **unproxied weak reference classes** (i.e., classes whose
instances are weak references to other instances *not* masquerading as those
instances).

This tuple contains classes matching unproxied weak references of both standard
objects *and* bound methods, which require specific handling.
'''

# ....................{ TUPLES ~ scalar                   }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Order is significant here. See commentary in the docstring below.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

NumericSimpleTypes = (float, int,)
'''
Tuple of all **builtin simple numeric types** (i.e., classes whose instances
are trivial scalar numbers), comprising both integer and real number types.

This tuple intentionally excludes complex number types - whose non-trivial
encapsulation of a pair of real numbers *usually* necessitates non-trivial
special handling.

Caveats
----------
Note that this tuple intentionally lists the :class:`float` type *before* the
:class:`int` type. Why/ Downstream consumers (e.g., BETSEE) coerce GUI-based
numeric string values into numbers by casting these strings into instances of
the first item of this tuple. Reversing the order of these items in this tuple
would adversely strip the decimal portion from real number strings. In simpler
words: "Just 'cause."
'''


NumericTypes = (complex,) + NumericSimpleTypes
'''
Tuple of all **builtin numeric types** (i.e., classes whose instances are
scalar numbers), comprising integer, real number, and complex number types.
'''


NumericlikeTypes = (bool,) + NumericTypes
'''
Tuple of all **builtin numeric-like types** (i.e., classes whose instances are
either scalar numbers or types trivially convertable into scalar numbers),
comprising boolean, integer, real number, and complex number types.

Booleans are trivially convertible into integers. While details differ by
implementation, the "standard" implementation trivially converts:

* ``False`` to ``0``.
* ``True`` to ``1``.
'''


ScalarTypes = (str,) + NumericlikeTypes
'''
Tuple of all **builtin scalar types** (i.e., classes whose instances are
single scalar primitives), comprising all boolean, numeric, and textual types.
'''

# ....................{ TUPLES : lib                      }....................
# Types conditionally dependent upon the importability of third-party
# dependencies. For safety, all such types default to ``None`` here and are
# subsequently redefined by the try-except block below.

BoolTypes = None
'''
Tuple of all strictly boolean types, including both the standard :class:`bool`
builtin *and* the non-standard NumPy-specific boolean type (when NumPy is
importable in the active Python interpreter).

Caveats
----------
Non-standard boolean types are typically *not* interoperable with the standard
standard :class:`bool` type. In particular, it is typically *not* the case, for
any variable ``my_bool`` of non-standard boolean type and truthy value,
that either ``my_bool is True`` or ``my_bool == True`` yield the desired
results. Rather, such variables should *always* be coerced into the standard
:class:`bool` type before being compared -- either:

* Implicitly (e.g., ``if my_bool: pass``).
* Explicitly (e.g., ``if bool(my_bool): pass``).

See Also
----------
:class:`SequenceTypes`
    Further details.
'''


ContainerTypes = None
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`collections.abc.Container` API and hence
defining the special ``__contains__()`` method internally called by the ``in``
operator.

See Also
----------
:class:`SequenceTypes`
    Further details.
'''


IterableTypes = None
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`collections.abc.Iterable` API.

See Also
----------
:class:`SequenceTypes`
    Further details.
'''


SequenceTypes = None
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`collections.abc.Sequence` API.

Sequences are iterables supporting efficient element access via integer
indices.  Most sequences implement the :class:`collections.abc.Sequence`
abstract base class, including the concrete :class:`str` string class. All
sequences define the special ``__getitem__()`` and ``__len__()`` methods,
amongst numerous others.

While all sequences are iterables, not all iterables are sequences. Generally
speaking, sequences correspond to the proper subset of iterables whose elements
are ordered. :class:`dict` and :class:`OrderedDict` are the canonical examples.
:class:`dict` implements :class:`collections.abc.Iterable` but *not*
:class:`collections.abc.Sequence`, due to failing to support integer
index-based lookup; :class:`OrderedDict` implements both, due to supporting
such lookup.

For generality, this tuple contains classes matching both pure-Python sequences
*and* non-Pythonic Fortran-based Numpy arrays and matrices -- which fail to
subclass :class:`collections.abc.Sequence` despite implementing the entirety of
that that API.
'''

# ....................{ TUPLES : lib ~ matplotlib         }....................
MatplotlibFigureType = None
'''
Type of :mod:`matplotlib` figures if :mod:`matplotlib` is importable *or*
``None`` otherwise.

This class is a synonym of the :class:`matplotlib.figure.Figure` class,
permitting callers to avoid importing that class.
'''

# ....................{ TUPLES : lib ~ numpy              }....................
NumpyArrayType = None
'''
Type of all Numpy arrays if :mod:`numpy` is importable *or* ``None`` otherwise.

This class is a synonym of the :class:`numpy.ndarray` class, permitting callers
to avoid importing that class.
'''


NumpyScalarType = None
'''
Superclass of all Numpy scalar subclasses (e.g., :class:`numpy.bool_`) if
:mod:`numpy` is importable *or* ``None`` otherwise.

This class is a synonym of the :class:`numpy.generic` class, permitting callers
to avoid importing that class.
'''


NumpyDataTypes = ()
'''
Tuple of the **Numpy data type** (i.e., Numpy-specific numeric scalar type
homogenously constraining all elements of all Numpy arrays) and all scalar
Python types transparently supported by Numpy as implicit data types (i.e.,
:class:`bool`, :class:`complex`, :class:`float`, and :class:`int`) if
:mod:`numpy` is importable *or* ``None`` otherwise.

This class is a synonym of the :class:`numpy.dtype` class, permitting callers
to avoid importing that class.
'''

# ....................{ TUPLES : init                     }....................
# Conditionally define dependency-specific types.
#
# Since this submodule is often imported early in application startup, the
# importability of *ANY* dependency (mandatory or not) at the top level of this
# submodule remains undecided. Since subsequent logic in application startup is
# guaranteed to raise human-readable exceptions on missing mandatory
# dependencies, their absence here is ignorable.

# If matplotlib is importable, conditionally define matplotlib-specific types.
try:
    from matplotlib.figure import Figure
    MatplotlibFigureType = Figure
except:
    pass

# If NumPy is importable, conditionally define NumPy-specific types.
try:
    import numpy

    BoolTypes = (bool, numpy.bool_)
    NumpyArrayType = numpy.ndarray
    NumpyScalarType = numpy.generic
    NumpyDataTypes = (numpy.dtype,) + NumericlikeTypes
    ContainerTypes = (Container, NumpyArrayType)
    IterableTypes = (Iterable, NumpyArrayType)
    SequenceTypes = (Sequence, NumpyArrayType)

    # Delete all of the Numpy-specific imports imported above to avoid
    # polluting the namespace of this module with these irrelevant names.
    del numpy
# Else, Numpy is unimportable. Define these tuples to contain only stock types.
except:
    BoolTypes = (bool,)
    ContainerTypes = (Container,)
    IterableTypes = (Iterable,)
    SequenceTypes = (Sequence,)

# ....................{ TUPLES : post-init                }....................
# Tuples of types assuming the above initialization to have been performed.

MappingOrSequenceTypes = (MappingType,) + SequenceTypes
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`Mapping` *or* :class:`Sequence` APIs.
'''


ModuleOrSequenceTypes = (ModuleType,) + SequenceTypes
'''
Tuple of the module type *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`Sequence` API.
'''


NumericOrIterableTypes = NumericSimpleTypes + IterableTypes
'''
Tuple of all numeric types *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`Iterable` API.
'''


NumericOrSequenceTypes = NumericSimpleTypes + SequenceTypes
'''
Tuple of all numeric types *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`Sequence` API.
'''

# ....................{ TUPLES : none                     }....................
# Tuples of types containing at least the type of the singleton "None" object.

NoneTypes = (NoneType,)
'''
Tuple of only the type of the ``None`` singleton.

This tuple is principally intended for use in efficiently constructing other
tuples of types containing this type.
'''


BoolOrNoneTypes = (bool, NoneType)
'''
Tuple of both the boolean type *and* that of the ``None`` singleton.
'''


CallableOrNoneTypes = CallableTypes + NoneTypes
'''
Tuple of all callable classes *and* the type of the ``None`` singleton.
'''


ClassOrNoneTypes = (ClassType, NoneType)
'''
Tuple of the type of all types *and* that of the ``None`` singleton.
'''


DistributionOrNoneTypes = (Distribution, NoneType)
'''
Tuple of the type of all :mod:`setuptools`-specific package metadata objects
*and* that of the ``None`` singleton.
'''


IntOrNoneTypes = (int, NoneType)
'''
Tuple of both the integer type *and* that of the ``None`` singleton.
'''


IterableOrNoneTypes = IterableTypes + NoneTypes
'''
Tuple of all container base classes conforming to (but _not_ necessarily
subclassing) the canonical :class:`Iterable` API as well as the type of the
``None`` singleton.
'''


MappingOrNoneTypes = (MappingType,) + NoneTypes
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`Mapping` API as well as the type of the
``None`` singleton.
'''


MappingOrSequenceOrNoneTypes = MappingOrSequenceTypes + NoneTypes
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`Mapping` *or* :class:`Sequence` APIs as well
as the type of the ``None`` singleton.
'''


NumericOrNoneTypes = NumericSimpleTypes + NoneTypes
'''
Tuple of all numeric types *and* the type of the singleton `None` object.
'''


NumericOrSequenceOrNoneTypes = NumericOrSequenceTypes + NoneTypes
'''
Tuple of all numeric types, all container base classes conforming to (but *not*
necessarily subclassing) the canonical :class:`int`, :class:`float`, *or*
:class:`Sequence` APIs as well as the type of the singletone ``None`` object.
'''


NumpyDataOrNoneTypes = NumpyDataTypes + NoneTypes
'''
Tuple of all Numpy data types *and* the type of the ``None`` singleton.
'''


SequenceOrNoneTypes = SequenceTypes + NoneTypes
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`Sequence` API as well as the type of the
``None`` singleton.
'''


SetOrNoneTypes = (SetType, NoneType)
'''
Tuple of both the set type *and* the type of the ``None`` singleton.
'''


StrOrNoneTypes = (str, NoneType)
'''
Tuple of both the string type *and* the type of the ``None`` singleton.
'''


TestableOrNoneTypes = TestableTypes + NoneTypes
'''
Tuple of all testable types *and* the type of the ``None`` singleton.
'''

# ....................{ TUPLES ~ regex                    }....................
# Yes, this is the only reliable means of obtaining the type of compiled
# regular expressions. For unknown reasons presumably concerning the archaic
# nature of Python's regular expression support, this type is *NOT* publicly
# exposed. While the private "re._pattern_type" attribute does technically
# provide this type, it does so in a private and hence non-portable manner.
RegexCompiledType = type(re.compile(''))
'''
Type of all compiled regular expressions.
'''


# Yes, this type is required for type validation et the module scope elsewhere.
# Yes, this is the most time-efficient means of obtaining this type. No, this
# type is *NOT* directly importable. Although this type's classname is
# published to be "_sre.SRE_Match", the "_sre" C extension provides no such
# type for pure-Python importation.
RegexMatchType = type(re.match(r'', ''))
'''
Type of all **regular expression match objects** (i.e., objects returned by the
:func:`re.match` function).
'''


RegexTypes = (str, RegexCompiledType)
'''
Tuple of all **regular expression-like types** (i.e., types either defining
regular expressions or losslessly convertible to such types, typically accepted
by functions in the :mod:`betse.util.type.regexes` submodule).
'''


RegexMatchOrNoneTypes = (RegexMatchType, NoneType)
'''
Tuple of both the regular expression match object type *and* the type of the
``None`` singleton.
'''
