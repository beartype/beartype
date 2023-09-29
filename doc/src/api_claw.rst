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
cubicle.

.. code-block:: python

   # Add *ONE* of the following semantically equivalent two-liners to the very
   # top of your "{your_package}.__init__" submodule. Start with the fast way.

   # ....................{ THE FAST WAY                    }....................
   from beartype.claw import beartype_this_package  # <-- this is boring
   beartype_this_package()                          # <-- the fast way

   # ....................{ THE LESS FAST WAY               }....................
   from beartype.claw import beartype_package       # <-- still boring
   beartype_package('{your_package}')               # <-- the less fast way

   # ....................{ THE MORE SLOW WAY               }....................
   from beartype.claw import beartype_packages      # <-- boring intensifies
   beartype_packages(('{your_package}',))           # <-- the more slow way

   # ....................{ THE WAY OF THE BEAR NINJA       }....................
   from beartype.claw import beartyping             # <-- getting weird here
   with beartyping():                               # <-- weird context manager
       from {your_package} import {your_thing}      # <-- import some stuff
       from {some_package} import {some_thing}      # <-- import more stuff

**That's it.** That's beartype import hooks in ten seconds.
:superscript:`dyslexia notwithstanding`

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

Claw your way to the top of the bug heap threatening to drown your codebase in a
deluge of chittering carapaces, masticating mandibles, and probing probosci. The
bugginess you feel may be real, but so is the bug-mugging power of beartype.

Import Hooks Overview, Part Deux
################################

Beartype import hooks is a hobbit hole that goes deeper than any Baggins ever
envisioned. Prepare to enter that hole.

Let's begin by outlining exactly what :func:`.beartype_this_package` does. As
the simplest and most convenient of several import hooks published by the
:mod:`beartype.claw` subpackage, the :func:`.beartype_this_package` import hook
subjects *all* subsequently imported submodules of ``{your_package}`` to
runtime type-checking based on purportedly high-tech :mod:`beartype` tech.

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
  that type hint.

For example, :func:`.beartype_this_package` silently transforms your
``{your_package}.buggy_submodule`` submodule that lacks runtime type-checking
from this broken code you pretend you never about:

.. code-block:: python

   import typing as t

   bad_global: int = 'My eyes! The goggles do nothing.'

   def bad_function() -> str:
       return b"I could've been somebody, instead of a bum byte string."

   class BadClass(object):
       def bad_method(self) -> t.NoReturn:
           return 'Nobody puts BadClass in the corner.'

...into this broken code you can no longer ignore:

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
need to maintain, preserved `DRY (Don't Repeat Yourself) <DRY_>`__, and saved
your coworker's career. You had nothing to do with that code!

This is why we :func:`.beartype_this_package`.

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

.. _api_claw:idempotent:

Idempotent Import Hooks
***********************

.. # FIXME: Revise signature up, please.
.. # .. py:function::
.. #    beartyping( \
.. #        *, \
.. #        conf: beartype.BeartypeConf = beartype.BeartypeConf(), \
.. #    ) -> None
