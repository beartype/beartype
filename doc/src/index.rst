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
type-checker <Usage_>`__ emphasizing efficiency, usability, and thrilling puns.

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
<Usage_>`__ against `type hints standardized by the Python community
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
<Usage_>`__.

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

  `beartype.vale.Is[...] <beartype.vale.Is_>`__: *it's lambdas all the way down.*

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
