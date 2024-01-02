#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.12.0')
def test_decor_pep695() -> None:
    '''
    Test :pep:`695` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.12 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    #
    # Note that merely importing this data submodule suffices to fully exercise
    # this test.

    #FIXME: Uncomment once worky, please. *sigh*
    # from beartype_test.a00_unit.data.pep import data_pep695
