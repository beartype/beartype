#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python interpreter version utilities**.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from sys import version_info

# ....................{ CONSTANTS ~ at least               }....................
IS_PYTHON_AT_LEAST_4_0 = version_info >= (4, 0)
'''
``True`` only if the active Python interpreter targets at least Python 4.0.0.
'''


#FIXME: After dropping Python 3.10 support:
#* Refactor all code conditionally testing this global to be unconditional.
#* Remove this global.
#* Remove all decorators resembling:
#  @skip_if_python_version_less_than('3.11.0')
IS_PYTHON_AT_LEAST_3_11 = IS_PYTHON_AT_LEAST_4_0 or version_info >= (3, 11)
'''
``True`` only if the active Python interpreter targets at least Python 3.11.0.
'''

#FIXME: After dropping Python 3.9 support:
#* Refactor all code conditionally testing this global to be unconditional.
#* Remove this global.
#* Remove all decorators resembling:
#  @skip_if_python_version_less_than('3.10.0')
IS_PYTHON_AT_LEAST_3_10 = IS_PYTHON_AT_LEAST_3_11 or version_info >= (3, 10)
'''
``True`` only if the active Python interpreter targets at least Python 3.10.0.
'''


#FIXME: After dropping Python 3.9 support:
#* Remove this global.
IS_PYTHON_AT_MOST_3_9 = not IS_PYTHON_AT_LEAST_3_10
'''
``True`` only if the active Python interpreter targets at most Python 3.9.x.
'''


#FIXME: After dropping Python 3.8 support:
#* Refactor all code conditionally testing this global to be unconditional.
#* Remove this global.
#* Remove all decorators resembling:
#  @skip_if_python_version_less_than('3.9.0')
IS_PYTHON_AT_LEAST_3_9 = IS_PYTHON_AT_LEAST_3_10 or version_info >= (3, 9)
'''
``True`` only if the active Python interpreter targets at least Python 3.9.0.
'''


#FIXME: After dropping Python 3.8 support:
#* Remove this global.
IS_PYTHON_AT_MOST_3_8 = not IS_PYTHON_AT_LEAST_3_9
'''
``True`` only if the active Python interpreter targets at most Python 3.8.x.
'''


#FIXME: After dropping Python 3.7 support:
#* Refactor all code conditionally testing this global to be unconditional.
#* Remove this global.
#* Remove all decorators resembling:
#  @skip_if_python_version_less_than('3.8.0')
IS_PYTHON_AT_LEAST_3_8 = IS_PYTHON_AT_LEAST_3_9 or version_info >= (3, 8)
'''
``True`` only if the active Python interpreter targets at least Python 3.8.0.
'''


#FIXME: After dropping Python 3.8 support, *REMOVE* all code conditionally
#testing this global.
IS_PYTHON_3_8 = version_info[:2] == (3, 8)
'''
``True`` only if the active Python interpreter targets exactly Python 3.8.
'''


#FIXME: After dropping Python 3.7 support:
#* Refactor all code conditionally testing this global to be unconditional.
#* Remove this global.
#* Remove all decorators resembling:
#  @skip_if_python_version_less_than('3.7.2')
IS_PYTHON_AT_LEAST_3_7_2 = IS_PYTHON_AT_LEAST_3_8 or version_info >= (3, 7, 2)
'''
``True`` only if the active Python interpreter targets at least Python 3.7.2,
which introduced several new public attributes to the :mod:`typing` module
(e.g., :attr:`typing.OrderedDict`).
'''


#FIXME: After dropping Python 3.7 support, *REMOVE* all code conditionally
#testing this global.
IS_PYTHON_3_7 = version_info[:2] == (3, 7)
'''
``True`` only if the active Python interpreter targets exactly Python 3.7.
'''

# ....................{ GETTERS                            }....................
def get_python_version_major_minor() -> str:
    '''
    ``"."``-delimited major and minor version of the active Python interpreter
    (e.g., ``3.11``, ``3.7``), excluding the patch version of this interpreter.
    '''

    # Heroic one-liners are an inspiration to us all.
    return f'{version_info[0]}.{version_info[1]}'
