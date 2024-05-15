#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **configuration enumerations** (i.e., public enumerations whose members
may be passed as initialization-time parameters to the
:meth:`beartype._conf.confcls.BeartypeConf.__init__` constructor to configure
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
        :mod:`beartype.claw` import hooks to inject the
        :func:`beartype.beartype` decorator as the first (i.e., bottom-most)
        decorator in relevant decorator chains: e.g.,

        .. code-block:: python

           # Registering this import hook...
           from beartype import BeartypeConf, BeartypeDecorationPosition
           from beartype.claw import beartype_this_package
           beartype_this_package(conf=BeartypeConf(
               claw_decoration_position_types=BeartypeDecorationPosition.FIRST))

           # ...transforms chains of class decorators like this...
           from dataclasses import dataclass
           @dataclass
           class ClassyData(object):
               integral_datum: int

           # ...into chains of class decorators like this.
           from beartype import beartype
           from dataclasses import dataclass
           @dataclass
           @beartype  # <-- @beartype decorates first rather than last! \\o/
           class ClassyData(object):
               integral_datum: int

    LAST : EnumMemberType
        **Last (i.e., top-most) decorator position**, configuring
        :mod:`beartype.claw` import hooks to inject the
        :func:`beartype.beartype` decorator as the last (i.e., top-most)
        decorator in relevant decorator chains. As the default, this position
        need *not* be explicitly passed: e.g.,

        .. code-block:: python

           # Registering this import hook...
           from beartype import BeartypeConf, BeartypeDecorationPosition
           from beartype.claw import beartype_this_package
           beartype_this_package(conf=BeartypeConf(
               claw_decoration_position_funcs=BeartypeDecorationPosition.FIRST))

           # ...transforms chains of function decorators like this...
           from functools import cache
           @cache
           def chad_func() -> int:
               return 42

           # ...into chains of function decorators like this.
           from beartype import beartype
           from functools import cache
           @cache
           @beartype  # <-- @beartype decorates first rather than last! \\o/
           def chad_func() -> int:
               return 42
    '''

    FIRST = next_enum_member_value()
    LAST = next_enum_member_value()


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
