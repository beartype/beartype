.. # ------------------( SYNOPSIS                           )------------------

========
beartype
========

.. epigraph:

   Look for the bare necessities,
     the simple bare necessities.
   Forget about your worries and your strife.

   -- The Jungle Book

**Beartype** is an open-source pure-Python runtime type checker emphasizing
efficiency, portability, and sadly unfunny punniness.

Unlike comparable static type checkers operating at the coarse-grained
application level (e.g., Pyre_, mypy_, pyright_, pytype_), beartype operates
exclusively at the fine-grained callable level of pure-Python functions and
methods via a decorator design pattern. This renders beartype natively
compatible with *all* interpreters and compilers targeting the Python language
– including CPython_, PyPy_, and Numba_.

Unlike comparable runtime type checkers (e.g., typeguard_), beartype
dynamically generates one unique wrapper implementing optimal type-checking for
each decorated callable. "Performance by default" is a first-class concern. For
efficiency and safety, *all* wrappers are guaranteed to:

* Exhibit ``O(1)`` time complexity with minimal constant factors.
* Be either more efficient (in the common case) or exactly as efficient (in
  the worst case) as equivalent type-checking implementated by hand.

Beartype thus brings Rust_- and C++_-inspired `zero-cost abstractions
<zero-cost abstraction_>`__ into the deliciously lawless world of pure Python.

Beartype is `portably implemented <codebase_>`__ in pure `Python 3`_,
continuously stress-tested with `Travis CI`_ **+** pytest_ **+** tox_, and
`permissively distributed <license_>`__ under the `MIT license`_.

.. # ------------------( TABLE OF CONTENTS                  )------------------
.. # Blank line. By default, Docutils appears to only separate the subsequent
.. # table of contents heading from the prior paragraph by less than a single
.. # blank line, hampering this table's readability and aesthetic comeliness.

|

.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Contents**
   :local:

.. # ------------------( DESCRIPTION                        )------------------

.. #FIXME: Uncomment the following *AFTER* releasing to PyPI and conda-forge.
.. # Installation
.. # ============
..
.. # Beartype is universally installable with either:
..
.. # - [\ *Recommended*\ ] pip_, the standard Python package manager:
..
.. #   .. code-block:: console
..
.. #      pip3 install beartype
..
.. # - Anaconda_, a third-party Python package manager:
..
.. #   .. code-block:: console
..
.. #      conda config --add channels conda-forge
.. #      conda install beartype

Usage
=====

.. attention:
   This section is currently a work in progress.

Beartype is usable and its usage shall be documented and this shall be good.

License
=======

Beartype is `open-source software released <license_>`__ under the
`permissive MIT license <MIT license_>`__.

Funding
=======

Beartype is currently financed as a purely volunteer open-source project.
However, prior funding sources include:

#. Over the period 2015—2018 preceding the untimely death of `Paul Allen`_,
   beartype was graciously associated with the `Paul Allen Discovery Center`_
   at `Tufts University`_ and grant-funded by a `Paul Allen Discovery Center
   award`_ from the `Paul G. Allen Frontiers Group`_ through its parent
   applications – the multiphysics biology simulators BETSE_ and BETSEE_.

See Also
========

**Runtime type checkers** (i.e., third-party mostly pure-Python packages
dynamically validating Python callable types at Python runtime, typically via
decorators, explicit function calls, and import hooks) include:

.. # Note: intentionally sorted in lexicographic order to avoid bias.

* beartype. :sup:`...that's us.`
* typeguard_.

**Static type checkers** (i.e., third-party tooling *not* implemented in Python
statically validating Python callable and/or variable types across a full
application stack at tool rather than Python runtime) include:

.. # Note: intentionally sorted in lexicographic order to avoid bias.

* `Pyre from FaceBook <Pyre_>`__.
* mypy_.
* `pyright from Microsoft <pyright_>`__.
* `pytype from Google <pytype_>`__.

Lastly, relevant **Python Enhancement Proposals (PEPs)** include:

.. # Note: intentionally sorted in numeric order for collective sanity.

* `PEP 483 -- The Theory of Type Hints <PEP 483_>`__.
* `PEP 484 -- Type Hints <PEP 484_>`__.
* `PEP 526 -- Syntax for Variable Annotations <PEP 526_>`__.
* `PEP 544 -- Protocols: Structural subtyping (static duck typing) <PEP
  544_>`_.
* `PEP 589 -- TypedDict: Type Hints for Dictionaries with a Fixed Set of Keys
  <PEP 589_>`__.

.. # ------------------( LINKS ~ beartype : local           )------------------
.. _license:
   LICENSE

.. # ------------------( LINKS ~ beartype : remote          )------------------
.. _codebase:
   https://github.com/beartype/beartype/tree/master/beartype

.. # ------------------( LINKS ~ beartype : funding         )------------------
.. _BETSE:
   https://gitlab.com/betse/betse
.. _BETSEE:
   https://gitlab.com/betse/betsee
.. _Paul Allen:
   https://en.wikipedia.org/wiki/Paul_Allen
.. _Paul Allen Discovery Center:
   http://www.alleninstitute.org/what-we-do/frontiers-group/discovery-centers/allen-discovery-center-tufts-university
.. _Paul Allen Discovery Center award:
   https://www.alleninstitute.org/what-we-do/frontiers-group/news-press/press-resources/press-releases/paul-g-allen-frontiers-group-announces-allen-discovery-center-tufts-university
.. _Paul G. Allen Frontiers Group:
   https://www.alleninstitute.org/what-we-do/frontiers-group
.. _Tufts University:
   https://www.tufts.edu

.. # ------------------( LINKS ~ non-py                     )------------------
.. _C++:
   https://en.wikipedia.org/wiki/C%2B%2B
.. _Rust:
   https://www.rust-lang.org
.. _zero-cost abstraction:
   https://boats.gitlab.io/blog/post/zero-cost-abstractions

.. # ------------------( LINKS ~ py                         )------------------
.. _Python 3:
   https://www.python.org
.. _pip:
   https://pip.pypa.io

.. # ------------------( LINKS ~ py : implementation        )------------------
.. _CPython:
.. _PyPy:
   .
.. _Numba:
   https://numba.pydata.org

.. # ------------------( LINKS ~ py : pep                   )------------------
.. _PEP 483:
   https://www.python.org/dev/peps/pep-0483
.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
.. _PEP 526:
   https://www.python.org/dev/peps/pep-0526
.. _PEP 544:
   https://www.python.org/dev/peps/pep-0544
.. _PEP 589:
   https://www.python.org/dev/peps/pep-0589

.. # ------------------( LINKS ~ py : test                  )------------------
.. _pytest:
   https://docs.pytest.org
.. _tox:
   https://tox.readthedocs.io

.. # ------------------( LINKS ~ py : type : runtime        )------------------
.. _typeguard:
   https://github.com/agronholm/typeguard

.. # ------------------( LINKS ~ py : type : static         )------------------
.. _Pyre:
   https://pyre-check.org
.. _mypy:
   http://mypy-lang.org
.. _pytype:
   https://github.com/google/pytype
.. _pyright:
   https://github.com/Microsoft/pyright

.. # ------------------( LINKS ~ service                    )------------------
.. _Travis CI:
   https://travis-ci.org

.. # ------------------( LINKS ~ standard                   )------------------
.. _MIT license:
   https://opensource.org/licenses/MIT
