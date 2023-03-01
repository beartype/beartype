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
:mod:`beartype.door` procedural API.

.. _beartype.door.die_if_unbearable:
.. _die_if_unbearable:

*def* beartype.door.\ **die_if_unbearable**\ (obj: object, hint: object, \*,
conf: beartype.BeartypeConf = beartype.BeartypeConf()) -> None

    **Type-hint exception raiser,** either:

    * Raising a **typing-checking violation** (i.e., human-readable
      :exc:`beartype.roar.BeartypeCallHintViolation` exception) if the passed
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

.. _beartype.door.is_bearable:
.. _is_bearable:

*def* beartype.door.\ **is_bearable**\ (obj: object, hint: object, \*, conf:
beartype.BeartypeConf = beartype.BeartypeConf()) -> bool

    **Type-hint tester,** returning either:

    * :data:`True` if the passed arbitrary object ``obj`` satisfies the passed
      PEP-compliant type hint ``hint`` under the passed beartype configuration
      ``conf``.
    * :data:`False` otherwise.

    .. code-block:: pycon

       >>> from beartype.door import is_bearable
       >>> from beartype.typing import List, Sequence, Optional, Union
       >>> is_bearable("Kif, I’m feeling the ‘Captain's itch.’", Optional[str])
       True
       >>> is_bearable('I hate these filthy Neutrals, Kif.', Sequence[str])
       True
       >>> is_bearable('Stop exploding, you cowards.', Union[List[bool], None])
       False

    This tester is a strict superset of the :func:`isinstance` builtin and can
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

    This tester is also a *spiritual* superset of the :func:`issubclass` builtin
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

.. _is_subhint:

*def* beartype.door.\ **is_subhint**\ (subhint: object, superhint: object) ->
bool

    **Subhint tester,** returning either:

    * :data:`True` if the first passed PEP-compliant type hint is a **subhint**
      of the second passed PEP-compliant type hint, in which case the second
      hint is a **superhint** of the first hint.
    * :data:`False` otherwise.

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

    Equivalently, this tester returns :data:`True` only if *all* of the
    following conditions apply:

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
      * In `incomprehensible set theoretic jargon <set theory_>`__, the size of
        the countably infinite set of all possible objects matched by the first
        hint is **less than or equal to** that of those matched by the second
        hint.

    This tester supports a wide variety of practical use cases – including:

    * **Multiple dispatch.** A pure-Python decorator can implement `multiple
      dispatch`_ over multiple overloaded implementations of the same callable
      by calling this function. An overload of the currently called callable can
      be dispatched to if the types of the passed parameters are all
      **subhints** of the type hints annotating that overload.
    * Formal verification of **API compatibility** across version bumps.
      Automated tooling like linters, continuous integration (CI), ``git``
      hooks, and integrated development environments (IDEs) can raise
      pre-release alerts prior to accidental publication of API breakage by
      calling this function. A Python API preserves backward compatibility if
      each type hint annotating each public class or callable of the current
      version of that API is a **superhint** of the type hint annotating the
      same class or callable of the prior release of that API.

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
classes. When the standard :mod:`typing` module has you scraping your
fingernails on the nearest whiteboard in chicken scratch, prefer the
:mod:`beartype.door` object-oriented API.

You've already seen that type hints do *not* define a usable public Pythonic
API. This was by design. Type hints were *never* intended to be used at runtime.
But that's a bad design. Runtime is all that matters, ultimately. If the app
doesn't run, it's broke – regardless of what the static type-checker says. Now,
beartype breaks a trail through the spiny gorse of unusable PEP standards.

Open the locked cathedral of type hints with :mod:`beartype.door`: your QA
crowbar that legally pries apart all type hints. Cry havoc, the bears of API
war!

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

:class:`.TypeHint` wrappers:

* Are **immutable**, **hashable**, and safely usable both as dictionary keys and
  in sets.
* Support efficient **lookup** of child type hints – just like **dictionaries**
  and **sets**.
* Support efficient **iteration** over and **random access** of child type hints
  – just like **lists** and **tuples**.
* Are **partially ordered** over the set of all type hints (according to the
  :func:`subhint relation <.is_subhint>`) and safely usable in any algorithm
  accepting a partial ordering (e.g., `topological sort`_).
* Guarantee similar performance as :func:`beartype.beartype` itself. All
  :class:`.TypeHint` methods and properties run in (possibly `amortized
  <amortized analysis_>`__) **constant time** with negligible constants.

:mod:`beartype.door`: never leave :mod:`typing` without it.
