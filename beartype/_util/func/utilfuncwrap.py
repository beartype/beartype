#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable wrapper** (i.e., higher-level callable, typically
implemented as a decorator, wrapping a lower-level callable) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableWrapperException
from beartype._cave._cavefast import MethodBoundInstanceOrClassType
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import TypeIs
from beartype._util.func.arg.utilfuncarglen import (
    get_func_args_nonvariadic_len)
from beartype._util.func.arg.utilfuncargtest import (
    is_func_arg_variadic_positional,
    is_func_arg_variadic_keyword,
)
from collections.abc import Callable
from typing import (
    Any,
    Optional,
    Union,
)

# ....................{ TESTERS                            }....................
def is_func_wrapper(func: Any) -> TypeIs[Callable]:
    '''
    :data:`True` only if the passed object is a **callable wrapper** (i.e.,
    callable decorated by the standard :func:`functools.wraps` decorator for
    wrapping a pure-Python callable with additional functionality defined by a
    higher-level decorator).

    Note that this tester returns :data:`True` for both pure-Python and C-based
    callable wrappers. As an example of the latter, the standard
    :func:`functools.lru_cache` decorator creates and returns low-level C-based
    callable wrappers of the private type :class:`functools._lru_cache_wrapper`
    wrapping pure-Python callables.

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a callable wrapper.
    '''

    # Return true only if this object defines a dunder attribute uniquely
    # specific to the @functools.wraps decorator.
    #
    # Technically, *ANY* callable (including non-wrappers *NOT* created by the
    # @functools.wraps decorator) could trivially define this attribute; ergo,
    # this invites the possibility of false positives. Pragmatically, doing so
    # would violate ad-hoc standards and real-world practice across the
    # open-source ecosystem; ergo, this effectively excludes false positives.
    return hasattr(func, '__wrapped__')


def is_func_wrapper_isomorphic(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    wrapper: Optional[Callable] = None,
) -> TypeIs[Callable]:
    '''
    :data:`True` only if the passed object is an **isomorphic wrapper** (i.e.,
    callable decorated by the standard :func:`functools.wraps` decorator for
    wrapping a pure-Python callable with additional functionality defined by a
    higher-level decorator such that that wrapper isomorphically preserves both
    the number and types of all passed parameters and returns by accepting only
    a variadic positional argument and a variadic keyword argument).

    This tester enables callers to detect when a user-defined callable has been
    decorated by an isomorphic decorator, which constitutes *most* real-world
    decorators of interest.

    This tester is currently *not* memoized for efficiency, despite performing a
    relatively non-trivial (albeit technically :math:`O(1)`) operation. Why?
    Because this tester should typically be called at most once by the parent
    :func:`beartype._util.func.utilfuncwrap.unwrap_func_all_isomorphic`
    function, which is currently:

    * The *only* other function calling this tester.
    * Itself currently unmemoized.

    Caveats
    -------
    **This tester is merely a heuristic** -- albeit a reasonably robust
    heuristic likely to succeed in almost all real-world use cases. Nonetheless,
    this tester *could* return false positives and negatives in edge cases.

    Parameters
    ----------
    func : object
        Object to be inspected.
    wrapper : Optional[Callable]
        Wrapper callable to be unwrapped in the event that the callable to be
        inspected for isomorphism differs from the callable to be unwrapped.
        Typically, these two callables are the same. Edge cases in which these
        two callables differ include:

        * When ``wrapper`` is a **pseudo-callable** (i.e., otherwise uncallable
          object whose type renders that object callable by defining the
          ``__call__()`` dunder method) *and* ``func`` is that ``__call__()``
          dunder method. If that pseudo-callable wraps a lower-level callable,
          then that pseudo-callable (rather than ``__call__()`` dunder method)
          defines the ``__wrapped__`` instance variable providing that callable.

        Defaults to :data:`None`, in which case this parameter *actually*
        defaults to ``func``.

    Returns
    -------
    bool
        :data:`True` only if this object is an isomorphic decorator wrapper.
    '''

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.func.utilfunccodeobj import get_func_codeobject_or_none
    from beartype._util.func.utilfunctest import (
        is_func_boundmethod)

    # ....................{ NOOP                           }....................
    # If the caller failed to explicitly pass a callable to be unwrapped,
    # default the callable to be unwrapped to the passed callable.
    if wrapper is None:
        wrapper = func
    # Else, the caller explicitly passed a callable to be unwrapped. In this
    # case, preserve that callable as is.

    # If that callable is *NOT* a wrapper, immediately return false.
    if not is_func_wrapper(wrapper):
        return False
    # Else, that callable is a wrapper.

    # ....................{ LOCALS                         }....................
    # Number of non-variadic arguments permitted for this wrapper if isomorphic,
    # defaulting to 0.
    func_args_nonvariadic_len = 0

    # ....................{ TEST                           }....................
    # If this object is a C-based bound method descriptor...
    if is_func_boundmethod(func):
        # print(f'Detecting bound method f{repr(func)} isomorphism...')

        # Unwrap this descriptor to the pure-Python callable encapsulated by
        # this descriptor.
        func = unwrap_func_boundmethod_once(func)

        # Permit this pure-Python callable to accept exactly one non-variadic
        # argument, typically named "self" whose value is the object to which
        # this bound method descriptor was bound at object instantiation time.
        func_args_nonvariadic_len = 1
    # Else, this object is *NOT* a C-based bound method descriptor.

    # Code object underlying that callable as is (rather than possibly unwrapped
    # to another code object entirely) if that callable is pure-Python *OR*
    # "None" otherwise (i.e., if that callable is C-based).
    func_codeobj = get_func_codeobject_or_none(func)

    # If that callable is C-based...
    if not func_codeobj:  # pragma: no cover
        # print(f'Detecting C-based callable {repr(func)} isomorphism...')

        # Return true only if that C-based callable is the __call__() dunder
        # method of a pseudo-callable parent object. Although this tester
        # *CANNOT* positively decide whether that object is isomorphic or not,
        # *ALMOST* all __call__() dunder methods are C-based. Technically, this
        # *COULD* constitute a false positive in various edge cases.
        # Pragmatically, the alternatives are all worse. Blindly rejecting *ALL*
        # C-based __call__() dunder methods as non-isomorphic would effectively
        # prevent @beartype from decorating numerous pseudo-callable objects of
        # interest, including:
        # * Pseudo-callables dynamically generated by the third-party
        #   "@jax.jit" decorator: e.g.,
        #       from beartype import beartype
        #       from jax import jit
        #
        #       # The @jax.jit decorator creates and returns a C-based
        #       # pseudo-callable object defining an isomorphic __call__()
        #       # dunder method. If this tester erroneously rejected that method
        #       # as non-isomorphic, @beartype would be unable to decorate these
        #       # pseudo-callable objects! Clearly, that would be bad.
        #       @beartype
        #       @jit
        #       def muh_func(muh_arg: int) -> int:
        #           return muh_arg
        return func.__name__ == '__call__'
    # Else, that callable is pure-Python.

    # ....................{ RETURN                         }....................
    # Return true only if...
    return (
        # That callable accepts no non-variadic arguments *AND*...
        (
            get_func_args_nonvariadic_len(func_codeobj) ==
            func_args_nonvariadic_len
        ) and
        # That callable accepts variadic positional and/or keyword arguments.
        (
            is_func_arg_variadic_positional(func_codeobj) or
            is_func_arg_variadic_keyword(func_codeobj)
        )
    )

# ....................{ UNWRAPPERS ~ once                  }....................
#FIXME: Unit test us up, please.
def unwrap_func_once(func: Callable) -> Callable:
    '''
    Immediate **wrappee** (i.e., callable wrapped by the passed wrapper
    callable) of the passed higher-level **wrapper** (i.e., callable wrapping
    the wrappee callable to be returned) if the passed callable is a wrapper
    *or* that callable as is otherwise (i.e., if that callable is *not* a
    wrapper).

    Specifically, this getter undoes the work performed by any of the following:

    * A single use of the :func:`functools.wrap` decorator on the wrappee
      callable to be returned.
    * A single call to the :func:`functools.update_wrapper` function on the
      wrappee callable to be returned.

    Parameters
    ----------
    func : Callable
        Wrapper callable to be unwrapped.

    Returns
    -------
    Callable
        The immediate wrappee callable wrapped by the passed wrapper callable.

    Raises
    ------
    _BeartypeUtilCallableWrapperException
        If the passed callable is *not* a wrapper.
    '''

    # Immediate wrappee callable wrapped by the passed wrapper callable if any
    # *OR* "None" otherwise (i.e., if that callable is *NOT* a wrapper).
    func_wrappee = getattr(func, '__wrapped__', None)

    # If that callable is *NOT* a wrapper, raise an exception.
    if func_wrappee is None:
        raise _BeartypeUtilCallableWrapperException(
            f'Callable {repr(func)} not wrapper '
            f'(i.e., has no "__wrapped__" dunder attribute '
            f'defined by @functools.wrap or functools.update_wrapper()).'
        )
    # Else, that callable is a wrapper.

    # Return this immediate wrappee callable.
    return func_wrappee

# ....................{ UNWRAPPERS ~ once : descriptor     }....................
#FIXME: Unit test us up, please.
def unwrap_func_boundmethod_once(
    # Mandatory parameters.
    func: MethodBoundInstanceOrClassType,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableWrapperException,
    exception_prefix: str = '',
) -> Callable:
    '''
    Pure-Python unbound function wrapped by the passed **C-based bound instance
    method descriptor** (i.e., callable implicitly instantiated and assigned on
    the instantiation of an object whose class declares an instance function
    (whose first parameter is typically named ``self``) as an instance variable
    of that object such that that callable unconditionally passes that object as
    the value of that first parameter on all calls to that callable).

    Parameters
    ----------
    func : MethodBoundInstanceOrClassType
        Bound method descriptor to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilCallableWrapperException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    Callable
        Pure-Python unbound function wrapped by this bound method descriptor.

    Raises
    ------
    exception_cls
         If the passed object is *not* a bound method descriptor.

    See Also
    --------
    :func:`beartype._util.func.utilfunctest.is_func_boundmethod`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import die_unless_func_boundmethod

    # If this object is *NOT* a class method descriptor, raise an exception.
    die_unless_func_boundmethod(
        func=func,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is a class method descriptor.

    # Return the pure-Python function wrapped by this descriptor. Just do it!
    return func.__func__


def unwrap_func_class_or_static_method_once(
    # Mandatory parameters.
    func: Union[classmethod, staticmethod],

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableWrapperException,
    exception_prefix: str = '',
) -> Callable:
    '''
    Pure-Python unbound function wrapped by the passed **C-based unbound class
    or static method descriptor** (i.e., method decorated by either the builtin
    :class:`classmethod` or :class:`staticmethod` decorators, yielding a
    non-callable instance of that decorator class implemented in low-level C and
    accessible via the low-level :attr:`object.__dict__` dictionary rather than
    as class or instance attributes).

    Parameters
    ----------
    func : Union[classmethod, staticmethod]
        Class or static method descriptor to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilCallableWrapperException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    Callable
        Pure-Python unbound function wrapped by this method descriptor.

    Raises
    ------
    exception_cls
         If the passed object is *not* a class or static method descriptor.

    See Also
    --------
    :func:`beartype._util.func.utilfunctest.is_func_classmethod`
    :func:`beartype._util.func.utilfunctest.is_func_staticmethod`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import (
        die_unless_func_class_or_static_method)

    # If this object is neither a class *NOR* static method descriptor, raise an
    # exception.
    die_unless_func_class_or_static_method(
        func=func,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is either a class or static method descriptor.

    # Return the pure-Python function wrapped by this descriptor. Just do it!
    return func.__func__


#FIXME: Currently unused, but extensively tested. *shrug*
def unwrap_func_classmethod_once(
    # Mandatory parameters.
    func: classmethod,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableWrapperException,
    exception_prefix: str = '',
) -> Callable:
    '''
    Pure-Python unbound function wrapped by the passed **C-based unbound class
    method descriptor** (i.e., method decorated by the builtin
    :class:`classmethod` decorator, yielding a non-callable instance of that
    :class:`classmethod` decorator class implemented in low-level C and
    accessible via the low-level :attr:`object.__dict__` dictionary rather than
    as class or instance attributes).

    Parameters
    ----------
    func : classmethod
        Class method descriptor to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilCallableWrapperException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    Callable
        Pure-Python unbound function wrapped by this class method descriptor.

    Raises
    ------
    exception_cls
         If the passed object is *not* a class method descriptor.

    See Also
    --------
    :func:`beartype._util.func.utilfunctest.is_func_classmethod`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import die_unless_func_classmethod

    # If this object is *NOT* a class method descriptor, raise an exception.
    die_unless_func_classmethod(
        func=func,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is a class method descriptor.

    # Return the pure-Python function wrapped by this descriptor. Just do it!
    return func.__func__


#FIXME: Currently unused, but extensively tested. *shrug*
def unwrap_func_staticmethod_once(
    # Mandatory parameters.
    func: staticmethod,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableWrapperException,
    exception_prefix: str = '',
) -> Callable:
    '''
    Pure-Python unbound function wrapped by the passed **C-based unbound static
    method descriptor** (i.e., method decorated by the builtin
    :class:`staticmethod` decorator, yielding a non-callable instance of that
    :class:`staticmethod` decorator class implemented in low-level C and
    accessible via the low-level :attr:`object.__dict__` dictionary rather than
    as class or instance attributes).

    Parameters
    ----------
    func : staticmethod
        Static method descriptor to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilCallableWrapperException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    Callable
        Pure-Python unbound function wrapped by this static method descriptor.

    Raises
    ------
    exception_cls
         If the passed object is *not* a static method descriptor.

    See Also
    --------
    :func:`beartype._util.func.utilfunctest.is_func_staticmethod`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import die_unless_func_staticmethod

    # If this object is *NOT* a static method descriptor, raise an exception.
    die_unless_func_staticmethod(
        func=func,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is a static method descriptor.

    # Return the pure-Python function wrapped by this descriptor. Just do it!
    return func.__func__

# ....................{ UNWRAPPERS ~ all                   }....................
def unwrap_func_all(func: Callable) -> Callable:
    '''
    Lowest-level **wrappee** (i.e., callable wrapped by the passed wrapper
    callable) of the passed higher-level **wrapper** (i.e., callable wrapping
    the wrappee callable to be returned) if the passed callable is a wrapper
    *or* that callable as is otherwise (i.e., if that callable is *not* a
    wrapper).

    Specifically, this getter iteratively undoes the work performed by:

    * One or more consecutive uses of the :func:`functools.wrap` decorator on
      the wrappee callable to be returned.
    * One or more consecutive calls to the :func:`functools.update_wrapper`
      function on the wrappee callable to be returned.

    Parameters
    ----------
    func : Callable
        Wrapper callable to be unwrapped.

    Returns
    -------
    Callable
        Either:

        * If the passed callable is a wrapper, the lowest-level wrappee
          callable wrapped by that wrapper.
        * Else, the passed callable as is.
    '''

    #FIXME: Not even this suffices to avoid a circular import, sadly. *sigh*
    # Avoid circular import dependencies.
    # from beartype._util.func.utilfunctest import is_func_wrapper

    # While this callable still wraps another callable, unwrap one layer of
    # wrapping by reducing this wrapper to its next wrappee.
    while hasattr(func, '__wrapped__'):
    # while is_func_wrapper(func):
        func = func.__wrapped__  # type: ignore[attr-defined]

    # Return this wrappee, which is now guaranteed to *NOT* be a wrapper.
    return func


def unwrap_func_all_isomorphic(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    wrapper: Optional[Callable] = None,
) -> Callable:
    '''
    Lowest-level **non-isomorphic wrappee** (i.e., callable wrapped by the
    passed wrapper callable) of the passed higher-level **isomorphic wrapper**
    (i.e., closure wrapping the wrappee callable to be returned by accepting
    both a variadic positional and keyword argument and thus preserving both the
    positions and types of all parameters originally passed to that wrappee) if
    the passed callable is an isomorphic wrapper *or* that callable as is
    otherwise (i.e., if that callable is *not* an isomorphic wrapper).

    Specifically, this getter iteratively undoes the work performed by:

    * One or more consecutive decorations of the :func:`functools.wrap`
      decorator on the wrappee callable to be returned.
    * One or more consecutive calls to the :func:`functools.update_wrapper`
      function on the wrappee callable to be returned.

    Parameters
    ----------
    func : Callable
        Wrapper callable to be inspected for isomorphism. If ``wrapper`` is
        :data:`None` (as is the common case), this callable is also unwrapped.
    wrapper : Optional[Callable]
        Wrapper callable to be unwrapped in the event that the callable to be
        inspected for isomorphism differs from the callable to be unwrapped.
        Typically, these two callables are the same. Edge cases in which these
        two callables differ include:

        * When ``wrapper`` is a **pseudo-callable** (i.e., otherwise uncallable
          object whose type renders that object callable by defining the
          ``__call__()`` dunder method) *and* ``func`` is that ``__call__()``
          dunder method. If that pseudo-callable wraps a lower-level callable,
          then that pseudo-callable (rather than ``__call__()`` dunder method)
          defines the ``__wrapped__`` instance variable providing that callable.

        Defaults to :data:`None`, in which case this parameter *actually*
        defaults to ``func``.

    Returns
    -------
    Callable
        Either:

        * If the passed callable is an isomorphic wrapper, the lowest-level
          non-isomorphic wrappee callable wrapped by that wrapper.
        * Else, the passed callable as is.
    '''

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import is_func_codeobjable

    # ....................{ LOCALS                         }....................
    # If the caller failed to explicitly pass a callable to be unwrapped,
    # default the callable to be unwrapped to the passed callable.
    if wrapper is None:
        wrapper = func
    # Else, the caller explicitly passed a callable to be unwrapped. In this
    # case, preserve that callable as is.

    # ....................{ UNWRAP                         }....................
    # While...
    while True:
        # This wrappee callable remains a higher-level wrapper callable
        # isomorphically wrapping a lower-level wrappee callable, undo one layer
        # of wrapping by reducing the former to the latter.
        if is_func_wrapper_isomorphic(func=func, wrapper=wrapper):
            func_wrapped = unwrap_func_once(wrapper)
            # print(f'Unwrapped isomorphic {repr(func)} wrapper {repr(wrapper)} to {repr(func_wrapped)}.')
        # Else, this wrappee callable is no longer a higher-level wrapper
        # callable isomorphically wrapping a lower-level wrappee callable.

        #FIXME: Unneeded at the moment, but preserved for posterity. *shrug*
        # # If this wrappee callable remains a higher-level bound method
        # # descriptor, this descriptor transparently proxies and thus (by
        # # definition) isomorphically wraps a lower-level unbound method. In this
        # # case, undo one layer of wrapping by reducing the former to the latter.
        # elif is_func_boundmethod(func):
        #     func_wrapped = unwrap_func_boundmethod_once(func)
        #     # print(f'Unwrapped bound method descriptor {repr(func)} to {repr(func_wrapped)}.')

        # Else, this wrappee callable is no longer a higher-level bound method
        # descriptor either. Since this wrappee callable no longer wraps
        # anything, halt iteration.
        else:
            break
        # print(f'Unwrapped isomorphic {repr(func)} wrapper {repr(wrapper)} to {repr(func_wrapped)}.')

        # If the lower-level object wrapped by this higher-level isomorphic
        # wrapper is *NOT* a pure-Python callable, this object is something
        # uselessly pathological like a class or C-based callable. Silently
        # ignore this useless object by halting iteration. Doing so preserves
        # this useful higher-level isomorphic wrapper as is.
        #
        # Note that this insane edge case arises due to the standard
        # @functools.wraps() decorator, which passively accepts possibly C-based
        # classes by wrapping those classes with pure-Python functions: e.g.,
        #     from beartype import beartype
        #     from functools import wraps
        #     from typing import Any
        #
        #     @beartype
        #     @wraps(list)
        #     def wrapper(*args: Any, **kwargs: Any):
        #         return list(*args, **kwargs)
        #
        # In the above example, the higher-level isomorphic wrapper wrapper()
        # wraps the lower-level C-based class "list".
        #
        # Unwrapping this wrapper to this class would induce insanity throughout
        # the codebase, which sanely expects wrappers to be callables rather
        # than classes. Clearly, classes have *NO* signatures. Technically, a
        # pure-Python class may define __new__() and/or __init__() dunder
        # methods that could be considered to be the signatures of those
        # classes. Nonetheless, C-based classes like "list" have *NO* such
        # analogues. The *ONLY* sane approach here is to pretend that we never
        # saw this pathological edge case.
        if not is_func_codeobjable(func_wrapped):
            break
        # Else, this lower-level callable is pure-Python.

        # Reduce this higher-level wrapper to this lower-level wrappee.
        func = wrapper = func_wrapped

    # ....................{ RETURN                         }....................
    # Return this wrappee, which is now guaranteed to *NOT* be an isomorphic
    # wrapper but might very well still be a wrapper, which is fine.
    return func
