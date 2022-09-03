#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **generic types data** submodule.

This submodule predefines low-level class constants exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from contextlib import contextmanager
from sys import exc_info, implementation
from typing import (
    AsyncGenerator,
    Callable,
    ContextManager,
    Coroutine,
    Generator,
)

# ....................{ CLASSES                            }....................
class CallableClass(object):
    '''
    Arbitrary pure-Python **callable class** (i.e., class defining the
    :meth:`__call__` dunder method implicitly called by Python when instances
    of this class are called using the standard calling convention).
    '''

    def __call__(self, *args, **kwargs) -> int:
        '''
        Dunder method implicitly called when this object is called.
        '''

        return len(args) + len(kwargs)

# ....................{ CLASSES ~ hierarchy : 1            }....................
# Arbitrary class hierarchy.

class Class(object):
    '''
    Arbitrary pure-Python class defining arbitrary methods.
    '''

    def instance_method(self):
        '''
        Arbitrary pure-Python instance method.
        '''

        pass


    @property
    def instance_property(self):
        '''
        Arbitrary pure-Python instance property.
        '''

        pass


    @classmethod
    def class_method(cls):
        '''
        Arbitrary pure-Python class method.
        '''

        pass


    @staticmethod
    def static_method():
        '''
        Arbitrary pure-Python static method.
        '''

        pass


class Subclass(Class):
    '''
    Arbitrary pure-Python subclass of an arbitrary pure-Python superclass.
    '''

    pass


class SubclassSubclass(Subclass):
    '''
    Arbitrary pure-Python subclass of an arbitrary pure-Python subclass of an
    arbitrary pure-Python superclass.
    '''

    pass

# ....................{ CLASSES ~ hierarchy : 2            }....................
# Yet another arbitrary class hierarchy.

class OtherClass(object):
    '''
    Arbitrary pure-Python class defining an arbitrary method.
    '''

    def instance_method(self):
        '''
        Arbitrary pure-Python instance method.
        '''

        pass


class OtherSubclass(OtherClass):
    '''
    Arbitrary pure-Python subclass of an arbitrary pure-Python superclass.
    '''

    pass


class OtherSubclassSubclass(OtherSubclass):
    '''
    Arbitrary pure-Python subclass of an arbitrary pure-Python subclass of an
    arbitrary pure-Python superclass.
    '''

    pass

# ....................{ CLASSES ~ isinstance               }....................
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

# ....................{ CLASSES ~ issubclass               }....................
class NonIssubclassableMetaclass(type):
    '''
    Metaclass overriding the ``__subclasscheck__()`` dunder method to
    unconditionally raise an exception, preventing classes with this metaclass
    from being passed as the second parameter to the :func:`issubclass`
    builtin.
    '''

    def __subclasscheck__(self, obj: object) -> bool:
        raise TypeError(
            f'{self} not passable as second parameter to issubclass().')


class NonIssubclassableClass(object, metaclass=NonIssubclassableMetaclass):
    '''
    Class whose metaclass overrides the ``__subclasscheck__()`` dunder method
    to unconditionally raise an exception, preventing this class from being
    passed as the second parameter to the :func:`issubclass` builtin.
    '''

    pass

# ....................{ CALLABLES ~ async : factory        }....................
# Note that we intentionally avoid declaring a factory function for deprecated
# generator-based coroutines decorated by either the types.coroutine() or
# asyncio.coroutine() decorators. CPython 3.10 removes support for these
# decorators and thus generator-based coroutines. See also:
#     https://docs.python.org/3/library/asyncio-task.html#asyncio.coroutine

async def async_coroutine_factory(text: str) -> Coroutine[None, None, str]:
    '''
    Arbitrary pure-Python asynchronous non-generator coroutine factory
    function.
    '''

    # Defer function-specific imports.
    from asyncio import sleep

    # Asynchronously switch to another scheduled asynchronous callable (if any).
    await sleep(0)

    # Return an arbitrary string.
    return f'{text}Yet not a city, but a flood of ruin'


async def async_generator_factory(text: str) -> AsyncGenerator[str, None]:
    '''
    Arbitrary pure-Python asynchronous generator factory function.
    '''

    # Defer function-specific imports.
    from asyncio import sleep

    # Asynchronously switch to another scheduled asynchronous callable (if any).
    await sleep(0)

    # Yield an arbitrary string.
    yield f'{text}Rolls its perpetual stream; vast pines are strewing'

# ....................{ CALLABLES ~ async : instance       }....................
async_generator = async_generator_factory(
    "Its destin'd path, or in the mangled soil")
'''
Arbitrary pure-Python asynchronous generator.
'''


async_coroutine = async_coroutine_factory(
    "Branchless and shatter'd stand; the rocks, drawn down")
'''
Arbitrary pure-Python asynchronous non-generator coroutine.
'''

# Prevent Python from emitting "ResourceWarning" warnings.
async_coroutine.close()

# ....................{ CALLABLES ~ sync                   }....................
def function():
    '''
    Arbitrary pure-Python function.
    '''

    pass


@contextmanager
def context_manager_factory(obj: object) -> ContextManager[object]:
    '''
    Create and return a new **identity context manager** (i.e., context
    manager trivially yielding the passed object).
    '''

    yield obj

# ....................{ CALLABLES ~ sync : decorator       }....................
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


def decorator_wrapping(func):
    '''
    **Identity wrapping decorator** (i.e., function returning a closure
    wrapping the passed callable in the trivial way by simply passing all
    passed arguments to that callable).
    '''

    # Defer decorator-specific imports.
    from functools import wraps

    @wraps(func)
    def _identity_wrapper(*args, **kwargs):
        '''
        **Identity wrapper** (i.e., closure trivially wrapping that callable).
        '''

        return func(*args, **kwargs)

    # Return this closure.
    return _identity_wrapper

# ....................{ CALLABLES ~ sync : generator       }....................
def sync_generator_factory() -> Generator[int, None, None]:
    '''
    Create and return a pure-Python generator yielding a single integer,
    accepting nothing, and returning nothing.
    '''

    yield 1


def sync_generator_factory_yield_int_send_float_return_str() -> (
    Generator[int, float, str]):
    '''
    Create and return a pure-Python generator yielding integers, accepting
    floating-point numbers sent to this generator by the caller, and returning
    strings.

    See Also
    ----------
    https://www.python.org/dev/peps/pep-0484/#id39
        ``echo_round`` function strongly inspiring this implementation, copied
        verbatim from this subsection of :pep:`484`.
    '''

    # Initial value externally sent to this generator.
    res = yield

    while res:
        res = yield round(res)

    # Return a string constant.
    return 'Unmarred, scarred revenant remnants'

# ....................{ CALLABLES ~ sync : closure         }....................
def closure_factory():
    '''
    Arbitrary pure-Python closure factory function.
    '''

    # Arbitrary non-local variable.
    outer_variable = 42

    def closure():
        '''
        Arbitrary pure-Python closure.
        '''

        nonlocal outer_variable

    # Return this closure.
    return closure


def closure_cell_factory():
    '''
    Arbitrary pure-Python closure cell factory function.
    '''

    # Arbitrary non-local variable.
    outer_variable = 1337

    def closure():
        '''
        Arbitrary pure-Python closure.
        '''

        nonlocal outer_variable

    # Return this closure's first and only cell variable.
    return closure.__closure__[0]

# ....................{ CALLABLES ~ sync : instance        }....................
sync_generator = sync_generator_factory()
'''
Arbitrary pure-Python synchronous generator.
'''

# ....................{ CONSTANTS                          }....................
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

# ....................{ CONSTANTS ~ filenames              }....................
MODULE_FILENAME = __file__
'''
Absolute filename of the current submodule, declared purely for convenience.
'''

# ....................{ SETS ~ callable                    }....................
CALLABLES_PYTHON = frozenset((
    function,
    Class,
    Class.instance_method,
    Class.class_method,
    Class.static_method,
))
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


CALLABLES = CALLABLES_PYTHON | CALLABLES_C
'''
Frozen set of both pure-Python *and* C-based callables exercising edge cases.
'''


#FIXME: Currently unused but preserved for posterity.
# NON_CALLABLES = (
#     CALLABLE_CODE_OBJECT,
#     type.__dict__,      # Mapping Proxy Type
#     implementation,     # Simple Namespace Type
#     async_coroutine,
#     async_generator,
#     sync_generator,
#     closure_cell_factory(), # Cell type
#     TRACEBACK,
#     TRACEBACK.tb_frame,
# )
# '''
# Tuple of callable-like non-callable objects exercising edge cases, intentionally
# defined as a tuple rather than frozen set due to the unhashability of one or
# more members (e.g., ``TRACEBACK``).
# '''

# ....................{ SETS ~ type : builtin              }....................
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

# ....................{ SETS ~ type : non-builtin          }....................
# Fully initialized below by the _init() function.
TYPES_BUILTIN_FAKE = None
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


# Fully initialized below by the _init() function.
TYPES_NONBUILTIN = None
'''
Frozen set of arbitrary non-builtin types.
'''

# ....................{ INITIALIZERS                       }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer initialization-specific imports.
    import builtins, types
    from beartype._data.mod.datamodpy import BUILTINS_MODULE_NAME
    from beartype._util.utilobject import get_object_type_unless_type

    # Global variables assigned to below.
    global TYPES_BUILTIN_FAKE, TYPES_NONBUILTIN

    # Set of all fake builtin types.
    TYPES_BUILTIN_FAKE_SET = set()

    # Frozen set of all standard modules well-known to define at least one fake
    # builtin type.
    #
    # Note that, although the "builtins" module defines *MOST* fake builtins,
    # the "types" module defines *SOME* fake builtins as well. These include:
    # * "types.TracebackType".
    MODULES_TYPES_BUILTIN_FAKE = frozenset((builtins, types))

    # For each such module...
    for module_type_builtin_fake in MODULES_TYPES_BUILTIN_FAKE:
        # For each builtin (i.e., globally accessible object implicitly imported
        # by the active Python interpreter into *EVERY* lexical context)...
        for builtin in module_type_builtin_fake.__dict__.values():
            # Type of this builtin if this builtin is *NOT* a type or this
            # builtin type as is.
            type_builtin = get_object_type_unless_type(builtin)

            # If...
            if (
                # This builtin type insists itself to be defined by the
                # "builtins" module and thus be a builtin *AND*...
                type_builtin.__module__ == BUILTINS_MODULE_NAME and
                # The "builtins" module contains *NO* globally-scoped attribute
                # whose name is that of this type...
                type_builtin.__name__ not in builtins.__dict__
            # Add this cheatin', lyin', no-good fake builtin type to this set.
            ):
                TYPES_BUILTIN_FAKE_SET.add(type_builtin)

    # Frozen set of all fake builtin types.
    TYPES_BUILTIN_FAKE = frozenset((TYPES_BUILTIN_FAKE_SET))

    # Frozen set of arbitrary non-builtin types.
    TYPES_NONBUILTIN = frozenset((
        # Arbitrary non-builtin type.
        Class,
    )) | TYPES_BUILTIN_FAKE


# Initialize this submodule.
_init()
