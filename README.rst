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

Unlike comparable runtime type checkers (e.g., typeguard_), beartype
dynamically wraps each decorated callable with a unique wrapper implementing
strongly optimized type-checking for that callable. Since "performance by
default" is our first-class concern, *all* wrappers are guaranteed to:

* Exhibit ``O(1)`` time complexity with negligible constant factors.
* Be either more efficient (in the common case) or exactly as efficient minus
  the cost of an additional stack frame (in the worst case) as equivalent
  type-checking implemented by hand.

Beartype thus brings Rust_- and `C++`_-inspired `zero-cost abstractions
<zero-cost abstraction_>`__ into the deliciously lawless world of pure Python.

Beartype is `portably implemented <codebase_>`__ in pure `Python 3`_,
`continuously stress-tested <tests_>`__ with `GitHub Actions`_ **+** tox_ **+**
pytest_, and `permissively distributed <license_>`__ under the `MIT license`_.

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

.. code-block:: shell-session

   pip3 install beartype

.. #FIXME: Uncomment the following *AFTER* releasing to PyPI and conda-forge.
..
.. # Beartype is universally installable with either:
..
.. # - [\ *Recommended*\ ] pip_, the standard Python package manager:
..
.. #   .. code-block:: shell-session
..
.. #      pip3 install beartype
..
.. # - Anaconda_, a third-party Python package manager:
..
.. #   .. code-block:: shell-session
..
.. #      conda config --add channels conda-forge
.. #      conda install beartype

Cheatsheet
==========

Let's type-check like greased lightning:

.. code-block:: python

   # Import the core @beartype decorator.
   from beartype import beartype

   # Import generic types for use with @beartype.
   from beartype.cave import (
       AnyType,
       FunctionTypes,
       CallableTypes,
       GeneratorType,
       IntOrNoneTypes,
       IterableTypes,
       IteratorType,
       NoneType,
       NumericTypes,
       RegexTypes,
       ScalarTypes,
       SequenceTypes,
       VersionTypes,
   )

   # Import user-defined classes for use with @beartype, too.
   from my_package.my_module import MyClass

   # Decorate functions with @beartype and...
   @beartype
   def bare_necessities(
       # Annotate builtin types as is, delimited by a colon (":" character).
       param1_must_be_of_type: str,

       # Annotate user-defined classes as is, too.
       param2_must_be_of_type: MyClass,

       # Annotate fully-qualified classnames dynamically resolved at call time
       # (referred to as "forward references") as "."-delimited strings.
       param3_must_be_of_type: 'my_package.my_module.MyClass',

       # Annotate unions of types as tuples. In PEP 484, this is equivalent to:
       # param4_may_be_any_of_several_types: typing.Union[dict, MyClass, None,]
       param4_may_be_any_of_several_types: (dict, MyClass, NoneType,),

       # Annotate unions of types as tuples predefined by the beartype cave.
       param5_may_be_any_of_several_types: SequenceTypes,

       # Annotate unions of types as tuples containing both types and
       # fully-qualified classnames.
       param6_may_be_any_of_several_types: (
           list, 'my_package.my_module.MyOtherClass', NoneType,),

       # Annotate unions of types as tuples concatenated together.
       param7_may_be_any_of_several_types: (str, int,) + IterableTypes,

       # Annotate variadic positional arguments as above, too.
       *args: VersionTypes + (NoneType, 'my_package.my_module.MyVersionType',)
   # Annotate return types as above, delimited by an arrow ("->" substring).
   ) -> (
       NumericTypes + (str, 'my_package.my_module.MyOtherClass', bool)):
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
       def bare_settermethod(
           self, bad: IntOrNoneTypes = 0xBAAAAAAD) -> NoneType:
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
   from beartype.cave import GeneratorType, IterableTypes, NoneType

   class MaximsOfBaloo(object):
       @beartype
       def __init__(self, sayings: IterableTypes): 
           self.sayings = sayings

   @beartype
   def inform_baloo(maxims: MaximsOfBaloo) -> GeneratorType: 
       for saying in maxims.sayings:
           yield saying

For genericity, the ``MaximsOfBaloo`` class initializer accepts *any* generic
iterable (via the ``beartype.cave.IterableTypes`` tuple listing all valid
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
   File "<ipython-input-10-7763b15e5591>", line 30, in <module>
     '     but hail them as Sister and Brother,',
   File "<string>", line 12, in __inform_baloo_beartyped__
   beartype.roar.BeartypeCallTypeParamException: @beartyped inform_baloo() parameter maxims=['Oppress not the cubs of the stranger,', '     but hail them as Sister and ...'] not a <class '__main__.MaximsOfBaloo'>.

Good generator! The type hints applied to these callables now accurately
document their respective APIs. Thanks to the pernicious magic of beartype, all
ends typed well... *yet again.*

.. # Tuples of Arbitrary Types
.. # -------------------------

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
.. _Python 3:
   https://www.python.org
.. _pip:
   https://pip.pypa.io

.. # ------------------( LINKS ~ py : implementation        )------------------
.. _CPython:
.. _PyPy:
   .
.. _Numba:
   https://numba.pydata.org

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
