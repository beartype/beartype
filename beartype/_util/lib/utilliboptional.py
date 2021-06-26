#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **optional runtime dependency** (i.e., third-party Python packages
optionally imported where importable by :mod:`beartype`) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.mod.utilmodule import is_module

# ....................{ CONSTANTS                         }....................
#FIXME: Excise us up. This should *NOT* actually be required anymore.
# IS_LIB_TYPING_EXTENSIONS = is_module('typing_extensions')
# '''
# ``True`` only if the third-party :mod:`typing_extensions` module is importable
# under the active Python interpreter.
#
# :mod:`typing_extensions` backports attributes of the :mod:`typing` module
# bundled with newer Python versions to older Python versions.
# '''
