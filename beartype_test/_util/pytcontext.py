#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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
    nullcontext,
)

# ....................{ CONTEXTS                          }....................
noop_context_manager = nullcontext
'''
**Noop context manager** (i.e., context manager trivially yielding the passed
parameter if any *or* ``None`` otherwise).

Parameters
----------
enter_result : object, optional
    Value to be yielded from this context manager. Defaults to ``None``.

Returns
----------
AbstractContextManager
    Noop context manager.
'''
