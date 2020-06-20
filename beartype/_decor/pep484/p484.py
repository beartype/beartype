#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator** `PEP 484`_ **support.**

This private submodule implements `PEP 484`_ (i.e., Type Hints) support.
Specifically, this submodule transparently converts high-level special-purpose
abstract types and methods defined by the stdlib :mod:`typing` module into
low-level general-use concrete types and code snippets independent of that
module.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
# from beartype.cave import (ClassType,)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']
