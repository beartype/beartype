#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **code object globals** (i.e., global constants describing code
objects of callables, classes, and modules).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from inspect import (
    CO_ASYNC_GENERATOR,
    CO_COROUTINE,
    CO_GENERATOR,
)

# ....................{ INTEGERS                           }....................
CODEOBJECT_FLAGS_ASYNC = CO_ASYNC_GENERATOR | CO_COROUTINE
'''
**Asynchronous callable factory binary flags** (i.e., bit field which when
AND-ed against the ``co_flags`` instance variable of any code object underlying
an asynchronous callable factory produces a non-zero integer).

This bit field enables efficient detection of both:

* **Coroutine factories** (i.e., callables declared via the ``async def``
  keywords whose bodies contain *no* ``yield`` expressions).
* **Asynchronous generator factories** (i.e., callables declared via the ``async
  def`` keywords whose bodies contain one or more ``yield`` expressions).
'''


CODEOBJECT_FLAGS_GENERATOR = CO_ASYNC_GENERATOR | CO_GENERATOR
'''
**Generator callable factory binary flags** (i.e., bit field which when AND-ed
against the ``co_flags`` instance variable of any code object underlying a
generator callable factory produces a non-zero integer).

This bit field enables efficient detection of both:

* **Asynchronous generator factories** (i.e., callables declared via the ``async
  def`` keywords whose bodies contain one or more ``yield`` expressions).
* **Synchronous generator factories** (i.e., callables *not* declared via the
  ``async def`` keywords whose bodies contain one or more ``yield``
  expressions).
'''

# ....................{ STRINGS                            }....................
CODEOBJECT_BASENAME_MODULE_OR_EVAL = '<module>'
'''
Arbitrary string constant unconditionally assigned to both the ``co_name`` *and*
``co_qualname`` attributes of the code objects of all pure-Python modules (i.e.,
the top-most lexical scope of each module in the current call stack) *and*
pure-Python code snippets dynamically executed by the :func:`exec` and
:func:`eval` builtins.

This constant enables callers to reliably differentiate between code objects
underlying:

* Module, :func:`exec`, and :func:`eval` scopes, whose ``co_name`` variable is
  this constant.
* Class and callable scopes, whose ``co_name`` variable is *not* this constant.
'''


CODEOBJECT_FILENAME_EVAL = '<string>'
'''
Arbitrary string constant unconditionally assigned to the ``co_filename``
attribute of the code objects of all pure-Python code snippets dynamically
executed by the :func:`exec` and :func:`eval` builtins.

This constant enables callers to reliably differentiate between code objects
underlying:

* :func:`exec` and :func:`eval` scopes, whose ``co_filename`` variable is this
  constant.
* Module, class, and callable scopes, whose ``co_filename`` variable is *not*
  this constant.
'''
