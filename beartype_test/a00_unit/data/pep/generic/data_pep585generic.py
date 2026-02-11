#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`585`-compliant **generics** (i.e., subclasses of a
:pep:`585`-compliant type hint factory subscripted by one or more type
parameters, exercising edge cases in unit tests requiring non-trivial generics).
'''

# ....................{ IMPORTS                            }....................
# Defer fixture-specific imports.
from beartype.typing import TypeVar
from beartype_test.a00_unit.data.data_type import Class
from beartype_test.a00_unit.data.pep.data_pep484 import (
    S,
    T,
    U,
)
from collections.abc import (
    Container as Pep585Container,
    Iterable as Pep585Iterable,
    Iterator as Pep585Iterator,
    Sequence as Pep585Sequence,
    Sized as SizedABC,
)
from contextlib import (
    AbstractContextManager as Pep585AbstractContextManager,
)

# ....................{ NON-PEP                            }....................
Nongeneric = Class
'''
Arbitrary PEP-noncompliant non-generic type.
'''

# ....................{ PEP 585 ~ non-T                    }....................
class Pep585ListStr(list[str]):
    '''
    :pep:`585`-compliant generic subclassing the builtin :class:`list` type
    subscripted (but unparametrized) by one child hint.
    '''

    # Redefine this generic's representation for debugging purposes.
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'


class Pep585ListListStr(list[list[str]]):
    '''
    :pep:`585`-compliant generic subclassing the builtin :class:`list` type
    itself subscripted the builtin :class:`list` type subscripted (but
    unparametrized) by one child hint.
    '''

    pass

# ....................{ PEP 585 ~ T                        }....................
# Note we intentionally do *NOT* declare unsubscripted PEP 585-compliant
# generics (e.g., "class Pep585List(list):"). Why? Because PEP 585-compliant
# generics are necessarily subscripted; when unsubscripted, the corresponding
# subclasses are simply standard types.

class Pep585SequenceT(Pep585Sequence[T]):
    '''
    :pep:`585`-compliant generic sequence parametrized by one unconstrained type
    variable.
    '''

    pass

# ....................{ PEP 585 ~ T : list                 }....................
class Pep585ListT(list[T]):
    '''
    :pep:`585`-compliant generic list subclassing the builtin :class:`list` type
    parametrized by one unconstrained type variable.
    '''

    # Redefine this generic's representation for debugging purposes.
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'


T_Pep585ListT = TypeVar('T_Pep585ListT', bound=Pep585ListT)  # <-- clever, yet sickening
'''
**Indirectly recursive type variable** (i.e., :pep:`484`-compliant type variable
inducing recursion when subscripting the otherwise non-recursive generic to
which this type variable is bound).
'''

# ....................{ PEP 585 ~ U                        }....................
class Pep585SequenceU(Pep585Sequence[U]):
    '''
    :pep:`585`-compliant generic sequence parametrized by one unconstrained type
    variable.
    '''

    pass

# ....................{ PEP 585 ~ S, T                     }....................
class Pep585DictST(dict[S, T]):
    '''
    :pep:`585`-compliant generic subclassing the builtin :class:`dict` type
    parametrized by multiple unconstrained type variables.
    '''

    # Redefine this generic's representation for debugging purposes.
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'

# ....................{ PEP 585 ~ usable : T               }....................
# Generics that are actually instantiable and usable as valid objects.

class Pep585IterableTContainerT(Pep585Iterable[T], Pep585Container[T]):
    '''
    :pep:`585`-compliant generic subclassing multiple :mod:`collections.abc`
    abstract base classes (ABCs) directly parametrized by the same unconstrained
    type variable.
    '''

    # ................{ INITIALIZERS                           }................
    def __init__(self, sequence: tuple[T]) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(sequence, tuple), f'{repr(sequence)} not tuple.'
        self._sequence = sequence

    # ................{ ABCs                                   }................
    # Define all protocols mandated by ABCs subclassed by this generic.
    def __contains__(self, obj: object) -> bool:
        return obj in self._sequence

    def __getitem__(self, index: int) -> T:
        return self._sequence[index]

    def __iter__(self) -> Pep585Iterator[T]:
        return iter(self._sequence)

    def __len__(self) -> int:
        return len(self._sequence)


class Pep585ContextManagerTSequenceT(
    Nongeneric, Pep585AbstractContextManager[T], Pep585Sequence[T]):
    '''
    :pep:`585`-compliant generic subclassing multiple :mod:`collection.abc`
    abstract base classes (ABCs) parametrized by the same unconstrained type
    variable *and* a normal non-generic class.
    '''

    # ................{ INITIALIZERS                           }................
    def __init__(self, sequence: tuple[T]) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(sequence, tuple), f'{repr(sequence)} not tuple.'
        self._sequence = sequence

    # ................{ ABCs                                   }................
    # Define all protocols mandated by ABCs subclassed by this generic.

    def __call__(self) -> int:
        return len(self)

    def __contains__(self, obj: object) -> bool:
        return obj in self._sequence

    def __enter__(self) -> 'Pep585ContextManagerTSequenceT':
        return self

    def __exit__(self, *args, **kwargs) -> bool:
        return False

    def __getitem__(self, index: int) -> T:
        return self._sequence[index]

    def __iter__(self) -> Pep585Iterator[T]:
        return iter(self._sequence)

    def __len__(self) -> bool:
        return len(self._sequence)

    def __reversed__(self) -> tuple[T]:
        return reversed(self._sequence)

# ....................{ PEP 585 ~ usable : S, T            }....................
# Generics that are actually instantiable and usable as valid objects.

class Pep585IterableTupleSTContainerTupleST(
    SizedABC, Pep585Iterable[tuple[S, T]], Pep585Container[tuple[S, T]]):
    '''
    :pep:`585`-compliant generic subclassing multiple :mod:`collections.abc`
    abstract base classes (ABCs) indirectly parametrized (but unsubscripted) by
    multiple type variables *and* an unsubscripted and unparametrized
    :mod:`collections.abc` ABC.
    '''

    # ................{ INITIALIZERS                           }................
    def __init__(self, sequence: tuple[T]) -> None:
        '''
        Initialize this generic from the passed tuple of 2-tuples.
        '''

        assert isinstance(sequence, tuple), f'{repr(sequence)} not tuple.'
        self._sequence = sequence

    # ................{ ABCs                                   }................
    # Define all protocols mandated by ABCs subclassed by this generic.
    def __contains__(self, obj: object) -> bool:
        return obj in self._sequence

    def __iter__(self) -> bool:
        return iter(self._sequence)

    def __len__(self) -> bool:
        return len(self._sequence)

# ....................{ PEP 585 ~ usable : S, T, U         }....................
# Generics that are actually instantiable and usable as valid objects.

class Pep585ListRootU(list[U]):
    '''
    :pep:`585`-compliant generic list subclassing the builtin :class:`list` type
    parametrized by one unconstrained type variable.
    '''

    pass


class Pep585ListStemT(Pep585ListRootU[T]):
    '''
    :pep:`585`-compliant generic parametrized by one unconstrained type variable
    subclassing a :pep:`585`-compliant generic list subclassing the builtin
    :class:`list` type parametrized by a different unconstrained type variable.
    '''

    pass


class Pep585ListLeafS(Pep585ListStemT[S]):
    '''
    :pep:`585`-compliant generic parametrized by one unconstrained type variable
    subclassing a similar :pep:`585`-compliant generic subclassing a
    :pep:`585`-compliant generic list subclassing the builtin :class:`list` type
    parametrized by a different unconstrained type variable.
    '''

    pass
