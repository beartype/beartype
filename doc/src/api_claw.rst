.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document detailing the public-facing API of
.. # the "beartype.claw" subpackage, governing import hooks.

.. # ------------------( METADATA                            )------------------
.. # Fully-qualified name of the (sub)package described by this document,
.. # enabling this document to be externally referenced as :mod:`{name}`.
.. py:module:: beartype.claw

.. # ------------------( MAIN                                )------------------

.. _api_claw:api_claw:

*********************
Beartype Import Hooks
*********************

**Beartype import hooks** enforce type hints across your entire app in two lines
of code with *no* runtime overhead. Do it for the new guy sobbing quietly in his
cubicle. This is beartype import hooks in ten seconds. :superscript:`dyslexia
notwithstanding`

.. code-block:: python

   # Add *ONE* of the following semantically equivalent two-liners to the very
   # top of your "{your_package}.__init__" submodule. Start with *THE FAST WAY*.

   # ....................{ THE FAST WAY                    }....................
   from beartype.claw import beartype_this_package  # <-- this is boring, but...
   beartype_this_package()                          # <-- the fast way

   # ....................{ THE LESS FAST WAY               }....................
   from beartype.claw import beartype_package       # <-- still boring, but...
   beartype_package('{your_package}')               # <-- the less fast way

   # ....................{ THE MORE SLOW WAY               }....................
   from beartype.claw import beartype_packages      # <-- boring intensifies
   beartype_packages(('{your_package}',))           # <-- the more slow way

   # ....................{ THE WAY OF THE BEAR NINJA       }....................
   from beartype.claw import beartyping             # <-- getting weird here
   with beartyping():                               # <-- weird context manager
       from {your_package} import {your_thing}      # <-- import some stuff
       from {some_package} import {some_thing}      # <-- import more stuff

Beartype import hooks extend the surprisingly sharp claws of :mod:`beartype` to
your full stack, whether any other devs wanted you to do that or not. Claw your
way to the top of the bug heap and then sit on that heap with a smug expression.

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

Import Hooks Overview
#####################

Beartype import hooks implicitly perform both:

* Standard **runtime type-checking** (ala the :func:`beartype.beartype`
  decorator).
* Standard **static type-checking** (ala mypy_ and pyright_) but **at runtime**
  – which ain't standard.

Automate the :func:`beartype.beartype` decorator away today with magical import
hooks published by the :mod:`beartype.claw` subpackage! When you install import
hooks from beartype, you augment beartype from a :ref:`pure-runtime
second-generation type-checker <faq:third>` to a :ref:`hybrid runtime-static
third-generation type-checker <faq:hybrid>` – instantaneously.

That's right. Beartype is now a tentacular cyberpunk horror like that mutant
brain baby from Katsuhiro Otomo's dystopian 80's masterpiece *Akira*. You can't
look away!

Import Hooks Overview, Part Deux
################################

Beartype import hooks is a hobbit hole so deep we had to deescalate it with
decrepit manga panels from *Akira*. Prepare to enter that hole.

Let's begin by outlining exactly what :func:`.beartype_this_package` does. As
the simplest and most convenient of several import hooks published by the
:mod:`beartype.claw` subpackage, the :func:`.beartype_this_package` import hook
subjects *all* subsequently imported submodules of ``{your_package}`` to
runtime type-checking based on "high-tech" :mod:`beartype`... tech.

Notably, :func:`.beartype_this_package`:

* Implicitly decorates *all* callables and classes by the
  :func:`beartype.beartype` decorator. Rejoice, fellow mammals! You no longer
  need to explicitly decorate anything by :func:`beartype.beartype` ever again.
  Of course, you *can* if you want to – but there's no compelling reason to do
  so and many compelling reasons *not* to do so. You have probably just thought
  of five, but there are even more.
* Implicitly appends *every* :pep:`526`\ -compliant annotated variable
  assignment (e.g., ``muh_int: int = 'Pretty sure this isn't an integer, but
  not sure.'``) by a new statement at the same indentation level calling the
  :func:`beartype.door.die_if_unbearable` function passed both that variable and
  that type hint. Never do that manually. Now, you never do.

For example, :func:`.beartype_this_package` silently transforms your
``{your_package}.{buggy_submodule}`` which currently lacks runtime type-checking
from this quietly broken code you insist you never knew about, you swear:

.. code-block:: python

   import typing as t

   bad_global: int = 'My eyes! The goggles do nothing.'

   def bad_function() -> str:
       return b"I could've been somebody, instead of a bum byte string."

   class BadClass(object):
       def bad_method(self) -> t.NoReturn:
           return 'Nobody puts BadClass in the corner.'

...into this loudly broken code even your DevOps can no longer ignore:

.. code-block:: python

   from beartype import beartype
   from beartype.door import die_if_unbearable
   import typing as t

   bad_global: int = 'My eyes! The goggles do nothing.'
   die_if_unbearable(bad_global, int)

   @beartype
   def bad_function() -> str:
       return b"I could've been somebody, instead of a bum byte string."

   @beartype
   class BadClass(object):
       def bad_method(self) -> t.NoReturn:
           return 'Nobody puts BadClass in the corner.'

By doing nothing, you saved five lines of extraneous boilerplate you no longer
need to maintain, preserved `DRY (Don't Repeat Yourself) <DRY_>`__, and mended
your coworker's career, who you would have blamed for all this. You had nothing
to do with that code! It's a nothingburger!

Beartype believes you. This is why we :func:`.beartype_this_package`.

Import Hooks API
################

Beartype import hooks come in two flavours:

* :ref:`Permanent import hooks <api_claw:permanent>` (i.e., side-effect-laden
  import hooks whose effects permanently apply to *all* subsequently imported
  packages and modules).
* :ref:`Idempotent import hooks <api_claw:idempotent>` (i.e., side-effect-free
  import hooks whose effects are isolated to a specific block of code).

.. _api_claw:permanent:

Permanent Import Hooks
**********************

.. py:function::
   beartype_this_package( \
       *, conf: beartype.BeartypeConf = beartype.BeartypeConf()) -> None

   :arg conf: Beartype configuration. Defaults to the default configuration
              performing :math:`O(1)` type-checking.
   :type conf: beartype.BeartypeConf
   :raise beartype.roar.BeartypeClawHookException: If either:

                                                   * This function is *not*
                                                     called from a module (i.e.,
                                                     this function is called
                                                     directly from within a
                                                     read–eval–print loop
                                                     (REPL)).
                                                   * ``conf`` is *not* a
                                                     beartype configuration.

   **Self-package runtime-static type-checking import hook.**

   This hook type-checks *all* annotated callables, classes, and variable
   assignments in *all* submodules of the **current package** (i.e., the
   caller-defined package directly calling this function), configured by the
   passed beartype configuration.

   .. code-block:: python

      from beartype import BeartypeConf                # <-- boilerplate
      from beartype.claw import beartype_this_package  # <-- boilerplate: the revenge
      beartype_this_package(conf=BeartypeConf(is_color=False))  # <-- you hate rainbows

   This hook isolates its bug-hunting action to the current package. This is
   what everyone wants to try first, because this is the safest course of
   action. Other hooks permissively type-check third-party packages outside your
   control, which have probably *never* been tested against beartype and are
   thus likely to raise type-checking violations; ``git blame`` has things to
   say about that. This hook restrictively type-checks only your first-party
   package under your control, which *has* been tested against beartype. It has,
   hasn't it? You're not making us look bad here, are you? If this hook fails,
   there is no hope for your package. Even though it might be beartype's fault,
   beartype will still blame you for its mistakes.

   This hook is typically called as the first statement in the ``__init__``
   submodule of some caller-defined (sub)package. If this hook is called from:

   * Your top-level ``{your_package}.__init__`` submodule, then this hook
     type-checks your entire package – including *all* submodules and
     subpackages of your package.
   * Some mid-level ``{your_package}.{your_subpackage}.__init__`` submodule,
     then this hook type-checks only that subpackage – including *all*
     submodules and subsubpackages of that subpackage.

   As the term "import hook" implies, this hook only applies to subsequent
   imports performed *after* this hook; previously imported submodules and
   subpackages remain unaffected.

.. _api_claw:idempotent:

Idempotent Import Hooks
***********************

.. # FIXME: Revise signature up, please.
.. # .. py:function::
.. #    beartyping( \
.. #        *, \
.. #        conf: beartype.BeartypeConf = beartype.BeartypeConf(), \
.. #    ) -> None

Import Hook Configuration
#########################

Beartype import hooks accept an optional keyword-only ``conf`` parameter whose
value is a **beartype configuration** (i.e., :class:`beartype.BeartypeConf`
instance), defaulting to the default beartype configuration ``BeartypeConf()``.
Unsurprisingly, that configuration configures the behaviour of its hook: e.g.,

.. code-block:: python

   # In your "{your_package}.__init__" submodule, enable @beartype's support for
   # the PEP 484-compliant implicit numeric tower (i.e., expand "int" to "int |
   # float" and "complex" to "int | float | complex"):
   from beartype import BeartypeConf           # <-- it all seems so familiar
   from beartype.claw import beartype_package  # <-- boil it up, boilerplate
   beartype_package('your_package', conf=BeartypeConf(is_pep484_tower=True))  # <-- *UGH.*


Equally unsurprisingly, :class:`beartype.BeartypeConf` has been equipped with
import hook-aware super powers. Fine-tune the behaviour of our import hooks for
your exact needs, including:

.. # FIXME: Document these options in "api_decor" as well, please. *sigh*

* ``BeartypeConf(claw_is_pep526: bool = True)``. By default,
  :mod:`beartype.claw` type-checks annotated variable assignments like
  ``muh_int: int = 'Pretty sure this isn't an integer.'``. Although this is
  *usually* what everyone wants, this may not be what someone suspicious wearing
  aviator goggles, a red velvet cape, and too-tight black leather wants. Nobody
  knows what those people want. If you are such a person, consider disabling
  this option to reduce type safety and destroy your code like Neo-Tokyo vs.
  Mecha-Baby-Godzilla: :superscript:`...who will win!?!?`

  .. code--block:: python

     # In your "{your_package}.__init__" submodule, disable PEP 526 support out
     # of spite. You cackle disturbingly as you do. Sanity crumbles. Python shrugs.
     from beartype import BeartypeConf            # <-- boiling boilerplate...
     from beartype.claw import beartype_packages  # <-- ...boils plates, what?
     beartype_packages(
         ('your.subpackage', 'your.submodule'),   # <-- pretend this makes sense
         conf=BeartypeConf(claw_is_pep526=False)  # <-- *GAH!*
     )

* ``BeartypeConf(warning_cls_on_decorator_exception: Optional[Type[Warning]] =
  None)``. By default, :mod:`beartype.claw` emits non-fatal warnings rather than
  fatal exceptions raised by the :func:`beartype.beartype` decorator at
  decoration time. This is *usually* what everyone wants, because
  :func:`beartype.beartype` currently fails to support all possible edge cases
  and is thus likely to raise at least one exception while decorating your
  entire package. To improve the resilience of :mod:`beartype.claw` against
  those edge cases, :func:`beartype.beartype` emits one warning for each
  decoration exception and then simply continues to the next decoratable
  callable or class. This is occasionally unhelpful. What if you really *do*
  want :mod:`beartype.claw` to raise a fatal exception on the first such edge
  case in your codebase – perhaps because you want to either see the full
  exception traceback *or* punish your coworkers who are violating typing
  standards by trying to use an imported module as a type hint?
  :superscript:`...this actually happened` In this case, consider:

  * Passing :data:`None` as the value of this parameter. Doing so forces
    :mod:`beartype.claw` to act strictly, inflexibly, and angrily. Expect
    spittle-flecked mouth frothing and claws all over the place:

  .. code-block:: python

     # In your "{your_package}.__init__" submodule, raise exceptions because you
     # hate worky. The CI pipeline you break over your knee may just be your own.
     from beartype import BeartypeConf                # <-- boiling boilerplate...
     from beartype.claw import beartype_this_package  # <-- ...ain't even lukewarm
     beartype_this_package(conf=BeartypeConf(warning_cls_on_decorator_exception=None))  # <-- *ohboy*
