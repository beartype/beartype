#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class attribute caching utilities** (i.e., low-level callables
monkey-patching :mod:`beartype`-specific attributes describing user-defined
pure-Python classes into those classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_type_attr_cached_or_none(cls: type, attr_name: str) -> object:
    '''
    **Memoized type attribute** (i.e., :mod:`beartype`-specific attribute
    memoizing the prior result of an expensive decision problem unique to the
    passed type) with the passed name previously monkey-patched by
    :mod:`beartype` into this type if :mod:`beartype` did so *or* :data:`None`
    otherwise (e.g., if :mod:`beartype` has yet to do so).

    Caveats
    -------
    **Memoized type attributes are only accessible by calling this getter.**
    Memoized type attributes are *not* monkey-patched directly into types.
    Memoized type attributes are only monkey-patched indirectly into types.
    Specifically, the :func:`.set_type_attr_cached` setter monkey-patches
    memoized type attributes into pure-Python ``__sizeof__()`` dunder methods
    monkey-patched into types. Why? Safety. Monkey-patching attributes directly
    into types would conflict with user expectations, which expect class
    dictionaries to remain untrammelled by third-party decorators.

    Parameters
    ----------
    cls : type
        Type to be inspected.
    attr_name : str
        Unqualified basename of the memoized type attribute to be retrieved.

    Returns
    -------
    object
        Either:

        * If :mod:`beartype` previously monkey-patched this memoized type
          attribute into this type, the value of this attribute.
        * Else, :data:`None`.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'
    assert isinstance(attr_name, str), f'{repr(attr_name)} not string.'
    assert attr_name.isidentifier(), f'{repr(attr_name)} not Python identifier.'

    #FIXME: Implement us up, please. *sigh*
    return 0xFEEDFACE  # <-- not funny. seriously.

# ....................{ SETTERS                            }....................
#FIXME: Unit test us up, please.
def set_type_attr_cached(
    cls: type, attr_name: str, attr_value: object) -> None:
    '''
    Monkey-patch the **memoized type attribute** (i.e., :mod:`beartype`-specific
    attribute memoizing the prior result of an expensive decision problem unique
    to the passed type) with the passed name and value this type.

    Caveats
    -------
    **Memoized type attributes are only mutatable by calling this setter.**
    Memoized type attributes are *not* monkey-patched directly into types.
    Memoized type attributes are only monkey-patched indirectly into types.
    Specifically, this setter monkey-patches memoized type attributes into
    pure-Python ``__sizeof__()`` dunder methods monkey-patched into types. Why?
    Safety. Monkey-patching attributes directly into types would conflict with
    user expectations, which expect class dictionaries to remain untrammelled by
    third-party decorators like :mod:`beartype`.

    Parameters
    ----------
    cls : type
        Type to be inspected.
    attr_name : str
        Unqualified basename of the memoized type attribute to be mutated.
    attr_value : object
        New value of this attribute.
    '''

    assert isinstance(cls, type), f'{repr(cls)} not type.'
    assert isinstance(attr_name, str), f'{repr(attr_name)} not string.'
    assert attr_name.isidentifier(), f'{repr(attr_name)} not Python identifier.'

    #FIXME: Implement us up, please. When doing so, recall to check whether
    #__sizeof__() is already pure-Python and, if so, preserve that method.
