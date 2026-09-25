#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) method caching
decorators** (i.e., low-level callables memoizing
:class:`beartype.door._cls.doorabc.TypeHint` methods *not* otherwise safely
memoizable by the general-purpose
:func:`beartype._util.cache.func.utilcachefunc.callable_cached` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import beartype  # <-- squelch static type-checking false positives *sigh*
from beartype.door._cls._doortest import die_unless_typehint
from beartype.roar._roarexc import _BeartypeUtilCallableCachedException
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatyping import CallableT
from beartype._util.func.arg.utilfuncargtest import (
    die_unless_func_args_len_flexible_equal,
    is_func_arg_variadic,
)
from beartype._util.func.utilfuncwrap import unwrap_func_all
from beartype._util.hint.utilhintget import get_hint_repr
from beartype._util.text.utiltextlabel import label_callable
from collections.abc import Callable
from functools import wraps

# ....................{ DECORATORS                         }....................
#FIXME: Unit test us up, please. *sigh*
#FIXME: Docstring us up, please. *sigh*
def typehint_method_cached_by_repr(
    is_if_not_typehint_return_notimplemented: bool = False) -> (
    Callable[[CallableT], CallableT]):

    # ....................{ CLOSURE ~ decorator            }....................
    def _typehint_method_cached_by_repr_decorator(
        func: CallableT) -> CallableT:
        '''
        **Memoize** (i.e., efficiently re-raise all exceptions previously raised
        by the decorated method when passed the same *exact* parameters (i.e.,
        parameters whose machine-readable string representations are equal) as a
        prior call to that method if any *or* return all values previously
        returned by that method otherwise rather than inefficiently recalling
        that method) the passed method.

        Caveats
        -------
        **This decorator is only intended to decorate bound methods** (i.e.,
        either class or instance methods bound to a class or instance). This
        decorator is *not* intended to decorate functions or static methods.

        **This decorator is only intended to decorate a method whose sole
        argument is guaranteed to be a memoized singleton** (e.g.,
        :class:`beartype.door.TypeHint` singleton). In this case, the
        machine-readable string representation of that argument uniquely
        identifies that argument across *all* calls to that method -- enabling
        this decorator to memoize that method. Conversely, if that argument is
        *not* guaranteed to be a memoized singleton, this decorator will fail to
        memoize that method while wasting considerable space and time attempting
        to do so. In short, caller caution is warranted.

        This decorator is a micro-optimized variant of the more general-purpose
        :func:`callable_cached` decorator, which should be preferred in most
        cases. This decorator mostly exists for one specific edge case that the
        :func:`callable_cached` decorator *cannot* by definition support:
        user-defined classes implementing the ``__eq__`` dunder method to
        internally call another method decorated by :func:`callable_cached`
        accepting an instance of the same class. This design pattern appears
        astonishingly frequently, including in our prominent
        :class:`beartype.door.TypeHint` class. This edge case provokes infinite
        recursion. Consider this minimal-length example (MLE) exhibiting the
        issue:

        .. code-block:: python

           from beartype._util.cache.func.utilcachefunc import callable_cached

           class MuhClass(object):
               def __eq__(self, other: object) -> bool:
                   return isinstance(other, MuhClass) and self._is_equal(other)

               @callable_cached
               def _is_equal(self, other: 'MuhClass') -> bool:
                   return True

        :func:`callable_cached` internally caches the ``other`` argument passed
        to the ``_is_equal()`` method as keys of various internal dictionaries.
        When passed the same ``other`` argument, subsequent calls to that method
        lookup that ``other`` argument in those dictionaries. Since dictionary
        lookups implicitly call the ``other.__eq__()`` method to resolve key
        collisions *and* since the ``__eq__()`` method has been overridden in
        terms of the ``_is_equal()`` method, infinite recursion results.

        This decorator circumvents this issue by internally looking up the
        object identifier of the passed argument rather than that argument
        itself, which then avoids implicitly calling the ``__eq__()`` method of
        that argument.

        Parameters
        ----------
        func : CallableT
            Callable to be memoized.

        Returns
        -------
        CallableT
            Closure wrapping this callable with memoization.

        Raises
        ------
        _BeartypeUtilCallableCachedException
            If this callable accepts either:

            * *No* parameters.
            * Two or more parameters.
            * A variadic positional parameter (e.g., ``*args``).

        See Also
        --------
        :func:`callable_cached`
            Further details.
        '''
        assert callable(func), f'{repr(func)} not callable.'

        # ....................{ PREAMBLE                   }....................
        # Lowest-level wrappee callable wrapped by this wrapper callable.
        func_wrappee = unwrap_func_all(func)

        # If this wrappee accepts either zero, one, *OR* three or more flexible
        # parameters (i.e., parameters passable as either positional or keyword
        # arguments), raise an exception.
        die_unless_func_args_len_flexible_equal(
            func=func_wrappee,
            func_args_len_flexible=2,
            exception_cls=_BeartypeUtilCallableCachedException,
            # Avoid unnecessary callable unwrapping as a negligible
            # optimization.
            is_unwrap=False,
        )
        # Else, this wrappee accepts exactly one flexible parameter.

        # If this wrappee accepts variadic arguments (either positional or
        # keyword), raise an exception.
        if is_func_arg_variadic(func_wrappee):
            raise _BeartypeUtilCallableCachedException(
                f'@method_cached_arg_by_id {label_callable(func)} '
                f'variadic arguments uncacheable.'
            )
        # Else, this wrappee accepts *NO* variadic arguments.

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize against the @callable_cached decorator. For
        # speed, this decorator violates DRY by duplicating logic.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # ....................{ LOCALS                     }....................
        # Dictionary mapping a tuple of all flattened parameters passed to each
        # prior call of the decorated callable with the value returned by that
        # call if any (i.e., if that call did *NOT* raise an exception).
        args_flat_to_return_value: dict[tuple, object] = {}

        # get() method of this dictionary, localized for efficiency.
        args_flat_to_return_value_get = args_flat_to_return_value.get

        # Dictionary mapping a tuple of all flattened parameters passed to each
        # prior call of the decorated callable with the exception raised by that
        # call if any (i.e., if that call raised an exception).
        args_flat_to_exception: dict[tuple, Exception] = {}

        # get() method of this dictionary, localized for efficiency.
        args_flat_to_exception_get = args_flat_to_exception.get

        # ....................{ CLOSURE ~ wrapper          }....................
        @wraps(func)
        def _typehint_method_cached(
            self: 'beartype.door.TypeHint', other: 'beartype.door.TypeHint'):  # pyright: ignore
            f'''
            Memoized variant of the {func.__name__}() callable.

            See Also
            --------
            :func:`callable_cached`
                Further details.
            '''

            #FIXME: Comment us up, please. *sigh*
            if is_if_not_typehint_return_notimplemented:
                # Avoid circular import dependencies.
                from beartype.door._cls.doorabc import TypeHint

                if not isinstance(other, TypeHint):
                    return NotImplemented
            else:
                # If the passed object is *NOT* a type hint wrapper, raise an
                # exception.
                die_unless_typehint(other)
                # Else, that object is a type hint wrapper.

            # 2-tuple comprising the machine-readable string representations of
            # the two positional parameters passed to the decorated method.
            args_flat = (
                get_hint_repr(self._hint),
                get_hint_repr(other._hint),
            )

            # Attempt to...
            try:
                # Exception raised by a prior call to the decorated callable
                # when passed these parameters *OR* the sentinel placeholder
                # otherwise (i.e., if this callable either has yet to be called
                # with these parameters *OR* has but failed to raise an
                # exception).
                #
                # Note that:
                # * This statement raises a "TypeError" exception if any item of
                #   this flattened tuple is unhashable.
                # * A sentinel placeholder (e.g., "SENTINEL") is *NOT* needed
                #   here. The values of the "args_flat_to_exception" dictionary
                #   are guaranteed to *ALL* be exceptions. Since "None" is *NOT*
                #   an exception, disambiguation between "None" and valid
                #   dictionary values is *NOT* needed here. Although a sentinel
                #   placeholder could still be employed, doing so would slightly
                #   reduce efficiency for *NO* real-world gain.
                exception = args_flat_to_exception_get(args_flat)

                # If this callable previously raised an exception when called
                # with these parameters, re-raise the same exception.
                if exception:
                    raise exception  # pyright: ignore
                # Else, this callable either has yet to be called with these
                # parameters *OR* has but failed to raise an exception.

                # Value returned by a prior call to the decorated callable when
                # passed these parameters *OR* a sentinel placeholder otherwise
                # (i.e., if this callable has yet to be passed these
                # parameters).
                return_value = args_flat_to_return_value_get(
                    args_flat, SENTINEL)

                # If this callable has already been called with these
                # parameters, return the value returned by that prior call.
                if return_value is not SENTINEL:
                    return return_value
                # Else, this callable has yet to be called with these
                # parameters.

                # Attempt to...
                try:
                    # Call this parameter with these parameters and cache the
                    # value returned by this call to these parameters.
                    return_value = args_flat_to_return_value[args_flat] = func(
                        self, other)
                # If this call raised an exception...
                except Exception as exception:
                    # Cache this exception to these parameters.
                    args_flat_to_exception[args_flat] = exception

                    # Re-raise this exception.
                    raise exception
            # If one or more objects either passed to *OR* returned from this
            # call are unhashable, perform this call as is *WITHOUT*
            # memoization. While non-ideal, stability is better than raising a
            # fatal exception.
            except TypeError:
                #FIXME: If testing, emit a non-fatal warning or possibly even
                #raise a fatal exception. In either case, we want our test suite
                #to notify us about this.
                return func(self, other)

            # Return this value.
            return return_value

        # ....................{ RETURN                     }....................
        # Return this wrapper closure.
        return _typehint_method_cached  # type: ignore[return-value]

    # ....................{ RETURN                         }....................
    # Return this decorator closure.
    return _typehint_method_cached_by_repr_decorator
