#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype `PEP 544`_**-compliant type hint data.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 544:
    https://www.python.org/dev/peps/pep-0544
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 544`_**-compliant type hint data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 544:
        https://www.python.org/dev/peps/pep-0544
    '''

    # If the active Python interpreter does *NOT* target at least Python >= 3.8
    # and thus fails to support PEP 544, silently reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_8:
        return
    # Else, the active Python interpreter targets at least Python >= 3.9 and
    # thus supports PEP 593.

    # Defer Python version-specific imports.
    from typing import Protocol

    # Register the version-specific signs introduced in this version.
    #
    # Note that ignoring the "typing.Protocol" superclass is vital here. For
    # unknown and presumably uninteresting reasons, *ALL* possible objects
    # satisfy this superclass. Ergo, this superclass is synonymous with the
    # "object" root superclass: e.g.,
    #     >>> import typing as t
    #     >>> isinstance(object(), t.Protocol)
    #     True
    #     >>> isinstance('ok', t.Protocol)
    #     True
    #     >>> isinstance(3333, t.Protocol)
    #     True
    data_module.HINT_PEP_SIGNS_DEEP_SUPPORTED.add(Protocol)
    data_module.HINT_PEP_SIGNS_IGNORABLE.add(Protocol)
