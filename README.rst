.. # ------------------( SEO                                )------------------
.. # Metadata converted into HTML-specific meta tags parsed by search engines.
.. # Note that:
.. # * The "description" should be no more than 300 characters and ideally no
.. #   more than 150 characters, as search engines may silently truncate this
.. #   description to 150 characters in edge cases.

.. meta::
   :description lang=en:
     Beartype is an open-source pure-Python PEP-compliant constant-time runtime
     type checker emphasizing efficiency and portability.

.. # ------------------( SYNOPSIS                           )------------------

===============
|beartype-logo|
===============
—[ the bare-metal type checker ]—

|GitHub Actions badge|

.. parsed-literal::

   Look for the bare necessities,
     the simple bare necessities.
   Forget about your worries and your strife.

                           — `The Jungle Book`_.

**Beartype** is an open-source pure-Python `PEP-compliant <Compliance_>`__
`constant-time <Timings_>`__ `runtime type checker <Usage_>`__ emphasizing
efficiency, portability, and thrilling puns.

Beartype brings Rust_- and `C++`_-inspired `zero-cost abstractions <zero-cost
abstraction_>`__ into the lawless world of dynamically-typed Python by
`enforcing type safety at the granular level of functions and methods
<Usage_>`__ against `type hints standardized by the Python community
<Compliance_>`__ in `O(1) non-amortized worst-case time with negligible
constant factors <Timings_>`__.

Beartype is `portably implemented <codebase_>`__ in `Python 3 <Python_>`__,
`continuously stress-tested <tests_>`__ via `GitHub Actions`_ **+** tox_ **+**
pytest_, and `permissively distributed <beartype license_>`__ under the `MIT
license`_. Beartype has *no* runtime dependencies, `only one test-time
dependency <pytest_>`__, and `only one documentation-time dependency
<Sphinx_>`__. Beartype supports `all actively developed Python versions
<Python status_>`__, `all Python package managers <Install_>`__, and `multiple
platform-specific package managers <Install_>`__.

.. # Ideally, this heading would actually be formatted as a proper heading
.. # (e.g., underlined by "=" characters). Since doing so causes the table of
.. # contents that follows to be silently ignored, we fallback to a simple
.. # block quote -- which technically suffices but is rather lame. So it goes!

.. topic:: **tl;dr:**
    
   #. `Install beartype <Install_>`__:
   
      .. code-block:: shell-session
      
         pip3 install beartype
   
   #. `Decorate functions and methods annotated by PEP-compliant type hints with
      the @beartype.beartype decorator <Usage_>`__:
   
      .. code-block:: python
   
         from beartype import beartype
         from collections.abc import Iterable
         from typing import Optional
   
         @beartype
         def print_messages(messages: Optional[Iterable[str]] = ('Hello, world.',)):
             print('\n'.join(messages))
   
   Quality assurance has now been assured.

.. # ------------------( TABLE OF CONTENTS                  )------------------
.. # Blank line. By default, Docutils appears to only separate the subsequent
.. # table of contents heading from the prior paragraph by less than a single
.. # blank line, hampering this table's readability and aesthetic comeliness.

|

.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Contents**
   :local:

.. # ------------------( DESCRIPTION                        )------------------

News
====

Beartype has a `roadmap forward to our first major milestone <beartype
1.0.0_>`__: **beartype 1.0.0,** delivering perfect constant-time compliance
with all annotation standards by late 2021. :sup:`...in theory`

Join `the strangely enticing conversation <beartype 1.0.0_>`__ and be a part of
the spicy runtime type-checker that `goes up to eleven`_.

Install
=======

Let's install ``beartype`` with pip_, because community standards are good:

.. code-block:: shell-session

   pip3 install beartype

Let's install ``beartype`` with Anaconda_, because corporate standards are
(occasionally) good too:

.. code-block:: shell-session

   conda config --add channels conda-forge
   conda install beartype

macOS
-----

Let's install ``beartype`` with MacPorts_ on macOS_, because HomeBrew_ `hates
packaging Python packages <HomeBrew Python packaging_>`__, because they
secretly want you to use MacPorts_ instead – which you should do:

.. code-block:: shell-session

   sudo port install py-beartype

Thanks to `MacPorts maintainer @harens <harens_>`__ for `packaging beartype for
our macOS audience <beartype MacPorts_>`__!

Linux
-----

Let's install ``beartype`` with ``emerge`` on Gentoo_, because source-based
Linux distributions are the CPU-bound nuclear option:

.. code-block:: shell-session

   emerge --ask app-eselect/eselect-repository
   mkdir -p /etc/portage/repos.conf
   eselect repository enable raiagent
   emerge --sync raiagent
   emerge beartype

Overview
========

Beartype is a novel first line of defense. In Python's vast arsenal of
`software quality assurance (SQA) <SQA_>`__, beartype holds the `shield wall`_
against breaches in type safety by improper parameter and return values
violating developer expectations.

Beartype is unopinionated. Beartype inflicts *no* developer constraints
beyond `importation and usage of a single configuration-free decorator
<Cheatsheet_>`__. Beartype is trivially integrated into new and existing
applications, stacks, modules, and scripts already annotating callables with
`PEP-compliant industry-standard type hints <Compliance_>`__.

Beartype is zero-cost. Beartype inflicts *no* harmful developer tradeoffs,
instead stressing expense-free strategies at both:

* **Installation time.** Beartype has no install-time or runtime dependencies,
  `supports standard Python package managers <Install_>`__, and happily
  coexists with competing static type checkers and other runtime type checkers.
* **Runtime.** Thanks to aggressive memoization and dynamic code generation at
  decoration time, beartype guarantees `O(1) non-amortized worst-case runtime
  complexity with negligible constant factors <Timings_>`__.

Versus Static Type Checkers
---------------------------

Like `competing static type checkers <See Also_>`__ operating at the
coarse-grained application level via ad-hoc heuristic type inference (e.g.,
Pyre_, mypy_, pyright_, pytype_), beartype effectively `imposes no runtime
overhead <Timings_>`__. Unlike static type checkers:

* Beartype operates exclusively at the fine-grained callable level of
  pure-Python functions and methods via the standard decorator design pattern.
  This renders beartype natively compatible with *all* interpreters and
  compilers targeting the Python language – including PyPy_, Numba_, Nuitka_,
  and (wait for it) CPython_ itself.
* Beartype enjoys deterministic Turing-complete access to the actual callables,
  objects, and types being type-checked. This enables beartype to solve dynamic
  problems decidable only at runtime – including type-checking of arbitrary
  objects whose:

  * Metaclasses `dynamically customize instance and subclass checks
    <_isinstancecheck>`__ by implementing the ``__instancecheck__()`` and/or
    ``__subclasscheck__()`` dunder methods, including:

    * `PEP 3119`_-compliant metaclasses (e.g., `abc.ABCMeta`_).

  * Pseudo-superclasses `dynamically customize the method resolution order
    (MRO) of subclasses <_mro_entries>`__ by implementing the
    ``__mro_entries__()`` dunder method, including:

    * `PEP 560`_-compliant pseudo-superclasses.

  * Classes dynamically register themselves with standard abstract base classes
    (ABCs), including:

    * `PEP 3119`_-compliant third-party virtual base classes.
    * `PEP 3141`_-compliant third-party virtual number classes (e.g., SymPy_).

  * Classes are dynamically constructed or altered, including by:

    * Class decorators.
    * Class factory functions and methods.
    * Metaclasses.
    * Monkey patches.

Versus Runtime Type Checkers
----------------------------

Unlike `comparable runtime type checkers <See Also_>`__ (e.g., enforce_,
pytypes_, typeguard_), beartype decorates callables with dynamically generated
wrappers efficiently type-checking each parameter passed to and value returned
from those callables in constant time. Since "performance by default" is our
first-class concern, generated wrappers are guaranteed to:

* Exhibit `O(1) non-amortized worst-case time complexity with negligible
  constant factors <Timings_>`__.
* Be either more efficient (in the common case) or exactly as efficient minus
  the cost of an additional stack frame (in the worst case) as equivalent
  type-checking implemented by hand, *which no one should ever do.*

Usage
=====

Beartype makes type-checking painless, portable, and transparent. Just:

    Decorate functions and methods annotated by `standard type hints <PEP
    484_>`__ with the ``@beartype.beartype`` decorator, which wraps those
    functions and methods in performant type-checking dynamically generated
    on-the-fly.

Toy Example
-----------

Let's see what that looks like for a "Hello, Jungle!" toy example. Just:

#. Import the ``@beartype.beartype`` decorator:

   .. code-block:: python

      from beartype import beartype

#. Decorate any annotated function with that decorator:

   .. code-block:: python

      from sys import stderr, stdout
      from typing import TextIO

      @beartype
      def hello_jungle(
          sep: str = ' ',
          end: str = '\n',
          file: TextIO = stdout,
          flush: bool = False,
      ):
          '''
          Print "Hello, Jungle!" to a stream, or to sys.stdout by default.

          Optional keyword arguments:
          file:  a file-like object (stream); defaults to the current sys.stdout.
          sep:   string inserted between values, default a space.
          end:   string appended after the last value, default a newline.
          flush: whether to forcibly flush the stream.
          '''

          print('Hello, Jungle!', sep, end, file, flush)

#. Call that function with valid parameters and relish as things work:

   .. code-block:: python

      >>> hello_jungle(sep='...ROOOAR!!!!', end='uhoh.', file=stderr, flush=True)
      Hello, Jungle! ...ROOOAR!!!! uhoh.

#. Call that function with invalid parameters and cringe as things blow up with
   human-readable exceptions exhibiting the single cause of failure:

   .. code-block:: python

      >>> hello_jungle(sep=(
      ...     b"What? Haven't you ever seen a byte-string separator before?"))
      BeartypeCallHintPepParamException: @beartyped hello_jungle() parameter
      sep="b"What? Haven't you ever seen a byte-string separator before?""
      violates type hint <class 'str'>, as value b"What? Haven't you ever seen
      a byte-string separator before?" not str.

Industrial Example
------------------

Let's wrap the `third-party numpy.empty_like() function <numpy.empty_like_>`__
with automated runtime type checking to demonstrate beartype's support for
non-trivial combinations of nested type hints compliant with different PEPs:

   .. code-block:: python

      from beartype import beartype
      from collections.abc import Sequence
      from numpy import dtype, empty_like, ndarray
      from typing import Optional, Union

      @beartype
      def empty_like_bear(
          prototype: object,
          dtype: Optional[dtype] = None,
          order: str = 'K',
          subok: bool = True,
          shape: Optional[Union[int, Sequence[int]]] = None,
      ) -> ndarray:
          return empty_like(prototype, dtype, order, subok, shape)

Note the non-trivial hint for the optional ``shape`` parameter, synthesized
from a `PEP 484-compliant optional <typing.Optional_>`__ of a `PEP
484-compliant union <typing.Union_>`__ of a builtin type and a `PEP
585-compliant subscripted abstract base class (ABC)
<collections.abc.Sequence_>`__, accepting as valid either:

* The ``None`` singleton.
* An integer.
* A sequence of integers.

Let's call that wrapper with both valid and invalid parameters:

   .. code-block:: python

      >>> empty_like_bear(([1,2,3], [4,5,6]), shape=(2, 2))
      array([[94447336794963,              0],
             [             7,             -1]])
      >>> empty_like_bear(([1,2,3], [4,5,6]), shape=([2], [2]))
      BeartypeCallHintPepParamException: @beartyped empty_like_bear() parameter
      shape=([2], [2]) violates type hint
      typing.Union[int, collections.abc.Sequence, NoneType], as ([2], [2]):
      * Not <class "builtins.NoneType"> or int.
      * Tuple item 0 value [2] not int.

Note the human-readable message of the raised exception, containing a bulleted
list enumerating the various ways this invalid parameter fails to satisfy its
type hint, including the types and indices of the first container item failing
to satisfy the nested ``Sequence[int]`` hint.

See the `"Decoration" section <Decoration_>`__ for actual code dynamically
generated by beartype for real-world use cases resembling those above. Fun!

Would You Like to Know More?
----------------------------

If you know `type hints <PEP 484_>`__, you know beartype. Since beartype is
driven entirely by `tool-agnostic community standards <PEP 0_>`__, beartype's
public API is simply the summation of those standards. As the end user, all you
need to know is that decorated callables magically begin raising human-readable
exceptions when you pass parameter or return values that violate the
PEP-compliant type hints annotating those parameter or return values.

If you don't know `type hints <PEP 484_>`__, this is your moment to go deep on
the hardest hammer in Python's SQA_ toolbox. Here are a few friendly primers to
guide you on your maiden voyage through the misty archipelagos of type hinting:

* `"Python Type Checking (Guide)" <RealPython_>`__, a comprehensive third-party
  introduction to the subject. Like most existing articles, this guide predates
  `O(1)` runtime type checkers and thus discusses only static type checking.
  Thankfully, the underlying syntax and semantics cleanly translate to runtime
  type checking.
* `"PEP 484 -- Type Hints" <PEP 484_>`__, the defining standard, holy grail,
  and first testament of type hinting `personally authored by Python's former
  Benevolent Dictator for Life (BDFL) himself, Guido van Rossum <Guido van
  Rossum_>`__. Since it's surprisingly approachable and covers all the core
  conceits in detail, we recommend reading at least a few sections of interest.
  Since it's really a doctoral thesis by another name, we can't recommend
  reading it in entirety. *So it goes.*

.. #FIXME: Concatenate the prior list item with this when I am no exhausted.
.. #  Instead, here's the highlights reel:
.. #
.. #  * `typing.Union`_, enabling .

Onward to the cheats!

Cheatsheet
==========

Let's type-check like `greased lightning`_:

.. code-block:: python

   # Import the core @beartype decorator.
   from beartype import beartype

   # Import PEP 593-compliant type hints. Note this requires Python ≥ 3.9.
   from typing import Annotated

   # Import PEP 585-compliant type hints. Note this requires Python ≥ 3.9.
   from collections.abc import (
       Callable, Generator, Iterable, MutableSequence, Sequence)

   # Import PEP 544-compliant type hints. Note this requires Python ≥ 3.8.
   from typing import Protocol, runtime_checkable

   # Import PEP 484-compliant type hints, too. Note that many of these types
   # have been deprecated by PEP 585-compliant type hints under Python ≥ 3.9,
   # where @beartype emits non-fatal deprecation warnings at decoration time.
   # See also: https://docs.python.org/3/library/typing.html
   from typing import Any, List, Optional, Tuple, TypeVar, Union

   # Import beartype-specific types to annotate callables with, too.
   from beartype.cave import (
       NoneType, NoneTypeOr, RegexTypes, ScalarTypes, VersionTypes)

   # Import standard abstract base classes (ABCs) for use with @beartype, too.
   from numbers import Integral, Real

   # Import user-defined classes for use with @beartype, too.
   from my_package.my_module import MyClass

   # User-defined PEP 544-compliant protocol referenced below in type hints.
   # Note this requires Python ≥ 3.8 and that protocols *MUST* be explicitly
   # decorated by the @runtime_checkable decorator to be usable with @beartype.
   @runtime_checkable
   class MyProtocol(Protocol):
       def my_method(self) -> str:
           return (
               'Objects satisfy this protocol only if their '
               'classes define a method with the same signature as this method.'
           )

   # User-defined PEP 484-compliant type variable. Note that @beartype currently
   # ignores type variables, but that @beartype 0.9.0 is expected to fully
   # support type variables. See also: https://github.com/beartype/beartype/issues/7
   T = TypeVar('T')

   # Decorate functions with @beartype and...
   @beartype
   def my_function(
       # Annotate builtin types as is.
       param_must_satisfy_builtin_type: str,

       # Annotate user-defined classes as is, too. Note this covariantly
       # matches all instances of both this class and subclasses of this class.
       param_must_satisfy_user_type: MyClass,

       # Annotate PEP 593-compliant types, indexed by a type checked by
       # @beartype followed by arbitrary objects ignored by @beartype.
       param_must_satisfy_pep593: Annotated[dict[int, bool], range(5), True],

       # Annotate PEP 585-compliant builtin container types, indexed by the
       # types of items these containers are required to contain.
       param_must_satisfy_pep585_builtin: list[str],

       # Annotate PEP 585-compliant standard collection types, indexed too.
       param_must_satisfy_pep585_collection: MutableSequence[str],

       # Annotate PEP 544-compliant protocols, either unindexed or indexed by
       # one or more type variables.
       param_must_satisfy_pep544: MyProtocol[T],

       # Annotate PEP 484-compliant non-standard container types defined by the
       # "typing" module, optionally indexed and only usable as type hints.
       # Note that these types have all been deprecated by PEP 585 under Python
       # ≥ 3.9. See also: https://docs.python.org/3/library/typing.html
       param_must_satisfy_pep484_typing: List[int],

       # Annotate PEP 484-compliant unions of arbitrary types, including
       # builtin types, type variables, and PEP 585-compliant type hints.
       param_must_satisfy_pep484_union: Union[dict, T, tuple[MyClass, ...]],

       # Annotate PEP 484-compliant relative forward references dynamically
       # resolved at call time as unqualified classnames relative to the
       # current user-defined submodule. Note this class is defined below and
       # that beartype-specific absolute forward references are also supported.
       param_must_satisfy_pep484_relative_forward_ref: 'MyOtherClass',

       # Annotate PEP-compliant types indexed by similar references. Note that
       # forward references are supported everywhere standard types are.
       param_must_satisfy_pep484_hint_relative_forward_ref: (
           Union['MyPep484Generic', set['MyPep585Generic']]),

       # Annotate beartype-specific types predefined by the beartype cave.
       param_must_satisfy_beartype_type_from_cave: NoneType,

       # Annotate beartype-specific unions of types as tuples.
       param_must_satisfy_beartype_union: (dict, MyClass, int),

       # Annotate beartype-specific unions predefined by the beartype cave.
       param_must_satisfy_beartype_union_from_cave: ScalarTypes,

       # Annotate beartype-specific unions concatenated together.
       param_must_satisfy_beartype_union_concatenated: (Iterator,) + ScalarTypes,

       # Annotate beartype-specific absolute forward references dynamically
       # resolved at call time as fully-qualified "."-delimited classnames.
       param_must_satisfy_beartype_absolute_forward_ref: (
           'my_package.my_module.MyClass'),

       # Annotate beartype-specific forward references in unions of types, too.
       param_must_satisfy_beartype_union_with_forward_ref: (
           Iterable, 'my_package.my_module.MyOtherClass', NoneType),

       # Annotate PEP 484-compliant optional types. Note that parameters
       # annotated by this type typically default to the "None" singleton.
       param_must_satisfy_pep484_optional: Optional[float] = None,

       # Annotate PEP 484-compliant optional unions of types.
       param_must_satisfy_pep484_optional_union: (
           Optional[Union[float, int]]) = None,

       # Annotate beartype-specific optional types.
       param_must_satisfy_beartype_type_optional: NoneTypeOr[float] = None,

       # Annotate beartype-specific optional unions of types.
       param_must_satisfy_beartype_tuple_optional: NoneTypeOr[float, int] = None,

       # Annotate variadic positional arguments as above, too.
       *args: VersionTypes + (Real, 'my_package.my_module.MyVersionType'),

       # Annotate keyword-only arguments as above, too.
       param_must_be_passed_by_keyword_only: Sequence[Union[bool, list[str]]],

   # Annotate return types as above, too.
   ) -> Union[Integral, 'MyPep585Generic', bool]:
       return 0xDEADBEEF

   # Decorate generators as above but returning a generator type.
   @beartype
   def my_generator() -> Generator[int, None, None]:
       yield from range(0xBEEFBABE, 0xCAFEBABE)

   # User-defined class referenced in forward references above.
   class MyOtherClass:
       # Decorate instance methods as above without annotating "self".
       @beartype
       def __init__(self, scalar: ScalarTypes) -> NoneType:
           self._scalar = scalar

       # Decorate class methods as above without annotating "cls". When
       # chaining decorators, "@beartype" should typically be specified last.
       @classmethod
       @beartype
       def bare_classmethod(cls, regex: RegexTypes, wut: str) -> (
           Callable[(), str]):
           import re
           return lambda: re.sub(regex, 'unbearable', str(cls._scalar) + wut)

       # Decorate static methods as above.
       @staticmethod
       @beartype
       def bare_staticmethod(callable: Callable, *args: str) -> Any:
           return callable(*args)

       # Decorate property getter methods as above.
       @property
       @beartype
       def bare_gettermethod(self) -> Iterator[int]:
           return range(0x0B00B135 + int(self._scalar), 0xB16B00B5)

       # Decorate property setter methods as above.
       @bare_gettermethod.setter
       @beartype
       def bare_settermethod(self, bad: Integral = 0xBAAAAAAD) -> NoneType:
           self._scalar = bad if bad else 0xBADDCAFE

   # User-defined PEP 585-compliant generic referenced above in type hints.
   # Note this requires Python ≥ 3.9.
   class MyPep585Generic(tuple[int, float]):
       # Decorate static class methods as above without annotating "cls".
       @beartype
       def __new__(cls, integer: int, real: float) -> tuple[int, float]:
           return tuple.__new__(cls, (integer, real))

   # User-defined PEP 484-compliant generic referenced above in type hints.
   class MyPep484Generic(Tuple[str, ...]):
       # Decorate static class methods as above without annotating "cls".
       @beartype
       def __new__(cls, *args: str) -> Tuple[str, ...]:
           return tuple.__new__(cls, args)

Features
========

Let's chart current and future compliance with Python's `typing`_ landscape:

.. # FIXME: Span category cells across multiple rows.

+------------------+-----------------------------------------+-------------------------------+---------------------------+
| category         | feature                                 | versions partially supporting | versions fully supporting |
+==================+=========================================+===============================+===========================+
| decoratable      | classes                                 | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | coroutines                              | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | functions                               | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | generators                              | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | methods                                 | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| parameters       | optional                                | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | keyword-only                            | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | positional-only                         | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | variadic keyword                        | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | variadic positional                     | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| hints            | `covariant <covariance_>`__             | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `contravariant <covariance_>`__         | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | absolute forward references             | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `relative forward references`_          | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `tuple unions <Unions of Types_>`__     | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| builtins_        | None_                                   | **0.5.2**\ —\ *current*       | **0.5.2**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | dict_                                   | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | frozenset_                              | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | list_                                   | **0.5.0**\ —\ *current*       | **0.5.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | set_                                    | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | tuple_                                  | **0.5.0**\ —\ *current*       | **0.5.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | type_                                   | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| collections_     | collections.ChainMap_                   | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.Counter_                    | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.OrderedDict_                | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.defaultdict_                | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.deque_                      | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| collections.abc_ | collections.abc.AsyncGenerator_         | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.AsyncIterable_          | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.AsyncIterator_          | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Awaitable_              | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.ByteString_             | **0.5.0**\ —\ *current*       | **0.5.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Callable_               | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Collection_             | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Container_              | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Coroutine_              | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Generator_              | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.ItemsView_              | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Iterable_               | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Iterator_               | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.KeysView_               | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Mapping_                | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.MappingView_            | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.MutableMapping_         | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.MutableSequence_        | **0.5.0**\ —\ *current*       | **0.5.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.MutableSet_             | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Reversible_             | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Sequence_               | **0.5.0**\ —\ *current*       | **0.5.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.Set_                    | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | collections.abc.ValuesView_             | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| contextlib_      | contextlib.AbstractAsyncContextManager_ | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | contextlib.AbstractContextManager_      | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| re_              | re.Match_                               | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | re.Pattern_                             | **0.5.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| typing_          | typing.AbstractSet_                     | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Annotated_                       | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Any_                             | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.AnyStr_                          | **0.4.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.AsyncContextManager_             | **0.4.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.AsyncGenerator_                  | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.AsyncIterable_                   | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.AsyncIterator_                   | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Awaitable_                       | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.BinaryIO_                        | **0.4.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.ByteString_                      | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Callable_                        | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.ChainMap_                        | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.ClassVar_                        | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Collection_                      | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Container_                       | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.ContextManager_                  | **0.4.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Coroutine_                       | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Counter_                         | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.DefaultDict_                     | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Deque_                           | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Dict_                            | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Final_                           | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.ForwardRef_                      | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.FrozenSet_                       | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Generator_                       | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Generic_                         | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Hashable_                        | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.IO_                              | **0.4.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.ItemsView_                       | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Iterable_                        | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Iterator_                        | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.KeysView_                        | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.List_                            | **0.2.0**\ —\ *current*       | **0.3.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Literal_                         | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Mapping_                         | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.MappingView_                     | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Match_                           | **0.4.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.MutableMapping_                  | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.MutableSequence_                 | **0.2.0**\ —\ *current*       | **0.3.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.MutableSet_                      | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.NamedTuple_                      | **0.1.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.NewType_                         | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.NoReturn_                        | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Optional_                        | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.OrderedDict_                     | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Pattern_                         | **0.4.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Protocol_                        | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Reversible_                      | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Sequence_                        | **0.2.0**\ —\ *current*       | **0.3.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Set_                             | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Sized_                           | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.SupportsAbs_                     | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.SupportsBytes_                   | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.SupportsComplex_                 | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.SupportsFloat_                   | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.SupportsIndex_                   | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.SupportsInt_                     | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.SupportsRound_                   | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Text_                            | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.TextIO_                          | **0.4.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Tuple_                           | **0.2.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Type_                            | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.TypedDict_                       | **0.1.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.TypeVar_                         | **0.4.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.Union_                           | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | typing.ValuesView_                      | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `typing.TYPE_CHECKING`_                 | **0.5.0**\ —\ *current*       | **0.5.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `@typing.final`_                        | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `@typing.no_type_check`_                | **0.5.0**\ —\ *current*       | **0.5.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| PEP              | `484 <PEP 484_>`__                      | **0.2.0**\ —\ *current*       | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `544 <PEP 544_>`__                      | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `560 <PEP 560_>`__                      | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `563 <PEP 563_>`__                      | **0.1.1**\ —\ *current*       | **0.1.1**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `572 <PEP 572_>`__                      | **0.3.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `585 <PEP 585_>`__                      | **0.5.0**\ —\ *current*       | **0.5.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `586 <PEP 586_>`__                      | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `589 <PEP 589_>`__                      | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `591 <PEP 591_>`__                      | *none*                        | *none*                    |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `593 <PEP 593_>`__                      | **0.4.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| packages         | `PyPI <beartype PyPI_>`__               | **0.1.0**\ —\ *current*       | —                         |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `Anaconda <beartype Anaconda_>`__       | **0.1.0**\ —\ *current*       | —                         |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `Gentoo Linux <beartype Gentoo_>`__     | **0.2.0**\ —\ *current*       | —                         |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | `macOS MacPorts <beartype MacPorts_>`__ | **0.5.1**\ —\ *current*       | —                         |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
| Python           | 3.5                                     | **0.1.0**\ —\ **0.3.0**       | —                         |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | 3.6                                     | **0.1.0**\ —\ *current*       | —                         |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | 3.7                                     | **0.1.0**\ —\ *current*       | —                         |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | 3.8                                     | **0.1.0**\ —\ *current*       | —                         |
+------------------+-----------------------------------------+-------------------------------+---------------------------+
|                  | 3.9                                     | **0.3.2**\ —\ *current*       | —                         |
+------------------+-----------------------------------------+-------------------------------+---------------------------+

Timings
=======

Let's profile ``beartype`` against other runtime type-checkers with `a battery
of surely fair, impartial, and unbiased use cases <profiler suite_>`__:

.. code-block:: shell-session

   $ bin/profile.bash

   beartype profiler [version]: 0.0.2
   
   python    [basename]: python3.9
   python    [version]: Python 3.9.0
   beartype  [version]: 0.5.2
   typeguard [version]: 2.9.1
   
   ===================================== str =====================================
   profiling regime:
      number of meta-loops:      3
      number of loops:           100
      number of calls each loop: 100
   decoration         [none     ]: 100 loops, best of 3: 359 nsec per loop
   decoration         [beartype ]: 100 loops, best of 3: 389 usec per loop
   decoration         [typeguard]: 100 loops, best of 3: 13.5 usec per loop
   decoration + calls [none     ]: 100 loops, best of 3: 14.8 usec per loop
   decoration + calls [beartype ]: 100 loops, best of 3: 514 usec per loop
   decoration + calls [typeguard]: 100 loops, best of 3: 6.34 msec per loop
   
   =============================== Union[int, str] ===============================
   profiling regime:
      number of meta-loops:      3
      number of loops:           100
      number of calls each loop: 100
   decoration         [none     ]: 100 loops, best of 3: 1.83 usec per loop
   decoration         [beartype ]: 100 loops, best of 3: 433 usec per loop
   decoration         [typeguard]: 100 loops, best of 3: 15.6 usec per loop
   decoration + calls [none     ]: 100 loops, best of 3: 17.7 usec per loop
   decoration + calls [beartype ]: 100 loops, best of 3: 572 usec per loop
   decoration + calls [typeguard]: 100 loops, best of 3: 10 msec per loop
   
   =========================== List[int] of 1000 items ===========================
   profiling regime:
      number of meta-loops:      1
      number of loops:           1
      number of calls each loop: 7485
   decoration         [none     ]: 1 loop, best of 1: 10.1 usec per loop
   decoration         [beartype ]: 1 loop, best of 1: 1.3 msec per loop
   decoration         [typeguard]: 1 loop, best of 1: 41.1 usec per loop
   decoration + calls [none     ]: 1 loop, best of 1: 1.24 msec per loop
   decoration + calls [beartype ]: 1 loop, best of 1: 18.3 msec per loop
   decoration + calls [typeguard]: 1 loop, best of 1: 104 sec per loop
   
   ============ List[Sequence[MutableSequence[int]]] of 10 items each ============
   profiling regime:
      number of meta-loops:      1
      number of loops:           1
      number of calls each loop: 7485
   decoration         [none     ]: 1 loop, best of 1: 11.8 usec per loop
   decoration         [beartype ]: 1 loop, best of 1: 1.77 msec per loop
   decoration         [typeguard]: 1 loop, best of 1: 48.9 usec per loop
   decoration + calls [none     ]: 1 loop, best of 1: 1.19 msec per loop
   decoration + calls [beartype ]: 1 loop, best of 1: 81.2 msec per loop
   decoration + calls [typeguard]: 1 loop, best of 1: 17.3 sec per loop

.. note::
   * ``sec`` = seconds.
   * ``msec`` = milliseconds = 10\ :sup:`-3` seconds.
   * ``usec`` = microseconds = 10\ :sup:`-6` seconds.
   * ``nsec`` = nanoseconds = 10\ :sup:`-9` seconds.

ELI5
----

``beartype`` is:

* **At least twenty times faster** (i.e., 20,000%) and consumes **three orders
  of magnitude less time** in the worst case than typeguard_ – the only
  comparable runtime type-checker also compatible with most modern Python
  versions.
* **Asymptotically faster** in the best case than typeguard_, which scales
  linearly (rather than not at all) with the size of checked containers.
* Constant across type hints, taking roughly the same time to check parameters
  and return values hinted by the builtin type ``str`` as it does to check
  those hinted by the unified type ``Union[int, str]`` as it does to check
  those hinted by the container type ``List[object]``. typeguard_ is
  variable across type hints, taking significantly longer to check
  ``List[object]`` as as it does to check ``Union[int, str]``, which takes
  roughly twice the time as it does to check ``str``.

``beartype`` performs most of its work at *decoration* time. The ``@beartype``
decorator consumes most of the time needed to first decorate and then
repeatedly call a decorated function. ``beartype`` is thus front-loaded. After
paying the initial cost of decoration, each type-checked call thereafter incurs
comparatively little overhead.

Conventional runtime type checkers perform most of their work at *call* time.
The ``@typeguard.typechecked`` and similar decorators consume almost none of
the time needed to first decorate and then repeatedly call a decorated
function. They are thus back-loaded. Although the initial cost of decoration is
essentially free, each type-checked call thereafter incurs significant
overhead.

How Much Does All This Cost?
----------------------------

Beartype dynamically generates functions wrapping decorated callables with
constant-time runtime type-checking. This separation of concerns means that
beartype exhibits different cost profiles at decoration and call time. Whereas
standard runtime type-checking decorators are fast at decoration time and slow
at call time, beartype is the exact opposite.

At call time, wrapper functions generated by the ``@beartype`` decorator are
guaranteed to unconditionally run in **O(1) non-amortized worst-case time with
negligible constant factors** regardless of type hint complexity or nesting.
This is *not* an amortized average-case analysis. Wrapper functions really are
``O(1)`` time in the best, average, and worst cases.

At decoration time, performance is slightly worse. Internally, beartype
non-recursively iterates over type hints at decoration time with a
micro-optimized breadth-first search (BFS). Since this BFS is memoized, its
cost is paid exactly once per type hint per process; subsequent references to
the same hint over different parameters and returns of different callables in
the same process reuse the results of the previously memoized BFS for that
hint. The ``@beartype`` decorator itself thus runs in:

* **O(1) amortized average-case time.**
* **O(k) non-amortized worst-case time** for ``k`` the number of child type
  hints nested in a parent type hint and including that parent.

Since we generally expect a callable to be decorated only once but called
multiple times per process, we might expect the cost of decoration to be
ignorable in the aggregate. Interestingly, this is not the case. Although only
paid once and obviated through memoization, decoration time is sufficiently
expensive and call time sufficiently inexpensive that beartype spends most of
its wall-clock merely decorating callables. The actual function wrappers
dynamically generated by ``@beartype`` consume comparatively little wall-clock,
even when repeatedly called many times.

That's Some Catch, That Catch-22
--------------------------------

Beartype's greatest strength is that it checks types in constant time.

Beartype's greatest weakness is that it checks types in constant time.

Only so many type-checks can be stuffed into a constant slice of time with
negligible constant factors. Let's detail exactly what (and why) beartype
stuffs into its well-bounded slice of the CPU pie.

Standard runtime type checkers naïvely brute-force the problem by type-checking
*all* child objects transitively reachable from parent objects passed to and
returned from callables in ``O(n)`` linear time for ``n`` such objects. This
approach avoids false positives (i.e., raising exceptions for valid objects)
*and* false negatives (i.e., failing to raise exceptions for invalid objects),
which is good. But this approach also duplicates work when those objects remain
unchanged over multiple calls to those callables, which is bad.

Beartype circumvents that badness by generating code at decoration time
performing a one-way random tree walk over the expected nested structure of
those objects at call time. For each expected nesting level of each container
passed to or returned from each callable decorated by ``@beartype`` starting at
that container and ending either when a check fails *or* all checks succeed,
that callable performs these checks (in order):

#. A **shallow type-check** that the current possibly nested container is an
   instance of the type given by the current possibly nested type hint.
#. A **deep type-check** that an item randomly selected from that container
   itself satisfies the first check.

For example, given a parameter's type hint ``list[tuple[Sequence[str]]]``,
beartype generates code at decoration time performing these checks at call time
(in order):

#. A check that the object passed as this parameter is a list.
#. A check that an item randomly selected from this list is a tuple.
#. A check that an item randomly selected from this tuple is a sequence.
#. A check that an item randomly selected from this sequence is a string.

Beartype thus performs one check for each possibly nested type hint for each
annotated parameter or return object for each call to each decorated callable.
This deep randomness gives us soft statistical expectations as to the number of
calls needed to check everything. Specifically, `it can be shown that beartype
type-checks on average <Nobody Expects the Linearithmic Time_>`__ *all* child
objects transitively reachable from parent objects passed to and returned from
callables in ``O(n log n)`` calls to those callables for ``n`` such objects.
Praise RNGesus_!

Beartype avoids false positives and rarely duplicates work when those objects
remain unchanged over multiple calls to those callables, which is good. Sadly,
beartype also invites false negatives, because this approach only checks a
vertical slice of the full container structure each call, which is bad.

We claim without evidence that false negatives are unlikely under the
optimistic assumption that most real-world containers are **homogenous** (i.e.,
contain only items of the same type) rather than **heterogenous** (i.e.,
contain items of differing types). Examples of homogenous containers include
(byte-)strings, `ranges <range_>`__, `streams <io_>`__, `memory views
<memoryview_>`__, `method resolution orders (MROs) <mro_>`__, `generic alias
parameters`_, lists returned by the dir_ builtin, iterables generated by the
os.walk_ function, standard NumPy_ arrays, Pandas_ `DataFrame` columns,
PyTorch_ tensors, NetworkX_ graphs, and really all scientific containers ever.

Nobody Expects the Linearithmic Time
------------------------------------

Math time, people. :sup:`it's happening`

Most runtime type-checkers exhibit ``O(n)`` time complexity (where ``n`` is the
total number of items recursively contained in a container to be checked) by
recursively and repeatedly checking *all* items of *all* containers passed to
or returned from *all* calls of decorated callables.

``beartype`` guarantees ``O(1)`` time complexity by non-recursively but
repeatedly checking *one* random item at *all* nesting levels of *all*
containers passed to or returned from *all* calls of decorated callables, thus
amortizing the cost of deeply checking containers across calls. (See the
subsection on `@beartype-generated code deeply type-checking arbitrarily nested
containers in constant time <Constant Nested Deep Sequence Decoration_>`__ for
what this means in practice.)

``beartype`` exploits the `well-known coupon collector's problem <coupon
collector's problem_>`__ applied to abstract trees of nested type hints,
enabling us to statistically predict the number of calls required to fully
type-check all items of an arbitrary container on average. Formally, let:

* ``E(T)`` be the expected number of calls needed to check all items of a
  container containing only non-container items (i.e., containing *no* nested
  subcontainers) either passed to or returned from a ``@beartype``\ -decorated
  callable.
* ``γ ≈ 0.5772156649`` be the `Euler–Mascheroni constant`_.

Then:

.. #FIXME: GitHub currently renders LaTeX-based "math" directives in
.. # reStructuredText as monospaced literals, which is hot garbage. Until
.. # resolved, do the following:
.. # * Preserve *ALL* such directives as comments, enabling us to trivially
.. #   revert to the default approach after GitHub resolves this.
.. # * Convert *ALL* such directives into GitHub-hosted URLs via any of the
.. #   following third-party webapps:
.. #     https://tex-image-link-generator.herokuapp.com
.. #     https://jsfiddle.net/8ndx694g
.. #     https://marketplace.visualstudio.com/items?itemName=MeowTeam.vscode-math-to-image
.. # See also this long-standing GitHub issue:
.. #     https://github.com/github/markup/issues/83
.. #FIXME: Actually, we'll be leveraging Sphinx's MathJax extension to render
.. # this, which means the currently disabled "math::" directives below should
.. # now work out-of-the-box. If so, remove the corresponding images, please.

.. #FIXME: Uncomment after GitHub resolves LaTeX math rendering.
.. # .. math:: E(T) = n \log n + \gamma n + \frac{1}{2} + O\left(\frac{1}{n}\right)

.. image:: https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+E%28T%29+%3D+n+%5Clog+n+%2B+%5Cgamma+n+%2B+%5Cfrac%7B1%7D%7B2%7D+%2B+O%5Cleft%28%5Cfrac%7B1%7D%7Bn%7D%5Cright%29

.. #FIXME: Uncomment after GitHub resolves LaTeX math rendering.
.. # The summation :math:`\frac{1}{2} + O\left(\frac{1}{n}\right) \le 1` is
.. # negligible. While non-negligible, the term :math:`\gamma n` grows significantly
.. # slower than the term :math:`n \log n`. So this reduces to:

The summation ``½ + O(1/n)`` is strictly less than 1 and thus negligible. While
non-negligible, the term ``γn`` grows significantly slower than the term
``nlogn``. So this reduces to:

.. #FIXME: Uncomment after GitHub resolves LaTeX math rendering.
.. # .. math:: E(T) = O(n \log n)

.. image:: https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+E%28T%29+%3D+O%28n+%5Clog+n%29

We now generalize this bound to the general case. When checking a container
containing *no* subcontainers, ``beartype`` only randomly samples one item from
that container on each call. When checking a container containing arbitrarily
many nested subcontainers, however, ``beartype`` randomly samples one random
item from each nesting level of that container on each call.

In general, ``beartype`` thus samples ``h`` random items from a container on
each call, where ``h`` is that container's height (i.e., maximum number of
edges on the longest path from that container to a non-container leaf item
reachable from items directly contained in that container). Since ``h ≥ 1``,
``beartype`` samples at least as many items each call as assumed in the usual
`coupon collector's problem`_ and thus paradoxically takes a fewer number of
calls on average to check all items of a container containing arbitrarily many
subcontainers as it does to check all items of a container containing *no*
subcontainers.

Ergo, the expected number of calls ``E(S)`` needed to check all items of an
arbitrary container exhibits the same or better growth rate and remains bound
above by at least the same upper bounds – but probably tighter: e.g.,

.. #FIXME: Uncomment after GitHub resolves LaTeX math rendering.
.. # .. math:: E(S) = O(E(T)) = O(n \log n)

.. image:: https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+E%28S%29+%3D+O%28E%28T%29%29+%3D+O%28n+%5Clog+n%29%0A

Fully checking a container takes no more calls than that container's size times
the logarithm of that size on average. For example, fully checking a **list of
50 integers** is expected to take **225 calls** on average.

Compliance
==========

``beartype`` is fully compliant with these `Python Enhancement Proposals (PEPs)
<PEP 0_>`__:

* `PEP 483 -- The Theory of Type Hints <PEP 483_>`__, subject to `caveats
  detailed below <Partial Compliance_>`__
* `PEP 484 -- Type Hints <PEP 484_>`__, subject to `caveats detailed below
  <Partial Compliance_>`__.
* `PEP 544 -- Protocols: Structural subtyping (static duck typing) <PEP
  544_>`_.
* `PEP 560 -- Core support for typing module and generic types <PEP 560_>`_.
* `PEP 563 -- Postponed Evaluation of Annotations <PEP 563_>`__.
* `PEP 572 -- Assignment Expressions <PEP 572_>`__.
* `PEP 585 -- Type Hinting Generics In Standard Collections <PEP 585_>`__.
* `PEP 593 -- Flexible function and variable annotations <PEP 593_>`__.

``beartype`` is currently *not* compliant whatsoever with these PEPs:

* `PEP 526 -- Syntax for Variable Annotations <PEP 526_>`__.
* `PEP 586 -- Literal Types <PEP 586_>`__.
* `PEP 589 -- TypedDict: Type Hints for Dictionaries with a Fixed Set of Keys
  <PEP 589_>`__.
* `PEP 591 -- Adding a final qualifier to typing <PEP 591_>`__.

See also the **PEP** and **typing** categories of our `features matrix
<Features_>`__ for further details.

Full Compliance
---------------

``beartype`` **deeply type-checks** (i.e., directly checks the types of *and*
recursively checks the types of items contained in) parameters and return
values annotated with these typing_ types:

* None_.
* list_.
* tuple_.
* collections.abc.ByteString_.
* collections.abc.MutableSequence_.
* collections.abc.Sequence_.
* typing.Annotated_.
* typing.Any_.
* typing.ByteString_.
* typing.ForwardRef_.
* typing.Hashable_.
* typing.List_.
* typing.MutableSequence_.
* typing.NewType_.
* typing.NoReturn_.
* typing.Optional_.
* typing.Sequence_.
* typing.Sized_.
* typing.Text_.
* typing.Tuple_.
* typing.Union_.
* **Generics** (i.e., classes subclassing one or more typing_ non-class
  objects), including:

  * typing.IO_.
  * typing.BinaryIO_.
  * typing.TextIO_.

* **Protocols** (i.e., classes directly subclassing the typing.Protocol_
  abstract base class (ABC) *and* zero or more typing_ non-class objects),
  including:

  * typing.SupportsAbs_.
  * typing.SupportsBytes_.
  * typing.SupportsComplex_.
  * typing.SupportsIndex_.
  * typing.SupportsInt_.
  * typing.SupportsFloat_.
  * typing.SupportsRound_.

* `Forward references <relative forward references_>`__ (i.e., unqualified
  relative classnames typically referring to user-defined classes that have yet
  to be defined).
* **Forward reference-subscripted types** (i.e., typing_ objects subscripted by
  one or more `forward references <relative forward references_>`__).

``beartype`` also fully supports callables decorated by these typing_
decorators:

* `@typing.no_type_check`_.

Lastly, ``beartype`` fully supports these typing_ constants:

* typing.TYPE_CHECKING_.

Partial Compliance
------------------

``beartype`` currently only **shallowly type-checks** (i.e., only directly
checks the types of) parameters and return values annotated with these typing_
types:

* frozenset_.
* set_.
* type_.
* collections.ChainMap_.
* collections.Counter_.
* collections.OrderedDict_.
* collections.defaultdict_.
* collections.deque_.
* collections.abc.AsyncGenerator_.
* collections.abc.AsyncIterable_.
* collections.abc.AsyncIterator_.
* collections.abc.Awaitable_.
* collections.abc.Callable_.
* collections.abc.Collection_.
* collections.abc.Container_.
* collections.abc.Coroutine_.
* collections.abc.Generator_.
* collections.abc.ItemsView_.
* collections.abc.Iterable_.
* collections.abc.Iterator_.
* collections.abc.KeysView_.
* collections.abc.Mapping_.
* collections.abc.MappingView_.
* collections.abc.MutableMapping_.
* collections.abc.MutableSet_.
* collections.abc.Reversible_.
* collections.abc.Set_.
* collections.abc.ValuesView_.
* contextlib.AbstractAsyncContextManager_.
* contextlib.AbstractContextManager_.
* re.Match_.
* re.Pattern_.
* typing.AbstractSet_.
* typing.AnyStr_.
* typing.AsyncContextManager_.
* typing.AsyncGenerator_.
* typing.AsyncIterable_.
* typing.AsyncIterator_.
* typing.Callable_.
* typing.Collection_.
* typing.Container_.
* typing.ContextManager_.
* typing.Coroutine_.
* typing.Counter_.
* typing.DefaultDict_.
* typing.Deque_.
* typing.Dict_.
* typing.FrozenSet_.
* typing.Generator_.
* typing.ItemsView_.
* typing.Iterable_.
* typing.Iterator_.
* typing.KeysView_.
* typing.MappingView_.
* typing.Mapping_.
* typing.Match_.
* typing.MutableMapping_.
* typing.MutableSet_.
* typing.NamedTuple_.
* typing.OrderedDict_.
* typing.Pattern_.
* typing.Reversible_.
* typing.Set_.
* typing.Type_.
* typing.TypedDict_.
* typing.ValuesView_.
* **Subscripted builtins** (i.e., `PEP 585`_-compliant C-based type hint
  instantiated by subscripting either a concrete builtin container class like
  list_ or tuple_ *or* an abstract base class (ABC) declared by
  the collections.abc_ or contextlib_ modules like collections.abc.Iterable_
  or contextlib.AbstractContextManager_ with one or more PEP-compliant child
  type hints).
* **Type variable-parametrized types** (i.e., typing_ objects subscripted by
  one or more type variables).

Subsequent ``beartype`` versions will deeply type-check these typing_ types
while preserving our `O(1) time complexity (with negligible constant factors)
guarantee <Timings_>`__.

No Compliance
-------------

``beartype`` currently silently ignores these typing_ types at decoration time:

* typing.ClassVar_.
* typing.Final_.
* `@typing.final`_.
* **Type variables** (i.e., typing.TypeVar_ instances enabling general-purpose
  type-checking of generically substitutable types), including:

  * typing.AnyStr_.

``beartype`` currently raises exceptions at decoration time when passed these
typing_ types:

* typing.Literal_.

Subsequent ``beartype`` versions will first shallowly and then deeply
type-check these typing_ types while preserving our `O(1) time complexity (with
negligible constant factors) guarantee <Timings_>`__.

Tutorial
========

Let's begin with the simplest type of type-checking supported by ``@beartype``.

Builtin Types
-------------

**Builtin types** like ``dict``, ``int``, ``list``, ``set``, and ``str`` are
trivially type-checked by annotating parameters and return values with those
types as is.

Let's declare a simple beartyped function accepting a string and a dictionary
and returning a tuple:

.. code-block:: python

   from beartype import beartype

   @beartype
   def law_of_the_jungle(wolf: str, pack: dict) -> tuple:
       return (wolf, pack[wolf]) if wolf in pack else None

Let's call that function with good types:

.. code-block:: python

   >>> law_of_the_jungle(wolf='Akela', pack={'Akela': 'alone', 'Raksha': 'protection'})
   ('Akela', 'alone')

Good function. Let's call it again with bad types:

.. code-block:: python

   >>> law_of_the_jungle(wolf='Akela', pack=['Akela', 'Raksha'])
   Traceback (most recent call last):
     File "<ipython-input-10-7763b15e5591>", line 1, in <module>
       law_of_the_jungle(wolf='Akela', pack=['Akela', 'Raksha'])
     File "<string>", line 22, in __law_of_the_jungle_beartyped__
   beartype.roar.BeartypeCallTypeParamException: @beartyped law_of_the_jungle() parameter pack=['Akela', 'Raksha'] not a <class 'dict'>.

The ``beartype.roar`` submodule publishes exceptions raised at both decoration
time by ``@beartype`` and at runtime by wrappers generated by ``@beartype``. In
this case, a runtime type exception describing the improperly typed ``pack``
parameter is raised.

Good function! Let's call it again with good types exposing a critical issue in
this function's implementation and/or return type annotation:

.. code-block:: python

   >>> law_of_the_jungle(wolf='Leela', pack={'Akela': 'alone', 'Raksha': 'protection'})
   Traceback (most recent call last):
     File "<ipython-input-10-7763b15e5591>", line 1, in <module>
       law_of_the_jungle(wolf='Leela', pack={'Akela': 'alone', 'Raksha': 'protection'})
     File "<string>", line 28, in __law_of_the_jungle_beartyped__
   beartype.roar.BeartypeCallTypeReturnException: @beartyped law_of_the_jungle() return value None not a <class 'tuple'>.

*Bad function.* Let's conveniently resolve this by permitting this function to
return either a tuple or ``None`` as `detailed below <Unions of Types_>`__:

.. code-block:: python

   >>> from beartype.cave import NoneType
   >>> @beartype
   ... def law_of_the_jungle(wolf: str, pack: dict) -> (tuple, NoneType):
   ...     return (wolf, pack[wolf]) if wolf in pack else None
   >>> law_of_the_jungle(wolf='Leela', pack={'Akela': 'alone', 'Raksha': 'protection'})
   None

The ``beartype.cave`` submodule publishes generic types suitable for use with
the ``@beartype`` decorator and anywhere else you might need them. In this
case, the type of the ``None`` singleton is imported from this submodule and
listed in addition to ``tuple`` as an allowed return type from this function.

Note that usage of the ``beartype.cave`` submodule is entirely optional (but
more efficient and convenient than most alternatives). In this case, the type
of the ``None`` singleton can also be accessed directly as ``type(None)`` and
listed in place of ``NoneType`` above: e.g.,

.. code-block:: python

   >>> @beartype
   ... def law_of_the_jungle(wolf: str, pack: dict) -> (tuple, type(None)):
   ...     return (wolf, pack[wolf]) if wolf in pack else None
   >>> law_of_the_jungle(wolf='Leela', pack={'Akela': 'alone', 'Raksha': 'protection'})
   None

Of course, the ``beartype.cave`` submodule also publishes types *not*
accessible directly like ``RegexCompiledType`` (i.e., the type of all compiled
regular expressions). All else being equal, ``beartype.cave`` is preferable.

Good function! The type hints applied to this function now accurately document
this function's API. All's well that ends typed well. Suck it, `Shere Khan`_.

Arbitrary Types
---------------

Everything above also extends to:

* **Arbitrary types** like user-defined classes and stock classes in the Python
  stdlib (e.g., ``argparse.ArgumentParser``) – all of which are also trivially
  type-checked by annotating parameters and return values with those types.
* **Arbitrary callables** like instance methods, class methods, static methods,
  and generator functions and methods – all of which are also trivially
  type-checked with the ``@beartype`` decorator.

Let's declare a motley crew of beartyped callables doing various silly things
in a strictly typed manner, *just 'cause*:

.. code-block:: python

   from beartype import beartype
   from beartype.cave import GeneratorType, IterableType, NoneType

   class MaximsOfBaloo(object):
       @beartype
       def __init__(self, sayings: IterableType):
           self.sayings = sayings

   @beartype
   def inform_baloo(maxims: MaximsOfBaloo) -> GeneratorType:
       for saying in maxims.sayings:
           yield saying

For genericity, the ``MaximsOfBaloo`` class initializer accepts *any* generic
iterable (via the ``beartype.cave.IterableType`` tuple listing all valid
iterable types) rather than an overly specific ``list`` or ``tuple`` type. Your
users may thank you later.

For specificity, the ``inform_baloo`` generator function has been explicitly
annotated to return a ``beartype.cave.GeneratorType`` (i.e., the type returned
by functions and methods containing at least one ``yield`` statement). Type
safety brings good fortune for the New Year.

Let's iterate over that generator with good types:

.. code-block:: python

   >>> maxims = MaximsOfBaloo(sayings={
   ...     '''If ye find that the Bullock can toss you,
   ...           or the heavy-browed Sambhur can gore;
   ...      Ye need not stop work to inform us:
   ...           we knew it ten seasons before.''',
   ...     '''“There is none like to me!” says the Cub
   ...           in the pride of his earliest kill;
   ...      But the jungle is large and the Cub he is small.
   ...           Let him think and be still.''',
   ... })
   >>> for maxim in inform_baloo(maxims): print(maxim.splitlines()[-1])
          Let him think and be still.
          we knew it ten seasons before.

Good generator. Let's call it again with bad types:

.. code-block:: python

   >>> for maxim in inform_baloo([
   ...     'Oppress not the cubs of the stranger,',
   ...     '     but hail them as Sister and Brother,',
   ... ]): print(maxim.splitlines()[-1])
   Traceback (most recent call last):
     File "<ipython-input-10-7763b15e5591>", line 30, in <module>
       '     but hail them as Sister and Brother,',
     File "<string>", line 12, in __inform_baloo_beartyped__
   beartype.roar.BeartypeCallTypeParamException: @beartyped inform_baloo() parameter maxims=['Oppress not the cubs of the stranger,', '     but hail them as Sister and ...'] not a <class '__main__.MaximsOfBaloo'>.

Good generator! The type hints applied to these callables now accurately
document their respective APIs. Thanks to the pernicious magic of beartype, all
ends typed well... *yet again.*

Unions of Types
---------------

That's all typed well, but everything above only applies to parameters and
return values constrained to *singular* types. In practice, parameters and
return values are often relaxed to any of *multiple* types referred to as
**unions of types.** :sup:`You can thank set theory for the jargon... unless
you hate set theory. Then it's just our fault.`

Unions of types are trivially type-checked by annotating parameters and return
values with the typing.Union_ type hint containing those types. Let's declare
another beartyped function accepting either a mapping *or* a string and
returning either another function *or* an integer:

.. code-block:: python

   from beartype import beartype
   from collections.abc import Callable, Mapping
   from numbers import Integral
   from typing import Any, Union

   @beartype
   def toomai_of_the_elephants(memory: Union[Integral, Mapping[Any, Any]]) -> (
       Union[Integral, Callable[(Any,), Any]]):
       return memory if isinstance(memory, Integral) else lambda key: memory[key]

For genericity, the ``toomai_of_the_elephants`` function both accepts and
returns *any* generic integer (via the standard ``numbers.Integral`` abstract
base class (ABC) matching both builtin integers and third-party integers from
frameworks like NumPy_ and SymPy_) rather than an overly specific ``int`` type.
The API you relax may very well be your own.

Let's call that function with good types:

.. code-block:: python

   >>> memory_of_kala_nag = {
   ...     'remember': 'I will remember what I was, I am sick of rope and chain—',
   ...     'strength': 'I will remember my old strength and all my forest affairs.',
   ...     'not sell': 'I will not sell my back to man for a bundle of sugar-cane:',
   ...     'own kind': 'I will go out to my own kind, and the wood-folk in their lairs.',
   ...     'morning':  'I will go out until the day, until the morning break—',
   ...     'caress':   'Out to the wind’s untainted kiss, the water’s clean caress;',
   ...     'forget':   'I will forget my ankle-ring and snap my picket stake.',
   ...     'revisit':  'I will revisit my lost loves, and playmates masterless!',
   ... }
   >>> toomai_of_the_elephants(len(memory_of_kala_nag['remember']))
   56
   >>> toomai_of_the_elephants(memory_of_kala_nag)('remember')
   'I will remember what I was, I am sick of rope and chain—'

Good function. Let's call it again with a tastelessly bad type:

.. code-block:: python

   >>> toomai_of_the_elephants(
   ...     'Shiv, who poured the harvest and made the winds to blow,')
   BeartypeCallHintPepParamException: @beartyped toomai_of_the_elephants()
   parameter memory='Shiv, who poured the harvest and made the winds to blow,'
   violates type hint typing.Union[numbers.Integral, collections.abc.Mapping],
   as 'Shiv, who poured the harvest and made the winds to blow,' not <protocol
   ABC "collections.abc.Mapping"> or <protocol "numbers.Integral">.

Good function! The type hints applied to this callable now accurately documents
its API. All ends typed well... *still again and again.*

Optional Types
~~~~~~~~~~~~~~

That's also all typed well, but everything above only applies to *mandatory*
parameters and return values whose types are never ``NoneType``. In practice,
parameters and return values are often relaxed to optionally accept any of
multiple types including ``NoneType`` referred to as **optional types.**

Optional types are trivially type-checked by annotating optional parameters
(parameters whose values default to ``None``) and optional return values
(callables returning ``None`` rather than raising exceptions in edge cases)
with the ``typing.Optional`` type hint indexed by those types.

Let's declare another beartyped function accepting either an enumeration type
*or* ``None`` and returning either an enumeration member *or* ``None``:

.. code-block:: python

   from beartype import beartype
   from beartype.cave import EnumType, EnumMemberType
   from typing import Optional

   @beartype
   def tell_the_deep_sea_viceroys(story: Optional[EnumType] = None) -> (
       Optional[EnumMemberType]):
       return story if story is None else list(story.__members__.values())[-1]

For efficiency, the ``typing.Optional`` type hint creates, caches, and returns
new tuples of types appending ``NoneType`` to the original types it's indexed
with. Since efficiency is good, ``typing.Optional`` is also good.

Let's call that function with good types:

.. code-block:: python

   >>> from enum import Enum
   >>> class Lukannon(Enum):
   ...     WINTER_WHEAT = 'The Beaches of Lukannon—the winter wheat so tall—'
   ...     SEA_FOG      = 'The dripping, crinkled lichens, and the sea-fog drenching all!'
   ...     PLAYGROUND   = 'The platforms of our playground, all shining smooth and worn!'
   ...     HOME         = 'The Beaches of Lukannon—the home where we were born!'
   ...     MATES        = 'I met my mates in the morning, a broken, scattered band.'
   ...     CLUB         = 'Men shoot us in the water and club us on the land;'
   ...     DRIVE        = 'Men drive us to the Salt House like silly sheep and tame,'
   ...     SEALERS      = 'And still we sing Lukannon—before the sealers came.'
   >>> tell_the_deep_sea_viceroys(Lukannon)
   <Lukannon.SEALERS: 'And still we sing Lukannon—before the sealers came.'>
   >>> tell_the_deep_sea_viceroys()
   None

You may now be pondering to yourself grimly in the dark: "...but could we not
already do this just by manually annotating optional types with
``typing.Union`` type hints explicitly indexed by ``NoneType``?"

You would, of course, be correct. Let's grimly redeclare the same function
accepting and returning the same types – only annotated with ``NoneType``
rather than ``typing.Optional``:

.. code-block:: python

   from beartype import beartype
   from beartype.cave import EnumType, EnumMemberType, NoneType
   from typing import Union

   @beartype
   def tell_the_deep_sea_viceroys(story: Union[EnumType, NoneType] = None) -> (
       Union[EnumMemberType, NoneType]):
       return list(story.__members__.values())[-1] if story is not None else None

Since ``typing.Optional`` internally reduces to ``typing.Union``, these two
approaches are semantically equivalent. The former is simply syntactic sugar
simplifying the latter.

Whereas ``typing.Union`` accepts an arbitrary number of child type hints,
however, ``typing.Optional`` accepts only a single child type hint. This can be
circumvented by either indexing ``typing.Optional`` by ``typing.Union`` *or*
indexing ``typing.Union`` by ``NoneType``. Let's exhibit the former approach by
declaring another beartyped function accepting either an enumeration type,
enumeration type member, or ``None`` and returning either an enumeration type,
enumeration type member, or ``None``:

.. code-block:: python

   from beartype import beartype
   from beartype.cave import EnumType, EnumMemberType, NoneType
   from typing import Optional, Union

   @beartype
   def sang_them_up_the_beach(
       woe: Optional[Union[EnumType, EnumMemberType]] = None) -> (
       Optional[Union[EnumType, EnumMemberType]]):
       return woe if isinstance(woe, (EnumMemberType, NoneType)) else (
           list(woe.__members__.values())[-1])

Let's call that function with good types:

.. code-block:: python

   >>> sang_them_up_the_beach(Lukannon)
   <Lukannon.SEALERS: 'And still we sing Lukannon—before the sealers came.'>
   >>> sang_them_up_the_beach()
   None

Behold! The terrifying power of the ``typing.Optional`` type hint, resplendent
in its highly over-optimized cache utilization.

Decoration
==========

Let's take a deep dive into the deep end of runtime type checking – the
``beartype`` way. In this subsection, we show code generated by the
``@beartype`` decorator in real-world use cases and tell why that code is the
fastest possible code type-checking those cases.

Identity Decoration
-------------------

We begin by wading into the torpid waters of the many ways ``beartype`` avoids
doing any work whatsoever, because laziness is the virtue we live by. The
reader may recall that the fastest decorator at decoration- *and* call-time is
the **identity decorator** returning its decorated callable unmodified: e.g.,

.. code-block:: python

   from collections.abc import Callable

   def identity_decorator(func: Callable): -> Callable:
       return func

``beartype`` silently reduces to the identity decorator whenever it can, which
is surprisingly often. Our three weapons are laziness, surprise, ruthless
efficiency, and an almost fanatical devotion to constant-time type checking.

Unconditional Identity Decoration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a trivial function annotated by *no* type hints:

.. code-block:: python

   def law_of_the_jungle(strike_first_and_then_give_tongue):
       return strike_first_and_then_give_tongue

Let's decorate that function by ``@beartype`` and verify that ``@beartype``
reduced to the identity decorator by returning that function unmodified:

.. code-block:: python

   >>> from beartype import beartype
   >>> beartype(law_of_the_jungle) is law_of_the_jungle
   True

We've verified that ``@beartype`` reduces to the identity decorator when
decorating unannotated callables. That's but the tip of the iceberg, though.
``@beartype`` unconditionally reduces to a noop when:

* The decorated callable is itself decorated by the `PEP 484`_-compliant
  `@typing.no_type_check`_ decorator.
* The decorated callable has already been decorated by ``@beartype``.
* Interpreter-wide optimization is enabled: e.g.,

  * `CPython is invoked with the "-O" command-line option <-O_>`__.
  * `The "PYTHONOPTIMIZE" environment variable is set <PYTHONOPTIMIZE_>`__.

Shallow Identity Decoration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a trivial function annotated by the `PEP 484`_-compliant
typing.Any_ type hint:

.. code-block:: python

   from typing import Any

   def law_of_the_jungle_2(never_order_anything_without_a_reason: Any) -> Any:
       return never_order_anything_without_a_reason

Again, let's decorate that function by ``@beartype`` and verify that
``@beartype`` reduced to the identity decorator by returning that function
unmodified:

.. code-block:: python

   >>> from beartype import beartype
   >>> beartype(law_of_the_jungle_2) is law_of_the_jungle_2
   True

We've verified that ``@beartype`` reduces to the identity decorator when
decorating callables annotated by typing.Any_ – a novel category of type hint
we refer to as **shallowly ignorable type hints** (known to be ignorable by
constant-time lookup in a predefined frozen set). That's but the snout of the
crocodile, though. ``@beartype`` conditionally reduces to a noop when *all*
type hints annotating the decorated callable are shallowly ignorable. These
include:

* object_, the root superclass of Python's class hierarchy. Since all objects
  are instances of object_, object_ conveys no meaningful constraints as a type
  hint and is thus shallowly ignorable.
* typing.Any_, equivalent to object_.
* typing.Generic_, equivalent to ``typing.Generic[typing.Any]``, which conveys
  no meaningful constraints as a type hint and is thus shallowly ignorable.
* typing.Protocol_, equivalent to ``typing.Protocol[typing.Any]`` and shallowly
  ignorable for similar reasons.
* typing.Union_, equivalent to ``typing.Union[typing.Any]``, equivalent to
  ``Any``.
* typing.Optional_, equivalent to ``typing.Optional[typing.Any]``, equivalent
  to ``Union[Any, type(None)]``. Since any union subscripted by ignorable type
  hints is itself ignorable, [#union_ignorable]_ typing.Optional_ is shallowly
  ignorable as well.

.. [#union_ignorable]
   Unions are only as narrow as their widest subscripted argument. However,
   ignorable type hints are ignorable *because* they are maximally wide.
   Unions subscripted by ignorable arguments are thus the widest possible
   unions, conveying no meaningful constraints and thus themselves ignorable.

Deep Identity Decoration
~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a trivial function annotated by a non-trivial `PEP 484`_-, `585
<PEP 585_>`__- and `593 <PEP 593_>`__-compliant type hint that superficially
*appears* to convey meaningful constraints:

.. code-block:: python

   from typing import Annotated, NewType, Union

   hint = Union[str, list[int], NewType('MetaType', Annotated[object, 53])]
   def law_of_the_jungle_3(bring_them_to_the_pack_council: hint) -> hint:
       return bring_them_to_the_pack_council

Despite appearances, it can be shown by exhaustive (and frankly exhausting)
reduction that that hint is actually ignorable. Let's decorate that function by
``@beartype`` and verify that ``@beartype`` reduced to the identity decorator
by returning that function unmodified:

.. code-block:: python

   >>> from beartype import beartype
   >>> beartype(law_of_the_jungle_3) is law_of_the_jungle_3
   True

We've verified that ``@beartype`` reduces to the identity decorator when
decorating callables annotated by the above object – a novel category of type
hint we refer to as **deeply ignorable type hints** (known to be ignorable only
by recursive linear-time inspection of subscripted arguments). That's but the
trunk of the elephant, though. ``@beartype`` conditionally reduces to a noop
when *all* type hints annotating the decorated callable are deeply ignorable.
These include:

* Parametrizations of typing.Generic_ and typing.Protocol_ by type variables.
  Since typing.Generic_, typing.Protocol_, *and* type variables all fail to
  convey any meaningful constraints in and of themselves, these
  parametrizations are safely ignorable in all contexts.
* Calls to typing.NewType_ passed an ignorable type hint.
* Subscriptions of typing.Annotated_ whose first argument is ignorable.
* Subscriptions of typing.Optional_ and typing.Union_ by at least one ignorable
  argument.

Constant Decoration
-------------------

We continue by trundling into the turbid waters out at sea, where ``beartype``
reluctantly performs its minimal amount of work with a heavy sigh.

Constant Builtin Type Decoration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a trivial function annotated by type hints that are builtin types:

.. code-block:: python

   from beartype import beartype

   @beartype
   def law_of_the_jungle_4(he_must_be_spoken_for_by_at_least_two: int):
       return he_must_be_spoken_for_by_at_least_two

Let's see the wrapper function ``@beartype`` dynamically generated from that:

.. code-block:: python

   def __beartyped_law_of_the_jungle_4(
       *args,
       __beartype_func=__beartype_func,
       __beartypistry=__beartypistry,
       **kwargs
   ):
       # Localize the number of passed positional arguments for efficiency.
       __beartype_args_len = len(args)
       # Localize this positional or keyword parameter if passed *OR* to the
       # sentinel value "__beartypistry" guaranteed to never be passed otherwise.
       __beartype_pith_0 = (
           args[0] if __beartype_args_len > 0 else
           kwargs.get('he_must_be_spoken_for_by_at_least_two', __beartypistry)
       )

       # If this parameter was passed...
       if __beartype_pith_0 is not __beartypistry:
           # Type-check this passed parameter or return value against this
           # PEP-compliant type hint.
           if not isinstance(__beartype_pith_0, int):
               __beartype_raise_pep_call_exception(
                   func=__beartype_func,
                   pith_name='he_must_be_spoken_for_by_at_least_two',
                   pith_value=__beartype_pith_0,
               )

       # Call this function with all passed parameters and return the value
       # returned from this call.
       return __beartype_func(*args, **kwargs)

Let's dismantle this bit by bit:

* The code comments above are verbatim as they appear in the generated code.
* ``__beartyped_law_of_the_jungle_4()`` is the ad-hoc function name
  ``@beartype`` assigned this wrapper function.
* ``__beartype_func`` is the original ``law_of_the_jungle_4()`` function.
* ``__beartypistry`` is a thread-safe global registry of all types, tuples of
  types, and forward references to currently undeclared types visitable from
  type hints annotating callables decorated by ``@beartype``. We'll see more
  about the ``__beartypistry`` in a moment. For know, just know that
  ``__beartypistry`` is a private singleton of the ``beartype`` package. This
  object is frequently accessed and thus localized to the body of this wrapper
  rather than accessed as a global variable, which would be mildly slower.
* ``__beartype_pith_0`` is the value of the first passed parameter, regardless
  of whether that parameter is passed as a positional or keyword argument. If
  unpassed, the value defaults to the ``__beartypistry``. Since *no* caller
  should access (let alone pass) that object, that object serves as an
  efficient sentinel value enabling us to discern passed from unpassed
  parameters. ``beartype`` internally favours the term "pith" (which we
  absolutely just made up) to transparently refer to the arbitrary object
  currently being type-checked against its associated type hint.
* ``isinstance(__beartype_pith_0, int)`` tests whether the value passed for
  this parameter satisfies the type hint annotating this parameter.
* ``__beartype_raise_pep_call_exception()`` raises a human-readable exception
  if this value fails this type-check.

So good so far. But that's easy. Let's delve deeper.

Constant Non-Builtin Type Decoration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a trivial function annotated by type hints that are pure-Python
classes rather than builtin types:

.. code-block:: python

   from argparse import ArgumentParser
   from beartype import beartype

   @beartype
   def law_of_the_jungle_5(a_cub_may_be_bought_at_a_price: ArgumentParser):
       return a_cub_may_be_bought_at_a_price

Let's see the wrapper function ``@beartype`` dynamically generated from that:

.. code-block:: python

   def __beartyped_law_of_the_jungle_5(
       *args,
       __beartype_func=__beartype_func,
       __beartypistry=__beartypistry,
       **kwargs
   ):
       # Localize the number of passed positional arguments for efficiency.
       __beartype_args_len = len(args)
       # Localize this positional or keyword parameter if passed *OR* to the
       # sentinel value "__beartypistry" guaranteed to never be passed otherwise.
       __beartype_pith_0 = (
           args[0] if __beartype_args_len > 0 else
           kwargs.get('a_cub_may_be_bought_at_a_price', __beartypistry)
       )

       # If this parameter was passed...
       if __beartype_pith_0 is not __beartypistry:
           # Type-check this passed parameter or return value against this
           # PEP-compliant type hint.
           if not isinstance(__beartype_pith_0, __beartypistry['argparse.ArgumentParser']):
               __beartype_raise_pep_call_exception(
                   func=__beartype_func,
                   pith_name='a_cub_may_be_bought_at_a_price',
                   pith_value=__beartype_pith_0,
               )

       # Call this function with all passed parameters and return the value
       # returned from this call.
       return __beartype_func(*args, **kwargs)

The result is largely the same. The only meaningful difference is the
type-check on line 20:

.. code-block:: python

           if not isinstance(__beartype_pith_0, __beartypistry['argparse.ArgumentParser']):

Since we annotated that function with a pure-Python class rather than builtin
type, ``@beartype`` registered that class with the ``__beartypistry`` at
decoration time and then subsequently looked that class up with its
fully-qualified classname at call time to perform this type-check.

So good so far... so what! Let's spelunk harder.

Constant Shallow Sequence Decoration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a trivial function annotated by type hints that are `PEP
585`_-compliant builtin types subscripted by ignorable arguments:

.. code-block:: python

   from beartype import beartype

   @beartype
   def law_of_the_jungle_6(all_the_jungle_is_thine: list[object]):
       return all_the_jungle_is_thine

Let's see the wrapper function ``@beartype`` dynamically generated from that:

.. code-block:: python

   def __beartyped_law_of_the_jungle_6(
       *args,
       __beartype_func=__beartype_func,
       __beartypistry=__beartypistry,
       **kwargs
   ):
       # Localize the number of passed positional arguments for efficiency.
       __beartype_args_len = len(args)
       # Localize this positional or keyword parameter if passed *OR* to the
       # sentinel value "__beartypistry" guaranteed to never be passed otherwise.
       __beartype_pith_0 = (
           args[0] if __beartype_args_len > 0 else
           kwargs.get('all_the_jungle_is_thine', __beartypistry)
       )

       # If this parameter was passed...
       if __beartype_pith_0 is not __beartypistry:
           # Type-check this passed parameter or return value against this
           # PEP-compliant type hint.
           if not isinstance(__beartype_pith_0, list):
               __beartype_raise_pep_call_exception(
                   func=__beartype_func,
                   pith_name='all_the_jungle_is_thine',
                   pith_value=__beartype_pith_0,
               )

       # Call this function with all passed parameters and return the value
       # returned from this call.
       return __beartype_func(*args, **kwargs)

We are still within the realm of normalcy. Correctly detecting this type hint
to be subscripted by an ignorable argument, ``@beartype`` only bothered
type-checking this parameter to be an instance of this builtin type:

.. code-block:: python

           if not isinstance(__beartype_pith_0, list):

It's time to iteratively up the ante.

Constant Deep Sequence Decoration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a trivial function annotated by type hints that are `PEP
585`_-compliant builtin types subscripted by builtin types:

.. code-block:: python

   from beartype import beartype

   @beartype
   def law_of_the_jungle_7(kill_everything_that_thou_canst: list[str]):
       return kill_everything_that_thou_canst

Let's see the wrapper function ``@beartype`` dynamically generated from that:

.. code-block:: python

   def __beartyped_law_of_the_jungle_7(
       *args,
       __beartype_func=__beartype_func,
       __beartypistry=__beartypistry,
       **kwargs
   ):
       # Generate and localize a sufficiently large pseudo-random integer for
       # subsequent indexation in type-checking randomly selected container items.
       __beartype_random_int = __beartype_getrandbits(64)
       # Localize the number of passed positional arguments for efficiency.
       __beartype_args_len = len(args)
       # Localize this positional or keyword parameter if passed *OR* to the
       # sentinel value "__beartypistry" guaranteed to never be passed otherwise.
       __beartype_pith_0 = (
           args[0] if __beartype_args_len > 0 else
           kwargs.get('kill_everything_that_thou_canst', __beartypistry)
       )

       # If this parameter was passed...
       if __beartype_pith_0 is not __beartypistry:
           # Type-check this passed parameter or return value against this
           # PEP-compliant type hint.
           if not (
               # True only if this pith shallowly satisfies this hint.
               isinstance(__beartype_pith_0, list) and
               # True only if either this pith is empty *OR* this pith is
               # both non-empty and deeply satisfies this hint.
               (not __beartype_pith_0 or isinstance(__beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)], str))
           ):
               __beartype_raise_pep_call_exception(
                   func=__beartype_func,
                   pith_name='kill_everything_that_thou_canst',
                   pith_value=__beartype_pith_0,
               )

       # Call this function with all passed parameters and return the value
       # returned from this call.
       return __beartype_func(*args, **kwargs)

We have now diverged from normalcy. Let's dismantle this iota by iota:

* ``__beartype_random_int`` is a pseudo-random unsigned 32-bit integer whose
  bit length intentionally corresponds to the `number of bits generated by each
  call to Python's C-based Mersenne Twister <random twister_>`__ internally
  performed by the random.getrandbits_ function generating this integer.
  Exceeding this length would cause that function to internally perform that
  call multiple times for no gain. Since the cost of generating integers to
  this length is the same as generating integers of smaller lengths, this
  length is preferred. Since most sequences are likely to contain fewer items
  than this integer, pseudo-random sequence items are indexable by taking the
  modulo of this integer with the sizes of those sequences. For big sequences
  containing more than this number of items, ``beartype`` deeply type-checks
  leading items with indices in this range while ignoring trailing items. Given
  the practical infeasibility of storing big sequences in memory, this seems an
  acceptable real-world tradeoff. Suck it, big sequences!
* As before, ``@beartype`` first type-checks this parameter to be a list.
* ``@beartype`` then type-checks this parameter to either be:

  * ``not __beartype_pith_0``, an empty list.
  * ``isinstance(__beartype_pith_0[__beartype_random_int %
    len(__beartype_pith_0)], str)``, a non-empty list whose pseudo-randomly
    indexed list item satisfies this nested builtin type.

Well, that escalated quickly.

Constant Nested Deep Sequence Decoration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a trivial function annotated by type hints that are `PEP
585`_-compliant builtin types recursively subscripted by instances of
themselves, because *we are typing masochists*:

.. code-block:: python

   from beartype import beartype

   @beartype
   def law_of_the_jungle_8(pull_thorns_from_all_wolves_paws: (
       list[list[list[str]]])):
       return pull_thorns_from_all_wolves_paws

Let's see the wrapper function ``@beartype`` dynamically generated from that:

.. code-block:: python

   def __beartyped_law_of_the_jungle_8(
       *args,
       __beartype_func=__beartype_func,
       __beartypistry=__beartypistry,
       **kwargs
   ):
       # Generate and localize a sufficiently large pseudo-random integer for
       # subsequent indexation in type-checking randomly selected container items.
       __beartype_random_int = __beartype_getrandbits(32)
       # Localize the number of passed positional arguments for efficiency.
       __beartype_args_len = len(args)
       # Localize this positional or keyword parameter if passed *OR* to the
       # sentinel value "__beartypistry" guaranteed to never be passed otherwise.
       __beartype_pith_0 = (
           args[0] if __beartype_args_len > 0 else
           kwargs.get('pull_thorns_from_all_wolves_paws', __beartypistry)
       )

       # If this parameter was passed...
       if __beartype_pith_0 is not __beartypistry:
           # Type-check this passed parameter or return value against this
           # PEP-compliant type hint.
           if not (
               # True only if this pith shallowly satisfies this hint.
               isinstance(__beartype_pith_0, list) and
               # True only if either this pith is empty *OR* this pith is
               # both non-empty and deeply satisfies this hint.
               (not __beartype_pith_0 or (
                   # True only if this pith shallowly satisfies this hint.
                   isinstance(__beartype_pith_1 := __beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)], list) and
                   # True only if either this pith is empty *OR* this pith is
                   # both non-empty and deeply satisfies this hint.
                   (not __beartype_pith_1 or (
                       # True only if this pith shallowly satisfies this hint.
                       isinstance(__beartype_pith_2 := __beartype_pith_1[__beartype_random_int % len(__beartype_pith_1)], list) and
                       # True only if either this pith is empty *OR* this pith is
                       # both non-empty and deeply satisfies this hint.
                       (not __beartype_pith_2 or isinstance(__beartype_pith_2[__beartype_random_int % len(__beartype_pith_2)], str))
                   ))
               ))
           ):
               __beartype_raise_pep_call_exception(
                   func=__beartype_func,
                   pith_name='pull_thorns_from_all_wolves_paws',
                   pith_value=__beartype_pith_0,
               )

       # Call this function with all passed parameters and return the value
       # returned from this call.
       return __beartype_func(*args, **kwargs)

We are now well beyond the deep end, where the benthic zone and the cruel
denizens of the fathomless void begins. Let's dismantle this pascal by pascal:

* ``__beartype_pith_1 := __beartype_pith_0[__beartype_random_int %
  len(__beartype_pith_0)]``, a `PEP 572`_-style assignment expression
  localizing repeatedly accessed random items of the first nested list for
  efficiency.
* ``__beartype_pith_2 := __beartype_pith_1[__beartype_random_int %
  len(__beartype_pith_1)]``, a similar expression localizing repeatedly
  accessed random items of the second nested list.
* The same ``__beartype_random_int`` pseudo-randomly indexes all three lists.
* Under older Python interpreters lacking `PEP 572`_ support, ``@beartype``
  generates equally valid (albeit less efficient) code repeating each
  nested list item access.

In the kingdom of the linear-time runtime type checkers, the constant-time
runtime type checker really stands out like a sore giant squid, doesn't it?

See the Developers_ section for further commentary on runtime optimization from
the higher-level perspective of architecture and internal API design.

Developers
==========

Let's contribute `pull requests`_ to ``beartype`` for the good of typing_. The
`primary maintainer of this repository is a friendly beardless Canadian guy
<leycec_>`__ who guarantees that he will *always* be nice and congenial and
promptly merge all requests that pass continuous integration (CI) tests.

And thanks for merely reading this! Like all open-source software, ``beartype``
thrives on community contributions, activity, and interest. *This means you,
stalwart Python hero.*

``beartype`` has two problem spots (listed below in order of decreasing
importance and increasing complexity) that could *always* benefit from a
volunteer army of good GitHub Samaritans. Let's take this from the top.

Moar Depth
----------

So, you want to help ``beartype`` deeply type-check even *more* type hints than
she already does? Let us help you help us, because you are awesome.

First, an egregious lore dump. It's commonly assumed that ``beartype`` only
internally implements a single type-checker. After all, every *other* static
and runtime type-checker only internally implements a single type-checker.
Why would a type-checker internally implement several divergent overlapping
type-checkers and... what would that even mean? Who would be so vile, cruel,
and sadistic as to do something like that?

*We would.* ``beartype`` often violates assumptions. This is no exception.
Externally, of course, ``beartype`` presents itself as a single type-checker.
Internally, ``beartype`` is implemented as a two-phase series of orthogonal
type-checkers. Why? Because efficiency, which is the reason we are all here.
These type-checkers are (in the order that callables decorated by ``beartype``
perform them at runtime):

#. **Testing phase.** In this fast first pass, each callable decorated by
   ``@beartype`` only *tests* whether all parameters passed to and values
   returned from the current call to that callable satisfy all type hints
   annotating that callable. This phase does *not* raise human-readable
   exceptions (in the event that one or more parameters or return values fails
   to satisfy these hints). ``@beartype`` highly optimizes this phase by
   dynamically generating one wrapper function wrapping each decorated callable
   with unique pure-Python performing these tests in O(1) constant-time. This
   phase is *always* unconditionally performed by code dynamically generated
   and returned by:

   * The fast-as-lightning ``pep_code_check_hint()`` function declared in the
     `"beartype._decor._code._pep._pephint" submodule <beartype pephint_>`__,
     which generates memoized O(1) code type-checking an arbitrary object
     against an arbitrary PEP-compliant type hint by iterating over all child
     hints nested in that hint with a highly optimized breadth-first search
     (BFS) leveraging extreme caching, fragile cleverness, and other salacious
     micro-optimizations.

#. **Error phase.** In this slow second pass, each call to a callable decorated
   by ``@beartype`` that fails the fast first pass (due to one or more
   parameters or return values failing to satisfy these hints) recursively
   discovers the exact underlying cause of that failure and raises a
   human-readable exception precisely detailing that cause. ``@beartype`` does
   *not* optimize this phase whatsoever. Whereas the implementation of the
   first phase is uniquely specific to each decorated callable and constrained
   to O(1) constant-time non-recursive operation, the implementation of the
   second phase is generically shared between all decorated callables and
   generalized to O(n) linear-time recursive operation. Efficiency no longer
   matters when you're raising exceptions. Exception handling is slow in any
   language and doubly slow in dynamically-typed (and mostly interpreted)
   languages like Python, which means that performance is mostly a non-concern
   in "cold" code paths guaranteed to raise exceptions. This phase is only
   *conditionally* performed when the first phase fails by:

   * The slow-as-molasses ``raise_pep_call_exception()`` function declared in
     the `"beartype._decor._code._pep._error.peperror" submodule <beartype
     peperror_>`__, which generates human-readable exceptions after performing
     unmemoized O(n) type-checking of an arbitrary object against a
     PEP-compliant type hint by recursing over all child hints nested in that
     hint with an unoptimized recursive algorithm prioritizing debuggability,
     readability, and maintainability.

This separation of concerns between performant O(1) *testing* on the one hand
and perfect O(n) *error handling* on the other preserves both runtime
performance and readable errors at a cost of developer pain. This is good!
:sup:`...what?`

Secondly, the same separation of concerns also complicates the development of
``@beartype``. This is bad. Since ``@beartype`` internally implements two
divergent type-checkers, deeply type-checking a new category of type hint
requires adding that support to (wait for it) two divergent type-checkers –
which, being fundamentally distinct codebases sharing little code in common,
requires violating the `Don't Repeat Yourself (DRY) principle <DRY_>`__ by
reinventing the wheel in the second type-checker. Such is the high price of
high-octane performance. You probably thought this would be easier and funner.
So did we.

Thirdly, this needs to be tested. After surmounting the above roadblocks by
deeply type-checking that new category of type hint in *both* type-checkers,
you'll now add one or more unit tests exhaustively exercising that checking.
Thankfully, we already did all of the swole lifting for you. All *you* need to
do is add at least one PEP-compliant type hint, one object satisfying that
hint, and one object *not* satisfying that hint to:

* A new ``PepHintMetadata`` object in the existing tuple passed to the
  ``data_module.HINTS_PEP_META.extend(...)`` call in the existing test data
  submodule for this PEP residing under the
  `"beartype_test.unit.data.hint.pep.proposal" subpackage <beartype test data
  pep_>`__. For example, if this is a `PEP 484`_-compliant type hint, add that
  hint and associated metadata to the
  `"beartype_test.unit.data.hint.pep.proposal.data_hintpep484" submodule
  <beartype test data pep 484_>`__.

You're done! *Praise Guido.*

Moar Compliance
---------------

So, you want to help ``beartype`` comply with even *more* `Python Enhancement
Proposals (PEPs) <PEP 0_>`__ than she already complies with? Let us help you
help us, because you are young and idealistic and you mean well.

You will need a spare life to squander. A clone would be most handy. In short,
you will want to at least:

* Define a new utility submodule for this PEP residing under the
  `"beartype._util.hint.pep.proposal" subpackage <beartype util pep_>`__
  implementing general-purpose validators, testers, getters, and other
  ancillary utility functions required to detect and handle *all* type hints
  compliant with this PEP. For efficiency, utility functions performing
  iteration or other expensive operations should be memoized via our internal
  `@callable_cached`_ decorator.
* Define a new data utility submodule for this PEP residing under the
  `"beartype._util.hint.data.pep.proposal" subpackage <beartype util data
  pep_>`__ adding various signs (i.e., arbitrary objects uniquely identifying
  type hints compliant with this PEP) to various global variables defined by
  the parent `"beartype._util.hint.data.pep.utilhintdatapep" submodule
  <_beartype util data pep parent>`__.
* Define a new test data submodule for this PEP residing under the
  `"beartype_test.unit.data.hint.pep.proposal" subpackage <beartype test data
  pep_>`__.

You're probably not done by a long shot! But the above should at least get you
fitfully started, though long will you curse our names. *Praise Cleese.*

License
=======

``beartype`` is `open-source software released <beartype license_>`__ under the
`permissive MIT license <MIT license_>`__.

Funding
=======

``beartype`` is currently financed as a purely volunteer open-source project –
which is to say, it's unfinanced. Prior funding sources (*yes, they once
existed*) include:

#. A `Paul Allen Discovery Center award`_ from the `Paul G. Allen Frontiers
   Group`_ under the administrative purview of the `Paul Allen Discovery
   Center`_ at `Tufts University`_ over the period 2015—2018 preceding the
   untimely death of `Microsoft co-founder Paul Allen <Paul Allen_>`__, during
   which ``beartype`` was maintained as the private ``@type_check`` decorator
   in the `Bioelectric Tissue Simulation Engine (BETSE) <BETSE_>`__.
   :superscript:`Phew!`

Authors
=======

``beartype`` is developed with the grateful assistance of a volunteer community
of enthusiasts, including (*in chronological order of issue or pull request*):

#. `Cecil Curry (@leycec) <leycec_>`__. :superscript:`Hi! It's me.` From
   beartype's early gestation as a nondescript ``@type_check`` decorator
   in the `Bioelectric Tissue Simulation Engine (BETSE) <BETSE_>`__ to its
   general-audience release as a `public package supported across multiple
   Python and platform-specific package managers <Install_>`__, I shepherd the
   fastest, hardest, and deepest runtime type-checking solution in any
   dynamically-typed language towards a well-typed future of PEP-compliance and
   boundless quality assurance. *Cue epic taiko drumming.*
#. `Felix Hildén (@felix-hilden) <felix-hilden_>`__, the Finnish `computer
   vision`_ expert world-renowned for his effulgent fun-loving disposition
   *and*:

   * `Branding beartype with the Logo of the Decade <beartype felix-hilden
     branding_>`__, say nine out of ten Finnish brown bears. "The other bears
     are just jelly," claims Hildén.
   * `Documenting beartype with its first Sphinx-based directory structure
     <beartype felix-hilden docs structure_>`__.
   * `Configuring that structure for Read The Docs (RTD)-friendly rendering
     <beartype felix-hilden docs RTD confs_>`__.

#. `@harens <harens_>`__, the boisterous London developer acclaimed for his
   defense of British animals that quack pridefully as they peck you in city
   parks *as well as* `maintaining our first third-party package, a
   macOS-specific MacPorts Portfile estimated to solve all your problems
   <beartype harens MacPorts_>`__.

See Also
========

**Runtime type checkers** (i.e., third-party mostly pure-Python packages
dynamically validating Python callable types at Python runtime, typically via
decorators, explicit function calls, and import hooks) include:

.. # Note: intentionally sorted in lexicographic order to avoid bias.

* ``beartype``. :sup:`...sup.`
* enforce_.
* pytypes_.
* typeen_.
* typeguard_.

**Static type checkers** (i.e., third-party tooling *not* implemented in Python
statically validating Python callable and/or variable types across a full
application stack at tool rather than Python runtime) include:

.. # Note: intentionally sorted in lexicographic order to avoid bias.

* mypy_.
* Pyre_, published by FaceBook. :sup:`...yah.`
* pyright_, published by Microsoft.
* pytype_, published by Google.

.. # ------------------( IMAGES                             )------------------
.. |beartype-logo| image:: https://raw.githubusercontent.com/beartype/beartype-assets/main/banner/logo-small.png
   :target: https://beartype.rtfd.org
   :alt: Beartype logo

.. |GitHub Actions badge| image:: https://github.com/beartype/beartype/workflows/tests/badge.svg
   :target: https://github.com/beartype/beartype/actions?workflow=tests
   :alt: GitHub Actions status

.. # ------------------( LINKS ~ beartype : local           )------------------
.. _beartype license:
   LICENSE

.. # ------------------( LINKS ~ beartype : local : module  )------------------
.. _beartype peperror:
   beartype/_decor/_code/_pep/_error/peperror.py
.. _beartype pephint:
   beartype/_decor/_code/_pep/_pephint.py
.. _beartype test data pep:
   beartype_test/unit/data/hint/pep/proposal/
.. _beartype test data pep 484:
   beartype_test/unit/data/hint/pep/proposal/data_hintpep484.py
.. _@callable_cached:
   beartype/_util/cache/utilcachecall.py
.. _beartype util data pep:
   beartype/_util/hint/data/pep/proposal/
.. _beartype util data pep parent:
   beartype/_util/hint/data/pep/utilhintdatapep.py
.. _beartype util pep:
   beartype/_util/hint/pep/proposal

.. # ------------------( LINKS ~ beartype : contributions   )------------------
.. _beartype felix-hilden branding:
   https://github.com/beartype/beartype/issues/8#issuecomment-760103474
.. _beartype felix-hilden docs structure:
   https://github.com/beartype/beartype/pull/8
.. _beartype felix-hilden docs RTD confs:
   https://github.com/beartype/beartype/pull/9
.. _beartype harens MacPorts:
   https://github.com/beartype/beartype/issues/12

.. # ------------------( LINKS ~ beartype : package         )------------------
.. _beartype Anaconda:
   https://anaconda.org/conda-forge/beartype
.. _beartype Gentoo:
   https://github.com/leycec/raiagent
.. _beartype MacPorts:
   https://ports.macports.org/port/py-beartype
.. _beartype PyPI:
   https://pypi.org/project/beartype

.. # ------------------( LINKS ~ beartype : remote          )------------------
.. _beartype 1.0.0:
   https://github.com/beartype/beartype/issues/7
.. _codebase:
   https://github.com/beartype/beartype/tree/main/beartype
.. _profiler suite:
   https://github.com/beartype/beartype/blob/main/bin/profile.bash
.. _pull requests:
   https://github.com/beartype/beartype/pulls
.. _tests:
   https://github.com/beartype/beartype/actions?workflow=tests

.. # ------------------( LINKS ~ beartype : funding         )------------------
.. _BETSE:
   https://gitlab.com/betse/betse
.. _BETSEE:
   https://gitlab.com/betse/betsee
.. _Paul Allen:
   https://en.wikipedia.org/wiki/Paul_Allen
.. _Paul Allen Discovery Center:
   http://www.alleninstitute.org/what-we-do/frontiers-group/discovery-centers/allen-discovery-center-tufts-university
.. _Paul Allen Discovery Center award:
   https://www.alleninstitute.org/what-we-do/frontiers-group/news-press/press-resources/press-releases/paul-g-allen-frontiers-group-announces-allen-discovery-center-tufts-university
.. _Paul G. Allen Frontiers Group:
   https://www.alleninstitute.org/what-we-do/frontiers-group
.. _Tufts University:
   https://www.tufts.edu

.. # ------------------( LINKS ~ github                     )------------------
.. _GitHub Actions:
   https://github.com/features/actions

.. # ------------------( LINKS ~ github : user              )------------------
.. _felix-hilden:
   https://github.com/felix-hilden
.. _harens:
   https://github.com/harens
.. _leycec:
   https://github.com/leycec

.. # ------------------( LINKS ~ idea                       )------------------
.. _Denial-of-Service:
   https://en.wikipedia.org/wiki/Denial-of-service_attack
.. _DRY:
   https://en.wikipedia.org/wiki/Don%27t_repeat_yourself
.. _SQA:
   https://en.wikipedia.org/wiki/Software_quality_assurance
.. _amortized analysis:
   https://en.wikipedia.org/wiki/Amortized_analysis
.. _computer vision:
   https://en.wikipedia.org/wiki/Computer_vision
.. _random walk:
   https://en.wikipedia.org/wiki/Random_walk
.. _shield wall:
   https://en.wikipedia.org/wiki/Shield_wall
.. _zero-cost abstraction:
   https://boats.gitlab.io/blog/post/zero-cost-abstractions

.. # ------------------( LINKS ~ kipling                    )------------------
.. _The Jungle Book:
   https://www.gutenberg.org/files/236/236-h/236-h.htm
.. _Shere Khan:
   https://en.wikipedia.org/wiki/Shere_Khan

.. # ------------------( LINKS ~ lang                       )------------------
.. _C++:
   https://en.wikipedia.org/wiki/C%2B%2B
.. _Rust:
   https://www.rust-lang.org

.. # ------------------( LINKS ~ license                    )------------------
.. _MIT license:
   https://opensource.org/licenses/MIT

.. # ------------------( LINKS ~ math                       )------------------
.. _Euler–Mascheroni constant:
   https://en.wikipedia.org/wiki/Euler%E2%80%93Mascheroni_constant
.. _coupon collector's problem:
   https://en.wikipedia.org/wiki/Coupon_collector%27s_problem
.. _covariance:
   https://en.wikipedia.org/wiki/Covariance_and_contravariance_(computer_science)

.. # ------------------( LINKS ~ meme                       )------------------
.. _RNGesus:
   https://knowyourmeme.com/memes/rngesus
.. _goes up to eleven:
   https://www.youtube.com/watch?v=uMSV4OteqBE
.. _greased lightning:
   https://www.youtube.com/watch?v=H-kL8A4RNQ8
.. _ludicrous speed:
   https://www.youtube.com/watch?v=6tTvklMXeFE
.. _the gripping hand:
   http://catb.org/jargon/html/O/on-the-gripping-hand.html

.. # ------------------( LINKS ~ os : linux                 )------------------
.. _Gentoo:
   https://www.gentoo.org

.. # ------------------( LINKS ~ os : macos                 )------------------
.. _macOS:
   https://en.wikipedia.org/wiki/MacOS
.. _HomeBrew:
   https://brew.sh
.. _HomeBrew Python packaging:
   https://github.com/numpy/numpy/issues/11454#issuecomment-401423500
.. _MacPorts:
   https://www.macports.org

.. # ------------------( LINKS ~ py                         )------------------
.. _Python:
   https://www.python.org
.. _Python status:
   https://devguide.python.org/#status-of-python-branches
.. _pip:
   https://pip.pypa.io

.. # ------------------( LINKS ~ py : article               )------------------
.. _Guido van Rossum:
   https://en.wikipedia.org/wiki/Guido_van_Rossum
.. _RealPython:
   https://realpython.com/python-type-checking

.. # ------------------( LINKS ~ py : cli                   )------------------
.. _-O:
   https://docs.python.org/3/using/cmdline.html#cmdoption-o
.. _PYTHONOPTIMIZE:
   https://docs.python.org/3/using/cmdline.html#envvar-PYTHONOPTIMIZE

.. # ------------------( LINKS ~ py : data model            )------------------
.. _generic alias parameters:
   https://docs.python.org/3/library/stdtypes.html#genericalias.__parameters__
.. _isinstancecheck:
   https://docs.python.org/3/reference/datamodel.html#customizing-instance-and-subclass-checks
.. _mro:
   https://docs.python.org/3/library/stdtypes.html#class.__mro__
.. _object:
   https://docs.python.org/3/reference/datamodel.html#basic-customization

.. # ------------------( LINKS ~ py : interpreter           )------------------
.. _CPython:
   https://github.com/python/cpython
.. _Nuitka:
   https://nuitka.net
.. _Numba:
   https://numba.pydata.org
.. _PyPy:
   https://www.pypy.org

.. # ------------------( LINKS ~ py : package               )------------------
.. _NetworkX:
   https://networkx.org
.. _Pandas:
   https://pandas.pydata.org
.. _PyTorch:
   https://pytorch.org
.. _Sphinx:
   https://www.sphinx-doc.org/en/master
.. _SymPy:
   https://www.sympy.org

.. # ------------------( LINKS ~ py : package : numpy       )------------------
.. _NumPy:
   https://numpy.org
.. _numpy.empty_like:
   https://numpy.org/doc/stable/reference/generated/numpy.empty_like.html

.. # ------------------( LINKS ~ py : package : test        )------------------
.. _pytest:
   https://docs.pytest.org
.. _tox:
   https://tox.readthedocs.io

.. # ------------------( LINKS ~ py : pep                   )------------------
.. _PEP 0:
   https://www.python.org/dev/peps
.. _PEP 20:
   https://www.python.org/dev/peps/pep-0020
.. _PEP 483:
   https://www.python.org/dev/peps/pep-0483
.. _PEP 526:
   https://www.python.org/dev/peps/pep-0526
.. _PEP 544:
   https://www.python.org/dev/peps/pep-0544
.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
.. _PEP 570:
   https://www.python.org/dev/peps/pep-0570
.. _PEP 572:
   https://www.python.org/dev/peps/pep-0572
.. _PEP 585:
   https://www.python.org/dev/peps/pep-0585
.. _PEP 586:
   https://www.python.org/dev/peps/pep-0586
.. _PEP 589:
   https://www.python.org/dev/peps/pep-0589
.. _PEP 591:
   https://www.python.org/dev/peps/pep-0591
.. _PEP 593:
   https://www.python.org/dev/peps/pep-0593
.. _PEP 3141:
   https://www.python.org/dev/peps/pep-3141

.. # ------------------( LINKS ~ py : pep : 3119            )------------------
.. _PEP 3119:
   https://www.python.org/dev/peps/pep-3119
.. _virtual base classes:
   https://www.python.org/dev/peps/pep-3119/#id33

.. # ------------------( LINKS ~ py : pep : 484             )------------------
.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
.. _relative forward references:
   https://www.python.org/dev/peps/pep-0484/#id28

.. # ------------------( LINKS ~ py : pep : 560             )------------------
.. _PEP 560:
   https://www.python.org/dev/peps/pep-0560
.. _mro_entries:
   https://www.python.org/dev/peps/pep-0560/#id20

.. # ------------------( LINKS ~ py : service               )------------------
.. _Anaconda:
   https://docs.conda.io/en/latest/miniconda.html
.. _PyPI:
   https://pypi.org

.. # ------------------( LINKS ~ py : stdlib : abc          )------------------
.. _abc:
   https://docs.python.org/3/library/abc.html
.. _abc.ABCMeta:
   https://docs.python.org/3/library/abc.html#abc.ABCMeta

.. # ------------------( LINKS ~ py : stdlib : builtins     )------------------
.. _builtins:
   https://docs.python.org/3/library/stdtypes.html
.. _None:
   https://docs.python.org/3/library/constants.html#None
.. _dict:
   https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
.. _dir:
   https://docs.python.org/3/library/functions.html#dir
.. _frozenset:
   https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset
.. _list:
   https://docs.python.org/3/library/stdtypes.html#lists
.. _memoryview:
   https://docs.python.org/3/library/stdtypes.html#memory-views
.. _range:
   https://docs.python.org/3/library/stdtypes.html#typesseq-range
.. _set:
   https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset
.. _tuple:
   https://docs.python.org/3/library/stdtypes.html#tuples
.. _type:
   https://docs.python.org/3/library/stdtypes.html#bltin-type-objects

.. # ------------------( LINKS ~ py : stdlib : collections  }------------------
.. _collections:
   https://docs.python.org/3/library/collections.html
.. _collections.ChainMap:
   https://docs.python.org/3/library/collections.html#collections.ChainMap
.. _collections.Counter:
   https://docs.python.org/3/library/collections.html#collections.Counter
.. _collections.OrderedDict:
   https://docs.python.org/3/library/collections.html#collections.OrderedDict
.. _collections.defaultdict:
   https://docs.python.org/3/library/collections.html#collections.defaultdict
.. _collections.deque:
   https://docs.python.org/3/library/collections.html#collections.deque

.. # ------------------( LINKS ~ py : stdlib : collections.abc }---------------
.. _collections.abc:
   https://docs.python.org/3/library/collections.abc.html
.. _collections.abc.AsyncGenerator:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncGenerator
.. _collections.abc.AsyncIterable:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterable
.. _collections.abc.AsyncIterator:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterator
.. _collections.abc.Awaitable:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Awaitable
.. _collections.abc.ByteString:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.ByteString
.. _collections.abc.Callable:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable
.. _collections.abc.Collection:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Collection
.. _collections.abc.Container:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Container
.. _collections.abc.Coroutine:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Coroutine
.. _collections.abc.Generator:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Generator
.. _collections.abc.ItemsView:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.ItemsView
.. _collections.abc.Iterable:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable
.. _collections.abc.Iterator:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator
.. _collections.abc.KeysView:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.KeysView
.. _collections.abc.Mapping:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping
.. _collections.abc.MappingView:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.MappingView
.. _collections.abc.MutableMapping:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping
.. _collections.abc.MutableSequence:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSequence
.. _collections.abc.MutableSet:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSet
.. _collections.abc.Reversible:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Reversible
.. _collections.abc.Sequence:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence
.. _collections.abc.Set:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.Set
.. _collections.abc.ValuesView:
   https://docs.python.org/3/library/collections.abc.html#collections.abc.ValuesView

.. # ------------------( LINKS ~ py : stdlib : contextlib   )------------------
.. _contextlib:
   https://docs.python.org/3/library/contextlib.html
.. _contextlib.AbstractAsyncContextManager:
   https://docs.python.org/3/library/contextlib.html#contextlib.AbstractAsyncContextManager
.. _contextlib.AbstractContextManager:
   https://docs.python.org/3/library/contextlib.html#contextlib.AbstractContextManager

.. # ------------------( LINKS ~ py : stdlib : io           )------------------
.. _io:
   https://docs.python.org/3/library/io.html

.. # ------------------( LINKS ~ py : stdlib : os           )------------------
.. _os:
   https://docs.python.org/3/library/os.html
.. _os.walk:
   https://docs.python.org/3/library/os.html#os.walk

.. # ------------------( LINKS ~ py : stdlib : random       )------------------
.. _random:
   https://docs.python.org/3/library/random.html
.. _random.getrandbits:
   https://docs.python.org/3/library/random.html#random.getrandbits
.. _random twister:
   https://stackoverflow.com/a/11704178/2809027

.. # ------------------( LINKS ~ py : stdlib : re           )------------------
.. _re:
   https://docs.python.org/3/library/re.html
.. _re.Match:
   https://docs.python.org/3/library/re.html#match-objects
.. _re.Pattern:
   https://docs.python.org/3/library/re.html#regular-expression-objects

.. # ------------------( LINKS ~ py : stdlib : typing : attr)------------------
.. _typing:
   https://docs.python.org/3/library/typing.html
.. _typing.AbstractSet:
   https://docs.python.org/3/library/typing.html#typing.AbstractSet
.. _typing.Annotated:
   https://docs.python.org/3/library/typing.html#typing.Annotated
.. _typing.Any:
   https://docs.python.org/3/library/typing.html#typing.Any
.. _typing.AnyStr:
   https://docs.python.org/3/library/typing.html#typing.AnyStr
.. _typing.AsyncContextManager:
   https://docs.python.org/3/library/typing.html#typing.AsyncContextManager
.. _typing.AsyncGenerator:
   https://docs.python.org/3/library/typing.html#typing.AsyncGenerator
.. _typing.AsyncIterable:
   https://docs.python.org/3/library/typing.html#typing.AsyncIterable
.. _typing.AsyncIterator:
   https://docs.python.org/3/library/typing.html#typing.AsyncIterator
.. _typing.Awaitable:
   https://docs.python.org/3/library/typing.html#typing.Awaitable
.. _typing.BinaryIO:
   https://docs.python.org/3/library/typing.html#typing.BinaryIO
.. _typing.ByteString:
   https://docs.python.org/3/library/typing.html#typing.ByteString
.. _typing.Callable:
   https://docs.python.org/3/library/typing.html#typing.Callable
.. _typing.ChainMap:
   https://docs.python.org/3/library/typing.html#typing.ChainMap
.. _typing.ClassVar:
   https://docs.python.org/3/library/typing.html#typing.ClassVar
.. _typing.Collection:
   https://docs.python.org/3/library/typing.html#typing.Collection
.. _typing.Container:
   https://docs.python.org/3/library/typing.html#typing.Container
.. _typing.ContextManager:
   https://docs.python.org/3/library/typing.html#typing.ContextManager
.. _typing.Coroutine:
   https://docs.python.org/3/library/typing.html#typing.Coroutine
.. _typing.Counter:
   https://docs.python.org/3/library/typing.html#typing.Counter
.. _typing.DefaultDict:
   https://docs.python.org/3/library/typing.html#typing.DefaultDict
.. _typing.Deque:
   https://docs.python.org/3/library/typing.html#typing.Deque
.. _typing.Dict:
   https://docs.python.org/3/library/typing.html#typing.Dict
.. _typing.ForwardRef:
   https://docs.python.org/3/library/typing.html#typing.ForwardRef
.. _typing.FrozenSet:
   https://docs.python.org/3/library/typing.html#typing.FrozenSet
.. _typing.Generator:
   https://docs.python.org/3/library/typing.html#typing.Generator
.. _typing.Generic:
   https://docs.python.org/3/library/typing.html#typing.Generic
.. _typing.Hashable:
   https://docs.python.org/3/library/typing.html#typing.Hashable
.. _typing.IO:
   https://docs.python.org/3/library/typing.html#typing.IO
.. _typing.ItemsView:
   https://docs.python.org/3/library/typing.html#typing.ItemsView
.. _typing.Iterable:
   https://docs.python.org/3/library/typing.html#typing.Iterable
.. _typing.Iterator:
   https://docs.python.org/3/library/typing.html#typing.Iterator
.. _typing.KeysView:
   https://docs.python.org/3/library/typing.html#typing.KeysView
.. _typing.List:
   https://docs.python.org/3/library/typing.html#typing.List
.. _typing.Literal:
   https://docs.python.org/3/library/typing.html#typing.Literal
.. _typing.Mapping:
   https://docs.python.org/3/library/typing.html#typing.Mapping
.. _typing.MappingView:
   https://docs.python.org/3/library/typing.html#typing.MappinViewg
.. _typing.Match:
   https://docs.python.org/3/library/typing.html#typing.Match
.. _typing.MutableMapping:
   https://docs.python.org/3/library/typing.html#typing.MutableMapping
.. _typing.MutableSequence:
   https://docs.python.org/3/library/typing.html#typing.MutableSequence
.. _typing.MutableSet:
   https://docs.python.org/3/library/typing.html#typing.MutableSet
.. _typing.NamedTuple:
   https://docs.python.org/3/library/typing.html#typing.NamedTuple
.. _typing.NewType:
   https://docs.python.org/3/library/typing.html#typing.NewType
.. _typing.NoReturn:
   https://docs.python.org/3/library/typing.html#typing.NoReturn
.. _typing.Optional:
   https://docs.python.org/3/library/typing.html#typing.Optional
.. _typing.OrderedDict:
   https://docs.python.org/3/library/typing.html#typing.OrderedDict
.. _typing.Pattern:
   https://docs.python.org/3/library/typing.html#typing.Pattern
.. _typing.Protocol:
   https://docs.python.org/3/library/typing.html#typing.Protocol
.. _typing.Reversible:
   https://docs.python.org/3/library/typing.html#typing.Reversible
.. _typing.Sequence:
   https://docs.python.org/3/library/typing.html#typing.Sequence
.. _typing.Set:
   https://docs.python.org/3/library/typing.html#typing.Set
.. _typing.Sized:
   https://docs.python.org/3/library/typing.html#typing.Sized
.. _typing.SupportsAbs:
   https://docs.python.org/3/library/typing.html#typing.SupportsAbs
.. _typing.SupportsBytes:
   https://docs.python.org/3/library/typing.html#typing.SupportsBytes
.. _typing.SupportsComplex:
   https://docs.python.org/3/library/typing.html#typing.SupportsComplex
.. _typing.SupportsFloat:
   https://docs.python.org/3/library/typing.html#typing.SupportsFloat
.. _typing.SupportsIndex:
   https://docs.python.org/3/library/typing.html#typing.SupportsIndex
.. _typing.SupportsInt:
   https://docs.python.org/3/library/typing.html#typing.SupportsInt
.. _typing.SupportsRound:
   https://docs.python.org/3/library/typing.html#typing.SupportsRound
.. _typing.Text:
   https://docs.python.org/3/library/typing.html#typing.Text
.. _typing.TextIO:
   https://docs.python.org/3/library/typing.html#typing.TextIO
.. _typing.Tuple:
   https://docs.python.org/3/library/typing.html#typing.Tuple
.. _typing.Type:
   https://docs.python.org/3/library/typing.html#typing.Type
.. _typing.TypedDict:
   https://docs.python.org/3/library/typing.html#typing.TypedDict
.. _typing.TypeVar:
   https://docs.python.org/3/library/typing.html#typing.TypeVar
.. _typing.Union:
   https://docs.python.org/3/library/typing.html#typing.Union
.. _typing.ValuesView:
   https://docs.python.org/3/library/typing.html#typing.ValuesView
.. _typing.Final:
   https://docs.python.org/3/library/typing.html#typing.Final
.. _@typing.final:
   https://docs.python.org/3/library/typing.html#typing.final
.. _@typing.no_type_check:
   https://docs.python.org/3/library/typing.html#typing.no_type_check
.. _typing.TYPE_CHECKING:
   https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING

.. # ------------------( LINKS ~ py : type : runtime        )------------------
.. _enforce:
   https://github.com/RussBaz/enforce
.. _pytypes:
   https://github.com/Stewori/pytypes
.. _typeen:
   https://github.com/k2bd/typen
.. _typeguard:
   https://github.com/agronholm/typeguard

.. # ------------------( LINKS ~ py : type : static         )------------------
.. _Pyre:
   https://pyre-check.org
.. _mypy:
   http://mypy-lang.org
.. _pytype:
   https://github.com/google/pytype
.. _pyright:
   https://github.com/Microsoft/pyright
