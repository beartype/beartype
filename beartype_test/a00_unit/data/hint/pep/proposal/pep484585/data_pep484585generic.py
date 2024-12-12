#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **generics** (i.e., :pep:`484`- and/or :pep:`585`-compliant
subclasses of the standard :class:`typing.Generic` superclass, exercising edge
cases in unit tests requiring non-trivial generics).
'''

# ....................{ IMPORTS                            }....................
# Defer fixture-specific imports.
from beartype.typing import (
    Generic,
    List,
    Sequence,
)
from beartype._data.hint.datahinttyping import (
    S,
    T,
    U,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype_test.a00_unit.data.data_type import Class
from collections.abc import (
    Callable as CallableABC,
    Sized as SizedABC,
)

# Intentionally import from the standard "typing" module rather than the
# forward-compatible "beartype.typing" subpackage to ensure PEP
# 484-compliance.
from typing import (
    Container as Pep484Container,
    ContextManager as Pep484ContextManager,
    Iterable as Pep484Iterable,
    Iterator as Pep484Iterator,
    List as Pep484List,
    Sequence as Pep484Sequence,
    Tuple as Pep484Tuple,
)

# ....................{ NON-PEP                            }....................
Nongeneric = Class
'''
Arbitrary PEP-noncompliant non-generic type.
'''

# ....................{ PEP 484 ~ non-T                    }....................
class Pep484ListUnsubscripted(Pep484List):
    '''
    :pep:`484`-compliant generic subclassing an unsubscripted :mod:`typing` type
    hint factory.
    '''

    pass


class Pep484ListStr(Pep484List[str]):
    '''
    :pep:`484`-compliant generic subclassing an unparametrized :mod:`typing`
    type hint factory.
    '''

    pass


class Pep484ListListStr(Pep484List[Pep484List[str]]):
    '''
    :pep:`484`-compliant generic subclassing a :mod:`typing` type hint factory
    subscripted by the same unparametrized :mod:`typing` type hint factory.
    '''

    pass

# ....................{ PEP 484 : T                        }....................
class Pep484GenericT(Generic[T]):
    '''
    :pep:`484`-compliant generic superclass parametrized by one unconstrained
    type variable.
    '''

    pass


class Pep484GenericSubT(Pep484GenericT[T]):
    '''
    :pep:`484`-compliant generic subclass inheriting a :pep:`484`-compliant
    generic parametrized by one unconstrained type variable.
    '''

    pass

# ....................{ PEP 484 : S, T                     }....................
class Pep484GenericST(Generic[S, T]):
    '''
    :pep:`484`-compliant generic subclassing the root :class:`typing.Generic`
    superclass parametrized by two type variables.
    '''

    pass


class Pep484GenericSInt(Pep484GenericST[S, int]):
    '''
    :pep:`484`-compliant partially concrete generic subclass inheriting a
    :pep:`484`-compliant generic superclass subscripted first by an
    unconstrained type variable and then by the builtin :class:`int` type.
    '''

    pass


class Pep484GenericIntInt(Pep484GenericST[int, int]):
    '''
    :pep:`484`-compliant concrete generic subclass inheriting a
    :pep:`484`-compliant generic superclass subscripted twice by the
    builtin :class:`int` type.
    '''

    pass

# ....................{ PEP 484 ~ usable : non-T           }....................
# Generics that are actually instantiable and usable as valid objects.

class Pep484CallableContextManagerStrSequenceStr(
    CallableABC, Pep484ContextManager[str], Pep484Sequence[str]):
    '''
    :pep:`484`-compliant generic subclassing multiple unparametrized
    :mod:`typing` types *and* a non-:mod:`typing` abstract base class (ABC).
    '''

    # ....................{ INITIALIZERS                   }....................
    def __init__(self, sequence: tuple) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(sequence, tuple), (
            f'{repr(sequence)} not tuple.')
        self._sequence = sequence

    # ....................{ DUNDERS                        }....................
    # Define all protocols mandated by ABCs subclassed by this generic.

    def __call__(self) -> int:
        return len(self)

    def __contains__(self, obj: object) -> bool:
        return obj in self._sequence

    def __enter__(self) -> object:
        return self

    def __exit__(self, *args, **kwargs) -> bool:
        return False

    def __getitem__(self, index: int) -> object:
        return self._sequence[index]

    def __iter__(self) -> bool:
        return iter(self._sequence)

    def __len__(self) -> bool:
        return len(self._sequence)

    def __reversed__(self) -> object:
        return self._sequence.reverse()

# ....................{ PEP 484 ~ usable : T               }....................
# Generics that are actually instantiable and usable as valid objects.

class Pep484IterableTContainerT(Pep484Iterable[T], Pep484Container[T]):
    '''
    :pep:`484`-compliant generic subclassing multiple directly parametrized
    :mod:`typing` types.
    '''

    # ....................{ INITIALIZERS                   }....................
    def __init__(self, iterable: tuple) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(iterable, tuple), (
            f'{repr(iterable)} not tuple.')
        self._iterable = iterable

    # ....................{ DUNDERS                        }....................
    # Define all protocols mandated by ABCs subclassed by this generic.

    def __contains__(self, obj: object) -> bool:
        return obj in self._iterable

    def __iter__(self) -> bool:
        return iter(self._iterable)

# ....................{ PEP 484 ~ usable : S, T            }....................
# Generics that are actually instantiable and usable as valid objects.

class Pep484IterableTupleSTContainerTupleST(
    SizedABC,
    Pep484Iterable[Pep484Tuple[S, T]],
    Pep484Container[Pep484Tuple[S, T]],
):
    '''
    :pep:`484`-compliant **2-tuple iterable** generic subclassing multiple
    indirectly parametrized :mod:`typing` types *and* a non-:mod:`typing`
    abstract base class (ABC).
    '''

    # ....................{ INITIALIZERS                   }....................
    def __init__(self, iterable: Pep484Iterable[Pep484Tuple[S, T]]) -> None:
        '''
        Initialize this generic from the passed iterable of 2-tuples.
        '''

        assert isinstance(iterable, tuple), (
            f'{repr(iterable)} not tuple.')
        self._iterable = iterable

    # ....................{ DUNDERS                        }....................
    # Define all protocols mandated by ABCs subclassed by this generic.
    def __contains__(self, obj: object) -> bool:
        return obj in self._iterable

    def __iter__(self) -> Pep484Iterator[Pep484Tuple[S, T]]:
        return iter(self._iterable)

    def __len__(self) -> int:
        return len(self._iterable)

# ....................{ PEP (484|585)                      }....................
class Pep484585SequenceT(Sequence[T]):
    '''
    :pep:`484`- or :pep:`585`-compliant generic sequence parametrized by one
    unconstrained type variable.
    '''

    pass


class Pep484585SequenceU(Sequence[U]):
    '''
    :pep:`484`- or :pep:`585`-compliant generic sequence parametrized by one
    unconstrained type variable.
    '''

    pass


class Pep484585GenericSTSequenceU(
    # Order is *EXTREMELY* significant. Avoid modifying, please.
    List[bool],
    Pep484GenericST[int, T],
    Nongeneric,
    Pep484585SequenceU,
):
    '''
    :pep:`484`- or :pep:`585`-compliant generic list parametrized by three
    unconstrained type variables.
    '''

    pass


class Pep484585GenericIntTSequenceU(Pep484585GenericSTSequenceU[float]):
    '''
    :pep:`484`- or :pep:`585`-compliant generic list parametrized by two
    unconstrained type variables.
    '''

    pass


class Pep484585GenericUUST(
    # Order is *EXTREMELY* significant. Avoid modifying, please.
    Pep484585SequenceU, Pep484GenericST, List[U]):
    '''
    :pep:`484`- or :pep:`585`-compliant generic list parametrized by three
    unconstrained type variables, one of which is repeated twice across two
    different pseudo-superclasses at different hierarchical nesting levels.
    '''

    pass

# ..................{ PEP 585                        }..................
# If the active Python interpreter targets Python >= 3.9 and thus
# behaves sanely with respect to complex subscripted generics, define
# complex subscripted generics. For unknown and presumably irrelevant
# reasons, Python 3.8 raises exceptions here. *shrug*
if IS_PYTHON_AT_LEAST_3_9:
    class Pep585GenericUIntT(Pep484585GenericUUST[U, int, T]):
        '''
        :pep:`585`-compliant generic list parametrized by two unconstrained type
        variables, one of which is repeated twice across two different
        pseudo-superclasses at different hierarchical nesting levels.
        '''

        pass
# Else, the active Python interpreter targets Python 3.8 and thus
# behaves insanely with respect to complex subscripted generics. In this
# case, fallback to reducing these generics to simply "None". *shrug*
else:
    Pep585GenericUIntT = None
