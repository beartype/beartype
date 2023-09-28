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

   # In your "{your_package}.__init__" submodule in a codebase far, far away...
   from beartype.claw import beartype_this_package  # <-- boilerplate for victory
   beartype_this_package()                          # <-- yay! your team just won

**That's it.** That's beartype import hooks in ten seconds.
:superscript:`dyslexia notwithstanding` As the simplest of several import hooks
published by the :mod:`beartype.claw` subpackage, the
:func:`.beartype_this_package` function:

* Implicitly decorates *all* callables and classes in ``{your_package}`` by the
  :func:`beartype.beartype` decorator. Rejoice, fellow mammals! You no longer
  need to explicitly decorate anything by :func:`beartype.beartype` ever again.
  Of course, you *can* if you want to – but there's no compelling reason to do
  so and many compelling reasons *not* to do so. You have probably just thought
  of five, but there are even more.
* Implicitly subjects *all* :pep:`526`\ -compliant annotated variable
  assignments (e.g., ``muh_int: int = 'Pretty sure this isn't an integer, but
  not sure.'``) to runtime type-checking performed by the
  :func:`beartype.door.die_if_unbearable` function. More below.

The :mod:`beartype.claw` rabbit hole goes deep. Prepare to enter that hole.

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
.. py:function::
   beartyping( \
       *, \
       conf: beartype.BeartypeConf = beartype.BeartypeConf(), \
   ) -> None
