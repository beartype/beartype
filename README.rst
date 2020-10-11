.. # ------------------( SYNOPSIS                           )------------------

===========================================
beartype —[ …the bare-metal type checker ]—
===========================================

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
language – including CPython_, PyPy_, Numba_, and Nuitka_.

Unlike comparable runtime type checkers (e.g., enforce_, pytypes_, typeguard_),
beartype wraps each decorated callable with a dynamically generated wrapper
efficiently type-checking that specific callable. Since "performance by
default" is our first-class concern, *all* wrappers are guaranteed to:

* Exhibit `O(1) time complexity with negligible constant factors <Nobody
  Believes You_>`__.
* Be either more efficient (in the common case) or exactly as efficient minus
  the cost of an additional stack frame (in the worst case) as equivalent
  type-checking implemented by hand, *which no one should ever do.*

Beartype thus brings Rust_- and `C++`_-inspired `zero-cost abstractions
<zero-cost abstraction_>`__ into the lawless world of pure Python.

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
(occasionally) good too:

.. code-block:: shell-session

   conda config --add channels conda-forge
   conda install beartype

Linux
-----

Let's install ``beartype`` with Gentoo_, because source-based Linux distros are
the computational nuclear option:

.. code-block:: shell-session

   emerge --ask app-eselect/eselect-repository
   mkdir -p /etc/portage/repos.conf
   eselect repository enable raiagent
   emerge --sync raiagent
   emerge beartype

Cheatsheet
==========

Let's type-check like `greased lightning`_:

.. code-block:: python

   # Import the core @beartype decorator.
   from beartype import beartype

   # Import PEP-compliant types for use with @beartype.
   from typing import List, Optional, Union

   # Import beartype-specific types for use with @beartype, too.
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

   # Import user-defined types for use with @beartype, three.
   from my_package.my_module import MyClass

   # Decorate functions with @beartype and...
   @beartype
   def bare_necessities(
       # Annotate builtin types as is.
       param_must_satisfy_builtin_type: str,

       # Annotate user-defined types as is, too.
       param_must_satisfy_user_type: MyClass,

       # Annotate PEP-compliant types predefined by the "typing" module.
       param_must_satisfy_pep_type: List[int],

       # Annotate beartypes-specific types predefined by the beartype cave.
       param_must_satisfy_beartype_type_from_cave: NumberType,

       # Annotate PEP-compliant unions of types.
       param_must_satisfy_pep_union: Union[dict, MyClass, int,],

       # Annotate beartype-specific unions of types as tuples, too.
       param_must_satisfy_beartype_union: (dict, MyClass, int,),

       # Annotate beartype-specific unions predefined by the beartype cave.
       param_must_satisfy_beartype_union_from_cave: CallableTypes,

       # Annotate beartype-specific unions concatenated together.
       param_must_satisfy_beartype_union_concatenated: (
           IteratorType,) + ScalarTypes,

       # Annotate beartype-specific forward references dynamically resolved 
       # at first call time as fully-qualified "."-delimited classnames.
       param_must_satisfy_beartype_forward_ref: 'my_package.my_module.MyClass',

       # Annotate beartype-specific forward references in unions of types, too.
       param_must_satisfy_beartype_union_with_forward_ref: (
           IterableType, 'my_package.my_module.MyOtherClass', NoneType,),

       # Annotate PEP-compliant optional types.
       param_must_satisfy_pep_type_optional: Optional[float] = None,

       # Annotate beartype-specific optional types.
       param_must_satisfy_beartype_type_optional: NoneTypeOr[float] = None,

       # Annotate PEP-compliant optional unions of types.
       param_must_satisfy_pep_tuple_optional: Optional[Union[float, int]]) = None,

       # Annotate beartype-specific optional unions of types.
       param_must_satisfy_beartype_tuple_optional: NoneTypeOr[float, int] = None,

       # Annotate variadic positional arguments as above, too.
       *args: VersionTypes + (IntOrFloatType, 'my_package.my_module.MyVersionType',),

       # Annotate keyword-only arguments as above, too.
       param_must_be_passed_by_keyword_only: SequenceType,

   # Annotate return types as above, too.
   ) -> (IntType, 'my_package.my_module.MyOtherOtherClass', BoolType):
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

Timings
=======

Let's run our `profiler suite quantitatively timing <profiler suite_>`__
``beartype`` and fellow runtime type-checkers against a battery of surely fair,
impartial, and unbiased use cases:

.. code-block:: shell-session

   beartype profiler [version]: 0.0.2
   
   python    [version]: Python 3.7.8
   beartype  [version]: 0.3.0
   typeguard [version]: 2.9.1
   
   ========================== str (100 calls each loop) ==========================
   decoration         [none     ]: 100 loops, best of 3: 366 nsec per loop
   decoration         [beartype ]: 100 loops, best of 3: 346 usec per loop
   decoration         [typeguard]: 100 loops, best of 3: 13.4 usec per loop
   decoration + calls [none     ]: 100 loops, best of 3: 16.4 usec per loop
   decoration + calls [beartype ]: 100 loops, best of 3: 480 usec per loop
   decoration + calls [typeguard]: 100 loops, best of 3: 7 msec per loop
   
   ==================== Union[int, str] (100 calls each loop) ====================
   decoration         [none     ]: 100 loops, best of 3: 2.97 usec per loop
   decoration         [beartype ]: 100 loops, best of 3: 363 usec per loop
   decoration         [typeguard]: 100 loops, best of 3: 16.7 usec per loop
   decoration + calls [none     ]: 100 loops, best of 3: 20.4 usec per loop
   decoration + calls [beartype ]: 100 loops, best of 3: 543 usec per loop
   decoration + calls [typeguard]: 100 loops, best of 3: 11.1 msec per loop
   
   ================ List[int] of 1000 items (7485 calls each loop) ================
   decoration         [none     ]: 1 loop, best of 1: 41.7 usec per loop
   decoration         [beartype ]: 1 loop, best of 1: 1.33 msec per loop
   decoration         [typeguard]: 1 loop, best of 1: 82.2 usec per loop
   decoration + calls [none     ]: 1 loop, best of 1: 1.4 msec per loop
   decoration + calls [beartype ]: 1 loop, best of 1: 22.5 msec per loop
   decoration + calls [typeguard]: 1 loop, best of 1: 124 sec per loop

.. note::
   * ``sec`` = seconds.
   * ``msec`` = milliseconds = 10\ :sup:`-3` seconds.
   * ``usec`` = microseconds = 10\ :sup:`-6` seconds.
   * ``nsec`` = nanoseconds = 10\ :sup:`-9` seconds.

ELI5
----

On the one hand, ``beartype`` is:

* **At least twenty times faster** (i.e., 20,000%) and takes **three orders of
  magnitude less time** in the worst case than typeguard_ – the only comparable
  runtime type-checker also compatible with all modern versions of Python.
* **Asymptotically faster** in the best case than typeguard_, which scales
  linearly (rather than not at all) with the size of checked containers.
* Constant across type hints, taking roughly the same time to check parameters
  and return values hinted by the builtin type ``str`` as it does to check
  those hinted by the synthetic type ``Union[int, str]`` as it does to check
  those hinted by the container type ``List[object]``. typeguard_ is
  variable across type hints, taking infinitely longer to check
  ``List[object]`` as as it does to check ``Union[int, str]``, taking roughly
  twice the time as it does to check ``str``.

:sup:`so that's good`

On the other hand, ``beartype`` is only partially compliant with
annotation-centric `Python Enhancement Proposals (PEPs) <PEP 0_>`__ like `PEP
484`_, whereas typeguard_ is *mostly* fully compliant with these PEPs.
:sup:`so that's bad`

But... How?
-----------

``beartype`` performs the lion's share of its work at decoration time. The
``@beartype`` decorator consumes most of the time needed to first decorate and
then repeatedly call a decorated function. ``beartype`` is thus front-loaded.
After paying the initial cost of decoration, each type-checked call thereafter
incurs comparatively little overhead.

All other runtime type checkers perform the lion's share of their work at call
time. ``@typeguard.typechecked`` and similar decorators consume almost none of
the time needed to first decorate and then repeatedly call a decorated
function. They're thus back-loaded. Although the initial cost of decoration is
essentially free, each type-checked call thereafter incurs significant
overhead.

Nobody Believes You
-------------------

Math time, people. :sup:`it's happening`

Most runtime type-checkers exhibit ``O(n)`` time complexity (where ``n`` is the
total number of items recursively contained in a container to be checked) by
recursively and repeatedly checking *all* items of *all* containers passed to
or returned from *all* calls of decorated callables.

``beartype`` guarantees ``O(1)`` time complexity by non-recursively but
repeatedly checking *one* random item from *each* nesting level of *all*
containers passed to or returned from *all* calls of decorated callables, thus
amortizing the cost of checking items across calls.

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

Usage
=====

The ``@beartype`` decorator published by the ``beartype`` package transparently
supports two fundamentally different types of callable type hints – each with
its own tradeoffs, tribal dogmas, religious icons, and zealous code
inquisitors:

* `Beartype-specific type hints <Beartype-specific Type Hints_>`__, which:

  * Are highly performant in both space and time. (\ *That's good.*\ )
    Efficiency is our raison d'être, after all. If your use case doesn't need
    efficiency, consider adopting an alternate runtime type-checker more
    compatible with Python's existing type-checking landscape – like
    typeguard_.
  * Are incapable of deeply type-checking the contents, elements, items,
    metadata, structure, or other attributes of passed parameters and returned
    values. (\ *That's bad.*\ )
  * Are fully supported by ``beartype``. (\ *That's good.*\ )
  * Do *not* comply with existing `Python Enhancement Proposals (PEPs) <PEP
    0_>`__. (\ *That's bad, arguably.*\ )

* `PEP-compliant type hints <PEP-compliant Type Hints_>`__, which:
  
  * Are highly inefficient in both space and time. (\ *That's bad.*\ )
  * Are capable of deeply type-checking the contents, elements, items,
    metadata, structure, and other attributes of passed parameters and returned
    values. (\ *That's good.*\ )
  * Are only partially supported by ``beartype``. (\ *That's bad.*\ )
  * Comply with existing PEPs. (\ *That's good, arguably.*\ )

Callers may freely intermingle these two types and thus obtain "the best of
both worlds" when annotating parameters and return values. All else being
equal, your maxim to type by ``beartype`` should be:

.. parsed-literal::

     Use `beartype-specific type hints <Beartype-specific Type Hints_>`__
       where sufficient.
     Use `PEP-compliant type hints <PEP-compliant Type Hints_>`__
       everywhere else.

Beartype-specific Type Hints
----------------------------

This is simpler than it sounds. Would we lie? Instead of answering that, let's
begin with the simplest type of type-checking supported by ``@beartype``.

Builtin Types
~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~

That's all typed well, but everything above only applies to parameters and
return values constrained to *singular* types. In practice, parameters and
return values are often relaxed to any of *multiple* types referred to as
**unions of types.** :sup:`You can thank set theory for the jargon... unless
you hate set theory. Then it's just our fault.`

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
++++++++++++++

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

PEP-compliant Type Hints
------------------------

``beartype`` is fully compliant with these `Python Enhancement Proposals (PEPs)
<PEP 0_>`__:

* `PEP 563 -- Postponed Evaluation of Annotations <PEP 563_>`__.

``beartype`` is partially compliant with these PEPs:

* `PEP 483 -- The Theory of Type Hints <PEP 483_>`__, subject to `caveats
  detailed below <PEP 484 Compliance_>`__
* `PEP 484 -- Type Hints <PEP 484_>`__, subject to `caveats detailed below
  <PEP 484 Compliance_>`__.

``beartype`` is currently *not* compliant whatsoever with these PEPs:

* `PEP 526 -- Syntax for Variable Annotations <PEP 526_>`__.
* `PEP 544 -- Protocols: Structural subtyping (static duck typing) <PEP
  544_>`_.
* `PEP 585 -- Type Hinting Generics In Standard Collections <PEP 585_>`__.
* `PEP 586 -- Literal Types <PEP 586_>`__.
* `PEP 589 -- TypedDict: Type Hints for Dictionaries with a Fixed Set of Keys
  <PEP 589_>`__.
* `PEP 591 -- Adding a final qualifier to typing <PEP 591_>`__.
* `PEP 593 -- Flexible function and variable annotations <PEP 593_>`__.

See also the **PEP** and **typing** categories of our `features matrix
<Features_>`__ for further details.

PEP 484 Compliance
~~~~~~~~~~~~~~~~~~

``beartype`` is only partially compliant with `PEP 483`_ and `484 <PEP
484_>`__. Let's see what that means in practice.

Full Compliance
+++++++++++++++

``beartype`` **deeply type-checks** (i.e., directly checks the types of *and*
recursively checks the types of items contained in) parameters and return
values annotated with these typing_ types:

* typing.Any_.
* typing.ByteString_.
* typing.List_.
* typing.MutableSequence_.
* typing.Optional_.
* typing.Sequence_.
* typing.Sized_.
* typing.SupportsAbs_.
* typing.SupportsBytes_.
* typing.SupportsComplex_.
* typing.SupportsInt_.
* typing.SupportsFloat_.
* typing.SupportsRound_.
* typing.Text_.
* typing.Union_.

Partial Compliance
++++++++++++++++++

``beartype`` currently only **shallowly type-checks** (i.e., only directly
checks the types of) parameters and return values annotated with these typing_
types:

* typing.AbstractSet_.
* typing.AsyncIterable_.
* typing.AsyncIterator_.
* typing.Awaitable_.
* typing.Callable_.
* typing.ChainMap_.
* typing.Container_.
* typing.Coroutine_.
* typing.Counter_.
* typing.DefaultDict_.
* typing.Deque_.
* typing.Dict_.
* typing.FrozenSet_.
* typing.Generator_.
* typing.Hashable_.
* typing.ItemsView_.
* typing.Iterable_.
* typing.Iterator_.
* typing.KeysView_.
* typing.MappingView_.
* typing.Mapping_.
* typing.MutableMapping_.
* typing.MutableSet_.
* typing.NamedTuple_.
* typing.Set_.
* typing.Tuple_.
* typing.Type_.
* typing.TypedDict_.
* typing.ValuesView_.

Subsequent ``beartype`` versions will deeply type-check these typing_ types
while preserving our `O(1) time complexity (with negligible constant factors)
guarantee <Nobody Believes You_>`__.

No Compliance
+++++++++++++

``beartype`` currently raises exceptions at decoration time when passed these
typing_ types:

* `Forward references <relative forward references_>`__ (i.e., unqualified
  relative string classnames internally coerced by typing_ into
  typing.ForwardRef_ instances).
* Forward reference-subscripted types (i.e., typing_ objects subscripted by one
  or more `forward references <relative forward references_>`__).
* Type variables (i.e., typing.TypeVar_ instances enabling general-purpose
  type-checking of generically substitutable types).
* Type variable-parametrized types (i.e., typing_ objects subscripted by one or
  more type variables).
* User-defined generics (i.e., user-defined classes subclassing one or more
  typing_ non-classes).
* User-defined protocols (i.e., user-defined classes transitively subclassing
  the typing.Protocol_ abstract base class (ABC)).
* typing.Annotated_.
* typing.AnyStr_.
* typing.BinaryIO_.
* typing.ClassVar_.
* typing.IO_.
* typing.Match_.
* typing.NewType_.
* typing.NoReturn_.
* typing.Pattern_.
* typing.TextIO_.
* typing.Final_.
* `@typing.final`_.

Subsequent ``beartype`` versions will first shallowly and then deeply
type-check these typing_ types while preserving our `O(1) time complexity (with
negligible constant factors) guarantee <Nobody Believes You_>`__.

Features
========

Let's chart current and prospective new features for future generations:

.. # FIXME: Span category cells across multiple rows.

+-------------+-------------------------------------+-------------------------------+---------------------------+
| category    | feature                             | versions partially supporting | versions fully supporting |
+=============+=====================================+===============================+===========================+
| decoratable | classes                             | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | coroutines                          | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | functions                           | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | generators                          | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | methods                             | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
| parameters  | optional                            | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | keyword-only                        | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | positional-only                     | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | variadic keyword                    | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | variadic positional                 | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
| hints       | `covariant <covariance_>`__         | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `contravariant <covariance_>`__     | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | absolute forward references         | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `relative forward references`_      | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `tuple unions <Unions of Types_>`__ | **0.1.0**\ —\ *current*       | **0.1.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
| typing_     | typing.AbstractSet_                 | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Annotated_                   | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Any_                         | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.AnyStr_                      | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.AsyncContextManager_         | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.AsyncGenerator_              | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.AsyncIterable_               | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.AsyncIterator_               | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Awaitable_                   | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.BinaryIO_                    | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.ByteString_                  | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Callable_                    | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.ChainMap_                    | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.ClassVar_                    | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Collection_                  | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Container_                   | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.ContextManager_              | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Coroutine_                   | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Counter_                     | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.DefaultDict_                 | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Deque_                       | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Dict_                        | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Final_                       | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.ForwardRef_                  | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.FrozenSet_                   | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Generator_                   | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Generic_                     | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Hashable_                    | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.IO_                          | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.ItemsView_                   | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Iterable_                    | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Iterator_                    | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.KeysView_                    | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.List_                        | **0.2.0**\ —\ *current*       | **0.3.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Mapping_                     | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.MappingView_                 | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Match_                       | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.MutableMapping_              | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.MutableSequence_             | **0.2.0**\ —\ *current*       | **0.3.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.MutableSet_                  | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.NamedTuple_                  | **0.1.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.NewType_                     | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.NoReturn_                    | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Optional_                    | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.OrderedDict_                 | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Pattern_                     | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Protocol_                    | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Reversible_                  | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Sequence_                    | **0.2.0**\ —\ *current*       | **0.3.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Set_                         | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Sized_                       | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.SupportsAbs_                 | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.SupportsBytes_               | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.SupportsComplex_             | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.SupportsFloat_               | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.SupportsIndex_               | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.SupportsInt_                 | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.SupportsRound_               | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Text_                        | **0.1.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.TextIO_                      | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Tuple_                       | **0.2.0**\ —\ *current*       | **0.4.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Type_                        | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.TypedDict_                   | **0.1.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.TypeVar_                     | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.Union_                       | **0.2.0**\ —\ *current*       | **0.2.0**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | typing.ValuesView_                  | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `@typing.final`_                    | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
| PEP         | `484 <PEP 484_>`__                  | **0.2.0**\ —\ *current*       | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `544 <PEP 544_>`__                  | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `563 <PEP 563_>`__                  | **0.1.1**\ —\ *current*       | **0.1.1**\ —\ *current*   |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `585 <PEP 585_>`__                  | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `586 <PEP 586_>`__                  | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `589 <PEP 589_>`__                  | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `591 <PEP 591_>`__                  | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `593 <PEP 593_>`__                  | *none*                        | *none*                    |
+-------------+-------------------------------------+-------------------------------+---------------------------+
| packages    | `PyPI <beartype PyPI_>`__           | **0.1.0**\ —\ *current*       | —                         |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `Anaconda <beartype Anaconda_>`__   | **0.1.0**\ —\ *current*       | —                         |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | `Gentoo <beartype Gentoo_>`__       | **0.2.0**\ —\ *current*       | —                         |
+-------------+-------------------------------------+-------------------------------+---------------------------+
| Python      | 3.5                                 | **0.1.0**\ —\ **0.3.0**       | —                         |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | 3.6                                 | **0.1.0**\ —\ *current*       | —                         |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | 3.7                                 | **0.1.0**\ —\ *current*       | —                         |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | 3.8                                 | **0.1.0**\ —\ *current*       | —                         |
+-------------+-------------------------------------+-------------------------------+---------------------------+
|             | 3.9                                 | **0.3.2**\ —\ *current*       | —                         |
+-------------+-------------------------------------+-------------------------------+---------------------------+

License
=======

``beartype`` is `open-source software released <license_>`__ under the
`permissive MIT license <MIT license_>`__.

Funding
=======

``beartype`` is currently financed as a purely volunteer open-source project –
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

* ``beartype``. :sup:`...sup.`
* enforce_.
* pytypes_.
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
.. |GitHub Actions badge| image:: https://github.com/beartype/beartype/workflows/tests/badge.svg
   :target: https://github.com/beartype/beartype/actions?workflow=tests
   :alt: GitHub Actions status

.. # ------------------( LINKS ~ beartype : local           )------------------
.. _license:
   LICENSE

.. # ------------------( LINKS ~ beartype : package         )------------------
.. _beartype Anaconda:
   https://anaconda.org/conda-forge/beartype
.. _beartype Gentoo:
   https://github.com/leycec/raiagent
.. _beartype PyPI:
   https://pypi.org/project/beartype

.. # ------------------( LINKS ~ beartype : remote          )------------------
.. _codebase:
   https://github.com/beartype/beartype/tree/master/beartype
.. _profiler suite:
   https://github.com/beartype/beartype/blob/master/bin/profile.bash
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

.. # ------------------( LINKS ~ kipling                    )------------------
.. _The Jungle Book:
   https://www.gutenberg.org/files/236/236-h/236-h.htm
.. _Shere Khan:
   https://en.wikipedia.org/wiki/Shere_Khan

.. # ------------------( LINKS ~ math                       )------------------
.. _Euler–Mascheroni constant:
   https://en.wikipedia.org/wiki/Euler%E2%80%93Mascheroni_constant
.. _coupon collector's problem:
   https://en.wikipedia.org/wiki/Coupon_collector%27s_problem
.. _covariance:
   https://en.wikipedia.org/wiki/Covariance_and_contravariance_(computer_science)

.. # ------------------( LINKS ~ meme                       )------------------
.. _greased lightning:
   https://www.youtube.com/watch?v=H-kL8A4RNQ8
.. _the gripping hand:
   http://catb.org/jargon/html/O/on-the-gripping-hand.html

.. # ------------------( LINKS ~ non-py                     )------------------
.. _Denial-of-Service:
   https://en.wikipedia.org/wiki/Denial-of-service_attack
.. _zero-cost abstraction:
   https://boats.gitlab.io/blog/post/zero-cost-abstractions

.. # ------------------( LINKS ~ non-py : lang              )------------------
.. _C++:
   https://en.wikipedia.org/wiki/C%2B%2B
.. _Rust:
   https://www.rust-lang.org

.. # ------------------( LINKS ~ non-py : os : linux        )------------------
.. _Gentoo:
   https://www.gentoo.org

.. # ------------------( LINKS ~ service                    )------------------
.. _GitHub Actions:
   https://github.com/features/actions

.. # ------------------( LINKS ~ standard                   )------------------
.. _MIT license:
   https://opensource.org/licenses/MIT

.. # ------------------( LINKS ~ py                         )------------------
.. _Python:
   https://www.python.org
.. _Python status:
   https://devguide.python.org/#status-of-python-branches
.. _pip:
   https://pip.pypa.io

.. # ------------------( LINKS ~ py : implementation        )------------------
.. _CPython:
   https://github.com/python/cpython
.. _Nuitka:
   https://nuitka.net
.. _Numba:
   https://numba.pydata.org
.. _PyPy:
   https://www.pypy.org

.. # ------------------( LINKS ~ py : package               )------------------
.. _NumPy:
   https://numpy.org
.. _SymPy:
   https://www.sympy.org

.. # ------------------( LINKS ~ py : pep                   )------------------
.. _PEP 0:
   https://www.python.org/dev/peps
.. _PEP 20:
   https://www.python.org/dev/peps/pep-0020
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
.. _PEP 570:
   https://www.python.org/dev/peps/pep-0570
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

.. # ------------------( LINKS ~ py : service               )------------------
.. _Anaconda:
   https://docs.conda.io/en/latest/miniconda.html
.. _PyPI:
   https://pypi.org

.. # ------------------( LINKS ~ py : test                  )------------------
.. _pytest:
   https://docs.pytest.org
.. _tox:
   https://tox.readthedocs.io

.. # ------------------( LINKS ~ py : type : runtime        )------------------
.. _enforce:
   https://github.com/RussBaz/enforce
.. _pytypes:
   https://github.com/Stewori/pytypes
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

.. # ------------------( LINKS ~ py : typing                )------------------
.. _typing:
   https://docs.python.org/3/library/typing.html
.. _relative forward references:
   https://www.python.org/dev/peps/pep-0484/#id28

.. # ------------------( LINKS ~ py : typing : attribute    )------------------
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
