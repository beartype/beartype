#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Coverage.py-specific main module trivially importing the main workhorse for this
test package.

Ideally, *this* main module would be that main workhorse. Sadly, the
"beartype.claw" import hooks registered by the "__init__" submodule for this
package fails to apply to this main module, presumably due to chicken-and-egg
importations performed by Coverage.py itself. We shrug disconsolately.
'''

# ....................{ IMPORTS                            }....................
# Import the main workhorse for this test package.
from line_numbers import haunt_us_till
