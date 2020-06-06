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

# ....................{ TODO                              }....................
#FIXME: Revise all "README.rst" examples in accordance with recent changes to
#this submodule. Let's preserve worky, please.

#FIXME: Add types for all remaining useful "collections.abc" interfaces,
#including:
#* "Reversible".
#* "AsyncIterable".
#* "AsyncIterator".
#* "AsyncGenerator".
#
#There certainly exist other "collections.abc" interfaces as well, but it's
#unclear whether they have any practical real-world utility during type
#checking. These include:
#* "ByteString". (wut)
#* Dictionary-specific views (e.g., "MappingView", "ItemsView").

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import functools as _functools
import numbers as _numbers
import re as _re
from argparse import (
    _SubParsersAction,
    ArgumentParser as _ArgumentParser,
)
from beartype._cave.abc import _BoolType
from beartype._cave.mapping import _NoneTypeOrType
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
    MutableSequence as _MutableSequence,
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
    ProxyTypes as _ProxyTypes,
)

# Note that:
#
# * "BuiltinMethodType" is intentionally *NOT* imported, as that type is
#   exactly synonymous with "BuiltinFunctionType", implying C-based methods are
#   indistinguishable from C-based functions. To prevent C-based functions from
#   being misidentified as C-based methods, all C-based functions and methods
#   are ambiguously identified as C-based callables.
# * "LambdaType" is intentionally *NOT* imported, as that type is exactly
#   synonymous with "FunctionType", implying lambdas are indistinguishable from
#   pure-Python functions. To prevent pure-Python functions from being
#   misidentified as lambdas, all lambdas are currently misidentified as
#   pure-Python functions.
#
# These are the lesser of multiple evils.
from types import (
    BuiltinFunctionType as _BuiltinFunctionType,
    FunctionType as _FunctionType,
    GeneratorType as _GeneratorType,
    MethodType as _MethodType,
    ModuleType as _ModuleType,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ IMPORTS ~ conditional             }....................
#FIXME: After dropping Python 3.5 support:
#
#* Unconditionally import these types with their brethren above.
#* Reduce the definitions of "AsyncGeneratorCType" and "AsyncCoroutineCType"
#  below to simply:
#    AsyncGeneratorCType = _AsyncGeneratorType
#    AsyncCoroutineCType = _CoroutineType

# Attempt to import types unavailable under Python 3.5.
try:
    from collections.abc import Collection as _Collection
    from types import (
        AsyncGeneratorType as _AsyncGeneratorType,
        CoroutineType as _CoroutineType,
    )
# If this is Python 3.5, define placeholder globals of the same name.
except ImportError:
    _AsyncGeneratorType = None
    _Collection = None
    _CoroutineType = None

# ....................{ TYPES ~ unavailable               }....................
# Unavailable types are defined *BEFORE* any subsequent types, as the latter
# commonly leverage the former.

class UnavailableType(object):
    '''
    **Unavailable type** (i.e., type *not* available under the active Python
    interpreter, typically due to insufficient Python version or non-installed
    third-party dependencies).
    '''

    pass


def _get_type_or_unavailable(cls: type) -> type:
    '''
    Return the passed type if non-``None`` *or* :class:`UnavailableType`
    otherwise (i.e., if this type is ``None``).
    '''

    return UnavailableType if cls is None else cls

# ....................{ TYPES ~ core                      }....................
AnyType = object
'''
Type of all objects regardless of type.
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


ClassType = type
'''
Type of all types.
'''

# ....................{ TYPES ~ py                        }....................
FileType = _IOBase
'''
Abstract base class of all **file-like objects** (i.e., objects implementing
the standard ``read()``, ``write()``, and ``close()`` methods).
'''


ModuleType = _ModuleType
'''
Type of all **C- and Python-based modules** (i.e., importable files implemented
either as C extensions or in pure Python).
'''

# ....................{ TYPES ~ call                      }....................
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

# ....................{ TYPES ~ call : function           }....................
FunctionType = _FunctionType
'''
Type of all **pure-Python functions** (i.e., functions implemented in pure
Python *not* associated with an owning class or instance of a class).

Caveats
----------
**This type ambiguously matches many callable types not commonly associated
with "named functions,"** including:

* **Lambda functions.** Of course, distinguishing between conventional named
  functions and unnamed lambda functions would usually be seen as overly
  specific. So, this ambiguity is *not* necessarily a bad thing.
* **Unbound instance methods** (i.e., instance methods accessed on their
  declaring classes rather than bound instances).
* **Static methods** (i.e., methods decorated with the builtin
  :func:`staticmethod` decorator regardless of whether accessed on their
  declaring classes or associated instances).

See Also
----------
:class:`MethodBoundInstanceOrClassType`
    Type of all pure-Python bound instance and class methods.
'''


FunctionOrMethodCType = _BuiltinFunctionType
'''
Type of all **C-based callables** (i.e., functions and methods implemented with
low-level C rather than high-level Python, typically either in third-party C
extensions, official stdlib C extensions, or the active Python interpreter
itself).
'''

# ....................{ TYPES ~ call : method : bound     }....................
MethodBoundInstanceOrClassType = _MethodType
'''
Type of all **pure-Python bound instance and class methods** (i.e., methods
implemented in pure Python, bound to either instances of classes or classes and
implicitly passed those instances or classes as their first parameters).

Caveats
----------
There exists *no* corresponding :class:`MethodUnboundInstanceType` type, as
unbound pure-Python instance methods are ambiguously implemented as functions
of type :class:`FunctionType` indistinguishable from conventional functions.
Indeed, `official documentation <PyInstanceMethod_Type documentation_>`__ for
the ``PyInstanceMethod_Type`` C type explicitly admits that:

    This instance of PyTypeObject represents the Python instance method type.
    It is not exposed to Python programs.

.. _PyInstanceMethod_Type documentation:
   https://docs.python.org/3/c-api/method.html#c.PyInstanceMethod_Type
'''


# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.MethodWrapperType" object, this is of no benefit to older
# versions of Python. Ergo, the type of an arbitrary method wrapper guaranteed
# to *ALWAYS* exist is obtained instead.
MethodBoundInstanceDunderCType = type(''.__add__)
'''
Type of all **C-based bound method wrappers** (i.e., callable objects
implemented in low-level C, associated with special methods of builtin types
when accessed as instance rather than class attributes).

See Also
----------
:class:`MethodUnboundInstanceDunderCType`
    Type of all C-based unbound dunder method wrapper descriptors.
'''

# ....................{ TYPES ~ call : method : unbound   }....................
# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.ClassMethodDescriptorType" object, this is of no benefit to
# older versions of Python. Ergo, the type of an arbitrary method descriptor
# guaranteed to *ALWAYS* exist is obtained instead.
MethodUnboundClassCType = type(dict.__dict__['fromkeys'])
'''
Type of all **C-based unbound class method descriptors** (i.e., callable
objects implemented in low-level C, associated with class methods of
builtin types when accessed with the low-level :attr:`object.__dict__`
dictionary rather than as class or instance attributes).

Despite being unbound, class method descriptors remain callable (e.g., by
explicitly passing the intended ``cls`` objects as their first parameters).
'''


# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.WrapperDescriptorType" object, this is of no benefit to older
# versions of Python. Ergo, the type of an arbitrary method descriptor
# guaranteed to *ALWAYS* exist is obtained instead.
MethodUnboundInstanceDunderCType = type(str.__add__)
'''
Type of all **C-based unbound dunder method wrapper descriptors** (i.e.,
callable objects implemented in low-level C, associated with dunder methods of
builtin types when accessed as class rather than instance attributes).

Despite being unbound, method descriptor wrappers remain callable (e.g., by
explicitly passing the intended ``self`` objects as their first parameters).

See Also
----------
:class:`MethodBoundInstanceDunderCType`
    Type of all C-based unbound dunder method wrappers.
:class:`MethodUnboundInstanceNondunderCType`
    Type of all C-based unbound non-dunder method descriptors.
'''


# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.MethodDescriptorType" object, this is of no benefit to older
# versions of Python. Ergo, the type of an arbitrary method descriptor
# guaranteed to *ALWAYS* exist is obtained instead.
MethodUnboundInstanceNondunderCType = type(str.upper)
'''
Type of all **C-based unbound non-dunder method descriptors** (i.e., callable
objects implemented in low-level C, associated with non-dunder methods of
builtin types when accessed as class rather than instance attributes).

Despite being unbound, method descriptors remain callable (e.g., by explicitly
passing the intended ``self`` objects as their first parameters).

See Also
----------
:class:`MethodUnboundInstanceDunderCType`
    Type of all C-based unbound dunder method wrapper descriptors.
'''

# ....................{ TYPES ~ call : method : decorator }....................
MethodDecoratorClassType = classmethod
'''
Type of all **C-based unbound class method descriptors** (i.e., non-callable
instances of the builtin :class:`classmethod` decorator class implemented in
low-level C, associated with class methods implemented in pure Python, and
accessed with the low-level :attr:`object.__dict__` dictionary rather than as
class or instance attributes).

Caveats
----------
Class method objects are *only* accessible with the low-level
:attr:`object.__dict__` dictionary. When accessed as class or instance
attributes, class methods are instances of the standard
:class:`MethodBoundInstanceOrClassType` type.

Class method objects are *not* callable, as their implementations fail to
define the ``__call__`` dunder method.
'''


MethodDecoratorPropertyType = property
'''
Type of all **C-based unbound property method descriptors** (i.e., non-callable
instances of the builtin :class:`property` decorator class implemented in
low-level C, associated with property getter and setter methods implemented in
pure Python, and accessed as class rather than instance attributes).

Caveats
----------
Property objects are accessible both as class attributes *and* with the
low-level :attr:`object.__dict__` dictionary. Property objects are *not*
accessible as instance attributes, for hopefully obvious reasons.

Property objects are *not* callable, as their implementations fail to define
the ``__call__`` dunder method.
'''


MethodDecoratorStaticType = staticmethod
'''
Type of all **C-based unbound static method descriptors** (i.e., non-callable
instances of the builtin :class:`classmethod` decorator class implemented in
low-level C, associated with static methods implemented in pure Python, and
accessed with the low-level :attr:`object.__dict__` dictionary rather than as
class or instance attributes).

Caveats
----------
Static method objects are *only* accessible with the low-level
:attr:`object.__dict__` dictionary. When accessed as class or instance
attributes, static methods are instances of the standard :class:`FunctionType`
type.

Static method objects are *not* callable, as their implementations fail to
define the ``__call__`` dunder method.
'''

# ....................{ TYPES ~ call : return : async     }....................
AsyncGeneratorCType = _get_type_or_unavailable(_AsyncGeneratorType)
'''
C-based type returned by all **asynchronous pure-Python generators** (i.e.,
callables implemented in pure Python containing one or more ``yield``
statements whose declaration is preceded by the ``async`` keyword) if the
active Python interpreter is at least version 3.6.0 *or*
:class:`UnavailableType` otherwise.


Caveats
----------
**This is not the type of asynchronous generator callables** but rather the
type implicitly created and *returned* by these callables. Since these
callables are simply callables subject to syntactic sugar, the type of these
callables is simply :data:`CallableTypes`.

**This type is unavailable under Python 3.5,** where it defaults to
:class:`UnavailableType` for safety.
'''


AsyncCoroutineCType = _get_type_or_unavailable(_CoroutineType)
'''
C-based type returned by all **asynchronous coroutines** (i.e., callables
implemented in pure Python *not* containing one or more ``yield`` statements
whose declaration is preceded by the ``async`` keyword) if the active Python
interpreter is at least version 3.6.0 *or* :class:`UnavailableType` otherwise.

Caveats
----------
**This is not the type of asynchronous coroutine callables** but rather the
type implicitly created and *returned* by these callables. Since these
callables are simply callables subject to syntactic sugar, the type of these
callables is simply :data:`CallableTypes`.

**This type is unavailable under Python 3.5,** where it defaults to
:class:`UnavailableType` for safety.
'''

# ....................{ TYPES ~ call : return : generator }....................
GeneratorType = _Generator
'''
Type of all **C- and Python-based generator objects** (i.e., iterators
implementing the :class:`collections.abc.Generator` protocol), including:

* Pure-Python subclasses of the :class:`collections.abc.Generator` superclass.
* C-based generators returned by pure-Python callables containing one or more
  ``yield`` statements.
* C-based generator comprehensions created by pure-Python syntax delimited by
  ``(`` and ``)``.

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

# ....................{ TYPES ~ call : weakref            }....................
WeakRefCType = _ref
'''
Type of all **unproxied weak references** (i.e., callable objects yielding
strong references to their referred objects when called).

This type matches both the C-based :class:`weakref.ref` class *and* the
pure-Python :class:`weakref.WeakMethod` class, which subclasses the former.
'''

# ....................{ TYPES ~ contain                   }....................
ContainerType = _Container
'''
Type of all **containers** (i.e., concrete instances of the abstract
:class:`collections.abc.Container` base class as well as arbitrary objects
whose classes implement all abstract methods declared by that base class
regardless of whether those classes actually subclass that base class).

Caveats
----------
This type ambiguously matches both:

* **Explicit container subtypes** (i.e., concrete subclasses of the
  :class:`collections.abc.Container` abstract base class (ABC)).
* **Structural container subtypes** (i.e., arbitrary classes implementing the
  abstract ``__contains__`` method declared by that ABC *without* subclassing
  that ABC), as formalized by `PEP 544 -- Protocols: Structural subtyping
  (static duck typing) <PEP 544_>`_. Notably, since the **NumPy array type**
  (i.e., :class:`numpy.ndarray`) defines that method, this type magically
  matches the NumPy array type as well.

Of course, distinguishing between explicit and structural subtypes would
usually be seen as overly specific. So, this ambiguity is *not* necessarily a
BadThing™.

What is a BadThing™ is that container ABCs violate the "explicit is better than
implicit" maxim of `PEP 20 -- The Zen of Python <PEP 20_>`__ by intentionally
deceiving you for your own benefit, which you of course appreciate. Thanks to
arcane dunder magics buried in the :class:`abc.ABCMeta` metaclass, the
:func:`isinstance` and :func:`issubclass` builtin functions (which the
:func:`beartype.beartype` decorator internally defers to) ambiguously mistype
structural container subtypes as explicit container subtypes:

.. code-block:: python

   >>> from collections.abc import Container
   >>> class FakeContainer(object):
   ...     def __contains__(self, obj): return True
   >>> FakeContainer.__mro__
   ... (FakeContainer, object)
   >>> issubclass(FakeContainer, Container)
   True
   >>> isinstance(FakeContainer(), Container)
   True

.. _PEP 20:
   https://www.python.org/dev/peps/pep-0020
.. _PEP 544:
   https://www.python.org/dev/peps/pep-0544
'''


IterableType = _Iterable
'''
Type of all **iterables** (i.e., both concrete and structural instances of the
abstract :class:`collections.abc.Iterable` base class).

Iterables are containers that may be indirectly iterated over by calling the
:func:`iter` builtin, which internally calls the ``__iter__()`` dunder methods
implemented by these containers, which return **iterators** (i.e., instances of
the :class:`IteratorType` type), which directly support iteration.

This type also matches **NumPy arrays** (i.e., instances of the concrete
:class:`numpy.ndarray` class) via structural subtyping.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
:class:`IteratorType`
    Further details on iteration.
'''


IteratorType = _Iterator
'''
Type of all **iterators** (i.e., both concrete and structural instances of
the abstract :class:`collections.abc.Iterator` base class; objects iterating
over associated data streams, which are typically containers).

Iterators implement at least two dunder methods:

* ``__next__()``, iteratively returning successive items from associated data
  streams (e.g., container objects) until throwing standard
  :data:`StopIteration` exceptions on reaching the ends of those streams.
* ``__iter__()``, returning themselves. Since iterables (i.e., instances of the
  :class:`IterableType` type) are *only* required to implement the
  ``__iter__()`` dunder method, all iterators are by definition iterables as
  well.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
:class:`IterableType`
    Further details on iteration.
'''


SizedType = _Sized
'''
Type of all **sized containers** (i.e., both concrete and structural instances
of the abstract :class:`collections.abc.Sized` base class; containers defining
the ``__len__()`` dunder method internally called by the :func:`len` builtin).

This type also matches **NumPy arrays** (i.e., instances of the concrete
:class:`numpy.ndarray` class) via structural subtyping.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


CollectionType = _get_type_or_unavailable(_Collection)
'''
Type of all **collections** (i.e., both concrete and structural instances of
the abstract :class:`collections.abc.Collection` base class; sized iterable
containers defining the ``__contains__()``, ``__iter__()``, and ``__len__()``
dunder methods) if the active Python interpreter is at least version 3.6.0 *or*
:class:`UnavailableType` otherwise.

This type also matches **NumPy arrays** (i.e., instances of the concrete
:class:`numpy.ndarray` class) via structural subtyping.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


QueueType = _deque
'''
Type of all **double-ended queues** (i.e., instances of the concrete
:class:`collections.deque` class, the only queue type defined by the Python
stdlib).

Caveats
----------
The :mod:`collections.abc` subpackage currently provides no corresponding
abstract interface to formalize queue types. Double-ended queues are it, sadly.
'''


SetType = _Set
'''
Type of all **set-like containers** (i.e., both concrete and structural
instances of the abstract :class:`collections.abc.Set` base class; containers
guaranteeing uniqueness across all contained items).

This type matches both the standard :class:`set` and :class:`frozenset` types
*and* the types of the :class:`dict`-specific views returned by the
:meth:`dict.items` and :meth:`dict.keys` (but *not* :meth:`dict.values`)
methods.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''

# ....................{ TYPES ~ contain : mapping         }....................
HashableType = _Hashable
'''
Type of all **hashable objects** (i.e., both concrete and structural instances
of the abstract :class:`collections.abc.Hashable` base class; objects
implementing the ``__hash__()`` dunder method required for all dictionary keys
and set items).

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


MappingType = _Mapping
'''
Type of all **mutable** and **immutable mappings** (i.e., both concrete and
structural instances of the abstract :class:`collections.abc.Mapping` base
class; dictionary-like containers containing key-value pairs mapping from
hashable keys to corresponding values).

Caveats
----------
**This type does not guarantee mutability** (i.e., the capacity to modify
instances of this type after instantiation). This type ambiguously matches both
mutable mapping types (e.g., :class:`dict`) and immutable mapping types (e.g.,
:class:`mappingproxy`). Where mutability is required, prefer the non-ambiguous
:class:`MappingMutableType` type instead.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


MappingMutableType = _MutableMapping
'''
Type of all **mutable mappings** (i.e., both concrete and structural instances
of the abstract :class:`collections.abc.MutableMapping` base class;
dictionary-like containers permitting modification of contained key-value
pairs).

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
:class:`MappingType`
    Type of all mutable and immutable mappings.
'''

# ....................{ TYPES ~ contain : sequence        }....................
SequenceType = _Sequence
'''
Type of all **mutable** and **immutable sequences** (i.e., both concrete and
structural instances of the abstract :class:`collections.abc.Sequence` base
class; reversible collections whose items are efficiently accessible but *not*
necessarily modifiable with 0-based integer-indexed lookup).

Caveats
----------
**This type does not guarantee mutability** (i.e., the capacity to modify
instances of this type after instantiation). This type ambiguously matches both
mutable sequence types (e.g., :class:`list`) and immutable sequence types
(e.g., :class:`tuple`). Where mutability is required, prefer the non-ambiguous
:class:`SequenceMutableType` type instead.

**This type matches the string type (i.e., :class:`str`),** which satisfies the
:class:`collections.abc.Sequence` API but *not* the
:class:`collections.abc.MutableSequence` API. Where **non-string sequences**
(i.e., sequences that are anything but strings) are required, prefer the
non-ambiguous :class:`SequenceMutableType` type instead.

**This type does not match NumPy arrays (i.e., instances of the concrete
:class:`numpy.ndarray` class),** which satisfy most but *not* all of the
:class:`collections.abc.Sequence` API. Specifically, NumPy arrays fail to
define:

* The ``__reversible__`` dunder method.
* The ``count`` public method.
* The ``index`` public method.

Most callables accepting sequences *never* invoke these edge-case methods and
should thus be typed to accept NumPy arrays as well. To do so, prefer either:

* The :class:`SequenceOrNumpyArrayTypes` tuple of types matching both sequences
  and NumPy arrays.
* The :class:`SequenceMutableOrNumpyArrayTypes` tuple of types matching both
  mutable sequences and NumPy arrays.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


SequenceMutableType = _MutableSequence
'''
Type of all **mutable sequences** (i.e., both concrete and structural instances
of the abstract :class:`collections.abc.Sequence` base class; reversible
collections whose items are both efficiently accessible *and* modifiable with
0-based integer-indexed lookup).

Caveats
----------
**This type does not match NumPy arrays (i.e., instances of the concrete
:class:`numpy.ndarray` class),** which satisfy most but *not* all of the
:class:`collections.abc.MutableSequence` API. Specifically, NumPy arrays fail
to define:

* The ``__reversible__`` dunder method.
* The ``append`` public method.
* The ``count`` public method.
* The ``extend`` public method.
* The ``index`` public method.
* The ``insert`` public method.
* The ``pop`` public method.
* The ``remove`` public method.
* The ``reverse`` public method.

Most callables accepting mutable sequences *never* invoke these edge-case
methods and should thus be typed to accept NumPy arrays as well. To do so,
prefer the :class:`SequenceMutableOrNumpyArrayTypes` tuple of types matching
both mutable sequences and NumPy arrays.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
:class:`SequenceType`
    Further details on sequences.
'''

# ....................{ TYPES ~ enum                      }....................
# Enumeration types are sufficiently obscure to warrant formalization here.

EnumType = _EnumMeta
'''
Type of all **enumeration types** (i.e., metaclass of all classes containing
all enumeration members comprising those enumerations).

Motivation
----------
This type is commonly used to validate callable parameters as enumerations. In
recognition of its popularity, this type is intentionally named ``EnumType``
rather than ``EnumMetaType``. While the latter *would* technically be less
ambiguous, the former has the advantage of inviting correctness throughout
downstream codebases -- a less abundant resource.

Why? Because *all* enumeration types are instances of this type rather than the
:class:`Enum` class despite being superficially defined as instances of the
:class:`Enum` class. Thanks to metaclass abuse, enumeration types do *not*
adhere to standard Pythonic semantics. Notably, the following non-standard
invariants hold across *all* enumerations:

.. code-block:: python

   >>> from enum import Enum
   >>> GyreType = Enum(
   ...     'GyreType', ('THE', 'FALCON', 'CANNOT', 'HEAR', 'THE', 'FALCONER'))
   >>> from beartype import cave
   >>> isinstance(GyreType, Enum)
   False
   >>> isinstance(GyreType, cave.EnumType)
   True
   >>> isinstance(GyreType, cave.ClassType)
   True
   >>> isinstance(GyreType.FALCON, cave.EnumType)
   False
   >>> isinstance(GyreType.FALCON, cave.EnumMemberType)
   True
   >>> isinstance(GyreType.FALCON, cave.ClassType)
   False

Yes, this is insane. Yes, this is Python.
'''


EnumMemberType = _Enum
'''
Type of all **enumeration members** (i.e., abstract base class of all
alternative choices defined as enumeration fields).

Caveats
----------
When type checking callable parameters, this class should *only* be referenced
where the callable permissively accepts any enumeration member type rather than
a specific enumeration member type. In the latter case, that type is simply
that enumeration's type and should be directly referenced as such: e.g.,

    >>> from enum import Enum
    >>> from beartype import beartype
    >>> EndymionType = Enum('EndymionType', ('BEAUTY', 'JOY',))
    >>> @beartype
    ... def our_feet_were_soft_in_flowers(superlative: EndymionType) -> str:
    ...     return str(superlative).lower()
'''

# ....................{ TYPES ~ scalar                    }....................
BoolType = _BoolType
'''
Type of all **booleans** (i.e., objects defining the ``__bool__()`` dunder
method; objects reducible in boolean contexts like ``if`` conditionals to
either ``True`` or ``False``).

This type matches:

* **Builtin booleans** (i.e., instances of the standard :class:`bool` class
  implemented in low-level C).
* **NumPy booleans** (i.e., instances of the :class:`numpy.bool_` class
  implemented in low-level C and Fortran) if :mod:`numpy` is importable.

Usage
----------
Non-standard boolean types like NumPy booleans are typically *not*
interoperable with the standard standard :class:`bool` type. In particular, it
is typically *not* the case, for any variable ``my_bool`` of non-standard
boolean type and truthy value, that either ``my_bool is True`` or ``my_bool ==
True`` yield the desired results. Rather, such variables should *always* be
coerced into the standard :class:`bool` type before being compared -- either:

* Implicitly (e.g., ``if my_bool: pass``).
* Explicitly (e.g., ``if bool(my_bool): pass``).

Caveats
----------
**There exists no abstract base class governing booleans in Python.** Although
various Python Enhancement Proposals (PEPs) were authored on the subject, all
were rejected as of this writing. Instead, this type trivially implements an
ad-hoc abstract base class (ABC) detecting objects satisfying the boolean
protocol via structural subtyping. Although no actual real-world classes
subclass this :mod:`beartype`-specific ABC, the detection implemented by this
ABC suffices to match *all* boolean types. So it goes.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


StrType = str    # Well, isn't that special.
'''
Type of all **unencoded Unicode strings** (i.e., instances of the builtin
:class:`str` class; sequences of abstract Unicode codepoints that have yet to
be encoded into physical encoded bytes in encoded byte strings).

This type matches:

* **Builtin Unicode strings** (i.e., :class:`str` instances).
* **NumPy Unicode strings** (i.e., :class:`numpy.str_` instances) if
  :mod:`numpy` is importable. Whereas most NumPy scalar types do *not* subclass
  builtin scalar types, the :class:`numpy.str_` class *does* subclass the
  builtin :class:`str` type. NumPy Unicode strings are thus usable wherever
  builtin Unicode strings are usable.

Caveats
----------
This type does *not* match **encoded byte strings** (i.e., sequences of
physical encoded bytes, including the builtin :class:`bytestring` type), which
require foreknowledge of the encoding previously used to encode those bytes.
Unencoded Unicode strings require no such foreknowledge and are thus
incompatible with encoded byte strings at the API level.

This type only matches **builtin Unicode strings** (i.e., :class:`str`
instances) and instances of subtypes of that type (e.g., :class:`numpy.str_`,
the NumPy Unicode string type). Whereas the comparable :class:`BoolType`
matches arbitrary objects satisfying the boolean protocol (i.e., ``__bool__()``
dunder method) via structural subtyping, this type does *not* match arbitrary
objects satisfying the string protocol via structural subtyping -- because
there is no string protocol. While Python's data model does define a
``__str__()`` dunder method called to implicitly convert arbitrary objects into
strings, that method is called infrequently. As exhibited by the infamously
rejected `PEP 3140`_ proposal, the :meth:`list.__str__` implementation
stringifies list items by erroneously calling the unrelated ``__repr__()``
method rather than the expected ``__str__()`` method on those items. Moreover,
``__str__()`` fails to cover common string operations such as string
concatenation and repetition. Covering those operations would require a new
abstract base class (ABC) matching arbitrary objects satisfying the
:class:`Sequence` protocol as well as ``__str__()`` via structural subtyping;
while trivial, that ABC would then ambiguously match all builtin sequence types
(e.g., :class:`list`, :class:`tuple`) as string types, which they clearly are
not. In short, matching only :class:`str` is the *only* unambiguous means of
matching Unicode string types.

.. _PEP 3140:
   https://www.python.org/dev/peps/pep-3140
'''

# ....................{ TYPES ~ scalar : number           }....................
NumberType = _numbers.Number
'''
Type of all **numbers** (i.e., concrete instances of the abstract
:class:`numbers.Number` base class).

This type effectively matches *all* numbers regardless of implementation,
including:

* **Integers** (i.e., real numbers expressible without fractional components),
  including:
  * **Builtin integers** (i.e., :class:`int` instances).
  * **NumPy integers** (e.g., :class:`numpy.int_` instances), whose types are
    all implicitly registered at :mod:`numpy` importation time as satisfying
    the :class:`numbers.Integral` protocol.
  * **SymPy integers** (e.g., :class:`sympy.core.numbers.Integer` instances),
    whose type is implicitly registered at :mod:`sympy` importation time as
    satisfying the class:`numbers.Integral` protocol.
* **Rational numbers** (i.e., real numbers expressible as the ratio of two
  integers), including:
  * **Builtin floating-point numbers** (i.e., :class:`float` instances).
  * **NumPy floating-point numbers** (e.g., :class:`numpy.single` instances),
    all of which are implicitly registered at :mod:`numpy` importation time as
    :class:`numbers.Rational` subclasses.
  * **Stdlib fractions** (i.e., :class:`fractions.Fraction` instances).
  * **SymPy floating-point numbers** (e.g., :class:`sympy.core.numbers.Float`
    instances), whose type implicitly registered at :mod:`sympy` importation
    time as satisfying the class:`numbers.Real` protocol.
  * **SymPy rational numbers** (e.g., :class:`sympy.core.numbers.Rational`
    instances), whose type implicitly registered at :mod:`sympy` importation
    time as satisfying the class:`numbers.Rational` protocol.
* **Irrational numbers** (i.e., real numbers *not* expressible as the ratio of
  two integers), including:
  * **SymPy irrational numbers** (i.e., SymPy-specific symbolic objects whose
    ``is_irrational`` assumption evaluates to ``True``).

Caveats
----------
This type does *not* match:

* **Stdlib decimals** (i.e., :class:`decimal.Decimal` instances), which support
  both unrounded decimal (i.e., fixed-point arithmetic) and rounded
  floating-point arithmetic. Despite being strictly rational, the
  :class:`decimal.Decimal` class only subclasses the coarse-grained abstract
  :class:`numbers.Number` base superclass rather than the fine-grained abstract
  :class:`numbers.Rational` base subclass. So it goes.
* **SymPy complex numbers,** which are "non-atomic" (i.e., defined as the
  combination of two separate real and imaginary components rather than as one
  unified complex number containing these components) and thus incommensurable
  with all of the above "atomic" types.
'''


NumberRealType = IntOrFloatType = _numbers.Real
'''
Type of all **real numbers** (i.e., concrete instances of the abstract
:class:`numbers.Real` base class; numbers expressible as linear values on the
real number line).

This type matches all numbers matched by :class:`NumberType` *except* complex
numbers with non-zero imaginary components, which (as the name implies) are
non-real.

Equivalently, this type matches all integers (e.g., :class:`int`,
:class:`numpy.int_`), floating-point numbers (e.g., :class:`float`,
:class:`numpy.single`), rational numbers (e.g., :class:`fractions.Fraction`,
:class:`sympy.core.numbers.Rational`), and irrational numbers. However,
rational and irrational numbers are rarely used in comparison to integers and
floating-point numbers. This type thus reduces to matching all integer and
floating-point types in practice and is thus also accessible under the alias
:class:`IntOrFloatType` -- a less accurate but more readable name than
:class:`NumberRealType`.

See Also
----------
:class:`NumberType`
    Further details.
'''


IntType = _numbers.Integral
'''
Type of all **integers** (i.e., concrete instances of the abstract
:class:`numbers.Integral` base class; real numbers expressible without
fractional components).

This type matches all numbers matched by the :class:`NumberType` *except*
complex numbers with non-zero imaginary components, rational numbers with
denominators not equal to one, and irrational numbers.

Equivalently, this type matches all integers (e.g., :class:`int`,
:class:`numpy.int_`).

See Also
----------
:class:`NumberType`
    Further details.
'''

# ....................{ TYPES ~ stdlib : argparse         }....................
ArgParserType = _ArgumentParser
'''
Type of argument parsers parsing all command-line arguments for either
top-level commands *or* subcommands of those commands.
'''


ArgSubparsersType = _SubParsersAction
'''
Type of argument subparser containers parsing subcommands for parent argument
parsers parsing either top-level commands *or* subcommands of those commands.
'''

# ....................{ TYPES ~ stdlib : re               }....................
# Regular expression types are also sufficiently obscure to warrant
# formalization here.

# Yes, this is the only reliable means of obtaining the type of compiled
# regular expressions. For unknown reasons presumably concerning the archaic
# nature of Python's regular expression support, this type is *NOT* publicly
# exposed. While the private "re._pattern_type" attribute does technically
# provide this type, it does so in a private and hence non-portable manner.
RegexCompiledType = type(_re.compile(r''))
'''
Type of all **compiled regular expressions** (i.e., objects created and
returned by the stdlib :func:`re.compile` function).
'''


# Yes, this type is required for type validation at module scope elsewhere.
# Yes, this is the most time-efficient means of obtaining this type. No, this
# type is *NOT* directly importable. Although this type's classname is
# published to be "_sre.SRE_Match", the "_sre" C extension provides no such
# type for pure-Python importation. So it goes.
RegexMatchType = type(_re.match(r'', ''))
'''
Type of all **regular expression match objects** (i.e., objects returned by the
:func:`re.match` function).
'''

# ....................{ TYPES ~ lib                       }....................
# Types conditionally dependent upon the importability of third-party
# dependencies. These types are subsequently redefined by try-except blocks
# below and initially default to "UnavailableType" for simple types.

# ....................{ TYPES ~ lib : numpy               }....................
# Conditionally redefined by the "TUPLES ~ init" subsection below.
NumpyArrayType = UnavailableType
'''
Type of all **NumPy arrays** (i.e., instances of the concrete
:class:`numpy.ndarray` class implemented in low-level C and Fortran) if
:mod:`numpy` is importable *or* :class:`UnavailableType` otherwise (i.e., if
:mod:`numpy` is unimportable).
'''


# Conditionally redefined by the "TUPLES ~ init" subsection below.
NumpyScalarType = UnavailableType
'''
Type of all **NumPy scalars** (i.e., instances of the abstract
:class:`numpy.generic` base class implemented in low-level C and Fortran) if
:mod:`numpy` is importable *or* :class:`UnavailableType` otherwise (i.e., if
:mod:`numpy` is unimportable).
'''

# ....................{ TUPLES ~ unavailable              }....................
# Unavailable types are defined *BEFORE* any subsequent types, as the latter
# commonly leverage the former.

# Private, as it's unclear whether anyone desperately wants access to this yet.
class _UnavailableTypesTuple(tuple):
    '''
    Type of any **tuple of unavailable types** (i.e., types *not* available
    under the active Python interpreter, typically due to insufficient Python
    version or non-installed third-party dependencies).
    '''

    pass


UnavailableTypes = _UnavailableTypesTuple()
'''
**Tuple of unavailable types** (i.e., types *not* available under the active
Python interpreter, typically due to insufficient Python version or
non-installed third-party dependencies).

Caveats
----------
**This tuple should always be used in lieu of the empty tuple.** Although
technically equivalent to the empty tuple, the :func:`beartype.beartype`
decorator explicitly distinguishes between this tuple and the empty tuple.
Specifically, for any callable parameter or return type annotated with:

* This tuple, :func:`beartype.beartype` emits a non-fatal warning ignorable
  with a simple :mod:`warnings` filter.
* The empty tuple, :func:`beartype.beartype` raises a fatal exception.
'''

# ....................{ TUPLES ~ core                     }....................
NoneTypeOr = _NoneTypeOrType()
'''
**:class:``NoneType`` tuple factory** (i.e., dictionary mapping from arbitrary
types or tuples of types to the same types or tuples of types concatenated with
the type of the ``None`` singleton).

This factory efficiently generates and caches tuples of types containing
:class:``NoneType`` from arbitrary user-specified types and tuples of types. To
do so, simply index this factory with any desired type *or* tuple of types; the
corresponding value will then be another tuple containing :class:``NoneType``
and that type *or* those types.

Motivation
----------
This factory is commonly used to type-hint **optional callable parameters**
(i.e., parameters defaulting to ``None`` when *not* explicitly passed by the
caller). Although such parameters may also be type-hinted with a tuple manually
containing :class:``NoneType``, doing so inefficiently recreates these tuples
for each optional callable parameter across the entire codebase.

This factory avoids such inefficient recreation. Instead, when indexed with any
arbitrary key:

* If that key has already been successfully accessed on this factory, this
  factory returns the existing value (i.e., tuple containing
  :class:``NoneType`` and that key if that key is a type *or* the items of that
  key if that key is a tuple) previously mapped and cached to that key.
* Else, if that key is:

  * A type, this factory:

    #. Creates a new tuple containing that type and :class:``NoneType``.
    #. Associates that key with that tuple.
    #. Returns that tuple.

  * A tuple of types, this factory:

    #. Creates a new tuple containing these types and :class:``NoneType``.
    #. Associates that key with that tuple.
    #. Returns that tuple.

  * Any other object, raises a human-readable
    :class:`beartype.roar.BeartypeCaveNoneTypeOrKeyException` exception.

This factory is analogous to the `PEP 484`_-compliant :class:`typing.Optional`
type despite otherwise *not* complying with `PEP 484`_.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484

Examples
----------
Function accepting an optional parameter with neither :mod:`beartype.cave` nor
:mod:`typing`:

    >>> def to_autumn(season_of_mists: (str, type(None)) = None) -> str
    ...     return season_of_mists if season_of_mists is not None else (
    ...         'While barred clouds bloom the soft-dying day,')

Function accepting an optional parameter with :mod:`beartype.cave`:

    >>> from beartype.cave import NoneTypeOr
    >>> def to_autumn(season_of_mists: NoneTypeOr[str] = None) -> str
    ...     return season_of_mists if season_of_mists is not None else (
    ...         'Then in a wailful choir the small gnats mourn')

Function accepting an optional parameter with :mod:`typing`:

    >>> from typing import Optional
    >>> def to_autumn(season_of_mists: Optional[str] = None) -> str
    ...     return season_of_mists if season_of_mists is not None else (
    ...         'Or sinking as the light wind lives or dies;')
'''

# ....................{ TUPLES ~ py                       }....................
ModuleOrStrTypes = (ModuleType, StrType)
'''
Tuple of both the module *and* string type.
'''


TestableTypes = (ClassType, tuple)
'''
Tuple of all **testable types** (i.e., types suitable for use as the second
parameter passed to the :func:`isinstance` and :func:`issubclass` builtins).
'''

# ....................{ TUPLES ~ call                     }....................
FunctionTypes = (FunctionType, FunctionOrMethodCType,)
'''
Tuple of all **function types** (i.e., types whose instances are either
built-in or user-defined functions).

Caveats
----------
**This tuple may yield false positives when used to validate types.** Since
Python fails to distinguish between C-based functions and methods, this tuple
is the set of all function types as well as the ambiguous type of all C-based
functions and methods.
'''

# ....................{ TUPLES ~ call : method            }....................
MethodBoundTypes = (
    MethodBoundInstanceOrClassType, MethodBoundInstanceDunderCType)
'''
Tuple of all **bound method types** (i.e., types whose instances are callable
objects bound to either instances or classes).
'''


MethodUnboundTypes = (
    MethodUnboundClassCType,
    MethodUnboundInstanceDunderCType,
    MethodUnboundInstanceNondunderCType,
)
'''
Tuple of all **unbound method types** (i.e., types whose instances are callable
objects bound to neither instances nor classes)

Unbound decorator objects (e.g., non-callable instances of the builtin
:class:`classmethod`, :class:`property`, or :class:`staticmethod` decorator
classes) are *not* callable and thus intentionally excluded.
'''


MethodDecoratorBuiltinTypes = (
    MethodDecoratorClassType,
    MethodDecoratorPropertyType,
    MethodDecoratorStaticType,
)
'''
Tuple of all **C-based unbound method decorator objects** (i.e., non-callable
instances of a builtin decorator class implemented in low-level C, associated
with methods implemented in pure Python)
'''


MethodTypes = (FunctionOrMethodCType,) + MethodBoundTypes + MethodUnboundTypes
'''
Tuple of all **method types** (i.e., types whose instances are callable objects
associated with methods implemented in either low-level C or pure Python).

Unbound decorator objects (e.g., non-callable instances of the builtin
:class:`classmethod`, :class:`property`, or :class:`staticmethod` decorator
classes) are *not* callable and thus intentionally excluded.

Caveats
----------
**This tuple may yield false positives when used to validate types.** Since
Python fails to distinguish between C-based functions and methods, this tuple
is the set of all pure-Python bound and unbound method types as well as the
ambiguous type of all C-based bound methods and non-method functions.
'''

# ....................{ TUPLES ~ call : callable          }....................
# For DRY, this tuple is defined as the set union of all function and method
# types defined above converted back to a tuple.
#
# While this tuple could also be defined as the simple concatenation of the
# "FunctionTypes" and "MethodTypes" tuples, doing so would duplicate all types
# ambiguously residing in both tuples (i.e., "FunctionOrMethodCType"). Doing so
# would induce inefficiencies during type checking. That would be bad.
CallableTypes = tuple(set(FunctionTypes) | set(MethodTypes))
'''
Tuple of all **callable types** (i.e., types whose instances are callable
objects, including both built-in and user-defined functions, lambdas, methods,
and method descriptors).
'''


CallableOrStrTypes = CallableTypes + (StrType,)
'''
Tuple of all callable types as well as the string type.
'''


#FIXME: Define a new "CallableClassType" by copying the "BoolType" approach
#except for the __call__() dunder method instead.
#FIXME: Replace "ClassType" below by "CallableClassType".
#FIXME: Add the "CallableClassType" type to the "CallableTypes" tuple as well.
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

# ....................{ TUPLES ~ call : return            }....................
AsyncCTypes = (AsyncGeneratorCType, AsyncCoroutineCType)
'''
Tuple of all C-based types returned by all **asynchronous callables** (i.e.,
callables implemented in pure Python whose declaration is preceded by the
``async`` keyword).
'''

# ....................{ TUPLES ~ call : weakref           }....................
WeakRefProxyCTypes = _ProxyTypes
'''
Tuple of all **C-based weak reference proxy classes** (i.e., classes
implemented in low-level C whose instances are weak references to other
instances masquerading as those instances).

This tuple contains classes matching both callable and uncallable weak
reference proxies.
'''

# ....................{ TUPLES ~ scalar                   }....................
BoolOrNumberTypes = (BoolType, NumberType,)
'''
Tuple of all **boolean** and **number types** (i.e., classes whose instances
are either numbers or types trivially convertible into numbers).

This tuple matches booleans, integers, rational numbers, irrational numbers,
real numbers, and complex numbers.

Booleans are trivially convertible into integers. While details differ by
implementation, common implementations in lower-level languages (e.g., C, C++,
Perl) typically implicitly convert:

* ``False`` to ``0`` and vice versa.
* ``True`` to ``1`` and vice versa.
'''

# ....................{ TUPLES ~ version                  }....................
# Conditionally expanded by the "TUPLES ~ init" subsection below.
VersionComparableTypes = (tuple,)
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
:class:`SetuptoolsVersionTypes` tuple do *not* necessarily support direct
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
SequenceOrNumpyArrayTypes = (SequenceType,)
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
SequenceMutableOrNumpyArrayTypes = (SequenceMutableType,)
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
SetuptoolsVersionTypes = UnavailableTypes
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
    import numpy as _numpy

    # Define NumPy-specific types.
    NumpyArrayType  = _numpy.ndarray
    NumpyScalarType = _numpy.generic

    # Extend NumPy-agnostic types with NumPy-specific types.
    SequenceOrNumpyArrayTypes        += (NumpyArrayType,)
    SequenceMutableOrNumpyArrayTypes += (NumpyArrayType,)
# Else, NumPy is unimportable. We're done here, folks.
except:
    pass


# If setuptools is importable, conditionally define setuptools-specific types.
try:
    import pkg_resources as _pkg_resources

    # Define setuptools-specific types.
    SetuptoolsVersionTypes = (
        _pkg_resources.packaging.version.Version,
        _pkg_resources.packaging.version.LegacyVersion,
    )
    VersionComparableTypes += SetuptoolsVersionTypes
# Else, setuptools is unimportable. While this should typically *NEVER* be the
# case, edge cases gonna edge case.
except:
    pass

# ....................{ TUPLES ~ post-init : container    }....................
# Tuples of types assuming the above initialization to have been performed.

MappingOrSequenceTypes = (MappingType, SequenceType)
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`collections.abc.Mapping` *or*
:class:`collections.abc.Sequence` APIs.
'''


ModuleOrSequenceTypes = (ModuleType, SequenceType)
'''
Tuple of the module type *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Sequence`
API.
'''


NumberOrIterableTypes = (NumberType, IterableType,)
'''
Tuple of all numeric types *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Iterable`
API.
'''


NumberOrSequenceTypes = (NumberType, SequenceType,)
'''
Tuple of all numeric types *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Sequence`
API.
'''

# ....................{ TUPLES ~ post-init : scalar       }....................
ScalarTypes = BoolOrNumberTypes + (StrType,)
'''
Tuple of all **scalar types** (i.e., classes whose instances are atomic scalar
primitives).

This tuple matches all:

* **Boolean types** (i.e., types satisfying the :class:`BoolType` protocol).
* **Numeric types** (i.e., types satisfying the :class:`NumberType` protocol).
* **Textual types** (i.e., types contained in the :class:`StrTypes` tuple).
'''

# ....................{ TUPLES ~ stdlib                   }....................
RegexTypes = (RegexCompiledType, StrType)
'''
Tuple of all **regular expression-like types** (i.e., types either defining
regular expressions or losslessly convertible to such types).

This tuple matches:

* The **compiled regular expression type** (i.e., type of all objects created
  and returned by the stdlib :func:`re.compile` function).
* All **textual types** (i.e., types contained in the :class:`StrTypes`
  tuple).
'''

# ....................{ TUPLES ~ post-init : version      }....................
VersionTypes = (StrType,) + VersionComparableTypes
'''
Tuple of all **version types** (i.e., types suitable for use as parameters to
callables accepting arbitrary version specifiers) if :mod:`pkg_resources` is
importable *or* ``(StrType, tuple,)`` otherwise.

This includes:

* :class:`StrType`, specifying versions in ``.``-delimited positive integer
  format (e.g., ``2.4.14.2.1.356.23``).
* :class:`tuple`, specifying versions as one or more positive integers (e.g.,
  ``(2, 4, 14, 2, 1, 356, 23)``),
* :class:`SetuptoolsVersionTypes`, whose :mod:`setuptools`-specific types
  specify versions as instance variables convertible into both of the prior
  formats (e.g., ``SetuptoolsVersionTypes[0]('2.4.14.2.1.356.23')``).
'''
