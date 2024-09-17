#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`646`-compliant :obj:`typing.Self` **unit tests**.

This submodule unit tests :pep:`646` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
#FIXME: *YIKES!* Support Python 3.11 please. Sadly, the Python 3.11-specific
#implementation of type variable tuple unpacking (e.g., "*Ts") appears to be
#totally different under Python 3.11. Well, isn't this madness. *sigh*
@skip_if_python_version_less_than('3.12.0')
# @skip_if_python_version_less_than('3.11.0')
def test_decor_pep646() -> None:
    '''
    Test :pep:`646` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.11 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        unit_test_decor_pep646)

    # ....................{ ASSERTS                        }....................
    # Defer to this external function, externalized to avoid "SyntaxError"
    # exceptions under older Python versions importing this test submodule.
    unit_test_decor_pep646()
