#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype Python interpreter utilities.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import sys

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS ~ at least              }....................
IS_PYTHON_AT_LEAST_4_0 = sys.version_info >= (4, 0)
'''
``True`` only if the active Python interpreter targets at least Python 4.0.0.
'''


#FIXME: After dropping Python 3.8 support:
#* Refactor all code conditionally testing this global to be unconditional.
#* Remove this global.
IS_PYTHON_AT_LEAST_3_9 = IS_PYTHON_AT_LEAST_4_0 or sys.version_info >= (3, 9)
'''
``True`` only if the active Python interpreter targets at least Python 3.8.0.
'''


#FIXME: After dropping Python 3.7 support:
#* Refactor all code conditionally testing this global to be unconditional.
#* Remove this global.
IS_PYTHON_AT_LEAST_3_8 = IS_PYTHON_AT_LEAST_3_9 or sys.version_info >= (3, 8)
'''
``True`` only if the active Python interpreter targets at least Python 3.8.0.
'''


#FIXME: After dropping Python 3.6 support:
#* Refactor all code conditionally testing this global to be unconditional.
#* Remove this global.
IS_PYTHON_AT_LEAST_3_7 = IS_PYTHON_AT_LEAST_3_8 or sys.version_info >= (3, 7)
'''
``True`` only if the active Python interpreter targets at least Python 3.7.0.
'''


#FIXME: After dropping Python 3.6 support, *REMOVE* all code conditionally
#testing this global.
IS_PYTHON_3_6 = not IS_PYTHON_AT_LEAST_3_7
'''
``True`` only if the active Python interpreter targets exactly Python 3.6.
'''
