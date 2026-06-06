#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`702`-compliant **callable utilities** (i.e., callables
specifically applicable to :pep:`702`-compliant decorators used to decorate
user-defined callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from collections.abc import Callable

# ....................{ TESTERS                            }....................
def is_func_pep702(func: Callable) -> bool:
    '''
    :data:`True` only if the passed callable was decorated by the
    :pep:`702`-compliant :func:`warnings.deprecated` decorator, issuing one
    non-fatal deprecation warning on each call of the decorated callable.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    -------
    bool
        :data:`True` only if that callable was decorated by the
        :pep:`702`-compliant :func:`warnings.deprecated` decorator.
    '''

    # Dunder attribute hopefully *ONLY* declared on by the @warnings.deprecated
    # decorator if the passed callable is an isomorphic wrapper closure created
    # and returned by that decorator *OR* "None" otherwise (i.e., if the passed
    # callable is *NOT* such a closure).
    func_deprecated = getattr(func, '__deprecated__', None)

    #FIXME: If even this test fails to suffice at some point, we could
    #disambiguate even further by additionally detecting that "func" also
    #defines the "__wrapped__" dunder attribute added by the @functools.wraps
    #decorator internally applied by @warnings.deprecated. *shrug*
    # Return true *ONLY* if the value of this attribute is a string, as mandated
    # by PEP 702.
    return isinstance(func_deprecated, str)
