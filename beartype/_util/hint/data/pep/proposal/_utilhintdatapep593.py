#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype `PEP 593`_**-compliant type hint data.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 593:
    https://www.python.org/dev/peps/pep-0593
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 593`_**-compliant type hint data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 593:
        https://www.python.org/dev/peps/pep-0593
    '''

    # ..................{ SETS ~ supported                  }..................
    # If the active Python interpreter targets at least Python >= 3.9 and thus
    # supports PEP 593, add the PEP 593-specific signs introduced in this
    # version.
    if IS_PYTHON_AT_LEAST_3_9:
        data_module.HINT_PEP_SIGNS_DEEP_SUPPORTED.update({typing.Annotated,})
