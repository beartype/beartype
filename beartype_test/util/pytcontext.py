#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
:mod:`pytest` **context manager utilities.**
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from contextlib import (
    AbstractContextManager,
    contextmanager,
)

# ....................{ CONTEXTS                          }....................
#FIXME: Once we drop Python 3.6 support, reduce this to:
#    from contextlib import nullcontext
#    noop_context_manager = nullcontext
@contextmanager
def noop_context_manager(yield_value: object = None) -> AbstractContextManager:
    '''
    **Noop context manager** (i.e., context manager trivially yielding the
    passed parameter if any *or* ``None`` otherwise).

    Parameters
    ----------
    yield_value : object, optional
        Value to be yielded from this context manager. Defaults to ``None``.

    Returns
    ----------
    AbstractContextManager
        Noop context manager.
    '''

    yield yield_value
