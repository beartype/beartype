.. # ------------------( SYNOPSIS                           )------------------

=====================================================
beartype ———[ …the barely there type checker ]———
=====================================================

|GitHub Actions badge|

.. parsed-literal::

   Look for the bare necessities,
     the simple bare necessities.
   Forget about your worries and your strife.

                           — `The Jungle Book`_.

**Beartype** is an open-source pure-Python runtime type checker emphasizing
efficiency, portability, and thrilling puns.

Unlike comparable static type checkers operating at the coarse-grained
application level (e.g., Pyre_, mypy_, pyright_, pytype_), beartype operates
exclusively at the fine-grained callable level of pure-Python functions and
methods via the standard decorator design pattern. This renders beartype
natively compatible with *all* interpreters and compilers targeting the Python
language – including CPython_, PyPy_, and Numba_.

Unlike comparable runtime type checkers (e.g., typeguard_), beartype wraps each
decorated callable with a dynamically generated wrapper efficiently
type-checking that specific callable. Since "performance by default" is our
first-class concern, *all* wrappers are guaranteed to:

* Exhibit ``O(1)`` time complexity with negligible constant factors.
* Be either more efficient (in the common case) or exactly as efficient minus
  the cost of an additional stack frame (in the worst case) as equivalent
  type-checking implemented by hand.

Beartype thus brings Rust_- and `C++`_-inspired `zero-cost abstractions
<zero-cost abstraction_>`__ into the deliciously lawless world of pure Python.

Beartype is `portably implemented <codebase_>`__ in `pure Python 3
<Python_>`__, `continuously stress-tested <tests_>`__ with `GitHub Actions`_
**+** tox_ **+** pytest_, and `permissively distributed <license_>`__ under the
`MIT license`_. Beartype has no runtime dependencies, `only one test-time
dependency <pytest_>`__, and supports `all Python 3.x releases still in active
development <Python status_>`__.

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

Installation
============

Let's install ``beartype`` with pip_, because community standards are good:

.. code-block:: shell-session

   pip3 install beartype

Let's install ``beartype`` with Anaconda_, because corporate standards are
sometimes good, too:

.. code-block:: shell-session

   conda config --add channels conda-forge
   conda install beartype

Cheatsheet
==========

Let's type-check like greased lightning:

.. code-block:: python

   # Import the core @beartype decorator.
   from beartype import beartype

   # Import generic types for use with @beartype.
   from beartype.cave import (
       AnyType,
       BoolType,
       FunctionTypes,
       CallableTypes,
       GeneratorType,
       IntOrFloatType,
       IntType,
       IterableType,
       IteratorType,
       NoneType,
       NoneTypeOr,
       NumberType,
       RegexTypes,
       ScalarTypes,
       SequenceType,
       StrType,
       VersionTypes,
   )

   # Import user-defined classes for use with @beartype, too.
   from my_package.my_module import MyClass

   # Decorate functions with @beartype and...
   @beartype
   def bare_necessities(
       # Annotate builtin types as is, delimited by a colon (":" character).
       param1_must_be_of_builtin_type: str,

       # Annotate user-defined classes as is, too.
       param2_must_be_of_user_type: MyClass,

       # Annotate generic types predefined by the beartype cave.
       param3_must_be_of_generic_type: NumberType,

       # Annotate forward references dynamically resolved (and cached) at first
       # call time as fully-qualified "."-delimited classnames.
       param4_must_be_of_forward_type: 'my_package.my_module.MyClass',

       # Annotate unions of types as tuples. In PEP 484, this is:
       # param5_may_be_any_of_several_types: typing.Union[dict, MyClass, int,],
       param5_may_be_any_of_several_types: (dict, MyClass, int,),

       # Annotate generic unions of types predefined by the beartype cave.
       param6_may_be_any_of_several_generic_types: CallableTypes,

       # Annotate forward references in unions of types, too.
       param7_may_be_any_of_several_forward_types: (
           IterableType, 'my_package.my_module.MyOtherClass', NoneType,),

       # Annotate unions of types as tuples concatenated together.
       param8_may_be_any_of_several_concatenated_types: (
           IteratorType,) + ScalarTypes,

       # Annotate optional types by indexing "NoneTypeOr" with those types. In
       # PEP 484, this is:
       # param9_must_be_of_type_if_passed: typing.Optional[float] = None,
       param9_must_be_of_type_if_passed: NoneTypeOr[float] = None,

       # Annotate optional unions of types by indexing "NoneTypeOr" with tuples
       # of those types. In PEP 484, this is:
       # param10_may_be_of_several_types_if_passed: typing.Optional[float, int] = None,
       param10_may_be_of_several_types_if_passed: NoneTypeOr[(float, int)] = None,

       # Annotate variadic positional arguments as above, too.
       *args: VersionTypes + (
           IntOrFloatType, 'my_package.my_module.MyVersionType',),

       # Annotate keyword-only arguments as above, too.
       paramN_must_be_passed_by_keyword_only: SequenceType,
   # Annotate return types as above, delimited by an arrow ("->" string).
   ) -> (IntType, 'my_package.my_module.MyOtherClass', BoolType):
       return 0xDEADBEEF


   # Decorate generators as above but returning a generator type.
   @beartype
   def bare_generator() -> GeneratorType:
       yield from range(0xBEEFBABE, 0xCAFEBABE)


   class MyCrassClass:
       # Decorate instance methods as above without annotating "self".
       @beartype
       def __init__(self, scalar: ScalarTypes) -> NoneType:
           self._scalar = scalar

       # Decorate class methods as above without annotating "cls". When
       # chaining decorators, "@beartype" should typically be specified last.
       @classmethod
       @beartype
       def bare_classmethod(cls, regex: RegexTypes, wut: str) -> FunctionTypes:
           import re
           return lambda: re.sub(regex, 'unbearable', str(cls._scalar) + wut)

       # Decorate static methods as above.
       @staticmethod
       @beartype
       def bare_staticmethod(callable: CallableTypes, *args: str) -> AnyType:
           return callable(*args)

       # Decorate property getter methods as above.
       @property
       @beartype
       def bare_gettermethod(self) -> IteratorType:
           return range(0x0B00B135 + int(self._scalar), 0xB16B00B5)

       # Decorate property setter methods as above.
       @bare_gettermethod.setter
       @beartype
       def bare_settermethod(self, bad: IntType = 0xBAAAAAAD) -> NoneType:
           self._scalar = bad if bad else 0xBADDCAFE

Usage
=====

The ``@beartype`` decorator published by the ``beartype`` package transparently
supports different types of type-checking, each declared with a different type
of **type hint** (i.e., annotation applied to a parameter or return value of a
callable).

This is simpler than it sounds. Would we lie? Instead of answering that, let's
begin with the simplest type of type-checking supported by ``@beartype``.

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
return either a tuple or ``None``:

.. # as `detailed below <Tuples of Arbitrary Types_>`__:

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
**unions of types.** :superscript:`You can thank set theory for the jargon...
unless you hate set theory. Then it's just our fault.`

Unions of types are trivially type-checked by annotating parameters and return
values with tuples containing those types. Let's declare another beartyped
function accepting either a mapping *or* a string and returning either another
function *or* an integer:

.. code-block:: python

   from beartype import beartype
   from beartype.cave import FunctionType, IntType, MappingType

   @beartype
   def toomai_of_the_elephants(memory: (str, MappingType)) -> (
       IntType, FunctionType):
       return len(memory) if isinstance(memory, str) else lambda key: memory[key]

For genericity, the ``toomai_of_the_elephants`` function accepts *any* generic
integer (via the ``beartype.cave.IntType`` abstract base class (ABC) matching
both builtin integers and third-party integers from frameworks like NumPy_ and
SymPy_) rather than an overly specific ``int`` type. The API you relax may very
well be your own.

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
   >>> toomai_of_the_elephants(memory_of_kala_nag['remember'])
   56
   >>> toomai_of_the_elephants(memory_of_kala_nag)('remember')
   'I will remember what I was, I am sick of rope and chain—'

Good function. Let's call it again with a tastelessly bad type:

.. code-block:: python

   >>> toomai_of_the_elephants(0xDEADBEEF)
   Traceback (most recent call last):
     File "<ipython-input-7-e323f8d6a4a0>", line 1, in <module>
       toomai_of_the_elephants(0xDEADBEEF)
     File "<string>", line 12, in __toomai_of_the_elephants_beartyped__
   BeartypeCallTypeParamException: @beartyped toomai_of_the_elephants() parameter memory=3735928559 not a (<class 'str'>, <class 'collections.abc.Mapping'>).

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
with the ``NoneTypeOr`` tuple factory indexed by those types or tuples of
types.

Let's declare another beartyped function accepting either an enumeration type
*or* ``None`` and returning either an enumeration member *or* ``None``:

.. code-block:: python

   from beartype import beartype
   from beartype.cave import EnumType, EnumMemberType, NoneTypeOr
   from enum import Enum

   class Lukannon(Enum):
       WINTER_WHEAT = 'The Beaches of Lukannon—the winter wheat so tall—'
       SEA_FOG      = 'The dripping, crinkled lichens, and the sea-fog drenching all!'
       PLAYGROUND   = 'The platforms of our playground, all shining smooth and worn!'
       HOME         = 'The Beaches of Lukannon—the home where we were born!'
       MATES        = 'I met my mates in the morning, a broken, scattered band.'
       CLUB         = 'Men shoot us in the water and club us on the land;'
       DRIVE        = 'Men drive us to the Salt House like silly sheep and tame,'
       SEALERS      = 'And still we sing Lukannon—before the sealers came.'

   @beartype
   def tell_the_deep_sea_viceroys(story: NoneTypeOr[EnumType] = None) -> (
       NoneTypeOr[EnumMemberType]):
       return story if story is None else list(story.__members__.values())[-1]

For efficiency, the ``NoneTypeOr`` tuple factory creates, caches, and returns
new tuples of types appending ``NoneType`` to the original types and tuples of
types it's indexed with. Since efficiency is good, ``NoneTypeOr`` is also good.

Let's call that function with good types:

.. code-block:: python

   >>> tell_the_deep_sea_viceroys(Lukannon)
   <Lukannon.SEALERS: 'And still we sing Lukannon—before the sealers came.'>
   >>> tell_the_deep_sea_viceroys()
   None

You may now be pondering to yourself grimly in the dark: "...but could we not
already do this just by manually annotating optional types with tuples
containing ``NoneType``?"

You would, of course, be correct. Let's grimly redeclare the same function
accepting and returning the same types – only annotated with ``NoneType``
rather than ``NoneTypeOr``:

.. code-block:: python

   from beartype import beartype
   from beartype.cave import EnumType, EnumMemberType, NoneType

   @beartype
   def tell_the_deep_sea_viceroys(story: (EnumType, NoneType) = None) -> (
       (EnumMemberType, NoneType)):
       return list(story.__members__.values())[-1] if story is not None else None

This manual approach has the same exact effect as the prior factoried approach
with one exception: the factoried approach efficiently caches and reuses tuples
over every annotated type, whereas the manual approach inefficiently recreates
tuples for each annotated type. For small codebases, that difference is
negligible; for large codebases, that difference is still probably negligible.
Still, "waste not want not" is the maxim we type our lives by here.

Naturally, the ``NoneTypeOr`` tuple factory accepts tuples of types as well.
Let's declare another beartyped function accepting either an enumeration type,
enumeration type member, or ``None`` and returning either an enumeration type,
enumeration type member, or ``None``:

.. code-block:: python

   from beartype import beartype
   from beartype.cave import EnumType, EnumMemberType, NoneTypeOr

   EnumOrEnumMemberType = (EnumType, EnumMemberType)

   @beartype
   def sang_them_up_the_beach(
       woe: NoneTypeOr[EnumOrEnumMemberType] = None) -> (
       NoneTypeOr[EnumOrEnumMemberType]):
       return woe if isinstance(woe, NoneTypeOr[EnumMemberType]) else (
           list(woe.__members__.values())[-1])

Let's call that function with good types:

.. code-block:: python

   >>> sang_them_up_the_beach(Lukannon)
   <Lukannon.SEALERS: 'And still we sing Lukannon—before the sealers came.'>
   >>> sang_them_up_the_beach()
   None

Behold! The terrifying power of the ``NoneTypeOr`` tuple factory, resplendent
in its highly over-optimized cache utilization.

PEP 484 & Friends
-----------------

For efficiency, beartype does *not* currently support any of the rapidly
proliferating **Python Enhancement Proposals (PEPs)** for officially sanctioned
type-checking, including (but *not* limited to):

.. # Note: intentionally sorted in numeric order for collective sanity.

* `PEP 483 -- The Theory of Type Hints <PEP 483_>`__.
* `PEP 484 -- Type Hints <PEP 484_>`__.
* `PEP 544 -- Protocols: Structural subtyping (static duck typing) <PEP
  544_>`_.
* `PEP 526 -- Syntax for Variable Annotations <PEP 526_>`__.
* `PEP 563 -- Postponed Evaluation of Annotations <PEP 563_>`__.
* `PEP 586 -- Literal Types <PEP 586_>`__.
* `PEP 589 -- TypedDict: Type Hints for Dictionaries with a Fixed Set of Keys
  <PEP 589_>`__.

Why? Because implementing even the core `PEP 484`_ standard in pure Python
while preserving beartype's ``O(1)`` time complexity guarantee is infeasible.

Consider a hypothetical `PEP 484`_-compliant ``@slothtype`` decorator
decorating a hypothetical callable accepting a list of strings and returning
anything, like so:

.. code-block:: python
   
   from slothtype import slothtype
   from typing import Any, List

   @slothtype
   def slothful(sluggard: List[str]) -> Any:
       ...

This is hardly the worst-case usage scenario. By compare to some of the more
grotesque outliers enabled by the ``typing`` API (e.g., infinitely recursive
type annotations), a non-nested iterable of scalars is rather tame. Sadly,
``slothful`` still exhibits ``Ω(n)`` time complexity for ``n`` the size of the
passed list, where ``Ω`` may be read as "at least as asymptotically complex as"
under the standard Knuth definition.

**That's bad.** Each call to ``slothful`` now type-checks each item of a list
of arbitrary size *before* performing any meaningful work. Python prohibits
monkey-patching builtin types, so this up-front cost *cannot* be amortized
across all calls to ``slothful`` (e.g., by monkey-patching the builtin ``list``
type to cache the result of prior type-checks of lists previously passed to
``slothful`` and invalidating these caches on external changes to these lists)
but *must* instead be paid on each call to ``slothful``. Ergo, ``Ω(n)``.

PEP 484 & Friends (Redux)
-------------------------

Beartype does intend to support the proper subset of `PEP 484`_ (and its
vituperative band of ne'er-do-wells) that *is* efficiently implementable in
pure Python – whatever that is. Full compliance may be off the map, but at
least partial compliance with the portions of these standards that average
users care about is well within the realm of "maybe?".

Preserving beartype's ``O(1)`` time complexity guarantee is the ultimate
barometer for what will be and will not be implemented. That and @leycec's
declining sanity. Our bumpy roadmap to a better-typed future now resembles:

+------------------+--------------------------------+
| Beartype version | Partial PEP compliance planned |
+------------------+--------------------------------+
| **0.2.0**        | PEP 563                        |
| **1.0.0**        | PEP 484                        |
| **2.0.0**        | PEP 544                        |
| **3.0.0**        | PEP 586                        |
| **4.0.0**        | PEP 589                        |
+------------------+--------------------------------+

If we wish upon a GitHub star, even the improbable is possible.

License
=======

Beartype is `open-source software released <license_>`__ under the
`permissive MIT license <MIT license_>`__.

Funding
=======

Beartype is currently financed as a purely volunteer open-source project –
which is to say, it's unfinanced. Prior funding sources (*yes, they once
existed*) include:

#. Over the period 2015—2018 preceding the untimely death of `Paul Allen`_,
   beartype was graciously associated with the `Paul Allen Discovery Center`_
   at `Tufts University`_ and grant-funded by a `Paul Allen Discovery Center
   award`_ from the `Paul G. Allen Frontiers Group`_ through its parent
   applications – the multiphysics biology simulators BETSE_ and BETSEE_.

See Also
========

**Runtime type checkers** (i.e., third-party mostly pure-Python packages
dynamically validating Python callable types at Python runtime, typically via
decorators, explicit function calls, and import hooks) include:

.. # Note: intentionally sorted in lexicographic order to avoid bias.

* beartype. :sup:`...'sup.`
* typeguard_.

**Static type checkers** (i.e., third-party tooling *not* implemented in Python
statically validating Python callable and/or variable types across a full
application stack at tool rather than Python runtime) include:

.. # Note: intentionally sorted in lexicographic order to avoid bias.

* `Pyre from FaceBook <Pyre_>`__.
* mypy_.
* `pyright from Microsoft <pyright_>`__.
* `pytype from Google <pytype_>`__.

.. # ------------------( IMAGES                             )------------------
.. |GitHub Actions badge| image:: https://github.com/beartype/beartype/workflows/tests/badge.svg
   :target: https://github.com/beartype/beartype/actions?workflow=tests
   :alt: GitHub Actions status

.. # ------------------( LINKS ~ beartype : local           )------------------
.. _license:
   LICENSE

.. # ------------------( LINKS ~ beartype : remote          )------------------
.. _codebase:
   https://github.com/beartype/beartype/tree/master/beartype
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

.. # ------------------( LINKS ~ beartype : issues          )------------------
.. _PEP 484 issue:
   .

.. # ------------------( LINKS ~ kipling                    )------------------
.. _The Jungle Book:
   https://www.gutenberg.org/files/236/236-h/236-h.htm
.. _Shere Khan:
   https://en.wikipedia.org/wiki/Shere_Khan

.. # ------------------( LINKS ~ non-py                     )------------------
.. _C++:
   https://en.wikipedia.org/wiki/C%2B%2B
.. _Rust:
   https://www.rust-lang.org
.. _zero-cost abstraction:
   https://boats.gitlab.io/blog/post/zero-cost-abstractions

.. # ------------------( LINKS ~ py                         )------------------
.. _Anaconda:
   https://docs.conda.io/en/latest/miniconda.html
.. _Python:
   https://www.python.org
.. _Python status:
   https://devguide.python.org/#status-of-python-branches
.. _pip:
   https://pip.pypa.io

.. # ------------------( LINKS ~ py : implementation        )------------------
.. _CPython:
   https://github.com/python/cpython
.. _PyPy:
   https://www.pypy.org
.. _Numba:
   https://numba.pydata.org

.. # ------------------( LINKS ~ py : package               )------------------
.. _NumPy:
   https://numpy.org
.. _SymPy:
   https://www.sympy.org

.. # ------------------( LINKS ~ py : pep                   )------------------
.. _PEP 483:
   https://www.python.org/dev/peps/pep-0483
.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
.. _PEP 526:
   https://www.python.org/dev/peps/pep-0526
.. _PEP 544:
   https://www.python.org/dev/peps/pep-0544
.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
.. _PEP 586:
   https://www.python.org/dev/peps/pep-0586
.. _PEP 589:
   https://www.python.org/dev/peps/pep-0589

.. # ------------------( LINKS ~ py : test                  )------------------
.. _pytest:
   https://docs.pytest.org
.. _tox:
   https://tox.readthedocs.io

.. # ------------------( LINKS ~ py : type : runtime        )------------------
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

.. # ------------------( LINKS ~ service                    )------------------
.. _GitHub Actions:
   https://github.com/features/actions

.. # ------------------( LINKS ~ standard                   )------------------
.. _MIT license:
   https://opensource.org/licenses/MIT
