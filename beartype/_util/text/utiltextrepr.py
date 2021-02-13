#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Cecil Curry.
# See "LICENSE" for further details.

"""
**Beartype string munging utilities** (i.e., callables transforming passed
strings into new strings with generic string operations).

This private submodule is *not* intended for importation by downstream callers.
"""

# ....................{ IMPORTS                           }....................
import re
from string import punctuation

# ....................{ GETTERS                           }....................
def get_object_representation(obj: object, max_len: int = 76) -> str:
    """
    Pretty-printed quasi-human-readable variant of the string returned by the
    non-pretty-printed machine-readable :meth:`obj.__repr__` dunder method of
    the passed object, truncated to the passed maximum string length.

    Specifically, this function (in order):

    #. Obtains this object's representation by calling ``repr(object)``.
    #. If this representation is *not* prefixed by a punctuation character
       (i.e., character in the standard :attr:`string.punctuation` set),
       double-quotes this representation for disambiguity with preceding
       characters -- notably, sequence indices. Since the string returned by
       this function commonly follows sequence indices in exception messages,
       failing to disambiguate the two produces non-human-readable output:

           >>> def wat(mate: typing.List[str]) -> int: return len(mate)
           >>> raise_pep_call_exception(
           ...     func=muh_func, pith_name='mate', pith_value=[7,])
           beartype.roar.BeartypeCallHintPepParamException: @beartyped wat()
           parameter mate=[7] violates PEP type hint typing.List[str], as list
           item 0 value 7 not a str.

       Note the substring "item 0 value 7", which misreads like a blatant bug.

    Caveats
    ----------
    **This function is unavoidably slow and should thus not be called from
    optimized performance-critical code.** This function internally performs
    mildly expensive operations, including regular expression-based matching
    and substitution. Ideally, this function should *only* be called to create
    user-oriented exception messages where performance is a negligible concern.

    Parameters
    ----------
    obj : object
        Object to be represented.
    max_len: Optional[int]
        Maximum length of the string to be returned. Defaults to the customary
        line length of 80 characters minus default output indentation of four
        characters.

    Returns
    ----------
    str
        Pretty-printed quasi-human-readable variant of this object's
        non-pretty-printed machine-readable representation.
    """
    assert isinstance(max_len, int), f'"{max_len}" not an integer.'

    # String describing the passed object. For debuggability, the verbose
    # (albeit less human-readable) output of repr() is preferred to the terse
    # (albeit more human-readable) output of str().
    #
    # Note that this representation is guaranteed to be non-empty, as *ALL*
    # objects (including outlier singletons like "None" and the empty string)
    # have non-empty representations. Ergo, testing both the first and last
    # characters of this representation is guaranteed to be safe.
    obj_repr = repr(obj)

    # If this representation is *NOT* prefixed by punctuation and thus *NOT*
    # demarcated from preceding characters in the exception message containing
    # the string returned by this function, double-quote this representation
    # for disambiguity with preceding characters -- notably, sequence indices.
    if obj_repr[0] not in punctuation:
        obj_repr = f'"{obj_repr}"'

    # If this representation either exceeds this maximum length *OR* contains a
    # newline...
    if len(obj_repr) > max_len or '\n' in obj_repr:
        # Uncompiled regular expression grouping zero or more non-newline
        # leading characters preceding this maximum length *AND* zero or more
        # trailing delimiters.
        #
        # Note that efficiency is *NOT* a consideration for this utility
        # function, which is only called in the edge-case event of a runtime
        # type exception.
        PRE_MAX_CHARS_LAST_DELIMITERS_REGEX = (
            r'^([^\n]{0,' + str(max_len) + r'}).*?([\])}>\'"]*)$')

        # Replace the substring of this representation from whichever of the
        # first character following this maximum length or the first newline
        # occurs first to the string end (excluding any optional trailing
        # delimiters) with a single ellipses.
        obj_repr = re.sub(
            PRE_MAX_CHARS_LAST_DELIMITERS_REGEX,
            r'\1...\2',
            obj_repr,
            flags=re.DOTALL
        )

    # Return this representation.
    return obj_repr
