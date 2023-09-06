.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document detailing the public-facing API of
.. # the @beartype.beartype decorator and associated data structures.

.. # ------------------( METADATA                            )------------------
.. # Fully-qualified name of the (sub)package described by this document,
.. # enabling this document to be externally referenced as :mod:`{name}`.
.. py:module:: beartype

.. # ------------------( MAIN                                )------------------

*******************
Beartype Decoration
*******************

.. code-block:: text

   wrap anything with runtime type-checking
       ...except that, of course.
          — Thus Spake Bearathustra, Book I

.. # FIXME: Revise all hard-code references to this decorator (e.g.,
.. # "``@beartype``", "``@beartype.beartype``) into actual beartype.beartype_
.. # interlinks, please.

The beating heart of beartype is the eponymous :func:`.beartype` decorator. This
is its story.

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

Beartype Decorator API
######################

.. py:decorator::
   beartype( \
       cls: type | None = None, \
       func: collections.abc.Callable | None = None, \
       conf: BeartypeConf = BeartypeConf(), \
   ) -> object

   :arg cls: Pure-Python class to be decorated.
   :type cls: type | None
   :arg func: Pure-Python function or method to be decorated.
   :type func: collections.abc.Callable | None
   :arg conf: Beartype configuration. Defaults to the default configuration
              performing :math:`O(1)` type-checking.
   :type conf: beartype.BeartypeConf
   :return: Passed class or callable wrapped with runtime type-checking.

   Augment the passed object with performant runtime type-checking. Unlike most
   decorators, ``@beartype`` has three orthogonal modes of operation:

   * `Class mode <class mode_>`__ – in which you decorate a class
     with ``@beartype``, which then iteratively decorates all methods declared
     by that class with ``@beartype``. This is the recommended mode for
     **object-oriented logic.**
   * `Callable mode <callable mode_>`__ – in which you decorate a
     function or method with ``@beartype``, which then dynamically generates a
     new function or method wrapping the original function or method with
     performant runtime type-checking. This is the recommended mode for
     **procedural logic.**
   * `Configuration mode <configuration mode_>`__ – in which you create your
     own app-specific ``@beartype`` decorator **configured** for your exact use
     case.

   When chaining multiple decorators, order of decoration is significant but
   conditionally depends on the mode of operation. Specifically, in:

   * `Class mode <class mode_>`__, ``@beartype`` should usually be listed
     *first*.
   * `Callable mode <callable mode_>`__,  ``@beartype`` should usually be listed
     *last*.

   It's not our fault. Surely documentation would never decieve you.

.. _callable mode:

Callable Mode
*************

*def* beartype.\ **beartype**\ (func: collections.abc.Callable_) ->
collections.abc.Callable_

In callable mode, :func:`.beartype` dynamically generates a new **callable**
(i.e., pure-Python function or method) runtime type-checking the passed
callable.

...as Decorator
===============

Because laziness prevails, :func:`.beartype` is *usually* invoked as a
decorator. Simply prefix the callable to be runtime type-checked with the line
``@beartype``. In this standard use pattern, :func:`.beartype` silently:

#. Replaces the decorated callable with a new callable of the same name and
   signature.
#. Preserves the original callable as the ``__wrapped__`` instance variable of
   that new callable.

An example explicates a thousand words.

.. code-block:: pycon

   # Import the requisite machinery.
   >>> from beartype import beartype

   # Decorate a function with @beartype.
   >>> @beartype
   ... def bother_free_is_no_bother_to_me(bothersome_string: str) -> str:
   ...     return f'Oh, bother. {bothersome_string}'

   # Call that function with runtime type-checking enabled.
   >>> bother_free_is_no_bother_to_me(b'Could you spare a small smackerel?')
   BeartypeCallHintParamViolation: @beartyped bother_free_is_no_bother_to_me()
   parameter bothersome_string=b'Could you spare a small smackerel?' violates
   type hint <class 'str'>, as bytes b'Could you spare a small smackerel?' not
   instance of str.

   # Call that function with runtime type-checking disabled. WHY YOU DO THIS!?
   >>> bother_free_is_no_bother_to_me.__wrapped__(
   ...     b'Could you spare a small smackerel?')
   "Oh, bother. b'Could you spare a small smackerel?'"

Because :func:`.beartype` preserves the original callable as ``__wrapped__``,
:func:`.beartype` seamlessly integrates with other well-behaved decorators that
respect that same pseudo-standard. This means that :func:`.beartype` can
*usually* be listed in any arbitrary order when chained (i.e., combined) with
other decorators.

Because this is the NP-hard timeline, however, assumptions are risky. If you
doubt anything, the safest approach is just to list ``@beartype`` as the
**last** (i.e., bottommost) decorator. This:

* Ensures that :func:`.beartype` is called first on the decorated callable
  *before* other decorators have a chance to really muck things up. Other
  decorators: *always the source of all your problems.*
* Improves both space and time efficiency. Unwrapping ``__wrapped__`` callables
  added by prior decorators is an :math:`O(k)` operation for :math:`k` the
  number of previously run decorators. Moreover, builtin decorators like
  :class:`classmethod`, :class:`property`, and :class:`staticmethod` create
  method descriptors; when run *after* a builtin decorator, :func:`.beartype`
  has no recourse but to:

  #. Destroy the original method descriptor created by that builtin decorator.
  #. Create a new method type-checking the original method.
  #. Create a new method descriptor wrapping that method by calling the same
     builtin decorator.

An example is brighter than a thousand Suns! :sup:`astronomers throwing
chalk here`

.. code-block:: pycon

   # Import the requisite machinery.
   >>> from beartype import beartype

   # Decorate class methods with @beartype in either order.
   >>> class BlastItAll(object):
   ...     @classmethod
   ...     @beartype  # <-- GOOD. this is the best of all possible worlds.
   ...     def good_idea(cls, we_will_dynamite: str) -> str:
   ...         return we_will_dynamite
   ...
   ...     @beartype  # <-- BAD. technically, fine. pragmatically, slower.
   ...     @classmethod
   ...     def save_time(cls, whats_the_charge: str) -> str:
   ...         return whats_the_charge

...as Function
==============

Because Python means not caring what anyone else thinks, :func:`.beartype` can
also be called as a function. This is useful in unthinkable edge cases like
monkey-patching *other* people's code with runtime type-checking. You usually
shouldn't do this, but you usually shouldn't do a lot of things that you do when
you're the sort of Pythonista that reads tortuous documentation like this.

.. code-block:: pycon

   # Import the requisite machinery.
   >>> from beartype import beartype

   # A function somebody else defined. Note the bad lack of @beartype.
   >>> def oh_bother_free_where_art_thou(botherfull_string: str) -> str:
   ...     return f'Oh, oh! Help and bother! {botherfull_string}'

   # Monkey-patch that function with runtime type-checking. *MUHAHAHA.*
   >>> oh_bother_free_where_art_thou = beartype(oh_bother_free_where_art_thou)

   # Call that function with runtime type-checking enabled.
   >>> oh_bother_free_where_art_thou(b"I'm stuck!")
   BeartypeCallHintParamViolation: @beartyped oh_bother_free_where_art_thou()
   parameter botherfull_string=b"I'm stuck!" violates type hint <class 'str'>,
   as bytes b"I'm stuck!" not instance of str.

One ``beartype()`` to monkey-patch them all and in the darkness type-check them.

.. _api_decor:noop:

...as Noop
==========

:func:`.beartype` silently reduces to a **noop** (i.e., scoops organic honey out
of a jar with its fat paws rather than doing something useful with its life)
under common edge cases. When *any* of the following apply, :func:`.beartype`
preserves the decorated callable or class as is by just returning that callable
or class unmodified (rather than augmenting that callable or class with unwanted
runtime type-checking):

* Beartype has been configured with the **no-time strategy**
  :attr:`.BeartypeStrategy.O0`: e.g.,

  .. code-block:: python

     # Import the requisite machinery.
     from beartype import beartype, BeartypeConf, BeartypeStrategy

     # Avoid type-checking *ANY* methods or attributes of this class.
     @beartype(conf=BeartypeConf(strategy=BeartypeStrategy.O0))
     class UncheckedDangerClassIsDangerous(object):
         # This method raises *NO* type-checking violation despite returning a
         # non-"None" value.
         def unchecked_danger_method_is_dangerous(self) -> None:
             return 'This string is not "None". Sadly, nobody cares anymore.'

* That callable or class has already been decorated by:

  * The :func:`.beartype` decorator itself.
  * The :pep:`484`\ -compliant :func:`typing.no_type_check` decorator: e.g.,

    .. code-block:: python

       # Import more requisite machinery. It is requisite.
       from beartype import beartype
       from typing import no_type_check

       # Avoid type-checking *ANY* methods or attributes of this class.
       @no_type_check
       class UncheckedRiskyClassRisksOurEntireHistoricalTimeline(object):
           # This method raises *NO* type-checking violation despite returning a
           # non-"None" value.
           def unchecked_risky_method_which_i_am_squinting_at(self) -> None:
               return 'This string is not "None". Why does nobody care? Why?'

* That callable is **unannotated** (i.e., *no* parameters or return values in
  the signature of that callable are annotated by type hints).
* Sphinx_ is currently autogenerating documentation (i.e., Sphinx's
  `"autodoc" extension <sphinx.ext.autodoc_>`__ is currently running).

Laziness **+** efficiency **==** :func:`.beartype`.

.. _class mode:

Class Mode
**********

*def* beartype.\ **beartype**\ (cls: type) -> type

In class mode, :func:`.beartype` dynamically replaces *each* method of the
passed pure-Python class with a new method runtime type-checking the original
method.

As with `callable mode <callable mode_>`__, simply prefix the class to be
runtime type-checked with the line ``@beartype``. In this standard use pattern,
:func:`.beartype` silently iterates over all instance, class, and static methods
declared by the decorated class and, for each such method:

#. Replaces that method with a new method of the same name and signature.
#. Preserves the original method as the ``__wrapped__`` instance variable of
   that new method.

...versus Callable Mode
=======================

Superficially, this is just syntactic sugar – but sometimes you gotta dip your
paws into the honey pot.

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype

   # Decorate a class with @beartype.
   @beartype
   class IAmABearOfNoBrainAtAll(object):
       def i_have_been_foolish(self) -> str:
           return 'A fly can't bird, but a bird can fly.'

       def and_deluded(self) -> str:
           return 'Ask me a riddle and I reply.'

   # ...or just decorate class methods directly with @beartype.
   # The class above is *EXACTLY* equivalent to the class below.
   class IAmABearOfNoBrainAtAll(object):
       @beartype
       def i_have_been_foolish(self) -> str:
           return 'A fly can't bird, but a bird can fly.'

       @beartype
       def and_deluded(self) -> str:
           return 'Ask me a riddle and I reply.'

Pragmatically, this is *not* just syntactic sugar. You *must* decorate classes
(rather than merely methods) with :func:`.beartype` to type-check the following:

* **Class-centric type hints** (i.e., type hints like the :pep:`673`\ -compliant
  typing.Self_ attribute that describe the decorated class itself). To
  type-check these kinds of type hints, :func:`.beartype` needs access to the
  class. :func:`.beartype` lacks access to the class when decorating methods
  directly. Instead, you *must* decorate classes by :func:`.beartype` for
  classes declaring one or more methods annotated by one or more class-centric
  type hints.
* **Dataclasses.** The standard :obj:`dataclasses.dataclass` decorator
  dynamically generates and adds new dunder methods (e.g., ``__init__()``,
  ``__eq__()``, ``__hash__()``) to the decorated class. These methods do *not*
  physically exist and thus *cannot* be decorated directly with
  :func:`.beartype`. Instead, you *must* decorate dataclasses first by
  ``@beartype`` and then by ``@dataclasses.dataclass``. Order is significant, of
  course. ``</sigh>``

When decorating classes, ``@beartype`` should *usually* be listed as the
**first** (i.e., topmost) decorator. This ensures that :func:`.beartype` is
called last on the decorated class *after* other decorators have a chance to
dynamically monkey-patch that class (e.g., by adding new methods to that class).
:func:`.beartype` will then type-check the monkey-patched functionality as well.

Come for the working examples. Stay for the wild hand-waving.

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype
   from dataclasses import dataclass

   # Decorate a dataclass first with @beartype and then with @dataclass. If you
   # accidentally reverse this order of decoration, methods added by @dataclass
   # like __init__() will *NOT* be type-checked by @beartype. (Blame Guido.)
   @beartype
   @dataclass
   class SoTheyWentOffTogether(object):
       a_little_boy_and_his_bear: str | bytes
       will_always_be_playing:    str | None = None

.. _configuration mode:

Configuration Mode
******************

*def* beartype.\ **beartype**\ (conf: beartype.BeartypeConf) ->
collections.abc.Callable[[T], T]

In configuration mode, :func:`.beartype` dynamically generates a new
:func:`.beartype` decorator – configured uniquely for your exact use case. You
too may cackle villainously as you feel the unbridled power of your keyboard.

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype, BeartypeConf, BeartypeStrategy

   # Dynamically create a new @monotowertype decorator configured to:
   # * Avoid outputting colors in type-checking violations.
   # * Enable support for the implicit numeric tower standardized by PEP 484.
   monotowertype = beartype(conf=BeartypeConf(
       is_color=False, is_pep484_tower=True))

   # Decorate with this decorator rather than @beartype everywhere.
   @monotowertype
   def muh_colorless_permissive_func(int_or_float: float) -> float:
       return int_or_float ** int_or_float ^ round(int_or_float)

Configuration: *because you know best*.

Beartype Configuration API
==========================

.. py:class::
   BeartypeConf( \
       *, \
       is_color: bool | None = None, \
       is_debug: bool = False, \
       is_pep484_tower: bool = False, \
       strategy: BeartypeStrategy = BeartypeStrategy.O1, \
   )

   **Beartype configuration** (i.e., self-caching dataclass instance
   encapsulating all flags, options, settings, and other metadata configuring
   each type-checking operation performed by beartype – including each
   decoration of a callable or class by the :func:`.beartype` decorator).

   The default configuration ``BeartypeConf()`` configures beartype to:

   * Perform :math:`O(1)` constant-time type-checking for safety, scalability,
     and efficiency.
   * Disable support for `PEP 484's implicit numeric tower <implicit numeric
     tower_>`__.
   * Disable developer-specific debugging logic.
   * Conditionally output color when standard output is attached to a terminal.

   Beartype configurations are immutable objects memoized (i.e., cached) on the
   unordered set of all passed parameters:

   .. code-block:: pycon

      >>> from beartype import BeartypeConf
      >>> BeartypeConf() is BeartypeConf()
      True
      >>> BeartypeConf(is_color=False) is BeartypeConf(is_color=False)
      True

   Beartype configurations are comparable under equality:

   .. code-block:: pycon

      >>> BeartypeConf(is_color=False) == BeartypeConf(is_color=True)
      False

   Beartype configurations are hashable and thus suitable for use as dictionary
   keys and set members:

   .. code-block:: pycon

      >>> BeartypeConf(is_color=False) == BeartypeConf(is_color=True)
      False
      >>> confs = {BeartypeConf(), BeartypeConf(is_color=False)}
      >>> BeartypeConf() in confs
      True

   Beartype configurations support meaningful :func:`repr` output:

   .. code-block:: pycon

      >>> repr(BeartypeConf())
      'BeartypeConf(is_color=None, is_debug=False, is_pep484_tower=False, strategy=<BeartypeStrategy.O1: 2>)'

   Beartype configurations expose read-only public properties of the same names
   as the above parameters:

   .. code-block:: pycon

      >>> BeartypeConf().is_color
      None
      >>> BeartypeConf().strategy
      <BeartypeStrategy.O1: 2>

   Keyword Parameters
   ------------------

   Beartype configurations support **optional read-only keyword-only**
   parameters at instantiation time. Most parameters are suitable for passing by
   *all* beartype users in *all* possible use cases. Some are only intended to
   be passed by *some* beartype users in *some* isolated use cases.

   This is their story.

   General Keyword Parameters
   ^^^^^^^^^^^^^^^^^^^^^^^^^^

   General-purpose configuration parameters are *always* safely passable:

   .. py:attribute:: is_debug

          ``Type:`` :class:`bool` = :data:`False`

      :data:`True` only if debugging the :func:`.beartype` decorator. If you're
      curious as to what exactly (if anything) :func:`.beartype` is doing on
      your behalf, temporarily enable this boolean. Specifically, enabling this
      boolean (*in no particular order*):

      * Caches the body of each type-checking wrapper function dynamically
        generated by :func:`.beartype` with the standard :mod:`linecache`
        module, enabling these function bodies to be introspected at runtime
        *and* improving the readability of tracebacks whose call stacks contain
        one or more calls to these :func:`.beartype`-decorated functions.
      * Prints the definition (including both the signature and body) of each
        type-checking wrapper function dynamically generated by :func:.beartype`
        to standard output.
      * Appends to the declaration of each **hidden parameter** (i.e., whose
        name is prefixed by ``"__beartype_"`` and whose value is that of an
        external attribute internally referenced in the body of that function)
        a comment providing the machine-readable representation of the initial
        value of that parameter, stripped of newlines and truncated to a
        hopefully sensible length. Since the low-level string munger called to
        do so is shockingly slow, these comments are conditionally embedded in
        type-checking wrapper functions *only* when this boolean is enabled.

      Defaults to :data:`False`. Eye-gouging sample output or it didn't happen,
      so:

      .. code-block:: pycon

         # Import the requisite machinery.
         >>> from beartype import beartype, BeartypeConf

         # Dynamically create a new @bugbeartype decorator enabling debugging.
         # Insider D&D jokes in my @beartype? You'd better believe. It's happening.
         >>> bugbeartype = beartype(conf=BeartypeConf(is_debug=True))

         # Decorate with this decorator rather than @beartype everywhere.
         >>> @bugbeartype
         ... def muh_bugged_func() -> str:
         ...     return b'Consistency is the bugbear that frightens little minds.'
         (line 0001) def muh_bugged_func(
         (line 0002)     *args,
         (line 0003)     __beartype_func=__beartype_func, # is <function muh_bugged_func at 0x7f52733bad40>
         (line 0004)     __beartype_conf=__beartype_conf, # is "BeartypeConf(is_color=None, is_debug=True, is_pep484_tower=False, strategy=<BeartypeStrategy...
         (line 0005)     __beartype_get_violation=__beartype_get_violation, # is <function get_beartype_violation at 0x7f5273081d80>
         (line 0006)     **kwargs
         (line 0007) ):
         (line 0008)     # Call this function with all passed parameters and localize the value
         (line 0009)     # returned from this call.
         (line 0010)     __beartype_pith_0 = __beartype_func(*args, **kwargs)
         (line 0011)
         (line 0012)     # Noop required to artificially increase indentation level. Note that
         (line 0013)     # CPython implicitly optimizes this conditional away. Isn't that nice?
         (line 0014)     if True:
         (line 0015)         # Type-check this passed parameter or return value against this
         (line 0016)         # PEP-compliant type hint.
         (line 0017)         if not isinstance(__beartype_pith_0, str):
         (line 0018)             raise __beartype_get_violation(
         (line 0019)                 func=__beartype_func,
         (line 0020)                 conf=__beartype_conf,
         (line 0021)                 pith_name='return',
         (line 0022)                 pith_value=__beartype_pith_0,
         (line 0023)             )
         (line 0024)
         (line 0025)     return __beartype_pith_0

   .. py:attribute:: is_pep484_tower

          ``Type:`` :class:`bool` = :data:`False`

      :data:`True` only if enabling support for `PEP 484's implicit numeric
      tower <implicit numeric tower_>`__ (i.e., lossy conversion of integers to
      floating-point numbers as well as both integers and floating-point numbers
      to complex numbers). Specifically, enabling this instructs beartype to
      automatically expand:

      * All :class:`float` type hints to :class:`float` ``|`` :class:`int`, thus
        implicitly accepting both integers and floating-point numbers for
        objects annotated as only accepting floating-point numbers.
      * All :class:`complex` type hints to :class:`complex` ``|`` :class:`float`
        ``|`` :class:`int`, thus implicitly accepting integers, floating-point,
        and complex numbers for objects annotated as only accepting complex
        numbers.

      Defaults to :data:`False` to minimize precision error introduced by lossy
      conversions from integers to floating-point numbers to complex numbers.
      Since most integers do *not* have exact representations as floating-point
      numbers, each conversion of an integer into a floating-point number
      typically introduces a small precision error that accumulates over
      multiple conversions and operations into a larger precision error.
      Enabling this improves the usability of public APIs at a cost of
      introducing precision errors.

      The standard use case is to dynamically define your own app-specific
      :func:`.beartype` decorator unconditionally enabling support for the
      implicit numeric tower, usually as a convenience to your userbase who do
      *not* particularly care about the above precision concerns. Behold the
      permissive powers of... ``@beartowertype``!

      .. code-block:: python

         # Import the requisite machinery.
         from beartype import beartype, BeartypeConf

         # Dynamically create a new @beartowertype decorator enabling the tower.
         beartowertype = beartype(conf=BeartypeConf(is_pep484_tower=True))

         # Decorate with this decorator rather than @beartype everywhere.
         @beartowertype
         def crunch_numbers(numbers: list[float]) -> float:
             return sum(numbers)

         # This is now fine.
         crunch_numbers([3, 1, 4, 1, 5, 9])

         # This is still fine, too.
         crunch_numbers([3.1, 4.1, 5.9])

      .. versionadded:: 0.12.0

   .. py:attribute:: strategy

          ``Type:`` :class:`.BeartypeStrategy` = :attr:`.BeartypeStrategy.O1`

      **Type-checking strategy** (i.e., :class:`.BeartypeStrategy` enumeration
      member dictating how many items are type-checked at each nesting level of
      each container and thus how responsively beartype type-checks containers).
      This setting governs the core tradeoff in runtime type-checking between:

      * **Overhead** in the amount of time that beartype spends type-checking.
      * **Completeness** in the number of objects that beartype type-checks.

      As beartype gracefully scales up to check larger and larger containers,
      so beartype simultaneously scales down to check fewer and fewer items of
      those containers. This scalability preserves performance regardless of
      container size while increasing the likelihood of false negatives (i.e.,
      failures to catch invalid items in large containers) as container size
      increases. You can either type-check a small number of objects nearly
      instantaneously *or* you can type-check a large number of objects slowly.
      Pick one.

      Defaults to :attr:`.BeartypeStrategy.O1`, the constant-time :math:`O(1)`
      strategy – maximizing scalability at a cost of also maximizing false
      positives.

   App-only Keyword Parameters
   ^^^^^^^^^^^^^^^^^^^^^^^^^^^

   **App-only configuration parameters** are passed *only* by first-party
   packages executed as apps, binaries, scripts, servers, or other executable
   processes (rather than imported as libraries, frameworks, or other importable
   APIs into the current process):

   .. py:attribute:: is_color

          ``Type:`` :class:`bool` | :data:`None` = :data:`None`

      Tri-state boolean governing how and whether beartype colours
      **type-checking violations** (i.e., human-readable
      :exc:`beartype.roar.BeartypeCallHintViolation` exceptions) with
      POSIX-compliant ANSI escape sequences for readability. Specifically, if
      this boolean is:

      * :data:`False`, beartype *never* colours type-checking violations raised
        by callables configured with this configuration.
      * :data:`True`, beartype *always* colours type-checking violations raised
        by callables configured with this configuration.
      * :data:`None`, beartype conditionally colours type-checking violations
        raised by callables configured with this configuration only when
        standard output is attached to an interactive terminal.

      The :ref:`${BEARTYPE_IS_COLOR} environment variable
      <api_decor:beartype_is_color>` globally overrides this parameter, enabling
      end users to enforce a global colour policy across their full app stack.
      When both that variable *and* this parameter are set to differing (and
      thus conflicting) values, the :class:`BeartypeConf` class:

      * Ignores this parameter in favour of that variable.
      * Emits a :class:`beartype.roar.BeartypeConfShellVarWarning` warning
        notifying callers of this conflict.

      To avoid this conflict, only downstream executables should pass this
      parameter; intermediary libraries should *never* pass this parameter.
      Non-violent communication begins with you.

      Effectively defaults to :data:`None`. Technically, this parameter defaults
      to a private magic constant *not* intended to be passed by callers,
      enabling :mod:`beartype` to reliably detect whether the caller has
      explicitly passed this parameter or not.

      The standard use case is to dynamically define your own app-specific
      :func:`.beartype` decorator unconditionally disabling colours in
      type-checking violations, usually due to one or more frameworks in your
      app stack failing to support ANSI escape sequences. Please file issues
      with those frameworks requesting ANSI support. In the meanwhile, behold
      the monochromatic powers of... ``@monobeartype``!

      .. code-block:: python

         # Import the requisite machinery.
         from beartype import beartype, BeartypeConf

         # Dynamically create a new @monobeartype decorator disabling colour.
         monobeartype = beartype(conf=BeartypeConf(is_color=False))

         # Decorate with this decorator rather than @beartype everywhere.
         @monobeartype
         def muh_colorless_func() -> str:
             return b'In the kingdom of the blind, you are now king.'

      .. versionadded:: 0.12.0

Beartype Strategy API
=====================

.. py:class:: BeartypeStrategy

       ``Superclass(es):`` :class:`enum.Enum`

   Enumeration of all kinds of **type-checking strategies** (i.e., competing
   procedures for type-checking objects passed to or returned from
   :func:`.beartype`-decorated callables, each with concomitant tradeoffs with
   respect to runtime complexity and quality assurance).

   Strategies are intentionally named according to `conventional Big O notation
   <Big O_>`__ (e.g., :attr:`.BeartypeStrategy.On` enables the :math:`O(n)`
   strategy). Strategies are established per-decoration at the fine-grained
   level of callables decorated by the :func:`.beartype` decorator. Simply set
   the :attr:`.BeartypeConf.strategy` parameter of the :class:`.BeartypeConf`
   object passed as the optional ``conf`` parameter to the :func:`.beartype`
   decorator.

   .. code-block:: python

      # Import the requisite machinery.
      from beartype import beartype, BeartypeConf, BeartypeStrategy

      # Dynamically create a new @slowmobeartype decorator enabling "full fat"
      # O(n) type-checking.
      slowmobeartype = beartype(conf=BeartypeConf(strategy=BeartypeStrategy.On))

      # Type-check all items of the passed list. Do this only when you pretend
      # to know in your guts that this list will *ALWAYS* be ignorably small.
      @bslowmobeartype
      def type_check_like_maple_syrup(liquid_gold: list[int]) -> str:
          return 'The slowest noop yet envisioned? You're not wrong.'

   Strategies enforce their corresponding runtime complexities (e.g.,
   :math:`O(n)`) across *all* type-checks performed for callables enabling those
   strategies. For example, a callable configured by the
   :attr:`.BeartypeStrategy.On` strategy will exhibit linear :math:`O(n)`
   complexity as its overhead for type-checking each nesting level of each
   container passed to and returned from that callable.

   This enumeration defines these members:

   .. py:attribute:: On

          ``Type:`` :class:`beartype.cave.EnumMemberType`

      **Linear-time strategy:** the :math:`O(n)` strategy, type-checking
      *all* items of a container.

      .. note::

         **This strategy is currently unimplemented.** Still, interested users
         are advised to opt-in to this strategy now; your code will then
         type-check as desired on the first beartype release supporting this
         strategy.

         Beartype: *We're here for you, fam.*

   .. py:attribute:: Ologn

          ``Type:`` :class:`beartype.cave.EnumMemberType`

      **Logarithmic-time strategy:** the :math:`O(\log n)` strategy,
      type-checking a randomly selected number of items ``log(len(obj))`` of
      each container ``obj``.

      .. note::

         **This strategy is currently unimplemented.** Still, interested users
         are advised to opt-in to this strategy now; your code will then
         type-check as desired on the first beartype release supporting this
         strategy.

         Beartype: *We're here for you, fam.*

   .. py:attribute:: O1

          ``Type:`` :class:`beartype.cave.EnumMemberType`

      **Constant-time strategy:** the default :math:`O(1)` strategy,
      type-checking a single randomly selected item of each container. As the
      default, this strategy need *not* be explicitly enabled.

   .. py:attribute:: O0

          ``Type:`` :class:`beartype.cave.EnumMemberType`

      **No-time strategy,** disabling type-checking for a decorated callable by
      reducing :func:`.beartype` to the identity decorator for that callable.
      This strategy is functionally equivalent to but more general-purpose than
      the standard :func:`typing.no_type_check` decorator; whereas
      :func:`typing.no_type_check` only applies to callables, this strategy
      applies to *any* context accepting a beartype configuration such as:

      * The :func:`.beartype` decorator decorating a class.
      * The :func:`beartype.door.is_bearable` function.
      * The :func:`beartype.door.die_if_unbearable` function.
      * The :meth:`beartype.door.TypeHint.is_bearable` method.
      * The :meth:`beartype.door.TypeHint.die_if_unbearable` method.

      Just like in real life, there exist valid use cases for doing absolutely
      nothing – including:

      * **Blacklisting callables.** While seemingly useless, this strategy
        allows callers to selectively prevent callables that would otherwise be
        type-checked (e.g., due to class decorations or import hooks) from
        being type-checked:

        .. code-block:: python

           # Import the requisite machinery.
           from beartype import beartype, BeartypeConf, BeartypeStrategy

           # Dynamically create a new @nobeartype decorator disabling type-checking.
           nobeartype = beartype(conf=BeartypeConf(strategy=BeartypeStrategy.O0))

           # Automatically decorate all methods of this class...
           @beartype
           class TypeCheckedClass(object):
               # Including this method, which raises a type-checking violation
               # due to returning a non-"None" value.
               def type_checked_method(self) -> None:
                   return 'This string is not "None". Apparently, that is a problem.'

               # Excluding this method, which raises *NO* type-checking
               # violation despite returning a non-"None" value.
               @nobeartype
               def non_type_checked_method(self) -> None:
                   return 'This string is not "None". Thankfully, no one cares.'

      * **Eliding overhead.** Beartype :ref:`already exhibits near-real-time
        overhead of less than 1µs (one microsecond, one millionth of a second)
        per call of type-checked callables <faq:realtime>`. When even that
        negligible overhead isn't negligible enough, brave callers considering
        an occupational change may globally disable *all* type-checking
        performed by beartype. Prepare your resume beforehand. Also, do so
        *only* under production builds intended for release; development builds
        intended for testing should preserve type-checking.

        Either:

        * `Pass Python the "-O" command-line option <-O_>`__, which beartype
          respects.
        * `Run Python under the "PYTHONOPTIMIZE" environment variable
          <PYTHONOPTIMIZE_>`__, which beartype also respects.
        * Define a new ``@maybebeartype`` decorator disabling type-checking when
          an app-specific constant ``I_AM_RELEASE_BUILD`` defined elsewhere is
          enabled:

          .. code-block:: python

             # Import the requisite machinery.
             from beartype import beartype, BeartypeConf, BeartypeStrategy

             # Let us pretend you know what you are doing for a hot moment.
             from your_app import I_AM_RELEASE_BUILD

             # Dynamically create a new @maybebeartype decorator disabling
             # type-checking when "I_AM_RELEASE_BUILD" is enabled.
             maybebeartype = beartype(conf=BeartypeConf(strategy=(
                 BeartypeStrategy.O0
                 if I_AM_RELEASE_BUILD else
                 BeartypeStrategy.O1
             ))

             # Decorate with this decorator rather than @beartype everywhere.
             @maybebeartype
             def muh_performance_critical_func(big_list: list[int]) -> int:
                 return sum(big_list)

Beartype Environment Variables
==============================

Beartype supports increasingly many **environment variables** (i.e., external
shell variables associated with the active Python interpreter). Most of these
variables globally override :class:`.BeartypeConf` parameters of similar names,
enabling end users to enforce global configuration policies across their full
app stacks.

Beneath environment variables... *thy humongous codebase shalt rise.*

.. _api_decor:beartype_is_color:

${BEARTYPE_IS_COLOR}
--------------------

The ``${BEARTYPE_IS_COLOR}`` environment variable globally overrides the
:attr:`.BeartypeConf.is_color` parameter, enabling end users to enforce a global
colour policy. As with that parameter, this variable is a tri-state boolean with
three possible string values:

* ``BEARTYPE_IS_COLOR='True'``, forcefully instantiating *all* beartype
  configurations across *all* Python processes with the ``is_color=True``
  parameter.
* ``BEARTYPE_IS_COLOR='False'``, forcefully instantiating *all* beartype
  configurations across *all* Python processes with the ``is_color=False``
  parameter.
* ``BEARTYPE_IS_COLOR='None'``, forcefully instantiating *all* beartype
  configurations across *all* Python processes with the ``is_color=None``
  parameter.

Force beartype to obey your unthinking hatred of the colour spectrum. You can't
be wrong!

.. code-block:: bash

   BEARTYPE_IS_COLOR=False python3 -m monochrome_retro_app.its_srsly_cool

.. versionadded:: 0.16.0
