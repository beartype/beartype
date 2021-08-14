#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **generic types data** submodule.

This submodule predefines low-level class constants exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                           }....................
import builtins
from beartype._data.mod.datamod import BUILTINS_MODULE_NAME
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

# ....................{ SETS ~ callable                   }....................
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

# ....................{ SETS ~ type : builtin             }....................
TYPES_BUILTIN = frozenset((
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

# ....................{ SETS ~ type : non-builtin         }....................
TYPES_BUILTIN_FAKE = frozenset((
    # Type of this builtin.
    builtin.__class__
    # For each builtin (i.e., globally accessible object implicitly imported by
    # the active Python interpreter into *EVERY* lexical context)...
    for builtin in builtins.__dict__.values()
    # If...
    if (
        # The type of this builtin also insists itself to be defined by the
        # "builtins" module and thus also be a builtin *AND*...
        builtin.__class__.__module__ == BUILTINS_MODULE_NAME and
        # The "builtins" module contains *NO* globally-scoped attribute whose
        # name is that of this type...
        builtin.__class__.__name__ not in builtins.__dict__
    # Then add this cheatin', lyin', no-good type to this set.
    )
))
'''
Frozen set of all **fake builtin types** (i.e., types that are *not* builtin
but which nonetheless erroneously masquerade as being builtin).

See Also
----------
:data:`beartype._data.cls.datacls.TYPES_BUILTIN_FAKE`
    Related runtime set. Whereas that runtime-specific set is efficiently
    defined explicitly by listing all non-builtin builtin mimic types, this
    test-specific set is inefficiently defined implicitly by introspecting the
    :mod:`builtins` module. While less efficient, this test-specific set serves
    as an essential sanity check on that runtime-specific set.
'''


TYPES_NONBUILTIN = frozenset((
    # Arbitrary non-builtin type.
    Class,
)) | TYPES_BUILTIN_FAKE
'''
Frozen set of arbitrary non-builtin types.
'''
