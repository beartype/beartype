#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hints** (i.e., hints annotating callables
declared throughout this codebase, either for compliance with :pep:`561` or
:mod:`mypy` *or* for documentation purposes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.typing import (
    Any,
    Callable,
    Iterable,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from types import (
    CodeType,
    FrameType,
    GeneratorType,
)

# ....................{ HINTS ~ callable ~ early          }....................
# Callable-specific type hints required by subsequent type hints below.

CallableAny = Callable[..., Any]
'''
PEP-compliant type hint matching any callable in a manner explicitly matching
all possible callable signatures.
'''

# ....................{ HINTS ~ typevar                   }....................
# Type variables required by subsequent type hints below.

BeartypeableT = TypeVar('BeartypeableT', bound=Union[type, CallableAny])
'''
:pep:`484`-compliant **generic beartypeable type variable** (i.e., type hint
matching any arbitrary callable or class).

This type variable notifies static analysis performed by both static type
checkers (e.g., :mod:`mypy`) and type-aware IDEs (e.g., VSCode) that the
:mod:`beartype` decorator preserves:

* Callable signatures by creating and returning callables with the same
  signatures as passed callables.
* Class hierarchies by preserving passed classes with respect to inheritance,
  including metaclasses and method-resolution orders (MRO) of those classes.
'''

# ....................{ HINTS ~ callable ~ late           }....................
# Callable-specific type hints *NOT* required by subsequent type hints below.

BeartypeConfedDecorator = Callable[[BeartypeableT], BeartypeableT]
'''
PEP-compliant type hint matching a **configured beartype decorator** (i.e.,
closure created and returned from the :func:`beartype.beartype` decorator when
passed a beartype configuration via the optional ``conf`` parameter rather than
an arbitrary object to be decorated via the optional ``obj`` parameter).
'''


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
