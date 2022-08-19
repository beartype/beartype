#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) API.**

This subpackage provides an object-oriented type hint class hierarchy,
encapsulating the crude non-object-oriented type hint declarative API
standardized by the :mod:`typing` module.
'''

# ....................{ TODO                               }....................
#FIXME: Publicly document everything in "README.rst", please. *sigh*
#
#This is a great first start on a cheat sheet-style synopsis:
#
#    # This is DOOR. It's a Pythonic API providing an object-oriented interface
#    # to low-level type hints that basically have no interface whatsoever.
#    >>> from beartype.door import TypeHint
#    >>> usable_type_hint = TypeHint(int | str | None)
#    >>> print(usable_type_hint)
#    TypeHint(int | str | None)
#    
#    # DOOR hints can be iterated Pythonically.
#    >>> for child_hint in usable_type_hint: print(child_hint)
#    TypeHint(<class 'int'>)
#    TypeHint(<class 'str'>)
#    TypeHint(<class 'NoneType'>)
#    
#    # DOOR hints support equality Pythonically.
#    >>> from typing import Union
#    >>> usable_type_hint == TypeHint(Union[int, str, None])
#    True  # <-- this is madness.
#    
#    # DOOR hints support rich comparisons Pythonically.
#    >>> usable_type_hint <= TypeHint(int | str | bool | None)
#    True  # <-- madness continues.
#    
#    # DOOR hints are self-caching.
#    >>> TypeHint(int | str | bool | None) is TypeHint(int | str | bool | None)
#    True  # <-- blowing minds over here.

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.door._doorcls import (
    TypeHint as TypeHint,
)
from beartype.door._doortest import (
    is_subhint as is_subhint,
)
