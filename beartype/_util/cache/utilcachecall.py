#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable caching utilities** (i.e., low-level callables
performing general-purpose memoization of function and method calls).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Generalize @callable_cached to revert to the body of the
#@betse._util.type.decorator.decmemo.func_cached decorator when the passed
#callable accepts *NO* parameters, which can be trivially decided by inspecting
#the code object of this callable. Why do this? Because the @func_cached
#decorator is *INSANELY* fast for this edge case -- substantially faster than
#the current general-purpose @callable_cached approach.

#FIXME: Generalize @callable_cached to support variadic parameters by appending
#to "params_flat":
#  1. A placeholder sentinel object after all positional and keyword arguments.
#  2. Those variadic parameters.

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableCachedException
from beartype.roar._roarwarn import _BeartypeUtilCallableCachedKwargsWarning
from beartype.typing import (
    Dict,
    TypeVar,
)
from beartype._util.func.arg.utilfuncargtest import (
    # is_func_argless,
    is_func_arg_variadic,
)
from beartype._util.text.utiltextlabel import label_callable
from beartype._util.utilobject import (
    SENTINEL,
    Iota,
)
from collections.abc import Callable
from functools import wraps
from warnings import warn

# ....................{ PRIVATE ~ hints                    }....................
_CallableT = TypeVar('_CallableT', bound=Callable)
'''
Type variable bound to match *only* callables.
'''

# ....................{ DECORATORS                         }....................
def callable_cached(func: _CallableT) -> _CallableT:
    '''
    **Memoize** (i.e., efficiently cache and return all previously returned
    values of the passed callable as well as all previously raised exceptions
    of that callable previously rather than inefficiently recalling that
    callable) the passed callable.

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
    ----------
    **The decorated callable must accept no variadic parameters** (i.e.,
    either variadic positional or keyword arguments). While memoizing variadic
    parameters would of course be feasible, this decorator has yet to implement
    support for memoizing variadic parameters.

    **The decorated callable should not be a property method** (i.e., either a
    property getter, setter, or deleter subsequently decorated by the
    :class:`property` decorator). Technically, this decorator *can* be used to
    memoize property methods; pragmatically, doing so would be sufficiently
    inefficient as to defeat the intention of memoizing in the first place.

    **Order of keyword arguments passed to the decorated callable is
    significant.** This decorator recaches return values produced by calls to
    the decorated callable when passed the same keyword arguments in differing
    order (e.g., ``muh_func(muh_kw=0, mah_kw=1)`` and ``muh_func(mah_kw=1,
    muh_kw=0)``, cached as two distinct calls by this decorator despite these
    calls ultimately receiving the same arguments).

    Efficiency
    ----------
    For efficiency, consider calling the decorated callable with only:

    * **Positional arguments.** While technically supported, every call to the
      decorated callable passed one or more keyword arguments reduces both the
      space and time efficiency of the memoization performed by that callable.
    * **Hashable** (i.e., immutable) arguments. While technically supported,
      every call to the decorated callable passed one or more unhashable
      arguments (e.g., mutable containers like lists and dictionaries) will
      *not* be memoized. Equivalently, only calls passed only hashable
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
    in the special case of unbounded caching with ``maxsize=None``, mostly as
    that decorator insists on unconditionally recording irrelevant statistics
    such as cache misses and hits. While bounding the number of cached values
    is advisable in the general case (e.g., to avoid exhausting memory merely
    for optional caching), the callable parameters and return values cached by
    this package are sufficiently small in size to render bounding irrelevant.

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
    func : _CallableT
        Callable to be memoized.

    Returns
    ----------
    _CallableT
        Closure wrapping this callable with memoization.

    Raises
    ----------
    _BeartypeUtilCallableCachedException
        If any parameter passed to this callable is **variadic**, including:

        * A variadic positional argument resembling ``*args``.
        * A variadic keyword argument resembling ``**kwargs``.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Avoid circular import dependencies.
    from beartype._util.func.utilfuncwrap import unwrap_func

    # Lowest-level wrappee callable wrapped by this wrapper callable.
    func_wrappee = unwrap_func(func)

    # If this wrappee accepts variadic arguments, raise an exception.
    if is_func_arg_variadic(func_wrappee):
        raise _BeartypeUtilCallableCachedException(
            f'@callable_cached {label_callable(func)} '
            f'variadic arguments uncacheable.'
        )
    # Else, this wrappee accepts *NO* variadic arguments.

    # Dictionary mapping a tuple of all flattened parameters passed to each
    # prior call of the decorated callable with the value returned by that call
    # if any (i.e., if that call did *NOT* raise an exception).
    params_flat_to_return_value: Dict[tuple, object] = {}

    # get() method of this dictionary, localized for efficiency.
    params_flat_to_return_value_get = params_flat_to_return_value.get

    # Dictionary mapping a tuple of all flattened parameters passed to each
    # prior call of the decorated callable with the exception raised by that
    # call if any (i.e., if that call raised an exception).
    params_flat_to_exception: Dict[tuple, Exception] = {}

    # get() method of this dictionary, localized for efficiency.
    params_flat_to_exception_get = params_flat_to_exception.get

    @wraps(func)
    def _callable_cached(*args, **kwargs):
        f'''
        Memoized variant of the {func.__name__}() callable.

        Warns
        ----------
        _BeartypeUtilCallableCachedKwargsWarning
            If one or more keyword arguments were passed. While technically
            supported, keyword arguments are substantially more space- and
            time-intensive to memoize than equivalent positional arguments,
            partially defeating the purpose of memoization in the first place.

        See Also
        ----------
        :func:`callable_cached`
            Further details.
        '''

        # Flatten the passed tuple of positional arguments and dictionary of
        # keyword arguments into a single tuple containing both positional and
        # keyword arguments. To minimize space consumption, this tuple contains
        # these arguments as is with *NO* nested containers.
        #
        # For example, when a decorated callable with signature:
        #    def muh_func(muh_arg1, muh_arg2, muh_arg3, muh_arg4)
        # ...is called as:
        #    muh_func('a', 'b', muh_arg3=0, muh_arg4=1)
        # ...this closure receives these variadic arguments:
        #    *args = ('a', 'b')
        #    *kwargs = {'muh_arg3': 0, 'muh_arg4': 1}
        # ...which the following logic flattens into this tuple:
        #    params_flat = (
        #        'a', 'b',
        #        _SENTINEL_KWARGS_KEYS, 'muh_arg3', 'muh_arg4',
        #        _SENTINEL_KWARGS_VALUES, 0, 1,
        #    )
        #
        # If one or more keyword arguments are passed, construct this flattened
        # tuple by concatenating together:
        #
        # * The passed tuple of positional arguments.
        # * A sentinel tuple differentiating the preceding positional arguments
        #   from subsequent keyword argument names.
        # * The names of all passed keyword arguments coerced into a tuple.
        # * A sentinel tuple differentiating the preceding keyword argument
        #   names from subsequent keyword argument values.
        # * The values of all passed keyword arguments coerced into a tuple.
        if kwargs:
            params_flat = (
                args +
                _SENTINEL_KWARGS_KEYS   + tuple(kwargs.keys()) +
                _SENTINEL_KWARGS_VALUES + tuple(kwargs.values())
            )

            # Emit a non-fatal warning to warn callers of the performance
            # pitfalls associated with memoizing keyword arguments.
            warn(
                (
                    f'@callable_cached {func.__name__}() inefficiently passed '
                    f'keyword arguments: {kwargs}'
                ),
                _BeartypeUtilCallableCachedKwargsWarning
            )
        # Else, only positional arguments are passed.
        #
        # If passed only one positional argument, minimize space consumption by
        # flattening this tuple of only that argument into that argument. Since
        # tuple items are necessarily hashable, this argument is necessarily
        # hashable as well and thus permissible as a dictionary key below.
        elif len(args) == 1:
            params_flat = args[0]
        # Else, one or more positional arguments are passed. In this case,
        # reuse this tuple as is.
        else:
            params_flat = args

        # Attempt to...
        try:
            #FIXME: Optimize the params_flat_to_exception_get() case, please.
            #Since "None" is *NOT* a valid exception, we shouldn't need a
            #sentinel for safety here. Instead, this should suffice:
            #    exception = params_flat_to_exception_get(params_flat)
            #
            #    # If this callable previously raised an exception when called with
            #    # these parameters, re-raise the same exception.
            #    if exception:
            #        raise exception

            # Exception raised by a prior call to the decorated callable when
            # passed these parameters *OR* the sentinel placeholder otherwise
            # (i.e., if this callable either has yet to be called with these
            # parameters *OR* has but failed to raise an exception).
            #
            # Note that this call raises a "TypeError" exception if any item of
            # this flattened tuple is unhashable.
            exception = params_flat_to_exception_get(params_flat, SENTINEL)

            # If this callable previously raised an exception when called with
            # these parameters, re-raise the same exception.
            if exception is not SENTINEL:
                raise exception  # pyright: ignore[reportGeneralTypeIssues]
            # Else, this callable either has yet to be called with these
            # parameters *OR* has but failed to raise an exception.

            # Value returned by a prior call to the decorated callable when
            # passed these parameters *OR* a sentinel placeholder otherwise
            # (i.e., if this callable has yet to be passed these parameters).
            return_value = params_flat_to_return_value_get(
                params_flat, SENTINEL)

            # If this callable has already been called with these parameters,
            # return the value returned by that prior call.
            if return_value is not SENTINEL:
                return return_value
            # Else, this callable has yet to be called with these parameters.

            # Attempt to...
            try:
                # Call this parameter with these parameters and cache the value
                # returned by this call to these parameters.
                return_value = params_flat_to_return_value[params_flat] = func(
                    *args, **kwargs)
            # If this call raises an exception...
            except Exception as exception:
                # Cache this exception to these parameters.
                params_flat_to_exception[params_flat] = exception

                # Re-raise this exception.
                raise exception
        # If one or more objects either passed to *OR* returned from this call
        # are unhashable, perform this call as is *WITHOUT* memoization. While
        # non-ideal, stability is better than raising a fatal exception.
        except TypeError:
            return func(*args, **kwargs)

        # Return this value.
        return return_value

    # Return this wrapper.
    return _callable_cached  # type: ignore[return-value]


def property_cached(func: _CallableT) -> _CallableT:
    '''
    **Memoize** (i.e., efficiently cache and return all previously returned
    values of the passed property method as well as all previously raised
    exceptions of that method previously rather than inefficiently recalling
    that method) the passed **property method method** (i.e., either a property
    getter, setter, or deleter subsequently decorated by the :class:`property`
    decorator).

    On the first access of a property decorated with this decorator (in order):

    #. The passed method implementing this property is called.
    #. The value returned by this property is internally cached into a private
       attribute of the object to which this method is bound.
    #. This value is returned.

    On each subsequent access of this property, this cached value is returned as
    is *without* calling this method. Hence, this method is called at most once
    for each object exposing this property.

    Caveats
    ----------
    **This decorator must be preceded by an explicit usage of the standard**
    :class:`property` **decorator.** Although this decorator could be trivially
    refactored to automatically decorate the returned property method by the
    :class:`property` decorator, doing so would violate static type-checking
    expectations -- introducing far more issues than it would solve.

    **This decorator should always be preferred over the standard**
    :func:`functools.cached_property` **decorator available under Python >=
    3.8.** This decorator is substantially more efficient in both space and time
    than that decorator -- which is, of course, the entire point of caching.

    **This decorator does not destroy bound property methods.** Technically,
    the most efficient means of caching a property value into an instance is to
    replace the property method currently bound to that instance with an
    instance variable initialized to that value (e.g., as documented by this
    `StackOverflow answer`_). Since a property should only ever be treated as an
    instance variable, there superficially exists little harm in dynamically
    changing the type of the former to the latter. Sadly, doing so introduces
    numerous subtle issues with no plausible workaround. In particular,
    replacing property methods by instance variables:

    * Permits callers to erroneously set **read-only properties** (i.e.,
      properties lacking setter methods), a profound violation of one of the
      principle use cases for properties.
    * Prevents pickling logic elsewhere from automatically excluding cached
      property values, forcing these values to *always* be pickled to disk.
      This is bad. Cached property values are *always* safely recreatable in
      memory (and hence need *not* be pickled) and typically space-consumptive
      in memory (and hence best *not* pickled). The slight efficiency gain from
      replacing property methods by instance variables is hardly worth the
      significant space loss from pickling these variables.

    .. _StackOverflow answer:
        https://stackoverflow.com/a/36684652/2809027

    Parameters
    ----------
    func : _CallableT
        Property method to be memoized.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Name of the private instance variable to which this decorator caches the
    # value returned by the decorated property method.
    property_var_name = (
        _PROPERTY_CACHED_VAR_NAME_PREFIX + func.__name__)

    # Raw string of Python statements comprising the body of this wrapper,
    # including (in order):
    #
    # * A "@wraps" decorator propagating the name, docstring, and other
    #   identifying metadata of the original function to this wrapper.
    # * A private "__property_method" parameter initialized to this function.
    #   In theory, the "func" parameter passed to this decorator
    #   should be accessible as a closure-style local in this wrapper. For
    #   unknown reasons (presumably, a subtle bug in the exec() builtin), this
    #   is not the case. Instead, a closure-style local must be simulated by
    #   passing the "func" parameter to this function at function
    #   definition time as the default value of an arbitrary parameter.
    #
    # While there exist numerous alternative implementations for caching
    # properties, the approach implemented below has been profiled to be the
    # most efficient. Alternatives include (in order of decreasing efficiency):
    #
    # * Dynamically getting and setting a property-specific key-value pair of
    #   the internal dictionary for the current object, timed to be
    #   approximately 1.5 times as slow as exception handling: e.g.,
    #
    #     if not {property_name!r} in self.__dict__:
    #         self.__dict__[{property_name!r}] = __property_method(self)
    #     return self.__dict__[{property_name!r}]
    #
    # * Dynamically getting and setting a property-specific attribute of
    #   the current object (e.g., the internal dictionary for the current
    #   object), timed to be approximately 1.5 times as slow as exception
    #   handling: e.g.,
    #
    #     if not hasattr(self, {property_name!r}):
    #         setattr(self, {property_name!r}, __property_method(self))
    #     return getattr(self, {property_name!r})
    #
    # Lastly, note that this implementation intentionally avoids calling our
    # higher-level beartype._util.func.utilfuncmake.make_func() factory function
    # for dynamically generating functions. Although this implementation could
    # certainly be refactored in terms of that factory, doing so would
    # needlessly reduce debuggability and portability for *NO* tangible gain.
    func_body = '''
@wraps(__property_method)
def property_method_cached(self, __property_method=__property_method):
    try:
        return self.{property_var_name}
    except AttributeError:
        self.{property_var_name} = __property_method(self)
        return self.{property_var_name}
'''.format(property_var_name=property_var_name)

    # Dictionary mapping from local attribute names to values. For efficiency,
    # only attributes required by the body of this wrapper are copied from the
    # current namespace. (See below.)
    local_attrs = {'__property_method': func}

    # Dynamically define this wrapper as a closure of this decorator. For
    # obscure and presumably uninteresting reasons, Python fails to locally
    # declare this closure when the locals() dictionary is passed; to capture
    # this closure, a local dictionary must be passed instead.
    exec(func_body, globals(), local_attrs)

    # Return this wrapper method.
    return local_attrs['property_method_cached']

# ....................{ PRIVATE ~ constants : var          }....................
_CALLABLE_CACHED_VAR_NAME_PREFIX = '_betse_cached__'
'''
Substring prefixing the names of all private instance variables to which all
caching decorators (e.g., :func:`property_cached`) cache values returned by
decorated callables.

This prefix guarantees uniqueness across *all* instances -- including those
instantiated from official Python and unofficial third-party classes and those
internally defined by this application. Doing so permits logic elsewhere (e.g.,
pickling filtering) to uniquely match and act upon these variables.
'''


_FUNCTION_CACHED_VAR_NAME = (
    f'{_CALLABLE_CACHED_VAR_NAME_PREFIX}function_value')
'''
Name of the private instance variable to which the :func:`func_cached`
decorator statically caches the value returned by the decorated function.
'''


_PROPERTY_CACHED_VAR_NAME_PREFIX = (
    f'{_CALLABLE_CACHED_VAR_NAME_PREFIX}property_')
'''
Substring prefixing the names of all private instance variables to which the
:func:`property_cached` decorator dynamically caches the value returned by the
decorated property method.
'''
# ....................{ PRIVATE ~ constant : sentinel      }....................
_SENTINEL_KWARGS_KEYS = (Iota(),)
'''
Sentinel tuple signifying subsequent keyword argument names.

This tuple is internally leveraged by the :func:`callable_cached` decorator to
differentiate keyword argument names from preceding positional arguments in the
flattened tuple of all parameters passed to the decorated callable.
'''


_SENTINEL_KWARGS_VALUES = (Iota(),)
'''
Sentinel tuple signifying subsequent keyword argument values.

This tuple is internally leveraged by the :func:`callable_cached` decorator to
differentiate keyword argument names from preceding positional arguments in the
flattened tuple of all parameters passed to the decorated callable.
'''
