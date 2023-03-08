.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document detailing the public-facing API of
.. # the "beartype.roar" subpackage.

.. # ------------------( METADATA                            )------------------
.. # Fully-qualified name of the (sub)package described by this document,
.. # enabling this document to be externally referenced as :mod:`{name}`.
.. py:module:: beartype.roar

.. # ------------------( MAIN                                )------------------

***************
Beartype Errors
***************

::

   ...is that bear growling or is it just me?
           — common last words in rural Canada

Beartype only raises:

* **Beartype-specific exceptions.** For your safety and ours, exceptions raised
  beartype are easily distinguished from exceptions raised by everybody else.
  *All* exceptions raised by beartype are instances of:

  * Public types importable from the :mod:`beartype.roar` subpackage.
  * The :exc:`beartype.roar.BeartypeException` abstract base class (ABC).

* **Disambiguous exceptions.** For your sanity and ours, *every* exception
  raised by beartype means one thing and one thing only. Beartype *never* reuses
  the same exception class to mean two different things – allowing you to
  trivially catch and handle the exact exception you're interested in.

Likewise, beartype only emits beartype-specific warnings and disambiguous
warnings. Beartype is fastidious to a fault. Error handling is no...
*exception*. :sup:`punny *or* funny? you decide.`

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

Exception API
#############

Beartype raises fatal exceptions whenever something explodes. Most are
self-explanatory – but some assume prior knowledge of arcane type-hinting
standards *or* require non-trivial resolutions warranting further discussion.

When that happens, don't be the guy that ignores this chapter.

.. py:exception:: BeartypeException

       ``Superclass(es):`` :exc:`Exception`

   **Beartype exception root superclass.** *All* exceptions raised by beartype
   are guaranteed to be instances of concrete subclasses of this abstract base
   class (ABC) whose class names strictly match either:

   * ``Beartype{subclass_name}Violation`` for type-checking violations
     (e.g., ``BeartypeCallHintReturnViolation``).
   * ``Beartype{subclass_name}Exception`` for non-type-checking violations
     (e.g., ``BeartypeDecorHintPep3119Exception``).

.. py:exception:: BeartypeDecorException

       ``Superclass(es):`` :exc:`.BeartypeException`

   **Beartype decorator exception superclass.** *All* exceptions raised by
   the ``@beartype`` decorator at decoration time (i.e., while dynamically
   generating type-checking wrappers for decorated callables and classes) are
   guaranteed to be instances of concrete subclasses of this abstract base
   class (ABC). Since decoration-time exceptions are typically raised from
   module scope early in the lifetime of a Python process, you are unlikely to
   manually catch and handle decorator exceptions.

   A detailed list of subclasses of this ABC is quite inconsequential. Very
   well. `@leycec`_ admits he was too tired to type it all out. `@leycec`_ also
   admits he played exploitative video games all night instead... *again*.
   `@leycec`_ is grateful nobody reads these API notes. :sup:`checkmate,
   readthedocs.`

.. py:exception:: BeartypeCallException

       ``Superclass(es):`` :exc:`.BeartypeException`

   **Beartype call-time exception superclass.** Beartype type-checkers
   (including :func:`beartype.door.die_if_unbearable` and
   :func:`beartype.beartype`-decorated callables) raise instances of concrete
   subclasses of this abstract base class (ABC) at call-time – typically when
   failing a type-check.

   *All* exceptions raised by beartype type-checkers are guaranteed to be
   instances of this ABC. Since type-checking exceptions are typically raised
   from function and method scopes later in the lifetime of a Python process,
   you are *much* more likely to manually catch and handle instances of this
   exception type than other types of beartype exceptions. This includes the
   pivotal :exc:`.BeartypeCallHintViolation` type, which subclasses this type.

   In fact, you're encouraged to do so. Repeat after Kermode Bear:

       "Exceptions are fun, everybody."

   *Gotta catch 'em all!*

.. py:exception:: BeartypeCallHintException

       ``Superclass(es):`` :exc:`.BeartypeCallException`

   **Beartype type-checking exception superclass.** Beartype type-checkers
   (including :func:`beartype.door.die_if_unbearable` and
   :func:`beartype.beartype`-decorated callables) raise instances of concrete
   subclasses of this abstract base class (ABC) when failing a type-check at
   call time – typically due to you passing a parameter or returning a value
   violating a type hint annotating that parameter or return.

   For once, we're not the ones to blame. The relief in our cubicle is palpable.

.. py:exception:: BeartypeCallHintForwardRefException

       ``Superclass(es):`` :exc:`.BeartypeCallHintException`

   **Beartype type-checking forward reference exception.** Beartype
   type-checkers raise instances of this exception type when a **forward
   reference type hint** (i.e., string referring to a class that has yet to be
   defined) erroneously references either:

   * An attribute that does *not* exist.
   * An attribute that exists but whose value is *not* actually a class.

   As we gaze forward in time, so too do we glimpse ourselves – unshaven and
   shabbily dressed – in the rear-view mirror.

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

.. py:exception:: BeartypeCallHintViolation

       ``Superclass(es):`` :exc:`.BeartypeCallHintException`

    **Beartype type-checking violation.** This is the most important beartype
    exception you never hope to see – and thus the beartype exception you are
    most likely to see. When your code explodes at midnight, instances of this
    exception class were lighting the fuse behind your back.

    Beartype type-checkers raise an instance of this exception class when an
    object to be type-checked violates the type hint annotating that object.
    Beartype type-checkers include:

    * The :func:`beartype.door.die_if_unbearable` function.
    * The :meth:`beartype.door.TypeHint.die_if_unbearable` method.
    * User-defined functions and methods decorated by the
      :func:`beartype.beartype` decorator, which then themselves become beartype
      type-checkers.

    Because type-checking violations are why we are all here, instances of this
    exception class offer additional read-only public properties to assist you
    in debugging. Inspect these properties at runtime to resolve any lingering
    doubts about which coworker(s) you intend to blame in your next twenty Git
    commits:

    .. py:attribute:: culprits

           ``Type:`` :class:`tuple`\ [:class:`object`\ , ...]

       Tuple of one or more **culprits** (i.e., irresponsible objects that
       violated the type hints annotating those objects during a recent
       type-check).

       Specifically, this property returns either:

       * If a standard slow Python container (e.g., :class:`dict`,
         :class:`list`, :class:`set`, :class:`tuple`) is responsible for this
         violation, the 2-tuple ``(root_culprit, leaf_culprit)`` where:

         * ``root_culprit`` is the outermost such container. This is usually the
           passed parameter or returned value indirectly violating this type
           hint.
         * ``leaf_culprit`` is the innermost item nested in ``root_culprit``
           directly violating this type hint.

       * If a non-container (e.g., scalar, class instance) is responsible for
         this violation, the 1-tuple ``(culprit,)`` where ``culprit`` is that
         non-container.

       Let us examine what the latter means for your plucky intern who will do
       this after fetching more pumpkin spice lattes for The Team™ (currently
       engrossed in a critical morale-building "Best of 260" Atari 2600 *Pong*
       competition):

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
       two edge cases beyond our control, this property falls back to listing
       truncated snapshots of the machine-readable representations of those
       culprits (e.g., the first 10,000 characters or so of their :func:`repr`
       strings). This safe fallback is triggered for each culprit that:

       * Has **already been garbage-collected.** To avoid memory leaks, this
         property only weakly (rather than strongly) refers to these culprits
         and is thus best accessed only where these culprits are accessible.
         Technically, this property is safely accessible from any context.
         Practically, this property is most usefully accessed from the
         ``except ...:`` block directly catching this violation. Since these
         culprits may be garbage-collected at any time thereafter, this property
         *cannot* be guaranteed to refer to these culprits outside that block.
         If this property is accessed from any other context and one or more of
         these culprits have sadly passed away, this property dynamically
         reduces the corresponding items of this tuple to only the
         machine-readable representations of those culprits. [#the-haunting]_
       * Is a **builtin variable-sized C-based object** (e.g., :class:`dict`,
         :class:`int`, :class:`list`, :class:`str`). Long-standing limitations
         within CPython itself prevent beartype from weakly referring to those
         objects. Openly riot on the `CPython bug tracker`_ if this displeases
         you as much as it does us.

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
          SPIRIT_BEAR_DO_AS_HE_PLEASE = [
              [b'Why do you sleep in my pinball room, Spirit Bear?']]

          # Call this callable with this invalid container.
          try:
              we_are_all_spirit_bear(SPIRIT_BEAR_DO_AS_HE_PLEASE)
          # Shoddy magic happens here. Catch violations and try (but fail) to
          # inspect the original culprits, because they were containers!
          except BeartypeCallHintViolation as violation:
              # Assert that two culprits were responsible for this violation.
              assert len(violation.culprits) == 2

              # Root and leaf culprits. We just made these words up, people.
              root_culprit = violation.culprits[0]
              leaf_culprit = violation.culprits[1]

              # Assert that these culprits are, in fact, just repr() strings.
              assert root_culprit == repr(SPIRIT_BEAR_DO_AS_HE_PLEASE)
              assert leaf_culprit == repr(SPIRIT_BEAR_DO_AS_HE_PLEASE[0][0])

       We see that beartype correctly identified the root culprit as the passed
       list of lists of byte-strings (rather than strings) *and* the leaf
       culprit as that byte-string. We also see that beartype only returned the
       :func:`repr` of both culprits rather than those culprits. Why? Because
       CPython prohibits weak references to both lists *and* byte-strings.

       This is why we facepalm ourselves in the morning. We did it this morning.
       We'll do it next morning, too. Until the :mod:`weakref` module improves,
       `@leycec`_'s forehead *will* be swollen with an angry mass of unsightly
       red welts that are now festering unbeknownst to his wife.

       .. versionadded:: 0.12.0
       .. [#the-haunting]
          This exception stores the representations of these culprits inside
          itself when first raised. Like a gruesome time capsule, they return to
          haunt you.

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

::

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
official :mod:`typing` module. All deprecated type hints are slated to "be
removed from the :mod:`typing` module in the first Python version released 5
years after the release of Python 3.9.0." Spoiler: Python 3.9.0 was released on
October 5th, 2020. Altogether, this means that:

.. caution::

   **Most of the "typing" module will be removed in 2025 or 2026.**

If your codebase currently imports from the :mod:`typing` module, *most* of
those imports will break under an upcoming Python release. This is what beartype
is shouting about. Bad changes are coming to dismantle your working code.

Are We on the Worst Timeline?
=============================

Season Eight of *Game of Thrones* previously answered this question, but let's
try again. You have three options to avert the looming disaster that threatens
to destroy everything you hold dear (in ascending order of justice):

#. **Import from** :mod:`beartype.typing` **instead.** The easiest (and best)
   solution is to globally replace all imports from the standard :mod:`typing`
   module with equivalent imports from our :mod:`beartype.typing` module. So:

   .. code-block:: python

      # If you prefer attribute imports, just do this...
      from beartype.typing import Dict, FrozenSet, List, Set, Tuple, Type

      # ...instead of this.
      #from typing import Dict, FrozenSet, List, Set, Tuple, Type

      # Or if you prefer module imports, just do this...
      from beartype import typing

      # ...instead of this.
      #import typing

   The public :mod:`beartype.typing` API is a mypy_-compliant replacement for
   the :mod:`typing` API offering improved forward compatibility with future
   Python releases. For example:

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
   :class:`.BeartypeDecorHintPep585DeprecationWarning` category. On the one
   hand, this will still fail in 2025 or 2026 with fiery explosions and thus
   only constitutes a temporary workaround at best. On the other hand, this has
   the obvious advantage of preserving Python < 3.9 support with minimal to no
   refactoring costs. The two ways to do this have differing tradeoffs depending
   on who you want to suffer most – your developers or your userbase:

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

   Then globally refactor all deprecated :pep:`484` imports from :mod:`typing`
   to ``{your_package}._typing`` instead:

   .. code-block:: python

      # Instead of this...
      from typing import List, Tuple

      # ...just do this.
      from {your_package}._typing import List, Tuple

   What could be simpler? :sup:`...gagging noises faintly heard`
