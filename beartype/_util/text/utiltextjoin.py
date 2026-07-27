#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **string joining utilities** (i.e., callables joining passed
strings into new strings delimited by passed substring delimiters).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.typing.datatyping import (
    BoolTristate,
    IterableStrs,
    IterableTypes,
)
from collections.abc import (
    Iterable as IterableABC,
    Sequence as SequenceABC,
)

# ....................{ JOINERS ~ bulleted                 }....................
# ....................{ JOINERS ~ commaed : and            }....................
#FIXME: Unit test us up, please.
def join_strings_commaed_and(strings: IterableStrs, **kwargs) -> str:
    '''
    Concatenate the passed iterable of zero or more strings delimited by commas
    and/or the conjunction "and" (conditionally depending on both the length of
    this iterable and index of each string in this iterable), yielding a
    human-readable string listing arbitrarily many substrings conjunctively.

    Specifically, this function returns either:

    * If this iterable contains no strings, the empty string.
    * If this iterable contains one string, this string as is is unmodified.
    * If this iterable contains two strings, these strings delimited by the
      conjunction "and".
    * If this iterable contains three or more strings, a string listing these
      contained strings such that:

      * All contained strings except the last two are suffixed by commas.
      * The last two contained strings are delimited by the conjunction "and".

    Parameters
    ----------
    strings : Iterable[str]
        Iterable of all strings to be concatenated conjunctively.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.join_delimeted` function underlying this higher-level function.

    Returns
    -------
    str
        Conjunctive concatenation of these strings.
    '''

    # One of us. We accept one-liner. One of us.
    return join_strings_delimited(
        strings=strings,
        delimiter_if_two=' and ',
        delimiter_if_three_or_more_nonlast=', ',
        delimiter_if_three_or_more_last=', and ',
        **kwargs
    )

# ....................{ JOINERS ~ commaed : or             }....................
def join_strings_commaed_or(strings: IterableStrs, **kwargs) -> str:
    '''
    Concatenate the passed iterable of zero or more strings delimited by commas
    and/or the disjunction "or" (conditionally depending on both the length of
    this iterable and index of each string in this iterable), yielding a
    human-readable string listing arbitrarily many substrings disjunctively.

    Specifically, this function returns either:

    * If this iterable contains no strings, the empty string.
    * If this iterable contains one string, this string as is is unmodified.
    * If this iterable contains two strings, these strings delimited by the
      disjunction "or".
    * If this iterable contains three or more strings, a string listing these
      contained strings such that:

      * All contained strings except the last two are suffixed by commas.
      * The last two contained strings are delimited by the disjunction "or".

    Parameters
    ----------
    strings : Iterable[str]
        Iterable of all strings to be concatenated disjunctively.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.join_delimeted` function underlying this higher-level function.

    Returns
    -------
    str
        Disjunctive concatenation of these strings.
    '''

    # He will join us... OR DIE! *cackling heard*
    return join_strings_delimited(
        strings=strings,
        delimiter_if_two=' or ',
        delimiter_if_three_or_more_nonlast=', ',
        delimiter_if_three_or_more_last=', or ',
        **kwargs
    )


def join_types_commaed_or(
    # Mandatory parameters.
    types: IterableTypes,

    # Optional parameters.
    is_color: BoolTristate = False,
) -> str:
    '''
    Concatenate the human-readable classname of each class in the passed
    iterable delimited by commas and/or the disjunction "or" (conditionally
    depending on both the length of this iterable and index of each string in
    this iterable), yielding a human-readable string listing arbitrarily many
    classnames disjunctively.

    Parameters
    ----------
    types : Iterable[type]
        Iterable of all classes whose human-readable classnames are to be
        concatenated disjunctively.
    is_color : BoolTristate, optional
        Tri-state colouring boolean governing ANSI usage. See the
        :attr:`beartype.BeartypeConf.is_color` attribute for further details.
        Defaults to :data:`False`.

    Returns
    -------
    str
        Disjunctive concatenation of these classnames.
    '''

    # Avoid circular import dependencies.
    from beartype._util.text.utiltextlabel import label_type

    # Make it so, ensign.
    return join_strings_commaed_or(
        label_type(cls=cls, is_color=is_color) for cls in types)

# ....................{ JOINERS ~ delimited                }....................
#FIXME: Unit test the "is_double_quoted" parameter, please.
def join_strings_delimited(
    # Mandatory parameters.
    strings: IterableStrs,

    # Mandatory keyword-only parameters.
    *,
    delimiter_if_two: str,
    delimiter_if_three_or_more_nonlast: str,
    delimiter_if_three_or_more_last: str,

    # Optional keyword-only parameters.
    is_double_quoted: bool = False,
) -> str:
    '''
    Concatenate the passed iterable of zero or more strings delimited by the
    passed delimiter (conditionally depending on both the length of this
    sequence and index of each string in this sequence), yielding a
    human-readable string listing arbitrarily many substrings.

    Specifically, this function returns either:

    * If this iterable contains no strings, the empty string.
    * If this iterable contains one string, this string as is is unmodified.
    * If this iterable contains two strings, these strings delimited by the
      passed ``delimiter_if_two`` delimiter.
    * If this iterable contains three or more strings, a string listing these
      contained strings such that:

      * All contained strings except the last two are suffixed by the passed
        ``delimiter_if_three_or_more_nonlast`` delimiter.
      * The last two contained strings are delimited by the passed
        ``delimiter_if_three_or_more_last`` separator.

    Parameters
    ----------
    strings : Iterable[str]
        Iterable of all strings to be joined.
    delimiter_if_two : str
        Substring separating each string contained in this iterable if this
        iterable contains exactly two strings.
    delimiter_if_three_or_more_nonlast : str
        Substring separating each string *except* the last two contained in
        this iterable if this iterable contains three or more strings.
    delimiter_if_three_or_more_last : str
        Substring separating each string the last two contained in this
        iterable if this iterable contains three or more strings.
    is_double_quoted : bool, optional
        :data:`True` only if **double-quoting** (i.e., both prefixing and
        suffixing by the ``"`` character) each item of this iterable. Defaults
        to :data:`False`.

    Returns
    -------
    str
        Concatenation of these strings.

    Examples
    --------
        >>> join_strings_delimited(
        ...     strings=('Fulgrim', 'Perturabo', 'Angron', 'Mortarion'),
        ...     delimiter_if_two=' and ',
        ...     delimiter_if_three_or_more_nonlast=', ',
        ...     delimiter_if_three_or_more_last=', and ',
        ... )
        'Fulgrim, Perturabo, Angron, and Mortarion'
    '''
    assert isinstance(strings, IterableABC) and not isinstance(strings, str), (
        f'{repr(strings)} not non-string iterable.')
    assert isinstance(delimiter_if_two, str), (
        f'{repr(delimiter_if_two)} not string.')
    assert isinstance(delimiter_if_three_or_more_nonlast, str), (
        f'{repr(delimiter_if_three_or_more_nonlast)} not string.')
    assert isinstance(delimiter_if_three_or_more_last, str), (
        f'{repr(delimiter_if_three_or_more_last)} not string.')

    # ....................{ PREAMBLE                        }....................
    # If this iterable is *NOT* a sequence, internally coerce this iterable
    # into a sequence for subsequent indexing purposes.
    if not isinstance(strings, SequenceABC):
        strings = tuple(strings)
    # Else, this iterable is already a sequence.
    #
    # In either case, this iterable is now a sequence.

    # If passed *NO* strings are passed, immediately reduce to a noop by
    # trivially returning the empty string.
    #
    # Note that the emptiness of this container is only safely testable *AFTER*
    # coercing this container into a sequence above.
    if not strings:
        return ''
    # Else, one or more strings are passed.
    #
    # If double-quoting these strings, do so.
    elif is_double_quoted:
        strings = tuple(f'"{string}"' for string in strings)
    # Else, preserve these strings as is.

    # ....................{ STRINGS <= 2                    }....................
    # Number of strings in this non-empty sequence.
    strings_len = len(strings)

    # If passed exactly one string, return this string as is.
    if strings_len == 1:
        # This is clearly a string, yet mypy thinks it's Any. *WHATEVAHS*.
        return strings[0]  # type: ignore[no-any-return]
    # If passed exactly two strings, return these strings delimited as requested
    # by the caller.
    elif strings_len == 2:
        return f'{strings[0]}{delimiter_if_two}{strings[1]}'
    # Else, three or more strings are passed.

    # ....................{ STRINGS >= 3                    }....................
    # All such strings except the last two, delimited appropriately.
    strings_before_last_two = delimiter_if_three_or_more_nonlast.join(
        strings[0:-2])

    # The last two such strings, delimited appropriately.
    strings_last_two = (
        f'{strings[-2]}{delimiter_if_three_or_more_last}{strings[-1]}')

    # Return these two substrings, delimited appropriately.
    return (
        f'{strings_before_last_two}'
        f'{delimiter_if_three_or_more_nonlast}'
        f'{strings_last_two}'
    )
