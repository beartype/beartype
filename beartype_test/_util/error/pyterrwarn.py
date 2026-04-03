#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **warnings handlers** (i.e., low-level callables manipulating
non-fatal warnings in a human-readable, general-purpose manner).
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
def warns_uncached(warning_cls: 'type[Warning]') -> 'ExceptionInfo':
    '''
    Context manager validating that the caller-defined body run by this manager
    issues an **unmemoized warning** (i.e., whose message previously containing
    one or more instances of the magic
    :data:`beartype._data.error.dataerrmagic.EXCEPTION_PLACEHOLDER` substring
    since replaced by the
    :func:`beartype._util.error.utilerrwarn.rewarn_warning_placeholder`
    function) of the passed type.

    Parameters
    ----------
    warning_cls : str
        Type of cached warning expected to be issued by that body.

    Returns
    -------
    :class:`pytest.nodes.ExceptionInfo`
        :mod:`pytest`-specific object collecting metadata on the cached warning
        of this type issued by that body.

    See Also
    --------
    https://docs.pytest.org/en/stable/reference.html#pytest._code.ExceptionInfo
        Official :class:`pytest.nodes.ExceptionInfo` documentation.
    '''

    # Defer test-specific imports.
    from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
    from pytest import warns

    # Within a "pytest"-specific context manager validating this contextual
    # block to issue an warning of this type, perform the body of that block.
    with warns(warning_cls) as warning_info:
        yield warning_info

    # For each "warning.WarningMessage" object contained in this
    # "pytest"-specific "warning_info" list...
    for warning_message_obj in warning_info:
        # Message issued with this warning. We didn't make this API. *BARF*
        warning_message = str(warning_message_obj.message.args[0])

        # Assert this warning message does *NOT* contain this magic substring.
        assert EXCEPTION_PLACEHOLDER not in warning_message

        #FIXME: Inadvisable in the general case, but preserved for posterity.
        # Assert this warning message does *NOT* contain two concurrent spaces,
        # implying an upstream failure in substring concatenation.
        # assert '  ' not in warning_message
