#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **container singletons** (i.e., instances of data structures
commonly required throughout this codebase, reducing space and time consumption
by preallocating widely used data structures).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    Dict,
)

# ....................{ STRINGS ~ return                   }....................
ARG_NAME_RETURN = 'return'
'''
Unique name arbitrarily assigned by Python to the key of the ``__annotations__``
dunder attribute providing the type hint annotating the return of callables.

Note that Python itself prohibits callable parameters from being named
``"return"`` and thus guarantees this name to be safe and unambiguous.
'''


ARG_NAME_RETURN_REPR = repr(ARG_NAME_RETURN)
'''
Object representation of the magic string implying a return value in various
Python objects (e.g., the ``__annotations__`` dunder dictionary of annotated
callables).
'''

# ....................{ DICTS                              }....................
# Note that this exact type annotation is required to avoid mypy complaints. :O
DICT_EMPTY: Dict[Any, Any] = {}
'''
**Empty dictionary singleton.**

Whereas Python guarantees the **empty tuple** (i.e., ``()``) to be a singleton,
Python does *not* extend that guarantee to dictionaries. This empty dictionary
singleton amends that oversight, providing efficient reuse of empty
dictionaries: e.g.,

.. code-block::

   >>> () is ()
   True  # <-- good. this is good.
   >>> {} is {}
   False  # <-- bad. this is bad.
   >>> from beartype._data.datakind import DICT_EMPTY
   >>> DICT_EMPTY is DICT_EMPTY
   True  # <-- good. this is good, because we made it so.
'''
