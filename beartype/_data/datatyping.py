#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hints** (i.e., hints annotating callables
declared throughout this codebase, either for compliance with :pep:`561` or
simply for documentation purposes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from beartype._cave._cavefast import (
    MethodDecoratorClassType,
    MethodDecoratorPropertyType,
    MethodDecoratorStaticType,
)
from types import (
    CodeType,
    FrameType,
    GeneratorType,
)

# ....................{ HINTS ~ callable ~ early           }....................
# Callable-specific type hints required by subsequent type hints below.

CallableAny = Callable[..., Any]
'''
PEP-compliant type hint matching any callable in a manner explicitly matching
all possible callable signatures.
'''

# ....................{ HINTS ~ typevar                    }....................
# Type variables required by subsequent type hints below.

BeartypeableT = TypeVar(
    'BeartypeableT',
    # The @beartype decorator decorates objects that are either...
    bound=Union[
        # An arbitrary class *OR*...
        type,

        # An arbitrary callable *OR*...
        CallableAny,

        # A C-based unbound class method descriptor (i.e., a pure-Python unbound
        # function decorated by the builtin @classmethod decorator) *OR*...
        MethodDecoratorClassType,

        # A C-based unbound property method descriptor (i.e., a pure-Python
        # unbound function decorated by the builtin @property decorator) *OR*...
        MethodDecoratorPropertyType,

        # A C-based unbound static method descriptor (i.e., a pure-Python
        # unbound function decorated by the builtin @staticmethod decorator).
        MethodDecoratorStaticType,
    ],
)
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

# ....................{ HINTS ~ callable ~ args            }....................
CallableMethodGetitemArg = Union[int, slice]
'''
PEP-compliant type hint matching the standard type of the single positional
argument accepted by the ``__getitem__` dunder method.
'''

# ....................{ HINTS ~ callable ~ late            }....................
# Callable-specific type hints *NOT* required by subsequent type hints below.

CallableTester = Callable[[object], bool]
'''
PEP-compliant type hint matching a **tester callable** (i.e., arbitrary callable
accepting a single arbitrary object and returning either ``True`` if that object
satisfies an arbitrary constraint *or* ``False`` otherwise).
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

# ....................{ HINTS ~ callable ~ late : decor    }....................
BeartypeConfedDecorator = Callable[[BeartypeableT], BeartypeableT]
'''
PEP-compliant type hint matching a **configured beartype decorator** (i.e.,
closure created and returned from the :func:`beartype.beartype` decorator when
passed a beartype configuration via the optional ``conf`` parameter rather than
an arbitrary object to be decorated via the optional ``obj`` parameter).
'''


BeartypeReturn = Union[BeartypeableT, BeartypeConfedDecorator]
'''
PEP-compliant type hint matching any possible value returned by any invocation
of the :func:`beartype.beartype` decorator, including calls to that decorator
in both configuration and decoration modes.
'''

# ....................{ HINTS ~ code                       }....................
LexicalScope = Dict[str, Any]
'''
PEP-compliant type hint matching a **lexical scope** (i.e., dictionary mapping
from the name to value of each locally or globally scoped variable accessible
to a callable or class).
'''


CodeGenerated = Tuple[str, LexicalScope, Tuple[str, ...]]
'''
PEP-compliant type hint matching **generated code** (i.e., a tuple containing
a Python code snippet dynamically generated on-the-fly by a
:mod:`beartype`-specific code generator and metadata describing that code).

Specifically, this hint matches a 3-tuple ``(func_wrapper_code,
func_wrapper_scope, hint_forwardrefs_class_basename)``, where:

* ``func_wrapper_code`` is a Python code snippet type-checking an arbitrary
  object against this hint. For the common case of code generated for a
  :func:`beartype.beartype`-decorated callable, this snippet type-checks a
  previously localized parameter or return value against this hint.
* ``func_wrapper_scope`` is the **local scope** (i.e., dictionary mapping from
  the name to value of each attribute referenced one or more times in this code)
  of the body of the function embedding this code.
* ``hint_forwardrefs_class_basename`` is a tuple of the unqualified classnames
  of :pep:`484`-compliant relative forward references visitable from this hint
  (e.g., ``('MuhClass', 'YoClass')`` given the hint ``Union['MuhClass',
  List['YoClass']]``).
'''

# ....................{ HINTS ~ iterable                   }....................
IterableStrs = Iterable[str]
'''
PEP-compliant type hint matching *any* iterable of zero or more strings.
'''

# ....................{ HINTS ~ type                       }....................
TypeException = Type[Exception]
'''
PEP-compliant type hint matching *any* exception class.
'''


TypeWarning = Type[Warning]
'''
PEP-compliant type hint matching *any* warning category.
'''

# ....................{ HINTS ~ type : tuple               }....................
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

# ....................{ HINTS ~ type : tuple : stack       }....................
TypeStack = Optional[Tuple[type, ...]]
'''
PEP-compliant type hint matching a **type stack** (i.e., either tuple of zero or
more arbitrary types *or* ``None``).
'''
