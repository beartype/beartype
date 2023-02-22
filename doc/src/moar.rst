.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document listing related projects.

.. # ------------------( MAIN                                )------------------

########
See Also
########

External beartype resources include:

* `This list of all open-source PyPI-hosted dependents of this package
  <beartype dependents_>`__ (i.e., third-party packages requiring beartype
  as a runtime dependency), kindly furnished by the `Libraries.io package
  registry <Libraries.io_>`__.

Related type-checking resources include:

.. _moar:runtime:

*********************
Runtime Type Checkers
*********************

**Runtime type checkers** (i.e., third-party Python packages dynamically
validating callables annotated by type hints at runtime, typically via
decorators, function calls, and import hooks) include:

.. # Note: intentionally sorted in lexicographic order to avoid bias.

+-----------------+---------+---------------+---------------------------+
| package         | active  | PEP-compliant | time multiplier [#speed]_ |
+=================+=========+===============+===========================+
| beartype        | **yes** | **yes**       | 1 ✕ beartype              |
+-----------------+---------+---------------+---------------------------+
| enforce_        | no      | **yes**       | *unknown*                 |
+-----------------+---------+---------------+---------------------------+
| enforce_typing_ | no      | **yes**       | *unknown*                 |
+-----------------+---------+---------------+---------------------------+
| pydantic_       | **yes** | no            | *unknown*                 |
+-----------------+---------+---------------+---------------------------+
| pytypes_        | no      | **yes**       | *unknown*                 |
+-----------------+---------+---------------+---------------------------+
| typeen_         | no      | no            | *unknown*                 |
+-----------------+---------+---------------+---------------------------+
| typical_        | **yes** | **yes**       | *unknown*                 |
+-----------------+---------+---------------+---------------------------+
| typeguard_      | no      | **yes**       | 20 ✕ beartype             |
+-----------------+---------+---------------+---------------------------+

.. [#speed]
   The *time multliplier* column approximates **how much slower on average
   than** beartype **that checker is** as :ref:`timed by our profile suite
   <math:time>`. A time multiplier of:

   * "1" means that checker is approximately as fast as beartype, which means
     that checker is probably beartype itself.
   * "20" means that checker is approximately twenty times slower than beartype
     on average.

Like `static type checkers <Static Type Checkers_>`__, runtime type checkers
*always* require callables to be annotated by type hints. Unlike `static type
checkers <Static Type Checkers_>`__, runtime type checkers do *not* necessarily
comply with community standards; although some do require callers to annotate
callables with strictly PEP-compliant type hints, others permit or even require
callers to annotate callables with PEP-noncompliant type hints. Runtime type
checkers that do so violate:

* `PEP 561 -- Distributing and Packaging Type Information <PEP 561_>`_, which
  requires callables to be annotated with strictly PEP-compliant type hints.
  Packages violating `PEP 561`_ even once cannot be type-checked with `static
  type checkers <Static Type Checkers_>`__ (e.g., mypy_), unless each such
  violation is explicitly ignored with a checker-specific filter (e.g., with a
  mypy_-specific inline type comment).
* `PEP 563 -- Postponed Evaluation of Annotations <PEP 563_>`_, which
  explicitly deprecates PEP-noncompliant type hints:

      With this in mind, **uses for annotations incompatible with the
      aforementioned PEPs** *[i.e., PEPs 484, 544, 557, and 560]* **should be
      considered deprecated.**

***********************
Runtime Data Validators
***********************

**Runtime data validators** (i.e., third-party Python packages dynamically
validating callables decorated by caller-defined contracts, constraints, and
validation routines at runtime) include:

.. # Note: intentionally sorted in lexicographic order to avoid bias.

* PyContracts_.
* contracts_.
* covenant_.
* dpcontracts_.
* icontract_.
* pcd_.
* pyadbc_.

Unlike both `runtime type checkers <Runtime Type Checkers_>`__ and `static type
checkers <Static Type Checkers_>`__, most runtime data validators do *not*
require callables to be annotated by type hints. Like some `runtime type
checkers <Runtime Type Checkers_>`__, most runtime data validators do *not*
comply with community standards but instead require callers to either:

* Decorate callables with package-specific decorators.
* Annotate callables with package-specific and thus PEP-noncompliant type
  hints.

.. _moar:static:

********************
Static Type Checkers
********************

**Static type checkers** (i.e., third-party tooling validating Python callable
and/or variable types across an application stack at static analysis time
rather than Python runtime) include:

.. # Note: Intentionally sorted in lexicographic order to avoid subjective bias.

* mypy_, Python's official static type checker.
* Pyre_, published by Meta. :sup:`...yah.`
* pyright_, published by Microsoft.
* pytype_, published by Google.
