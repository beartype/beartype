.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document detailing all public-facing APIs
.. # exposed by this project.

.. # ------------------( MAIN                                )------------------

###
API
###

Beartype isn't just the ``@beartype.beartype`` decorator.

Beartype is a menagerie of public APIs for type-checking, introspecting, and
manipulating type hints at runtime – all accessible under the ``beartype``
package installed when you installed beartype. But all beartype documentation
begins with ``@beartype.beartype``, just like all rivers run to the sea.
:superscript:`False! Do endorheic basins mean nothing to you!?`

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Project-wide tables of contents (TOCs). See also official documentation on
.. # the Sphinx-specific "toctree::" directive:
.. #     https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree

.. #FIXME: Uncomment as needed, please.
.. # Child TOC tree.
.. # .. toctree::
.. #    :hidden:
.. #    :caption: Bear with Us
.. #
.. #    Bearpedia <self>
.. #    Install <install>

.. #FIXME: Uncomment *AFTER* re-enabling "autoapi" support in "conf.py" and
.. #resolving outstanding issues with that support. *gulp*
.. # .. toctree::
.. #    :caption: Beartype API reference
.. #
.. #    API </api/beartype/index>
.. #
.. # Would You Like to Know More?
.. # ----------------------------
.. #
.. # * :ref:`genindex`
.. # * :ref:`modindex`
.. # * :ref:`search`

.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

*******************
Beartype Decoration
*******************

.. _@beartype.beartype:

.. # FIXME: Revise all hard-code references to this decorator (e.g.,
.. # "``@beartype``", "``@beartype.beartype``) into actual beartype.beartype_
.. # interlinks, please.

The beating heart of beartype is the eponymous ``@beartype.beartype`` decorator.
This is its story.

Unlike most decorators, ``@beartype.beartype`` has three modes of operation:

* `Callable mode <beartype.beartype func_>`__, in which you decorate a function
  or method with ``@beartype``, which then dynamically generates a new function
  or method wrapping the original function or method with runtime type-checking.
* `Class mode <beartype.beartype type_>`__, in which you decorate a class with
  ``@beartype``, which then decorates all methods declared by that class with
  ``@beartype``.
* `Configuration mode <beartype.beartype conf_>`__, in which you create your own
  app-specific ``@beartype`` decorator – **configured** for your exact use case.

Callable Mode
#############

.. _beartype.beartype func:

*def* beartype.\ **beartype**\ (func: collections.abc.Callable_) ->
collections.abc.Callable_

In callable mode, ``@beartype`` dynamically generates a new **callable** (i.e.,
pure-Python function or method) runtime type-checking the passed callable.

...as Decorator
***************

Because laziness prevails, ``@beartype`` is *usually* invoked as a decorator.
Simply prefix the callable to be runtime type-checked with the line
``@beartype``. In this standard use pattern, ``@beartype`` silently:

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

Because ``@beartype`` preserves the original callable as ``__wrapped__``,
``@beartype`` seamlessly integrates with other well-behaved decorators that
respect that same pseudo-standard. This means that ``@beartype`` can *usually*
be listed in any arbitrary order when chained (i.e., combined) with other
decorators.

Because this is the NP-hard timeline, however, assumptions are risky. If you
doubt anything, the safest approach is just to list ``@beartype`` as the
**last** (i.e., bottommost) decorator. This:

* Ensures that ``@beartype`` is called first on the decorated callable *before*
  other decorators have a chance to really muck things up. Other decorators:
  *always the source of all your problems.*
* Improves both space and time efficiency. Unwrapping ``__wrapped__`` callables
  added by prior decorators is an ``O(k)`` operation for ``k`` the number of
  previously run decorators. Moreover, builtin decorators like ``@classmethod``,
  ``@property``, and ``@staticmethod`` create method descriptors; when run
  *after* a builtin decorator, ``@beartype`` has no recourse but to:

  #. Destroy the original method descriptor created by that builtin decorator.
  #. Create a new method type-checking the original method.
  #. Create a new method descriptor wrapping that method by calling the same
     builtin decorator.

An example is brighter than a thousand Suns! :superscript:`astronomers throwing
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
**************

Because Python means not caring what anyone else thinks, ``@beartype`` can also
be called as a function. This is useful in unthinkable edge cases like
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

...as Noop
**********

``@beartype`` silently reduces to a noop under common edge cases. When *any* of
the following apply, ``@beartype`` preserves the decorated callable as is by
just returning that callable unmodified:

* That callable is **unannotated** (i.e., *no* parameters or return values in
  the signature of that callable are annotated by type hints).
* That callable has already been decorated by ``@@beartype``.
* That callable has already been decorated by the :pep:`484`\ -compliant
  @typing.no_type_check_ decorator.
* Beartype has been configured with the **no-time strategy** (i.e.,
  _BeartypeStrategy.O0).
* Sphinx_ is currently autogenerating documentation (i.e., Sphinx's
  `"autodoc" extension <sphinx.ext.autodoc_>`__ is currently running).

Laziness **+** efficiency **==** ``@beartype``.

Class Mode
##########

.. _beartype.beartype type:

*def* beartype.\ **beartype**\ (cls: type) -> type

In class mode, ``@beartype`` dynamically replaces *each* method of the passed
pure-Python class with a new method runtime type-checking the original method.

As with `callable mode <Callable Mode_>`__, simply prefix the class to be
runtime type-checked with the line ``@beartype``. In this standard use pattern,
``@beartype`` silently iterates over all instance, class, and static methods
declared by the decorated class and, for each such method:

#. Replaces that method with a new method of the same name and signature.
#. Preserves the original method as the ``__wrapped__`` instance variable of
   that new method.

...versus Callable Mode
***********************

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
(rather than merely methods) with ``@beartype`` to type-check the following:

* **Class-centric type hints** (i.e., type hints like the :pep:`673`\ -compliant
  typing.Self_ attribute that describe the decorated class itself). To
  type-check these kinds of type hints, ``@beartype`` needs access to the class.
  ``@beartype`` lacks access to the class when decorating methods directly.
  Instead, you *must* decorate classes by ``@beartype`` for classes declaring
  one or more methods annotated by one or more class-centric type hints.
* **Dataclasses.** The standard dataclasses.dataclass_ decorator dynamically
  generates and adds new dunder methods (e.g., ``__init__()``, ``__eq__()``,
  ``__hash__()``) to the decorated class. These methods do *not* physically
  exist and thus *cannot* be decorated directly with ``@beartype``. Instead, you
  *must* decorate dataclasses first by ``@beartype`` and then by
  ``@dataclasses.dataclass``. Order is significant, of course. ``</sigh>``

When decorating classes, ``@beartype`` should *usually* be listed as the
**first** (i.e., topmost) decorator. This ensures that ``@beartype`` is called
last on the decorated class *after* other decorators have a chance to
dynamically monkey-patch that class (e.g., by adding new methods to that class).
``@beartype`` will then type-check the monkey-patched functionality as well.

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

Configuration Mode
##################

.. _beartype.beartype conf:

*def* beartype.\ **beartype**\ (conf: beartype.BeartypeConf_) ->
collections.abc.Callable[[T], T]

In configuration mode, ``@beartype`` dynamically generates a new ``@beartype``
decorator configured for your special needs. You too shall cackle villainously
as you feel the growing power of your keyboard.

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

BeartypeConf
************

.. _beartype.BeartypeConf:

| *class* beartype.\ **BeartypeConf**\ (
| |_| |_| |_| |_| \*,
| |_| |_| |_| |_| `is_color <BeartypeConf.is_color_>`__: Optional[bool] = None,
| |_| |_| |_| |_| `is_debug <BeartypeConf.is_debug_>`__: bool = False,
| |_| |_| |_| |_| `is_pep484_tower <BeartypeConf.is_pep484_tower_>`__: bool = False,
| |_| |_| |_| |_| `strategy <BeartypeConf.strategy_>`__: BeartypeStrategy_ = BeartypeStrategy.O1_,
| )

    **Beartype configuration** (i.e., self-caching dataclass instance
    encapsulating all flags, options, settings, and other metadata configuring
    each type-checking operation performed by beartype – including each
    decoration of a callable or class by the ``@beartype.beartype`` decorator).

    The default configuration ``BeartypeConf()`` configures beartype to:

    * Conditionally output color when standard output is attached to a terminal.
    * Disable developer-specific debugging logic.
    * Disable support for `PEP 484's implicit numeric tower <implicit numeric
      tower_>`__.
    * Perform ``O(1)`` constant-time type-checking for safety, scalability, and
      efficiency.

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

    Beartype configurations support meaningful ``repr()`` output:

    .. code-block:: pycon

       >>> repr(BeartypeConf())
       'BeartypeConf(is_color=None, is_debug=False, is_pep484_tower=False, strategy=<BeartypeStrategy.O1: 2>)'

    Beartype configurations expose read-only public properties of the same
    names as the above parameters:

    .. code-block:: pycon

       >>> BeartypeConf().is_color
       None
       >>> BeartypeConf().strategy
       <BeartypeStrategy.O1: 2>

    Beartype configurations support these optional keyword-only parameters at
    instantiation time:

    .. _BeartypeConf.is_color:

    * **is_color**\ : Optional[bool] = None

      Tri-state boolean governing how and whether beartype colours
      **type-checking violations** (i.e., human-readable
      beartype.roar.BeartypeCallHintViolation_ exceptions) with POSIX-compliant
      ANSI escape sequences for readability. Specifically, if this boolean is:

      * ``False``, beartype *never* colours type-checking violations
        raised by callables configured with this configuration.
      * ``True``, beartype *always* colours type-checking violations
        raised by callables configured with this configuration.
      * ``None``, beartype conditionally colours type-checking violations
        raised by callables configured with this configuration only when
        standard output is attached to an interactive terminal.

      Defaults to ``None``.

      The standard use case is to dynamically define your own app-specific
      ``@beartype`` decorator unconditionally disabling colours in type-checking
      violations, usually due to one or more frameworks in your application
      stack failing to support ANSI escape sequences. Please file upstream
      issues with those frameworks requesting ANSI support. In the meanwhile,
      behold the monochromatic powers of... ``@monobeartype``!

      .. code-block:: python

         # Import the requisite machinery.
         from beartype import beartype, BeartypeConf

         # Dynamically create a new @monobeartype decorator disabling colour.
         monobeartype = beartype(conf=BeartypeConf(is_color=False))

         # Decorate with this decorator rather than @beartype everywhere.
         @monobeartype
         def muh_colorless_func() -> str:
             return b'In the kingdom of the blind, you are now king.'

      *First introduced in beartype 0.12.0.*

    .. _BeartypeConf.is_debug:

    * **is_debug**\ : bool = False

      ``True`` only if debugging the ``@beartype`` decorator. If you're curious
      as to what exactly (if anything) ``@beartype`` is doing on your behalf,
      temporarily enable this boolean. Specifically, enabling this boolean:

      * Caches the body of each type-checking wrapper function dynamically
        generated by ``@beartype`` with the standard linecache_ module, enabling
        these function bodies to be introspected at runtime *and* improving the
        readability of tracebacks whose call stacks contain one or more calls to
        these ``@beartype.beartype``\ -decorated functions.
      * Prints the definition (including both the signature and body) of each
        type-checking wrapper function dynamically generated by ``@beartype`` to
        standard output.
      * Appends to the declaration of each **hidden parameter** (i.e., whose
        name is prefixed by ``"__beartype_"`` and whose value is that of an
        external attribute internally referenced in the body of that function)
        a comment providing the machine-readable representation of the initial
        value of that parameter, stripped of newlines and truncated to a
        hopefully sensible length. Since the low-level string munger called to
        do so is shockingly slow, these comments are conditionally embedded in
        type-checking wrapper functions *only* when this boolean is enabled.

      Defaults to ``False``. Eye-gouging sample output or it didn't happen, so:

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

    .. _BeartypeConf.is_pep484_tower:

    * **is_pep484_tower**\ : bool = False

      ``True`` only if enabling support for `PEP 484's implicit numeric tower
      <implicit numeric tower_>`__ (i.e., lossy conversion of integers to
      floating-point numbers as well as both integers and floating-point
      numbers to complex numbers). Specifically, enabling this instructs
      beartype to automatically expand:

      * All ``float`` type hints to ``float | int``, thus implicitly accepting
        both integers and floating-point numbers for objects annotated as only
        accepting floating-point numbers.
      * All ``complex`` type hints to ``complex | float | int``, thus
        implicitly accepting integers, floating-point, and complex numbers for
        objects annotated as only accepting complex numbers.

      Defaults to ``False`` to minimize precision error introduced by lossy
      conversions from integers to floating-point numbers to complex numbers.
      Since most integers do *not* have exact representations as floating-point
      numbers, each conversion of an integer into a floating-point number
      typically introduces a small precision error that accumulates over
      multiple conversions and operations into a larger precision error.
      Enabling this improves the usability of public APIs at a cost of
      introducing precision errors.

      The standard use case is to dynamically define your own app-specific
      ``@beartype`` decorator unconditionally enabling support for the implicit
      numeric tower, usually as a convenience to your userbase who do *not*
      particularly care about the above precision concerns. Behold the
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

      *First introduced in beartype 0.12.0.*

    .. _BeartypeConf.strategy:

    * **strategy**\ : BeartypeStrategy_ = BeartypeStrategy.O1_

      **Type-checking strategy** (i.e., BeartypeStrategy_ enumeration member
      dictating how many items are type-checked at each nesting level of each
      container and thus how responsively beartype type-checks containers). This
      setting governs the core tradeoff in runtime type-checking between:

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

      Defaults to BeartypeStrategy.O1_, the constant-time ``O(1)`` strategy –
      maximizing scalability at a cost of also maximizing false positives.

BeartypeStrategy
****************

.. _beartype.BeartypeStrategy:

*class* beartype.\ **BeartypeStrategy**\ (enum.Enum)

    Enumeration of all kinds of **type-checking strategies** (i.e., competing
    procedures for type-checking objects passed to or returned from
    ``@beartype``\ -decorated callables, each with concomitant tradeoffs with
    respect to runtime complexity and quality assurance).

    Strategies are intentionally named according to `conventional Big O
    notation <Big O_>`__ (e.g., BeartypeStrategy.On_ enables the ``O(n)``
    strategy). Strategies are established per-decoration at the fine-grained
    level of callables decorated by the ``@beartype`` decorator by setting the
    BeartypeConf.strategy_ parameter of the beartype.BeartypeConf_ object passed
    as the optional ``conf`` parameter to that decorator.

    Strategies enforce their corresponding runtime complexities (e.g., ``O(n)``)
    across *all* type-checks performed for callables enabling those strategies.
    For example, a callable configured by the BeartypeStrategy.On_ strategy will
    exhibit linear ``O(n)`` complexity as its overhead for type-checking each
    nesting level of each container passed to and returned from that callable.

    This enumeration defines these members:

    .. _BeartypeStrategy.O0:

    * BeartypeStrategy.\ **O0** : beartype.cave.EnumMemberType

      **No-time strategy** (i.e, disabling type-checking for a decorated
      callable by reducing ``@beartype`` to the identity decorator for that
      callable). This strategy is functionally equivalent to but more
      general-purpose than the standard `@typing.no_type_check`_ decorator;
      whereas `@typing.no_type_check`_ only applies to callables, this strategy
      applies to *any* context accepting a beartype configuration such as:

      * The ``@beartype`` decorator decorating a class.
      * The `beartype.door.is_bearable() function <is_bearable_>`__.
      * The `beartype.door.die_if_unbearable() function <die_if_unbearable_>`__.
      * The `beartype.door.TypeHint.is_bearable() method <beartype.door_>`__.
      * The `beartype.door.TypeHint.die_if_unbearable() method
        <beartype.door_>`__.

      Just like in real life, there exist use cases for doing absolutely
      nothing – including:

      * **Blacklisting callables.** Although seemingly useless, this strategy
        allows callers to selectively prevent callables that would otherwise be
        type-checked (e.g., due to class decorations or import hooks) from being
        type-checked:

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
        performed by beartype. Please prepare your resume beforehand. Also, do
        so *only* under production builds intended for release; development
        builds intended for testing should preserve type-checking.

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

    .. _BeartypeStrategy.O1:

    * BeartypeStrategy.\ **O1** : beartype.cave.EnumMemberType

      **Constant-time strategy** (i.e., the default ``O(1)`` strategy,
      type-checking a single randomly selected item of each container). As the
      default, this strategy need *not* be explicitly enabled.

    .. _BeartypeStrategy.Ologn:

    * BeartypeStrategy.\ **Ologn** : beartype.cave.EnumMemberType

      **Logarithmic-time strategy** (i.e., the ``O(log n)`` strategy,
      type-checking a randomly selected number of items ``log(len(obj))`` of
      each container ``obj``). This strategy is **currently unimplemented.**
      (*To be implemented by a future beartype release.*)

    .. _BeartypeStrategy.On:

    * BeartypeStrategy.\ **On** : beartype.cave.EnumMemberType

      **Linear-time strategy** (i.e., the ``O(n)`` strategy, type-checking *all*
      items of a container). This strategy is **currently unimplemented.** (*To
      be implemented by a future beartype release.*)


*************
Beartype DOOR
*************

.. _beartype.door:

Enter the **DOOR** (\ **D**\ ecidedly **O**\ bject-\ **o**\ riented **R**\
untime-checker): the first usable public Pythonic API for introspecting,
comparing, and type-checking type hints in ``O(1)`` time with negligible
constants.

Procedural API
##############

Type-check *anything* at *any* time against *any* type hint. When the
``isinstance()`` and ``issubclass()`` builtins fail to scale, prefer the
``beartype.door`` procedural API.

.. # FIXME: Document the new "beartype.peps" submodule as well, please!

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

.. _api:beartype.vale:

*******************
Beartype Validators
*******************

.. parsed-literal::

   Validate anything with two-line type hints
          designed by you ⇄ built by beartype

When official type hints fail to scale, design your own PEP-compliant type
hints with compact two-line **beartype validators:**

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
nestable declarative expressions leveraging `familiar "typing" syntax
<typing_>`__ – all seamlessly composable with :ref:`standard type hints
<eli5:typing>` via an `expressive domain-specific language (DSL) <Validator
Syntax_>`__.

Validate custom project constraints *now* without waiting for the open-source
community to officially standardize, implement, and publish those constraints.
Filling in the Titanic-sized gaps between :ref:`Python's patchwork quilt of PEPs
<pep:pep>`, validators accelerate your QA workflow with your greatest asset.

Yup. It's your brain.

See `Validator Showcase`_ for comforting examples – or blithely continue for
uncomfortable details you may regret reading.

Validator Overview
##################

Beartype validators are **zero-cost code generators.** Like the rest of beartype
(but unlike other validation frameworks), beartype validators dynamically
generate optimally efficient pure-Python type-checking logic with *no* hidden
function or method calls, undocumented costs, or runtime overhead.

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

Beartype validators thus come in two flavours – each with its attendant
tradeoffs:

* **Functional validators,** created by subscripting the `beartype.vale.Is`_
  class with a function accepting a single parameter and returning ``True`` only
  when that parameter satisfies a caller-defined constraint. Each functional
  validator incurs the cost of calling that function for each call to each
  ``@beartype``\ -decorated callable annotated by that validator, but is
  Turing-complete and thus supports all possible validation scenarios.
* **Declarative validators,** created by subscripting any *other* class in the
  ``beartype.vale`` subpackage (e.g., `beartype.vale.IsEqual`_) with arguments
  specific to that class. Each declarative validator generates efficient inline
  code calling *no* hidden functions and thus incurring no function costs, but
  is special-purpose and thus supports only a narrow band of validation
  scenarios.

Wherever you can, prefer *declarative* validators for efficiency. Everywhere
else, fallback to *functional* validators for generality.

Validator API
#############

.. _beartype.vale.Is:

*class* beartype.vale.\ **Is**\ [collections.abc.Callable_\ [[typing.Any_\ ], bool]]

    **Functional validator.** A PEP-compliant type hint enforcing any arbitrary
    runtime constraint, created by subscripting (indexing) the ``Is`` type hint
    factory with a function accepting a single parameter and returning either:

    * ``True`` if that parameter satisfies that constraint.
    * ``False`` otherwise.

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

    See ``help(beartype.vale.Is)`` for further details.

.. _beartype.vale.IsAttr:

*class* beartype.vale.\ **IsAttr**\ [str, beartype.vale.*]

    **Declarative attribute validator.** A PEP-compliant type hint enforcing any
    arbitrary runtime constraint on any named object attribute, created by
    subscripting (indexing) the ``IsAttr`` type hint factory with (in order):

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
    ``"dtype.type"``) may be validated by nesting successive ``IsAttr``
    subscriptions:

    .. code-block:: python

       # Type hint matching only NumPy arrays of 64-bit floating-point numbers.
       # From this, @beartype generates an efficient expression resembling:
       #     isinstance(array, np.ndarray) and array.dtype.type == np.float64
       NumpyFloat64Array = Annotated[np.ndarray,
           IsAttr['dtype', IsAttr['type', IsEqual[np.float64]]]]

    The second argument subscripting this class *must* be a beartype validator.
    This includes:

    * ``beartype.vale.Is``, in which case this parent ``IsAttr`` class validates
      the desired object attribute to satisfy the caller-defined function
      subscripting that child ``Is`` class.
    * ``beartype.vale.IsAttr``, in which case this parent ``IsAttr`` class
      validates the desired object attribute to contain a nested object
      attribute satisfying the child ``IsAttr`` class. See above example.
    * ``beartype.vale.IsEqual``, in which case this ``IsAttr`` class validates
      the desired object attribute to be equal to the object subscripting that
      ``IsEqual`` class. See above example.

    See ``help(beartype.vale.IsAttr)`` for further details.

.. _beartype.vale.IsEqual:

*class* beartype.vale.\ **IsEqual**\ [typing.Any_\ ]

    **Declarative equality validator.** A PEP-compliant type hint enforcing
    equality against any object, created by subscripting (indexing) the
    ``IsEqual`` type hint factory with that object:

    .. code-block:: python

       # Import the requisite machinery.
       from beartype.vale import IsEqual
       from typing import Annotated   # <--------------- if Python ≥ 3.9.0
       #from typing_extensions import Annotated   # <--- if Python < 3.9.0

       # Type hint matching only lists equal to [0, 1, 2, ..., 40, 41, 42].
       AnswerToTheUltimateQuestion = Annotated[list, IsEqual[list(range(42))]]

    ``beartype.vale.IsEqual`` generalizes the comparable `PEP 586`_-compliant
    typing.Literal_ type hint. Both check equality against user-defined objects.
    Despite the differing syntax, these two type hints enforce the same
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

    * ``beartype.vale.IsEqual`` permissively validates equality against objects
      that are instances of **any arbitrary type.** ``IsEqual`` doesn't care
      what the types of your objects are. ``IsEqual`` will test equality
      against everything you tell it to, because you know best.
    * typing.Literal_ rigidly validates equality against objects that are
      instances of **only six predefined types:**

      * Booleans (i.e., ``bool`` objects).
      * Byte strings (i.e., ``bytes`` objects).
      * Integers (i.e., ``int`` objects).
      * Unicode strings (i.e., ``str`` objects).
      * enum.Enum_ members. [#enum_type]_
      * The ``None`` singleton.

    Wherever you can (which is mostly nowhere), prefer typing.Literal_. Sure,
    typing.Literal_ is mostly useless, but it's standardized across
    type checkers in a mostly useless way. Everywhere else, default to
    ``beartype.vale.IsEqual``.

    See ``help(beartype.vale.IsEqual)`` for further details.

.. _beartype.vale.IsInstance:

*class* beartype.vale.\ **IsInstance**\ [type, ...]

    **Declarative instance validator.** A PEP-compliant type hint enforcing
    instancing of one or more classes, created by subscripting (indexing) the
    ``IsInstance`` type hint factory with those classes:

    .. code-block:: python

       # Import the requisite machinery.
       from beartype.vale import IsInstance
       from typing import Annotated   # <--------------- if Python ≥ 3.9.0
       #from typing_extensions import Annotated   # <--- if Python < 3.9.0

       # Type hint matching only string and byte strings, equivalent to:
       #     StrOrBytesInstance = Union[str, bytes]
       StrOrBytesInstance = Annotated[object, IsInstance[str, bytes]]

    ``beartype.vale.IsInstance`` generalizes **isinstanceable type hints**
    (i.e., normal pure-Python or C-based classes that can be passed as the
    second parameter to the ``isinstance()`` builtin). Both check instancing of
    classes. Despite the differing syntax, these hints enforce the same
    semantics:

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

    * ``beartype.vale.IsInstance`` permissively validates type instancing of
      **arbitrary objects** (including possibly nested attributes of parameters
      and returns when combined with ``beartype.vale.IsAttr``) against **one or
      more classes.**
    * Isinstanceable classes rigidly validate type instancing of only
      **parameters and returns** against only **one class.**

    Unlike isinstanceable type hints, instance validators support various `set
    theoretic operators <Validator Syntax_>`__. Critically, this includes
    negation. Instance validators prefixed by the negation operator ``~``
    match all objects that are *not* instances of the classes subscripting
    those validators. Wait. Wait just a hot minute there. Doesn't a
    typing.Annotated_ type hint necessarily match instances of the class
    subscripting that type hint? Yup. This means type hints of the form
    ``typing.Annotated[{superclass}, ~IsInstance[{subclass}]`` match all
    instances of a superclass that are *not* also instances of a subclass.
    And... pretty sure we just invented `type hint arithmetic <Type Hint
    Elision_>`__ right there.

    That sounded intellectual and thus boring. Yet, the disturbing fact that
    Python booleans are integers :superscript:`yup` while Python strings are
    infinitely recursive sequences of strings :superscript:`yup` means that
    `type hint arithmetic <Type Hint Elision_>`__ can save your codebase from
    Guido's younger self. Consider this instance validator matching only
    non-boolean integers, which *cannot* be expressed with any isinstanceable
    type hint (e.g., ``int``) or other combination of standard off-the-shelf
    type hints (e.g., unions):

    .. code-block:: python

       # Type hint matching any non-boolean integer. Never fear integers again.
       IntNonbool = Annotated[int, ~IsInstance[bool]]   # <--- bruh

    Wherever you can, prefer isinstanceable type hints. Sure, they're
    inflexible, but they're inflexibly standardized across type checkers.
    Everywhere else, default to ``beartype.vale.IsInstance``.

    See ``help(beartype.vale.IsInstance)`` for further details.

.. _beartype.vale.IsSubclass:

*class* beartype.vale.\ **IsSubclass**\ [type, ...]

    **Declarative inheritance validator.** A PEP-compliant type hint enforcing
    subclassing of one or more superclasses (base classes), created by
    subscripting (indexing) the ``IsSubclass`` type hint factory with those
    superclasses:

    .. code-block:: python

       # Import the requisite machinery.
       from beartype.vale import IsSubclass
       from typing import Annotated   # <--------------- if Python ≥ 3.9.0
       #from typing_extensions import Annotated   # <--- if Python < 3.9.0

       # Type hint matching only string and byte string subclasses.
       StrOrBytesSubclass = Annotated[type, IsSubclass[str, bytes]]

    ``beartype.vale.IsSubclass`` generalizes the comparable
    :pep:`484`\ -compliant typing.Type_ and :pep:`585`\ -compliant type_ type
    hints. All three check subclassing of arbitrary superclasses. Despite the
    differing syntax, these hints enforce the same semantics:

    .. code-block:: python

       # This beartype validator enforces the same semantics as...
       IsStringSubclassWithBeartype = Annotated[type, IsSubclass[str]]

       # ...this PEP 484-compliant type hint as well as...
       IsStringSubclassWithPep484 = Type[str]

       # ...this PEP 585-compliant type hint.
       IsStringSubclassWithPep585 = type[str]

    The similarities end there, of course:

    * ``beartype.vale.IsSubclass`` permissively validates type inheritance of
      **arbitrary classes** (including possibly nested attributes of parameters
      and returns when combined with `beartype.vale.IsAttr`_) against **one or
      more superclasses.**
    * typing.Type_ and type_ rigidly validates type inheritance of only
      **parameters and returns** against only **one superclass.**

    Consider this subclass validator, which validates type inheritance of a
    deeply nested attribute and thus *cannot* be expressed with typing.Type_ or
    type_:

    .. code-block:: python

       # Type hint matching only NumPy arrays of reals (i.e., either integers
       # or floats) of arbitrary precision, generating code resembling:
       #    (isinstance(array, np.ndarray) and
       #     issubclass(array.dtype.type, (np.floating, np.integer)))
       NumpyRealArray = Annotated[
           np.ndarray, IsAttr['dtype', IsAttr['type', IsSubclass[
               np.floating, np.integer]]]]

    Wherever you can, prefer type_ and typing.Type_. Sure, they're
    inflexible, but they're inflexibly standardized across type checkers.
    Everywhere else, default to ``beartype.vale.IsSubclass``.

    See ``help(beartype.vale.IsSubclass)`` for further details.

.. [#enum_type]
   You don't want to know the type of enum.Enum_ members. Srsly. You don't. OK?
   You do? Very well. It's enum.Enum_. :superscript:`mic drop`

.. _api:beartype.vale syntax:

Validator Syntax
################

Beartype validators support a rich domain-specific language (DSL) leveraging
familiar Python operators. Dynamically create new validators on-the-fly from
existing validators, fueling reuse and preserving DRY_:

* **Negation** (i.e., ``not``). Negating any validator with the ``~`` operator
  creates a new validator returning ``True`` only when the negated validator
  returns ``False``:

  .. code-block:: python

     # Type hint matching only strings containing *no* periods, semantically
     # equivalent to this type hint:
     #     PeriodlessString = Annotated[str, Is[lambda text: '.' not in text]]
     PeriodlessString = Annotated[str, ~Is[lambda text: '.' in text]]

* **Conjunction** (i.e., ``and``). And-ing two or more validators with the
  ``&`` operator creates a new validator returning ``True`` only when *all* of
  the and-ed validators return ``True``:

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
  operator creates a new validator returning ``True`` only when at least one of
  the or-ed validators returns ``True``:

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
  commas at the top level of a typing.Annotated_ type hint is an alternate
  syntax for and-ing those validators with the ``&`` operator, creating a new
  validator returning ``True`` only when *all* of those delimited validators
  return ``True``.

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
     validators (e.g., ``beartype.vale.IsAttr``, ``beartype.vale.IsEqual``). We
     leave this as an exercise to the idealistic doctoral thesis candidate.
     :superscript:`Please do this for us, someone who is not us.`
   * Either **Python ≥ 3.9** *or* `typing_extensions ≥ 3.9.0.0
     <typing_extensions_>`__. Validators piggyback onto the typing.Annotated_
     class first introduced with Python 3.9.0 and since backported to older
     Python versions by the `third-party "typing_extensions" package
     <typing_extensions_>`__, which beartype also transparently supports.

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
``@beartype`` decorator with a new parameter enabling full-fat type-checking.
But don't wait on us. Force the issue now by just doing it yourself and then
mocking us all over Gitter! *Fight the bear, man.*

There are good reasons to believe that :ref:`O(1) type-checking is preferable
<faq:O1>`. Violating that core precept exposes your codebase to scalability and
security concerns. But you're the Big Boss, you swear you know best, and (in any
case) we can't stop you because we already let the unneutered tomcat out of his
trash bin by `publishing this API into the badlands of PyPI <beartype PyPI_>`__.

Trendy String Matching
**********************

Let's accept strings either at least 80 characters long *or* both quoted and
suffixed by a period. Look, it doesn't matter. Just do it already,
``@beartype``!

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

:pep:`484` standardized the typing.Union_ factory `disjunctively
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
You're already there. :superscript:`...woah`

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
     4.141500000000001    # <-- oh. by. god.
     >>> isinstance(False, int)
     True                 # <-- when nothing is true, everything is true

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
     'y'                 # <-- pretty sure we just broke the world
     >>> from collections.abc import Sequence
     >>> isinstance("Ph'nglui mglw'nafh Cthu—"[0][0][0][0][0], Sequence)
     True                # <-- ...curse you, curse you to heck and back

When we annotate a callable as accepting an ``int``, we *never* want that
callable to also silently accept a ``bool``. Likewise, when we annotate another
callable as accepting a ``Sequence[Any]`` or ``Sequence[str]``, we *never* want
that callable to also silently accept a ``str``. These are sensible
expectations – just not in Python, where madness prevails.

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
uneasy, and suspicious of our core worldview, beartype also supports
third-party type hints like `typed NumPy arrays <NumPy Type Hints_>`__.

Whereas beartype validators are verbose, expressive, and general-purpose, the
following hints are terse, inexpressive, and domain-specific. Since beartype
internally converts these hints to their equivalent validators, `similar
caveats apply <Validator Caveats_>`__. Notably, these hints require:

* Either **Python ≥ 3.9** *or* `typing_extensions ≥ 3.9.0.0
  <typing_extensions_>`__.
* **Beartype,** which hopefully goes without saying.

NumPy Type Hints
****************

Beartype conditionally supports `NumPy type hints (i.e., annotations created by
subscripting (indexing) various attributes of the "numpy.typing" subpackage)
<numpy.typing_>`__ when these optional runtime dependencies are *all*
satisfied:

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
(which demands this behaviour). May there be hope for our future…

*class* numpy.typing.\ **NDArray**\ [numpy.dtype]

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

*class* numpy.typing.\ **NDArray**\ [numpy.dtype.type]

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

*class* numpy.typing.\ **NDArray**\ [type[numpy.dtype.type]]

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

.. #FIXME: Resume here tomorrow, please.

.. # ------------------( IMAGES                              )------------------
.. |beartype-banner| image:: https://raw.githubusercontent.com/beartype/beartype-assets/main/banner/logo.png
   :target: https://github.com/beartype/beartype
   :alt: beartype —[ the bare-metal type-checker ]—

.. # ------------------( IMAGES ~ badge                      )------------------
.. |ci-badge| image:: https://github.com/beartype/beartype/workflows/test/badge.svg
   :target: https://github.com/beartype/beartype/actions?workflow=test
   :alt: beartype continuous integration (CI) status
.. |codecov-badge| image:: https://codecov.io/gh/beartype/beartype/branch/main/graph/badge.svg?token=E6F4YSY9ZQ
   :target: https://codecov.io/gh/beartype/beartype
   :alt: beartype test coverage status
.. |rtd-badge| image:: https://readthedocs.org/projects/beartype/badge/?version=latest
   :target: https://beartype.readthedocs.io/en/latest/?badge=latest
   :alt: beartype Read The Docs (RTD) status
