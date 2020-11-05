#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
Beartype **Python identifier** (i.e., class, module, or attribute name)
utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
def is_identifiers_joined(text: str) -> bool:
    '''
    ``True`` only if the passed string is the ``.``-delimited concatenation of
    one or more `PEP 3131`_-compliant syntactically valid **Python
    identifiers** (i.e., class, module, or attribute name), suitable for
    testing whether this string is the fully-qualified name of an arbitrary
    Python object.

    Parameters
    ----------
    text : string
        String to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this string is the ``.``-delimited concatenation of
        one or more syntactically valid Python identifiers.

    .. _PEP 3131:
       https://www.python.org/dev/peps/pep-3131
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Return true only if *ALL*...
    #
    # Note that there exists an alternative and significantly more
    # computationally expensive means of testing this condition, employed by
    # the typing.ForwardRef.__init__() method to valid the validity of the
    # passed relative classname:
    #     try:
    #         all(
    #             compile(identifier, '<string>', 'eval')
    #             for identifier in text.split('.')
    #         )
    #         return True
    #     except SyntaxError:
    #         return False
    #
    # Needless to say, we'll never be doing that.
    return all(
        # "."-delimited substrings split from this string are syntactically
        # valid PEP 3131-compliant Python identifiers.
        identifier.isidentifier()
        for identifier in text.split('.')
    )
