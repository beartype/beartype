.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2025 Beartype authors.
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
of code with *no* runtime overhead. This is beartype import hooks in ten
seconds. :superscript:`dyslexia notwithstanding`

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

.. #FIXME: Uncomment *AFTER* we actually build out a reasonable first iteration
.. #of our local import hook API. *sigh*
.. #   # ....................{ THE WAY OF THE BEAR NINJA       }....................
.. #   from beartype.claw import beartyping             # <-- getting weird here
.. #   with beartyping():                               # <-- weird context manager
.. #       from {your_package} import {your_thing}      # <-- import some stuff
.. #       from {some_package} import {some_thing}      # <-- import more stuff

Beartype import hooks extend the surprisingly sharp claws of :mod:`beartype` to
your full app stack, whether anyone else wanted you to do that or not. Claw your
way to the top of the bug heap; then sit on that heap with a smug expression. Do
it for the new guy sobbing quietly in his cubicle.

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear with Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

Import Hooks Overview
#####################

Beartype import hooks implicitly perform both:

* Standard **runtime type-checking** (ala the :func:`beartype.beartype`
  decorator).
* Standard **static type-checking** (ala mypy_ and pyright_) but **at runtime**
  – and that ain't standard.

Automate the :func:`beartype.beartype` decorator away today with magical import
hooks published by the :mod:`beartype.claw` subpackage. When you install import
hooks from beartype, you augment beartype from a :ref:`pure-runtime
second-generation type-checker <faq:third>` into a :ref:`hybrid runtime-static
third-generation type-checker <faq:hybrid>`. That's right.

Beartype is now a tentacular cyberpunk horror like that mutant brain baby from
Katsuhiro Otomo's dystopian 80's masterpiece *Akira*. You can't look away!

.. image:: https://user-images.githubusercontent.com/217028/272775190-8996c4a2-b320-4ca1-ba83-5c4dd36e6165.png
   :width: 300
   :alt: mutant brain baby

:superscript:`May Neo-Tokyo have mercy on your codebase's soul.`

Import Hooks Overview, Part Deux
################################

Beartype import hooks is a hobbit hole so deep we had to deescalate it with
decrepit manga panels from *Akira*. Prepare to enter that hole.

What Is beartype_this_package()?
********************************

Let's begin by outlining exactly **what** :func:`.beartype_this_package` does.

As the simplest and most convenient of several import hooks published by the
:mod:`beartype.claw` subpackage, :func:`.beartype_this_package` type-checks
*all* subsequently imported submodules of ``{your_package}``. Notably,
:func:`.beartype_this_package`:

* Implicitly decorates *all* callables and classes across ``{your_package}`` by
  the :func:`beartype.beartype` decorator. Rejoice, fellow mammals! You no
  longer need to explicitly decorate anything by :func:`beartype.beartype` ever
  again. Of course, you *can* if you want to – but there's no compelling reason
  to do so and many compelling reasons *not* to do so. You have probably just
  thought of five, but there are even more.
* Implicitly appends *every* :pep:`526`\ -compliant annotated variable
  assignment (e.g., ``muh_int: int = 'Pretty sure this isn't an integer, but
  not sure.'``) across ``{your_package}`` by a new statement at the same
  indentation level calling the :func:`beartype.door.die_if_unbearable` function
  passed both that variable and that type hint. Never do that manually. Now, you
  never do.

Examples or we're lying again. :func:`.beartype_this_package` transforms your
``{your_package}.{buggy_submodule}`` from this quietly broken code that you
insist you never knew about, you swear:

.. code-block:: python

   # This is "{your_package}.{buggy_submodule}". It is bad, but you never knew.
   import typing as t

   bad_global: int = 'My eyes! The goggles do nothing.'  # <-- no exception

   def bad_function() -> str:
       return b"I could've been somebody, instead of a bum byte string."
   bad_function()  # <-- no exception

   class BadClass(object):
       def bad_method(self) -> t.NoReturn:
           return 'Nobody puts BadClass in the corner.'
   BadClass().bad_method()  # <-- no exception

...into this loudly broken code that even your unionized QA team can no longer
ignore:

.. code-block:: python

   # This is "{your_package}.{buggy_submodule}" on beartype_this_package().
   # Any questions? Actually, that was rhetorical. No questions, please.
   from beartype import beartype
   from beartype.door import die_if_unbearable
   import typing as t

   bad_global: int = 'My eyes! The goggles do nothing.'
   die_if_unbearable(bad_global, int)  # <-- raises exception

   @beartype
   def bad_function() -> str:
       return b"I could've been somebody, instead of a bum byte string."
   bad_function()  # <-- raises exception

   @beartype
   class BadClass(object):
       def bad_method(self) -> t.NoReturn:
           return 'Nobody puts BadClass in the corner.'
   BadClass().bad_method()  # <-- raises exception

By doing nothing, you saved five lines of extraneous boilerplate you no longer
need to maintain, preserved `DRY (Don't Repeat Yourself) <DRY_>`__, and mended
your coworker's career, who you would have blamed for all this. You had nothing
to do with that code. It's a nothingburger!

Beartype believes you. This is why we :func:`.beartype_this_package`.

.. image:: https://user-images.githubusercontent.com/217028/272775040-9bf81c0b-3994-4420-a1d5-ac5835f0a0b2.png
   :alt: looks kinda bad

:superscript:`This is what happens when we don't beartype_this_package().`

Why Is beartype_this_package()?
*******************************

Let's continue by justifying **why** you want to use
:func:`.beartype_this_package`. Don't worry. The "why?" is easier than the
"what?". It often is. The answer is: "Safety is my middle name."
:superscript:`<-- more lies`

:func:`.beartype_this_package` isolates its bug-hunting action to the current
package. This is what everyone wants to try first. Type-checking only *your*
first-party package under *your* control is the safest course of action, because
you rigorously stress-tested your package with beartype. You did, didn't you?
You're not making us look bad here? Don't make us look bad. We already have
GitHub and Reddit for that.

Other beartype import hooks – like :func:`.beartype_packages` or
:func:`.beartyping` – can be (mis)used to dangerously type-check *other*
third-party packages outside your control that have probably never been
stress-tested with beartype. Those packages could raise type-checking violations
at runtime that you have no control over. If they don't now, they could later.
Forward compatibility is out the window. ``git blame`` has things to say about
that.

If :func:`.beartype_this_package` fails, there is no hope for your package. Even
though it might be beartype's fault, beartype will still blame you for its
mistakes.

Import Hooks API
################

Beartype import hooks come in two flavours:

* :ref:`Global import hooks <api_claw:global>`, whose effects encompass *all*
  subsequently imported packages and modules matching various patterns.
* :ref:`Local import hooks <api_claw:local>`, whose effects are isolated to only
  specific packages and modules imported inside specific blocks of code. Any
  subsequently imported packages and modules remain unaffected.

.. _api_claw:global:

Global Import Hooks
*******************

Global beartype import hooks are... well, *global*. Their claws extend to a
horizontal slice of your full stack. These hooks globally type-check *all*
annotated callables, classes, and variable assignments in *all* subsequently
imported packages and modules matching various patterns.

With great globality comes great responsibility.

.. py:function::
   beartype_this_package(*, conf: beartype.BeartypeConf = beartype.BeartypeConf()) -> None

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

   **Self-package runtime-static type-checking import hook.** This hook accepts
   *no* package or module names, instead type-checking *all* annotated
   callables, classes, and variable assignments across *all* submodules of the
   **current package** (i.e., the caller-defined package directly calling this
   function).

   This hook only applies to subsequent imports performed *after* this hook, as
   the term "import hook" implies; previously imported submodules and
   subpackages remain unaffected.

   This hook is typically called as the first statement in the ``__init__``
   submodule of whichever (sub)package you would like to type-check. If you
   call this hook from:

   * Your top-level ``{your_package}.__init__`` submodule, this hook type-checks
     your entire package. This includes *all* submodules and subpackages across
     your entire package.
   * Some mid-level ``{your_package}.{your_subpackage}.__init__`` submodule,
     this hook type-checks only that subpackage. This includes *only* submodules
     and subsubpackages of that subpackage. All other submodules and subpackages
     of your package remain unaffected (i.e., will *not* be type-checked).

   .. code-block:: python

      # At the top of your "{your_package}.__init__" submodule:
      from beartype import BeartypeConf                # <-- boilerplate
      from beartype.claw import beartype_this_package  # <-- boilerplate: the revenge
      beartype_this_package(conf=BeartypeConf(is_color=False))  # <-- no color is best color

   This hook is effectively syntactic sugar for the following idiomatic
   one-liners that are so cumbersome, fragile, and unreadable that no one should
   even be reading this:

   .. code-block:: python

      beartype_this_package()                            # <-- this...
      beartype_package(__name__.rpartition('.')[0])      # <-- ...is equivalent to this...
      beartype_packages((__name__.rpartition('.')[0],))  # <-- ...is equivalent to this.

   When in doubt, have no doubt. Just call :func:`.beartype_this_package`.

   .. versionadded:: 0.15.0
   .. image:: https://user-images.githubusercontent.com/217028/272775398-761b9f11-95c2-4410-ad56-fd1ebe99bf04.png
      :alt: fierce determined face

   :superscript:`beartype_this_package(): It do be like that.`

.. py:function::
   beartype_package( \
       package_name: str, \
       *, \
       conf: beartype.BeartypeConf = beartype.BeartypeConf() \
   ) -> None

   :arg package_name: Absolute name of the package or module to be type-checked.
   :type package_name: str
   :arg conf: Beartype configuration. Defaults to the default configuration
              performing :math:`O(1)` type-checking.
   :type conf: beartype.BeartypeConf
   :raise beartype.roar.BeartypeClawHookException: If either:

                                                   * ``conf`` is *not* a
                                                     beartype configuration.
                                                   * ``package_name`` is either:

                                                     * *Not* a string.
                                                     * The empty string.
                                                     * A non-empty string that
                                                       is *not* a valid
                                                       **package or module
                                                       name** (i.e.,
                                                       ``"."``-delimited
                                                       concatenation of valid
                                                       Python identifiers).

   **Uni-package runtime-static type-checking import hook.** This hook accepts
   only a single package or single module name, type-checking *all* annotated
   callables, classes, and variable assignments across either:

   * If the passed name is that of a (sub)package, *all* submodules of that
     (sub)package.
   * If the passed name is that of a (sub)module, *only* that (sub)module.

   This hook should be called *before* that package or module is imported; when
   erroneously called *after* that package or module is imported, this hook
   silently reduces to a noop (i.e., does nothing regardless of how many times
   you squint at it suspiciously).

   This hook is typically called as the first statement in the ``__init__``
   submodule of your top-level ``{your_package}.__init__`` submodule.

   .. code-block:: python

      # At the top of your "{your_package}.__init__" submodule:
      from beartype import BeartypeConf           # <-- <Ctrl-c> <Ctrl-v>
      from beartype.claw import beartype_package  # <-- <Ctrl-c> <Ctrl-v> x 2
      beartype_package('your_package', conf=BeartypeConf(is_debug=True))
                      # ^-- they said explicit is better than implicit,
                      #     but all i got was this t-shirt and a hicky.

   Of course, that's fairly worthless. Just call :func:`.beartype_this_package`,
   right? But what if you want to type-check just *one* subpackage or submodule
   of your package rather than your *entire* package? In that case,
   :func:`.beartype_this_package` is overbearing. :superscript:`badum ching`
   Enter :func:`.beartype_package`, the outer limits of QA where you control the
   horizontal and the vertical:

   .. code-block:: python

      # Just because you can do something, means you should do something.
      beartype_package('good_package.m.A.A.d_submodule')  # <-- fine-grained precision strike

   :func:`.beartype_package` shows it true worth, however, in type-checking
   *other* people's code. Because the :mod:`beartype.claw` API is a permissive
   Sarlacc pit, :func:`.beartype_package` happily accepts the absolute name of
   *any* package or module – whether they wanted you to do that or not:

   .. code-block:: python

      # Whenever you want to break something over your knee, never leave your
      # favorite IDE [read: Vim] without beartype_package().
      beartype_package('somebody_elses_package')  # <-- blow it up like you just don't care

   This hook is effectively syntactic sugar for passing the
   :func:`.beartype_packages` function a 1-tuple containing only this package or
   module name.

   .. code-block:: python

      beartype_package('your_package')      # <-- this...
      beartype_packages(('your_package',))  # <-- ...is equivalent to this.

   Pretend you didn't see that. Just call :func:`.beartype_package`.

   .. versionadded:: 0.15.0
   .. image:: https://user-images.githubusercontent.com/217028/272775461-e5f62d59-9fe9-49e8-9904-47a1326d8695.png
      :alt: wizened psychic baby lady

   :superscript:`Truer words were never spoken, wizened psychic baby lady.`

.. py:function::
   beartype_packages( \
       package_names: collections.abc.Iterable[str], \
       *, \
       conf: beartype.BeartypeConf = beartype.BeartypeConf() \
   ) -> None

   :arg package_name: Iterable of the absolute names of one or more packages or
                      modules to be type-checked.
   :type package_name: collections.abc.Iterable[str]
   :arg conf: Beartype configuration. Defaults to the default configuration
              performing :math:`O(1)` type-checking.
   :type conf: beartype.BeartypeConf
   :raise beartype.roar.BeartypeClawHookException: If either:

                                                   * ``conf`` is *not* a
                                                     beartype configuration.
                                                   * ``package_names`` is
                                                     either:

                                                     * *Not* an iterable.
                                                     * The empty iterable.
                                                     * A non-empty iterable
                                                       containing at least one
                                                       item that is either:

                                                       * *Not* a string.
                                                       * The empty string.
                                                       * A non-empty string that
                                                         is *not* a valid
                                                         **package or module
                                                         name** (i.e.,
                                                         ``"."``-delimited
                                                         concatenation of valid
                                                         Python identifiers).

   **Multi-package runtime-static type-checking import hook.** This hook accepts
   one or more package and module names in any arbitrary order (i.e., order is
   insignificant), type-checking *all* annotated callables, classes, and
   variable assignments across:

   * For each passed name that is a (sub)package, *all* submodules of that
     (sub)package.
   * For each passed name that is a (sub)module, *only* that (sub)module.

   This hook should be called *before* those packages and modules are imported;
   when erroneously called *after* those packages and modules are imported, this
   hook silently reduces to a noop. Squinting still does nothing.

   This hook is typically called as the first statement in the ``__init__``
   submodule of your top-level ``{your_package}.__init__`` submodule.

   .. code-block:: python

      # At the top of your "{your_package}.__init__" submodule:
      from beartype import BeartypeConf            # <-- copy-pasta
      from beartype.claw import beartype_packages  # <-- copy-pasta intensifies
      beartype_packages((
          'your_package',
          'some_package.published_by.the_rogue_ai.Johnny_Twobits',  # <-- seems trustworthy
          'numpy',  # <-- ...heh. no one knows what will happen here!
          'scipy',  # <-- ...but we can guess, can't we? *sigh*
      ), conf=BeartypeConf(is_pep484_tower=True))  # <-- so. u 2 h8 precision.

   This hook is the penultimate force in :ref:`global import hooks
   <api_claw:global>`. The terser :func:`.beartype_this_package` and
   :func:`.beartype_package` hooks are effectively syntactic sugar for this
   verboser hook.

       One hook to QA them all, and in the darkness of your codebase bind them.

   .. versionadded:: 0.15.0
   .. image:: https://user-images.githubusercontent.com/217028/272775529-42b85874-56b7-40b4-b9d8-19b603df1657.png
      :width: 256
      :alt: it's the end of the road as we know it, and i feel fine

   :superscript:`It’s almost as if we know what “penultimate” means.`

.. py:function::
   beartype_all(*, conf: beartype.BeartypeConf = beartype.BeartypeConf()) -> None

   :arg conf: Beartype configuration. Defaults to the default configuration
              performing :math:`O(1)` type-checking.
   :type conf: beartype.BeartypeConf
   :raise beartype.roar.BeartypeClawHookException: If ``conf`` is *not* a
                                                   beartype configuration.

   **All-packages runtime-static type-checking import hook.** This hook accepts
   *no* package or module names, instead type-checking *all* callables, classes,
   and variable assignments across *all* submodules of *all* packages.

   This hook should be called *before* those packages and modules are imported;
   when erroneously called *after* those packages and modules are imported, this
   hook silently reduces to a noop. Not even squinting can help you now.

   This hook is typically called as the first statement in the ``__init__``
   submodule of your top-level ``{your_package}.__init__`` submodule.

   .. code-block:: python

      # At the top of your "{your_package}.__init__" submodule,
      from beartype import BeartypeConf       # <-- @beartype seemed so innocent, once
      from beartype.claw import beartype_all  # <-- where did it all go wrong?
      beartype_all(conf=BeartypeConf(claw_is_pep526=False))  # <-- U WILL BE ASSIMILATE

   This hook is the ultimate import hook, spasmodically unleashing a wave of
   bug-defenestrating action over **the entire Python ecosystem.** After calling
   this hook, *any* package or module authored by *anybody* (including packages
   and modules in CPython's standard library) will be subject to the iron claw
   of :mod:`beartype.claw`. Its rule is law!

   This hook is the runtime equivalent of a full-blown :ref:`pure-static
   <faq:third>` type-checker like mypy_ or pyright_, enabling full-stack_
   :ref:`runtime-static <faq:hybrid>` type-checking over your entire app. This
   includes submodules defined by both:

   * First-party proprietary packages authored explicitly for this app.
   * Third-party open-source packages authored and maintained elsewhere.

   Nothing is isolated. Everything is permanent. Do not trust this hook.

   Caveat Emptor: Empty Promises Not Even a Cat Would Eat
   ------------------------------------------------------
   This hook imposes type-checking on *all* downstream packages importing your
   package, which may not necessarily want, expect, or tolerate type-checking.
   This hook is *not* intended to be called from intermediary APIs, libraries,
   frameworks, or other middleware. Packages imported by other packages should
   *not* call this hook. This hook is *only* intended to be called from
   full-stack_ end-user applications as a convenient alternative to manually
   passing the names of all packages to be type-checked to the more granular
   :func:`.beartype_packages` hook.

   This hook is the extreme QA nuclear option. Because this hook is the extreme
   QA nuclear option, **most codebases should not call this hook.**

   :mod:`beartype` cannot be held responsible for a sudden rupture in the
   plenæne of normalcy, the space-time continuum, or your once-stable job. Pour
   one out for those who are about to vitriolically explode their own code.

      Nuke Python from orbit. Because now you can.

   .. versionadded:: 0.15.0
   .. image:: https://github.com/beartype/beartype-assets/assets/217028/cf43dca7-1852-4fec-bcbc-6d4aeca23230
      :width: 400
      :alt: quiet, safe life

   :superscript:`The beartype_all() lifestyle. Short but sweet.`

.. _api_claw:local:

.. #FIXME: Uncomment *AFTER* we actually build out a reasonable first iteration
.. #of our local import hook API. *sigh*
.. Local Import Hooks
.. ******************

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
