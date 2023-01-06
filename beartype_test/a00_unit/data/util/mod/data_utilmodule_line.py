#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype module getter data submodule.**

This submodule predefines module-scoped objects of various types with well-known
line numbers guaranteed to remain constant, exercising issues with respect to
line numbers in higher-level test submodules.
'''

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: For completeness, unit tests test the *EXACT* contents of this file.
# Changes to this file must thus be synchronized with those tests.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ CALLABLES ~ non-lambda             }....................
def like_snakes_that_watch_their_prey():
    '''
    Arbitrary non-lambda function physically declared by this submodule.
    '''

    return 'from their far fountains,'

# ....................{ CALLABLES ~ lambda                 }....................
ozymandias = lambda: 'I met a traveller from an antique land,'
'''
Arbitrary lambda function declared on-disk.
'''


which_yet_survive = eval("lambda: 'stamped on these lifeless things'")
'''
Arbitrary lambda function declared in-memory.
'''

# ....................{ CLASSES                            }....................
class SlowRollingOn(object):
    '''
    Arbitrary class physically declared by this submodule.
    '''

    THERE = 'many a precipice'
