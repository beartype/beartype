#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype cached exception handling utilities.**

This private submodule implements supplementary exception-handling utility
functions required by various :mod:`beartype` facilities, including callables
generating code for the :func:`beartype.beartype` decorator.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ CONSTANTS                         }....................
EXCEPTION_CACHED_PLACEHOLDER = '$%ROOT_PITH_LABEL/~'
'''
Default non-human-readable source substring to be globally replaced by the
target substring in the generic messages of memoized exceptions passed to the
:func:`reraise_exception` function.

Usage
----------
This substring is typically hard-coded into non-human-readable exception
messages raised by low-level callables memoized with the
:func:`beartype._util.cache.utilcachecall.callable_cached` decorator. Why?
Memoization prohibits those callables from raising human-readable exception
messages. Why? Doing so would require those callables to accept fine-grained
parameters unique to each call to those callables, which those callables would
then dynamically format into human-readable exception messages raised by those
callables. The standard example would be a ``hint_label`` parameter labelling
the human-readable category of type hint being inspected by the current call
(e.g., ``@beartyped muh_func() parameter "muh_param" PEP type hint "List[int]"``
for a ``List[int]`` type hint on the `muh_param` parameter of a ``muh_func()``
function decorated by the :func:`beartype.beartype` decorator). Since the whole
point of memoization is to cache callable results between calls, any callable
accepting any fine-grained parameter unique to each call to that callable is
effectively *not* memoizable in any meaningful sense of the adjective
"memoizable." Ergo, memoized callables *cannot* raise human-readable exception
messages unique to each call to those callables.

This substring indirectly solves this issue by inverting the onus of human
readability. Rather than requiring memoized callables to raise human-readable
exception messages unique to each call to those callables (which we've shown
above to be pragmatically infeasible), memoized callables instead raise
non-human-readable exception messages containing this substring where they
instead would have contained the human-readable portions of their messages
unique to each call to those callables. This indirection renders exceptions
raised by memoized callables generic between calls and thus safely memoizable.

This indirection has the direct consequence, however, of shifting the onus of
human readability from those lower-level memoized callables onto higher-level
non-memoized callables -- which are then required to explicitly (in order):

#. Catch exceptions raised by those lower-level memoized callables.
#. Call the :func:`reraise_exception_cached` function with those exceptions and
   the desired human-readable substring fragments. That function then:

   #. Replaces this magic substring hard-coded into those exception messages
      with those human-readable substring fragments.
   #. Reraises the original exceptions in a manner preserving their original
      tracebacks.

Unsurprisingly, as with most inversion of control schemes, this approach is
non-intuitive. Surprisingly, however, the resulting code is actually *more*
elegant than the standard approach of raising human-readable exceptions from
low-level callables. Why? Because the standard approach percolates
human-readable substring fragments from the higher-level callables defining
those fragments to the lower-level callables raising exception messages
containing those fragments. The indirect approach avoids percolation, thus
streamlining the implementations of all callables involved. Phew!
'''

# ....................{ RAISERS                           }....................
def reraise_exception_cached(
    # Mandatory parameters.
    exception: Exception,
    target_str: str,

    # Optional parameters.
    source_str: str = EXCEPTION_CACHED_PLACEHOLDER,
) -> None:
    '''
    Reraise the passed exception in a safe manner preserving both this
    exception object *and* the original traceback associated with this
    exception object, but globally replacing all instances of the passed source
    substring hard-coded into this exception's message with the passed target
    substring.

    Parameters
    ----------
    exception : Exception
        Exception to be reraised.
    target_str : str
        Target human-readable format substring to replace the passed source
        substring previously hard-coded into this exception's message.
    source_str : Optional[str]
        Source non-human-readable substring previously hard-coded into this
        exception's message to be replaced by the passed target substring.
        Defaults to :data:`EXCEPTION_CACHED_PLACEHOLDER`.

    Raises
    ----------
    exception
        The passed exception, globally replacing all instances of this source
        substring in this exception's message with this target substring.


    See Also
    ----------
    :data:`EXCEPTION_CACHED_PLACEHOLDER`
        Further commentary on usage and motivation.
    https://stackoverflow.com/a/62662138/2809027
        StackOverflow answer mildly inspiring this implementation.

    Examples
    ----------
        >>> from beartype.roar import BeartypeDecorHintPepException
        >>> from beartype._util.cache.utilcachecall import callable_cached
        >>> from beartype._util.cache.utilcacheerror import (
        ...     reraise_exception_cached, EXCEPTION_CACHED_PLACEHOLDER)
        >>> from random import getrandbits
        >>> @callable_cached
        ... def portend_low_level_winter(is_winter_coming: bool) -> str:
        ...     if is_winter_coming:
        ...         raise BeartypeDecorHintPepException(
        ...             '{} intimates that winter is coming.'.format(
        ...                 EXCEPTION_CACHED_PLACEHOLDER))
        ...     else:
        ...         return 'PRAISE THE SUN'
        >>> def portend_high_level_winter() -> None:
        ...     try:
        ...         print(portend_low_level_winter(is_winter_coming=False))
        ...         print(portend_low_level_winter(is_winter_coming=True))
        ...     except BeartypeDecorHintPepException as exception:
        ...         reraise_exception_cached(
        ...             exception=exception,
        ...             target_str=(
        ...                 'Random "Song of Fire and Ice" spoiler' if getrandbits(1) else
        ...                 'Random "Dark Souls" plaintext meme'
        ...             ))
        >>> portend_high_level_winter()
        PRAISE THE SUN
        Traceback (most recent call last):
          File "<input>", line 30, in <module>
            portend_high_level_winter()
          File "<input>", line 27, in portend_high_level_winter
            'Random "Dark Souls" plaintext meme'
          File "/home/leycec/py/beartype/beartype/_util/cache/utilcacheerror.py", line 225, in reraise_exception_cached
            raise exception.with_traceback(exception.__traceback__)
          File "<input>", line 20, in portend_high_level_winter
            print(portend_low_level_winter(is_winter_coming=True))
          File "/home/leycec/py/beartype/beartype/_util/cache/utilcachecall.py", line 296, in _callable_cached
            raise exception
          File "/home/leycec/py/beartype/beartype/_util/cache/utilcachecall.py", line 289, in _callable_cached
            *args, **kwargs)
          File "<input>", line 13, in portend_low_level_winter
            EXCEPTION_CACHED_PLACEHOLDER))
        beartype.roar.BeartypeDecorHintPepException: Random "Song of Fire and Ice" spoiler intimates that winter is coming.
    '''
    assert isinstance(exception, Exception), (
        '{!r} not exception.'.format(exception))
    assert isinstance(source_str, str), (
        'Source substring {!r} not string.'.format(source_str))
    assert isinstance(target_str, str), (
        'Target substring {!r} not string.'.format(target_str))

    # If...
    if (
        # Exception arguments are a tuple (as is typically but not necessarily
        # the case) *AND*...
        isinstance(exception.args, tuple) and
        # This tuple is non-empty (as is typically but not necessarily the
        # case) *AND*...
        exception.args and
        # The first item of this tuple is a string providing this exception's
        # message (as is typically but not necessarily the case)...
        isinstance(exception.args[0], str)
    # Then this is a conventional exception. In this case...
    ):
        # Munged exception message globally replacing all instances of this
        # source substring with this target substring.
        exception_message = exception.args[0].replace(source_str, target_str)

        # If doing so actually changed this message...
        if exception_message != exception.args[0]:
            # Reconstitute this exception argument tuple from this message.
            #
            # Note that if this tuple contains only this message, this slice
            # "exception.args[1:]" safely yields the empty tuple. Go, Python!
            exception.args = (exception_message,) + exception.args[1:]
        # Else, this message remains preserved as is.

    # Re-raise this exception while preserving its original traceback.
    raise exception.with_traceback(exception.__traceback__)
