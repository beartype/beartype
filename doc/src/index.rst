.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Root reStructuredText (reST) document transitively referencing all other
.. # child reST documents for this project.
.. #
.. # ------------------( SEO                                 )------------------
.. # Metadata converted into HTML-specific meta tags parsed by search engines.
.. # Note that:
.. # * The "description" should be no more than 300 characters and ideally no
.. #   more than 150 characters, as search engines may silently truncate this
.. #   description to 150 characters in edge cases.

.. meta::
   :description lang=en:
     Beartype is an open-source pure-Python PEP-compliant constant-time runtime
     type-checker emphasizing efficiency and portability.

.. # ------------------( MAIN                                )------------------

#################
|beartype-banner|
#################

|codecov-badge| |ci-badge| |rtd-badge|

**Beartype** is an `open-source <beartype license_>`__ :ref:`PEP-compliant
<pep:pep>` :ref:`near-real-time <faq:realtime>` :ref:`pure-Python runtime
type-checker <eli5:eli5>` emphasizing efficiency, usability, and thrilling puns.

.. #FIXME: Once we actually receive a sponsor at this tier, please remove this
.. #placeholder as well as the icon links below. kthx
.. #The `Bear Team <beartype organization_>`__ gratefully thanks `our family of
.. #breathtaking GitHub Sponsors <beartype sponsorship_>`__:
.. #
.. #* **Your iconic URL here.** `Let us bestow you with eyeballs <beartype
.. #  sponsorship_>`__.
.. #FIXME: Once we actually receive a sponsor at this tier, please remove this
.. #placeholder as well as the icon links below. kthx
.. #    |icon-for-glorious-sponsor|

.. code-block:: bash

   # Install beartype.
   $ pip3 install beartype
   # So let's do this.
   $ python3

.. code-block:: pycon

   # Import the @beartype decorator.
   >>> from beartype import beartype

   # Annotate @beartype-decorated classes and callables with type hints.
   >>> @beartype
   ... def quote_wiggum(lines: list[str]) -> None:
   ...     print('“{}”\n\t— Police Chief Wiggum'.format("\n ".join(lines)))

   # Call those callables with valid parameters.
   >>> quote_wiggum(["Okay, folks. Show's over!", " Nothing to see here. Show's…",])
   “Okay, folks. Show's over!
    Nothing to see here. Show's…”
      — Police Chief Wiggum

   # Call those callables with invalid parameters.
   >>> quote_wiggum([b"Oh, my God! A horrible plane crash!", b"Hey, everybody! Get a load of this flaming wreckage!",])
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "<string>", line 30, in quote_wiggum
     File "/home/springfield/beartype/lib/python3.9/site-packages/beartype/_decor/_code/_pep/_error/errormain.py", line 220, in get_beartype_violation
       raise exception_cls(
   beartype.roar.BeartypeCallHintParamViolation: @beartyped
   quote_wiggum() parameter lines=[b'Oh, my God! A horrible plane
   crash!', b'Hey, everybody! Get a load of thi...'] violates type hint
   list[str], as list item 0 value b'Oh, my God! A horrible plane crash!'
   not str.

   # ..................{ VALIDATORS  }..................
   # Squash bugs by refining type hints with validators.
   >>> from beartype.vale import Is  # <---- validator factory
   >>> from typing import Annotated  # <---------------- if Python ≥ 3.9.0
   # >>> from typing_extensions import Annotated   # <-- if Python < 3.9.0

   # Validators are type hints constrained by lambda functions.
   >>> ListOfStrings = Annotated[  # <----- type hint matching non-empty list of strings
   ...     list[str],  # <----------------- type hint matching possibly empty list of strings
   ...     Is[lambda lst: bool(lst)]  # <-- lambda matching non-empty object
   ... ]

   # Annotate @beartype-decorated callables with validators.
   >>> @beartype
   ... def quote_wiggum_safer(lines: ListOfStrings) -> None:
   ...     print('“{}”\n\t— Police Chief Wiggum'.format("\n ".join(lines)))

   # Call those callables with invalid parameters.
   >>> quote_wiggum_safer([])
   beartype.roar.BeartypeCallHintParamViolation: @beartyped
   quote_wiggum_safer() parameter lines=[] violates type hint
   typing.Annotated[list[str], Is[lambda lst: bool(lst)]], as value []
   violates validator Is[lambda lst: bool(lst)].

   # ..................{ AT ANY TIME }..................
   # Type-check anything against any type hint –
   # anywhere at anytime.
   >>> from beartype.door import (
   ...     is_bearable,  # <-------- like "isinstance(...)"
   ...     die_if_unbearable,  # <-- like "assert isinstance(...)"
   ... )
   >>> is_bearable(['The', 'goggles', 'do', 'nothing.'], list[str])
   True
   >>> die_if_unbearable([0xCAFEBEEF, 0x8BADF00D], ListOfStrings)
   beartype.roar.BeartypeDoorHintViolation: Object [3405692655, 2343432205]
   violates type hint typing.Annotated[list[str], Is[lambda lst: bool(lst)]],
   as list index 0 item 3405692655 not instance of str.

   # ..................{ GO TO PLAID }..................
   # Type-check anything in around 1µs (one millionth of
   # a second) – including this list of one million
   # 2-tuples of NumPy arrays.
   >>> from beartype.door import is_bearable
   >>> from numpy import array, ndarray
   >>> data = [(array(i), array(i)) for i in range(1000000)]
   >>> %time is_bearable(data, list[tuple[ndarray, ndarray]])
       CPU times: user 31 µs, sys: 2 µs, total: 33 µs
       Wall time: 36.7 µs
   True

Beartype brings Rust_- and `C++`_-inspired `zero-cost abstractions <zero-cost
abstraction_>`__ into the lawless world of `dynamically-typed`_ Python by
:ref:`enforcing type safety at the granular level of functions and methods
<eli5:eli5>` against :ref:`type hints standardized by the Python community
<pep:pep>` in `O(1) non-amortized worst-case time with negligible constant
factors <Timings_>`__. If the prior sentence was unreadable jargon, see
:ref:`our friendly and approachable FAQ for a human-readable synopsis
<faq:faq>`.

Beartype is `portably implemented <beartype codebase_>`__ in `Python 3
<Python_>`__, `continuously stress-tested <beartype tests_>`__ via `GitHub
Actions`_ **×** tox_ **×** pytest_ **×** Codecov_, and `permissively
distributed <beartype license_>`__ under the `MIT license`_. Beartype has *no*
runtime dependencies, `only one test-time dependency <pytest_>`__, and `only
one documentation-time dependency <Sphinx_>`__. Beartype supports `all actively
developed Python versions <Python status_>`__, :ref:`all Python package managers
<install:install>`, and :ref:`multiple platform-specific package managers
<install:install>`.

    Beartype `powers quality assurance across the Python ecosystem <beartype
    dependents_>`__.

.. #FIXME: Currently unused, but we still adore this section heading. Preserved!
.. # Let's Type This
.. # ***************

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Project-wide tables of contents (TOCs). See also official documentation on
.. # the Sphinx-specific "toctree::" directive:
.. #     https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree

.. # FIXME: *AH-HA!* The left sidebar is empty, which frankly doesn't make sense.
.. # To resolve this, let's:
.. # * First, try updating to the newest version of the PyData theme.
.. # * If that fails, it looks like we'll manually need to add a new
.. #   "_templates/sidebar-nav-bs.html" file resembling this:
.. #   https://github.com/holoviz/holoviews/blob/main/doc/_templates/sidebar-nav-bs.html
.. #   See this related link as well:
.. #   https://github.com/pydata/pydata-sphinx-theme/issues/90#issuecomment-1181250562
.. # * Let's necrobump document this for others struggling with similar issues
.. #   at this related issue:
.. #   https://github.com/pydata/pydata-sphinx-theme/issues/221
.. #   Humorously, note that the Holoviews guy forgot how he did this. *lolbro*
.. #   In particular, gently suggest that the current behaviour makes *NO SENSE*
.. #   and that the other behaviour that literally everyone is copy-pasting into
.. #   their projects is a substantial improvement. Indeed, let's just promote
.. #   this to a feature request for a theme-specific option to enable this.

.. # Leading TOC entry self-referentially referring back to this document,
.. # enabling users to trivially navigate back to this document from elsewhere.
.. #
.. # Note that:
.. # * The ":hidden:" option adds this entry to the TOC sidebar while omitting
.. #   this entry from the TOC displayed inline in this document. This is
.. #   sensible; since any user currently viewing this document has *NO* need to
.. #   navigate to the current document, this inline TOC omits this entry.
.. toctree::
   :caption: Bear with Us
   :hidden:
   :titlesonly:
   :maxdepth: 2

   Bearpedia <self>
   Install <install>
   ELI5 <eli5>
   FAQ <faq>
   Features <pep>

.. #   :hidden:
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

|

.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

###
API
###

Beartype isn't just the ``@beartype.beartype`` decorator.

Beartype is a menagerie of public APIs for type-checking, introspecting, and
manipulating type hints at runtime – all accessible under the ``beartype``
package installed when you installed beartype. But all beartype documentation
begins with ``@beartype.beartype``, just as all rivers run to the sea.
:superscript:`False! Do endorheic basins mean nothing to you, Ecclesiastes 1:7?`

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

*******************
Beartype Exceptions
*******************

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

Beartype is fastidious to a fault. Exception handling is no... *exception*.
<sup>punny *or* funny? you decide.</sup>

Exception API
#############

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
