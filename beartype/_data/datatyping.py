#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hints** (i.e., hints annotating callables
declared throughout this codebase, either for compliance with :pep:`561` or
:mod:`mypy` *or* for documentation purposes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from collections.abc import Callable
from types import CodeType, FrameType, GeneratorType
from typing import Iterable, Tuple, Type, Union

# ....................{ HINTS ~ callable                  }....................
Codeobjable = Union[Callable, CodeType, FrameType, GeneratorType]
'''
PEP-compliant type hint matching a **codeobjable** (i.e., pure-Python object
directly associated with a code object and thus safely passable as the first
parameter to the :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj`
getter retrieving the code object associated with this codeobjable).

Specifically, this hint matches:

* Code objects.
* Pure-Python callables, including generators (but *not* C-based callables,
  which lack code objects).
* Pure-Python callable stack frames.
'''

# ....................{ HINTS ~ iterable                  }....................
IterableStrs = Iterable[str]
'''
PEP-compliant type hint matching *any* iterable of zero or more strings.
'''

# ....................{ HINTS ~ type                      }....................
TypeException = Type[Exception]
'''
PEP-compliant type hint matching *any* exception class.
'''

# ....................{ HINTS ~ type : tuple              }....................
TupleTypes = Tuple[type, ...]
'''
PEP-compliant type hint matching a tuple of zero or more classes.

Equivalently, this hint matches all tuples passable as the second parameters to
the :func:`isinstance` and :func:`issubclass` builtins.
'''


TypeOrTupleTypes = Union[type, TupleTypes]
'''
PEP-compliant type hint matching either a single class *or* a tuple of zero or
more classes.

Equivalently, this hint matches all objects passable as the second parameters
to the :func:`isinstance` and :func:`issubclass` builtins.
'''
