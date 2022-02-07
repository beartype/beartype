#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Public beartype decorator.**

This private submodule defines the core :func:`beartype` decorator, which the
:mod:`beartype.__init__` submodule then imports for importation as the public
:mod:`beartype.beartype` decorator by downstream callers -- completing the
virtuous cycle of code life.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeConfException
from beartype.typing import (
    TYPE_CHECKING,
    Dict,
    Optional,
    Union,
)
from beartype._data.datatyping import (
    BeartypeConfedDecorator,
    BeartypeableT,
)
from beartype._decor.conf import (
    BeartypeConf,
    BeartypeStrategy,
)
from beartype._decor._core import beartype_args_mandatory

# Intentionally import the standard mypy-friendly @typing.overload decorator
# rather than a possibly mypy-unfriendly @beartype.typing.overload decorator --
# which, in any case, would be needlessly inefficient and thus bad.
from typing import overload

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ OVERLOADS                         }....................
# Declare PEP 484-compliant overloads to avoid breaking downstream code
# statically type-checked by a static type checker (e.g., mypy). The concrete
# @beartype decorator declared below is permissively annotated as returning a
# union of multiple types desynchronized from the types of the passed arguments
# and thus fails to accurately convey the actual public API of that decorator.
# See also: https://www.python.org/dev/peps/pep-0484/#function-method-overloading
@overload
def beartype(obj: BeartypeableT) -> BeartypeableT: ...
@overload
def beartype(*, conf: BeartypeConf) -> BeartypeConfedDecorator: ...

# ....................{ DECORATORS                        }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Synchronize the signature of this decorator with the identity
# decorator redeclared below.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def beartype(
    # Optional positional or keyword parameters.
    obj: Optional[BeartypeableT] = None,

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BeartypeConf(),
) -> Union[BeartypeableT, BeartypeConfedDecorator]:
    '''
    Decorate the passed **beartypeable** (i.e., pure-Python callable or class)
    with optimal type-checking dynamically generated unique to that
    beartypeable under the passed beartype configuration.

    Specifically:

    * If the passed object is a callable, this decorator dynamically generates
      and returns a **runtime type-checker** (i.e., pure-Python function
      validating all parameters and returns of all calls to the passed
      pure-Python callable against all PEP-compliant type hints annotating
      those parameters and returns). The type-checker returned by this
      decorator is:

      * Optimized uniquely for the passed callable.
      * Guaranteed to run in ``O(1)`` constant-time with negligible constant
        factors.
      * Type-check effectively instantaneously.
      * Add effectively no runtime overhead to the passed callable.

    * If the passed object is a class, this decorator iteratively applies
      itself to all annotated methods of this class by dynamically wrapping
      each such method with a runtime type-checker (as described above).

    If optimizations are enabled by the active Python interpreter (e.g., due to
    option ``-O`` passed to this interpreter), this decorator silently reduces
    to a noop.

    Parameters
    ----------
    obj : Optional[BeartypeableT]
        **Beartypeable** (i.e., pure-Python callable or class) to be decorated.
        Defaults to ``None``, in which case this decorator is in configuration
        rather than decoration mode. In configuration mode, this decorator
        creates and returns an efficiently cached private decorator that
        generically applies the passed beartype configuration to any
        beartypeable object passed to that decorator. Look... It just works.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable or class). Defaults to
        ``BeartypeConf()``, the default beartype configuration.

    Returns
    ----------
    BeartypeableT
        Either:

        * If the passed object is a class, this existing class embellished with
          dynamically generated type-checking.
        * If the passed object is a callable, a new callable wrapping that
          callable with dynamically generated type-checking.

    Raises
    ----------
    BeartypeConfException
        If the passed configuration is *not* actually a configuration (i.e.,
        instance of the :class:`BeartypeConf` class).
    BeartypeDecorHintException
        If any annotation on this callable is neither:

        * A **PEP-compliant type** (i.e., instance or class complying with a
          PEP supported by :mod:`beartype`), including:

          * :pep:`484` types (i.e., instance or class declared by the stdlib
            :mod:`typing` module).

        * A **PEP-noncompliant type** (i.e., instance or class complying with
          :mod:`beartype`-specific semantics rather than a PEP), including:

          * **Fully-qualified forward references** (i.e., strings specified as
            fully-qualified classnames).
          * **Tuple unions** (i.e., tuples containing one or more classes
            and/or forward references).
    BeartypeDecorHintPep563Exception
        If :pep:`563` is active for this callable and evaluating a **postponed
        annotation** (i.e., annotation whose value is a string) on this
        callable raises an exception (e.g., due to that annotation referring to
        local state no longer accessible from this deferred evaluation).
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__beartype_``.
    BeartypeDecorWrappeeException
        If this callable is either:

        * Uncallable.
        * A class, which :mod:`beartype` currently fails to support.
        * A C-based callable (e.g., builtin, third-party C extension).
    BeartypeDecorWrapperException
        If this decorator erroneously generates a syntactically invalid wrapper
        function. This should *never* happen, but here we are, so this probably
        happened. Please submit an upstream issue with our issue tracker if you
        ever see this. (Thanks and abstruse apologies!)
    '''

    # If this configuration is *NOT* a configuration, raise an exception.
    if not isinstance(conf, BeartypeConf):
        raise BeartypeConfException(
            f'{repr(conf)} not beartype configuration.')
    # Else, this configuration is a configuration.

    # If passed an object to be decorated, this decorator is in decoration
    # rather than configuration mode. In this case, decorate this object with
    # type-checking configured by this configuration.
    #
    # Note this branch is typically *ONLY* entered when the "conf" parameter
    # is *NOT* explicitly passed and thus defaults to the default
    # configuration. While callers may technically run this decorator in
    # decoration mode with a non-default configuration, doing so would be both
    # highly irregular *AND* violate PEP 561-compliance by violating the
    # decorator overloads declared above. Nonetheless, we're largely permissive
    # here; callers that are doing this are sufficiently intelligent to be
    # trusted to violate PEP 561-compliance if they so choose. So... *shrug*
    if obj is not None:
        return beartype_args_mandatory(obj, conf)
    # Else, we were passed *NO* object to be decorated. In this case, this
    # decorator is in configuration rather than decoration mode.

    # Private decorator (possibly previously generated and cached by a prior
    # call to this decorator also in configuration mode) generically applying
    # this configuration to any beartypeable object passed to that decorator
    # if a prior call to this public decorator has already been passed the same
    # configuration (and thus generated and cached this private decorator) *OR*
    # "None" otherwise (i.e., if this is the first call to this public
    # decorator passed this configuration in configuration mode). Phew!
    beartype_confed_cached = _bear_conf_to_decor.get(conf)

    # If a prior call to this public decorator has already been passed the same
    # configuration (and thus generated and cached this private decorator),
    # return this private decorator for subsequent use in decoration mode.
    if beartype_confed_cached:
        return beartype_confed_cached
    # Else, this is the first call to this public decorator passed this
    # configuration in configuration mode.

    # If this configuration enables the no-time strategy performing *NO*
    # type-checking, define only the identity decorator reducing to a noop.
    if conf.strategy is BeartypeStrategy.O0:
        def beartype_confed(obj: BeartypeableT) -> BeartypeableT:
            '''
            Return the passed **beartypeable** (i.e., pure-Python callable or
            class) as is *without* type-checking that beartypeable under a
            beartype configuration enabling the **no-time strategy** (i.e.,
            :attr:`beartype.BeartypeStrategy.O0`) passed to a prior call to the
            :func:`beartype.beartype` decorator.

            Parameters
            ----------
            obj : BeartypeableT
                Beartypeable to be preserved as is.

            Returns
            ----------
            BeartypeableT
                This beartypeable unmodified.

            See Also
            ----------
            :func:`beartype.beartype`
                Further details.
            '''

            return obj
    # Else, this configuration enables a positive-time strategy performing at
    # least the minimal amount of type-checking. In this case, define a private
    # decorator generically applying this configuration to any beartypeable
    # object passed to this decorator.
    else:
        def beartype_confed(obj: BeartypeableT) -> BeartypeableT:
            '''
            Decorate the passed **beartypeable** (i.e., pure-Python callable or
            class) with optimal type-checking dynamically generated unique to
            that beartypeable under the beartype configuration passed to a
            prior call to the :func:`beartype.beartype` decorator.

            Parameters
            ----------
            obj : BeartypeableT
                Beartypeable to be decorated.

            Returns
            ----------
            BeartypeableT
                Either:

                * If the passed object is a class, this existing class
                  embellished with dynamically generated type-checking.
                * If the passed object is a callable, a new callable wrapping
                  that callable with dynamically generated type-checking.

            See Also
            ----------
            :func:`beartype.beartype`
                Further details.
            '''

            # Decorate this object with type-checking configured by this
            # configuration.
            return beartype_args_mandatory(obj, conf)

    # Cache this private decorator against this configuration.
    _bear_conf_to_decor[conf] = beartype_confed

    # Return this private decorator.
    return beartype_confed

# ....................{ OPTIMIZATION                      }....................
# If the active Python interpreter is either...
if (
    # Optimized (e.g., option "-O" was passed to this interpreter) *OR*...
    not __debug__ or
    # Running under an external static type checker -- in which case there is
    # no benefit to attempting runtime type-checking whatsoever...
    #
    # Note that this test is largely pointless. By definition, static type
    # checkers should *NOT* actually run any code -- merely parse and analyze
    # that code. Ergo, this boolean constant should *ALWAYS* be false from the
    # runtime context under which @beartype is only ever run. Nonetheless, this
    # test is only performed once per process and is thus effectively free.
    TYPE_CHECKING
):
# Then unconditionally disable @beartype-based type-checking across the entire
# codebase by reducing the @beartype decorator to the identity decorator.
# Ideally, this would have been implemented at the top rather than bottom of
# this submodule as a conditional resembling:
#     if __debug__:
#         def beartype(func: CallableTypes) -> CallableTypes:
#             return func
#         return
#
# Tragically, Python fails to support module-scoped "return" statements. *sigh*
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Synchronize the signature of this decorator with the actual
# decorator declared above.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def beartype(  # type: ignore[no-redef]
        obj: BeartypeableT,

        # Optional keyword-only parameters.
        *,
        conf: BeartypeConf = BeartypeConf(),
    ) -> BeartypeableT:
        '''
        Identity decorator.

        This decorator currently reduces to a noop, as the active Python
        interpreter is optimized (e.g., option ``-O`` was passed to this
        interpreter at execution time).
        '''

        return obj

# ....................{ SINGLETONS                        }....................
_bear_conf_to_decor: Dict[BeartypeConf, BeartypeConfedDecorator] = {}
'''
Non-thread-safe **beartype decorator cache.**

This cache is implemented as a singleton dictionary mapping from each
**beartype configuration** (i.e., self-caching dataclass encapsulating all
flags, options, settings, and other metadata configuring the current decoration
of the decorated callable or class) to the corresponding **configured beartype
decorator** (i.e., closure created and returned from the
:func:`beartype.beartype` decorator when passed a beartype configuration via
the optional ``conf`` parameter rather than an object to be decorated via
the optional ``obj`` parameter).

Caveats
----------
**This cache is not thread-safe.** Although rendering this cache thread-safe
would be trivial, doing so would needlessly reduce efficiency. This cache is
merely a runtime optimization and thus need *not* be thread-safe.
'''
