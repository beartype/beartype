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

# ....................{ IMPORTS                           }....................
from beartype.roar import _BeartypeUtilCachedTextException

# ....................{ CONSTANTS                         }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Synchronize changes to this global constant with the corresponding
# string embedded into the body of the format_text_cached() function.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
CACHED_FORMAT_VAR_NAME = 'cached_format_var'
'''
Name of the format variable embedded in the magic
:data:`CACHED_FORMAT_VAR` string constant.
'''


CACHED_FORMAT_VAR = '{' + CACHED_FORMAT_VAR_NAME + '}'
'''
``{``- and ``}``-delimited format variable substring to be replaced by default
by the :func:`reraise_exception` function.

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
#. Call the :func:`reraise_exception` function with those exceptions and the
   desired human-readable substring fragments. That function then:

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

# ....................{ FORMATTERS                        }....................
def format_text_cached(
    # Mandatory parameters.
    text: str,
    format_str: str,

    # Optional parameters.
    format_var: str = CACHED_FORMAT_VAR,
) -> None:
    '''
    The passed text formatted such that all substrings matching the passed
    format variable in this text are globally replaced with the passed format
    substring if this text contains one or more such substrings *or* this text
    preserved as is otherwise (i.e., if this text contains no such substrings).

    Parameters
    ----------
    text : str
        Text to be formatted.
    format_str : str
        Human-readable format substring to replace the passed format variable
        previously hard-coded into this text.
    format_var : str
        Non-human-readable ``{``- and ``}``-delimited format variable substring
        previously hard-coded into this text to be replaced by the passed
        format substring. Defaults to the :data:`CACHED_FORMAT_VAR` magic
        substring.

    Returns
    ----------
    str
        This text formatted such that all substrings matching this format
        variable in this text are globally replaced with this format substring.

    Raises
    ----------
    _BeartypeUtilCachedTextException
        If this format variable is *not* ``{``- and ``}``-delimited.

    See Also
    ----------
    :data:`CACHED_FORMAT_VAR`
        Further commentary on usage and motivation.
    '''
    assert isinstance(text, str), '{!r} not string.'.format(text)
    assert isinstance(format_str, str), (
        '{!r} not format substring.'.format(format_str))
    assert isinstance(format_var, str), (
        '{!r} not format variable.'.format(format_var))

    # If this format variable is the magic "CACHED_FORMAT_VAR" constant,
    # format this string with an optimized code path.
    if format_var is CACHED_FORMAT_VAR:
        # Return either...
        return (
            # If this text contains this format variable substring, reformat
            # this text by replacing all instances of this format variable in
            # this text with this format substring.
            #
            # Note that this test is *NOT* simply an optimization but is, in
            # fact, required to prevent the str.format() method from raising a
            # non-human-readable "KeyError" exception in the common case that
            # this text does *NOT* contain this format variable.
            text.format(cached_format_var=format_str)
            if format_var in text
            # Else, this text does *NOT* contain this format variable. In this
            # case, preserve this text as is.
            else text
        )
    # Else, this format variable is *NOT* the magic "CACHED_FORMAT_VAR"
    # constant. In this case, we do this the harder, slower, worse way...
    else:
        assert isinstance(format_var, str), (
            '{!r} not format variable substring.'.format(format_var))

        # If this string is *NOT* "{"- and "}"-delimited, raise an exception.
        if not (
            format_var[ 0] == '{' and
            format_var[-1] == '}'
        ):
            raise _BeartypeUtilCachedTextException(
                'Format variable "{}" not delimited by "{{" and "}}".'.format(
                    format_var))

        # Name of this format variable stripped of "{" and "}" delimiters.
        format_var_name = format_var[1:-1]

        # If this text contains this format variable substring...
        #
        # Note that this test is *NOT* simply an optimization but is, in fact,
        # required to prevent the str.format() method from raising a
        # non-human-readable "KeyError" exception in the common case that this
        # text does *NOT* contain this format variable.
        if format_var in text:
            # Dictionary mapping from the name of this format variable to this
            # format substring to be passed to the str.format() method below.
            #
            # Note that this indirection is required, as "format_var_name" is
            # dynamically passed at call time and thus *CANNOT* be directly
            # passed as a keyword argument to the str.format() method below.
            format_var_replacement = {format_var_name: format_str}

            # Reformat this text by replacing all instances of this format
            # variable in this text with this format substring.
            text = text.format(**format_var_replacement)
        # Else, this text does *NOT* contain this format variable. In this
        # case, preserve this text as is.

    # Return this possibly formatted text.
    return text

# ....................{ RAISERS                           }....................
def reraise_exception_cached(
    # Mandatory parameters.
    exception: Exception,
    format_str: str,

    # Optional parameters.
    format_var: str = CACHED_FORMAT_VAR,
) -> None:
    '''
    Reraise the passed exception in a safe manner preserving both this
    exception object *and* the original traceback associated with this
    exception object, but reformatting the passed format variable hard-coded
    into this exception's message with the passed format substring if this
    message contains one or more substrings matching this variable *or*
    preserving this message as is otherwise (i.e., if this message contains no
    substrings matching this variable).

    Parameters
    ----------
    exception : Exception
        Exception to be reraised.
    format_str : str
        Human-readable format substring to replace the passed format variable
        previously hard-coded into this exception's message.
    format_var : str
        Non-human-readable ``{``- and ``}``-delimited format variable substring
        previously hard-coded into this exception's message to be replaced by
        the passed format substring. Defaults to the
        :data:`CACHED_FORMAT_VAR` magic substring.

    Raises
    ----------
    _BeartypeUtilCachedTextException
        If one or more passed parameters are invalid, including:

        * If this format variable is *not* ``{``- and ``}``-delimited.
        * If the standard ``exception.args`` attribute of this exception is
          either not a tuple *or* or is but is the empty tuple.
        * If the first item of this tuple is *not* a string.
    exception
        If this function otherwise succeeds (i.e., does *not* raise a
        :class:`_BeartypeUtilCachedTextException` exception).

    See Also
    ----------
    :data:`CACHED_FORMAT_VAR`
        Further commentary on usage and motivation.
    https://stackoverflow.com/a/62662138/2809027
        StackOverflow answer mildly inspiring this implementation.

    Examples
    ----------
        >>> from beartype.roar import BeartypeDecorHintPepException
        >>> from beartype._util.cache.utilcachecall import callable_cached
        >>> from beartype._util.cache.utilcachetext import (
        ...     reraise_exception_cached, CACHED_FORMAT_VAR)
        >>> from random import getrandbits
        >>> @callable_cached
        ... def portend_low_level_winter(is_winter_coming: bool) -> str:
        ...     if is_winter_coming:
        ...         raise BeartypeDecorHintPepException(
        ...             '{} intimates that winter is coming.'.format(
        ...                 CACHED_FORMAT_VAR))
        ...     else:
        ...         return 'PRAISE THE SUN'
        >>> def portend_high_level_winter() -> None:
        ...     try:
        ...         print(portend_low_level_winter(is_winter_coming=False))
        ...         print(portend_low_level_winter(is_winter_coming=True))
        ...     except BeartypeDecorHintPepException as exception:
        ...         reraise_exception_cached(
        ...             exception=exception,
        ...             format_str=(
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
          File "/home/leycec/py/beartype/beartype/_util/cache/utilcachetext.py", line 225, in reraise_exception_cached
            raise exception.with_traceback(exception.__traceback__)
          File "<input>", line 20, in portend_high_level_winter
            print(portend_low_level_winter(is_winter_coming=True))
          File "/home/leycec/py/beartype/beartype/_util/cache/utilcachecall.py", line 296, in _callable_cached
            raise exception
          File "/home/leycec/py/beartype/beartype/_util/cache/utilcachecall.py", line 289, in _callable_cached
            *args, **kwargs)
          File "<input>", line 13, in portend_low_level_winter
            CACHED_FORMAT_VAR))
        beartype.roar.BeartypeDecorHintPepException: Random "Song of Fire and Ice" spoiler intimates that winter is coming.
    '''
    # Note that the format_text_cached() function called below validates both
    # the "format_str" and "format_var" parameters.
    assert isinstance(exception, Exception), (
        '{!r} not exception.'.format(exception))

    # If exception arguments are *NOT* a tuple, raise an exception.
    if not isinstance(exception.args, tuple):
        raise _BeartypeUtilCachedTextException(
            'Exception {!r} arguments {!r} not tuple.'.format(
                exception, exception.args)) from exception
    # Else, exception arguments are a tuple.
    #
    # If the exception argument tuple is empty, raise an exception.
    elif not exception.args:
        raise _BeartypeUtilCachedTextException(
            'Exception {!r} argument tuple empty.'.format(exception)
        ) from exception
    # Else, the exception argument tuple is non-empty.
    #
    # If this exception message is *NOT* a string, raise an exception.
    elif not isinstance(exception.args[0], str):
        raise _BeartypeUtilCachedTextException(
            'Exception {!r} first argument {!r} not '
            'exception message.'.format(exception, exception.args[0])
        ) from exception
    # Else, this exception message is a string.

    # Exception message possibly reformatted.
    exception_message = format_text_cached(
        text=exception.args[0],
        format_str=format_str,
        format_var=format_var,
    )

    # If this message was reformatted...
    if exception_message != exception.args[0]:
        # Reconstitute this exception argument tuple from this message.
        #
        # Note that if this tuple contains only this message, this slice
        # "exception.args[1:]" safely yields the empty tuple. Thanks, Python!
        exception.args = (exception_message,) + exception.args[1:]
    # Else, this message was *NOT* reformatted. In this case, preserve this
    # message as is.

    # Re-raise this exception while preserving its original traceback.
    raise exception.with_traceback(exception.__traceback__)
