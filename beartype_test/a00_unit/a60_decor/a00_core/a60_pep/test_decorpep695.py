#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`695`-compliant **type alias** unit tests.

This submodule unit tests :pep:`695` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.12.0')
def test_decor_pep695_type_recursive_indirect() -> None:
    '''
    Test :pep:`695` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.12 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype_test.a00_unit.data.pep.pep695.data_pep695util import (
        unit_test_decor_hint_pep695_type_recursive_indirect)

    # Perform this test.
    unit_test_decor_hint_pep695_type_recursive_indirect()
