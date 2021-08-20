#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

"""
Project-wide **string munging** (i.e., generic low-level operations
transforming strings into new derivative strings) utilities.

This private submodule is *not* intended for importation by downstream callers.
"""

# ....................{ IMPORTS                           }....................
from beartype.roar._roarwarn import _BeartypeUtilCallableWarning
from beartype._util.utilobject import get_object_scopes_name
from collections.abc import Callable
from pprint import saferepr
from re import (
    DOTALL,
    sub as re_sub
)
from string import punctuation

# ....................{ REPRESENTERS                      }....................
def represent_object(
    # Mandatory parameters.
    obj: object,

    # Optional parameters.
    max_len: int = 76,
    is_strip_from_newline_first: bool = True,
) -> str:
    """
    Pretty-printed quasi-human-readable variant of the string returned by the
    non-pretty-printed machine-readable :meth:`obj.__repr__` dunder method of
    the passed object, truncated to the passed maximum string length.

    Specifically, this function (in order):

    #. Obtains this object's representation by calling ``repr(object)``.
    #. If this representation is neither suffixed by a punctuation character
       (i.e., character in the standard :attr:`string.punctuation` set) *nor*
       representing a byte-string whose representations are prefixed by `b'`
       and suffixed by `'` (e.g., `b'Check, mate.'`), double-quotes this
       representation for disambiguity with preceding characters -- notably,
       sequence indices. Since strings returned by this function commonly
       follow sequence indices in error messages, failing to disambiguate the
       two produces non-human-readable output:

           >>> def wat(mate: typing.List[str]) -> int: return len(mate)
           >>> raise_pep_call_exception(
           ...     func=muh_func, pith_name='mate', pith_value=[7,])
           beartype.roar.BeartypeCallHintPepParamException: @beartyped wat()
           parameter mate=[7] violates PEP type hint typing.List[str], as list
           item 0 value 7 not a str.

       Note the substring "item 0 value 7", which misreads like a blatant bug.
       Double-quoting the "7" suffices to demarcate values from indices.
    #. If this representation exceeds the passed maximum length, replaces the
       suffix of this representation exceeding this length with an ellipses
       (i.e., `"..."` substring).

    Caveats
    ----------
    **This function is unavoidably slow and should thus not be called from
    optimized performance-critical code.** This function internally performs
    mildly expensive operations, including regular expression-based matching
    and substitution. Ideally, this function should *only* be called to create
    user-oriented exception messages where performance is a negligible concern.

    **This function preserves all quote-protected newline characters** (i.e.,
    ``"\\n"``) **in this representation.** Since the :meth:`str.__repr__`
    dunder method implicitly quote-protects all newlines in the original
    string, this function effectively preserves all newlines in strings.

    Parameters
    ----------
    obj : object
        Object to be represented.
    max_len: int, optional
        Maximum length of the string to be returned. Defaults to a standard
        line length of 80 characters minus output indentation of 4 characters.

    Returns
    ----------
    str
        Pretty-printed quasi-human-readable variant of this object's
        non-pretty-printed machine-readable representation.
    """
    assert isinstance(max_len, int), f'{repr(max_len)} not integer.'

    # String describing the passed object. Note that:
    # * This Representation quote-protects all newlines in this representation.
    #   Ergo, "\n" *MUST* be matched as r"\n" instead below.
    # * For debuggability, the verbose (albeit less readable) output of repr()
    #   is preferred to the terse (albeit more readable) output of str().
    # * For safety, the saferepr() function explicitly protected against
    #   recursive data structures is preferred to the unsafe repr() builtin
    #   *NOT* protected against such recursion.
    obj_repr = saferepr(obj)

    # If this representation is empty, return empty double-quotes. Although
    # most objects (including outlier singletons like "None" and the empty
    # string) have non-empty representations, caller-defined classes may
    # maliciously override the __repr__() dunder method to return an empty
    # string rather than the representation of an empty string (i.e., '""').
    if not obj_repr:
        return '""'
    # Else, this representation is non-empty.
    #
    # If this representation is neither...
    elif not (
        # Prefixed by punctuation *NOR*...
        obj_repr[0] in punctuation or
        # A byte-string, in which case this representation is instead prefixed
        # by "b'".
        isinstance(obj, bytes)
    ):
    # Then this representation is *NOT* demarcated from preceding characters in
    # the parent string embedding this representation. In this case,
    # double-quote this representation for disambiguity with preceding
    # characters (e.g., sequence indices).
        obj_repr = f'"{obj_repr}"'

    # If this representation exceeds this maximum length...
    if len(obj_repr) > max_len:
        # If this maximum length is long enough to at least allow truncation to
        # ellipses (i.e., a substring of length 3)...
        if max_len > 3:
            #FIXME: Consider compiling and caching this regex into a module
            #dictionary mapping from "max_len" values to compiled regexes.

            # Uncompiled regular expression grouping zero or more leading
            # characters preceding this maximum length *AND* zero or more
            # trailing delimiters.
            #
            # Note that:
            # * This expression conditionally depends on a passed parameter and
            #   thus *CANNOT* be compiled as a module-scoped global.
            # * Efficiency is *NOT* a consideration for this function, which is
            #   only called in the edge-case event of a runtime error.
            PRE_MAX_CHARS_LAST_DELIMITERS_REGEX = (
                # Group anchored at the string start preserving a maximum
                # number (excluding the length required to inject an ellipses)
                # minus one to account for the fact that both bounds of the
                # "{...,...}" range operator are inclusive) of any characters.
                r'^(.{0,'
                f'{max_len - 4}'
                r'})'
                # Ungrouped remainder to be truncated.
                r'.*?'
                # Group anchored at the string end preserving zero or more
                # trailing delimiters.
                r'([\'")}>\]]*)$'
            )

            # Replace the substring of this representation from whichever of the
            # first character following this maximum length or the first newline
            # occurs first to the string end (excluding any optional trailing
            # delimiters) with a single ellipses.
            obj_repr = re_sub(
                PRE_MAX_CHARS_LAST_DELIMITERS_REGEX,
                r'\1...\2',
                obj_repr,
                flags=DOTALL,
            )
        # Else, this maximum length is *NOT* long enough to at least allow
        # truncation to ellipses (i.e., a substring of length 3). In this case,
        # truncate this string to this length *WITHOUT* ellipses.
        else:
            obj_repr = obj_repr[:max_len]
        # print(f'obj repr truncated: {obj_repr}')

    # Return this representation.
    return obj_repr

# ....................{ REPRESENTER ~ callable            }....................
def represent_func(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    warning_cls: type = _BeartypeUtilCallableWarning,
) -> str:
    '''
    Machine-readable representation of the passed callable.

    Caveats
    ----------
    **This function is unavoidably slow and should thus not be called from
    optimized performance-critical code.** This function internally performs
    extremely expensive operations, including abstract syntax tree (AST)-based
    parsing of Python scripts and modules deserialized from disk. Ideally, this
    function should *only* be called to create user-oriented exception messages
    where performance is a negligible concern.

    Parameters
    ----------
    func : Callable
        Callable to be represented.
    warning_cls : type, optional
        Type of warning to be emitted in the event of a non-fatal error.
        Defaults to :class:`_BeartypeUtilCallableWarning`.

    Warns
    ----------
    warning_cls
        If this callable is a pure-Python lambda function whose definition is
        *not* parsable from the script or module defining that lambda.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunccode import get_func_code_or_none
    from beartype._util.func.utilfunctest import is_func_lambda

    # Return either...
    return (
        # If this callable is a pure-Python lambda function, either:
        # * If this lambda is defined by an on-disk script or module source
        #   file, the exact substring of that file defining this lambda.
        # * Else (e.g., if this lambda is dynamically defined in-memory), a
        #   placeholder string.
        get_func_code_or_none(func=func, warning_cls=warning_cls) or '<lambda>'
        if is_func_lambda(func) else
        # Else, this callable is *NOT* a pure-Python lambda function. In this
        # case, the fully-qualified name of this non-lambda function.
        f'{get_object_scopes_name(func)}()'
    )
