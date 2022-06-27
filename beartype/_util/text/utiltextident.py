#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python identifier** (i.e., attribute, callable, class, module,
or variable name) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ TESTERS                            }....................
def is_identifier(text: str) -> bool:
    '''
    ``True`` only if the passed string is the ``.``-delimited concatenation of
    one or more :pep:`3131`-compliant syntactically valid **Python
    identifiers** (i.e., attribute, callable, class, module, or variable name),
    suitable for testing whether this string is the fully-qualified name of an
    arbitrary Python object.

    Caveats
    ----------
    **This tester is mildly slow,** due to unavoidably splitting this string on
    ``.`` delimiters and iteratively passing each of the split substrings to
    the :meth:`str.isidentifier` builtin. Due to the following caveat, this
    inefficiency is unavoidable.

    **This tester is not optimizable with regular expressions** -- at least,
    not trivially. Technically, this tester *can* be optimized by leveraging
    the "General Category" of Unicode filters provided by the third-party
    :mod:`regex` package. Practically, doing so would require the third-party
    :mod:`regex` package and would still almost certainly fail in edge cases.
    Why? Because Python 3 permits Python identifiers to contain Unicode letters
    and digits in the "General Category" of Unicode code points, which is
    highly non-trivial to match with the standard :mod:`re` module.

    Parameters
    ----------
    text : string
        String to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this string is the ``.``-delimited concatenation of
        one or more syntactically valid Python identifiers.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Return either...
    return (
        # If this text contains *NO* "." delimiters and is thus expected to be
        # an unqualified Python identifier, true only if this is the case;
        text.isidentifier()
        if '.' not in text else
        # Else, this text contains one or more "." delimiters and is thus
        # expected to be a qualified Python identifier. In this case, true only
        # if *ALL* "."-delimited substrings split from this string are valid
        # unqualified Python identifiers.
        #
        # Note that:
        # * Regular expressions report false negatives. See the docstring.
        # * There exists an alternative and significantly more computationally
        #   expensive means of testing this condition, employed by the
        #   typing.ForwardRef.__init__() method to valid the validity of the
        #   passed relative classname:
        #       # Needless to say, we'll never be doing this.
        #       try:
        #           all(
        #               compile(identifier, '<string>', 'eval')
        #               for identifier in text.split('.')
        #           )
        #           return True
        #       except SyntaxError:
        #           return False
        all(identifier.isidentifier() for identifier in text.split('.'))
    )
