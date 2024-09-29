#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`contextlib` utilities (i.e., low-level callables handling the
standard :mod:`contextlib` module).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from collections.abc import (
    Callable,
    # Generator,
)

from beartype._data.hint.datahintfactory import TypeGuard
from beartype._util.func.utilfunccodeobj import (
    get_func_codeobj_basename,
    get_func_codeobj_or_none,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_MOST_3_10
from beartype.typing import (
    Any,
)

# ....................{ TESTERS                            }....................
def is_func_contextlib_contextmanager(func: Any) -> TypeGuard[Callable]:
    '''
    :data:`True` only if the passed object is a
    :func:`contextlib.contextmanager`-based **isomorphic decorator closure**
    (i.e., closure both defined and returned by the standard
    :func:`contextlib.contextmanager` decorator where that closure
    isomorphically preserves both the number and types of all passed parameters
    and returns by accepting only a variadic positional argument and variadic
    keyword argument).

    This tester enables callers to detect when a user-defined callable has been
    decorated by :func:`contextlib.contextmanager` and thus has a mismatch
    between the type hints annotating that decorated callable and the type of
    the object created and returned by that decorated callable.

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a
        :func:`contextlib.contextmanager`-based isomorphic decorator closure.

    See Also
    --------
    beartype._data.func.datafunc.CONTEXTLIB_CONTEXTMANAGER_CO_NAME_QUALNAME
        Further discussion.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import is_func_closure

    # If either...
    if (
        # The active Python interpreter targets Python < 3.10 and thus fails to
        # define the "co_qualname" attribute on code objects required to
        # robustly implement this test *OR*...
        IS_PYTHON_AT_MOST_3_10 or
        # The passed callable is *NOT* a closure...
        not is_func_closure(func)
    ):
        # Then immediately return false.
        return False
    # Else, that callable is a closure.

    # Code object underlying that callable as is (rather than possibly unwrapped
    # to another code object entirely) if that callable is pure-Python *OR*
    # "None" otherwise (i.e., if that callable is C-based).
    func_codeobj = get_func_codeobj_or_none(func)

    # If that callable is C-based, immediately return false.
    if func_codeobj is None:
        return False
    # Else, that callable is pure-Python.

    # Defer heavyweight tester-specific imports with potential side effects --
    # notably, increased costs to space and time complexity.
    from beartype._data.module.datamodcontextlib import (
        CONTEXTLIB_CONTEXTMANAGER_CODEOBJ_NAME,
    )

    # Fully-qualified name of that code object.
    func_codeobj_name = get_func_codeobj_basename(func_codeobj)

    # Return true only if the fully-qualified name of that code object is that
    # of the isomorphic decorator closure created and returned by the standard
    # @contextlib.contextmanager decorator.
    #
    # Note that we *COULD* technically also explicitly test whether that
    # callable satisfies the is_func_wrapper_isomorphic() tester, but that
    # there's no benefit and a minor efficiency cost  to doing so.
    return func_codeobj_name == CONTEXTLIB_CONTEXTMANAGER_CODEOBJ_NAME
