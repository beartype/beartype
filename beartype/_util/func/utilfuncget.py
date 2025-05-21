#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable getters** (i.e., utility functions dynamically
querying and retrieving various properties of passed callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype.typing import (
    Callable,
    Optional,
)
from beartype._cave._cavefast import MethodBoundInstanceOrClassType
from beartype._data.hint.datahinttyping import (
    HintAnnotations,
    TypeException,
)

# ....................{ GETTERS ~ descriptors              }....................
#FIXME: Unit test us up, please.
#FIXME: Docstring us up, please.
def get_func_boundmethod_self(
    # Mandatory parameters.
    func: MethodBoundInstanceOrClassType,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> object:
    '''
    Instance object to which the passed **C-based bound instance method
    descriptor** (i.e., callable implicitly instantiated and assigned on the
    instantiation of an object whose class declares an instance function (whose
    first parameter is typically named ``self``) as an instance variable of that
    object such that that callable unconditionally passes that object as the
    value of that first parameter on all calls to that callable) was bound as an
    instance attribute at instantiation time.

    Parameters
    ----------
    func : object
        Bound method descriptor to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilCallableWrapperException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    object
        Instance object to which this bound method descriptor is bound to.

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
    return func.__self__

# ....................{ GETTERS ~ hints                    }....................
#FIXME: Refactor all unsafe access of the low-level "__annotations__" dunder
#attribute to instead call this high-level getter, please.
#FIXME: See "FIXME:" comments in the "beartype._check.metadata.metadecor" submodule for
#how this needs to be refactored to support Python >= 3.13, please.
#FIXME: Unit test us up, please.
def get_func_annotations(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> HintAnnotations:
    '''
    **Annotations** (i.e., possibly empty ``__annotations__`` dunder dictionary
    mapping from the name of each annotated parameter or return of the passed
    possibly C-based callable to the type hint annotating that parameter or
    return) possibly annotating the passed callable if that callable defines the
    ``__annotations__`` dunder dictionary *or* raise an exception otherwise
    (i.e., if that callable fails to define the ``__annotations__`` dunder
    dictionary).

    Parameters
    ----------
    func : object
        Object to be inspected.
    exception_cls : TypeException, default: _BeartypeUtilCallableException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilCallableException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    HintAnnotations
        Possibly empty ``__annotations__`` dunder dictionary defined by that
        callable.

    Raises
    ------
    exception_cls
         If that callable fails to define the ``__annotations__`` dunder
         dictionary. Since *all* pure-Python callables (including unannotated
         callables) define this dictionary, this getter raises an exception only
         if the passed callable is either uncallable *or* a **pseudo-callable
         object** (i.e., otherwise uncallable object whose class renders all
         instances of that class callable by defining the ``__call__()`` dunder
         method).

    See Also
    --------
    :func:`.get_func_annotations_or_none`
        Further details.
    '''

    # Annotations of that callable if that callable is actually a pure-Python
    # callable *OR* "None" otherwise.
    hint_annotations = get_func_annotations_or_none(func)

    # If that callable is *NOT* pure-Python, raise an exception.
    if hint_annotations is None:
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
            f'{exception_prefix}{repr(func)} not annotatable by type hints '
            f'(i.e., fails to define "__annotations__" dunder dictionary).'
        )
    # Else, that callable is pure-Python.

    # Return these annotations.
    return hint_annotations


#FIXME: Refactor all unsafe access of the low-level "__annotations__" dunder
#attribute to instead call this high-level getter, please.
#FIXME: Unit test us up, please.
def get_func_annotations_or_none(func: Callable) -> Optional[HintAnnotations]:
    '''
    **Annotations** (i.e., possibly empty ``__annotations__`` dunder dictionary
    mapping from the name of each annotated parameter or return of the passed
    possibly C-based callable to the type hint annotating that parameter or
    return) possibly annotating the passed callable if that callable defines the
    ``__annotations__`` dunder dictionary *or* :data:`None` otherwise (i.e., if
    that callable fails to define the ``__annotations__`` dunder dictionary).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    Optional[HintAnnotations]
        Either:

        * If that callable is a pure-Python function, method, or object
          transitively wrapping a pure-Python function or method, the possibly
          empty ``__annotations__`` dunder dictionary defined by that callable.
        * Else, :data:`None`.
    '''

    # Demonstrable monstrosity demons!
    #
    # Note that:
    # * The "__annotations__" dunder attribute is guaranteed to exist *ONLY* for
    #   standard pure-Python callables. Various other callables of interest
    #   (e.g., functions exported by the standard "operator" module) do *NOT*
    #   necessarily declare that attribute. Since this getter is commonly called
    #   in general-purpose contexts where this guarantee does *NOT*
    #   necessarily hold, we intentionally access that attribute safely albeit
    #   somewhat more slowly via getattr().
    return getattr(func, '__annotations__', None)
