#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable testers** (i.e., utility functions dynamically
validating and inspecting various properties of passed callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype.typing import Any
from beartype._util.func.utilfunccodeobj import (
    get_func_codeobj_or_none)
from beartype._data.datatyping import (
    Codeobjable,
    TypeException,
)
from inspect import (
    CO_ASYNC_GENERATOR,
    CO_COROUTINE,
    CO_GENERATOR,
)

# ....................{ CONSTANTS                          }....................
FUNC_NAME_LAMBDA = '<lambda>'
'''
Default name of all **pure-Python lambda functions** (i.e., function declared
as a ``lambda`` expression embedded in a larger statement rather than as a
full-blown ``def`` statement).

Python initializes the names of *all* lambda functions to this lambda-specific
placeholder string on lambda definition.

Caveats
----------
**Usage of this placeholder to differentiate lambda from non-lambda callables
invites false positives in unlikely edge cases.** Technically, malicious third
parties may externally change the name of any lambda function *after* defining
that function. Pragmatically, no one sane should ever do such a horrible thing.
While predictably absurd, this is also the only efficient (and thus sane) means
of differentiating lambda from non-lambda callables. Alternatives require
AST-based parsing, which comes with its own substantial caveats, concerns,
edge cases, and false positives. If you must pick your poison, pick this one.
'''

# ....................{ VALIDATORS                         }....................
def die_unless_func_python(
    # Mandatory parameters.
    func: Codeobjable,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception if the passed callable is **C-based** (i.e., implemented
    in C as either a builtin bundled with the active Python interpreter *or*
    third-party C extension function).

    Equivalently, this validator raises an exception unless the passed function
    is **pure-Python** (i.e., implemented in Python as either a function or
    method).

    Parameters
    ----------
    func : Codeobjable
        Callable to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :class:`_BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`exception_cls`
         If the passed callable is C-based.

    See Also
    ----------
    :func:`is_func_python`
        Further details.
    '''

    # If this callable is *NOT* pure-Python, raise an exception.
    if not is_func_python(func):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # If this callable is uncallable, raise an appropriate exception.
        if not callable(func):
            raise exception_cls(f'{exception_prefix}{repr(func)} not callable.')
        # Else, this callable is callable.

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{repr(func)} not '
            f'pure-Python callable backed by code object '
            f'(i.e., either C-based callable or pure-Python callable backed by '
            f'__call__() dunder method).'
        )
    # Else, this callable is pure-Python.

# ....................{ VALIDATORS ~ descriptors           }....................
def die_unless_func_classmethod(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **C-based unbound class
    method descriptor** (i.e., method decorated by the builtin
    :class:`classmethod` decorator, yielding a non-callable instance of that
    :class:`classmethod` decorator class implemented in low-level C and
    accessible via the low-level :attr:`object.__dict__` dictionary rather than
    as class or instance attributes).

    Parameters
    ----------
    func : Any
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :class:`_BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`exception_cls`
         If the passed object is *not* a class method descriptor.

    See Also
    ----------
    :func:`is_func_classmethod`
        Further details.
    '''

    # If this object is *NOT* a class method descriptor, raise an exception.
    if not is_func_classmethod(func):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{repr(func)} not '
            f'C-based unbound class method descriptor.'
        )
    # Else, this object is a class method descriptor.


def die_unless_func_property(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **C-based unbound property
    method descriptor** (i.e., method decorated by the builtin :class:`property`
    decorator, yielding a non-callable instance of that :class:`property`
    decorator class implemented in low-level C and accessible as a class rather
    than instance attribute).

    Parameters
    ----------
    func : Any
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :property:`_BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`exception_cls`
         If the passed object is *not* a property method descriptor.

    See Also
    ----------
    :func:`is_func_property`
        Further details.
    '''

    # If this object is *NOT* a property method descriptor, raise an exception.
    if not is_func_property(func):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{repr(func)} not '
            f'C-based unbound property method descriptor.'
        )
    # Else, this object is a property method descriptor.


def die_unless_func_staticmethod(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **C-based unbound static
    method descriptor** (i.e., method decorated by the builtin
    :class:`staticmethod` decorator, yielding a non-callable instance of that
    :class:`staticmethod` decorator class implemented in low-level C and
    accessible via the low-level :attr:`object.__dict__` dictionary rather than
    as class or instance attributes).

    Parameters
    ----------
    func : Any
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :static:`_BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`exception_cls`
         If the passed object is *not* a static method descriptor.

    See Also
    ----------
    :func:`is_func_staticmethod`
        Further details.
    '''

    # If this object is *NOT* a static method descriptor, raise an exception.
    if not is_func_staticmethod(func):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{repr(func)} not '
            f'C-based unbound static method descriptor.'
        )
    # Else, this object is a static method descriptor.

# ....................{ TESTERS                            }....................
def is_func_lambda(func: Any) -> bool:
    '''
    ``True`` only if the passed object is a **pure-Python lambda function**
    (i.e., function declared as a ``lambda`` expression embedded in a larger
    statement rather than as a full-blown ``def`` statement).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a pure-Python lambda function.
    '''

    # Return true only if this both...
    return (
        # This callable is pure-Python *AND*...
        is_func_python(func) and
        # This callable's name is the lambda-specific placeholder name
        # initially given by Python to *ALL* lambda functions. Technically,
        # this name may be externally changed by malicious third parties after
        # the declaration of this lambda. Pragmatically, no one sane would ever
        # do such a horrible thing. Would they!?!?
        #
        # While predictably absurd, this is also the only efficient (and thus
        # sane) means of differentiating lambda from non-lambda callables.
        # Alternatives require AST-based parsing, which comes with its own
        # substantial caveats, concerns, and edge cases.
        func.__name__ == FUNC_NAME_LAMBDA
    )


def is_func_python(func: object) -> bool:
    '''
    ``True`` only if the passed object is a **pure-Python callable** (i.e.,
    implemented in Python as either a function or method rather than in C as
    either a builtin bundled with the active Python interpreter *or*
    third-party C extension function).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a pure-Python callable
    '''

    # Return true only if a pure-Python code object underlies this object.
    # C-based callables are associated with *NO* code objects.
    return get_func_codeobj_or_none(func) is not None

# ....................{ TESTERS ~ descriptor               }....................
def is_func_classmethod(func: Any) -> bool:
    '''
    ``True`` only if the passed object is a **C-based unbound class method
    descriptor** (i.e., method decorated by the builtin :class:`classmethod`
    decorator, yielding a non-callable instance of that :class:`classmethod`
    decorator class implemented in low-level C and accessible via the
    low-level :attr:`object.__dict__` dictionary rather than as class or
    instance attributes).

    Caveats
    ----------
    Class method objects are *only* directly accessible via the low-level
    :attr:`object.__dict__` dictionary. When accessed as class or instance
    attributes, class methods reduce to instances of the standard
    :class:`MethodBoundInstanceOrClassType` type.

    Class method objects are *not* callable, as their implementations fail to
    define the ``__call__`` dunder method.

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a C-based unbound class method
        descriptor.
    '''

    # Now you too have seen the pure light of the one-liner.
    return isinstance(func, classmethod)


def is_func_property(func: Any) -> bool:
    '''
    ``True`` only if the passed object is a **C-based unbound property method
    descriptor** (i.e., method decorated by the builtin :class:`property`
    decorator, yielding a non-callable instance of that :class:`property`
    decorator class implemented in low-level C and accessible as a class rather
    than instance attribute).

    Caveats
    ----------
    Property objects are directly accessible both as class attributes *and* via
    the low-level :attr:`object.__dict__` dictionary. Property objects are *not*
    accessible as instance attributes, for hopefully obvious reasons.

    Property objects are *not* callable, as their implementations fail to define
    the ``__call__`` dunder method.

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a pure-Python property.
    '''

    # We rejoice in the shared delight of one-liners.
    return isinstance(func, property)


def is_func_staticmethod(func: Any) -> bool:
    '''
    ``True`` only if the passed object is a **C-based unbound static method
    descriptor** (i.e., method decorated by the builtin :class:`staticmethod`
    decorator, yielding a non-callable instance of that :class:`staticmethod`
    decorator class implemented in low-level C and accessible via the low-level
    :attr:`object.__dict__` dictionary rather than as class or instance
    attributes).

    Caveats
    ----------
    Static method objects are *only* directly accessible via the low-level
    :attr:`object.__dict__` dictionary. When accessed as class or instance
    attributes, static methods reduce to instances of the standard
    :class:`FunctionType` type.

    Static method objects are *not* callable, as their implementations fail to
    define the ``__call__`` dunder method.

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a pure-Python static method.
    '''

    # Does the one-liner have Buddhahood? Mu.
    return isinstance(func, staticmethod)

# ....................{ TESTERS ~ async                    }....................
def is_func_async(func: object) -> bool:
    '''
    ``True`` only if the passed object is an **asynchronous callable** (i.e.,
    awaitable factory callable implicitly creating and returning an awaitable
    object (i.e., satisfying the :class:`collections.abc.Awaitable` protocol) by
    being declared via the ``async def`` syntax and thus callable *only* when
    preceded by comparable ``await`` syntax).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is an asynchronous callable.

    See Also
    ----------
    :func:`inspect.iscoroutinefunction`
    :func:`inspect.isasyncgenfunction`
        Stdlib functions strongly inspiring this implementation.
    '''

    # Code object underlying this pure-Python callable if any *OR* "None".
    #
    # Note this tester intentionally:
    # * Inlines the tests performed by the is_func_coro() and
    #   is_func_async_generator() testers for efficiency.
    # * Calls the get_func_codeobj_or_none() with "is_unwrapping" disabled
    #   rather than enabled. Why? Because the asynchronicity of this possibly
    #   higher-level wrapper has *NO* relation to that of the possibly
    #   lower-level wrappee wrapped by this wrapper. Notably, it is both
    #   feasible and commonplace for third-party decorators to enable:
    #   * Synchronous callables to be called asynchronously by wrapping
    #     synchronous callables with asynchronous closures.
    #   * Asynchronous callables to be called synchronously by wrapping
    #     asynchronous callables with synchronous closures. Indeed, our
    #     top-level "conftest.py" pytest plugin does exactly this -- enabling
    #     asynchronous tests to be safely called by pytest's currently
    #     synchronous framework.
    func_codeobj = get_func_codeobj_or_none(func)

    # If this object is *NOT* a pure-Python callable, immediately return false.
    if func_codeobj is None:
        return False
    # Else, this object is a pure-Python callable.

    # Bit field of OR-ed binary flags describing this callable.
    func_codeobj_flags = func_codeobj.co_flags

    # Return true only if these flags imply this callable to be either...
    return (
        # An asynchronous coroutine *OR*...
        func_codeobj_flags & CO_COROUTINE != 0 or
        # An asynchronous generator.
        func_codeobj_flags & CO_ASYNC_GENERATOR != 0
    )


def is_func_coro(func: object) -> bool:
    '''
    ``True`` only if the passed object is an **asynchronous coroutine factory**
    (i.e., awaitable callable containing *no* ``yield`` expression implicitly
    creating and returning an awaitable object (i.e., satisfying the
    :class:`collections.abc.Awaitable` protocol) by being declared via the
    ``async def`` syntax and thus callable *only* when preceded by comparable
    ``await`` syntax).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is an asynchronous coroutine factory.

    See Also
    ----------
    :func:`inspect.iscoroutinefunction`
        Stdlib function strongly inspiring this implementation.
    '''

    # Code object underlying this pure-Python callable if any *OR* "None".
    func_codeobj = get_func_codeobj_or_none(func)

    # Return true only if...
    return (
        # This object is a pure-Python callable *AND*...
        func_codeobj is not None and
        # This callable's code object implies this callable to be an
        # asynchronous coroutine.
        func_codeobj.co_flags & CO_COROUTINE != 0
    )


def is_func_async_generator(func: object) -> bool:
    '''
    ``True`` only if the passed object is an **asynchronous generator factory**
    (i.e., awaitable callable containing one or more ``yield`` expressions
    implicitly creating and returning an awaitable object (i.e., satisfying the
    :class:`collections.abc.Awaitable` protocol) by being declared via the
    ``async def`` syntax and thus callable *only* when preceded by comparable
    ``await`` syntax).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is an asynchronous generator.

    See Also
    ----------
    :func:`inspect.isasyncgenfunction`
        Stdlib function strongly inspiring this implementation.
    '''

    # Code object underlying this pure-Python callable if any *OR* "None".
    func_codeobj = get_func_codeobj_or_none(func)

    # Return true only if...
    return (
        # This object is a pure-Python callable *AND*...
        func_codeobj is not None and
        # This callable's code object implies this callable to be an
        # asynchronous generator.
        func_codeobj.co_flags & CO_ASYNC_GENERATOR != 0
    )

# ....................{ TESTERS ~ sync                     }....................
def is_func_sync_generator(func: object) -> bool:
    '''
    ``True`` only if the passed object is an **synchronous generator factory**
    (i.e., awaitable callable containing one or more ``yield`` expressions
    implicitly creating and returning a generator object (i.e., satisfying the
    :class:`collections.abc.Generator` protocol) by being declared via the
    ``def`` rather than ``async def`` syntax).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a synchronous generator.

    See Also
    ----------
    :func:`inspect.isgeneratorfunction`
        Stdlib function strongly inspiring this implementation.
    '''

    # If this object is uncallable, immediately return False.
    #
    # Note this test is explicitly required to differentiate synchronous
    # generator callables from synchronous generator objects (i.e., the objects
    # they implicitly create and return). Whereas both asynchronous coroutine
    # objects *AND* asynchronous generator objects do *NOT* contain code
    # objects whose "CO_COROUTINE" and "CO_ASYNC_GENERATOR" flags are non-zero,
    # synchronous generator objects do contain code objects whose
    # "CO_GENERATOR" flag is non-zero. This implies synchronous generator
    # callables to create and return synchronous generator objects that are
    # themselves technically valid synchronous generator callables, which is
    # absurd. We prohibit this ambiguity by differentiating the two here.
    if not callable(func):
        return False
    # Else, this object is callable.

    # Code object underlying this pure-Python callable if any *OR* "None".
    func_codeobj = get_func_codeobj_or_none(func)

    # Return true only if...
    return (
        # This object is a pure-Python callable *AND*...
        func_codeobj is not None and
        # This callable's code object implies this callable to be a
        # synchronous generator.
        func_codeobj.co_flags & CO_GENERATOR != 0
    )
