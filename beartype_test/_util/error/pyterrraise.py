#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **exception handlers** (i.e., low-level callables manipulating fatal
exceptions in a human-readable, general-purpose manner).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from contextlib import contextmanager

# ....................{ CONTEXTS                           }....................
@contextmanager
def raises_uncached(exception_cls: 'type[Exception]') -> (
    'pytest.nodes.ExceptionInfo'):
    '''
    Context manager validating that the caller-defined body run by this manager
    raises an **unmemoized exception** (i.e., whose message previously
    containing one or more instances of the magic
    :data:`beartype._data.error.dataerrmagic.EXCEPTION_PLACEHOLDER` substring
    since replaced by the
    :func:`beartype._util.error.utilerrraise.reraise_exception_placeholder`
    function) of the passed type.

    Parameters
    ----------
    exception_cls : str
        Type of cached exception expected to be raised by that body.

    Returns
    -------
    :class:`pytest.nodes.ExceptionInfo`
        :mod:`pytest`-specific object collecting metadata on the cached
        exception of this type raised by that body.

    See Also
    --------
    https://docs.pytest.org/en/stable/reference.html#pytest._code.ExceptionInfo
        Official :class:`pytest.nodes.ExceptionInfo` documentation.
    '''

    # Defer test-specific imports.
    from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
    from pytest import raises

    # Within a "pytest"-specific context manager validating this contextual
    # block to raise an exception of this type, perform the body of that block.
    with raises(exception_cls) as exception_info:
        yield exception_info

    # Exception message raised by the body of that block.
    exception_message = str(exception_info.value)

    # Assert this exception message does *NOT* contain this magic substring.
    assert EXCEPTION_PLACEHOLDER not in exception_message

    #FIXME: Inadvisable in the general case, but preserved for posterity.
    # Assert this exception message does *NOT* contain two concurrent spaces,
    # implying an upstream failure in substring concatenation.
    # assert '  ' not in exception_message
