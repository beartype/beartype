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

.. # ------------------( TODO                                )------------------
.. #FIXME: Replace and/or supplement badges shown below with third-party badges
.. #published by "https://shields.io"; the look-and-feel of shields.io badges is
.. #the flat design favoured by modern apps and thus ostensibly superior to
.. #anything else I've seen. Relevant HTML that we'll want to translate into
.. #corresponding reST resembles:
.. #    <a href="https://github.com/beartype/beartype/stargazers">
.. #    <img src="https://img.shields.io/github/stars/beartype/beartype?style=for-the-badge" alt="@beartype stars"/>
.. #    </a>
.. #    <a href="https://github.com/beartype/beartype/fork">
.. #    <img src="https://img.shields.io/github/forks/beartype/beartype?style=for-the-badge" alt="@beartype forks"/>
.. #    </a>
.. #    </a>
.. #    <a href="https://github.com/beartype/beartype/releases">
.. #    <img src="https://img.shields.io/github/release/beartype/beartype?&label=Latest&style=for-the-badge"/>
.. #
.. #See also this exhaustive list of all GitHub-specific shield.io badges:
.. #    https://shields.io/category/activity

.. # ------------------( MAIN                                )------------------

|beartype-banner|

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
<pep:pep>` in :math:`O(1)` :ref:`non-amortized worst-case time with negligible
constant factors <math:time>`. If the prior sentence was unreadable jargon, see
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

.. # FIXME: Gah! Libraries.io has fallen down and cannot get back up... *AGAIN.*
.. #     Beartype `powers quality assurance across the Python ecosystem <beartype
.. #     dependents_>`__.

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Project-wide tables of contents (TOCs). See also official documentation on
.. # the Sphinx-specific "toctree::" directive:
.. #     https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree

###############
The Typing Tree
###############

Welcome to the **Bearpedia** – your one-stop "free as in freedom" shop for
beartype's ponderous documentation. It's "typing_ or bust!" as you...

.. # Root TOC tree, including:
.. # * "... <self>", an entry self-referentially referring back to this document
.. #   enabling users to trivially navigate back to this document from
.. #   elsewhere. The ":hidden:" option adds this entry to the TOC sidebar while
.. #   omitting this entry from the TOC displayed inline in this document. This
.. #   is sensible; since any user currently viewing this document has *NO* need
.. #   to navigate to the current document, this inline TOC omits this entry.
.. #   :hidden:
.. #   :titlesonly:
.. #   :maxdepth: 2
.. toctree::
   :caption: Bear with Us

   Bearpedia <self>
   Install <install>
   tl;dr <tldr>
   ELI5 <eli5>
   API <api>
   FAQ <faq>
   BigData™ <pep>
   Code <code>
   Math <math>
   Moar <moar>

*Let's type this.*

.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

#######
License
#######

Beartype is `open-source software released <beartype license_>`__ under the
`permissive MIT license <MIT license_>`__.

#######
Funding
#######

Beartype is financed as a `purely volunteer open-source project via GitHub
Sponsors <GitHub Sponsors_>`__, to whom our burgeoning community is eternally
indebted. Without your generosity, runtime type-checking would be a shadow of
its current hulking bulk. We genuflect before your selfless charity, everyone!

Prior official funding sources (*yes, they once existed*) include:

#. A `Paul Allen Discovery Center award`_ from the `Paul G. Allen Frontiers
   Group`_ under the administrative purview of the `Paul Allen Discovery
   Center`_ at `Tufts University`_ over the period 2015—2018 preceding the
   untimely death of `Microsoft co-founder Paul Allen <Paul Allen_>`__, during
   which beartype was maintained as the private ``@type_check`` decorator in the
   `Bioelectric Tissue Simulation Engine (BETSE) <BETSE_>`__. :sup:`Phew!`

############
Contributors
############

Beartype is the work product of volunteer enthusiasm, excess caffeine, and
sleepless Wednesday evenings. These brave GitHubbers hurtled `the pull request
(PR) gauntlet <beartype pulls_>`__ so that you wouldn't have to:

|beartype-contributors|

It's a heavy weight they bear. Applaud them as they buckle under the load!

#######
History
#######

|beartype-stars|

.. # ------------------( IMAGES                              )------------------
.. |beartype-banner| image:: https://raw.githubusercontent.com/beartype/beartype-assets/main/banner/logo.png
   :target: https://github.com/beartype/beartype
   :alt: beartype —[ the bare-metal type-checker ]—
.. |beartype-contributors| image:: https://contrib.rocks/image?repo=beartype/beartype
   :target: https://github.com/beartype/beartype/graphs/contributors
   :alt: Beartype contributors
.. |beartype-stars| image:: https://star-history.com/#beartype/beartype&Date
   :target: https://github.com/beartype/beartype/stargazers
   :alt: Beartype stargazers

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
