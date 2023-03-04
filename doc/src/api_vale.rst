.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document detailing the public-facing API of
.. # the "beartype.vale" subpackage.

.. # ------------------( METADATA                            )------------------
.. # Fully-qualified name of the (sub)package described by this document,
.. # enabling this document to be externally referenced as :mod:`{name}`.
.. py:module:: beartype.vale

.. # ------------------( MAIN                                )------------------

*******************
Beartype Validators
*******************

::

   Validate anything with two-line type hints
          designed by you ⇄ built by beartype

When standards fail, do what you want anyway. When official type hints fail to
scale to your validation use case, design your own PEP-compliant type hints with
compact **beartype validators:**

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype
   from beartype.vale import Is
   from typing import Annotated   # <--------------- if Python ≥ 3.9.0
   #from typing_extensions import Annotated   # <--- if Python < 3.9.0

   # Type hint matching any two-dimensional NumPy array of floats of arbitrary
   # precision. Aye, typing matey. Beartype validators a-hoy!
   import numpy as np
   Numpy2DFloatArray = Annotated[np.ndarray, Is[lambda array:
       array.ndim == 2 and np.issubdtype(array.dtype, np.floating)]]

   # Annotate @beartype-decorated callables with beartype validators.
   @beartype
   def polygon_area(polygon: Numpy2DFloatArray) -> float:
       '''
       Area of a two-dimensional polygon of floats defined as a set of
       counter-clockwise points, calculated via Green's theorem.

       *Don't ask.*
       '''

       # Calculate and return the desired area. Pretend we understand this.
       polygon_rolled = np.roll(polygon, -1, axis=0)
       return np.abs(0.5*np.sum(
           polygon[:,0]*polygon_rolled[:,1] -
           polygon_rolled[:,0]*polygon[:,1]))

Validators enforce arbitrary runtime constraints on the internal structure and
contents of parameters and returns with user-defined lambda functions and
nestable declarative expressions leveraging familiar :mod:`typing` syntax – all
seamlessly composable with :ref:`standard type hints <eli5:typing>` via an
`expressive domain-specific language (DSL) <Validator Syntax_>`__.

Validate custom project constraints *now* without waiting for the open-source
community to officially standardize, implement, and publish those constraints.
Filling in the Titanic-sized gaps between :ref:`Python's patchwork quilt of PEPs
<pep:pep>`, validators accelerate your QA workflow with your greatest asset.

    Yup. It's your brain.

See `Validator Showcase`_ for comforting examples – or blithely continue for
uncomfortable details you may regret reading.

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

Validator Overview
##################

Beartype validators are **zero-cost code generators.** Like the rest of beartype
(but unlike other validation frameworks), beartype validators generate optimally
efficient pure-Python type-checking logic with *no* hidden function or method
calls, undocumented costs, or runtime overhead.

Beartype validator code is thus **call-explicit.** Since pure-Python function
and method calls are notoriously slow in CPython_, the code we generate only
calls the pure-Python functions and methods you specify when you subscript
``beartype.vale.Is*`` classes with those functions and methods. That's it. We
*never* call anything without your permission. For example:

* The declarative validator ``Annotated[np.ndarray, IsAttr['dtype',
  IsAttr['type', IsEqual[np.float64]]]]`` detects NumPy arrays of 64-bit
  floating-point precision by generating the fastest possible inline expression
  for doing so:

  .. code-block:: python

     isinstance(array, np.ndarray) and array.dtype.type == np.float64

* The functional validator ``Annotated[np.ndarray, Is[lambda array:
  array.dtype.type == np.float64]]`` also detects the same arrays by generating
  a slightly slower inline expression calling the lambda function you define:

  .. code-block:: python

     isinstance(array, np.ndarray) and your_lambda_function(array)

Beartype validators thus come in two flavours – each with attendant tradeoffs:

* **Functional validators,** created by subscripting the
  :class:`beartype.vale.Is` factory with a function accepting a single parameter
  and returning :data:`True` only when that parameter satisfies a caller-defined
  constraint. Each functional validator incurs the cost of calling that function
  for each call to each :func:`beartype.beartype`-decorated callable annotated
  by that validator, but is Turing-complete and thus supports all possible
  validation scenarios.
* **Declarative validators,** created by subscripting any *other* class in the
  :mod:`beartype.vale` subpackage (e.g., :class:`beartype.vale.IsEqual`) with
  arguments specific to that class. Each declarative validator generates
  efficient inline code calling *no* hidden functions and thus incurring no
  function costs, but is special-purpose and thus supports only a narrow band of
  validation scenarios.

Wherever you can, prefer *declarative* validators for efficiency.

Everywhere else, fallback to *functional* validators for generality.

Validator API
#############

.. py:class:: Is

       ``Subscription API:`` beartype.vale.\ **Is**\ [\
       :class:`collections.abc.Callable`\ [[:class:`object`\ ], :class:`bool`\ ]]

   **Functional validator.** A PEP-compliant type hint enforcing any arbitrary
   runtime constraint – created by subscripting (indexing) the :class:`.Is` type
   hint factory with a function accepting a single parameter and returning
   either:

   * :data:`True` if that parameter satisfies that constraint.
   * :data:`False` otherwise.

   .. code-block:: python

      # Import the requisite machinery.
      from beartype.vale import Is
      from typing import Annotated   # <--------------- if Python ≥ 3.9.0
      #from typing_extensions import Annotated   # <--- if Python < 3.9.0

      # Type hint matching only strings with lengths ranging [4, 40].
      LengthyString = Annotated[str, Is[lambda text: 4 <= len(text) <= 40]]

   Functional validators are caller-defined and may thus validate the internal
   integrity, consistency, and structure of arbitrary objects ranging from
   simple builtin scalars like integers and strings to complex data structures
   defined by third-party packages like NumPy arrays and Pandas DataFrames.


.. py:class:: IsAttr

       ``Subscription API:`` beartype.vale.\ **IsAttr**\ [\
       :class:`str`, ``beartype.vale.*``\ ]

   **Declarative attribute validator.** A PEP-compliant type hint enforcing any
   arbitrary runtime constraint on any named object attribute – created by
   subscripting (indexing) the :class:`.IsAttr` type hint factory with (in
   order):

   #. The unqualified name of that attribute.
   #. Any other beartype validator enforcing that constraint.

   .. code-block:: python

      # Import the requisite machinery.
      from beartype.vale import IsAttr, IsEqual
      from typing import Annotated   # <--------------- if Python ≥ 3.9.0
      #from typing_extensions import Annotated   # <--- if Python < 3.9.0

      # Type hint matching only two-dimensional NumPy arrays. Given this,
      # @beartype generates efficient validation code resembling:
      #     isinstance(array, np.ndarray) and array.ndim == 2
      import numpy as np
      Numpy2DArray = Annotated[np.ndarray, IsAttr['ndim', IsEqual[2]]]

   The first argument subscripting this class *must* be a syntactically valid
   unqualified Python identifier string containing only alphanumeric and
   underscore characters (e.g., ``"dtype"``, ``"ndim"``). Fully-qualified
   attributes comprising two or more dot-delimited identifiers (e.g.,
   ``"dtype.type"``) may be validated by nesting successive :class:`.IsAttr`
   subscriptions:

   .. code-block:: python

      # Type hint matching only NumPy arrays of 64-bit floating-point numbers.
      # From this, @beartype generates an efficient expression resembling:
      #     isinstance(array, np.ndarray) and array.dtype.type == np.float64
      NumpyFloat64Array = Annotated[np.ndarray,
          IsAttr['dtype', IsAttr['type', IsEqual[np.float64]]]]

   The second argument subscripting this class *must* be a beartype validator.
   This includes:

   * :class:`beartype.vale.Is`, in which case this parent :class:`.IsAttr` class
     validates the desired object attribute to satisfy the caller-defined
     function subscripting that child :class:`.Is` class.
   * :class:`beartype.vale.IsAttr`, in which case this parent :class:`.IsAttr`
     class validates the desired object attribute to contain a nested object
     attribute satisfying the child :class:`.IsAttr` class. See above example.
   * :class:`beartype.vale.IsEqual`, in which case this :class:`.IsAttr` class
     validates the desired object attribute to be equal to the object
     subscripting that :class:`.IsEqual` class. See above example.


.. py:class:: IsEqual

       ``Subscription API:`` beartype.vale.\ **IsEqual**\ [:class:`object`\ ]

   **Declarative equality validator.** A PEP-compliant type hint enforcing
   equality against any object – created by subscripting (indexing) the
   :class:`IsEqual` type hint factory with that object:

   .. code-block:: python

      # Import the requisite machinery.
      from beartype.vale import IsEqual
      from typing import Annotated   # <--------------- if Python ≥ 3.9.0
      #from typing_extensions import Annotated   # <--- if Python < 3.9.0

      # Type hint matching only lists equal to [0, 1, 2, ..., 40, 41, 42].
      AnswerToTheUltimateQuestion = Annotated[list, IsEqual[list(range(42))]]

   :class:`.IsEqual` generalizes the comparable :pep:`586`-compliant
   :obj:`typing.Literal` type hint. Both check equality against user-defined
   objects. Despite the differing syntax, these two type hints enforce the same
   semantics:

   .. code-block:: python

      # This beartype validator enforces the same semantics as...
      IsStringEqualsWithBeartype = Annotated[str,
          IsEqual['Don’t you envy our pranceful bands?'] |
          IsEqual['Don’t you wish you had extra hands?']
      ]

      # This PEP 586-compliant type hint.
      IsStringEqualsWithPep586 = Literal[
          'Don’t you envy our pranceful bands?',
          'Don’t you wish you had extra hands?',
      ]

   The similarities end there, of course:

   * :class:`.IsEqual` permissively validates equality against objects that are
     instances of **any arbitrary type.** :class:`.IsEqual` doesn't care what
     the types of your objects are. :class:`.IsEqual` will test equality against
     everything you tell it to, because you know best.
   * :obj:`typing.Literal` rigidly validates equality against objects that are
     instances of **only six predefined types:**

     * Booleans (i.e., :class:`bool` objects).
     * Byte strings (i.e., :class:`bytes` objects).
     * Integers (i.e., :class:`int` objects).
     * Unicode strings (i.e., :class:`str` objects).
     * :class:`enum.Enum` members. [#enum_type]_
     * The :data:`None` singleton.

   Wherever you can (which is mostly nowhere), prefer :obj:`typing.Literal`.
   Sure, :obj:`typing.Literal` is mostly useless, but it's standardized across
   type checkers in a mostly useless way. Everywhere else, default to
   :class:`.IsEqual`.


.. py:class:: IsInstance

       ``Subscription API:`` beartype.vale.\ **IsInstance**\ [:class:`type`\, ...]

   **Declarative instance validator.** A PEP-compliant type hint enforcing
   instancing of one or more classes – created by subscripting (indexing) the
   :class:`.IsInstance` type hint factory with those classes:

   .. code-block:: python

      # Import the requisite machinery.
      from beartype.vale import IsInstance
      from typing import Annotated   # <--------------- if Python ≥ 3.9.0
      #from typing_extensions import Annotated   # <--- if Python < 3.9.0

      # Type hint matching only string and byte strings, equivalent to:
      #     StrOrBytesInstance = Union[str, bytes]
      StrOrBytesInstance = Annotated[object, IsInstance[str, bytes]]

   :class:`.IsInstance` generalizes **isinstanceable type hints** (i.e., normal
   pure-Python or C-based classes that can be passed as the second parameter to
   the :func:`isinstance` builtin). Both check instancing of classes. Despite
   the differing syntax, the following hints all enforce the same semantics:

   .. code-block:: python

      # This beartype validator enforces the same semantics as...
      IsUnicodeStrWithBeartype = Annotated[object, IsInstance[str]]

      # ...this PEP 484-compliant type hint.
      IsUnicodeStrWithPep484 = str

      # Likewise, this beartype validator enforces the same semantics as...
      IsStrWithWithBeartype = Annotated[object, IsInstance[str, bytes]]

      # ...this PEP 484-compliant type hint.
      IsStrWithWithPep484 = Union[str, bytes]

   The similarities end there, of course:

   * :class:`.IsInstance` permissively validates type instancing of **arbitrary
     objects** (including possibly nested attributes of parameters and returns
     when combined with :class:`beartype.vale.IsAttr`) against **one or more
     classes.**
   * Isinstanceable classes rigidly validate type instancing of only
     **parameters and returns** against only **one class.**

   Unlike isinstanceable type hints, instance validators support various `set
   theoretic operators <Validator Syntax_>`__. Critically, this includes
   negation. Instance validators prefixed by the negation operator ``~`` match
   all objects that are *not* instances of the classes subscripting those
   validators. Wait. Wait just a hot minute there. Doesn't a
   :obj:`typing.Annotated` type hint necessarily match instances of the class
   subscripting that type hint? Yup. This means type hints of the form
   ``typing.Annotated[{superclass}, ~IsInstance[{subclass}]`` match all
   instances of a superclass that are *not* also instances of a subclass. And...
   pretty sure we just invented `type hint arithmetic <Type Hint Elision_>`__
   right there.

   That sounded intellectual and thus boring. Yet, the disturbing fact that
   Python booleans are integers :sup:`...yup` while Python strings are
   infinitely recursive sequences of strings :sup:`...yup` means that
   `type hint arithmetic <Type Hint Elision_>`__ can save your codebase from
   Guido's younger self. Consider this instance validator matching only
   non-boolean integers, which *cannot* be expressed with any isinstanceable
   type hint (e.g., :class:`int`) or other combination of standard off-the-shelf
   type hints (e.g., unions):

   .. code-block:: python

      # Type hint matching any non-boolean integer. Never fear integers again.
      IntNonbool = Annotated[int, ~IsInstance[bool]]   # <--- bruh

   Wherever you can, prefer isinstanceable type hints. Sure, they're inflexible,
   but they're inflexibly standardized across type checkers. Everywhere else,
   default to :class:`.IsInstance`.


.. py:class:: IsSubclass

       ``Subscription API:`` beartype.vale.\ **IsSubclass**\ [:class:`type`\, ...]

   **Declarative inheritance validator.** A PEP-compliant type hint enforcing
   subclassing of one or more superclasses (base classes) – created by
   subscripting (indexing) the :class:`.IsSubclass` type hint factory with those
   superclasses:

   .. code-block:: python

      # Import the requisite machinery.
      from beartype.vale import IsSubclass
      from typing import Annotated   # <--------------- if Python ≥ 3.9.0
      #from typing_extensions import Annotated   # <--- if Python < 3.9.0

      # Type hint matching only string and byte string subclasses.
      StrOrBytesSubclass = Annotated[type, IsSubclass[str, bytes]]

   :class:`.IsSubclass` generalizes the comparable :pep:`484`-compliant
   :obj:`typing.Type` and :pep:`585`-compliant :class:`type` type hint
   factories. All three check subclassing of arbitrary superclasses. Despite the
   differing syntax, the following hints all enforce the same semantics:

   .. code-block:: python

      # This beartype validator enforces the same semantics as...
      IsStringSubclassWithBeartype = Annotated[type, IsSubclass[str]]

      # ...this PEP 484-compliant type hint as well as...
      IsStringSubclassWithPep484 = Type[str]

      # ...this PEP 585-compliant type hint.
      IsStringSubclassWithPep585 = type[str]

   The similarities end there, of course:

   * :class:`.IsSubclass` permissively validates type inheritance of **arbitrary
     classes** (including possibly nested attributes of parameters and returns
     when combined with :class:`beartype.vale.IsAttr`) against **one or more
     superclasses.**
   * :obj:`typing.Type` and :class:`type` rigidly validates type inheritance of
     only **parameters and returns** against only **one superclass.**

   Consider this subclass validator, which validates type inheritance of a
   deeply nested attribute and thus *cannot* be expressed with
   :obj:`typing.Type` or :class:`type`:

   .. code-block:: python

      # Type hint matching only NumPy arrays of reals (i.e., either integers
      # or floats) of arbitrary precision, generating code resembling:
      #    (isinstance(array, np.ndarray) and
      #     issubclass(array.dtype.type, (np.floating, np.integer)))
      NumpyRealArray = Annotated[
          np.ndarray, IsAttr['dtype', IsAttr['type', IsSubclass[
              np.floating, np.integer]]]]

   Wherever you can, prefer :class:`type` and :obj:`typing.Type`. Sure, they're
   inflexible, but they're inflexibly standardized across type checkers.
   Everywhere else, default to :class:`.IsSubclass`.

.. [#enum_type]
   You don't want to know the type of :class:`enum.Enum` members. Srsly. You
   don't. Okay... you do? Very well. It's :class:`enum.Enum`. :sup:`mic
   drop`

.. _vale:vale syntax:

Validator Syntax
################

Beartype validators support a rich domain-specific language (DSL) leveraging
familiar Python operators. Dynamically create new validators on-the-fly from
existing validators, fueling reuse and preserving DRY_:

* **Negation** (i.e., ``not``). Negating any validator with the ``~`` operator
  creates a new validator returning :data:`True` only when the negated validator
  returns :data:`False`:

  .. code-block:: python

     # Type hint matching only strings containing *no* periods, semantically
     # equivalent to this type hint:
     #     PeriodlessString = Annotated[str, Is[lambda text: '.' not in text]]
     PeriodlessString = Annotated[str, ~Is[lambda text: '.' in text]]

* **Conjunction** (i.e., ``and``). And-ing two or more validators with the
  ``&`` operator creates a new validator returning :data:`True` only when *all*
  of the and-ed validators return :data:`True`:

  .. code-block:: python

     # Type hint matching only non-empty strings containing *no* periods,
     # semantically equivalent to this type hint:
     #     NonemptyPeriodlessString = Annotated[
     #         str, Is[lambda text: text and '.' not in text]]
     SentenceFragment = Annotated[str, (
          Is[lambda text: bool(text)] &
         ~Is[lambda text: '.' in text]
     )]

* **Disjunction** (i.e., ``or``). Or-ing two or more validators with the ``|``
  operator creates a new validator returning :data:`True` only when at least one
  of the or-ed validators returns :data:`True`:

  .. code-block:: python

     # Type hint matching only empty strings *and* non-empty strings containing
     # one or more periods, semantically equivalent to this type hint:
     #     EmptyOrPeriodfullString = Annotated[
     #         str, Is[lambda text: not text or '.' in text]]
     EmptyOrPeriodfullString = Annotated[str, (
         ~Is[lambda text: bool(text)] |
          Is[lambda text: '.' in text]
     )]

* **Enumeration** (i.e., ``,``). Delimiting two or or more validators with
  commas at the top level of a :obj:`typing.Annotated` type hint is an alternate
  syntax for and-ing those validators with the ``&`` operator, creating a new
  validator returning :data:`True` only when *all* of those delimited validators
  return :data:`True`.

  .. code-block:: python

     # Type hint matching only non-empty strings containing *no* periods,
     # semantically equivalent to the "SentenceFragment" defined above.
     SentenceFragment = Annotated[str,
          Is[lambda text: bool(text)],
         ~Is[lambda text: '.' in text],
     ]

  Since the ``&`` operator is more explicit *and* usable in a wider variety of
  syntactic contexts, the ``&`` operator is generally preferable to enumeration
  (all else being equal).
* **Interoperability.** As PEP-compliant type hints, validators are safely
  interoperable with other PEP-compliant type hints and usable wherever other
  PEP-compliant type hints are usable. Standard type hints are subscriptable
  with validators, because validators *are* standard type hints:

  .. code-block:: python

     # Type hint matching only sentence fragments defined as either Unicode or
     # byte strings, generalizing "SentenceFragment" type hints defined above.
     SentenceFragment = Union[
         Annotated[bytes, Is[lambda text: b'.' in text]],
         Annotated[str,   Is[lambda text: u'.' in text]],
     ]

`Standard Python precedence rules <_operator precedence>`__ may apply.

DSL: *it's not just a telecom acronym anymore.*

Validator Caveats
#################

.. note::

   **Validators require:**

   * **Beartype.** Currently, all *other* static and runtime type checkers
     silently ignore beartype validators during type-checking. This includes
     mypy_ – which we could possibly solve by bundling a `mypy plugin`_ with
     beartype that extends mypy_ to statically analyze declarative beartype
     validators (e.g., :class:`beartype.vale.IsAttr`,
     :class:`beartype.vale.IsEqual`). We leave this as an exercise to the
     idealistic doctoral thesis candidate. :sup:`Please do this for us,
     someone who is not us.`
   * Either **Python ≥ 3.9** *or* `typing_extensions ≥ 3.9.0.0
     <typing_extensions_>`__. Validators piggyback onto the
     :obj:`typing.Annotated` class first introduced with Python 3.9.0 and since
     backported to older Python versions by the `third-party "typing_extensions"
     package <typing_extensions_>`__, which beartype also transparently
     supports.

Validator Showcase
##################

Observe the disturbing (yet alluring) utility of beartype validators in action
as they unshackle type hints from the fetters of PEP compliance. Begone,
foulest standards!

Full-Fat O(n) Matching
**********************

Let's validate **all integers in a list of integers in O(n) time**, because
validators mean you no longer have to accept the QA scraps we feed you:

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype
   from beartype.vale import Is
   from typing import Annotated   # <--------------- if Python ≥ 3.9.0
   #from typing_extensions import Annotated   # <--- if Python < 3.9.0

   # Type hint matching all integers in a list of integers in O(n) time. Please
   # never do this. You now want to, don't you? Why? You know the price! Why?!?
   IntList = Annotated[list[int], Is[lambda lst: all(
       isinstance(item, int) for item in lst)]]

   # Type-check all integers in a list of integers in O(n) time. How could you?
   @beartype
   def sum_intlist(my_list: IntList) -> int:
       '''
       The slowest possible integer summation over the passed list of integers.

       There goes your whole data science pipeline. Yikes! So much cringe.
       '''

       return sum(my_list)  # oh, gods what have you done

Welcome to **full-fat type-checking.** In `our disastrous roadmap to beartype
1.0.0 <beartype 1.0.0_>`__, we reluctantly admit that we'd like to augment the
:func:`beartype.beartype` decorator with a new parameter enabling full-fat
type-checking. But don't wait for us. Force the issue now by just doing it
yourself and then mocking us all over Gitter! *Fight the bear, man.*

:ref:`There are good reasons to believe that O(1) type-checking is preferable
<faq:O1>`. Violating that core precept exposes your codebase to scalability and
security concerns. But you're the Big Boss, you swear you know best, and (in any
case) we can't stop you because we already let the unneutered tomcat out of his
trash bin by `publishing this API into the badlands of PyPI <beartype PyPI_>`__.

Trendy String Matching
**********************

Let's accept strings either at least 80 characters long *or* both quoted and
suffixed by a period. Look, it doesn't matter. Just do it already, beartype!

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype
   from beartype.vale import Is
   from typing import Annotated   # <--------------- if Python ≥ 3.9.0
   #from typing_extensions import Annotated   # <--- if Python < 3.9.0

   # Validator matching only strings at least 80 characters in length.
   IsLengthy = Is[lambda text: len(text) >= 80]

   # Validator matching only strings suffixed by a period.
   IsSentence = Is[lambda text: text and text[-1] == '.']

   # Validator matching only single- or double-quoted strings.
   def _is_quoted(text): return text.count('"') >= 2 or text.count("'") >= 2
   IsQuoted = Is[_is_quoted]

   # Combine multiple validators by just listing them sequentially.
   @beartype
   def desentence_lengthy_quoted_sentence(
       text: Annotated[str, IsLengthy, IsSentence, IsQuoted]]) -> str:
       '''
       Strip the suffixing period from a lengthy quoted sentence... 'cause.
       '''

       return text[:-1]  # this is horrible

   # Combine multiple validators by just "&"-ing them sequentially. Yes, this
   # is exactly identical to the prior function. We do this because we can.
   @beartype
   def desentence_lengthy_quoted_sentence_part_deux(
       text: Annotated[str, IsLengthy & IsSentence & IsQuoted]]) -> str:
       '''
       Strip the suffixing period from a lengthy quoted sentence... again.
       '''

       return text[:-1]  # this is still horrible

   # Combine multiple validators with as many "&", "|", and "~" operators as
   # you can possibly stuff into a module that your coworkers can stomach.
   # (They will thank you later. Possibly much later.)
   @beartype
   def strip_lengthy_or_quoted_sentence(
       text: Annotated[str, IsLengthy | (IsSentence & ~IsQuoted)]]) -> str:
       '''
       Strip the suffixing character from a string that is lengthy and/or a
       quoted sentence, because your web app deserves only the best data.
       '''

       return text[:-1]  # this is frankly outrageous

Type Hint Arithmetic
********************

    **Subtitle:** *From Set Theory They Shall Grow*

:pep:`484` standardized the :obj:`typing.Union` factory `disjunctively
<disjunction_>`__ matching any of several equally permissible type hints ala
Python's builtin ``or`` operator or the overloaded ``|`` operator for sets.
That's great, because set theory is the beating heart behind type theory.

But that's just disjunction_. What about intersection_ (e.g., ``and``, ``&``),
`complementation <relative set complement_>`__ (e.g., ``not``, ``~``), or any
of the vast multitude of *other* set theoretic operations? Can we logically
connect simple type hints validating trivial constraints into complex type
hints validating non-trivial constraints via PEP-standardized analogues of
unary and binary operators?

**Nope.** They don't exist yet. But that's okay. You use beartype, which means
you don't have to wait for official Python developers to get there first.
You're already there. :sup:`...woah`

Type Hint Elision
=================

Python's core type hierarchy conceals an ugly history of secretive backward
compatibility. In this subsection, we uncover the two filthiest, flea-infested,
backwater corners of the otherwise well-lit atrium that is the Python language
– and how exactly you can finalize them. Both obstruct type-checking, readable
APIs, and quality assurance in the post-Python 2.7 era.

Guido doesn't want you to know. But you want to know, don't you? You are about
to enter another dimension, a dimension not only of syntax and semantics but of
shame. A journey into a hideous land of annotation wrangling. Next stop... *the
Beartype Zone.* Because guess what?

* **Booleans are integers.** They shouldn't be. Booleans aren't integers in most
  high-level languages. Wait. Are you telling me booleans are literally integers
  in Python? Surely you jest. That can't be. You can't *add* booleans, can you?
  What would that even mean if you could? Observe and cower, rigorous data
  scientists.

  .. code-block:: python

     >>> True + 3.1415
     4.141500000000001  # <-- oh. by. god.
     >>> isinstance(False, int)
     True               # <-- when nothing is true, everything is true

* **Strings are infinitely recursive sequences of...** yup, it's strings. They
  shouldn't be. Strings aren't infinitely recursive data structures in any
  other language devised by incautious mortals – high-level or not. Wait. Are
  you telling me strings are both indistinguishable from full-blown immutable
  sequences containing arbitrary items *and* infinitely recurse into themselves
  like that sickening non-Euclidean Hall of Mirrors I puked all over when I was
  a kid? Surely you kid. That can't be. You can't infinitely index into strings
  *and* pass and return the results to and from callables expecting either
  ``Sequence[Any]`` or ``Sequence[str]`` type hints, can you? Witness and
  tremble, stricter-than-thou QA evangelists.

  .. code-block:: python

     >>> 'yougottabekiddi—'[0][0][0][0][0][0][0][0][0][0][0][0][0][0][0]
     'y'   # <-- pretty sure we just broke the world
     >>> from collections.abc import Sequence
     >>> isinstance("Ph'nglui mglw'nafh Cthu—"[0][0][0][0][0], Sequence)
     True  # <-- ...curse you, curse you to heck and back

When we annotate a callable as accepting an :class:`int`, we *never* want that
callable to also silently accept a :class:`bool`. Likewise, when we annotate
another callable as accepting a ``Sequence[Any]`` or ``Sequence[str]``, we
*never* want that callable to also silently accept a :class:`str`. These are
sensible expectations – just not in Python, where madness prevails.

To resolve these counter-intuitive concerns, we need the equivalent of the
`relative set complement (or difference) <relative set complement_>`__. We now
call this thing... **type elision!** Sounds pretty hot, right? We know.

Booleans ≠ Integers
-------------------

Let's first validate **non-boolean integers** with a beartype validator
effectively declaring a new ``int - bool`` class (i.e., the subclass of all
integers that are *not* booleans):

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype
   from beartype.vale import IsInstance
   from typing import Annotated   # <--------------- if Python ≥ 3.9.0
   #from typing_extensions import Annotated   # <--- if Python < 3.9.0

   # Type hint matching any non-boolean integer. This day all errata die.
   IntNonbool = Annotated[int, ~IsInstance[bool]]   # <--- bruh

   # Type-check zero or more non-boolean integers summing to a non-boolean
   # integer. Beartype wills it. So it shall be.
   @beartype
   def sum_ints(*args: IntNonbool) -> IntNonbool:
       '''
       I cast thee out, mangy booleans!

       You plague these shores no more.
       '''

       return sum(args)

Strings ≠ Sequences
-------------------

Let's next validate **non-string sequences** with beartype validators
effectively declaring a new ``Sequence - str`` class (i.e., the subclass of all
sequences that are *not* strings):

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype
   from beartype.vale import IsInstance
   from collections.abc import Sequence
   from typing import Annotated   # <--------------- if Python ≥ 3.9.0
   #from typing_extensions import Annotated   # <--- if Python < 3.9.0

   # Type hint matching any non-string sequence. Your day has finally come.
   SequenceNonstr = Annotated[Sequence, ~IsInstance[str]]   # <--- we doin this

   # Type hint matching any non-string sequence *WHOSE ITEMS ARE ALL STRINGS.*
   SequenceNonstrOfStr = Annotated[Sequence[str], ~IsInstance[str]]

   # Type-check a non-string sequence of arbitrary items coerced into strings
   # and then joined on newline to a new string. (Beartype got your back, bro.)
   @beartype
   def join_objects(my_sequence: SequenceNonstr) -> str:
       '''
       Your tide of disease ends here, :class:`str` class!
       '''

       return '\n'.join(map(str, my_sequence))  # <-- no idea how that works

   # Type-check a non-string sequence whose items are all strings joined on
   # newline to a new string. It isn't much, but it's all you ask.
   @beartype
   def join_strs(my_sequence: SequenceNonstrOfStr) -> str:
       '''
       I expectorate thee up, sequence of strings.
       '''

       return '\n'.join(my_sequence)  # <-- do *NOT* do this to a string

.. _api:tensor:

Tensor Property Matching
************************

Let's validate `the same two-dimensional NumPy array of floats of arbitrary
precision as in the lead example above <Beartype Validators_>`__ with an
efficient declarative validator avoiding the additional stack frame imposed by
the functional validator in that example:

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype
   from beartype.vale import IsAttr, IsEqual, IsSubclass
   from typing import Annotated   # <--------------- if Python ≥ 3.9.0
   #from typing_extensions import Annotated   # <--- if Python < 3.9.0

   # Type hint matching only two-dimensional NumPy arrays of floats of
   # arbitrary precision. This time, do it faster than anyone has ever
   # type-checked NumPy arrays before. (Cue sonic boom, Chuck Yeager.)
   import numpy as np
   Numpy2DFloatArray = Annotated[np.ndarray,
       IsAttr['ndim', IsEqual[2]] &
       IsAttr['dtype', IsAttr['type', IsSubclass[np.floating]]]
   ]

   # Annotate @beartype-decorated callables with beartype validators.
   @beartype
   def polygon_area(polygon: Numpy2DFloatArray) -> float:
       '''
       Area of a two-dimensional polygon of floats defined as a set of
       counter-clockwise points, calculated via Green's theorem.

       *Don't ask.*
       '''

       # Calculate and return the desired area. Pretend we understand this.
       polygon_rolled = np.roll(polygon, -1, axis=0)
       return np.abs(0.5*np.sum(
           polygon[:,0]*polygon_rolled[:,1] -
           polygon_rolled[:,0]*polygon[:,1]))

Validator Alternatives
######################

If the unbridled power of beartype validators leaves you variously queasy,
uneasy, and suspicious of our core worldview, beartype also supports third-party
type hints like `typed NumPy arrays <NumPy Type Hints_>`__.

Whereas beartype validators are verbose, expressive, and general-purpose, the
following hints are terse, inexpressive, and domain-specific. Since beartype
internally converts these hints to their equivalent validators, `similar
caveats apply <Validator Caveats_>`__. Notably, these hints require:

* Either **Python ≥ 3.9** *or* `typing_extensions ≥ 3.9.0.0
  <typing_extensions_>`__.
* **Beartype,** which hopefully goes without saying.

.. _api:numpy:

NumPy Type Hints
****************

Beartype conditionally supports `NumPy type hints (i.e., annotations created by
subscripting (indexing) various attributes of the "numpy.typing" subpackage)
<numpy.typing_>`__ when these optional runtime dependencies are *all* satisfied:

* Python ≥ 3.8.0.
* beartype ≥ 0.8.0.
* `NumPy ≥ 1.21.0 <NumPy_>`__.
* Either **Python ≥ 3.9** *or* `typing_extensions ≥ 3.9.0.0
  <typing_extensions_>`__.

Beartype internally converts `NumPy type hints <numpy.typing_>`__ into
`equivalent beartype validators <Beartype Validators_>`__ at decoration time.
`NumPy type hints currently only validate dtypes <numpy.typing_>`__, a common
but limited use case. `Beartype validators <Beartype Validators_>`__ validate
*any* arbitrary combinations of array constraints – including dtypes, shapes,
contents, and... well, *anything.* Which is alot. `NumPy type hints
<numpy.typing.NDArray_>`__ are thus just syntactic sugar for `beartype
validators <Beartype Validators_>`__ – albeit quasi-portable syntactic sugar
also supported by mypy_.

Wherever you can, prefer `NumPy type hints <numpy.typing_>`__ for portability.
Everywhere else, default to `beartype validators <Beartype Validators_>`__ for
generality. Combine them for the best of all possible worlds:

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype
   from beartype.vale import IsAttr, IsEqual
   from numpy import floating
   from numpy.typing import NDArray
   from typing import Annotated   # <--------------- if Python ≥ 3.9.0
   #from typing_extensions import Annotated   # <--- if Python < 3.9.0

   # Beartype validator + NumPy type hint matching all two-dimensional NumPy
   # arrays of floating-point numbers of any arbitrary precision.
   NumpyFloat64Array = Annotated[NDArray[floating], IsAttr['ndim', IsEqual[2]]]

Rejoice! A one-liner solves everything yet again.

Typed NumPy Arrays
==================

Type NumPy arrays by subscripting (indexing) the numpy.typing.NDArray_ class
with one of three possible types of objects:

* An **array dtype** (i.e., instance of the numpy.dtype_ class).
* A **scalar dtype** (i.e., concrete subclass of the numpy.generic_ abstract
  base class (ABC)).
* A **scalar dtype ABC** (i.e., abstract subclass of the numpy.generic_ ABC).

Beartype generates fundamentally different type-checking code for these types,
complying with both mypy_ semantics (which behaves similarly) and our userbase
(which demands this behaviour). May there be hope for our collective future.

*class* numpy.typing.\ **NDArray**\ [numpy.dtype_\ ]

    **NumPy array typed by array dtype.** A PEP-noncompliant type hint enforcing
    object equality against any **array dtype** (i.e., numpy.dtype_ instance),
    created by subscripting (indexing) the numpy.typing.NDArray_ class with that
    array dtype.

    Prefer this variant when validating the exact data type of an array:

    .. code-block:: python

       # Import the requisite machinery.
       from beartype import beartype
       from numpy import dtype
       from numpy.typing import NDArray

       # NumPy type hint matching all NumPy arrays of 32-bit big-endian integers,
       # semantically equivalent to this beartype validator:
       #     NumpyInt32BigEndianArray = Annotated[
       #         np.ndarray, IsAttr['dtype', IsEqual[dtype('>i4')]]]
       NumpyInt32BigEndianArray = NDArray[dtype('>i4')]

*class* numpy.typing.\ **NDArray**\ [numpy.dtype.type_\ ]

    **NumPy array typed by scalar dtype.** A PEP-noncompliant type hint
    enforcing object equality against any **scalar dtype** (i.e., concrete
    subclass of the numpy.generic_ ABC), created by subscripting (indexing) the
    numpy.typing.NDArray_ class with that scalar dtype.

    Prefer this variant when validating the exact scalar precision of an array:

    .. code-block:: python

       # Import the requisite machinery.
       from beartype import beartype
       from numpy import float64
       from numpy.typing import NDArray

       # NumPy type hint matching all NumPy arrays of 64-bit floats, semantically
       # equivalent to this beartype validator:
       #     NumpyFloat64Array = Annotated[
       #         np.ndarray, IsAttr['dtype', IsAttr['type', IsEqual[float64]]]]
       NumpyFloat64Array = NDArray[float64]

    Common scalar dtypes include:

    * **Fixed-precision integer dtypes** (e.g., ``numpy.int32``,
      ``numpy.int64``).
    * **Fixed-precision floating-point dtypes** (e.g.,
      ``numpy.float32``, ``numpy.float64``).

*class* numpy.typing.\ **NDArray**\ [type_\ [numpy.dtype.type_\ ]]

    **NumPy array typed by scalar dtype ABC.** A PEP-noncompliant type hint
    enforcing type inheritance against any **scalar dtype ABC** (i.e.,
    abstract subclass of the numpy.generic_ ABC), created by subscripting
    (indexing) the numpy.typing.NDArray_ class with that ABC.

    Prefer this variant when validating only the *kind* of scalars (without
    reference to exact precision) in an array:

    .. code-block:: python

       # Import the requisite machinery.
       from beartype import beartype
       from numpy import floating
       from numpy.typing import NDArray

       # NumPy type hint matching all NumPy arrays of floats of arbitrary
       # precision, equivalent to this beartype validator:
       #     NumpyFloatArray = Annotated[
       #         np.ndarray, IsAttr['dtype', IsAttr['type', IsSubclass[floating]]]]
       NumpyFloatArray = NDArray[floating]

    Common scalar dtype ABCs include:

    * numpy.integer_, the superclass of all fixed-precision integer dtypes.
    * numpy.floating_, the superclass of all fixed-precision floating-point
      dtypes.
