.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document gently introducing this project.

.. # ------------------( MAIN                                )------------------

.. # _ELI5:

####
ELI5
####

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

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Project-wide tables of contents (TOCs). See also official documentation on
.. # the Sphinx-specific "toctree::" directive:
.. #     https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree

|

.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

**********
Comparison
**********

Beartype is zero-cost. Beartype inflicts *no* harmful developer tradeoffs,
instead stressing expense-free strategies at both:

* **Installation time.** Beartype has no install-time or runtime dependencies,
  `supports standard Python package managers <Install_>`__, and happily
  coexists with competing static type-checkers and other runtime type-checkers.
* **Runtime.** Thanks to aggressive memoization and dynamic code generation at
  decoration time, beartype guarantees `O(1) non-amortized worst-case runtime
  complexity with negligible constant factors <Timings_>`__.

...versus Static Type-checkers
##############################

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

...versus Runtime Type-checkers
###############################

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

**********
Quickstart
**********

Beartype makes type-checking painless, portable, and purportedly fun. Just:

    Decorate functions and methods `annotated by standard type hints <Standard
    Hints_>`__ with the @beartype.beartype_ decorator, which wraps those
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

Standard Hints
##############

Beartype supports *most* `type hints standardized by the developer community
through Python Enhancement Proposals (PEPs) <Compliance_>`__. Since type hinting
is its own special hell, we'll start by wading into the thalassophobia-inducing
waters of type-checking with a sane example – the O(1) ``@beartype`` way.

Toy Example
***********

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
******************

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
