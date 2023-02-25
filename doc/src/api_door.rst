.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document detailing the public-facing API of
.. # the "beartype.door" subpackage.

.. # ------------------( TODO                                )------------------
.. # FIXME: Substantially improve the documentation for the object-oriented API
.. # defined by the "beartype.door" subpackage.

.. # ------------------( METADATA                            )------------------
.. # Fully-qualified name of the (sub)package described by this document,
.. # enabling this document to be externally referenced as :mod:`{name}`.
.. py:module:: beartype.door

.. # ------------------( MAIN                                )------------------
.. _door:door:

.. # FIXME: Similar issue as with "code.rst", sadly. *sigh*
.. # ************************************************************
.. # Beartype DOOR: The Decidedly Object-oriented Runtime-checker
.. # ************************************************************

*************
Beartype DOOR
*************

::

   DOOR: the Decidedly Object-Oriented Runtime-checker
   DOOR: it's capitalized, so it matters

Enter the **DOOR** (\ **D**\ ecidedly **O**\ bject-\ **o**\ riented **R**\
untime-checker): the first usable public Pythonic API for introspecting,
comparing, and type-checking type hints in :math:`O(1)` time with negligible
constants.

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

Procedural API
##############

Type-check *anything* at *any* time against *any* type hint. When the
:func:`isinstance` and :func:`issubclass` builtins fail to scale, prefer the
``beartype.door`` procedural API.

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

***************
Beartype Errors
***************

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

Likewise, beartype only emits beartype-specific warnings and disambiguous
warnings. Beartype is fastidious to a fault. Error handling is no...
*exception*. <sup>punny *or* funny? you decide.</sup>

Exception API
#############

Beartype raises fatal exceptions whenever something explodes. Most are
self-explanatory – but some assume prior knowledge of arcane type-hinting
standards *or* require non-trivial resolutions warranting further discussion.
This is their story.

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
    * User-defined functions and methods decorated by the @beartype.beartype_
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

Warning API
###########

Beartype emits non-fatal warnings whenever something looks it might explode in
your lap later... *but has yet to do so.* Since it is dangerous to go alone, let
beartype's words of anxiety-provoking wisdom be your guide. The codebase you
save might be your own.

PEP 585 Deprecations
********************

Beartype may occasionally emit non-fatal :pep:`585` deprecation warnings under
Python ≥ 3.9 resembling:

.. code-block::

   /home/kumamon/beartype/_util/hint/pep/utilpeptest.py:377:
   BeartypeDecorHintPep585DeprecationWarning: PEP 484 type hint
   typing.List[int] deprecated by PEP 585 scheduled for removal in the first
   Python version released after October 5th, 2025. To resolve this, import
   this hint from "beartype.typing" rather than "typing". See this discussion
   for further details and alternatives:
       https://github.com/beartype/beartype#pep-585-deprecations

This is that discussion topic. Let's dissect this like a mantis shrimp
repeatedly punching out giant kraken.

What Does This Mean?
====================

The :pep:`585` standard first introduced by Python 3.9.0 deprecated (obsoleted)
*most* of the :pep:`484` standard first introduced by Python 3.5.0 in the
official typing_ module. All deprecated type hints are slated to "be removed
from the typing_ module in the first Python version released 5 years after the
release of Python 3.9.0." Spoiler: Python 3.9.0 was released on October 5th,
2020. Altogether, this means that:

.. caution::

   **Most of the "typing" module will be removed in 2025 or 2026.**

If your codebase currently imports from the typing_ module, *most* of those
imports will break under an upcoming Python release. This is what beartype is
shouting about. Bad Changes™ are coming to dismantle your working code.

Are We on the Worst Timeline?
=============================

Season Eight of *Game of Thrones* previously answered this question, but let's
try again. You have three options to avert the looming disaster that threatens
to destroy everything you hold dear (in ascending order of justice):

#. **Import from** ``beartype.typing`` **instead.** The easiest (and best)
   solution is to globally replace all imports from the standard typing_ module
   with equivalent imports from our ``beartype.typing`` module. So:

   .. code-block:: python

      # Just do this...
      from beartype import typing

      # ...instead of this.
      #import typing

      # Likewise, just do this...
      from beartype.typing import Dict, FrozenSet, List, Set, Tuple, Type

      # ...instead of this.
      #from typing import Dict, FrozenSet, List, Set, Tuple, Type

   The public ``beartype.typing`` API is a mypy_-compliant replacement for the
   typing_ API offering improved forward compatibility with future Python
   releases. For example:

   * ``beartype.typing.Set is set`` under Python ≥ 3.9 for :pep:`585`
     compliance.
   * ``beartype.typing.Set is typing.Set`` under Python < 3.9 for :pep:`484`
     compliance.

#. **Drop Python < 3.9.** The next easiest (but worst) solution is to brutally
   drop support for Python < 3.9 by globally replacing all deprecated
   :pep:`484`\ -compliant type hints with equivalent :pep:`585`\ -compliant type
   hints (e.g., ``typing.List[int]`` with ``list[int]``). This is really only
   ideal for closed-source proprietary projects with a limited userbase. All
   other projects should prefer saner solutions outlined below.
#. **Hide warnings.** The reprehensible (but understandable) middle-finger
   way is to just squelch all deprecation warnings with an ignore warning
   filter targeting the
   ``BeartypeDecorHintPep585DeprecationWarning`` category. On the one hand,
   this will still fail in 2025 or 2026 with fiery explosions and thus only
   constitutes a temporary workaround at best. On the other hand, this has the
   obvious advantage of preserving Python < 3.9 support with minimal to no
   refactoring costs. The two ways to do this have differing tradeoffs
   depending on who you want to suffer most – your developers or your userbase:

   .. code-block:: python

      # Do it globally for everyone, whether they want you to or not!
      # This is the "Make Users Suffer" option.
      from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
      from warnings import filterwarnings
      filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)
      ...

      # Do it locally only for you! (Hope you like increasing your
      # indentation level in every single codebase module.)
      # This is the "Make Yourself Suffer" option.
      from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
      from warnings import catch_warnings, filterwarnings
      with catch_warnings():
          filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)
          ...

#. **Type aliases.** The hardest (but best) solution is to use `type aliases`_
   to conditionally annotate callables with either :pep:`484` *or* :pep:`585`
   type hints depending on the major version of the current Python interpreter.
   Since this is life, the hard way is also the best way – but also hard. Unlike
   the **drop Python < 3.9** approach, this approach preserves backward
   compatibility with Python < 3.9. Unlike the **hide warnings** approach, this
   approach also preserves forward compatibility with Python ≥ 3.14159265. `Type
   aliases`_ means defining a new private ``{your_package}._typing`` submodule
   resembling:

   .. code-block:: python

      # In "{your_package}._typing":
      from sys import version_info

      if version_info >= (3, 9):
          List = list
          Tuple = tuple
          ...
      else:
          from typing import List, Tuple, ...

   Then globally refactor all deprecated :pep:`484` imports from typing_ to
   ``{your_package}._typing`` instead:

   .. code-block:: python

      # Instead of this...
      from typing import List, Tuple

      # ...just do this.
      from {your_package}._typing import List, Tuple

   What could be simpler? :superscript:`...gagging noises faintly heard`
