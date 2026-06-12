#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable testers** (i.e., low-level callables dynamically
validating and inspecting various properties of passed callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._cave._cavefast import (
    CallableCodeObjectType,
    FunctionType,
    MethodBoundInstanceOrClassType,
    MethodDecoratorClassOrStaticTypes,
    MethodDecoratorClassType,
    MethodDecoratorPropertyType,
    MethodDecoratorStaticType,
)
from beartype._data.func.datafunc import FUNC_NAME_LAMBDA
from beartype._data.typing.datatyping import (
    Codeobjable,
    TypeException,
)
from beartype._data.typing.datatypingport import TypeIs
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.func.utilfunccodeobj import get_func_codeobject_or_none
from collections.abc import Callable
from inspect import (
    CO_ASYNC_GENERATOR,
    CO_COROUTINE,
    CO_GENERATOR,
)
from typing import (
    Any,
    NoReturn,
)

# ....................{ RAISERS                            }....................
#FIXME: Unit test us up, please.
def die_unless_func_python(
    # Mandatory parameters.
    func: FunctionType,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **pure-Python callable**
    directly defined in Python as either a function or method.

    Parameters
    ----------
    func : FunctionType
        Pure-Python callable to be validated.
    exception_cls : TypeException, default: _BeartypeUtilCallableException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Raises
    ------
    exception_cls
         Unless the passed callable is pure-Python.
    '''

    # If that callable is *NOT* pure-Python, raise an exception.
    if not is_func_python(func):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # If that callable is uncallable, raise an appropriate exception.
        if not callable(func):
            raise exception_cls(f'{exception_prefix}{repr(func)} not callable.')
        # Else, that callable is callable.

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{repr(func)} not '
            f'pure-Python function or method.'
        )
    # Else, that callable is pure-Python.

# ....................{ RAISERS ~ codeobjable              }....................
#FIXME: Currently unused, but preserved for posterity. *shrug*
# def die_unless_func_codeobjable(
#     # Mandatory parameters.
#     func: Codeobjable,
#
#     # Optional parameters.
#     exception_cls: TypeException = _BeartypeUtilCallableException,
#     exception_prefix: str = '',
# ) -> None:
#     '''
#     Raise an exception unless the passed object is **code-objectable** (i.e.,
#     either a pure-Python callable, low-level code object underlying a
#     pure-Python callable, or related object encapsulating such a code object).
#
#     Parameters
#     ----------
#     func : Codeobjable
#         Code-objectable to be validated.
#     exception_cls : TypeException, default: _BeartypeUtilCallableException
#         Type of exception to be raised in the event of a fatal error. Defaults
#         to :class:`._BeartypeUtilCallableException`.
#     exception_prefix : str, default: ''
#         Human-readable substring prefixing raised exception messages. Defaults
#         to the empty string.
#
#     Raises
#     ------
#     exception_cls
#          Unless the passed callable is code-objectable.
#
#     See Also
#     --------
#     :func:`.is_func_codeobjable`
#         Further details.
#     '''
#
#     # If that callable is *NOT* code-objectable, raise an exception.
#     if not is_func_codeobjable(func):
#         die_as_func_not_codeobjable(
#             func=func,
#             exception_cls=exception_cls,
#             exception_prefix=exception_prefix,
#         )
#     # Else, that callable is code-objectable.


def die_as_func_not_codeobjable(
    # Mandatory parameters.
    func: Codeobjable,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> NoReturn:
    '''
    Unconditionally raise an exception describing why the passed object is *not*
    **code-objectable** (i.e., either a pure-Python callable, low-level code
    object underlying a pure-Python callable, or related object encapsulating
    such a code object).

    Parameters
    ----------
    func : Codeobjable
        Code-objectable to be validated.
    exception_cls : TypeException, default: _BeartypeUtilCallableException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Raises
    ------
    exception_cls
         Unless the passed callable is code-objectable.
    '''
    assert isinstance(exception_cls, type), (
        f'{repr(exception_cls)} not class.')
    assert issubclass(exception_cls, Exception), (
        f'{repr(exception_cls)} not exception subclass.')
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # Raise a human-readable exception.
    raise exception_cls(
        f'{exception_prefix}{repr(func)} code object not found, '
        f'as neither:\n'
        f'* Pure-Python callable.\n'
        f'* C-based code object underlying a pure-Python callable.\n'
        f'* Related C-based object encapsulating such a code object '
        f'(e.g., call stack frame, generator object).'
    )

# ....................{ RAISERS ~ descriptors              }....................
#FIXME: Unit test us up, please.
def die_unless_func_boundmethod(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **C-based bound instance
    method descriptor** callable implicitly instantiated and assigned on the
    instantiation of an object whose class declares an instance function (whose
    first parameter is typically named ``self``) as an instance variable of that
    object such that that callable unconditionally passes that object as the
    value of that first parameter on all calls to that callable).

    Parameters
    ----------
    func : Any
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :class:`._BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    exception_cls
         If the passed object is *not* a bound method descriptor.

    See Also
    --------
    :func:`.is_func_boundmethod`
        Further details.
    '''

    # If this object is *NOT* a bound method descriptor, raise an exception.
    if not is_func_boundmethod(func):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{repr(func)} not '
            f'C-based bound instance method descriptor.'
        )
    # Else, this object is a bound method descriptor.


#FIXME: Unit test us up, please.
def die_unless_func_class_or_static_method(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **C-based unbound class or
    static method descriptor** (i.e., method decorated by either the builtin
    :class:`classmethod` or :class:`staticmethod` decorators, yielding a
    non-callable instance of that decorator class implemented in low-level C and
    accessible via the low-level :attr:`object.__dict__` dictionary rather than
    as class or instance attributes).

    Parameters
    ----------
    func : Any
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :exc:`._BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Raises
    ------
    exception_cls
         If the passed object is *not* a class or static method descriptor.

    See Also
    --------
    :func:`.is_func_classmethod`
        Further details.
    '''

    # If this object is neither a class *NOR* static method descriptor, raise an
    # exception.
    if not isinstance(func, MethodDecoratorClassOrStaticTypes):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{repr(func)} not '
            f'C-based unbound @classmethod or @staticmethod descriptor.'
        )
    # Else, this object is a class or static method descriptor.


#FIXME: Currently unused, but extensively tested. *shrug*
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
        :class:`._BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    exception_cls
         If the passed object is *not* a class method descriptor.

    See Also
    --------
    :func:`.is_func_classmethod`
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
    ------
    exception_cls
         If the passed object is *not* a property method descriptor.

    See Also
    --------
    :func:`.is_func_property`
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


#FIXME: Currently unused, but extensively tested. *shrug*
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
    exception_cls : TypeException, default: _BeartypeUtilCallableException
        Type of exception to be raised. Defaults to
        :exc:`_BeartypeUtilCallableException`.
    exception_prefix : str, default: ''
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    exception_cls
         If the passed object is *not* a static method descriptor.

    See Also
    --------
    :func:`.is_func_staticmethod`
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

# ....................{ RAISERS ~ nested                   }....................
#FIXME: Unit test us up, please. *sigh*
def die_unless_func_closure(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **closure** (i.e.,
    pure-Python nested callable accessing one or more local variables defined by
    the parent pure-Python callable also declaring that callable).

    Parameters
    ----------
    func : Callable
        Object to be inspected.
    exception_cls : TypeException, default: _BeartypeUtilCallableException
        Type of exception to be raised. Defaults to
        :exc:`_BeartypeUtilCallableException`.
    exception_prefix : str, default: ''
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    exception_cls
         If the passed object is *not* a closure.

    See Also
    --------
    :func:`.is_func_closure`
        Further details.
    '''

    # If this object is *NOT* a closure, raise an exception.
    if not is_func_closure(func):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(f'{exception_prefix}{repr(func)} not closure.')
    # Else, this object is a closure.

# ....................{ TESTERS                            }....................
def is_func_codeobjable(func: object) -> TypeIs[Callable]:
    '''
    :data:`True` only if the passed object is **code-objectable** (i.e., either
    a pure-Python callable, low-level code object underlying a pure-Python
    callable, or related object encapsulating such a low-level code object).

    This tester effectively tests whether this object is a **pure-Python
    callable** (i.e., implemented in Python as either a function or method
    rather than in C as either a builtin bundled with the active Python
    interpreter *or* third-party C extension function).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is code-objectable.
    '''

    # Return true only if a pure-Python code object underlies this object.
    # C-based callables are associated with *NO* code objects.
    return get_func_codeobject_or_none(func) is not None


def is_func_lambda(func: object) -> TypeIs[Callable]:
    '''
    :data:`True` only if the passed object is a **pure-Python lambda function**
    (i.e., function declared as a ``lambda`` expression embedded in a larger
    statement rather than as a full-blown ``def`` statement).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a pure-Python lambda function.
    '''

    # Return true only if this both...
    return (
        # This callable is pure-Python *AND*...
        is_func_codeobjable(func) and
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


#FIXME: Unit test us up, please.
def is_func_python(func: object) -> TypeIs[FunctionType]:
    '''
    :data:`True` only if the passed object is a **pure-Python callable**
    directly defined in Python as either a function or method.

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a pure-Python callable.
    '''

    # Singular decomposition across this Singularity: "Engage!"
    return isinstance(func, FunctionType)

# ....................{ TESTERS ~ descriptor : builtin     }....................
#FIXME: Unit test us up, please.
def is_func_boundmethod(func: object) -> TypeIs[MethodBoundInstanceOrClassType]:
    '''
    :data:`True` only if the passed object is a **C-based bound instance method
    descriptor** (i.e., callable implicitly instantiated and assigned on the
    instantiation of an object whose class declares an instance function (whose
    first parameter is typically named ``self``) as an instance variable of that
    object such that that callable unconditionally passes that object as the
    value of that first parameter on all calls to that callable).

    Caveats
    -------
    Instance method objects are *only* directly accessible as instance
    attributes. When accessed as either class attributes *or* via the low-level
    :attr:`object.__dict__` dictionary, instance methods are only functions
    (i.e., instances of the standard :class:`beartype.cave.FunctionType` type).

    Instance method objects are callable. Indeed, the callability of instance
    method objects is the entire point of instance method objects.

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a C-based bound instance method
        descriptor.
    '''

    # Only the penitent one-liner shall pass.
    return isinstance(func, MethodBoundInstanceOrClassType)


#FIXME: Unit test us up, please.
#FIXME: Currently unused but preserved for posterity. We'll want this someday!
# def is_func_class_property_or_static_method(func: Any)  -> TypeIs[
#     MethodDescriptorBuiltin]:
#     '''
#     :data:`True` only if the passed object is an **unbound class, property, or
#     static method descriptor** (i.e., C-based decorator type builtin to Python
#     whose instance is typically uncallable but encapsulates a callable
#     pure-Python method).
#
#     These method objects are *not* callable, as their implementations fail to
#     define the ``__call__()`` dunder method.
#
#     Parameters
#     ----------
#     func : object
#         Object to be inspected.
#
#     Returns
#     -------
#     bool
#         :data:`True` only if this object is an unbound class, property, or
#         static method descriptor.
#     '''
#
#     # Line up for the one-liner you never knew you needed in your life.
#     return isinstance(func, MethodDecoratorBuiltinTypes)


def is_func_classmethod(func: Any) -> TypeIs[MethodDecoratorClassType]:
    '''
    :data:`True` only if the passed object is an **unbound class method
    descriptor** (i.e., method decorated by the builtin :class:`classmethod`
    decorator, yielding a non-callable instance of that :class:`classmethod`
    decorator class implemented in low-level C and accessible via the low-level
    :attr:`object.__dict__` dictionary rather than as class or instance
    attributes).

    Caveats
    -------
    Class method objects are *only* directly accessible via the low-level
    :attr:`object.__dict__` dictionary. When accessed as class or instance
    attributes, class methods are indistinguishable from **bound method
    descriptors** (i.e., :class:`MethodBoundInstanceOrClassType` instances)
    bound to that class.

    Class method objects are *not* callable, as their implementations fail to
    define the ``__call__()`` dunder method.

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is an unbound class method descriptor.
    '''

    # Now you too have seen the pure light of the one-liner.
    return isinstance(func, MethodDecoratorClassType)


def is_func_property(func: Any) -> TypeIs[MethodDecoratorPropertyType]:
    '''
    :data:`True` only if the passed object is a **C-based unbound property
    method descriptor** (i.e., method decorated by the builtin :class:`property`
    decorator, yielding a non-callable instance of that :class:`property`
    decorator class implemented in low-level C and accessible as a class rather
    than instance attribute).

    Caveats
    -------
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
    -------
    bool
        :data:`True` only if this object is a pure-Python property.
    '''

    # We rejoice in the shared delight of one-liners.
    return isinstance(func, MethodDecoratorPropertyType)


def is_func_staticmethod(func: Any) -> TypeIs[MethodDecoratorStaticType]:
    '''
    :data:`True` only if the passed object is a **C-based unbound static method
    descriptor** (i.e., method decorated by the builtin :class:`staticmethod`
    decorator, yielding a non-callable instance of that :class:`staticmethod`
    decorator class implemented in low-level C and accessible via the low-level
    :attr:`object.__dict__` dictionary rather than as class or instance
    attributes).

    Caveats
    -------
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
    -------
    bool
        :data:`True` only if this object is a pure-Python static method.
    '''

    # Does the one-liner have Buddhahood? Mu.
    return isinstance(func, MethodDecoratorStaticType)

# ....................{ TESTERS ~ async                    }....................
def is_func_async(func: object) -> TypeIs[Callable]:
    '''
    :data:`True` only if the passed object is an **asynchronous callable
    factory** (i.e., awaitable factory callable implicitly creating and
    returning an awaitable object (i.e., satisfying the
    :class:`collections.abc.Awaitable` protocol) by being declared via the
    ``async def`` syntax and thus callable *only* when preceded by comparable
    ``await`` syntax).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is an asynchronous callable.

    See Also
    --------
    :func:`inspect.iscoroutinefunction`
    :func:`inspect.isasyncgenfunction`
        Stdlib functions strongly inspiring this implementation.
    '''

    # Code object underlying this pure-Python callable if any *OR* "None".
    #
    # Note this tester intentionally:
    # * Inlines the tests performed by the is_func_coro() and
    #   is_func_async_generator() testers for efficiency.
    # * Calls the get_func_codeobject_or_none() with "is_unwrap" disabled
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
    func_codeobj = get_func_codeobject_or_none(func)

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


def is_func_coro(func: object) -> TypeIs[Callable]:
    '''
    :data:`True` only if the passed object is an **asynchronous coroutine
    factory** (i.e., awaitable callable containing *no* ``yield`` expression
    implicitly creating and returning an awaitable object (i.e., satisfying the
    :class:`collections.abc.Awaitable` protocol) by being declared via the
    ``async def`` syntax and thus callable *only* when preceded by comparable
    ``await`` syntax).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is an asynchronous coroutine factory.

    See Also
    --------
    :func:`inspect.iscoroutinefunction`
        Stdlib function strongly inspiring this implementation.
    '''

    # Code object underlying this pure-Python callable if any *OR* "None".
    func_codeobj = get_func_codeobject_or_none(func)

    # Return true only if...
    return (
        # This object is a pure-Python callable *AND*...
        func_codeobj is not None and
        # This callable's code object implies this callable to be an
        # asynchronous coroutine.
        func_codeobj.co_flags & CO_COROUTINE != 0
    )


def is_func_async_generator(func: object) -> TypeIs[Callable]:
    '''
    :data:`True` only if the passed object is an **asynchronous generator
    factory** (i.e., awaitable callable containing one or more ``yield``
    expressions implicitly creating and returning an awaitable object (i.e.,
    satisfying the :class:`collections.abc.Awaitable` protocol) by being
    declared via the ``async def`` syntax and thus callable *only* when preceded
    by comparable ``await`` syntax).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is an asynchronous generator.

    See Also
    --------
    :func:`inspect.isasyncgenfunction`
        Stdlib function strongly inspiring this implementation.
    '''

    # Code object underlying this pure-Python callable if any *OR* "None".
    func_codeobj = get_func_codeobject_or_none(func)

    # Return true only if...
    return (
        # This object is a pure-Python callable *AND*...
        func_codeobj is not None and
        # This callable's code object implies this callable to be an
        # asynchronous generator.
        func_codeobj.co_flags & CO_ASYNC_GENERATOR != 0
    )

# ....................{ TESTERS ~ sync                     }....................
def is_func_sync_generator(func: object) -> TypeIs[Callable]:
    '''
    :data:`True` only if the passed object is an **synchronous generator
    factory** (i.e., iterable callable containing one or more ``yield``
    expressions implicitly creating and returning a generator object (i.e.,
    satisfying the :class:`collections.abc.Generator` protocol) by being
    declared via the ``def`` rather than ``async def`` syntax).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a synchronous generator.

    See Also
    --------
    :func:`inspect.isgeneratorfunction`
        Stdlib function strongly inspiring this implementation.
    '''

    # If this object is neither...
    #
    # This logic enables this tester to differentiate synchronous generator
    # *FACTORIES* from synchronous generator *OBJECTS* (i.e., the objects those
    # factories implicitly create and return). Whereas neither asynchronous
    # coroutine objects *NOR* asynchronous generator objects have code objects
    # whose "CO_COROUTINE" and "CO_ASYNC_GENERATOR" flags are enabled,
    # synchronous generator objects do have code objects whose "CO_GENERATOR"
    # flag is enabled. Ergo, synchronous generator factories create and return
    # synchronous generator objects that are themselves technically valid
    # synchronous generator factories... which, frankly, is absurd. Explicitly
    # prohibit this ambiguity by differentiating the two here.
    if not (
        # A callable *NOR*...
        callable(func) or
        # A code object (which is uncallable by definition).
        isinstance(func, CallableCodeObjectType)
    ):
        # Then immediately return false to prevent synchronous generator objects
        # from being ambiguously conflated with synchronous generator factories.
        return False
    # Else, this object is either callable *OR* a code object. In either case,
    # this object is *NOT* a synchronous generator object.

    # Code object underlying this pure-Python callable if any *OR* "None".
    func_codeobj = get_func_codeobject_or_none(func)

    # Return true only if...
    return (
        # This object is a pure-Python callable *AND*...
        func_codeobj is not None and
        # This callable's code object implies this callable to be a
        # synchronous generator.
        func_codeobj.co_flags & CO_GENERATOR != 0
    )

# ....................{ TESTERS : nested                   }....................
def is_func_closure(func: Any) -> TypeIs[Callable]:
    '''
    :data:`True` only if the passed callable is a **closure** (i.e., pure-Python
    nested callable accessing one or more local variables defined by the parent
    pure-Python callable also declaring that callable).

    Note that all closures are necessarily nested callables but that the
    converse is *not* necessarily the case. In particular, a nested callable
    accessing *no* variables declared by the parent callable also declaring that
    callable is *not* a closure; it's simply a nested callable.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this callable is a closure.
    '''

    # Return true only if that callable defines the closure-specific
    # "__closure__" dunder variable whose value is either:
    # * If that callable is a closure, a tuple of zero or more cell variables.
    # * If that callable is a pure-Python non-closure, "None".
    # * If that callable is C-based, undefined.
    return getattr(func, '__closure__', None) is not None


@callable_cached
def is_func_local(func: Callable) -> bool:
    '''
    :data:`True` only if the passed callable is **local** (i.e., a pure-Python
    callable locally defined in the body of another pure-Python callable and
    thus accessible *only* as a local attribute of the latter).

    Equivalently, this tester returns :data:`True` only if that callable is
    either:

    * A closure, which by definition is nested inside another callable.
    * A **nested non-closure function** (i.e., a closure-like function that does
      *not* reference local attributes of the parent callable enclosing that
      function and is thus technically *not* a closure): e.g.,

      .. code-block:: python

         def muh_parent_func():           # <-- parent function
             def muh_nested_func(): pass  # <-- nested non-closure function
             return muh_nested_func

    * A **callable-isolated method** (i.e., a method of a type nested inside
      another callable): e.g.,

      .. code-block:: python

         def muh_parent_func():                     # <-- parent function
             class MuhType(object):                 # <-- nested type
                 def muh_nested_method(self): pass  # <-- nested method
             return MuhType.muh_nested_method

    This tester is memoized for efficiency.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this callable is locally defined.
    '''

    # Return true only if either...
    return (
        # That callable is a closure (in which case that closure is necessarily
        # nested inside another callable) *OR*...
        #
        # Note that this tester intentionally tests for whether that callable is
        # a closure first, as doing so efficiently reduces to a constant-time
        # attribute test -- whereas the following test for non-closure nested
        # callables inefficiently requires a linear-time string search.
        is_func_closure(func) or
        # The fully-qualified name of that callable contains one or more
        # ".<locals>." substrings, each signifying a local callable scope. Since
        # *ALL* callables (i.e., both pure-Python and C-based) define a
        # non-empty "__qualname__" dunder variable containing at least their
        # unqualified names, this simplistic test is guaranteed to be safe.
        '.<locals>.' in func.__qualname__
    )


@callable_cached
def is_func_nested(func: Callable) -> bool:
    '''
    :data:`True` only if the passed callable is **nested** (i.e., a pure-Python
    callable declared in the body of another pure-Python callable or class).

    Equivalently, this tester returns :data:`True` only if that callable is
    either:

    * A closure, which by definition is nested inside another callable.
    * A method, which by definition is nested inside its class.
    * A **nested non-closure function** (i.e., a closure-like function that does
      *not* reference local attributes of the parent callable enclosing that
      function and is thus technically *not* a closure): e.g.,

      .. code-block:: python

         def muh_parent_func():           # <-- parent function
             def muh_nested_func(): pass  # <-- nested non-closure function
             return muh_nested_func

    This tester is memoized for efficiency.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this callable is nested.
    '''

    # Return true only if either...
    return (
        # That callable is a closure (in which case that closure is necessarily
        # nested inside another callable) *OR*...
        #
        # Note that this tester intentionally tests for whether that callable is
        # a closure first, as doing so efficiently reduces to a constant-time
        # attribute test -- whereas the following test for non-closure nested
        # callables inefficiently requires a linear-time string search.
        is_func_closure(func) or
        # The fully-qualified name of that callable contains one or more "."
        # delimiters, each signifying a nested lexical scope. Since *ALL*
        # callables (i.e., both pure-Python and C-based) define a non-empty
        # "__qualname__" dunder variable containing at least their unqualified
        # names, this simplistic test is guaranteed to be safe.
        #
        # Note this tester intentionally tests for the general-purpose existence
        # of a "." delimiter rather than the special-cased existence of a
        # ".<locals>." placeholder substring. Why? Because there are two types
        # of nested callables:
        # * Non-methods, which are lexically nested in a parent callable whose
        #   scope encapsulates all previously declared local variables. For
        #   unknown reasons, the unqualified names of nested non-method
        #   callables are *ALWAYS* prefixed by ".<locals>." in their
        #   "__qualname__" variables:
        #       >>> from collections.abc import Callable
        #       >>> def muh_parent_callable() -> Callable:
        #       ...     def muh_nested_callable() -> None: pass
        #       ...     return muh_nested_callable
        #       >>> muh_nested_callable = muh_parent_callable()
        #       >>> muh_parent_callable.__qualname__
        #       'muh_parent_callable'
        #       >>> muh_nested_callable.__qualname__
        #       'muh_parent_callable.<locals>.muh_nested_callable'
        # * Methods, which are lexically nested in the scope encapsulating all
        #   previously declared class variables (i.e., variables declared in
        #   class scope and thus accessible as method annotations). For unknown
        #   reasons, the unqualified names of methods are *NEVER* prefixed by
        #   ".<locals>." in their "__qualname__" variables: e.g.,
        #       >>> from typing import ClassVar
        #       >>> class MuhClass(object):
        #       ...    # Class variable declared in class scope.
        #       ...    muh_class_var: ClassVar[type] = int
        #       ...    # Instance method annotated by this class variable.
        #       ...    def muh_method(self) -> muh_class_var: return 42
        #       >>> MuhClass.muh_method.__qualname__
        #       'MuhClass.muh_method'
        '.' in func.__qualname__
    )
