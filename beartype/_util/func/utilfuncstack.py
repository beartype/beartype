#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **call stack frame** utilities.

This private submodule implements utility functions dynamically introspecting
the current **call stack** (i.e., stack of frame objects signifying the chain
of calls to all callables leading to the call to the current callable).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import sys
from collections.abc import Callable
from typing import Optional

# ....................{ TESTERS                           }....................
def get_func_stack_frame_getter_or_none() -> Optional[Callable]:
    '''
    Private low-level :func:`sys._getframes` getter if the active Python
    interpreter declares that getter *or* ``None`` otherwise (i.e., if this
    interpreter does *not* declare that getter).

    Since that getter exists in all standard Python interpreters (e.g.,
    CPython, PyPy) supported by this package, this getter should *always*
    return a valid callable rather than ``None``. If that callable exists, that
    callable has a docstring under CPython resembling:

    .. _code-block:: python

       _getframe([depth]) -> frameobject

       Return a frame object from the call stack.  If optional integer depth is
       given, return the frame object that many calls below the top of the
       stack. If that is deeper than the call stack, ValueError is raised. The
       default for depth is zero, returning the frame at the top of the call
       stack.

       Frame objects provide these attributes:
           f_back          next outer frame object (this frame's caller)
           f_builtins      built-in namespace seen by this frame
           f_code          code object being executed in this frame
           f_globals       global namespace seen by this frame
           f_lasti         index of last attempted instruction in bytecode
           f_lineno        current line number in Python source code
           f_locals        local namespace seen by this frame
           f_trace         tracing function for this frame, or None

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    ----------
    Optional[Callable]
        Either:

        * If the active Python interpreter declares the private low-level
          :func:`sys._getframes` getter, that getter.
        * Else, ``None``.
    '''

    # Ultimate One-liners defy the Ancient Enemy!
    return getattr(sys, '_getframes', None)
