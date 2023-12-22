#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`695`-compliant :obj:`typing.Self` **unit tests**.

This submodule unit tests :pep:`695` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import (
    skip, skip_if_python_version_less_than)

# ....................{ TESTS                              }....................
#FIXME: Repair and unskip, please. *sigh*
@skip('Currently broken, sadly.')
@skip_if_python_version_less_than('3.12.0')
def test_decor_pep695() -> None:
    '''
    Test :pep:`695` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.12 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype_test.a00_unit.data.pep.data_pep695 import (
        unit_test_decor_pep695)

    # Run this unit test in a safe manner isolated from the main test suite to
    # avoid raising spurious "SyntaxError" exceptions under older interpreters.
    unit_test_decor_pep695()
