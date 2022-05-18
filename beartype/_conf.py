#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator configuration API** (i.e., enumerations, classes,
singletons, and other attributes enabling external callers to selectively
configure the :func:`beartype` decorator on a fine-grained per-decoration call
basis).

Most of the public attributes defined by this private submodule are explicitly
exported to external callers in our top-level :mod:`beartype.__init__`
submodule. This private submodule is *not* intended for direct importation by
downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeConfException
from beartype.typing import (
    TYPE_CHECKING,
    Dict,
)
from enum import (
    Enum,
    auto as next_enum_member_value,
    unique as die_unless_enum_member_values_unique,
)

# ....................{ ENUMERATIONS                      }....................
#FIXME: Document us up in "README.rst", please.
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
    fine-grained level of callables decorated by the :func: `beartype.beartype`
    decorator by either:

    * Calling a high-level convenience decorator establishing that strategy
      (e.g., :func:`beartype.conf.beartype_On`, enabling the ``O(n)`` strategy
      for all callables decorated by that decorator).
    * Setting the :attr:`BeartypeConfiguration.strategy` variable of the
      :attr:`BeartypeConfiguration` object passed as the optional ``conf``
      parameter to the lower-level core :func: `beartype.beartype` decorator.

    Strategies enforce and guarantee their corresponding runtime complexities
    (e.g., ``O(n)``) across all type checks performed for all callables
    enabling those strategies. For example, a callable decorated with the
    :attr:`BeartypeStrategy.On` strategy will exhibit linear runtime complexity
    as its type-checking overhead.

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
        type-checking a single randomly selected item of each container). As
        the default, this strategy need *not* be explicitly enabled.
    Ologn : EnumMemberType
        **Logarithmic-time strategy** (i.e., the ``O(log n)` strategy,
        type-checking a randomly selected number of items ``log(len(obj))`` of
        each container ``obj``). This strategy is **currently unimplemented.**
        (*To be implemented by a future beartype release.*)
    On : EnumMemberType
        **Linear-time strategy** (i.e., an ``O(n)`` strategy, type-checking
        *all* items of a container). This strategy is **currently
        unimplemented.** (*To be implemented by a future beartype release.*)
    '''

    O0 = next_enum_member_value()
    O1 = next_enum_member_value()
    Ologn = next_enum_member_value()
    On = next_enum_member_value()

# ....................{ CLASSES                           }....................
#FIXME: Document us up in "README.rst", please.
#FIXME: Refactor to use @dataclass.dataclass once we drop Python 3.7 support.
class BeartypeConf(object):
    '''
    **Beartype configuration** (i.e., self-caching dataclass encapsulating all
    flags, options, settings, and other metadata configuring each granular
    decoration of a callable or class by the :func:`beartype.beartype`
    decorator).

    Attributes
    ----------
    _is_debug : bool, optional
        ``True`` only if the :func:`beartype.beartype` decorator prints to
        standard output the definition (including both signature and body) of
        the type-checking wrapper function dynamically generated for the
        decorated callable. This is mostly intended for internal debugging,
        documentation, and optimization purposes.
    _strategy : BeartypeStrategy, optional
        **Type-checking strategy** (i.e., :class:`BeartypeStrategy` enumeration
        member) with which to implement all type-checks in the wrapper function
        dynamically generated by the :func:`beartype.beartype` decorator for
        the decorated callable.
    '''

    # ..................{ CLASS VARIABLES                   }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize this slots list with the implementations of:
    # * The __new__() dunder method.
    # * The __eq__() dunder method.
    # * The __hash__() dunder method.
    # * The __repr__() dunder method.
    # CAUTION: Subclasses declaring uniquely subclass-specific instance
    # variables *MUST* additionally slot those variables. Subclasses violating
    # this constraint will be usable but unslotted, which defeats our purposes.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_is_debug',
        '_strategy',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        _is_debug: bool
        _strategy: BeartypeStrategy

    # ..................{ INSTANTIATORS                     }..................
    # Note that this __new__() dunder method implements the superset of the
    # functionality typically implemented by the __init__() dunder method. Due
    # to Python instantiation semantics, the __init__() dunder method is
    # intentionally left undefined. Why? Because Python unconditionally invokes
    # __init__() if defined, even when the initialization performed by that
    # __init__() has already been performed for the cached instance returned by
    # __new__(). In short, __init__() and __new__() are largely mutually
    # exclusive; one typically defines one or the other but *NOT* both.

    def __new__(
        cls,

        # Optional flexible parameters.
        strategy: BeartypeStrategy = BeartypeStrategy.O1,

        # Optional keyword-only parameters.
        *,
        is_debug: bool = False,
    ) -> 'BeartypeConf':
        '''
        Instantiate this configuration if needed (i.e., if *no* prior
        configuration with these same parameters was previously instantiated)
        *or* reuse that previously instantiated configuration otherwise.

        This dunder methods guarantees beartype configurations to be memoized:

        .. code-block:: python

           >>> from beartype import BeartypeConf
           >>> BeartypeConf() is BeartypeConf()
           True

        This memoization is *not* merely an optimization. The
        :func:`beartype.beartype` decorator internally memoizes the private
        closure it creates and returns on the basis of this configuration,
        which *must* thus also be memoized.

        Parameters
        ----------
        is_debug : bool, optional
            ``True`` only if the :func:`beartype.beartype` decorator prints to
            standard output the definition (including signature and body) of
            the type-checking wrapper function dynamically generated for the
            decorated callable. This is mostly intended for internal debugging,
            documentation, and optimization purposes. Defaults to ``False``.
        strategy : BeartypeStrategy, optional
            **Type-checking strategy** (i.e., :class:`BeartypeStrategy`
            enumeration member) with which to implement all type-checks in the
            wrapper function dynamically generated by the :func:
            `beartype.beartype` decorator for the decorated callable. Defaults
            to :attr: `BeartypeStrategy.O1`, the constant-time strategy.

        Returns
        ----------
        BeartypeConf
            Beartype configuration memoized with these parameters.

        Raises
        ----------
        :exc:`BeartypeConfException`
            If either:

            * ``is_debug`` is *not* a boolean.
            * ``strategy`` is *not* a :class:`BeartypeStrategy` enumeration
              member.
        '''

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize this logic with BeartypeConf.__hash__().
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Hash of these parameters.
        #
        # Note this logic inlines the body of the BeartypeConf.__hash__()
        # dunder method, maximizing efficiency (the entire point of caching) by
        # avoiding the cost of an additional method call both here and (more
        # importantly) in BeartypeConf.__hash__(). See that method for details.
        BEARTYPE_CONF_HASH = hash((
            is_debug,
            strategy,
        ))

        # If this method has already instantiated a configuration with these
        # parameters, return that configuration for consistency and efficiency.
        if BEARTYPE_CONF_HASH in _BEARTYPE_CONF_HASH_TO_CONF:
            return _BEARTYPE_CONF_HASH_TO_CONF[BEARTYPE_CONF_HASH]
        # Else, this method has yet to instantiate a configuration with these
        # parameters. In this case, do so below (and cache that configuration).

        # If this boolean is *NOT* actually a boolean, raise an exception.
        if not isinstance(is_debug, bool):
            raise BeartypeConfException(
                f'Beartype configuration setting "is_debug" '
                f'value {repr(is_debug)} not boolean.'
            )
        # Else, this boolean is actually a boolean.
        #
        # If this enumeration member is *NOT* actually an enumeration member,
        # raise an exception.
        elif not isinstance(strategy, BeartypeStrategy):
            raise BeartypeConfException(
                f'Beartype configuration setting "strategy" value '
                f'{repr(strategy)} not "BeartypeStrategy" enumeration member.'
            )
        # Else, this enumeration member is actually an enumeration member.

        # Instantiate a new configuration of this type.
        self = super().__new__(cls)

        # Classify all passed parameters with this configuration.
        self._is_debug = is_debug
        self._strategy = strategy

        # Cache this configuration.
        _BEARTYPE_CONF_HASH_TO_CONF[BEARTYPE_CONF_HASH] = self

        # Return this configuration.
        return self

    # ..................{ PROPERTIES                        }..................
    # Read-only public properties effectively prohibiting mutation of their
    # underlying private attributes.

    @property
    def is_debug(self) -> bool:
        '''
        ``True`` only if the :func:`beartype.beartype` decorator prints to
        standard output the definition (including both signature and body) of
        the type-checking wrapper function dynamically generated for the
        decorated callable.

        This is mostly intended for internal debugging, documentation, and
        optimization purposes.
        '''

        return self._is_debug


    @property
    def strategy(self) -> BeartypeStrategy:
        '''
        **Type-checking strategy** (i.e., :class:`BeartypeStrategy`
        enumeration member) with which to implement all type-checks in the
        wrapper function dynamically generated by the :func:
        `beartype.beartype` decorator for the decorated callable.
        '''

        return self._strategy

    # ..................{ DUNDERS                           }..................
    def __eq__(self, other: object) -> bool:
        '''
        **Beartype configuration equality comparator.**

        Parameters
        ----------
        other : object
            Arbitrary object to be compared for equality against this
            configuration.

        Returns
        ----------
        Union[bool, type(NotImplemented)]
            Either:

            * If this other object is also a beartype configuration, either:

              * If these configurations share the same settings, ``True``.
              * Else, ``False``.

            * Else, ``NotImplemented``.

        See Also
        ----------
        :func:`_hash_beartype_conf`
            Further details.
        '''

        # If this other object is also a beartype configuration...
        if isinstance(other, BeartypeConf):
            # Return true only if these configurations share the same settings.
            return (
                self._is_debug == other._is_debug and
                self._strategy == other._strategy
            )
        # Else, this other object is *NOT* also a beartype configuration.

        # In this case, return the standard singleton informing Python that
        # this equality comparator fails to support this comparison.
        return NotImplemented


    def __hash__(self) -> int:
        '''
        **Hash** (i.e., non-negative integer quasi-uniquely identifying this
        beartype configuration with respect to hashable container membership).

        Returns
        ----------
        int
            Hash of this configuration.
        '''

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize this logic with BeartypeConf.__new__().
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Return the hash of a tuple containing these parameters in an
        # arbitrary (albeit well-defined) order.
        #
        # Note this has been profiled to be the optimal means of hashing object
        # attributes in Python, where "optimal" means:
        # * Optimally fast. CPython in particular optimizes the creation and
        #   garbage collection of "small" tuples, where "small" is ill-defined
        #   but almost certainly applies here.
        # * Optimally uniformly distributed, thus minimizing the likelihood of
        #   expensive hash collisions.
        return hash((
            self._is_debug,
            self._strategy,
        ))


    def __repr__(self) -> str:
        '''
        **Beartype configuration representation** (i.e., machine-readable
        string which, when dynamically evaluated as code, restores access to
        this exact configuration object).

        Returns
        ----------
        str
            Representation of this configuration.
        '''

        return (
            f'{self.__class__.__name__}(\n'
            f'    is_debug={repr(self._is_debug)},\n'
            f'    strategy={repr(self._strategy)},\n'
            f')'
        )

# ....................{ PRIVATE ~ globals                 }....................
_BEARTYPE_CONF_HASH_TO_CONF: Dict[int, BeartypeConf] = {}
'''
Non-thread-safe **beartype configuration cache** (i.e., dictionary mapping from
the hash of each set of parameters accepted by a prior call of the
:meth:`BeartypeConf.__new__` instantiator to the unique :class:`BeartypeConf`
instance instantiated by that call).

Note that this cache is technically non-thread-safe. Since this cache is only
used as a memoization optimization, the only harmful consequences of a race
condition between threads contending over this cache is a mildly inefficient
(but otherwise harmless) repeated re-memoization of duplicate configurations.
'''
