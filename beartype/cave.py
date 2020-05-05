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
#FIXME: Add types for all remaining useful "collections.abc" interfaces,
#including:
#* "Collection".
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
**Many types not commonly thought of as functions are ambiguously implemented
as functions in Python.** This includes:

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
:data:`MethodBoundInstanceOrClassType`
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
There exists *no* corresponding :data:`MethodUnboundInstanceType` type, as
unbound pure-Python instance methods are ambiguously implemented as functions
of type :data:`FunctionType` indistinguishable from conventional functions.
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
:data:`MethodUnboundInstanceDunderCType`
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
:data:`MethodBoundInstanceDunderCType`
    Type of all C-based unbound dunder method wrappers.
:data:`MethodUnboundInstanceNondunderCType`
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
:data:`MethodUnboundInstanceDunderCType`
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
:data:`MethodBoundInstanceOrClassType` type.

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
attributes, static methods are instances of the standard :data:`FunctionType`
type.

Static method objects are *not* callable, as their implementations fail to
define the ``__call__`` dunder method.
'''

# ....................{ TYPES ~ call : return : async     }....................
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
pure-Python :class:`weakref.WeakMethod` class.
'''

# ....................{ TYPES ~ contain                   }....................
IterableType = _Iterable
'''
Type of all **iterables** (i.e., concrete instances of the abstract
:class:`collections.abc.Iterable` base class).

Iterables are containers that may be indirectly iterated over by calling the
builtin :func:`iter` function, which internally calls the ``__iter__`` dunder
methods implemented by these containers, which return **iterators** (i.e.,
instances of the :data:`IteratorType` type), which directly support iteration.

**Iterables are the most important container type.** They're sufficiently
important, in fact, that the builtin :func:`isinstance` and :func:`issubclass`
functions (which the :func:`beartype.beartype` decorator internally defers to)
intentionally misidentify types declaring ``__iter__`` dunder methods *not*
subclassing the abstract :class:`collections.abc.Iterable` base class as
subclassing the abstract :class:`collections.abc.Iterable` base class:

.. code-block:: python

   >>> from collections.abc import Iterable
   >>> class FakeIterable(object):
   ...     def __iter__(self): return iter([0x1337C0D3, 0x1337BABE])
   >>> FakeIterable.__mro__
   ... (FakeIterable, object)
   >>> isinstance(FakeIterable(), Iterable)
   True
   >>> issubclass(FakeIterable, Iterable)
   True

Yes, Python violates the "explicit is better than implicit" maxim of `PEP 20
("The Zen of Python") <PEP 20_>`__ by intentionally deceiving you for your own
benefit, which you of course appreciate. That's how important iterables are.

.. _PEP 20:
   https://www.python.org/dev/peps/pep-0020

See Also
----------
:class:`IteratorType`
    Further details.
'''


IteratorType = _Iterator
'''
Type of all **iterators** (i.e., concrete instances of the abstract
:class:`collections.abc.Iterator` base class, which typically iterate over
associated container objects).

Iterators implement at least two dunder methods:

* ``__next__``, iteratively returning successive items from associated data
  streams (e.g., container objects) until throwing standard
  :data:`StopIteration` exceptions on reaching the ends of those streams.
* ``__iter__``, returning themselves. Since iterables (i.e., instances of the
  :data:`IterableType` type) are *only* required to implement the ``__iter__``
  dunder method, all iterators are by definition iterables as well.

See Also
----------
:class:`IterableType`
    Further details.
'''


QueueType = _deque
'''
Type of all **double-ended queues** (i.e., instances of the concrete
:class:`collections.deque` class), the only queue type implemented within the
Python stdlib.

Caveats
----------
The :mod:`collections.abc` subpackage currently provides no corresponding
abstract interface to formalize queue types. Double-ended queues are it, sadly.
'''


SetType = _Set
'''
Type of all **set-like containers** (i.e., concrete instances of the abstract
:class:`collections.abc.Set` base class, which are containers guaranteeing
uniqueness across all contained items).

This type matches both the standard :class:`set` and :class:`frozenset` types
*and* the types of the :class:`dict`-specific views returned by the
:meth:`dict.items` and :meth:`dict.keys` (but *not* :meth:`dict.values`)
methods.
'''


SizedType = _Sized
'''
Type of all **sized containers** (i.e., concrete instances of the abstract
:class:`collections.abc.Sized` base class, which are containers defining the
dunder ``__len__()`` method internally called by the :func:`len` builtin).
'''

# ....................{ TYPES ~ contain : mapping         }....................
HashableType = _Hashable
'''
Type of all **hashable objects** (i.e., concrete instances of the abstract
:class:`collections.abc.Hashable` base class, which are objects implementing
the dunder ``__hash__()`` method required for all dictionary keys and set
items).
'''


MappingType = _Mapping
'''
Type of all **mutable and immutable mappings** (i.e., concrete instances of the
abstract :class:`collections.abc.Mapping` base class, which are dictionary-like
containers containing key-value pairs mapping from hashable keys to
corresponding values).

Caveats
----------
**This type does not guarantee mutability** (i.e., the capacity to modify
instances of this type after instantiation). This type ambiguously matches both
mutable mapping types (e.g., :class:`dict`) and immutable mapping types (e.g.,
:class:`mappingproxy`). If mutability is required, prefer the non-ambiguous
:data:`MappingMutableType` type instead.
'''


MappingMutableType = _MutableMapping
'''
Type of all **mutable mappings** (i.e., concrete instances of the abstract
:class:`collections.abc.MutableMapping` base class, which are dictionary-like
containers containing key-value pairs mapping from hashable keys to
corresponding values that also permit modification of those pairs).

See Also
----------
:data:`MappingType`
    Type of all mutable and immutable mappings.
'''

# ....................{ TYPES ~ enum                      }....................
# Enumeration types are sufficiently obscure to warrant formalization here.

EnumType = _EnumMeta
'''
Metaclass of all **enumeration types** (i.e., classes containing all
enumeration members comprising those enumerations).

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

Yes, this is insane. Yes, this is Python.
'''


EnumClassType = _Enum
'''
Abstract base class of all **enumeration types** (i.e., classes containing all
enumeration members comprising those enumerations).

See Also
----------
:class:`EnumType`
    Further details.
'''


EnumMemberType = _Enum
'''
Abstract base class implemented by all **enumeration members** (i.e.,
alternative choices comprising their parent enumerations).

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


TestableTypes = (ClassType, tuple)
'''
Tuple of all **testable types** (i.e., types suitable for use as the second
parameter passed to the :func:`isinstance` and :func:`issubclass` builtins).
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
# ambiguously residing in both tuples (i.e., "FunctionOrMethodCType"). Doing so would
# induce inefficiencies during type checking, which would be awfully bad.
CallableTypes = tuple(set(FunctionTypes) | set(MethodTypes))
'''
Tuple of all **callable types** (i.e., types whose instances are callable
objects, including both built-in and user-defined functions, lambdas, methods,
and method descriptors).
'''


CallableOrStrTypes = CallableTypes + (str,)
'''
Tuple of all callable types as well as the string type.
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


#FIXME: Docstring and test us up.
SequenceMutableTypes = (_MutableSequence,)

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

# ....................{ TUPLES ~ stdlib                   }....................
RegexTypes = (str, RegexCompiledType)
'''
Tuple of all **regular expression-like types** (i.e., types either defining
regular expressions or losslessly convertible to such types).
'''

# ....................{ TUPLES ~ lib                      }....................
# Types conditionally dependent upon the importability of third-party
# dependencies. These types are subsequently redefined by try-except blocks
# below and initially default to either:
#
# * "UnavailableType" for simple types.
# * "UnavailableTypes" for tuples of simple types.

# ....................{ TUPLES ~ lib : numpy              }....................
# Defined by the "TUPLES ~ init" subsection below.
NumpyArrayType = UnavailableType
'''
Type of all NumPy arrays if :mod:`numpy` is importable *or*
:data:`UnavailableType` otherwise (i.e., if :mod:`numpy` is unimportable).
'''


# Defined by the "TUPLES ~ init" subsection below.
NumpyScalarType = UnavailableType
'''
Superclass of all NumPy scalar subclasses (e.g., :class:`numpy.bool_`) if
:mod:`numpy` is importable *or* :data:`UnavailableType` otherwise (i.e., if
:mod:`numpy` is unimportable).
'''


# Defined by the "TUPLES ~ init" subsection below.
NumpyDataTypes = UnavailableTypes
'''
Tuple of the **NumPy data type** (i.e., NumPy-specific numeric scalar type
homogeneously constraining all elements of all NumPy arrays) and all scalar
Python types transparently supported by NumPy as implicit data types (i.e.,
:class:`bool`, :class:`complex`, :class:`float`, and :class:`int`) if
:mod:`numpy` is importable *or* :data:`UnavailableTypes` otherwise.
'''

# ....................{ TUPLES ~ lib : setuptools         }....................
# Defined by the "TUPLES ~ init" subsection below.
DistributionSetuptoolsOrNoneTypes = UnavailableTypes
'''
Tuple of the type of all :mod:`setuptools`-specific package metadata objects
as well as the ``None`` singleton if :mod:`pkg_resources` is importable *or*
:data:`UnavailableTypes` otherwise.
'''


# Defined by the "TUPLES ~ init" subsection below.
VersionSetuptoolsTypes = UnavailableTypes
'''
Tuple of all :mod:`setuptools`-specific version types (i.e., types instantiated
and returned by the stable :func:`pkg_resources.parse_version` function bundled
with :mod:`setuptools`) if :mod:`pkg_resources` is importable *or*
:data:`UnavailableTypes` otherwise.

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


NumericOrIterableTypes = NumericSimpleTypes + (IterableType,)
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
IterableOrNoneTypes = (IterableType, NoneType)
'''
Tuple of all container base classes conforming to (but _not_ necessarily
subclassing) the canonical :class:`_Iterable` API as well as the type of the
``None`` singleton.
'''


MappingOrNoneTypes = (MappingType, NoneTypes)
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
