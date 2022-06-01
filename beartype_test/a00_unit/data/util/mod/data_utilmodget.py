#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype module getter data submodule.**

This submodule predefines low-level class constants exercising known edge
cases on behalf of the higher-level
:mod:`beartype_test.a00_unit.a20_util.mod.test_utilmodget` submodule. Unit
tests defined in that submodule are sufficiently fragile that *no* other
submodule should import from this submodule.
'''

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: For completeness, unit tests test the *EXACT* contents of this file.
# Changes to this file must thus be synchronized with those tests.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ CALLABLES                          }....................
def like_snakes_that_watch_their_prey():
    '''
    Arbitrary non-lambda function physically declared by this submodule.
    '''

    return 'from their far fountains,'

# ....................{ CLASSES                            }....................
class SlowRollingOn(object):
    '''
    Arbitrary class physically declared by this submodule.
    '''

    THERE = 'many a precipice'
