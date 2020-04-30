#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

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

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import functools as _functools
import re as _re
from argparse import (
    _SubParsersAction,
    ArgumentParser as _ArgumentParser,
)
from collections import deque as _deque
from collections.abc import (
    Container as _Container,
    Generator as _Generator,
    Hashable as _Hashable,
    Iterable as _Iterable,
    Iterator as _Iterator,
    Mapping as _Mapping,
    MutableMapping as _MutableMapping,
    Sequence as _Sequence,
    Set as _Set,
    Sized as _Sized,
)
from enum import (
    Enum as _Enum,
    EnumMeta as _EnumMeta,
)
from io import IOBase as _IOBase
from weakref import (
    ref as _ref,
    CallableProxyType as _CallableProxyType,
    ProxyType as _ProxyType,
    WeakMethod as _WeakMethod,
)

# Note that:
#
# * The "BuiltinMethodType" is intentionally *NOT* imported. Why? Because that
#   type is exactly synonymous with "BuiltinFunctionType", implying C-based
#   methods are indistinguishable from C-based functions. To prevent C-based
#   functions from being misidentified as C-based methods, all C-based
#   functions and methods are ambiguously identified as C-based callables.
# * The "LambdaType" is intentionally *NOT* imported. Why? Because that type is
#   exactly synonymous with "FunctionType", implying lambdas are
#   indistinguishable from pure-Python functions. To prevent pure-Python
#   functions from being misidentified as lambdas, all lambdas are currently
#   misidentified as pure-Python functions.
#
# These are the lesser of multiple evils.
from types import (
    BuiltinFunctionType as _BuiltinFunctionType,
    FunctionType as _FunctionType,
    GeneratorType as _GeneratorType,
    MethodType as _MethodType,
    ModuleType as _ModuleType,
)

#FIXME: After dropping Python 3.5 support:
#
#* Unconditionally import these types with their brethren above.
#* Reduce the definitions of "AsyncGeneratorCType" and "AsyncCoroutineCType"
#  below to simply:
#    AsyncGeneratorCType = _AsyncGeneratorType
#    AsyncCoroutineCType = _CoroutineType

# Attempt to import types unavailable under Python 3.5.
try:
    from types import (
        AsyncGeneratorType as _AsyncGeneratorType,
        CoroutineType as _CoroutineType,
    )
# If this is Python 3.5, define placeholder globals of the same name.
except ImportError:
    _AsyncGeneratorType = None
    _CoroutineType = None

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TYPES                             }....................
AnyType = object
'''
Type of all objects regardless of type.
'''


ClassType = type
'''
Type of all types.
'''


FileType = _IOBase
'''
Abstract base class implemented by *all* **file-like objects** (i.e., objects
implementing the standard ``read()`` and ``write()`` methods).

This class is a synonym of the :class:`io.IOBase` class, provided merely as a
convenience to callers preferring to avoid importing that class.
'''


ModuleType = _ModuleType
'''
Type of all **C- and Python-based modules** (i.e., importable files implemented
either as C extensions or in pure Python).
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
module defined the same type with the same name under Python 2.x but *not* 3.x.
Depressingly, this type must now be manually redefined everywhere.
'''


class UnavailableType(object):
    '''
    Placeholder value for all **unavailable types** (i.e., types *not*
    available under the active Python interpreter, typically due to
    insufficient Python version or uninstalled third-party dependencies).
    '''

    pass

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
CallableCType = _BuiltinFunctionType
'''
Type of all **C-based callables** (i.e., functions and methods implemented with
low-level C rather than high-level Python, typically either in third-party C
extensions, official stdlib C extensions, or the active Python interpreter
itself).
'''


CallablePartialType = _functools.partial
'''
Type of all **pure-Python partial callables** (i.e., callables dynamically
wrapped by the function-like :class:`functools.partial` class, implemented in
pure Python).

Caveats
----------
This type does *not* distinguish between whether the original callable wrapped
by :class:`functools.partial` is C-based or pure Python -- only that some
callable of indeterminate origin is in fact wrapped.
'''


FunctionType = _FunctionType
'''
Type of all **pure-Python functions** (i.e., functions implemented in pure
Python *not* associated with an owning class or instance of a class).

Caveats
----------
This type does *not* distinguish between conventional named functions and
unnamed lambda functions. Since doing so would usually be seen as overly
specific and insufficiently general, this ambiguity is *not* necessarily a bad
thing.
'''

# ....................{ TYPES ~ callable ~ method         }....................
MethodType = _MethodType
'''
Type of all **pure-Python instance methods** (i.e., methods implemented in pure
Python, bound to instances of classes and implicitly passed those instances as
their first parameters).
'''


# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.MethodWrapperType" object, this is of no benefit to older
# versions of Python. Ergo, the type of an arbitrary method wrapper guaranteed
# to *ALWAYS* exist is obtained instead.
MethodCWrapperType = type(''.__add__)
'''
Type of all **C-based method wrappers** (i.e., bound special methods of a small
subset of builtin types implemented in C).
'''


MethodClassType = classmethod
'''
Type of all **pure-Python class methods** (i.e., methods implemented in pure
Python, bound to classes and implicitly passed those classes as their first
parameters).
'''


# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.MethodDescriptorType" object, this is of no benefit to older
# versions of Python. Ergo, the type of an arbitrary method descriptor
# guaranteed to *ALWAYS* exist is obtained instead.
MethodDescriptorType = type(str.upper)
'''
Type of all **pure-Python method descriptors** (i.e., unbound functions
implemented in pure Python, accessed as class rather than instance attributes).

Note that, despite being unbound, method descriptors remain callable (e.g., by
explicitly passing the intended ``self`` object as their first parameter).
'''


MethodDescriptorPropertyType = property
'''
Type of all **pure-Python property method descriptors** (i.e., unbound
functions implemented in pure Python, accessed as class rather than instance
attributes and decorated by the builtin :class:`property` class decorator).

Note that, unlike comparable method descriptors and slot wrappers, property
objects are *not* callable (i.e., their implementation fails to define the
special ``__call__`` method).
'''


# Since Python appears to expose no explicit slot wrapper type via any standard
# module (e.g., "types", "collections.abc"), the type of an arbitrary slot
# wrapper guaranteed to *ALWAYS* exist is obtained instead.
MethodSlotCWrapperType = type(str.__len__)
'''
Type of all **C-based slot wrappers** (i.e., unbound methods implemented in C,
accessed as class rather than instance attributes).

Note that, despite being unbound, slot wrappers remain callable (e.g., by
explicitly passing the intended ``self`` object as the first parameter).
'''


MethodStaticType = staticmethod
'''
Type of all **pure-Python static methods** (i.e., methods implemented in pure
Python, bound to a class rather than an instance of a class but *not*
implicitly passed that class as their first parameter, unlike class methods).
'''

# ....................{ TYPES ~ callable ~ return : async }....................
AsyncGeneratorCType = (
    UnavailableType if _AsyncGeneratorType is None else _AsyncGeneratorType)
'''
C-based type returned by all **asynchronous pure-Python generators** (i.e.,
callables implemented in pure Python containing one or more ``yield``
statements whose declaration is preceded by the ``async`` keyword).

Caveats
----------
**This is not the type of asynchronous generator callables** but rather the
type implicitly created and *returned* by these callables. Since these
callables are simply callables subject to syntactic sugar, the type of these
callables is simply :data:`CallableTypes`.

**This type is unavailable under Python 3.5,** where it defaults to
:data:`UnavailableType` for safety.
'''


AsyncCoroutineCType = (
    UnavailableType if _CoroutineType is None else _CoroutineType)
'''
C-based type returned by all **asynchronous coroutines** (i.e., callables
implemented in pure Python *not* containing one or more ``yield`` statements
whose declaration is preceded by the ``async`` keyword).

Caveats
----------
**This is not the type of asynchronous coroutine callables** but rather the
type implicitly created and *returned* by these callables. Since these
callables are simply callables subject to syntactic sugar, the type of these
callables is simply :data:`CallableTypes`.

**This type is unavailable under Python 3.5,** where it defaults to
:data:`UnavailableType` for safety.
'''

# ....................{ TYPES ~ callable ~ return : gener }....................
GeneratorType = _Generator
'''
Type of all **C- and Python-based generator objects** (i.e., iterators
implementing the :class:`collections.abc.Generator` protocol), including:

* Pure-Python subclasses of the :class:`collections.abc.Generator` superclass.
* C-based generators returned by pure-Python callables containing one or more
  ``yield`` statements.
* C-based generator comprehensions created by pure-Python syntax delimited by
  ``(`` and ``)``.

This class is a synonym of the :class:`collections.abc.Generator` class,
provided merely as a convenience to callers preferring to avoid importing that
class.

Caveats
----------
**This is not the type of generator callables** but rather the type implicitly
created and *returned* by these callables. Since these callables are simply
callables subject to syntactic sugar, the type of these callables is simply
:data:`CallableTypes`.

See Also
----------
:class:`GeneratorCType`
    Subtype of all C-based generators.
'''


GeneratorCType = _GeneratorType
'''
C-based type returned by all **pure-Python generators** (i.e., callables
implemented in pure Python containing one or more ``yield`` statements,
implicitly converted at runtime to return a C-based iterator of this type) as
well as the C-based type of all **pure-Python generator comprehensions** (i.e.,
``(``- and ``)``-delimited syntactic sugar implemented in pure Python, also
implicitly converted at runtime to return a C-based iterator of this type).

Caveats
----------
**This is not the type of generator callables** but rather the type implicitly
created and *returned* by these callables. Since these callables are simply
callables subject to syntactic sugar, the type of these callables is simply
:data:`CallableTypes`.

This special-purpose type is a subtype of the more general-purpose
:class:`GeneratorType`. Whereas the latter applies to *all* generators
implementing the :class:`collections.abc.Iterator` protocol, the former only
applies to generators implicitly created by Python itself.
'''

# ....................{ TYPES ~ callable : weakref        }....................
WeakRefStandardType = _ref
'''
Type of all **unproxied general-purpose weak references** (i.e., callable
objects yielding a strong reference to their referred object when called).
'''


WeakRefBoundMethodType = _WeakMethod
'''
Type of all **unproxied bound method weak references** (i.e., callable
objects yielding a strong reference to their referred bound method when
called).
'''

# ....................{ TYPES ~ container                 }....................
IteratorType = _Iterator
'''
Abstract interface implemented by all **iterators** (i.e., objects implementing
the standard ``__iter__()`` and ``__next__()`` methods, typically iterating
over an associated container).

This class is a synonym of the :class:`collections.abc.Iterator` class,
provided merely as a convenience to callers preferring to avoid importing that
class.
'''


QueueType = _deque
'''
Concrete type of the only available queue implementation in Python's stdlib.

This class is a synonym of the :class:`collections.deque` class, provided
merely as a convenience to callers preferring to avoid importing that class.

Caveats
----------
Since the :mod:`collections.abc` subpackage currently provides no corresponding
abstract interface to formalize queue types, this type applies *only* to the
standard double-ended queue implementation.
'''


SetType = _Set
'''
Abstract interface implemented by all **set-like containers** (i.e., containers
guaranteeing uniqueness across all items in these containers), including both
the standard :class:`set` and :class:`frozenset` types *and* the types of the
:class:`dict`-specific views returned by the :meth:`dict.items` and
:meth:`dict.keys` (but *not* :meth:`dict.values`) methods.

This class is a synonym of the :class:`collections.abc.Set` class, provided
merely as a convenience to callers preferring to avoid importing that class.
'''


SizedType = _Sized
'''
Abstract interface implemented by all containers defining the special
``__len__()`` method internally called by the :func:`len` builtin.

This class is a synonym of the :class:`collections.abc.Sized` class, provided
merely as a convenience to callers preferring to avoid importing that class.
'''

# ....................{ TYPES ~ container : mapping       }....................
HashableType = _Hashable
'''
Abstract interface implemented by all **hashables** (i.e., objects implementing
the standard ``__hash__()`` method required by all dictionary keys).

This class is a synonym of the :class:`collections.abc.Hashable` class,
provided merely as a convenience to callers preferring to avoid importing that
class.
'''


MappingType = _Mapping
'''
Abstract interface implemented by all dictionary-like objects, both mutable and
immutable.

This class is a synonym of the :class:`collections.abc.Mapping` class, provided
merely as a convenience to callers preferring to avoid importing that class.
'''


MappingMutableType = _MutableMapping
'''
Abstract interface implemented by all mutable dictionary-like objects.

This class is a synonym of the :class:`collections.abc.MutableMapping` class,
provided merely as a convenience to callers preferring to avoid importing that
class.
'''

# ....................{ TYPES ~ enum                      }....................
# Enumeration types are sufficiently obscure to warrant formalization here.

EnumType = _EnumMeta
'''
Metaclass of all **enumeration types** (i.e., classes containing all
enumeration members comprising those enumerations).

This class is a synonym of the :class:`enum.EnumMeta` class, permitting callers
to avoid importing that class.

Motivation
----------
This type is commonly used to type check callable parameters as enumerations.
In recognition of its popularity, this type is intentionally named ``EnumType``
rather than ``EnumMetaType``. While the latter *would* technically be less
ambiguous, the former has the advantage of inviting correctness throughout
downstream codebases -- a less abundant resource.

Why? Because *all* enumeration types are instances of this type rather than the
:class:`Enum` class despite being superficially defined as instances of the
:class:`Enum` class. Thanks to metaclass abuse, enumeration types do *not*
adhere to standard Pythonic semantics. Notably, the following non-standard
invariants hold across *all* enumerations:

    >>> from beartype.cave import (
    ...     ClassType, EnumType, EnumClassType, EnumMemberType)
    >>> GyreType = EnumClassType(
    ...     'Gyre', ('The', 'falcon', 'cannot', 'hear', 'the', 'falconer'))
    >>> isinstance(GyreType, EnumType)
    True
    >>> isinstance(GyreType, EnumClassType)
    False
    >>> isinstance(GyreType, ClassType)
    True
    >>> isinstance(GyreType.falcon, EnumType)
    False
    >>> isinstance(GyreType.falcon, EnumMemberType)
    True
    >>> isinstance(GyreType.falcon, ClassType)
    False
'''


EnumClassType = _Enum
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


EnumMemberType = _Enum
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

    >>> from beartype import beartype
    >>> from beartype.cave import EnumClassType
    >>> EndymionType = EnumClassType('EndymionType', ('BEAUTY', 'JOY',))
    >>> @beartype
    ... def our_feet_were_soft_in_flowers(superlative: EndymionType) -> str:
    ...     return str(superlative).lower()
'''

# ....................{ TYPES ~ regex                     }....................
# Regular expression types are also sufficiently obscure to warrant
# formalization here.

# Yes, this is the only reliable means of obtaining the type of compiled
# regular expressions. For unknown reasons presumably concerning the archaic
# nature of Python's regular expression support, this type is *NOT* publicly
# exposed. While the private "re._pattern_type" attribute does technically
# provide this type, it does so in a private and hence non-portable manner.
RegexCompiledType = type(_re.compile(r''))
'''
Type of all compiled regular expressions.
'''


# Yes, this type is required for type validation at module scope elsewhere.
# Yes, this is the most time-efficient means of obtaining this type. No, this
# type is *NOT* directly importable. Although this type's classname is
# published to be "_sre.SRE_Match", the "_sre" C extension provides no such
# type for pure-Python importation.
RegexMatchType = type(_re.match(r'', ''))
'''
Type of all **regular expression match objects** (i.e., objects returned by the
:func:`re.match` function).
'''

# ....................{ TUPLES                            }....................
ModuleOrStrTypes = (str, ModuleType)
'''
Tuple of both the module *and* string type.
'''


RegexTypes = (str, RegexCompiledType)
'''
Tuple of all **regular expression-like types** (i.e., types either defining
regular expressions or losslessly convertible to such types).
'''


TestableTypes = (ClassType, tuple)
'''
Tuple of all **testable types** (i.e., types suitable for use as the second
parameter passed to the :func:`isinstance` and :func:`issubclass` builtins).
'''

# ....................{ TUPLES ~ callable                 }....................
FunctionTypes = (FunctionType, CallableCType,)
'''
Tuple of all **function classes** (i.e., classes whose instances are either
built-in or user-defined functions).

Caveats
----------
**This tuple may yield false positives when used to validate types.** Since
Python fails to distinguish between C-based functions and methods, this tuple
is the set of all function types as well as the ambiguous type of all C-based
functions and methods.
'''


MethodClassBoundTypes = (MethodClassType, MethodStaticType)
'''
Tuple of all **class-bound method classes** (i.e., classes whose instances are
callable objects bound to a class rather than instance of a class).
'''


MethodBoundTypes = (MethodType, MethodCWrapperType) + MethodClassBoundTypes
'''
Tuple of all **bound method classes** (i.e., classes whose instances are
callable objects bound to either classes or instances of classes).
'''


MethodUnboundTypes = (MethodDescriptorType, MethodSlotCWrapperType)
'''
Tuple of all **unbound method classes** (i.e., classes whose instances are
callable objects bound to neither classes nor instances of classes).

Note that property objects are *not* callable and thus intentionally excluded.
'''


MethodTypes = (CallableCType,) + MethodBoundTypes + MethodUnboundTypes
'''
Tuple of all **method classes** (i.e., classes whose instances are either
built-in or user-defined methods).

Caveats
----------
**This tuple may yield false positives when used to validate types.** Since
Python fails to distinguish between C-based functions and methods, this tuple
is the set of all bound and unbound method types as well as the ambiguous type
of all C-based functions and methods.
'''


# For DRY, this tuple is defined as the set union of all function and method
# types defined above converted back to a tuple.
#
# While this tuple could also be defined as the simple concatenation of the
# "FunctionTypes" and "MethodTypes" tuples, doing so would duplicate all types
# ambiguously residing in both tuples (i.e., "CallableCType"). Doing so would
# induce inefficiencies during type checking, which would be awfully bad.
CallableTypes = tuple(set(FunctionTypes) | set(MethodTypes))
'''
Tuple of all **callable classes** (i.e., classes whose instances are callable
objects, including both built-in and user-defined functions, lambdas, methods,
and method descriptors).
'''


CallableOrStrTypes = CallableTypes + (str,)
'''
Tuple of all callable classes *and* the string type.
'''


DecoratorTypes = CallableTypes + (ClassType,)
'''
Tuple of all **decorator types** (i.e., both callable classes *and* the type of
those classes).

Caveats
----------
**This tuple may yield false positives when used to validate types.** Since
classes themselves may be callable (i.e., by defining the special ``__call__``
method), this tuple is the set of all standard callable types as well as that
of classes. In particular, this tuple describes all types permissible for use
as decorators. Since most classes are *not* callable, however, this tuple may
yield false positives when passed classes.
'''

# ....................{ TUPLES ~ callable ~ return        }....................
AsyncCTypes = (AsyncGeneratorCType, AsyncCoroutineCType)
'''
Tuple of all C-based types returned by all **asynchronous callables** (i.e.,
callables implemented in pure Python whose declaration is preceded by the
``async`` keyword).
'''

# ....................{ TUPLES ~ container                }....................
# Note: this is conditionally expanded by the "TUPLES ~ init" subsection below.
ContainerTypes = (_Container,)
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


# Note: this is conditionally expanded by the "TUPLES ~ init" subsection below.
IterableTypes = (_Iterable,)
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`collections.abc.Iterable` API.

See Also
----------
:class:`SequenceTypes`
    Further details.
'''


# Note: this is conditionally expanded by the "TUPLES ~ init" subsection below.
SequenceTypes = (_Sequence,)
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`collections.abc.Sequence` API.

Sequences are iterables supporting efficient element access via integer
indices. Most sequences implement the :class:`collections.abc.Sequence`
abstract base class, including the concrete :class:`str` string class. All
sequences define the special ``__getitem__()`` and ``__len__()`` methods
(amongst various others).

While all sequences are iterables, not all iterables are sequences. Generally
speaking, sequences correspond to the proper subset of iterables whose elements
are ordered. :class:`dict` and :class:`OrderedDict` are the canonical examples.
:class:`dict` implements :class:`collections.abc.Iterable` but *not*
:class:`collections.abc._Sequence`, due to failing to support integer
index-based lookup; :class:`OrderedDict` implements both, due to supporting
such lookup.

For generality, this tuple contains classes matching both pure-Python sequences
*and* non-Pythonic Fortran-based NumPy arrays and matrices -- which fail to
subclass :class:`collections.abc.Sequence` despite implementing the entirety of
that that API.
'''

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

# ....................{ TUPLES ~ scalar                   }....................
# Note: this is conditionally expanded by the "TUPLES ~ init" subsection below.
BoolTypes = (bool,)
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
'''


NumericSimpleTypes = (float, int,)
'''
Tuple of all **builtin simple numeric types** (i.e., classes whose instances
are trivial scalar numbers), comprising both integer and real number types.

This tuple intentionally excludes complex number types - whose non-trivial
encapsulation of a pair of real numbers *usually* necessitates non-trivial
special handling.
'''


NumericTypes = (complex,) + NumericSimpleTypes
'''
Tuple of all **builtin numeric types** (i.e., classes whose instances are
scalar numbers), comprising integer, real number, and complex number types.
'''


NumericlikeTypes = (bool,) + NumericTypes
'''
Tuple of all **builtin numeric-like types** (i.e., classes whose instances are
either scalar numbers or types trivially convertible into scalar numbers),
comprising boolean, integer, real number, and complex number types.

Booleans are trivially convertible into integers. While details differ by
implementation, common implementations in lower-level languages (e.g., C, C++,
Perl) typically implicitly convert:

* ``False`` to ``0``.
* ``True`` to ``1``.
'''


ScalarTypes = (str,) + NumericlikeTypes
'''
Tuple of all **builtin scalar types** (i.e., classes whose instances are
single scalar primitives), comprising all boolean, numeric, and textual types.
'''

# ....................{ TUPLES ~ weakref                  }....................
WeakRefProxyTypes = (_CallableProxyType, _ProxyType)
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

# ....................{ TUPLES ~ lib                      }....................
# Types conditionally dependent upon the importability of third-party
# dependencies. For safety, all such types default to "None" for simple types
# and the empty tuple for tuples of simple types and are subsequently redefined
# by the try-except block below.

# ....................{ TUPLES ~ lib : numpy              }....................
# Defined by the "TUPLES ~ init" subsection below.
NumpyArrayType = UnavailableType
'''
Type of all NumPy arrays if :mod:`numpy` is importable *or*
:data:`UnavailableType` otherwise (i.e., if :mod:`numpy` is unimportable).

This class is a synonym of the :class:`numpy.ndarray` class, permitting callers
to avoid importing that class.
'''


# Defined by the "TUPLES ~ init" subsection below.
NumpyScalarType = UnavailableType
'''
Superclass of all NumPy scalar subclasses (e.g., :class:`numpy.bool_`) if
:mod:`numpy` is importable *or* :data:`UnavailableType` otherwise (i.e., if
:mod:`numpy` is unimportable).

This class is a synonym of the :class:`numpy.generic` class, permitting callers
to avoid importing that class.
'''


# Defined by the "TUPLES ~ init" subsection below.
NumpyDataTypes = ()
'''
Tuple of the **NumPy data type** (i.e., NumPy-specific numeric scalar type
homogeneously constraining all elements of all NumPy arrays) and all scalar
Python types transparently supported by NumPy as implicit data types (i.e.,
:class:`bool`, :class:`complex`, :class:`float`, and :class:`int`) if
:mod:`numpy` is importable *or* the empty tuple otherwise.

This class is a synonym of the :class:`numpy.dtype` class, permitting callers
to avoid importing that class.
'''

# ....................{ TUPLES ~ lib : setuptools         }....................
# Defined by the "TUPLES ~ init" subsection below.
DistributionSetuptoolsOrNoneTypes = ()
'''
Tuple of the type of all :mod:`setuptools`-specific package metadata objects
and of the ``None`` singleton if :mod:`pkg_resources` is importable *or* the
empty tuple otherwise.
'''


# Defined by the "TUPLES ~ init" subsection below.
VersionSetuptoolsTypes = ()
'''
Tuple of all :mod:`setuptools`-specific version types (i.e., types instantiated
and returned by the stable :func:`pkg_resources.parse_version` function bundled
with :mod:`setuptools`) if :mod:`pkg_resources` is importable *or* the empty
tuple otherwise.

Specifically, this tuple contains the following types if :mod:`pkg_resources`
is importable:

* :class:`pkg_resources.packaging.version.Version`, a `PEP 440`_-compliant
  version type.
* :class:`pkg_resources.packaging.version.LegacyVersion`, a `PEP
  440`_-noncompliant version type.

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
    import numpy as _numpy

    # Define NumPy-specific types.
    NumpyArrayType  =  _numpy.ndarray
    NumpyScalarType =  _numpy.generic
    NumpyDataTypes  = (_numpy.dtype,) + NumericlikeTypes

    # Extend NumPy-agnostic types with NumPy-specific types.
    BoolTypes += (_numpy.bool_,)
    ContainerTypes += (NumpyArrayType,)
    IterableTypes  += (NumpyArrayType,)
    SequenceTypes  += (NumpyArrayType,)
# Else, NumPy is unimportable. We're done here, folks.
except:
    pass


# If setuptools is importable, conditionally define setuptools-specific types.
try:
    import pkg_resources as _pkg_resources

    # Define setuptools-specific types.
    DistributionSetuptoolsOrNoneTypes = (_pkg_resources.Distribution, NoneType)
    VersionSetuptoolsTypes = (
        _pkg_resources.packaging.version.Version,
        _pkg_resources.packaging.version.LegacyVersion,
    )
# Else, setuptools is unimportable. While this should typically *NEVER* be the
# case, edge cases gonna edge case.
except:
    pass

# ....................{ TUPLES ~ post-init : container    }....................
# Tuples of types assuming the above initialization to have been performed.

MappingOrSequenceTypes = (MappingType,) + SequenceTypes
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`collections.abc.Mapping` *or*
:class:`collections.abc.Sequence` APIs.
'''


ModuleOrSequenceTypes = (ModuleType,) + SequenceTypes
'''
Tuple of the module type *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Sequence`
API.
'''


NumericOrIterableTypes = NumericSimpleTypes + IterableTypes
'''
Tuple of all numeric types *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Iterable`
API.
'''


NumericOrSequenceTypes = NumericSimpleTypes + SequenceTypes
'''
Tuple of all numeric types *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Sequence`
API.
'''

# ....................{ TUPLES ~ post-init : version      }....................
VersionComparableTypes = (tuple,) + VersionSetuptoolsTypes
'''
Tuple of all **comparable version types** (i.e., types suitable for use both as
parameters to callables accepting arbitrary version specifiers *and* as
operands to numeric operators comparing such specifiers) if
:mod:`pkg_resources` is importable *or* ``(tuple,)`` otherwise.

This is the proper subset of types listed by the :data:`VersionTypes` tuple
that are directly comparable, thus excluding the :class:`str` type.
``.``-delimited version specifier strings are only indirectly comparable after
conversion to a comparable version type.

Caveats
----------
Note that all types listed by this tuple are *only* safely comparable with
versions of the same type. In particular, the types listed by the
:class:`VersionSetuptoolsTypes` tuple do *not* necessarily support direct
comparison with either the :class:`tuple` *or* `class:`str` version types;
ironically, those types supported both under older but *not* newer versions of
:mod:`setuptools`. This is why we can't have good things.
'''


VersionTypes = (str,) + VersionComparableTypes
'''
Tuple of all **version types** (i.e., types suitable for use as parameters to
callables accepting arbitrary version specifiers) if :mod:`pkg_resources` is
importable *or* ``(str, tuple,)`` otherwise.

This includes:

* :class:`str`, specifying versions in ``.``-delimited positive integer format
  (e.g., ``2.4.14.2.1.356.23``).
* :class:`tuple`, specifying versions as one or more positive integers (e.g.,
  ``(2, 4, 14, 2, 1, 356, 23)``),
* :class:`VersionSetuptoolsTypes`, whose :mod:`setuptools`-specific types
  specify versions as instance variables convertible into both of the prior
  formats (e.g., ``VersionSetuptoolsTypes[0]('2.4.14.2.1.356.23')``).
'''

# ....................{ TUPLES ~ none                     }....................
# Tuples of types containing at least the type of the singleton "None" object.

NoneTypes = (NoneType,)
'''
Tuple of only the type of the ``None`` singleton.

This tuple is principally intended for use in efficiently constructing other
tuples of types containing this type.
'''


CallableOrNoneTypes = CallableTypes + NoneTypes
'''
Tuple of all callable classes *and* the type of the ``None`` singleton.
'''


ClassOrNoneTypes = (ClassType, NoneType)
'''
Tuple of the type of all types *and* that of the ``None`` singleton.
'''


RegexMatchOrNoneTypes = (RegexMatchType, NoneType)
'''
Tuple of both the regular expression match object type *and* the type of the
``None`` singleton.
'''


TestableOrNoneTypes = TestableTypes + NoneTypes
'''
Tuple of all testable types *and* the type of the ``None`` singleton.
'''

# ....................{ TUPLES ~ none : container         }....................
IterableOrNoneTypes = IterableTypes + NoneTypes
'''
Tuple of all container base classes conforming to (but _not_ necessarily
subclassing) the canonical :class:`_Iterable` API as well as the type of the
``None`` singleton.
'''


MappingOrNoneTypes = (MappingType,) + NoneTypes
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`_Mapping` API as well as the type of the
``None`` singleton.
'''


MappingOrSequenceOrNoneTypes = MappingOrSequenceTypes + NoneTypes
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`_Mapping` *or* :class:`_Sequence` APIs as
well as the type of the ``None`` singleton.
'''


NumericOrSequenceOrNoneTypes = NumericOrSequenceTypes + NoneTypes
'''
Tuple of all numeric types, all container base classes conforming to (but *not*
necessarily subclassing) the canonical :class:`int`, :class:`float`, *or*
:class:`_Sequence` APIs as well as the type of the singleton ``None`` object.
'''


NumpyDataOrNoneTypes = NumpyDataTypes + NoneTypes
'''
Tuple of all NumPy data types *and* the type of the ``None`` singleton.
'''


SequenceOrNoneTypes = SequenceTypes + NoneTypes
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`_Sequence` API as well as the type of the
``None`` singleton.
'''


SetOrNoneTypes = (SetType, NoneType)
'''
Tuple of both the set type *and* the type of the ``None`` singleton.
'''


# ....................{ TUPLES ~ none : scalar            }....................
BoolOrNoneTypes = (bool, NoneType)
'''
Tuple of both the boolean type *and* that of the ``None`` singleton.
'''


IntOrNoneTypes = (int, NoneType)
'''
Tuple of both the integer type *and* that of the ``None`` singleton.
'''


NumericOrNoneTypes = NumericSimpleTypes + NoneTypes
'''
Tuple of all numeric types *and* the type of the singleton ``None`` object.
'''


StrOrNoneTypes = (str, NoneType)
'''
Tuple of both the string type *and* the type of the ``None`` singleton.
'''
