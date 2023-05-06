#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype generic callable code data submodule.**

This submodule predefines low-level class constants exercising known edge cases
on behalf of the higher-level
:mod:`beartype_test.a00_unit.a20_util.func.test_utilfunccode` submodule. Unit
tests defined in that submodule are sufficiently fragile that *no* other
submodule should import from this submodule.
'''

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: For completeness, unit tests test the *EXACT* contents of this file.
# Changes to this file must thus be synchronized with those tests.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ IMPORTS                            }....................
from beartype._util.func.utilfuncmake import make_func

# ....................{ CALLABLES ~ dynamic                }....................
of_vapours = make_func(
    func_name='vaulted_with_all_thy_congregated_might',
    func_code='''
def vaulted_with_all_thy_congregated_might():
    return 'Of vapours, from whose solid atmosphere'
''',
    func_doc='''
Arbitrary callable dynamically declared in-memory.
''')

# ....................{ CALLABLES ~ physical               }....................
def will_be_the_dome():
    '''
    Arbitrary non-lambda function physically declared by this submodule.
    '''

    return 'of a vast sepulchre'

# ....................{ CALLABLES ~ physical : lambda      }....................
thou_dirge = lambda: 'Of the dying year, to which this closing night'
'''
Arbitrary lambda function physically declared by this submodule.
'''


yellow = lambda: 'and black,', lambda: 'and pale,', lambda: 'and hectic red,'
'''
3-tuple of three arbitrary lambda functions physically declared by this
submodule, intentionally declared on the same line so as to induce edge cases
in lambda function detection code.
'''
