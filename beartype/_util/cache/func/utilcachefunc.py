#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable caching utilities** (i.e., low-level callables
performing general-purpose memoization of function and method calls).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Generalize @callable_cached to revert to the body of the
#betse._util.type.decorator.decmemo.func_cached decorator when the passed
#callable accepts *NO* parameters, which can be trivially decided by inspecting
#the code object of this callable. Why do this? Because the @func_cached
#decorator is *INSANELY* fast for this edge case -- substantially faster than
#the current general-purpose @callable_cached approach.

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableCachedException
from beartype._data.typing.datatyping import CallableT
from beartype._util.func.arg.utilfuncargtest import (
    die_unless_func_args_len_flexible_equal,
    is_func_arg_variadic,
)
from beartype._util.text.utiltextlabel import label_callable
from beartype._data.kind.datakindiota import SENTINEL
from functools import wraps

# ....................{ DECORATORS ~ callable              }....................
def callable_cached(func: CallableT) -> CallableT:
    '''
    **Memoize** (i.e., efficiently re-raise all exceptions previously raised by
    the decorated callable when passed the same parameters (i.e., parameters
    that evaluate as equals) as a prior call to that callable if any *or* return
    all values previously returned by that callable otherwise rather than
    inefficiently recalling that callable) the passed callable.

    Specifically, this decorator (in order):

    #. Creates:

       * A local dictionary mapping parameters passed to this callable with the
         values returned by this callable when passed those parameters.
       * A local dictionary mapping parameters passed to this callable with the
         exceptions raised by this callable when passed those parameters.

    #. Creates and returns a closure transparently wrapping this callable with
       memoization. Specifically, this wrapper (in order):

       #. Tests whether this callable has already been called at least once
          with the passed parameters by lookup of those parameters in these
          dictionaries.
       #. If this callable previously raised an exception when passed these
          parameters, this wrapper re-raises the same exception.
       #. Else if this callable returned a value when passed these parameters,
          this wrapper re-returns the same value.
       #. Else, this wrapper:

          #. Calls that callable with those parameters.
          #. If that call raised an exception:

             #. Caches that exception with those parameters in that dictionary.
             #. Raises that exception.

          #. Else:

             #. Caches the value returned by that call with those parameters in
                that dictionary.
             #. Returns that value.

    Caveats
    -------
    **The decorated callable must accept no keyword parameters.** While this
    decorator previously memoized keyword parameters, doing so incurred
    significant performance penalties defeating the purpose of caching. This
    decorator now intentionally memoizes *only* positional parameters.

    **The decorated callable must accept no variadic positional parameters.**
    While memoizing variadic parameters would of course be feasible, this
    decorator has yet to implement support for doing so.

    **The decorated callable should not be a property method** (i.e., either a
    property getter, setter, or deleter subsequently decorated by the
    :class:`property` decorator). Technically, this decorator *can* be used to
    memoize property methods; pragmatically, doing so would be sufficiently
    inefficient as to defeat the intention of memoizing in the first place.

    **This decorator does not memoizes warnings issued by the decorated
    callable.** This decorator *does* memoize exceptions raised by the decorated
    callable. Ideally, this decorator would memoize both. Pragmatically, this
    decorator *must* memoize exceptions. That's non-negotiable. However, this
    decorator has *no* such compulsion to memoize warnings. Warnings are
    non-fatal and commonly treated as an ignorable annoying nuisance by users.
    Although memoizing warnings would be both feasible and trivial, doing so
    would reduce the efficiency and thus point of this memoization.

    Efficiency
    ----------
    For efficiency, consider calling the decorated callable with only:

    * **Hashable** (i.e., immutable) arguments. While technically supported,
      every call to the decorated callable passed one or more unhashable
      arguments (e.g., mutable containers like lists and dictionaries) will
      silently *not* be memoized. Equivalently, only calls passed only hashable
      arguments will be memoized. This flexibility enables decorated callables
      to accept unhashable PEP-compliant type hints. Although *all*
      PEP-noncompliant and *most* PEP-compliant type hints are hashable, some
      sadly are not. These include:

      * :pep:`585`-compliant type hints subscripted by one or more unhashable
        objects (e.g., ``collections.abc.Callable[[], str]``, the `PEP
        585`_-compliant type hint annotating piths accepting callables
        accepting no parameters and returning strings).
      * :pep:`586`-compliant type hints subscripted by an unhashable object
        (e.g., ``typing.Literal[[]]``, a literal empty list).
      * :pep:`593`-compliant type hints subscripted by one or more unhashable
        objects (e.g., ``typing.Annotated[typing.Any, []]``, the
        :attr:`typing.Any` singleton annotated by an empty list).

    **This decorator is intentionally not implemented in terms of the stdlib**
    :func:`functools.lru_cache` **decorator,** as that decorator is inefficient
    in the special case of unbounded caching with ``maxsize=None``. Why? Because
    that decorator insists on unconditionally recording irrelevant statistics
    like cache misses and hits. While bounding the number of cached values is
    advisable in the general case (e.g., to avoid exhausting memory merely for
    optional caching), parameters and returns cached by this package are
    sufficiently small in size to render such bounding irrelevant.

    Consider the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_type_typing`
    function, for example. Each call to that function only accepts a single
    class and returns a boolean. Under conservative assumptions of 4 bytes of
    storage per class reference and 4 byte of storage per boolean reference,
    each call to that function requires caching at most 8 bytes of storage.
    Again, under conservative assumptions of at most 1024 unique type
    annotations for the average downstream consumer, memoizing that function in
    full requires at most 1024 * 8 == 8096 bytes or ~8Kb of storage. Clearly,
    8Kb of overhead is sufficiently negligible to obviate any space concerns
    that would warrant an LRU cache in the first place.

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
        If this callable accepts a variadic positional parameter (e.g.,
        ``*args``).
    '''
    assert callable(func), f'{repr(func)} not callable.'

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize against the @method_cached_arg_by_id decorator
    # below. For speed, this decorator violates DRY by duplicating logic.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # ....................{ LOCALS                         }....................
    # Dictionary mapping a tuple of all flattened parameters passed to each
    # prior call of the decorated callable with the value returned by that call
    # if any (i.e., if that call did *NOT* raise an exception).
    args_flat_to_return_value: dict[tuple, object] = {}

    # get() method of this dictionary, localized for efficiency.
    args_flat_to_return_value_get = args_flat_to_return_value.get

    # Dictionary mapping a tuple of all flattened parameters passed to each
    # prior call of the decorated callable with the exception raised by that
    # call if any (i.e., if that call raised an exception).
    args_flat_to_exception: dict[tuple, Exception] = {}

    # get() method of this dictionary, localized for efficiency.
    args_flat_to_exception_get = args_flat_to_exception.get

    # ....................{ CLOSURE                        }....................
    @wraps(func)
    def _callable_cached(*args):
        f'''
        Memoized variant of the {func.__name__}() callable.

        See Also
        --------
        :func:`.callable_cached`
            Further details.
        '''

        # Object representing all passed positional arguments to be used as the
        # key of various memoized dictionaries, defined as either...
        args_flat = (
            # If passed only one positional argument, minimize space consumption
            # by flattening this tuple of only that argument into that argument.
            # Since tuple items are necessarily hashable, this argument is
            # necessarily hashable and thus permissible as a dictionary key;
            args[0]
            if len(args) == 1 else
            # Else, one or more positional arguments are passed. In this case,
            # reuse this tuple as is.
            args
        )

        # Attempt to...
        try:
            # Exception raised by a prior call to the decorated callable when
            # passed these parameters *OR* the sentinel placeholder otherwise
            # (i.e., if this callable either has yet to be called with these
            # parameters *OR* has but failed to raise an exception).
            #
            # Note that:
            # * This statement raises a "TypeError" exception if any item of
            #   this flattened tuple is unhashable.
            # * A sentinel placeholder (e.g., "SENTINEL") is *NOT* needed here.
            #   The values of the "args_flat_to_exception" dictionary are
            #   guaranteed to *ALL* be exceptions. Since "None" is *NOT* an
            #   exception, disambiguation between "None" and valid dictionary
            #   values is *NOT* needed here. Although a sentinel placeholder
            #   could still be employed, doing so would slightly reduce
            #   efficiency for *NO* real-world gain.
            exception = args_flat_to_exception_get(args_flat)

            # If this callable previously raised an exception when called with
            # these parameters, re-raise the same exception.
            if exception:
                raise exception  # pyright: ignore
            # Else, this callable either has yet to be called with these
            # parameters *OR* has but failed to raise an exception.

            # Value returned by a prior call to the decorated callable when
            # passed these parameters *OR* a sentinel placeholder otherwise
            # (i.e., if this callable has yet to be passed these parameters).
            return_value = args_flat_to_return_value_get(args_flat, SENTINEL)

            # If this callable has already been called with these parameters,
            # return the value returned by that prior call.
            if return_value is not SENTINEL:
                return return_value
            # Else, this callable has yet to be called with these parameters.

            # Attempt to...
            try:
                # Call this parameter with these parameters and cache the value
                # returned by this call to these parameters.
                return_value = args_flat_to_return_value[args_flat] = func(
                    *args)
            # If this call raised an exception...
            except Exception as exception:
                # Cache this exception to these parameters.
                args_flat_to_exception[args_flat] = exception

                # Re-raise this exception.
                raise exception
        # If one or more objects either passed to *OR* returned from this call
        # are unhashable, perform this call as is *WITHOUT* memoization. While
        # non-ideal, stability is better than raising a fatal exception.
        except TypeError:
            #FIXME: If testing, emit a non-fatal warning or possibly even raise
            #a fatal exception. In either case, we want our test suite to notify
            #us about this.
            # print(f'Callable {repr(func)} caching failed on args: {args}')
            # from beartype._util.error.utilerrwarn import issue_warning
            # issue_warning(
            #     f'Callable {repr(func)} caching failed on args: {args}')

            return func(*args)

        # Return this value.
        return return_value

    # ....................{ RETURN                         }....................
    # Return this wrapper.
    return _callable_cached  # type: ignore[return-value]

# ....................{ DECORATORS ~ method                }....................
#FIXME: *BIG MISTAKE.* Woops. Under CPython, object IDs are (mostly) simply the
#underlying C-based memory addresses of those objects. Ergo, object IDs are
#unique *ONLY* for the duration of those objects.
#
#This makes this decorator fundamentally unsound. Refactor as follows, please:
#* Replace the two usages of this decorator in the
#  "beartype.door._cls.doorsuper" submodule with a manual caching scheme
#  leveraging a global dictionary mapping from the name to... *SOMETHING.* Sigh!
#* Permanently destroy this decorator and associated tests.
def method_cached_arg_by_id(func: CallableT) -> CallableT:
    '''
    **Memoize** (i.e., efficiently re-raise all exceptions previously raised by
    the decorated method when passed the same *exact* parameters (i.e.,
    parameters whose object IDs are equals) as a prior call to that method if
    any *or* return all values previously returned by that method otherwise
    rather than inefficiently recalling that method) the passed method.

    Caveats
    -------
    **This decorator is only intended to decorate bound methods** (i.e., either
    class or instance methods bound to a class or instance). This decorator is
    *not* intended to decorate functions or static methods.

    **This decorator is only intended to decorate a method whose sole argument
    is guaranteed to be a memoized singleton** (e.g.,
    :class:`beartype.door.TypeHint` singleton). In this case, the object ID of
    that argument uniquely identifies that argument across *all* calls to that
    method -- enabling this decorator to memoize that method. Conversely, if
    that argument is *not* guaranteed to be a memoized singleton, this decorator
    will fail to memoize that method while wasting considerable space and time
    attempting to do so. In short, care is warranted.

    This decorator is a micro-optimized variant of the more general-purpose
    :func:`callable_cached` decorator, which should be preferred in most cases.
    This decorator mostly exists for one specific edge case that the
    :func:`callable_cached` decorator *cannot* by definition support:
    user-defined classes implementing the ``__eq__`` dunder method to internally
    call another method decorated by :func:`callable_cached` accepting an
    instance of the same class. This design pattern appears astonishingly
    frequently, including in our prominent :class:`beartype.door.TypeHint`
    class. This edge case provokes infinite recursion. Consider this
    minimal-length example (MLE) exhibiting the issue:

    .. code-block:: python

       from beartype._util.cache.func.utilcachefunc import callable_cached

       class MuhClass(object):
           def __eq__(self, other: object) -> bool:
               return isinstance(other, MuhClass) and self._is_equal(other)

           @callable_cached
           def _is_equal(self, other: 'MuhClass') -> bool:
               return True

    :func:`callable_cached` internally caches the ``other`` argument passed to
    the ``_is_equal()`` method as keys of various internal dictionaries. When
    passed the same ``other`` argument, subsequent calls to that method lookup
    that ``other`` argument in those dictionaries. Since dictionary lookups
    implicitly call the ``other.__eq__()`` method to resolve key collisions
    *and* since the ``__eq__()`` method has been overridden in terms of the
    ``_is_equal()`` method, infinite recursion results.

    This decorator circumvents this issue by internally looking up the object
    identifier of the passed argument rather than that argument itself, which
    then avoids implicitly calling the ``__eq__()`` method of that argument.

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

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.func.utilfuncwrap import unwrap_func_all

    # ....................{ PREAMBLE                       }....................
    # Lowest-level wrappee callable wrapped by this wrapper callable.
    func_wrappee = unwrap_func_all(func)

    # If this wrappee accepts either zero, one, *OR* three or more flexible
    # parameters (i.e., parameters passable as either positional or keyword
    # arguments), raise an exception.
    die_unless_func_args_len_flexible_equal(
        func=func_wrappee,
        func_args_len_flexible=2,
        exception_cls=_BeartypeUtilCallableCachedException,
        # Avoid unnecessary callable unwrapping as a negligible optimization.
        is_unwrap=False,
    )
    # Else, this wrappee accepts exactly one flexible parameter.

    # If this wrappee accepts variadic arguments (either positional or keyword),
    # raise an exception.
    if is_func_arg_variadic(func_wrappee):
        raise _BeartypeUtilCallableCachedException(
            f'@method_cached_arg_by_id {label_callable(func)} '
            f'variadic arguments uncacheable.'
        )
    # Else, this wrappee accepts *NO* variadic arguments.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize against the @callable_cached decorator above. For
    # speed, this decorator violates DRY by duplicating logic.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # ....................{ LOCALS                         }....................
    # Dictionary mapping a tuple of all flattened parameters passed to each
    # prior call of the decorated callable with the value returned by that call
    # if any (i.e., if that call did *NOT* raise an exception).
    args_flat_to_return_value: dict[tuple, object] = {}

    # get() method of this dictionary, localized for efficiency.
    args_flat_to_return_value_get = args_flat_to_return_value.get

    # Dictionary mapping a tuple of all flattened parameters passed to each
    # prior call of the decorated callable with the exception raised by that
    # call if any (i.e., if that call raised an exception).
    args_flat_to_exception: dict[tuple, Exception] = {}

    # get() method of this dictionary, localized for efficiency.
    args_flat_to_exception_get = args_flat_to_exception.get

    # ....................{ CLOSURE                        }....................
    @wraps(func)
    def _method_cached(self_or_cls, arg):
        f'''
        Memoized variant of the {func.__name__}() callable.

        See Also
        --------
        :func:`callable_cached`
            Further details.
        '''

        # Object identifiers of the sole positional parameters passed to the
        # decorated method.
        args_flat = (id(self_or_cls), id(arg))

        # Attempt to...
        try:
            # Exception raised by a prior call to the decorated callable when
            # passed these parameters *OR* the sentinel placeholder otherwise
            # (i.e., if this callable either has yet to be called with these
            # parameters *OR* has but failed to raise an exception).
            #
            # Note that:
            # * This statement raises a "TypeError" exception if any item of
            #   this flattened tuple is unhashable.
            # * A sentinel placeholder (e.g., "SENTINEL") is *NOT* needed here.
            #   The values of the "args_flat_to_exception" dictionary are
            #   guaranteed to *ALL* be exceptions. Since "None" is *NOT* an
            #   exception, disambiguation between "None" and valid dictionary
            #   values is *NOT* needed here. Although a sentinel placeholder
            #   could still be employed, doing so would slightly reduce
            #   efficiency for *NO* real-world gain.
            exception = args_flat_to_exception_get(args_flat)

            # If this callable previously raised an exception when called with
            # these parameters, re-raise the same exception.
            if exception:
                raise exception  # pyright: ignore
            # Else, this callable either has yet to be called with these
            # parameters *OR* has but failed to raise an exception.

            # Value returned by a prior call to the decorated callable when
            # passed these parameters *OR* a sentinel placeholder otherwise
            # (i.e., if this callable has yet to be passed these parameters).
            return_value = args_flat_to_return_value_get(args_flat, SENTINEL)

            # If this callable has already been called with these parameters,
            # return the value returned by that prior call.
            if return_value is not SENTINEL:
                return return_value
            # Else, this callable has yet to be called with these parameters.

            # Attempt to...
            try:
                # Call this parameter with these parameters and cache the value
                # returned by this call to these parameters.
                return_value = args_flat_to_return_value[args_flat] = func(
                    self_or_cls, arg)
            # If this call raised an exception...
            except Exception as exception:
                # Cache this exception to these parameters.
                args_flat_to_exception[args_flat] = exception

                # Re-raise this exception.
                raise exception
        # If one or more objects either passed to *OR* returned from this call
        # are unhashable, perform this call as is *WITHOUT* memoization. While
        # non-ideal, stability is better than raising a fatal exception.
        except TypeError:
            #FIXME: If testing, emit a non-fatal warning or possibly even raise
            #a fatal exception. In either case, we want our test suite to notify
            #us about this.
            return func(self_or_cls, arg)

        # Return this value.
        return return_value

    # ....................{ RETURN                         }....................
    # Return this wrapper.
    return _method_cached  # type: ignore[return-value]


#FIXME: Uncomment to debug memoization-specific issues. *sigh*
# def callable_cached(func: _CallableT) -> _CallableT: return func
