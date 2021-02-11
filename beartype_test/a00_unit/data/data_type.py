#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2021 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype generic types data submodule.**

This submodule predefines low-level class constants exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                           }....................

# ....................{ CLASSES                           }....................
class Class:
    '''
    Arbitrary pure-Python class defining an arbitrary method.
    '''

    def instance_method(self):
        '''Arbitrary pure-Python instance method.'''

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


def generator_factory():
    '''
    Arbitrary pure-Python generator factory function.
    '''

    yield 1


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

# ....................{ CONSTANTS ~ filenames             }....................
MODULE_FILENAME = __file__
'''
Absolute filename of the current submodule, declared purely for convenience.
'''

# ....................{ CONSTANTS ~ types                 }....................
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
