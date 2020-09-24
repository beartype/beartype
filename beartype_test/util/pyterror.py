#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**:mod:`pytest` exception-handling utilities.**

This submodule provides functions validating caller-defined exceptions raised
during testing.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from contextlib import contextmanager
from pytest import raises

# ....................{ CONTEXTS                          }....................
@contextmanager
def raises_uncached(exception_cls: type) -> 'ExceptionInfo':
    '''
    Context manager validating that the block exercised by this manager raises
    a **cached exception** (i.e., whose message previously containing one or
    more instances of the magic
    :data:`beartype._util.cache.utilcacheerror.EXCEPTION_CACHED_PLACEHOLDER`
    substring since replaced by the
    :func:`beartype._util.cache.utilcacheerror.reraise_exception_cached`
    function) of the passed type.

    Parameters
    ----------
    exception_cls : str
        Type of cached exception expected to be raised by this block.

    Returns
    ----------
    :class:`pytest.nodes.ExceptionInfo`
        :mod:`pytest`-specific object collecting metadata on the cached
        exception of this type raised by this block.

    See Also:
    ----------
    https://docs.pytest.org/en/stable/reference.html#pytest._code.ExceptionInfo
        Official :class:`pytest.nodes.ExceptionInfo` documentation.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcacheerror import (
        EXCEPTION_CACHED_PLACEHOLDER)

    # With a "pytest"-specific context manager validating this contextual block
    # to raise an exception of this type...
    with raises(exception_cls) as exception_info:
        yield exception_info

    # Assert this exception message does *NOT* contain this magic substring.
    assert EXCEPTION_CACHED_PLACEHOLDER not in str(exception_info.value)
