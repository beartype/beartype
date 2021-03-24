#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 563`_**-compliant type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 563:
    https://www.python.org/dev/peps/pep-0563
'''

# ....................{ IMPORTS                           }....................
import __future__
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_10,
    IS_PYTHON_AT_LEAST_3_7,
)
from collections.abc import Callable
from sys import modules as sys_modules

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
def is_func_hints_pep563(func: Callable) -> bool:
    '''
    ``True`` only if `PEP 563`_ is active for the currently decorated callable.

    Parameters
    ----------
    func : Callable
        Decorated callable to be inspected.

    Returns
    ----------
    bool
        ``True`` only if `PEP 563`_ is active for this callable.

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # True only if PEP 563 is active for this callable.
    #
    # If the active Python interpreter targets Python >= 3.10, PEP 563 is
    # unconditionally active. Ergo, *ALL* annotations including this callable's
    # annotations are necessarily postponed.
    is_postponed = IS_PYTHON_AT_LEAST_3_10

    # If the active Python interpreter targets Python >= 3.7, PEP 563 is
    # conditionally active only if...
    if not is_postponed and IS_PYTHON_AT_LEAST_3_7:
        # Module declaring this callable.
        func_module = sys_modules[func.__module__]

        # "annotations" attribute declared by this module if any *OR* None.
        func_module_annotations_attr = getattr(
            func_module, 'annotations', None)

        # If this attribute is the "__future__.annotations" object, then the
        # module declaring this callable *MUST* necessarily have enabled PEP
        # 563 support with a leading statement resembling:
        #     from __future__ import annotations
        is_postponed = func_module_annotations_attr is __future__.annotations

    # Return true only if PEP 563 is active for this callable.
    return is_postponed
