#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **standard Python library decorators** (i.e., low-level private
decorators internally called by the high-level public :mod:`beartype` decorator
to decorate low-level objects created and returned by decorators defined by
modules in Python's standard library).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorWrappeeException
from beartype._data.typing.datatyping import BeartypeableT
from beartype._util.api.standard.utilfunctools import (
    is_func_functools_lru_cache)
from beartype._util.api.standard.utilwarnings import (
    is_func_warnings_deprecated,
    make_func_warnings_deprecated,
)
from beartype._util.func.utilfuncwrap import unwrap_func_once
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_13
from collections.abc import Callable
from functools import lru_cache

# ....................{ DECORATORS ~ contextlib            }....................
def beartype_func_contextlib_contextmanager(
    func: BeartypeableT, func_contextmanager: Callable, **kwargs) -> (
    BeartypeableT):
    '''
    Decorate the passed :mod:`contextlib`-based **isomorphic decorator closure**
    (i.e., closure created and returned by either the standard
    :func:`contextlib.asynccontextmanager` or :func:`contextlib.contextmanager`
    decorator such that that closure isomorphically preserves both the number
    and types of all passed parameters and returns by accepting only a variadic
    positional argument and variadic keyword argument) with dynamically
    generated type-checking.

    Parameters
    ----------
    func : BeartypeableT
        Decorator closure to be decorated by :func:`beartype.beartype`.
    func_contextmanager : Callable
        Either:

        * If this context manager is a
          :func:`contextlib.asynccontextmanager`-based isomorphic decorator
          closure, :func:`contextlib.asynccontextmanager`.
        * Else, this context manager is a
          :func:`contextlib.contextmanager`-based isomorphic decorator closure.
          In this case, :func:`contextlib.contextmanager`.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`beartype._decor._nontype.decornontype.beartype_nontype` decorator
    internally called by this higher-level decorator on the pure-Python function
    encapsulated in this descriptor.

    Returns
    -------
    BeartypeableT
        New pure-Python callable wrapping this context manager with
        type-checking.
    '''
    assert callable(func_contextmanager), (
        f'{repr(func_contextmanager)} uncallable.')
    # print(f'Redecorating {repr(func_contextmanager)}-decorated callable {repr(func)}...')

    # Avoid circular import dependencies.
    from beartype._decor._nontype.decornontype import beartype_nontype

    # Original pure-Python generator factory function decorated by either the
    # @contextlib.asynccontextmanager or @contextlib.contextmanager decorator.
    generator = unwrap_func_once(func)  # type: ignore[arg-type]

    # Decorate this generator factory function with type-checking.
    generator_checked = beartype_nontype(obj=generator, **kwargs)

    # Re-decorate this generator factory function by the same decorator.
    generator_checked_contextmanager = func_contextmanager(generator_checked)

    # Return this context manager.
    return generator_checked_contextmanager  # type: ignore[return-value]

# ....................{ DECORATORS ~ functools             }....................
def beartype_func_functools_lru_cache(
    pseudofunc: BeartypeableT, **kwargs) -> BeartypeableT:
    '''
    Monkey-patch the passed :func:`functools.lru_cache`-memoized
    **pseudo-callable** (i.e., low-level C-based callable object both created
    and returned by the standard :func:`functools.lru_cache` decorator) with
    dynamically generated type-checking.

    Parameters
    ----------
    pseudofunc : BeartypeableT
        Pseudo-callable to be monkey-patched by :func:`beartype.beartype`.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`beartype._decor._nontype.decornontype.beartype_nontype` decorator
    internally called by this higher-level decorator on the pure-Python function
    encapsulated in this descriptor.

    Returns
    -------
    BeartypeableT
        New pseudo-callable monkey-patched by :func:`beartype.beartype`.
    '''

    # Avoid circular and third-party import dependencies.
    from beartype._decor._nontype.decornontype import beartype_nontype

    # If this pseudo-callable is *NOT* actually a @functools.lru_cache-memoized
    # callable, raise an exception.
    if not is_func_functools_lru_cache(pseudofunc):  # pragma: no cover
        raise BeartypeDecorWrappeeException(
            f'@functools.lru_cache-memoized callable {repr(pseudofunc)} not  '
            f'decorated by @functools.lru_cache.'
        )
    # Else, this pseudo-callable is a @functools.lru_cache-memoized callable.

    # Original pure-Python callable decorated by @functools.lru_cache.
    func = unwrap_func_once(pseudofunc)  # pyright: ignore

    # Decorate that callable with type-checking.
    func_checked = beartype_nontype(obj=func, **kwargs)

    # Dictionary mapping the names to values of all parameters originally passed
    # by the caller to that decorator, enabling the re-decoration of that
    # callable. Thankfully, that decorator preserves these parameters via the
    # decorator-specific "cache_parameters" instance variable whose value is a
    # bizarre argumentless lambda function (...for unknown reasons that are
    # probably indefensible) creating and returning this dictionary: e.g.,
    #     >>> from functools import lru_cache
    #     >>> @lru_cache(maxsize=3)
    #     ... def plus_one(n: int) -> int: return n +1
    #     >>> plus_one.cache_parameters()
    #     {'maxsize': 3, 'typed': False}
    lru_cache_kwargs = pseudofunc.cache_parameters()  # type: ignore[attr-defined]

    # Closure defined and returned by the @functools.lru_cache decorator when
    # passed these keyword parameters.
    lru_cache_configured = lru_cache(**lru_cache_kwargs)

    # Re-decorate that callable by @functools.lru_cache by the same parameters
    # originally passed by the caller to that decorator.
    pseudofunc_checked = lru_cache_configured(func_checked)

    # Return that new pseudo-callable.
    return pseudofunc_checked  # pyright: ignore

# ....................{ DECORATORS ~ warnings              }....................
def beartype_func_warnings_deprecated(
    func: BeartypeableT, **kwargs) -> BeartypeableT:
    '''
    Decorate the passed :func:`warnings.deprecated`-based **isomorphic decorator
    closure** (i.e., closure created and returned by the standard
    :func:`warnings.deprecated` decorator such that that closure isomorphically
    preserves both the number and types of all passed parameters and returns by
    accepting only a variadic positional argument and variadic keyword argument)
    with dynamically generated type-checking.

    Parameters
    ----------
    func : BeartypeableT
        Decorator closure to be decorated by :func:`beartype.beartype`.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`beartype._decor._nontype.decornontype.beartype_nontype` decorator
    internally called by this higher-level decorator on the pure-Python function
    encapsulated in this descriptor.

    Returns
    -------
    BeartypeableT
        New pure-Python callable wrapping this context manager with
        type-checking.
    '''

    # This is ugly, but I'm not sure how else to do it without trying to import things
    # or perform some other environmental inspection nonsense? See also a similar
    # approach in the sister site in utilwarnings.py.
    deprecated_source = "warnings" if IS_PYTHON_AT_LEAST_3_13 else "typing_extensions"
    # print(f"Redecorating @{deprecated_source}.deprecated-decorated callable {repr(func)}...")

    # Avoid circular and third-party import dependencies.
    from beartype._decor._nontype.decornontype import beartype_nontype

    # If this callable is *NOT* a closure created and returned by the
    # @warnings.deprecated decorator, raise an exception.
    if not is_func_warnings_deprecated(func):  # type: ignore[arg-type]
        raise BeartypeDecorWrappeeException(  # pragma: no cover
            f"@{deprecated_source}.deprecated-decorated callable {repr(func)} not  "
            f"decorated by @{deprecated_source}.deprecated."
        )
    # Else, this callable is a closure created and returned by the
    # @warnings.deprecated decorator.

    # Original pure-Python callable decorated by @warnings.deprecated.
    func_wrapped = unwrap_func_once(func)  # type: ignore[arg-type]

    # Decorate that callable with type-checking.
    func_wrapped_checked = beartype_nontype(obj=func_wrapped, **kwargs)

    # @warnings.deprecated decorator initialized with all parameters originally
    # passed to the passed @warnings.deprecated-based closure.
    deprecated_configured = make_func_warnings_deprecated(
        func=func, exception_cls=BeartypeDecorWrappeeException)  # type: ignore[arg-type]

    # Re-decorate that callable by @warnings.deprecated with the same parameters
    # originally passed by the caller to that decorator.
    deprecated_checked = deprecated_configured(func_wrapped_checked)

    # Return that new callable.
    return deprecated_checked  # type: ignore[return-value]
