.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Root reStructuredText (reST) document transitively referencing all other
.. # child reST documents for this project.
.. #
.. # ------------------( SEO                                 )------------------
.. # Metadata converted into HTML-specific meta tags parsed by search engines.
.. # Note that:
.. # * The "description" should be no more than 300 characters and ideally no
.. #   more than 150 characters, as search engines may silently truncate this
.. #   description to 150 characters in edge cases.

.. meta::
   :description lang=en:
     Beartype is an open-source pure-Python PEP-compliant constant-time runtime
     type-checker emphasizing efficiency and portability.

.. # ------------------( MAIN                                )------------------

|beartype-banner|

|codecov-badge| |ci-badge| |rtd-badge|

**Beartype** is an `open-source <beartype license_>`__ `PEP-compliant
<Compliance_>`__ `near-real-time <beartype realtime_>`__ `pure-Python runtime
type-checker <Introduction_>`__ emphasizing efficiency, usability, and thrilling puns.

.. #FIXME: Once we actually receive a sponsor at this tier, please remove this
.. #placeholder as well as the icon links below. kthx
.. #The `Bear Team <beartype organization_>`__ gratefully thanks `our family of
.. #breathtaking GitHub Sponsors <beartype sponsorship_>`__:
.. #
.. #* **Your iconic URL here.** `Let us bestow you with eyeballs <beartype
.. #  sponsorship_>`__.
.. #FIXME: Once we actually receive a sponsor at this tier, please remove this
.. #placeholder as well as the icon links below. kthx
.. #    |icon-for-glorious-sponsor|

.. code-block:: bash

   # Install beartype.
   $ pip3 install beartype
   # So let's do this.
   $ python3

.. code-block:: pycon

   # Import the @beartype decorator.
   >>> from beartype import beartype

   # Annotate @beartype-decorated classes and callables with type hints.
   >>> @beartype
   ... def quote_wiggum(lines: list[str]) -> None:
   ...     print('“{}”\n\t— Police Chief Wiggum'.format("\n ".join(lines)))

   # Call those callables with valid parameters.
   >>> quote_wiggum(["Okay, folks. Show's over!", " Nothing to see here. Show's…",])
   “Okay, folks. Show's over!
    Nothing to see here. Show's…”
      — Police Chief Wiggum

   # Call those callables with invalid parameters.
   >>> quote_wiggum([b"Oh, my God! A horrible plane crash!", b"Hey, everybody! Get a load of this flaming wreckage!",])
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "<string>", line 30, in quote_wiggum
     File "/home/springfield/beartype/lib/python3.9/site-packages/beartype/_decor/_code/_pep/_error/errormain.py", line 220, in get_beartype_violation
       raise exception_cls(
   beartype.roar.BeartypeCallHintParamViolation: @beartyped
   quote_wiggum() parameter lines=[b'Oh, my God! A horrible plane
   crash!', b'Hey, everybody! Get a load of thi...'] violates type hint
   list[str], as list item 0 value b'Oh, my God! A horrible plane crash!'
   not str.

   # ..................{ VALIDATORS  }..................
   # Squash bugs by refining type hints with validators.
   >>> from beartype.vale import Is  # <---- validator factory
   >>> from typing import Annotated  # <---------------- if Python ≥ 3.9.0
   # >>> from typing_extensions import Annotated   # <-- if Python < 3.9.0

   # Validators are type hints constrained by lambda functions.
   >>> ListOfStrings = Annotated[  # <----- type hint matching non-empty list of strings
   ...     list[str],  # <----------------- type hint matching possibly empty list of strings
   ...     Is[lambda lst: bool(lst)]  # <-- lambda matching non-empty object
   ... ]

   # Annotate @beartype-decorated callables with validators.
   >>> @beartype
   ... def quote_wiggum_safer(lines: ListOfStrings) -> None:
   ...     print('“{}”\n\t— Police Chief Wiggum'.format("\n ".join(lines)))

   # Call those callables with invalid parameters.
   >>> quote_wiggum_safer([])
   beartype.roar.BeartypeCallHintParamViolation: @beartyped
   quote_wiggum_safer() parameter lines=[] violates type hint
   typing.Annotated[list[str], Is[lambda lst: bool(lst)]], as value []
   violates validator Is[lambda lst: bool(lst)].

   # ..................{ AT ANY TIME }..................
   # Type-check anything against any type hint –
   # anywhere at anytime.
   >>> from beartype.door import (
   ...     is_bearable,  # <-------- like "isinstance(...)"
   ...     die_if_unbearable,  # <-- like "assert isinstance(...)"
   ... )
   >>> is_bearable(['The', 'goggles', 'do', 'nothing.'], list[str])
   True
   >>> die_if_unbearable([0xCAFEBEEF, 0x8BADF00D], ListOfStrings)
   beartype.roar.BeartypeDoorHintViolation: Object [3405692655, 2343432205]
   violates type hint typing.Annotated[list[str], Is[lambda lst: bool(lst)]],
   as list index 0 item 3405692655 not instance of str.

   # ..................{ GO TO PLAID }..................
   # Type-check anything in around 1µs (one millionth of
   # a second) – including this list of one million
   # 2-tuples of NumPy arrays.
   >>> from beartype.door import is_bearable
   >>> from numpy import array, ndarray
   >>> data = [(array(i), array(i)) for i in range(1000000)]
   >>> %time is_bearable(data, list[tuple[ndarray, ndarray]])
       CPU times: user 31 µs, sys: 2 µs, total: 33 µs
       Wall time: 36.7 µs
   True

Beartype brings Rust_- and `C++`_-inspired `zero-cost abstractions <zero-cost
abstraction_>`__ into the lawless world of `dynamically-typed`_ Python by
`enforcing type safety at the granular level of functions and methods
<Introduction_>`__ against `type hints standardized by the Python community
<Compliance_>`__ in `O(1) non-amortized worst-case time with negligible constant
factors <Timings_>`__. If the prior sentence was unreadable jargon, `see our
friendly and approachable FAQ for a human-readable synopsis <Frequently Asked
Questions (FAQ)_>`__.

Beartype is `portably implemented <beartype codebase_>`__ in `Python 3
<Python_>`__, `continuously stress-tested <beartype tests_>`__ via `GitHub
Actions`_ **×** tox_ **×** pytest_ **×** Codecov_, and `permissively
distributed <beartype license_>`__ under the `MIT license`_. Beartype has *no*
runtime dependencies, `only one test-time dependency <pytest_>`__, and `only
one documentation-time dependency <Sphinx_>`__. Beartype supports `all actively
developed Python versions <Python status_>`__, `all Python package managers
<Install_>`__, and `multiple platform-specific package managers <Install_>`__.

.. #FIXME: So sad! @beartype's Libraries.io listing has gone stale for nearly a
.. #year. And they've been shockingly unresponsive about this. Things seem...
.. #not all right with their service. Until they resolve whatever Python-related
.. #breakage has ruptured on their end, let's quietly disable this link and
.. #pretend this never happened. *sigh*
.. #    Beartype `powers quality assurance across the Python ecosystem <beartype
.. #    dependents_>`__.

.. #FIXME: Currently unused, but we still adore this section heading. Preserved!
.. # Let's Type This
.. # ***************

.. # Leading TOC entry self-referentially referring back to this document,
.. # enabling users to trivially navigate back to this document from elsewhere.
.. #
.. # Note that the ":hidden:" option adds this entry to the TOC sidebar while
.. # omitting this entry from the TOC displayed inline in this document. This is
.. # sensible; since any user currently viewing this document has *NO* need to
.. # navigate to the current document, this inline TOC omits this entry.
.. toctree::
   :hidden:
   :caption: Contents

   Bear with Us <self>

.. #FIXME: Uncomment *AFTER* re-enabling "autoapi" support in "conf.py" and
.. #resolving outstanding issues with that support. *gulp*
.. # .. toctree::
.. #    :caption: Beartype API reference
.. #
.. #    API </api/beartype/index>
.. #
.. # Would You Like to Know More?
.. # ----------------------------
.. #
.. # * :ref:`genindex`
.. # * :ref:`modindex`
.. # * :ref:`search`

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Project-wide tables of contents (TOCs). See also official documentation on
.. # the Sphinx-specific "toctree::" directive:
.. #     https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree

|

.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.
.. #
.. # Dismantled, this is:
.. # * ":class: ...", a Furo-specific directive instructing Furo to *NOT* emit
.. #   a prominent human-readable red warning. We don't particularly care, Furo.

.. contents:: **Contents**
   :class: this-will-duplicate-information-and-it-is-still-useful-here.
   :local:

.. # ------------------( DESCRIPTION                        )------------------

#######
Install
#######

Let's install beartype with pip_:

.. code-block:: bash

   pip3 install beartype

Let's install beartype with Anaconda_:

.. code-block:: bash

   conda config --add channels conda-forge
   conda install beartype

`Commemorate this moment in time <Badge_>`__ with |bear-ified|, our
over\ *bear*\ ing project shield. What says quality like `a bear on a badge
<Badge_>`__, amirite?

********
Platform
********

Beartype is also installable with platform-specific package managers, because
sometimes you just need this thing to work.

macOS
#####

Let's install beartype with Homebrew_ on macOS_ courtesy `our third-party
tap <beartype Homebrew_>`__:

.. code-block:: bash

   brew install beartype/beartype/beartype

Let's install beartype with MacPorts_ on macOS_:

.. code-block:: bash

   sudo port install py-beartype

A big bear hug to `our official macOS package maintainer @harens <harens_>`__
for `packaging beartype for our Apple-appreciating audience <beartype
MacPorts_>`__.

Linux
#####

Let's install beartype with ``emerge`` on Gentoo_ courtesy `a third-party
overlay <beartype Gentoo_>`__, because source-based Linux distributions are the
CPU-bound nuclear option:

.. code-block:: bash

   emerge --ask app-eselect/eselect-repository
   mkdir -p /etc/portage/repos.conf
   eselect repository enable raiagent
   emerge --sync raiagent
   emerge beartype

*What could be simpler?* O_o

*****
Badge
*****

If you're feeling the quality assurance and want to celebrate, consider
signaling that you're now publicly *bear-*\ ified:

  YummySoft is now |bear-ified|!

All this magic and possibly more can be yours with:

* **Markdown**:

  .. code-block:: md

     YummySoft is now [![bear-ified](https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg)](https://beartype.readthedocs.io)!

* **reStructuredText**:

  .. code-block:: rst

     YummySoft is now |bear-ified|!

     .. # See https://docutils.sourceforge.io/docs/ref/rst/directives.html#image
     .. |bear-ified| image:: https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg
        :align: top
        :target: https://beartype.readthedocs.io
        :alt: bear-ified

* **Raw HTML**:

  .. code-block:: html

     YummySoft is now <a href="https://beartype.readthedocs.io"><img
       src="https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg"
       alt="bear-ified"
       style="vertical-align: middle;"></a>!

Let a soothing pastel bear give your users the reassuring **OK** sign.

########
Overview
########

.. parsed-literal::

   Look for the bare necessities,
     the simple bare necessities.
   Forget about your worries and your strife.
                           — `The Jungle Book`_.

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
  coexists with competing static type-checkers and other runtime type-checkers.
* **Runtime.** Thanks to aggressive memoization and dynamic code generation at
  decoration time, beartype guarantees `O(1) non-amortized worst-case runtime
  complexity with negligible constant factors <Timings_>`__.

***************************
Versus Static Type-checkers
***************************

Like `competing static type-checkers <Static type-checkers_>`__ operating at
the coarse-grained application level via ad-hoc heuristic type inference (e.g.,
Pyre_, mypy_, pyright_, pytype_), beartype effectively `imposes no runtime
overhead <Timings_>`__. Unlike static type-checkers:

* Beartype operates exclusively at the fine-grained callable level of
  pure-Python functions and methods via the standard decorator design pattern.
  This renders beartype natively compatible with *all* interpreters and
  compilers targeting the Python language – including Brython_, PyPy_, Numba_,
  Nuitka_, and (wait for it) CPython_ itself.
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

****************************
Versus Runtime Type-checkers
****************************

Unlike `comparable runtime type-checkers <Runtime type-checkers_>`__ (e.g.,
pydantic_, typeguard_), beartype decorates callables with dynamically generated
wrappers efficiently type-checking each parameter passed to and value returned
from those callables in constant time. Since "performance by default" is our
first-class concern, generated wrappers are guaranteed to:

* Exhibit `O(1) non-amortized worst-case time complexity with negligible
  constant factors <Timings_>`__.
* Be either more efficient (in the common case) or exactly as efficient minus
  the cost of an additional stack frame (in the worst case) as equivalent
  type-checking implemented by hand, *which no one should ever do.*

################################
Frequently Asked Questions (FAQ)
################################

*****************
What is beartype?
*****************

Why, it's the world's first ``O(1)`` runtime type-checker in any
`dynamically-typed`_ lang... oh, *forget it.*

You know typeguard_? Then you know beartype – more or less. beartype is
typeguard_'s younger, faster, and slightly sketchier brother who routinely
ingests performance-enhancing anabolic nootropics.

******************
What is typeguard?
******************

**Okay.** Work with us here, people.

You know how in low-level `statically-typed`_ `memory-unsafe <memory safety_>`__
languages that no one should use like C_ and `C++`_, the compiler validates at
compilation time the types of all values passed to and returned from all
functions and methods across the entire codebase?

.. code-block:: bash

   $ gcc -Werror=int-conversion -xc - <<EOL
   #include <stdio.h>
   int main() {
       printf("Hello, world!");
       return "Goodbye, world.";
   }
   EOL
   <stdin>: In function ‘main’:
   <stdin>:4:11: error: returning ‘char *’ from a function with return type
   ‘int’ makes integer from pointer without a cast [-Werror=int-conversion]
   cc1: some warnings being treated as errors

You know how in high-level `duck-typed <duck typing_>`__ languages that everyone
should use instead like Python_ and Ruby_, the interpreter performs no such
validation at any interpretation phase but instead permits any arbitrary values
to be passed to or returned from any function or method?

.. code-block:: bash

   $ python3 - <<EOL
   def main() -> int:
       print("Hello, world!");
       return "Goodbye, world.";  # <-- pretty sure that's not an "int".
   main()
   EOL

   Hello, world!

Runtime type-checkers like beartype_ and typeguard_ selectively shift the dial
on type safety in Python from `duck <duck typing_>`__ to `static typing
<statically-typed_>`__ while still preserving all of the permissive benefits of
the former as a default behaviour. Now you too can quack like a duck while
roaring like a bear.

.. code-block:: bash

   $ python3 - <<EOL
   from beartype import beartype
   @beartype
   def main() -> int:
       print("Hello, world!");
       return "Goodbye, world.";  # <-- pretty sure that's not an "int".
   main()
   EOL

   Hello, world!
   Traceback (most recent call last):
     File "<stdin>", line 6, in <module>
     File "<string>", line 17, in main
     File "/home/leycec/py/beartype/beartype/_decor/_code/_pep/_error/errormain.py", line 218, in get_beartype_violation
       raise exception_cls(
   beartype.roar.BeartypeCallHintPepReturnException: @beartyped main() return
   'Goodbye, world.' violates type hint <class 'int'>, as value 'Goodbye,
   world.' not int.

***************************
When should I use beartype?
***************************

Use beartype to assure the quality of Python code beyond what tests alone can
assure. If you have yet to test, do that first with a pytest_-based test suite,
tox_ configuration, and `continuous integration (CI) <continuous
integration_>`__. If you have any time, money, or motivation left, `annotate
callables and classes with PEP-compliant type hints <Compliance_>`__ and
`decorate those callables and classes with the @beartype.beartype decorator
<Introduction_>`__.

Prefer beartype over other runtime and static type-checkers whenever you lack
perfect control over the objects passed to or returned from your callables –
*especially* whenever you cannot limit the size of those objects. This includes
common developer scenarios like:

* You are the author of an **open-source library** intended to be reused by a
  general audience.
* You are the author of a **public app** manipulating Bigly Data™ (i.e., data
  that is big) in app callables – especially when accepting data as input into
  *or* returning data as output from those callables.

If none of the above apply, prefer beartype over static type-checkers
whenever:

* You want to `check types decidable only at runtime <Versus Static
  Type-checkers_>`__.
* You want to write code rather than fight a static type-checker, because
  `static type inference <type inference_>`__ of a `dynamically-typed`_ language
  is guaranteed to fail and frequently does. If you've ever cursed the sky after
  suffixing working code incorrectly typed by mypy_ with non-portable
  vendor-specific pragmas like ``# type: ignore[{unreadable_error}]``, beartype
  was written for you.
* You want to preserve `dynamic typing`_, because Python is a
  `dynamically-typed`_ language. Unlike beartype, static type-checkers enforce
  `static typing`_ and are thus strongly opinionated; they believe `dynamic
  typing`_ is harmful and emit errors on `dynamically-typed`_ code. This
  includes common use patterns like changing the type of a variable by assigning
  that variable a value whose type differs from its initial value. Want to
  freeze a variable from a ``set`` into a ``frozenset``? That's sad, because
  static type-checkers don't want you to. In contrast:

    **Beartype never emits errors, warnings, or exceptions on dynamically-typed
    code,** because Python is not an error.

    **Beartype believes dynamic typing is beneficial by default,** because
    Python is beneficial by default.

    **Beartype is unopinionated.** That's because beartype `operates exclusively
    at the higher level of pure-Python callables and classes <Versus Static
    Type-checkers_>`__ rather than the lower level of individual statements
    *inside* pure-Python callables and class. Unlike static type-checkers,
    beartype can't be opinionated about things that no one should be.

If none of the above *still* apply, still use beartype. It's `free as in beer
and speech <gratis versus libre_>`__, `cost-free at installation- and runtime
<Overview_>`__, and transparently stacks with existing type-checking solutions.
Leverage beartype until you find something that suites you better, because
beartype is *always* better than nothing.

*******************************
Does beartype do any bad stuff?
*******************************

**Beartype is free** – free as in beer, speech, dependencies, space complexity,
*and* time complexity. Beartype is the textbook definition of "free." We're
pretty sure the Oxford Dictionary now just shows the `beartype mascot`_ instead
of defining that term. Vector art that `a Finnish man <beartype mascot
artist_>`__ slaved for weeks over paints a thousand words.

Beartype might not do as much as you'd like, but it will always do *something* –
which is more than Python's default behaviour, which is to do *nothing* and then
raise exceptions when doing nothing inevitably turns out to have been a bad
idea. Beartype also cleanly interoperates with popular static type-checkers, by
which we mean mypy_ and pyright_. (The `other guys <pytype_>`__ don't exist.)

Beartype can *always* be safely added to *any* Python package, module, app, or
script regardless of size, scope, funding, or audience. Never worry about your
backend Django_ server taking an impromptu swan dive on St. Patty's Day just
because your frontend React_ client pushed a 5MB JSON file serializing a
doubly-nested list of integers. :superscript:`Nobody could have foreseen this!`

The idea of competing runtime type-checkers like typeguard_ is that they
compulsively do *everything.* If you annotate a function decorated by typeguard_
as accepting a triply-nested list of integers and pass that function a list of
1,000 nested lists of 1,000 nested lists of 1,000 integers, *every* call to that
function will check *every* integer transitively nested in that list – even when
that list never changes. Did we mention that list transitively contains
1,000,000,000 integers in total?

.. code-block:: bash

   $ python3 -m timeit -n 1 -r 1 -s '
   from typeguard import typechecked
   @typechecked
   def behold(the_great_destroyer_of_apps: list[list[list[int]]]) -> int:
       return len(the_great_destroyer_of_apps)
   ' 'behold([[[0]*1000]*1000]*1000)'

   1 loop, best of 1: 6.42e+03 sec per loop

Yes, ``6.42e+03 sec per loop == 6420 seconds == 107 minutes == 1 hour, 47
minutes`` to check a single list once. Yes, it's an uncommonly large list...
*but it's still just a list.* This is the worst-case cost of a single call to a
function decorated by a naïve runtime type-checker.

***********************************
Does beartype actually do anything?
***********************************

Generally, as little as it can while still satisfying the accepted definition of
"runtime type-checker." Specifically, beartype performs a `one-way random walk
over the expected data structure of objects passed to and returned from
@beartype-decorated functions and methods <Beartype just does random stuff?
Really?_>`__. Colloquially, beartype type-checks randomly sampled data.
RNGesus_, show your humble disciples the way. ``</ahem>``

Consider `the prior example of a function annotated as accepting a triply-nested
list of integers passed a list containing 1,000 nested lists each containing
1,000 nested lists each containing 1,000 integers <Does beartype do any bad
stuff?_>`__. When decorated by:

* typeguard_, every call to that function checks every integer nested in that
  list.
* beartype, every call to the same function checks only a single random integer
  contained in a single random nested list contained in a single random nested
  list contained in that parent list. This is what we mean by the quaint phrase
  "one-way random walk over the expected data structure."

.. code-block:: bash

   $ python3 -m timeit -n 1024 -r 4 -s '
   from beartype import beartype
   @beartype
   def behold(the_great_destroyer_of_apps: list[list[list[int]]]) -> int:
      return len(the_great_destroyer_of_apps)
   ' 'behold([[[0]*1000]*1000]*1000)'

   1024 loops, best of 4: 13.8 usec per loop

Yes, ``13.8 usec per loop == 13.8 microseconds = 0.0000138 seconds`` to
transitively check only a random integer nested in a single triply-nested list
passed to each call of that function. This is the worst-case cost of a single
call to a function decorated by an ``O(1)`` runtime type-checker.

*************************************
How much does all this *really* cost?
*************************************

What substring of `"Beartype is free we swear it would we lie" <Does beartype do
any bad stuff?_>`__ did you not grep?

*...very well.* Let's pontificate.

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

****************************************
Beartype just does random stuff? Really?
****************************************

**Yes.** Beartype just does random stuff. That's what we're trying to say here.
We didn't want to admit it, but the ugly truth is out now. Are you smirking?
Because that looks like a smirk. Repeat after this FAQ:

* Beartype's greatest strength is that it checks types in constant time.
* Beartype's greatest weakness is that it checks types in constant time.

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
os.walk_ function, standard NumPy_ arrays, Pandas_ ``DataFrame`` columns,
PyTorch_ tensors, NetworkX_ graphs, and really all scientific containers ever.

*************************************
What does "near-real-time" even mean?
*************************************

.. _beartype realtime:

Beartype type-checks objects at runtime in around **1µs** (i.e., one
microsecond, one millionth of a second), the standard high-water mark for
`real-time software <real-time_>`__:

.. code-block:: pycon

   # Let's check a list of 181,320,382 integers in ~1µs.
   >>> from beartype import beartype
   >>> def sum_list_unbeartyped(some_list: list) -> int:
   ...     return sum(some_list)
   >>> sum_list_beartyped = beartype(sum_list_unbeartyped)
   >>> %time sum_list_unbeartyped([42]*0xACEBABE)
   CPU times: user 3.15 s, sys: 418 ms, total: 3.57 s
   Wall time: 3.58 s  # <-- okay.
   Out[20]: 7615456044
   >>> %time sum_list_beartyped([42]*0xACEBABE)
   CPU times: user 3.11 s, sys: 440 ms, total: 3.55 s
   Wall time: 3.56 s  # <-- woah.
   Out[22]: 7615456044

Beartype does *not* contractually guarantee this performance, as this example
demonstrates. Under abnormal processing loads (e.g., leycec_'s arthritic Athlon™
II X2 240, because you can't have enough redundant 2's in a product line) or
when passed edge-case type hints (e.g., classes whose metaclasses implement
stunningly awful ``__isinstancecheck__()`` dunder methods), beartype's
worst-case performance could exceed an average-case near-instantaneous response.

Beartype is therefore *not* real-time_; beartype is merely `near-real-time (NRT)
<near-real-time_>`__, also variously referred to as "pseudo-real-time,"
"quasi-real-time," or simply "high-performance." Real-time_ software guarantees
performance with a scheduler forcibly terminating tasks exceeding some deadline.
That's bad in most use cases. The outrageous cost of enforcement harms
real-world performance, stability, and usability.

**NRT.** It's good for you. It's good for your codebase. It's just good.

**********************
How do I type-check...
**********************

...yes? Go on.

...Boto3 types?
###############

**tl;dr:** You just want bearboto3_, a well-maintained third-party package
cleanly integrating beartype **+** Boto3_. But you're not doing that. You're
reading on to find out why you want bearboto3_, aren't you? I *knew* it.

Boto3_ is the official Amazon Web Services (AWS) Software Development Kit (SDK)
for Python. Type-checking Boto3_ types is decidedly non-trivial, because Boto3_
dynamically fabricates unimportable types from runtime service requests. These
types *cannot* be externally accessed and thus *cannot* be used as type hints.

**H-hey!** Put down the hot butter knife. Your Friday night may be up in flames,
but we're gonna put out the fire. It's what we do here. Now, you have two
competing solutions with concomitant tradeoffs. You can type-check Boto3_ types
against either:

* **Static type-checkers** (e.g., mypy_, pyright_) by importing Boto3_ stub
  types from an external third-party dependency (e.g., mypy-boto3_), enabling
  context-aware code completion across compliant IDEs (e.g., PyCharm_, `VSCode
  Pylance <Pylance_>`__). Those types are merely placeholder stubs; they do
  *not* correspond to actual Boto3_ types and thus break runtime type-checkers
  (including beartype) when used as type hints.
* **Beartype** by fabricating your own `PEP-compliant beartype validators
  <Beartype Validators_>`__, enabling beartype to validate arbitrary objects
  against actual Boto3_ types at runtime when used as type hints. You already
  require beartype, so no additional third-party dependencies are required.
  Those validators are silently ignored by static type-checkers; they do *not*
  enable context-aware code completion across compliant IDEs.

"B-but that *sucks*! How can we have our salmon and devour it too?", you demand
with a tremulous quaver. Excessive caffeine and inadequate gaming did you no
favors tonight. You know this. Yet again you reach for the hot butter knife.

**H-hey!** You can, okay? You can have everything that market forces demand.
Bring to *bear* :superscript:`cough` the combined powers of `PEP 484-compliant
type aliases <type aliases_>`__, the `PEP 484-compliant "typing.TYPE_CHECKING"
boolean global <typing.TYPE_CHECKING_>`__, and `beartype validators <Beartype
Validators_>`__ to satisfy both static and runtime type-checkers:

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype
   from boto3 import resource
   from boto3.resources.base import ServiceResource
   from typing import TYPE_CHECKING

   # If performing static type-checking (e.g., mypy, pyright), import boto3
   # stub types safely usable *ONLY* by static type-checkers.
   if TYPE_CHECKING:
       from mypy_boto3_s3.service_resource import Bucket
   # Else, @beartime-based runtime type-checking is being performed. Alias the
   # same boto3 stub types imported above to their semantically equivalent
   # beartype validators accessible *ONLY* to runtime type-checkers.
   else:
       # Import even more requisite machinery. Can't have enough, I say!
       from beartype.vale import IsAttr, IsEqual
       from typing import Annotated   # <--------------- if Python ≥ 3.9.0
       # from typing_extensions import Annotated   # <-- if Python < 3.9.0

       # Generalize this to other boto3 types by copy-and-pasting this and
       # replacing the base type and "s3.Bucket" with the wonky runtime names
       # of those types. Sadly, there is no one-size-fits all common base class,
       # but you should find what you need in the following places:
       # * "boto3.resources.base.ServiceResource".
       # * "boto3.resources.collection.ResourceCollection".
       # * "botocore.client.BaseClient".
       # * "botocore.paginate.Paginator".
       # * "botocore.waiter.Waiter".
       Bucket = Annotated[ServiceResource,
           IsAttr['__class__', IsAttr['__name__', IsEqual["s3.Bucket"]]]]

   # Do this for the good of the gross domestic product, @beartype.
   @beartype
   def get_s3_bucket_example() -> Bucket:
       s3 = resource('s3')
       return s3.Bucket('example')

You're welcome.

...JAX arrays?
##############

You only have two options here. Choose wisely, wily scientist. If:

* You don't mind adding an **additional mandatory runtime dependency** to your
  app:

  * Require the `third-party "jaxtyping" package <jaxtyping_>`__.
  * Annotate callables with type hint factories published by ``jaxtyping``
    (e.g., ``jaxtyping.Float[jaxtyping.Array, '{metadata1 ... metadataN}']``).

  Beartype fully supports `typed JAX arrays <jaxtyping_>`__. Because `Google
  mathematician @patrick-kidger <patrick-kidger_>`__ did all the hard work, we
  didn't have to. Bless your runtime API, @patrick-kidger.

* You mind adding an additional mandatory runtime dependency to your app, prefer
  `beartype validators <Tensor Property Matching_>`__. Since `JAX declares a
  broadly similar API to that of NumPy with its "jax.numpy" compatibility layer
  <jax.numpy_>`__, most NumPy-specific examples cleanly generalize to JAX.
  Beartype is *no* exception.

Bask in the array of options at your disposal! :superscript:`...get it?
...array? I'll stop now.`

...NumPy arrays?
################

You have more than a few options here. If you want to type-check:

* The ``dtype`` of a NumPy array, prefer the `official
  "numpy.typing.NDArray[{dtype}]" type hint factory bundled with NumPy
  explicitly supported by beartype <NumPy Type Hints_>`__ – also referred to as
  a `typed NumPy array <NumPy Type Hints_>`__.
* The ``shape`` of a NumPy array (and possibly more), you have two additional
  sub-options here depending on whether:

  * You want **static type-checkers** to enforce that ``shape`` *and* you don't
    mind adding an **additional mandatory runtime dependency** to your app. In
    this case:

    * Require the `third-party "nptyping" package <nptyping_>`__.
    * Prefer the unofficial ``nptyping.NDArray[{nptyping.dtype},
      nptyping.Shape[...]]`` type hint factory implicitly supported by beartype.

    Beartype fully supports `typed NumPy arrays <NumPy Type Hints_>`__. Because
    beartype cares.

  * You don't mind static type-checkers ignoring that ``shape`` *or* you mind
    adding an additional mandatory runtime dependency to your app. In this case,
    prefer `beartype validators <Tensor Property Matching_>`__.

Options are good! Repeat this mantra in times of need.

...PyTorch tensors?
###################

You only have two options here. We're pretty sure two is better than none. Thus,
we give thanks. If:

* You don't mind adding an **additional mandatory runtime dependency** to your
  app:

  * Require the `third-party "TorchTyping" package <TorchTyping_>`__.
  * Annotate callables with type hint factories published by TorchTyping (e.g.,
    ``TorchTyping.TensorType['{metadata1}', ..., '{metadataN}']``).

  Beartype fully supports `typed PyTorch tensors <TorchTyping_>`__. Because
  `Google mathematician @patrick-kidger <patrick-kidger_>`__ did all the hard
  work, we didn't have to. Bless your runtime API, @patrick-kidger.

* You mind adding an additional mandatory runtime dependency to your app. In
  this case, prefer `beartype validators <Beartype Validators_>`__. For example,
  validate callable parameters and returns as either floating-point *or*
  integral PyTorch tensors via the `functional validator factory
  beartype.vale.Is[...] <beartype.vale.Is_>`__:

  .. code-block:: python

     # Import the requisite machinery.
     from beartype import beartype
     from beartype.vale import Is
     from typing import Annotated   # <--------------- if Python ≥ 3.9.0
     # from typing_extensions import Annotated   # <-- if Python < 3.9.0

     # Import PyTorch (d)types of interest.
     from torch import (
         float as torch_float,
         int as torch_int,
         tensor,
     )

     # PEP-compliant type hint matching only a floating-point PyTorch tensor.
     TorchTensorFloat = Annotated[tensor, Is[
         lambda tens: tens.type() is torch_float]]

     # PEP-compliant type hint matching only an integral PyTorch tensor.
     TorchTensorInt = Annotated[tensor, Is[
         lambda tens: tens.type() is torch_int]]

     # Type-check everything like an NLP babelfish.
     @beartype
     def deep_dream(dreamy_tensor: TorchTensorFloat) -> TorchTensorInt:
         return dreamy_tensor.type(dtype=torch_int)

  Since `beartype.vale.Is[...] <beartype.vale.Is_>`__ supports arbitrary
  Turing-complete Python expressions, the above example generalizes to typing
  the device, dimensionality, and other metadata of PyTorch tensors to whatever
  degree of specificity you desire.

  `beartype.vale.Is[...] <beartype.vale.Is_>`__: *it's lambdas all the way
  down.*

...mock types?
##############

Beartype fully relies upon the `isinstance() builtin <isinstance_>`__ under the
hood for its low-level runtime type-checking needs. If you can fool
``isinstance()``, you can fool beartype. Can you fool beartype into believing
an instance of a mock type is an instance of the type it mocks, though?

**You bet your bottom honey barrel.** In your mock type, just define a new
``__class__()`` property returning the original type: e.g.,

.. code-block:: pycon

   >>> class OriginalType: pass
   >>> class MockType:
   ...     @property
   ...     def __class__(self) -> type: return OriginalType

   >>> from beartype import beartype
   >>> @beartype
   ... def muh_func(self, muh_arg: OriginalType): print('Yolo, bro.')
   >>> muh_func(MockType())
   Yolo, bro.

This is why we beartype.

...under VSCode?
################

**Beartype fully supports VSCode out-of-the-box** – especially via Pylance_,
Microsoft's bleeding-edge Python extension for VSCode. Chortle in your joy,
corporate subscribers and academic sponsors! All the intellisense you can
tab-complete and more is now within your honey-slathered paws. Why? Because...

Beartype laboriously complies with pyright_, Microsoft's in-house static
type-checker for Python. Pylance_ enables pyright_ as its default static
type-checker. Beartype thus complies with Pylance_, too.

Beartype *also* laboriously complies with mypy_, Python's official static
type-checker. VSCode users preferring mypy_ to pyright_ may switch Pylance_ to
type-check via the former. Just:

#. `Install mypy <mypy install_>`__.
#. `Install the VSCode Mypy extension <VSCode Mypy extension_>`__.
#. Open the *User Settings* dialog.
#. Search for ``Type Checking Mode``.
#. Browse to ``Python › Analysis: Type Checking Mode``.
#. Switch the "default rule set for type checking" to ``off``.

|VSCode-Pylance-type-checking-setting|

:superscript:`Pretend that reads "off" rather than "strict". Pretend we took
this screenshot.`

There are tradeoffs here, because that's just how the code rolls. On:

* The one paw, pyright_ is *significantly* more performant than mypy_ under
  Pylance_ and supports type-checking standards currently unsupported by mypy_
  (e.g., recursive type hints).
* The other paw, mypy_ supports a vast plugin architecture enabling third-party
  Python packages to describe dynamic runtime behaviour statically.

Beartype: we enable hard choices, so that you can make them for us.

.. # ------------------( IMAGES ~ screenshot                 )------------------
.. |VSCode-Pylance-type-checking-setting| image:: https://user-images.githubusercontent.com/217028/164616311-c4a24889-0c53-4726-9051-29be7263ee9b.png
   :alt: Disabling pyright-based VSCode Pylance type-checking

...under [insert-IDE-name-here]?
################################

Beartype fully complies with mypy_, pyright_, :pep:`561`, and other community
standards that govern how Python is statically type-checked. Modern Integrated
Development Environments (IDEs) support these standards - hopefully including
your GigaChad IDE of choice.

...with type narrowing?
#######################

Beartype fully supports `type narrowing`_ with the :pep:`647`\ -compliant
typing.TypeGuard_ type hint. In fact, beartype supports type narrowing of *all*
PEP-compliant type hints and is thus the first maximal type narrower.

Specifically, the `procedural beartype.door.is_bearable() function
<is_bearable_>`__ and `object-oriented beartype.door.TypeHint.is_bearable()
method <beartype.door_>`__ both narrow the type of the passed test object (which
can be *anything*) to the passed type hint (which can be *anything*
PEP-compliant). Both soft-guarantee runtime performance on the order of less
than 1µs (i.e., less than one millionth of a second), preserving runtime
performance and your personal sanity.

Calling either `is_bearable() <is_bearable_>`__ *or* `TypeHint.is_bearable()
<beartype.door_>`__ in your code enables beartype to symbiotically eliminate
false positives from static type-checkers checking that code, substantially
reducing static type-checker spam that went rotten decades ago: e.g.,

.. code-block:: python

   # Import the requisite machinery.
   from beartype.door import is_bearable

   def narrow_types_like_a_boss_with_beartype(lst: list[int | str]):
       '''
       This function eliminates false positives from static type-checkers
       like mypy and pyright by narrowing types with ``is_bearable()``.

       Note that decorating this function with ``@beartype`` is *not*
       required to inform static type-checkers of type narrowing. Of
       course, you should still do that anyway. Trust is a fickle thing.
       '''

       # If this list contains integers rather than strings, call another
       # function accepting only a list of integers.
       if is_bearable(lst, list[int]):
           # "lst" has been though a lot. Let's celebrate its courageous story.
           munch_on_list_of_strings(lst)  # mypy/pyright: OK!
       # If this list contains strings rather than integers, call another
       # function accepting only a list of strings.
       elif is_bearable(lst, list[str]):
           # "lst": The Story of "lst." The saga of false positives ends now.
           munch_on_list_of_strings(lst)  # mypy/pyright: OK!

   def munch_on_list_of_strings(lst: list[str]): ...
   def munch_on_list_of_integers(lst: list[int]): ...

Beartype: *because you no longer care what static type-checkers think.*

############
Introduction
############

Beartype makes type-checking painless, portable, and purportedly fun. Just:

    Decorate functions and methods `annotated by standard type hints <Standard
    Hints_>`__ with the ``@beartype.beartype`` decorator, which wraps those
    functions and methods in performant type-checking dynamically generated
    on-the-fly.

    When `standard type hints <Standard Hints_>`__ fail to support your use
    case, annotate functions and methods with `beartype-specific validator type
    hints <Beartype Validators_>`__ instead. Validators enforce runtime
    constraints on the internal structure and contents of parameters and returns
    via simple caller-defined lambda functions and declarative expressions – all
    seamlessly composable with `standard type hints <Standard Hints_>`__ in an
    `expressive domain-specific language (DSL) <Validator Syntax_>`__ designed
    just for you.

"Embrace the bear," says the bear peering over your shoulder as you read this.

**************
Standard Hints
**************

Beartype supports *most* `type hints standardized by the developer community
through Python Enhancement Proposals (PEPs) <Compliance_>`__. Since type hinting
is its own special hell, we'll start by wading into the thalassophobia-inducing
waters of type-checking with a sane example – the O(1) ``@beartype`` way.

Toy Example
###########

Let's type-check a ``"Hello, Jungle!"`` toy example. Just:

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

#. Call that function with valid parameters and caper as things work:

   .. code-block:: pycon

      >>> hello_jungle(sep='...ROOOAR!!!!', end='uhoh.', file=stderr, flush=True)
      Hello, Jungle! ...ROOOAR!!!! uhoh.

#. Call that function with invalid parameters and cringe as things blow up with
   human-readable exceptions exhibiting the single cause of failure:

   .. code-block:: pycon

      >>> hello_jungle(sep=(
      ...     b"What? Haven't you ever seen a byte-string separator before?"))
      BeartypeCallHintPepParamException: @beartyped hello_jungle() parameter
      sep=b"What? Haven't you ever seen a byte-string separator before?"
      violates type hint <class 'str'>, as value b"What? Haven't you ever seen
      a byte-string separator before?" not str.

Industrial Example
##################

Let's wrap the `third-party numpy.empty_like() function <numpy.empty_like_>`__
with automated runtime type checking to demonstrate beartype's support for
non-trivial combinations of nested type hints compliant with different PEPs:

.. code-block:: python

   from beartype import beartype
   from collections.abc import Sequence
   from typing import Optional, Union
   import numpy as np

   @beartype
   def empty_like_bear(
       prototype: object,
       dtype: Optional[np.dtype] = None,
       order: str = 'K',
       subok: bool = True,
       shape: Optional[Union[int, Sequence[int]]] = None,
   ) -> np.ndarray:
       return np.empty_like(prototype, dtype, order, subok, shape)

Note the non-trivial hint for the optional ``shape`` parameter, synthesized from
a `PEP 484-compliant optional <typing.Optional_>`__ of a `PEP 484-compliant
union <typing.Union_>`__ of a builtin type and a `PEP 585-compliant subscripted
abstract base class (ABC) <collections.abc.Sequence_>`__, accepting as valid
either:

* The ``None`` singleton.
* An integer.
* A sequence of integers.

Let's call that wrapper with both valid and invalid parameters:

.. code-block:: pycon

   >>> empty_like_bear(([1,2,3], [4,5,6]), shape=(2, 2))
   array([[94447336794963,              0],
          [             7,             -1]])
   >>> empty_like_bear(([1,2,3], [4,5,6]), shape=([2], [2]))
   BeartypeCallHintPepParamException: @beartyped empty_like_bear() parameter
   shape=([2], [2]) violates type hint typing.Union[int,
   collections.abc.Sequence, NoneType], as ([2], [2]):
   * Not <class "builtins.NoneType"> or int.
   * Tuple item 0 value [2] not int.

Note the human-readable message of the raised exception, containing a bulleted
list enumerating the various ways this invalid parameter fails to satisfy its
type hint, including the types and indices of the first container item failing
to satisfy the nested ``Sequence[int]`` hint.

See a `subsequent section <Implementation_>`__ for actual code dynamically
generated by beartype for real-world use cases resembling those above. Fun!

****************************
Would You Like to Know More?
****************************

If you know `type hints <PEP 484_>`__, you know beartype. Since beartype is
driven by `tool-agnostic community standards <PEP 0_>`__, the public API for
beartype is *basically* just those standards. As the user, all you need to know
is that decorated callables magically raise human-readable exceptions when you
pass parameters or return values violating the PEP-compliant type hints
annotating those parameters or returns.

If you don't know `type hints <PEP 484_>`__, this is your moment to go deep on
the hardest hammer in Python's SQA_ toolbox. Here are a few friendly primers to
guide you on your maiden voyage through the misty archipelagos of type hinting:

* `"Python Type Checking (Guide)" <RealPython_>`__, a comprehensive third-party
  introduction to the subject. Like most existing articles, this guide predates
  ``O(1)`` runtime type checkers and thus discusses only static type checking.
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

#####
Usage
#####

Beartype isn't just the standards-compliant ``@beartype.beartype`` decorator.
Beartype is a menagerie of public APIs for type-checking, introspecting, and
manipulating type hints at runtime – all accessible under the ``beartype``
package installed when you installed beartype.

Beartype: *more than meets the eye.*

*******************
Beartype Decoration
*******************

.. _beartype.beartype:

.. # FIXME: Revise all hard-code references to this decorator (e.g.,
.. # "``@beartype``", "``@beartype.beartype``) into actual beartype.beartype_
.. # interlinks, please.

The beating heart of beartype is the eponymous ``@beartype.beartype`` decorator.
This is its story.

Unlike most decorators, ``@beartype.beartype`` has three modes of operation:

* `Callable mode <beartype.beartype func_>`__, in which you decorate a function
  or method with ``@beartype``, which then dynamically generates a new function
  or method wrapping the original function or method with runtime type-checking.
* `Class mode <beartype.beartype type_>`__, in which you decorate a class with
  ``@beartype``, which then decorates all methods declared by that class with
  ``@beartype``. This is mostly just syntactic sugar – but sometimes you just
  gotta dip your paws into the honey pot.
* `Configuration mode <beartype.beartype conf_>`__, in which you create your own
  app-specific ``@beartype`` decorator – **configured** for your exact use case.

.. _beartype.beartype func:
.. _beartype.beartype type:
.. _beartype.beartype conf:

*def* beartype.\ **beartype**\ (conf: beartype.BeartypeConf_) ->
Callable[[BeartypeableT], BeartypeableT]

Define your own app-specific ``@beartype`` decorator – **configured** for your
exact use case:

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype, BeartypeConf, BeartypeStrategy

   # Dynamically create a new @monotowertype decorator configured to:
   # * Avoid outputting colors in type-checking violations.
   # * Enable support for the implicit numeric tower standardized by PEP 484.
   monotowertype = beartype(conf=BeartypeConf(
       is_color=False, is_pep484_tower=True))

   # Decorate with this decorator rather than @beartype everywhere.
   @monotowertype
   def muh_colorless_permissive_func(int_or_float: float) -> float:
       return int_or_float ** int_or_float ^ round(int_or_float)

Configuration: *because you know best*.

Configuration API
#################

.. _beartype.BeartypeConf:

| *class* beartype.\ **BeartypeConf**\ (
| |_| |_| |_| |_| \*,
| |_| |_| |_| |_| `is_color <BeartypeConf.is_color_>`__: Optional[bool] = None,
| |_| |_| |_| |_| `is_debug <BeartypeConf.is_debug_>`__: bool = False,
| |_| |_| |_| |_| `is_pep484_tower <BeartypeConf.is_pep484_tower_>`__: bool = False,
| |_| |_| |_| |_| `strategy <BeartypeConf.strategy_>`__: BeartypeStrategy_ = BeartypeStrategy.O1_,
| )

    **Beartype configuration** (i.e., self-caching dataclass instance
    encapsulating all flags, options, settings, and other metadata configuring
    each type-checking operation performed by beartype – including each
    decoration of a callable or class by the ``@beartype.beartype`` decorator).

    The default configuration ``BeartypeConf()`` configures beartype to:

    * Conditionally output color when standard output is attached to a terminal.
    * Disable developer-specific debugging logic.
    * Disable support for `PEP 484's implicit numeric tower <implicit numeric
      tower_>`__.
    * Perform ``O(1)`` constant-time type-checking for safety, scalability, and
      efficiency.

    Beartype configurations are immutable objects memoized (i.e., cached) on the
    unordered set of all passed parameters:

    .. code-block:: pycon

       >>> from beartype import BeartypeConf
       >>> BeartypeConf() is BeartypeConf()
       True
       >>> BeartypeConf(is_color=False) is BeartypeConf(is_color=False)
       True

    Beartype configurations are comparable under equality:

    .. code-block:: pycon

       >>> BeartypeConf(is_color=False) == BeartypeConf(is_color=True)
       False

    Beartype configurations are hashable and thus suitable for use as dictionary
    keys and set members:

    .. code-block:: pycon

       >>> BeartypeConf(is_color=False) == BeartypeConf(is_color=True)
       False
       >>> confs = {BeartypeConf(), BeartypeConf(is_color=False)}
       >>> BeartypeConf() in confs
       True

    Beartype configurations support meaningful ``repr()`` output:

    .. code-block:: pycon

       >>> repr(BeartypeConf())
       'BeartypeConf(is_color=None, is_debug=False, is_pep484_tower=False, strategy=<BeartypeStrategy.O1: 2>)'

    Beartype configurations expose read-only public properties of the same
    names as the above parameters:

    .. code-block:: pycon

       >>> BeartypeConf().is_color
       None
       >>> BeartypeConf().strategy
       <BeartypeStrategy.O1: 2>

    Beartype configurations support these optional keyword-only parameters at
    instantiation time:

    .. _BeartypeConf.is_color:

    * **is_color**\ : Optional[bool] = None

      Tri-state boolean governing how and whether beartype colours
      **type-checking violations** (i.e., human-readable
      beartype.roar.BeartypeCallHintViolation_ exceptions) with POSIX-compliant
      ANSI escape sequences for readability. Specifically, if this boolean is:

      * ``False``, beartype *never* colours type-checking violations
        raised by callables configured with this configuration.
      * ``True``, beartype *always* colours type-checking violations
        raised by callables configured with this configuration.
      * ``None``, beartype conditionally colours type-checking violations
        raised by callables configured with this configuration only when
        standard output is attached to an interactive terminal.

      Defaults to ``None``.

      The standard use case is to dynamically define your own app-specific
      ``@beartype`` decorator unconditionally disabling colours in type-checking
      violations, usually due to one or more frameworks in your application
      stack failing to support ANSI escape sequences. Please file upstream
      issues with those frameworks requesting ANSI support. In the meanwhile,
      behold the monochromatic powers of... ``@monobeartype``!

      .. code-block:: python

         # Import the requisite machinery.
         from beartype import beartype, BeartypeConf

         # Dynamically create a new @monobeartype decorator disabling colour.
         monobeartype = beartype(conf=BeartypeConf(is_color=False))

         # Decorate with this decorator rather than @beartype everywhere.
         @monobeartype
         def muh_colorless_func() -> str:
             return b'In the kingdom of the blind, you are now king.'

      *First introduced in beartype 0.12.0.*

    .. _BeartypeConf.is_debug:

    * **is_debug**\ : bool = False

      ``True`` only if debugging the ``@beartype`` decorator. If you're curious
      as to what exactly (if anything) ``@beartype`` is doing on your behalf,
      temporarily enable this boolean. Specifically, enabling this boolean:

      * Caches the body of each type-checking wrapper function dynamically
        generated by ``@beartype`` with the standard linecache_ module, enabling
        these function bodies to be introspected at runtime *and* improving the
        readability of tracebacks whose call stacks contain one or more calls to
        these ``@beartype.beartype``\ -decorated functions.
      * Prints the definition (including both the signature and body) of each
        type-checking wrapper function dynamically generated by ``@beartype`` to
        standard output.
      * Appends to the declaration of each **hidden parameter** (i.e., whose
        name is prefixed by ``"__beartype_"`` and whose value is that of an
        external attribute internally referenced in the body of that function)
        a comment providing the machine-readable representation of the initial
        value of that parameter, stripped of newlines and truncated to a
        hopefully sensible length. Since the low-level string munger called to
        do so is shockingly slow, these comments are conditionally embedded in
        type-checking wrapper functions *only* when this boolean is enabled.

      Defaults to ``False``. Eye-gouging sample output or it didn't happen, so:

      .. code-block:: pycon

         # Import the requisite machinery.
         >>> from beartype import beartype, BeartypeConf

         # Dynamically create a new @bugbeartype decorator enabling debugging.
         # Insider D&D jokes in my @beartype? You'd better believe. It's happening.
         >>> bugbeartype = beartype(conf=BeartypeConf(is_debug=True))

         # Decorate with this decorator rather than @beartype everywhere.
         >>> @bugbeartype
         ... def muh_bugged_func() -> str:
         ...     return b'Consistency is the bugbear that frightens little minds.'
         (line 0001) def muh_bugged_func(
         (line 0002)     *args,
         (line 0003)     __beartype_func=__beartype_func, # is <function muh_bugged_func at 0x7f52733bad40>
         (line 0004)     __beartype_conf=__beartype_conf, # is "BeartypeConf(is_color=None, is_debug=True, is_pep484_tower=False, strategy=<BeartypeStrategy...
         (line 0005)     __beartype_get_violation=__beartype_get_violation, # is <function get_beartype_violation at 0x7f5273081d80>
         (line 0006)     **kwargs
         (line 0007) ):
         (line 0008)     # Call this function with all passed parameters and localize the value
         (line 0009)     # returned from this call.
         (line 0010)     __beartype_pith_0 = __beartype_func(*args, **kwargs)
         (line 0011)
         (line 0012)     # Noop required to artificially increase indentation level. Note that
         (line 0013)     # CPython implicitly optimizes this conditional away. Isn't that nice?
         (line 0014)     if True:
         (line 0015)         # Type-check this passed parameter or return value against this
         (line 0016)         # PEP-compliant type hint.
         (line 0017)         if not isinstance(__beartype_pith_0, str):
         (line 0018)             raise __beartype_get_violation(
         (line 0019)                 func=__beartype_func,
         (line 0020)                 conf=__beartype_conf,
         (line 0021)                 pith_name='return',
         (line 0022)                 pith_value=__beartype_pith_0,
         (line 0023)             )
         (line 0024)
         (line 0025)     return __beartype_pith_0

    .. _BeartypeConf.is_pep484_tower:

    * **is_pep484_tower**\ : bool = False

      ``True`` only if enabling support for `PEP 484's implicit numeric tower
      <implicit numeric tower_>`__ (i.e., lossy conversion of integers to
      floating-point numbers as well as both integers and floating-point
      numbers to complex numbers). Specifically, enabling this instructs
      beartype to automatically expand:

      * All ``float`` type hints to ``float | int``, thus implicitly accepting
        both integers and floating-point numbers for objects annotated as only
        accepting floating-point numbers.
      * All ``complex`` type hints to ``complex | float | int``, thus
        implicitly accepting integers, floating-point, and complex numbers for
        objects annotated as only accepting complex numbers.

      Defaults to ``False`` to minimize precision error introduced by lossy
      conversions from integers to floating-point numbers to complex numbers.
      Since most integers do *not* have exact representations as floating-point
      numbers, each conversion of an integer into a floating-point number
      typically introduces a small precision error that accumulates over
      multiple conversions and operations into a larger precision error.
      Enabling this improves the usability of public APIs at a cost of
      introducing precision errors.

      The standard use case is to dynamically define your own app-specific
      ``@beartype`` decorator unconditionally enabling support for the implicit
      numeric tower, usually as a convenience to your userbase who do *not*
      particularly care about the above precision concerns. Behold the
      permissive powers of... ``@beartowertype``!

      .. code-block:: python

         # Import the requisite machinery.
         from beartype import beartype, BeartypeConf

         # Dynamically create a new @beartowertype decorator enabling the tower.
         beartowertype = beartype(conf=BeartypeConf(is_pep484_tower=True))

         # Decorate with this decorator rather than @beartype everywhere.
         @beartowertype
         def crunch_numbers(numbers: list[float]) -> float:
             return sum(numbers)

         # This is now fine.
         crunch_numbers([3, 1, 4, 1, 5, 9])

         # This is still fine, too.
         crunch_numbers([3.1, 4.1, 5.9])

      *First introduced in beartype 0.12.0.*

    .. _BeartypeConf.strategy:

    * **strategy**\ : BeartypeStrategy_ = BeartypeStrategy.O1_

      **Type-checking strategy** (i.e., BeartypeStrategy_ enumeration member
      dictating how many items are type-checked at each nesting level of each
      container and thus how responsively beartype type-checks containers). This
      setting governs the core tradeoff in runtime type-checking between:

      * **Overhead** in the amount of time that beartype spends type-checking.
      * **Completeness** in the number of objects that beartype type-checks.

      As beartype gracefully scales up to check larger and larger containers,
      so beartype simultaneously scales down to check fewer and fewer items of
      those containers. This scalability preserves performance regardless of
      container size while increasing the likelihood of false negatives (i.e.,
      failures to catch invalid items in large containers) as container size
      increases. You can either type-check a small number of objects nearly
      instantaneously *or* you can type-check a large number of objects slowly.
      Pick one.

      Defaults to BeartypeStrategy.O1_, the constant-time ``O(1)`` strategy –
      maximizing scalability at a cost of also maximizing false positives.

.. _BeartypeStrategy:

*class* beartype.\ **BeartypeStrategy**\ (enum.Enum)

    Enumeration of all kinds of **type-checking strategies** (i.e., competing
    procedures for type-checking objects passed to or returned from
    ``@beartype``\ -decorated callables, each with concomitant tradeoffs with
    respect to runtime complexity and quality assurance).

    Strategies are intentionally named according to `conventional Big O
    notation <Big O_>`__ (e.g., BeartypeStrategy.On_ enables the ``O(n)``
    strategy). Strategies are established per-decoration at the fine-grained
    level of callables decorated by the ``@beartype`` decorator by setting the
    BeartypeConf.strategy_ parameter of the beartype.BeartypeConf_ object passed
    as the optional ``conf`` parameter to that decorator.

    Strategies enforce their corresponding runtime complexities (e.g., ``O(n)``)
    across *all* type-checks performed for callables enabling those strategies.
    For example, a callable configured by the BeartypeStrategy.On_ strategy will
    exhibit linear ``O(n)`` complexity as its overhead for type-checking each
    nesting level of each container passed to and returned from that callable.

    This enumeration defines these members:

    .. _BeartypeStrategy.O0:

    * BeartypeStrategy.\ **O0** : beartype.cave.EnumMemberType

      **No-time strategy** (i.e, disabling type-checking for a decorated
      callable by reducing ``@beartype`` to the identity decorator for that
      callable). This strategy is functionally equivalent to but more
      general-purpose than the standard `@typing.no_type_check`_ decorator;
      whereas `@typing.no_type_check`_ only applies to callables, this strategy
      applies to *any* context accepting a beartype configuration such as:

      * The ``@beartype`` decorator decorating a class.
      * The `beartype.door.is_bearable() function <is_bearable_>`__.
      * The `beartype.door.die_if_unbearable() function <die_if_unbearable_>`__.
      * The `beartype.door.TypeHint.is_bearable() method <beartype.door_>`__.
      * The `beartype.door.TypeHint.die_if_unbearable() method
        <beartype.door_>`__.

      Just like in real life, there exist use cases for doing absolutely
      nothing – including:

      * **Blacklisting callables.** Although seemingly useless, this strategy
        allows callers to selectively prevent callables that would otherwise be
        type-checked (e.g., due to class decorations or import hooks) from being
        type-checked:

        .. code-block:: python

           # Import the requisite machinery.
           from beartype import beartype, BeartypeConf, BeartypeStrategy

           # Dynamically create a new @nobeartype decorator disabling type-checking.
           nobeartype = beartype(conf=BeartypeConf(strategy=BeartypeStrategy.O0))

           # Automatically decorate all methods of this class...
           @beartype
           class TypeCheckedClass(object):
               # Including this method, which raises a type-checking violation
               # due to returning a non-"None" value.
               def type_checked_method(self) -> None:
                   return 'This string is not "None". Apparently, that is a problem.'

               # Excluding this method, which raises *NO* type-checking
               # violation despite returning a non-"None" value.
               @nobeartype
               def non_type_checked_method(self) -> None:
                   return 'This string is not "None". Thankfully, no one cares.'

      * **Eliding overhead.** Beartype `already exhibits near-real-time overhead
        of less than 1µs (one microsecond, one millionth of a second) per call
        of type-checked callables <beartype realtime_>`__. When even that
        negligible overhead isn't negligible enough, brave callers considering
        an occupational change may globally disable *all* type-checking
        performed by beartype. Please prepare your resume before doing so. Also,
        do so *only* under production builds intended for release; development
        builds intended for testing should preserve type-checking. Either:

        * `Pass Python the "-O" command-line option <-O_>`__, which beartype
          respects.
        * `Run Python under the "PYTHONOPTIMIZE" environment variable
          <PYTHONOPTIMIZE_>`__, which beartype also respects.
        * Define a new ``@maybebeartype`` decorator disabling type-checking when
          an app-specific constant ``I_AM_RELEASE_BUILD`` defined elsewhere is
          enabled:

          .. code-block:: python

             # Import the requisite machinery.
             from beartype import beartype, BeartypeConf, BeartypeStrategy

             # Let us pretend you know what you are doing for a hot moment.
             from your_app import I_AM_RELEASE_BUILD

             # Dynamically create a new @maybebeartype decorator disabling
             # type-checking when "I_AM_RELEASE_BUILD" is enabled.
             maybebeartype = beartype(conf=BeartypeConf(strategy=(
                 BeartypeStrategy.O0
                 if I_AM_RELEASE_BUILD else
                 BeartypeStrategy.O1
             ))

             # Decorate with this decorator rather than @beartype everywhere.
             @maybebeartype
             def muh_performance_critical_func(big_list: list[int]) -> int:
                 return sum(big_list)

    .. _BeartypeStrategy.O1:

    * BeartypeStrategy.\ **O1** : beartype.cave.EnumMemberType

      **Constant-time strategy** (i.e., the default ``O(1)`` strategy,
      type-checking a single randomly selected item of each container). As the
      default, this strategy need *not* be explicitly enabled.

    .. _BeartypeStrategy.Ologn:

    * BeartypeStrategy.\ **Ologn** : beartype.cave.EnumMemberType

      **Logarithmic-time strategy** (i.e., the ``O(log n)`` strategy,
      type-checking a randomly selected number of items ``log(len(obj))`` of
      each container ``obj``). This strategy is **currently unimplemented.**
      (*To be implemented by a future beartype release.*)

    .. _BeartypeStrategy.On:

    * BeartypeStrategy.\ **On** : beartype.cave.EnumMemberType

      **Linear-time strategy** (i.e., the ``O(n)`` strategy, type-checking *all*
      items of a container). This strategy is **currently unimplemented.** (*To
      be implemented by a future beartype release.*)


*************
Beartype DOOR
*************

.. _beartype.door:

Enter the **DOOR** (\ **D**\ ecidedly **O**\ bject-\ **o**\ riented **R**\
untime-checker): the first usable public Pythonic API for introspecting,
comparing, and type-checking type hints in ``O(1)`` time with negligible
constants.

Procedural API
##############

Type-check *anything* at *any* time against *any* type hint. When the
``isinstance()`` and ``issubclass()`` builtins fail to scale, prefer the
``beartype.door`` procedural API.

.. # FIXME: Document the new "beartype.peps" submodule as well, please!

.. _beartype.door.die_if_unbearable:
.. _die_if_unbearable:

*def* beartype.door.\ **die_if_unbearable**\ (obj: object, hint: object, \*,
conf: beartype.BeartypeConf_ = BeartypeConf()) -> None

    **Type-hint exception raiser,** either:

    * Raising a **typing-checking violation** (i.e., human-readable
      beartype.roar.BeartypeCallHintViolation_ exception) if the passed
      arbitrary object ``obj`` violates the passed type hint ``hint`` under the
      passed beartype configuration ``conf``.
    * Reducing to a noop otherwise (i.e., if ``obj`` satisfies ``hint`` under
      ``conf``).

    .. code-block:: pycon

       >>> from beartype.door import die_if_unbearable
       >>> from beartype.typing import List, Sequence, Optional, Union
       >>> die_if_unbearable("My people ate them all!", Union[List[int], None])
       BeartypeDoorHintViolation: Object 'My people ate them all!' violates type
       hint typing.Optional[list[int]], as str 'My people ate them all!' not
       list or <class "builtins.NoneType">.
       >>> die_if_unbearable("I'm swelling with patriotic mucus!", Optional[str])
       >>> die_if_unbearable("I'm not on trial here.", Sequence[str])

    For those familiar with typeguard_, this function implements the beartype
    equivalent of the low-level typeguard.check_type_ function.

    See ``help(beartype.door.die_if_unbearable)`` for further details.

.. _beartype.door.is_bearable:
.. _is_bearable:

*def* beartype.door.\ **is_bearable**\ (obj: object, hint: object, \*, conf:
beartype.BeartypeConf_ = BeartypeConf()) -> bool

    **Type-hint tester,** returning either:

    * ``True`` if the passed arbitrary object ``obj`` satisfies the passed
      PEP-compliant type hint ``hint`` under the passed beartype configuration
      ``conf``.
    * ``False`` otherwise.

    .. code-block:: pycon

       >>> from beartype.door import is_bearable
       >>> from beartype.typing import List, Sequence, Optional, Union
       >>> is_bearable("Kif, I’m feeling the ‘Captain's itch.’", Optional[str])
       True
       >>> is_bearable('I hate these filthy Neutrals, Kif.', Sequence[str])
       True
       >>> is_bearable('Stop exploding, you cowards.', Union[List[bool], None])
       False

    This tester is a strict superset of the ``isinstance()`` builtin and can
    thus be safely called wherever that builtin is called with the same exact
    parameters in the same exact order:

    .. code-block:: pycon

       >>> from beartype.door import is_bearable
       >>> is_bearable('I surrender and volunteer for treason.', str)
       True
       >>> is_bearable(b'Stop exploding, you cowards.', (str, bytes))
       True
       >>> is_bearable('Comets, the icebergs of the sky.', bool | None)
       False

    This tester is also a *spiritual* superset of the ``issubclass()`` builtin
    and can thus be safely called wherever that builtin is called by replacing
    the superclass(es) to be tested against with a ``type[{superclass}]`` or
    ``typing.Union[type[{superclass1}], ..., type[{superclassN}]]`` type hint:

    .. code-block:: pycon

       >>> from beartype.door import is_bearable
       >>> from beartype.typing import Type, Union
       >>> from collections.abc import Awaitable, Collection, Iterable
       >>> is_bearable(str, Type[Iterable])
       True
       >>> is_bearable(bytes, Union[Type[Collection], Type[Awaitable]])
       True
       >>> is_bearable(bool, Union[Type[str], Type[float]])
       False

    See ``help(beartype.door.is_bearable)`` for further details.

.. _is_subhint:

*def* beartype.door.\ **is_subhint**\ (subhint: object, superhint: object) ->
bool

    **Subhint tester,** returning either:

    * ``True`` if the first passed PEP-compliant type hint is a **subhint** of
      the second passed PEP-compliant type hint, in which case the second hint
      is a **superhint** of the first hint.
    * ``False`` otherwise.

    .. code-block:: pycon

       # Import the requisite machinery.
       >>> from beartype.door import is_subhint

       # A type hint matching any callable accepting no arguments and returning
       # a list is a subhint of a type hint matching any callable accepting any
       # arguments and returning a sequence of any types.
       >>> is_subhint(Callable[[], list], Callable[..., Sequence[Any]])
       True

       # A type hint matching any callable accepting no arguments and returning
       # a list, however, is *NOT* a subhint of a type hint matching any
       # callable accepting any arguments and returning a sequence of integers.
       >>> is_subhint(Callable[[], list], Callable[..., Sequence[int]])
       False

       # Booleans are subclasses and thus subhints of integers.
       >>> is_subhint(bool, int)
       True

       # The converse, however, is *NOT* true.
       >>> is_subhint(int, bool)
       False

       # All classes are subclasses and thus subhints of themselves.
       >>> is_subhint(int, int)
       True

    Equivalently, this tester returns ``True`` only if *all* of the following
    conditions apply:

    * **Commensurability.** These two hints are **semantically related** (i.e.,
      convey broadly similar semantics enabling these two hints to be reasonably
      compared). For example:

      * ``callable.abc.Iterable[str]`` and ``callable.abc.Sequence[int]`` are
        semantically related. These two hints both convey container semantics.
        Despite their differing child hints, these two hints are broadly similar
        enough to be reasonably comparable.
      * ``callable.abc.Iterable[str]`` and ``callable.abc.Callable[[], int]``
        are *not* semantically related. Whereas the first hints conveys a
        container semantic, the second hint conveys a callable semantic. Since
        these two semantics are unrelated, these two hints are dissimilar
        enough to *not* be reasonably comparable.

    * **Narrowness.** The first hint is either **narrower** than or
      **semantically equivalent** to the second hint. Equivalently:

      * The first hint matches **less than or equal to** the total number of all
        possible objects matched by the second hint.
      * In `set theoretic jargon <set theory_>`__, the size of the countably
        infinite set of all possible objects matched by the first hint is **less
        than or equal to** that of those matched by the second hint.

    This tester supports a wide variety of practical use cases – including:

    * **Multiple dispatch.** A pure-Python decorator can implement `multiple
      dispatch`_ over multiple overloaded implementations of the same callable
      by calling this function. An overload of the currently called callable can
      be dispatched to if the types of the passed parameters are all
      **subhints** of the type hints annotating that overload.
    * Formal verification of **API compatibility** across version bumps.
      Automated tooling like linters, continuous integration (CI), `git` hooks,
      and integrated development environments (IDEs) can raise pre-release
      alerts prior to accidental publication of API breakage by calling this
      function. A Python API preserves backward compatibility if each type hint
      annotating each public class or callable of the current version of that
      API is a **superhint** of the type hint annotating the same class or
      callable of the prior release of that API.

    See ``help(beartype.door.is_subhint)`` for further details.

Procedural Showcase
*******************

By the power of beartype, you too shall catch all bugs.

Detect API Breakage
===================

Detect breaking API changes in arbitrary callables via type hints alone in ten
lines of code: :superscript:`...ignoring imports, docstrings, comments, and
blank lines to make us look better`

.. code-block:: python

   from beartype import beartype
   from beartype.door import is_subhint
   from beartype.peps import resolve_pep563
   from collections.abc import Callable

   @beartype
   def is_func_api_preserved(func_new: Callable, func_old: Callable) -> bool:
       '''
       ``True`` only if the signature of the first passed callable (presumably
       the newest version of some callable to be released) preserves backward
       API compatibility with the second passed callable (presumably an older
       previously released version of the first passed callable) according to
       the PEP-compliant type hints annotating these two callables.

       Parameters
       ----------
       func_new: Callable
           Newest version of a callable to test for API breakage.
       func_old: Callable
           Older version of that same callable.

       Returns
       ----------
       bool
           ``True`` only if the ``func_new`` API preserves the ``func_old`` API.
       '''

       # Resolve all PEP 563-postponed type hints annotating these two callables
       # *BEFORE* reasoning with these type hints.
       resolve_pep563(func_new)
       resolve_pep563(func_old)

       # For the name of each annotated parameter (or "return" for an annotated
       # return) and the hint annotating that parameter or return for this newer
       # callable...
       for func_arg_name, func_new_hint in func_new.__annotations__.items():
           # Corresponding hint annotating this older callable if any or "None".
           func_old_hint = func_old.__annotations__.get(func_arg_name)

           # If no corresponding hint annotates this older callable, silently
           # continue to the next hint.
           if func_old_hint is None:
               continue
           # Else, a corresponding hint annotates this older callable.

           # If this older hint is *NOT* a subhint of this newer hint, this
           # parameter or return breaks backward compatibility.
           if not is_subhint(func_old_hint, func_new_hint):
               return False
           # Else, this older hint is a subhint of this newer hint. In this case,
           # this parameter or return preserves backward compatibility.

       # All annotated parameters and returns preserve backward compatibility.
       return True

The proof is in the real-world pudding:

.. code-block:: pycon

   >>> from numbers import Real

   # New and successively older APIs of the same example function.
   >>> def new_func(text: str | None, ints: list[Real]) -> int: ...
   >>> def old_func(text: str, ints: list[int]) -> bool: ...
   >>> def older_func(text: str, ints: list) -> bool: ...

   # Does the newest version of that function preserve backward compatibility
   # with the next older version?
   >>> is_func_api_preserved(new_func, old_func)
   True  # <-- good. this is good.

   # Does the newest version of that function preserve backward compatibility
   # with the oldest version?
   >>> is_func_api_preserved(new_func, older_func)
   False  # <-- OH. MY. GODS.

In the latter case, the oldest version ``older_func()`` of that function
ambiguously annotated its ``ints`` parameter to accept *any* list rather than
merely a list of numbers. Both the newer version ``new_func()`` and the next
older version ``old_func()`` resolve the ambiguity by annotating that parameter
to accept *only* lists of numbers. Technically, that constitutes API breakage;
users upgrading from the older version of the package providing ``older_func()``
to the newer version of the package providing ``new_func()`` *could* have been
passing lists of non-numbers to ``older_func()``. Their code is now broke. Of
course, their code was probably always broke. But they're now screaming murder
on your issue tracker and all you can say is: "We shoulda used beartype."

In the former case, ``new_func()`` relaxes the constraint from ``old_func()``
that this list contain only integers to accept a list containing both integers
and floats. ``new_func()`` thus preserves backward compatibility with
``old_func()``.

**Thus was Rome's API preserved in a day.**

Object-oriented API
###################

.. #FIXME: Shift these anchor links to document these exact attributes *AFTER*
.. #we actually define documentation for these attributes below.
.. _beartype.door.TypeHint.die_if_unbearable:
.. _beartype.door.TypeHint.is_unbearable:

.. # FIXME: Synopsize this in our introduction and cheatsheet, please!
.. # FIXME: Synopsize class decoration in our introduction, too!

Introspect and compare type hints with an object-oriented hierarchy of Pythonic
classes. When the standard typing_ module has you scraping your fingernails on
the nearest whiteboard in chicken scratch, prefer the ``beartype.door``
object-oriented API.

You've already seen that type hints do *not* define a usable public Pythonic
API. This was by design. Type hints were *never* intended to be used at runtime.
But that's a bad design. Runtime is all that matters, ultimately. If the app
doesn't run, it's broke – regardless of what the static type-checker says. Now,
beartype breaks a trail through the spiny gorse of unusable PEP standards.

Open the locked cathedral of type hints with ``beartype.door``: your QA crowbar
that legally pries apart all type hints. Cry havoc, the bears of API war!

.. code-block:: pycon

   # This is DOOR. It's a Pythonic API providing an object-oriented interface
   # to low-level type hints that *OFFICIALLY* have no API whatsoever.
   >>> from beartype.door import TypeHint

   # DOOR hint wrapping a PEP 604-compliant type union.
   >>> union_hint = TypeHint(int | str | None)  # <-- so. it begins.

   # DOOR hints have Pythonic public classes -- unlike normal type hints.
   >>> type(union_hint)
   beartype.door.UnionTypeHint  # <-- what madness is this?

   # DOOR hints can be detected Pythonically -- unlike normal type hints.
   >>> from beartype.door import UnionTypeHint
   >>> isinstance(union_hint, UnionTypeHint)  # <-- *shocked face*
   True

   # DOOR hints can be type-checked Pythonically -- unlike normal type hints.
   >>> union_hint.is_bearable('The unbearable lightness of type-checking.')
   True
   >>> union_hint.die_if_unbearable(b'The @beartype that cannot be named.')
   beartype.roar.BeartypeDoorHintViolation: Object b'The @beartype that cannot
   be named.' violates type hint int | str | None, as bytes b'The @beartype
   that cannot be named.' not str, <class "builtins.NoneType">, or int.

   # DOOR hints can be iterated Pythonically -- unlike normal type hints.
   >>> for child_hint in union_hint: print(child_hint)
   TypeHint(<class 'int'>)
   TypeHint(<class 'str'>)
   TypeHint(<class 'NoneType'>)

   # DOOR hints can be indexed Pythonically -- unlike normal type hints.
   >>> union_hint[0]
   TypeHint(<class 'int'>)
   >>> union_hint[-1]
   TypeHint(<class 'str'>)

   # DOOR hints can be sliced Pythonically -- unlike normal type hints.
   >>> union_hint[0:2]
   (TypeHint(<class 'int'>), TypeHint(<class 'str'>))

   # DOOR hints supports "in" Pythonically -- unlike normal type hints.
   >>> TypeHint(int) in union_hint  # <-- it's all true.
   True
   >>> TypeHint(bool) in union_hint  # <-- believe it.
   False

   # DOOR hints are sized Pythonically -- unlike normal type hints.
   >>> len(union_hint)  # <-- woah.
   3

   # DOOR hints test as booleans Pythonically -- unlike normal type hints.
   >>> if union_hint: print('This type hint has children.')
   This type hint has children.
   >>> if not TypeHint(tuple[()]): print('But this other type hint is empty.')
   But this other type hint is empty.

   # DOOR hints support equality Pythonically -- unlike normal type hints.
   >>> from typing import Union
   >>> union_hint == TypeHint(Union[int, str, None])
   True  # <-- this is madness.

   # DOOR hints support comparisons Pythonically -- unlike normal type hints.
   >>> union_hint <= TypeHint(int | str | bool | None)
   True  # <-- madness continues.

   # DOOR hints publish the low-level type hints they wrap.
   >>> union_hint.hint
   int | str | None  # <-- makes sense.

   # DOOR hints publish tuples of the low-level child type hints subscripting
   # (indexing) the low-level parent type hints they wrap -- unlike normal type
   # hints, which unreliably publish similar tuples under differing names.
   >>> union_hint.args
   (int, str, NoneType)  # <-- sense continues to be made.

   # DOOR hints are semantically self-caching.
   >>> TypeHint(int | str | bool | None) is TypeHint(None | bool | str | int)
   True  # <-- blowing minds over here.

``beartype.door.TypeHint`` wrappers:

* Are **immutable**, **hashable**, and safely usable both as dictionary keys and
  in sets.
* Support efficient **lookup** of child type hints – just like **dictionaries**
  and **sets**.
* Support efficient **iteration** over and **random access** of child type hints
  – just like **lists** and **tuples**.
* Are **partially ordered** over the set of all type hints (according to the
  `subhint relation <is_subhint_>`__) and safely usable in any algorithm
  accepting a partial ordering (e.g., `topological sort`_).
* Guarantee similar performance as ``@beartype`` itself. All ``TypeHint``
  methods and properties run in (possibly `amortized <amortized analysis_>`__)
  **constant time** with negligible constants.

``beartype.door``: never leave typing_ without it.

.. # FIXME: Write us up, please.
.. # TypeHint Methods
.. # ~~~~~~~~~~~~~~~~
.. #
.. #
.. # TypeHint as Sequence
.. # ~~~~~~~~~~~~~~~~~~~~
.. #
.. # TypeHint as Set
.. # ~~~~~~~~~~~~~~~
.. #
.. # TypeHint Comparison
.. # ~~~~~~~~~~~~~~~~~~~

*******************
Beartype Exceptions
*******************

Beartype only raises:

* **Beartype-specific exceptions.** For your safety and ours, exceptions raised
  beartype are easily distinguished from exceptions raised by everybody else.
  *All* exceptions raised by beartype are instances of:

  * Public types importable from the ``beartype.roar`` subpackage.
  * The beartype.roar.BeartypeException_ abstract base class (ABC).

* **Disambiguous exceptions.** For your sanity and ours, *every* exception
  raised by beartype means one thing and one thing only. Beartype *never* reuses
  the same exception class to mean two different things – allowing you to
  trivially catch and handle the exact exception you're interested in.

Beartype is fastidious to a fault. Exception handling is no... *exception*.
<sup>punny *or* funny? you decide.</sup>

Exception API
#############

.. _BeartypeException:
.. _beartype.roar.BeartypeException:

*class* beartype.roar.\ **BeartypeException**\ (Exception)

    **Beartype exception root superclass.** *All* exceptions raised by beartype
    are guaranteed to be instances of concrete subclasses of this abstract base
    class (ABC) whose class names strictly match either:

    * ``Beartype{subclass_name}Exception`` for non-type-checking violations
      (e.g., ``BeartypeDecorHintPep3119Exception``).
    * ``Beartype{subclass_name}Violation`` for type-checking violations
      (e.g., ``BeartypeCallHintReturnViolation``).

.. _BeartypeDecorException:

*class* beartype.roar.\ **BeartypeDecorException**\ (BeartypeException_)

    **Beartype decorator exception superclass.** *All* exceptions raised by
    the ``@beartype`` decorator at decoration time (i.e., while dynamically
    generating type-checking wrappers for decorated callables and classes) are
    guaranteed to be instances of concrete subclasses of this abstract base
    class (ABC). Since decoration-time exceptions are typically raised from
    module scope early in the lifetime of a Python process, you are unlikely to
    manually catch and handle decorator exceptions.

    A detailed list of subclasses of this ABC is thus quite inconsequential.
    Very well. Leycec_ admits he was too tired to type it all out. Leycec_ also
    admits he played exploitative video games all night instead... *again*.
    Leycec_ is grateful nobody actually reads these API notes. <sup>checkmate,
    GitHub</sup>

.. _BeartypeCallHintException:

*class* beartype.roar.\ **BeartypeCallHintException**\ (BeartypeCallException)

    **Beartype type-checking exception superclass.** Beartype type-checkers
    (including beartype.door.die_if_unbearable_ and ``@beartype``\ -decorated
    callables) raise instances of concrete subclasses of this abstract base
    class (ABC) when failing a type-check at call time (e.g., due to passing a
    parameter or returning a value violating a type hint annotating that
    parameter or return). *All* exceptions raised when type-checking are
    guaranteed to be instances of this ABC. Since type-checking exceptions are
    typically raised from function and method scopes later in the lifetime of a
    Python process, you are *much* more likely to manually catch and handle
    type-checking exceptions than other types of beartype exceptions.

    In fact, you're encouraged to do so. Repeat after Kermode Bear: "Exceptions
    are fun, everybody." *Gotta catch 'em all!*

.. _BeartypeCallHintForwardRefException:

*class* beartype.roar.\ **BeartypeCallHintForwardRefException**\
(BeartypeCallHintException_)

    **Beartype type-checking forward reference exception.** Beartype
    type-checkers raise instances of this exception type when a **forward
    reference type hint** (i.e., string referring to a class that has yet to be
    defined) erroneously references either:

    * An attribute that does *not* exist.
    * An attribute that exists but whose value is *not* actually a class.

    As we gaze forward in time, so too do we glimpse ourselves – unshaven and
    shabbily dressed – in the rear-view mirror:

    .. code-block:: pycon

       >>> from beartype import beartype
       >>> from beartype.roar import BeartypeCallHintForwardRefException
       >>> @beartype
       ... def i_am_spirit_bear(favourite_foodstuff: 'salmon.of.course') -> None: pass
       >>> try:
       ...     i_am_spirit_bear('Why do you eat all my salmon, Spirit Bear?')
       ... except BeartypeCallHintForwardRefException as exception:
       ...     print(exception)
       Forward reference "salmon.of.course" unimportable.

.. _beartype.roar.BeartypeCallHintViolation:
.. _BeartypeCallHintViolation:

*class* beartype.roar.\ **BeartypeCallHintViolation**\
(BeartypeCallHintException_)

    **Beartype type-checking violation.** This is the most important beartype
    exception you never hope to see – and thus the beartype exception you are
    most likely to see. When your code explodes at midnight, instances of this
    exception class were probably lighting the fuse behind your back.

    Beartype type-checkers raise an instance of this exception class when an
    object to be type-checked violates the type hint annotating that object.
    Beartype type-checkers include:

    * The beartype.door.die_if_unbearable_ function.
    * The beartype.door.TypeHint.die_if_unbearable_ method.
    * User-defined functions and methods decorated by the beartype.beartype_
      decorator -- which then themselves become beartype type-checkers.

    Because type-checking violations are why we are all here, instances of this
    exception class offer additional read-only public properties to assist you
    in debugging. Inspect these properties at runtime to resolve any lingering
    doubts about which coworker(s) you intend to blame in your next twenty Git
    commits:

    .. _BeartypeCallHintViolation.culprits:

    * **culprits**\ : Tuple[object, ...]

      Tuple of one or more **culprits** (i.e., irresponsible objects that
      violated the type hints annotating those objects during a type-check).

      Specifically, this property returns either:

      * If a standard container (e.g., ``dict``, ``list``, ``set``, ``tuple``)
        is responsible for this violation, the 2-tuple
        ``(root_culprit, leaf_culprit)`` where:

        * ``root_culprit`` is the outermost such container. This is usually the
          passed parameter or returned value indirectly violating this type
          hint.
        * ``leaf_culprit`` is the innermost item nested in ``root_culprit``
          directly violating this type hint.

      * If a non-container (e.g., scalar, class instance) is responsible for
        this violation, the 1-tuple ``(culprit,)`` where ``culprit`` is that
        non-container.

      Let us examine what the latter means for the plucky intern (who will do
      this after fetching more pumpkin spice lattes for the team engrossed in a
      high-level morale-building "Best of 200" ping pong competition):

      .. code-block:: python

         # Import the requisite machinery.
         from beartype import beartype
         from beartype.roar import BeartypeCallHintViolation

         # Arbitrary user-defined classes.
         class SpiritBearIGiveYouSalmonToGoAway(object): pass
         class SpiritBearIGiftYouHoneyNotToStay(object): pass

         # Arbitrary instance of one of these classes.
         SPIRIT_BEAR_REFUSE_TO_GO_AWAY = SpiritBearIGiftYouHoneyNotToStay()

         # Callable annotated to accept instances of the *OTHER* class.
         @beartype
         def when_spirit_bear_hibernates_in_your_bed(
             best_bear_den: SpiritBearIGiveYouSalmonToGoAway) -> None: pass

         # Call this callable with this invalid instance.
         try:
             when_spirit_bear_hibernates_in_your_bed(
                 SPIRIT_BEAR_REFUSE_TO_GO_AWAY)
         # *MAGIC HAPPENS HERE*. Catch violations and inspect their "culprits"!
         except BeartypeCallHintViolation as violation:
             # Assert that one culprit was responsible for this violation.
             assert len(violation.culprits) == 1

             # The one culprit: don't think we don't see you hiding there!
             culprit = violation.culprits[0]

             # Assert that this culprit is the same instance passed above.
             assert culprit is SPIRIT_BEAR_REFUSE_TO_GO_AWAY

      **Caveats apply.** This property makes a good-faith effort to list the
      most significant culprits responsible for this type-checking violation. In
      two edge cases beyond our control, however, this property falls back to
      listing truncated snapshots of the machine-readable representations of
      those culprits (e.g., the first 10,000 characters or so of their `repr()`
      strings). This safe fallback is triggered for each culprit that:

      * Has **already been garbage-collected.** To avoid memory leaks, this
        property only weakly (rather than strongly) refers to these culprits and
        is thus best accessed only where these culprits are accessible.
        *Technically*, this property is safely accessible from any context.
        *Practically*, this property is most usefully accessed from the
        ``except ...:`` block directly catching this violation. Since these
        culprits may be garbage-collected at any time thereafter, this property
        *cannot* be guaranteed to refer to these culprits outside that block. If
        this property is accessed from any other context and one or more of
        these culprits have sadly passed away, this property dynamically reduces
        the corresponding items of this tuple to only the machine-readable
        representations of those culprits. :superscript:`This exception stored the
        representations of those culprits inside itself when first raised. Like
        a gruesome time capsule, they return to haunt you.`
      * Is a **builtin variable-sized C-based object** (e.g., ``dict``, ``int``,
        ``list``, ``str``). Long-standing limitations in CPython itself prevent
        beartype from weakly referring to those objects. Openly riot on the
        `CPython bug tracker`_ if this displeases you.

      Let us examine what this means for your malding CTO:

      .. code-block:: python

         # Import the requisite machinery.
         from beartype import beartype
         from beartype.roar import BeartypeCallHintViolation
         from beartype.typing import List

         # Callable annotated to accept a standard container.
         @beartype
         def we_are_all_spirit_bear(
             best_bear_dens: List[List[str]]) -> None: pass

         # Standard container deeply violating the above type hint.
         SPIRIT_BEAR_DO_AS_HE_LIKE = [
             [b'Why do you sleep in my pinball room, Spirit Bear?']]

         # Call this callable with this invalid container.
         try:
             we_are_all_spirit_bear(SPIRIT_BEAR_DO_AS_HE_LIKE)
         # Shoddy magic happens here. Catch violations and try (but fail) to
         # inspect the original culprits, because they were containers!
         except BeartypeCallHintViolation as violation:
             # Assert that two culprits were responsible for this violation.
             assert len(violation.culprits) == 2

             # Root and leaf culprits. We just made these words up, people.
             root_culprit = violation.culprits[0]
             leaf_culprit = violation.culprits[1]

             # Assert that these culprits are, in fact, just repr() strings.
             assert root_culprit == repr(SPIRIT_BEAR_DO_AS_HE_LIKE)
             assert leaf_culprit == repr(SPIRIT_BEAR_DO_AS_HE_LIKE[0][0])

      We see that beartype correctly identified the root culprit as the passed
      list of lists of byte-strings (rather than strings) *and* the leaf culprit
      as that byte-string. We also see that beartype only returned the
      ``repr()`` of both culprits rather than those culprits. Why? Because
      CPython prohibits weak references to both lists *and* byte-strings.

      This is why we facepalm ourselves in the morning. We did it this morning.
      We'll do it next morning, too. Until the weakref_ module improves,
      leycec's forehead *will* be swollen with an angry mass of unsightly red
      welts that are now festering unbeknownst to his wife.

      *First introduced in beartype 0.12.0.*

.. #FIXME: Resume here tomorrow, please.

.. # ------------------( IMAGES                              )------------------
.. |beartype-banner| image:: https://raw.githubusercontent.com/beartype/beartype-assets/main/banner/logo.png
   :target: https://github.com/beartype/beartype
   :alt: beartype —[ the bare-metal type-checker ]—

.. # ------------------( IMAGES ~ badge                      )------------------
.. |ci-badge| image:: https://github.com/beartype/beartype/workflows/test/badge.svg
   :target: https://github.com/beartype/beartype/actions?workflow=test
   :alt: beartype continuous integration (CI) status
.. |codecov-badge| image:: https://codecov.io/gh/beartype/beartype/branch/main/graph/badge.svg?token=E6F4YSY9ZQ
   :target: https://codecov.io/gh/beartype/beartype
   :alt: beartype test coverage status
.. |rtd-badge| image:: https://readthedocs.org/projects/beartype/badge/?version=latest
   :target: https://beartype.readthedocs.io/en/latest/?badge=latest
   :alt: beartype Read The Docs (RTD) status
