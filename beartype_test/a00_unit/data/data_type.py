#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype generic types data submodule.**

This submodule predefines low-level class constants exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                           }....................
from sys import exc_info, implementation
from typing import Callable

# ....................{ CLASSES                           }....................
class Class(object):
    '''
    Arbitrary pure-Python class defining an arbitrary method.
    '''

    def instance_method(self):
        '''Arbitrary pure-Python instance method.'''

        pass

# ....................{ CLASSES ~ isinstance              }....................
class NonIsinstanceableMetaclass(type):
    '''
    Metaclass overriding the ``__instancecheck__()`` dunder method to
    unconditionally raise an exception, preventing classes with this metaclass
    from being passed as the second parameter to the :func:`isinstance`
    builtin.
    '''

    def __instancecheck__(self, obj: object) -> bool:
        raise TypeError(
            f'{self} not passable as second parameter to isinstance().')


class NonIsinstanceableClass(object, metaclass=NonIsinstanceableMetaclass):
    '''
    Class whose metaclass overrides the ``__instancecheck__()`` dunder method
    to unconditionally raise an exception, preventing this class from being
    passed as the second parameter to the :func:`isinstance` builtin.
    '''

    pass

# ....................{ CALLABLES                         }....................
def function():
    '''
    Arbitrary pure-Python function.
    '''

    pass


def closure_cell_factory():
    '''
    Arbitrary pure-Python closure cell factory function.
    '''

    # Arbitrary non-local variable.
    outer_variable = 1

    def closure():
        '''
        Arbitrary pure-Python closure.
        '''

        nonlocal outer_variable

    # Return this closure's first and only cell variable.
    return closure.__closure__[0]


def decorator(func: Callable) -> Callable:
    '''
    **Identity decorator** (i.e., decorator returning the passed callable
    unmodified).

    This decorator enables logic elsewhere to exercise the
    :mod:`beartype.beartype` decorator with respect to nested callables
    decorated by both the :mod:`beartype.beartype` decorator and one or more
    decorators *not* the :mod:`beartype.beartype` decorator.
    '''

    return func


def generator_factory():
    '''
    Arbitrary pure-Python generator factory function.
    '''

    yield 1

# ....................{ CALLABLES ~ async                 }....................
async def async_generator_factory():
    '''
    Arbitrary pure-Python asynchronous generator factory function.
    '''

    yield


async def coroutine_factory():
    '''
    Arbitrary pure-Python coroutine factory function.
    '''

    pass


async_generator = async_generator_factory()
'''
Arbitrary pure-Python asynchronous generator.
'''


coroutine = coroutine_factory()
'''
Arbitrary pure-Python coroutine.
'''

# Prevent Python from emitting "ResourceWarning" warnings.
coroutine.close()

# ....................{ CONSTANTS                         }....................
CALLABLE_CODE_OBJECT = function.__code__
'''
Arbitrary callable code object.
'''


# Initialized below.
TRACEBACK = None
'''
Arbitrary traceback object.
'''

# Define the "TRACEBACK" constant via EAFP.
try:
    raise TypeError
except TypeError:
    TRACEBACK = exc_info()[2]

# ....................{ CONSTANTS ~ filenames             }....................
MODULE_FILENAME = __file__
'''
Absolute filename of the current submodule, declared purely for convenience.
'''

# ....................{ CONSTANTS ~ sets : callable       }....................
CALLABLES_PYTHON = frozenset((function, Class, Class.instance_method))
'''
Frozen set of pure-Python callables exercising edge cases.
'''


CALLABLES_C = frozenset((
    len,              # Built-in FunctionType
    ().count,         # Built-in Method Type
    object.__init__,  # Wrapper Descriptor Type
    object().__str__, # Method Wrapper Type
    str.join,         # Method Descriptor Type

    #FIXME: *UGH.* This probably should be callable under PyPy 3.6, but
    #it's not, which is why we've currently disabled this. That's clearly a
    #PyPy bug. Uncomment this *AFTER* we drop support for PyPy 3.6 (and any
    #newer PyPy versions also failing to implement this properly). We
    #should probably also consider filing an upstream issue with PyPy,
    #because this is non-ideal and non-orthogonal behaviour with CPython.
    #dict.__dict__['fromkeys'],
))
'''
Frozen set of C-based callables exercising edge cases.
'''


NON_CALLABLES = (
    CALLABLE_CODE_OBJECT,
    type.__dict__,      # Mapping Proxy Type
    implementation,     # Simple Namespace Type
    async_generator,
    closure_cell_factory(), # Cell type
    coroutine,
    generator_factory(),
    TRACEBACK,
    TRACEBACK.tb_frame,
)
'''
Tuple of callable-like non-callable objects exercising edge cases,
intentionally defined as a tuple rather than frozen set due to the
unhashability of one or more members (e.g., ``TRACEBACK``).
'''

# ....................{ CONSTANTS ~ sets : class          }....................
CLASSES_BUILTIN = frozenset((
    bool,
    complex,
    dict,
    float,
    frozenset,
    int,
    list,
    set,
    str,
    tuple,
))
'''
Frozen set of all **builtin types** i.e., globally accessible C-based type
requiring *no* explicit importation)(.
'''


CLASSES_NON_BUILTIN = frozenset((
    # Arbitrary non-builtin type.
    Class,

    # Type of the "None" singleton, which constitutes an edge case due to being
    # globally inaccessible and thus effectively *NOT* builtin despite being
    # declared by the "builtins" module.
    type(None),
))
'''
Frozen set of arbitrary non-builtin types.
'''
