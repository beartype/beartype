#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **generic types data** submodule.

This submodule predefines low-level class constants exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    AsyncGenerator,
    AsyncIterator,
    Callable,
    Coroutine,
    Generator,
    Iterable,
    Iterator,
    Tuple,
)
from beartype._util.func.utilfuncmake import make_func
from collections import defaultdict
from collections.abc import (
    Hashable as HashableABC,
    ItemsView as ItemsViewABC,
    KeysView as KeysViewABC,
    ValuesView as ValuesViewABC,
    Sized as SizedABC,
)
from contextlib import (
    asynccontextmanager,
    contextmanager,
)
from enum import Enum
from functools import (
    lru_cache,
    partial,
    update_wrapper,
    wraps,
)
from sys import exc_info

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

# ....................{ CALLABLES ~ sync : api : contextlib}....................
@asynccontextmanager
async def async_context_manager_factory(obj: object) -> AsyncIterator[object]:
    '''
    **Asynchronous context manager factory** (i.e., function creating and
    returning a new **asynchronous identity context manager** (i.e., context
    manager trivially yielding the passed object implemented as a generator
    factory function decorated by the standard
    :func:`contextlib.asynccontextmanager` decorator)).
    '''

    yield obj

# ....................{ CALLABLES ~ sync                   }....................
def function():
    '''
    Arbitrary pure-Python function physically declared by this submodule.
    '''

    pass


function_lambda = lambda: 'The day was fair and sunny: sea and sky'
'''
Arbitrary pure-Python lambda function physically declared by this submodule.
'''


function_in_memory = make_func(
    func_name='function_in_memory',
    func_code='''
def function_in_memory():
    return 'And tremble and despoil themselves: oh hear!'
''',
    func_doc='''
Arbitrary pure-Python function dynamically declared in-memory.
''')


@wraps(function)
def wrapper_isomorphic(*args, **kwargs):
    '''
    **Isomorphic wrapper** (i.e., higher-level function transparently preserving
    both the positions and types of all parameters and returns passed to the
    lowel-level wrappee callable).
    '''

    return function(*args, **kwargs)

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


def decorator_isomorphic(func):
    '''
    **Isomorphic decorator** (i.e., function returning an isomorphic decorator
    closure transparently preserving both the positions and types of all
    parameters passed to the passed callable).
    '''

    @wraps(func)
    def _closure_isomorphic(*args, **kwargs):
        '''
        **Isomorphic decorator closure** (i.e., closure transparently
        preserving both the positions and types of all parameters and returns
        passed to the decorated callable).
        '''

        return func(*args, **kwargs)

    # Return this closure.
    return _closure_isomorphic


def decorator_nonisomorphic(func):
    '''
    **Non-isomorphic decorator** (i.e., function returning a non-isomorphic
    decorator closure destroying the positions and/or types of one or more
    parameters passed to the passed callable).
    '''

    @wraps(func)
    def _closure_nonisomorphic():
        '''
        **Non-isomorphic decorator closure** (i.e., closure destroying the
        positions and/or types of one or more parameters passed to the decorated
        callable).
        '''

        return func()

    # Return this closure.
    return _closure_nonisomorphic

# ....................{ CALLABLES ~ sync : wrapper         }....................
def function_wrappee(text_one: str, text_two: str) -> str:
    '''
    **Annotated wrappee** (i.e., lower-level function annotated by one or more
    type hints and subsequently wrapped by a higher-level wrapper function).
    '''

    return text_one + text_two


# Note that the "assigned" parameter is intentionally passed the empty tuple,
# preserving the original "__name__" and "__qualname__" dunder attributes of
# wrapper callables for debuggability.
@wraps(function_wrappee, assigned=())
def function_wrapper_nonisomarphic(text):
    '''
    **Non-isomorphic wrapper** (i.e., higher-level function destroying the
    positions and/or types of one or more parameters passed to the lower-level
    function wrapped by this wrapper).
    '''

    return function_wrappee(text[0], text[1:])


@wraps(function_wrapper_nonisomarphic, assigned=())
def function_wrapper_isomarphic(*args, **kwargs):
    '''
    **Isomorphic wrapper** (i.e., higher-level function preserving both the
    positions and types of all parameters passed to the lower-level
    non-isomarphic wrapper wrapped by this wrapper).
    '''

    return function_wrapper_nonisomarphic(*args, **kwargs)


@wraps(function_wrapper_nonisomarphic, assigned=())
def function_wrapper_isomarphic_args(*args):
    '''
    **Positionally isomorphic wrapper** (i.e., higher-level function preserving
    both the positions and types of all parameters excluding keyword parameters
    passed to the lower-level non-isomarphic wrapper wrapped by this wrapper).
    '''

    return function_wrapper_nonisomarphic(*args)


@wraps(function_wrapper_nonisomarphic, assigned=())
def function_wrapper_isomarphic_kwargs(**kwargs):
    '''
    **Keyword isomorphic wrapper** (i.e., higher-level function preserving both
    the positions and types of all parameters excluding positional parameters
    passed to the lower-level non-isomarphic wrapper wrapped by this wrapper).
    '''

    return function_wrapper_nonisomarphic(**kwargs)


class ClassCallableWrapperIsomorphic(object):
    '''
    **Callable class** (i.e., pure-Python class defining the :meth:`__call__`
    dunder method implicitly called by Python when instances of this class are
    called using the standard calling convention such that that :meth:`__call__`
    dunder method is defined as an isomorphic wrapper method wrapping an
    isomorphic wrapper function).
    '''

    def __call__(self, *args, **kwargs):
        '''
        Arbitrary isomorphic wrapper dunder method implicitly wrapping an
        isomorphic wrapper function.
        '''

        return function_wrapper_isomarphic(*args, **kwargs)


    @wraps(function_wrappee)
    def method_wrapper_isomorphic(self, *args, **kwargs):
        '''
        Arbitrary isomorphic wrapper method explicitly wrapping a wrappee
        function, decorated by the :func:`.wraps` decorator.
        '''

        return function_wrappee(*args, **kwargs)


    def method_wrapper_isomorphic_implicit(self, *args, **kwargs):
        '''
        Arbitrary isomorphic wrapper method implicitly wrapping a wrappee
        function *without* being decorated by the :func:`.wraps` decorator.
        '''

        return function_wrappee(*args, **kwargs)


object_callable_wrapper_isomorphic = ClassCallableWrapperIsomorphic()
'''
**Pseudo-callable object** (i.e., pure-Python object whose class defines the
:meth:`__call__` dunder method implicitly called by Python when instances of
this class are called using the standard calling convention such that that
:meth:`__call__` dunder method is defined as an isomorphic wrapper method
wrapping an isomorphic wrapper function).
'''

# Declare that this pseudo-callable object wraps this lower-level function.
update_wrapper(
    wrapper=object_callable_wrapper_isomorphic,
    wrapped=function_wrapper_isomarphic,
    assigned=(),
)

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


sync_generator = sync_generator_factory()
'''
Arbitrary pure-Python synchronous generator.
'''

# ....................{ CALLABLES ~ sync : api : contextlib}....................
@contextmanager
def context_manager_factory(obj: object) -> Iterator[object]:
    '''
    **Context manager factory** (i.e., function creating and returning a new
    **identity context manager** (i.e., context manager trivially yielding the
    passed object implemented as a generator factory function decorated by the
    standard :func:`contextlib.contextmanager` decorator)).
    '''

    yield obj

# ....................{ CALLABLES ~ sync : api : functools }....................
@lru_cache
def function_lru_cached(n: int) -> int:
    '''
    Arbitrary :func:`functools.lru_cache`-memoized function.
    '''

    return n + 1


def function_partialized(
    and_one_majestic_river: str,
    that_mighty_shadow_loves: str,
) -> str:
    '''
    Arbitrary pure-Python function to be wrapped by the :class:`.partial`
    factory as the :data:`.function_partial` object, accepting both positional
    and keyword parameters to exercise all possible edge cases.
    '''

    return and_one_majestic_river + that_mighty_shadow_loves


FUNCTION_PARTIALIZED_ARG_VALUE = (
    'The breath and blood of distant lands, for ever')
'''
Arbitrary value passed as the first and only positional parameter to the
:func:`function_partialized` function by the :data:`.function_partial` object.
'''


FUNCTION_PARTIALIZED_KWARG_NAME = 'that_mighty_shadow_loves'
'''
Name of the first and only keyword parameter passed to the
:func:`function_partialized` function by the :data:`.function_partial` object.
'''


FUNCTION_PARTIALIZED_KWARG_VALUE = 'The slimy caverns of the populous deep.'
'''
Arbitrary value passed as the first and only keyword parameter to the
:func:`function_partialized` function by the :data:`.function_partial` object.
'''


builtin_partial = partial(divmod, 2)
'''
Arbitrary instance of the :class:`.partial` factory wrapping the C-based
:func:`divmod` builtin.
'''


function_partial = partial(
    function_partialized,
    FUNCTION_PARTIALIZED_ARG_VALUE,
    that_mighty_shadow_loves=FUNCTION_PARTIALIZED_KWARG_VALUE,
)
'''
Arbitrary instance of the :class:`.partial` factory wrapping the pure-Python
:func:`function_partialized` function.
'''


function_partial_bad = partial(
    function_partialized,
    FUNCTION_PARTIALIZED_ARG_VALUE,
    that_mighty_shadow_loves=FUNCTION_PARTIALIZED_KWARG_VALUE,
    the_day_was_fair_and_sunny='sea and sky',
)
'''
Arbitrary instance of the :class:`.partial` factory wrapping the pure-Python
:func:`function_partialized` function in an invalid manner by passing more
parameters than that function actually accepts.
'''

# ....................{ CALLABLES ~ sync : module          }....................
def function_module_name_fake() -> None:
    '''
    Arbitrary pure-Python class with a **non-existent module name** (i.e., whose
    ``__module__`` dunder attribute refers to a file that is guaranteed to *not*
    exist on the local filesystem).
    '''

    pass


def function_module_name_none() -> None:
    '''
    Arbitrary pure-Python function with a **missing module name** (i.e., whose
    ``__module__`` dunder attribute is :data:`None`).
    '''

    pass


# Monkey-patch the above callables with "bad" module names.
function_module_name_fake.__module__ = 'He_had.a_mask.like_Castlereagh'
function_module_name_none.__module__ = None

# ....................{ CLASSES ~ abc                      }....................
class ClassSized(object):
    '''
    Class manually satisfying *only* the standard :class:`collections.abc.Sized`
    protocol *without* simply subclassing a builtin immutable sized type (e.g.,
    :class:`str`).
    '''

    def __init__(self, sized: SizedABC) -> None: self._sized = sized
    def __len__(self) -> int: return len(self._sized)

# ....................{ CLASSES ~ abc : mapping            }....................
class ClassMapping(object):
    '''
    Class manually satisfying *only* the standard
    :class:`collections.abc.Mapping` protocol *without* simply subclassing a
    builtin mutable dictionary type (e.g., :class:`dict`).
    '''

    __abc_tpflags__ = 1 << 6 # Py_TPFLAGS_MAPPING
    def __init__(self, items: dict) -> None: self._items = items
    def __contains__(self, item: object) -> bool: return item in self._items
    def __iter__(self) -> Iterator: return iter(self._items)
    def __len__(self) -> int: return len(self._items)
    def __eq__(self, other: 'ClassMapping') -> bool:
        return self._items == other._items
    def __ne__(self, other: 'ClassMapping') -> bool:
        return self._items != other._items
    def __getitem__(self, key: HashableABC) -> object: return self._items[key]
    def get(self, *args, **kwargs) -> object:
        return self._items.get(*args, **kwargs)
    def items(self) -> ItemsViewABC: return self._items.items()
    def keys(self) -> KeysViewABC: return self._items.keys()
    def values(self) -> ValuesViewABC: return self._items.values()


class ClassMutableMapping(ClassMapping):
    '''
    Class manually satisfying *only* the standard
    :class:`collections.abc.MutableMapping` protocol *without* simply
    subclassing a builtin mutable dictionary type (e.g., :class:`dict`).
    '''

    def __delitem__(self, key: HashableABC) -> None: del self._items[key]
    def __setitem__(self, key: HashableABC, value: object) -> None:
        self._items[key] = value
    def clear(self) -> None: self._items.clear()
    def pop(self, *args, **kwargs) -> object:
        return self._items.pop(*args, **kwargs)
    def popitem(self) -> Tuple[object, object]: return self._items.popitem()
    def setdefault(self, *args, **kwargs) -> object:
        return self._items.setdefault(*args, **kwargs)
    def update(self, *args, **kwargs) -> object:
        return self._items.update(*args, **kwargs)

# ....................{ CLASSES ~ abc : sequence           }....................
class ClassContainer(object):
    '''
    Class manually satisfying *only* the standard
    :class:`collections.abc.Container` protocol *without* simply subclassing a
    builtin immutable container type (e.g., :class:`str`).
    '''

    def __init__(self, items: list) -> None: self._items = items
    def __contains__(self, item: object) -> bool: return item in self._items


class ClassCollection(ClassContainer):
    '''
    Class manually satisfying *only* the standard
    :class:`collections.abc.Collection` protocol *without* simply subclassing a
    builtin immutable container type (e.g., :class:`bytes`).
    '''

    def __iter__(self) -> Iterator: return iter(self._items)
    def __len__(self) -> int: return len(self._items)


class ClassSequence(ClassCollection):
    '''
    Class manually satisfying *only* the standard
    :class:`collections.abc.Sequence` protocol *without* simply subclassing a
    builtin immutable sequence type (e.g., :class:`tuple`).
    '''

    def __getitem__(self, index: int) -> object: return self._items[index]
    def __reversed__(self) -> Iterator: return reversed(self._items)
    def count(self, item: object) -> int: return self._items.count(item)
    def index(self, *args, **kwargs) -> int:
        return self._items.index(*args, **kwargs)


class ClassMutableSequence(ClassSequence):
    '''
    Class manually satisfying *only* the standard
    :class:`collections.abc.MutableSequence` protocol *without* simply
    subclassing a builtin mutable sequence type (e.g., :class:`list`).
    '''

    def __delitem__(self, index: int) -> None: del self._items[index]
    def __setitem__(self, index: int, item: object) -> None:
        self._items[index] = item
    def __iadd__(self, item: object) -> object: self._items += item
    def append(self, item: object) -> None: self._items.append(item)
    def clear(self) -> None: self._items.clear()
    def extend(self, items: Iterable) -> None: self._items.extend(items)
    def insert(self, index: int, item: object) -> None:
        self._items.insert(index, item)
    def pop(self, *args, **kwargs) -> object:
        return self._items.pop(*args, **kwargs)
    def remove(self, item: object) -> None: self._items.remove(item)
    def reverse(self) -> None: self._items.reverse()



class ClassMappingSequence(ClassMapping, ClassSequence):
    '''
    Class manually satisfying both the standard :class:`collections.abc.Mapping`
    *and* :class:`collections.abc.Sequence` protocols *without* simply
    subclassing a builtin mapping or sequence type (e.g., :class:`list`).
    '''

    pass

# ....................{ CLASSES ~ builtin                  }....................
class ClassDict(dict):
    '''
    Class subclassing the builtin C-based :class:`dict` type.
    '''

    pass


class ClassList(list):
    '''
    Class subclassing the builtin C-based :class:`list` type.
    '''

    pass

# ....................{ CLASSES ~ enum                     }....................
class MasterlessDecreeVenomlessWhich(Enum):
    '''
    Arbitrary enumeration whose members are accessed elsewhere as integers,
    typically when subscripting the :pep:`586`-compliant :attr:`typing.Literal`
    type hint factory.
    '''

    NOMENCLATURE_WEATHER_VANES_OF = 0
    NOMINALLY_UNSWAIN_AUTODIDACTIC_IDIOCRACY_LESS_A = 1

# ....................{ CLASSES ~ dunder : call            }....................
class ClassCallable(object):
    '''
    **Callable class** (i.e., pure-Python class defining the :meth:`__call__`
    dunder method implicitly called by Python when instances of this class are
    called using the standard calling convention).
    '''

    def __call__(self, *args, **kwargs) -> int:
        '''
        Dunder method implicitly called when this object is called.
        '''

        return len(args) + len(kwargs)

# ....................{ CLASSES ~ dunder : instancecheck   }....................
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

# ....................{ CLASSES ~ dunder : subclasscheck   }....................
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

# ....................{ CLASSES ~ dunder : module          }....................
class ClassModuleNameFake(object):
    '''
    Arbitrary pure-Python class with a **non-existent module name** (i.e., whose
    ``__module__`` dunder attribute refers to a file that is guaranteed to *not*
    exist on the local filesystem).
    '''

    pass


class ClassModuleNameNone(object):
    '''
    Arbitrary pure-Python class with a **missing module name** (i.e., whose
    ``__module__`` dunder attribute is :data:`None`).
    '''

    pass


# Monkey-patch the above classes with "bad" module names.
ClassModuleNameFake.__module__ = 'If_I.were.a_dead_leaf.thou_mightest.bear'
ClassModuleNameNone.__module__ = None

# ....................{ CLASSES ~ hierarchy : 1            }....................
# Arbitrary class hierarchy.

class Class(object):
    '''
    Arbitrary pure-Python class defining arbitrary methods.
    '''

    # ....................{ NESTED                         }....................
    class NestedClass(object):
        '''
        Arbitrary pure-Python **nested class** whose definition is nested inside
        the definition of another class.
        '''

        pass

    # ....................{ METHODS                        }....................
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

# ....................{ DICTS                              }....................
def _default_dict_str_factory() -> str:
    '''
    Arbitrary factory function returning arbitrary strings.
    '''

    return 'His steps to the sea-shore. A swan was there,'


default_dict_int_to_str = defaultdict(_default_dict_str_factory)
'''
Non-empty default dictionary mapping integers to strings, initialized with an
arbitrary factory function returning arbitrary strings.
'''
default_dict_int_to_str[0] = 'Beside a sluggish stream among the reeds.'
default_dict_int_to_str[1] # == 'His steps to the sea-shore. A swan was there,'


default_dict_str_to_str = defaultdict(_default_dict_str_factory)
'''
Non-empty default dictionary mapping strings to strings, initialized with an
arbitrary factory function returning arbitrary strings.
'''
default_dict_str_to_str['His eyes pursued its flight.'] = (
    'Thou hast a home,')

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
--------
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
    from beartype._data.api.standard.datamodpy import BUILTINS_MODULE_NAME
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
        for builtin_name, builtin in module_type_builtin_fake.__dict__.items():
            # Either:
            # * If this builtin is already a class, this builtin as is.
            # * If this builtin is *NOT* already a class, this builtin's class.
            builtin_type = get_object_type_unless_type(builtin)

            # If...
            if (
                # This builtin type insists itself to be defined by the
                # "builtins" module and thus be a builtin *AND*...
                builtin_type.__module__ == BUILTINS_MODULE_NAME and
                # The "builtins" module contains *NO* globally-scoped attribute
                # whose name is that of this type...
                builtin_type.__name__ not in builtins.__dict__
            # Add this cheatin', lyin', no-good fake builtin type to this set.
            ):
                # if builtin_type.__name__ == 'PyCapsule':
                #     print(f'Auto-detected fake PyCapsule {repr(builtin_name)}...')
                    # continue
                # print(f'Auto-detected fake builtin type {repr(builtin_type)}...')
                TYPES_BUILTIN_FAKE_SET.add(builtin_type)

    # Frozen set of all fake builtin types.
    TYPES_BUILTIN_FAKE = frozenset((TYPES_BUILTIN_FAKE_SET))

    # Frozen set of arbitrary non-builtin types.
    TYPES_NONBUILTIN = frozenset((
        # Arbitrary non-builtin type.
        Class,
    )) | TYPES_BUILTIN_FAKE
    # print(f'Auto-detected non-builtin types: {repr(TYPES_NONBUILTIN)}')


# Initialize this submodule.
_init()
