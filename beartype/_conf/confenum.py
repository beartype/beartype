#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **configuration enumerations** (i.e., public enumerations whose members
may be passed as initialization-time parameters to the
:meth:`beartype._conf.confmain.BeartypeConf.__init__` constructor to configure
:mod:`beartype` with optional runtime type-checking behaviours).

Most of the public attributes defined by this private submodule are explicitly
exported to external users in our top-level :mod:`beartype.__init__` submodule.
This private submodule is *not* intended for direct importation by downstream
callers.
'''

# ....................{ IMPORTS                            }....................
from enum import (
    Enum,
    IntEnum,
    auto as next_enum_member_value,
    unique as die_unless_enum_member_values_unique,
)

# ....................{ ENUMERATIONS                       }....................
@die_unless_enum_member_values_unique
class BeartypeDecorationPosition(Enum):
    '''
    Enumeration of all kinds of **import hook decorator positions** (i.e.,
    competing locations to which the :func:`beartype.beartype` decorator will be
    implicitly injected into existing chains of one or more decorators
    decorating classes and callables defined by modules imported under
    :mod:`beartype.claw` import hooks, each with concomitant tradeoffs with
    respect to decorator interoperability and quality assurance).

    Attributes
    ----------
    FIRST : EnumMemberType
        **First (i.e., bottom-most) decorator position**, configuring
        :mod:`beartype.claw` import hooks to unintelligently inject the
        :func:`beartype.beartype` decorator as the first (i.e., bottom-most)
        decorator in relevant decorator chains.

        This position is intentionally *not* the default. By ignoring standard
        decorators, this position **violates PEP standards.** Notably, this
        position ignores:

        * The :pep:`484`-compliant :func:`typing.no_type_check` decorator, which
          then erroneously instructs the :func:`beartye.beartype` decorator to
          type-check classes and callables that should *not* be type-checked.
        * The :pep:`557`-compliant :func:`dataclasses.dataclass` decorator,
          which then prevents the :func:`beartye.beartype` decorator from
          type-checking dataclasses.
        * Explicitly configured :func:`beartype.beartype` decorators (e.g.,
          ``@beartype(conf=BeartypeConf(...))``), which then instructs
          :func:`beartye.beartype` to type-check classes and callables under
          differing configurations.

        When this position is used, implicit :func:`beartype.beartype`
        decorators injected by :mod:`beartype.claw` import hooks assume
        precedence over *all* other decorators (including those listed above),
        with predictably catastrophic results. Since this is almost never what
        anyone wants, this is *not* the default: e.g.,

        .. code-block:: python

           # Registering this import hook...
           from beartype import beartype, BeartypeConf, BeartypeDecorationPosition
           from beartype.claw import beartype_this_package
           beartype_this_package(conf=BeartypeConf(
               claw_decoration_position_types=BeartypeDecorationPosition.FIRST))

           # ...transforms chains of class decorators like this...
           from dataclasses import dataclass
           @beartype(conf=BeartypeConf(is_debug=True))
           @dataclass
           class ClassyData(object):
               integral_datum: int

           # ...into chains of class decorators like this.
           from dataclasses import dataclass
           @beartype(conf=BeartypeConf(is_debug=True))  # <-- *IGNORED*
           @dataclass  # <-- *IGNORED* by the @beartype decorator injected below
           @beartype   # <-- @beartype now ignores all of the above decorators!!
           class ClassyData(object):
               integral_datum: int

        In the above example, the default :func:`beartype.beartype` decorator
        injected by the :func:`beartype.claw.beartype_this_package` silently
        fails to type-check the :func:`dataclasses.dataclass` decorator and then
        overwrites the ``@beartype(conf=BeartypeConf(is_debug=True))`` decorator
        manually configured by the author of that third-party package.
        Consequently, caveats apply to usage of this position:

        * This position should only be applied to codebases that avoid
          explicitly decorating classes and/or callables with standard
          decorators, including:

          * The :pep:`484`-compliant :func:`typing.no_type_check` decorator.
          * The :pep:`557`-compliant :func:`dataclasses.dataclass` decorator.
          * The :func:`beartype.beartype` decorator itself.

        * Equivalently, this position should only be applied to codebases that
          implicitly decorate *all* classes and callables with
          :mod:`beartype.claw` import hooks.
        * Equivalently, if a codebase explicitly decorates even a single class
          or callable with the :func:`typing.no_type_check`,
          :func:`dataclasses.dataclass`, or :func:`beartype.beartype`
          decorators, this position should *not* be used.
        * Consequently, this position should *not* be applied to other packages
          outside your direct control.
        * In particular, this position should *not* be applied to all packages
          with the :func:`beartype.claw.beartype_all` import hook: e.g.,

          .. code-block:: python

             # Never do this. Srsly. Never do this. Srsly! Read this and weep.
             from beartype import BeartypeConf, BeartypeDecorationPosition
             from beartype.claw import beartype_all
             beartype_all(conf=BeartypeConf(
                 claw_decoration_position_types=BeartypeDecorationPosition.FIRST))
    LAST : EnumMemberType
        **Last (i.e., top-most) decorator position**, configuring
        :mod:`beartype.claw` import hooks to unintelligently inject the
        :func:`beartype.beartype` decorator as the last (i.e., top-most)
        decorator in relevant decorator chains.

        This position is intentionally *not* the default. By ignoring
        **decorator-hostile decorators** (i.e., decorators hostile to other
        decorators by prematurely terminating decorator chaining such that *no*
        decorators may appear above those decorators in any chain of one or more
        decorators), this position **breaks third-party package compatibility.**
        This position breaks compatibility with popular decorator-hostile
        decorators from such third-party packages as:

        * Celery_, including the `celery.Celery.task` decorator.
        * FastMCP_, including the `mcp.tool` decorator.
        * LangChain_, including the `langchain_core.runnables.chain` decorator.
        * Typer_, including the `typer.Typer.command` decorator.

        This position is both more and less fragile than the :attr:`.FIRST`
        position. Neither is intrinsically better or worse than the other. Both
        demonstrate advantages in some use cases and disadvantages in others.
        Specifically:

        * The :attr:`.FIRST` position is compatible with decorator-hostile
          decorators (like those exhibited above), unlike this position.
        * This position is compatible with standard decorators (like those
          exhibited above) required for **PEP-compliance,** unlike the
          :attr:`.FIRST` position.

        This position, for example, respects explicitly configured
        :func:`beartype.beartype` decorations (e.g.,
        ``@beartype(conf=BeartypeConf(...))``). When this position is used,
        explicit :func:`beartype.beartype` decorations assume precedence over
        implicit :func:`beartype.beartype` decorations injected by
        :mod:`beartype.claw` import hooks: e.g.,

        .. code-block:: python

           # Registering this import hook...
           from beartype import beartype, BeartypeConf, BeartypeDecorationPosition
           from beartype.claw import beartype_this_package
           beartype_this_package(conf=BeartypeConf(
               claw_decoration_position_funcs=BeartypeDecorationPosition.LAST))

           # ...transforms chains of function decorators like this...
           from functools import cache
           @cache
           @beartype(conf=BeartypeConf(is_debug=True))
           def chad_func() -> int:
               return 42

           # ...into chains of function decorators like this.
           from functools import cache
           @beartype  # <-- @beartype decorates last rather than first! \\o/
           @cache
           @beartype(conf=BeartypeConf(is_debug=True))
           def chad_func() -> int:
               return 42

        In the above example, the default :func:`beartype.beartype` decorator
        injected by the :func:`beartype.claw.beartype_this_package` import hook
        is silently ignored in favour of the non-default
        ``@beartype(conf=BeartypeConf(is_debug=True))`` decorator manually
        configured by the author of that third-party package.
    LAST_BEFORELIST : EnumMemberType
        **Beforelist-moderated last (i.e., top-most) decorator position**,
        configuring :mod:`beartype.claw` import hooks to intelligently inject
        the :func:`beartype.beartype` decorator ideally as the last (i.e.,
        top-most) decorator in relevant decorator chains.

        This position is algorithmically subject to the **beforelist** (i.e.,
        user-configurable data structures deciding where the
        :func:`beartype.beartype` decorator should be applied in chains of one
        or more third-party decorators decorating callables and types). Notably,
        this position positions the :func:`beartype.beartype` decorator:

        * *Below* all **decorator-hostile decorators** (i.e., third-party
          decorators hostile to other decorators by prematurely terminating
          decorator chaining such that *no* decorators may appear above those
          decorators in any chain of one or more decorators). The beforelist
          configures which decorators are considered to be "decorator-hostile."
          Since decorator-hostile decorators are hostile to
          :func:`beartype.beartype` as well, :func:`beartype.beartype` *cannot*
          appear above these decorators.
        * *Above* all other decorators. This position thus respects standard
          decorators required for PEP-compliance, including:

          * The :pep:`484`-compliant :func:`typing.no_type_check` decorator.
          * The :pep:`557`-compliant :func:`dataclasses.dataclass` decorator.
          * Explicitly configured :func:`beartype.beartype` decorators (e.g.,
            ``@beartype(conf=BeartypeConf(...))``).

        This position is the default. By respecting rather than ignoring
        decorator-hostile decorators, this position is innately compatible with
        third-party packages. Likewise, by respecting rather than ignoring
        standard decorators, this position is innately compatible with Python's
        core typing standards.
    '''

    FIRST = next_enum_member_value()
    LAST = next_enum_member_value()
    LAST_BEFORELIST = next_enum_member_value()


@die_unless_enum_member_values_unique
class BeartypeStrategy(Enum):
    '''
    Enumeration of all kinds of **type-checking strategies** (i.e., competing
    procedures for type-checking objects passed to or returned from
    :func:`beartype.beartype`-decorated callables, each with concomitant
    tradeoffs with respect to runtime complexity and quality assurance).

    Strategies are intentionally named according to `conventional Big O
    notation <Big O_>`__ (e.g., :attr:`BeartypeStrategy.On` enables the
    ``O(n)`` strategy). Strategies are established per-decoration at the
    fine-grained level of callables decorated by the :func:`beartype.beartype`
    decorator by setting the :attr:`beartype.BeartypeConf.strategy` parameter of
    the :class:`beartype.BeartypeConf` object passed as the optional ``conf``
    parameter to that decorator.

    Strategies enforce their corresponding runtime complexities (e.g., ``O(n)``)
    across *all* type-checks performed for callables enabling those strategies.
    For example, a callable configured by the :attr:`BeartypeStrategy.On`
    strategy will exhibit linear ``O(n)`` complexity as its overhead for
    type-checking each nesting level of each container passed to and returned
    from that callable.

    .. _Big O:
       https://en.wikipedia.org/wiki/Big_O_notation

    Attributes
    ----------
    O0 : EnumMemberType
        **No-time strategy** (i.e, disabling type-checking for a decorated
        callable by reducing :func:`beartype.beartype` to the identity
        decorator for that callable). Although seemingly useless, this strategy
        enables users to selectively blacklist (prevent) callables from being
        type-checked by our as-yet-unimplemented import hook. When implemented,
        that hook will type-check all callables within a package or module
        *except* those callables explicitly decorated by this strategy.
    O1 : EnumMemberType
        **Constant-time strategy** (i.e., the default ``O(1)`` strategy,
        type-checking a single randomly selected item of each container). As the
        default, this strategy need *not* be explicitly enabled.
    Ologn : EnumMemberType
        **Logarithmic-time strategy** (i.e., the ``O(log n)`` strategy,
        type-checking a randomly selected number of items ``log(len(obj))`` of
        each container ``obj``). This strategy is **currently unimplemented.**
        (*To be implemented by a future beartype release.*)
    On : EnumMemberType
        **Linear-time strategy** (i.e., the ``O(n)`` strategy, type-checking
        *all* items of a container). This strategy is **currently
        unimplemented.** (*To be implemented by a future beartype release.*)
    '''

    O0 = next_enum_member_value()
    O1 = next_enum_member_value()
    Ologn = next_enum_member_value()
    On = next_enum_member_value()


@die_unless_enum_member_values_unique
class BeartypeViolationVerbosity(IntEnum):
    '''
    Enumeration of all kinds of **violation verbosities** (i.e., positive
    integers in the inclusive range ``[1, 5]`` governing the verbosity of
    exception messages raised by type-checking wrappers generated by the
    :func:`beartype.beartype` decorator when either receiving parameters *or*
    returning values violating their annotated type hints).

    Verbosities transparently reduce to integers and can thus be used wherever
    integers are used (e.g., ``BeartypeViolationVerbosity.DEFAULT + 1`` is the next
    level of verbosity beyond that of the default). Verbosities are established
    per-decoration at the fine-grained level of callables decorated by the
    :func:`beartype.beartype` decorator by setting the
    :attr:`beartype.BeartypeConf.violation_verbosity` parameter of the
    :class:`beartype.BeartypeConf` object passed as the optional ``conf``
    parameter to that decorator.

    Attributes
    ----------
    MINIMAL : EnumMemberType
        **Minimal verbosity,** intended for end users potentially lacking core
        expertise in Python.
    DEFAULT : EnumMemberType
        **Default verbosity,** intended for a general developer audience assumed
        to be fluent in Python.
    MAXIMAL : EnumMemberType
        **Maximum verbosity,** extending the default verbosity with additional
        contextual metadata intended for debugging violations. This includes:

        * A machine-readable representation of the beartype configuration under
          which the current violation occurred.
    '''

    MINIMAL = next_enum_member_value()
    DEFAULT = next_enum_member_value()
    MAXIMAL = next_enum_member_value()
