<!--
------------------( LICENSE                                  )------------------
Copyright (c) 2014-2026 Beartype authors.
See "LICENSE" for further details.

------------------( SYNOPSIS                                 )------------------
Child Markdown document listing related projects.
-->

# See Also

External beartype resources include:

- [This list of all open-source PyPI-hosted dependents of this package][beartype dependents] (i.e., third-party packages requiring beartype as a runtime dependency), kindly furnished by the [Libraries.io package registry][Libraries.io].

Related type-checking resources include:

## Runtime Type Checkers

**Runtime type checkers** (i.e., third-party Python packages dynamically validating callables annotated by type hints at runtime, typically via decorators, function calls, and import hooks) include:

| package                                                               | active  | PEP-compliant | time multiplier[^1] |
|-----------------------------------------------------------------------|---------|---------------|---------------------|
| beartype                                                              | **yes** | **yes**       | 1 ✕ beartype        |
| [enforce]                         | no      | **yes**       | *unknown*           |
| [enforce_typing] | no      | **yes**       | *unknown*           |
| [pydantic][Pydantic]                                 | **yes** | no            | *unknown*           |
| [pytypes]                         | no      | **yes**       | *unknown*           |
| [typeen]                               | no      | no            | *unknown*           |
| [typical]                    | **yes** | **yes**       | *unknown*           |
| [typeguard]                   | no      | **yes**       | 20 ✕ beartype       |

Like [static type checkers](#static-type-checkers), runtime type checkers *always* require callables to be annotated by type hints. Unlike [static type checkers](#static-type-checkers), runtime type checkers do *not* necessarily comply with community standards; although some do require callers to annotate callables with strictly PEP-compliant type hints, others permit or even require callers to annotate callables with PEP-noncompliant type hints. Runtime type checkers that do so violate:

- [PEP 561 -- Distributing and Packaging Type Information][PEP 561], which requires callables to be annotated with strictly PEP-compliant type hints. Packages violating [PEP 561] even once cannot be type-checked with [static type checkers](#static-type-checkers) (e.g., [mypy]), unless each such violation is explicitly ignored with a checker-specific filter (e.g., with a [mypy]-specific inline type comment).

- [PEP 563 -- Postponed Evaluation of Annotations][PEP 563], which explicitly deprecates PEP-noncompliant type hints:

  > With this in mind, **uses for annotations incompatible with the aforementioned PEPs** *\[i.e., PEPs 484, 544, 557, and 560\]* **should be considered deprecated.**

## Runtime Data Validators

**Runtime data validators** (i.e., third-party Python packages dynamically validating callables decorated by caller-defined contracts, constraints, and validation routines at runtime) include:

- [PyContracts].
- [contracts].
- [covenant].
- [dpcontracts].
- [icontract].
- [pcd].
- [pyadbc].

Unlike both [runtime type checkers](#runtime-type-checkers) and [static type checkers](#static-type-checkers), most runtime data validators do *not* require callables to be annotated by type hints. Like some [runtime type checkers](#runtime-type-checkers), most runtime data validators do *not* comply with community standards but instead require callers to either:

- Decorate callables with package-specific decorators.
- Annotate callables with package-specific and thus PEP-noncompliant type hints.

## Static Type Checkers

**Static type checkers** (i.e., third-party tooling validating Python callable and/or variable types across an application stack at static analysis time rather than Python runtime) include:

- [mypy], Python's official static type checker.
- [Pyre], published by Meta. <sup>...yah.</sup>
- [pyright], published by Microsoft.
- [pytype], published by Google.

[^1]: The *time multiplier* column approximates **how much slower on average than** beartype **that checker is** as [timed by our profile suite](math.md#beartype-timings). A time multiplier of:

    - "1" means that checker is approximately as fast as beartype, which means that checker is probably beartype itself.
    - "20" means that checker is approximately twenty times slower than beartype on average.
