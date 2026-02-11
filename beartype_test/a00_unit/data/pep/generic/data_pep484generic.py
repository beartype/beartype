#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`484`-compliant **generics** (i.e., subclasses of the standard
:pep:`484`-compliant :class:`typing.Generic` superclass, exercising edge cases
in unit tests requiring non-trivial generics).
'''

# ....................{ IMPORTS                            }....................
# Defer fixture-specific imports.
from beartype.typing import Generic
from beartype_test.a00_unit.data.data_type import Class
from beartype_test.a00_unit.data.pep.data_pep484 import (
    S,
    T,
)
from collections.abc import (
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
    generic parametrized by the same unconstrained type variable.
    '''

    pass


class Pep484GenericSubTToS(Pep484GenericT[S]):
    '''
    :pep:`484`-compliant generic subclass inheriting a :pep:`484`-compliant
    generic parametrized by a different unconstrained type variable.
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

# ....................{ PEP 484 ~ usable : T               }....................
# Generics that are actually instantiable and usable as valid objects.

class Pep484ContextManagerTSequenceT(
    Nongeneric, Pep484ContextManager[T], Pep484Sequence[T]):
    '''
    :pep:`484`-compliant generic subclassing multiple :mod:`collection.abc`
    abstract base classes (ABCs) parametrized by the same unconstrained type
    variable *and* a normal non-generic class.
    '''

    # ....................{ INITIALIZERS                   }....................
    def __init__(self, sequence: Pep484Tuple[T]) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(sequence, tuple), f'{repr(sequence)} not tuple.'
        self._sequence = sequence

    # ....................{ DUNDERS                        }....................
    # Define all protocols mandated by ABCs subclassed by this generic.

    def __call__(self) -> int:
        return len(self)

    def __contains__(self, obj: object) -> bool:
        return obj in self._sequence

    def __enter__(self) -> 'Pep484ContextManagerTSequenceT':
        return self

    def __exit__(self, *args, **kwargs) -> bool:
        return False

    def __getitem__(self, index: int) -> T:
        return self._sequence[index]

    def __iter__(self) -> Pep484Iterator[T]:
        return iter(self._sequence)

    def __len__(self) -> int:
        return len(self._sequence)

    def __reversed__(self) -> Pep484Tuple[T]:
        return reversed(self._sequence)


class Pep484IterableTContainerT(Pep484Iterable[T], Pep484Container[T]):
    '''
    :pep:`484`-compliant generic subclassing multiple directly parametrized
    :mod:`typing` types.
    '''

    # ....................{ INITIALIZERS                   }....................
    def __init__(self, sequence: Pep484Tuple[T]) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(sequence, tuple), f'{repr(sequence)} not tuple.'
        self._sequence = sequence

    # ....................{ DUNDERS                        }....................
    # Define all protocols mandated by ABCs subclassed by this generic. Also
    # define all *OTHER* protocols mandated by the "sequences.abc.Collection"
    # ABC to enable @beartype to generate code deeply type-checking one or more
    # of the items of instances of this generic.

    def __contains__(self, obj: object) -> bool:
        return obj in self._sequence

    def __getitem__(self, index: int) -> T:
        return self._sequence[index]

    def __iter__(self) -> Pep484Iterator[T]:
        return iter(self._sequence)

    def __len__(self) -> int:
        return len(self._sequence)

# ....................{ PEP 484 ~ usable : S, T            }....................
# Generics that are actually instantiable and usable as valid objects.

class Pep484IterableTupleSTContainerTupleST(
    SizedABC,
    Pep484Iterable[Pep484Tuple[S, T]],
    Pep484Container[Pep484Tuple[S, T]],
):
    '''
    :pep:`484`-compliant generic subclassing multiple :mod:`typing` types
    indirectly parametrized (but unsubscripted) by multiple type variables *and*
    an unsubscripted and unparametrized :mod:`collections.abc` ABC.
    '''

    # ....................{ INITIALIZERS                   }....................
    def __init__(self, sequence: Pep484Tuple[Pep484Tuple[S, T]]) -> None:
        '''
        Initialize this generic from the passed tuple of 2-tuples.
        '''

        assert isinstance(sequence, tuple), f'{repr(sequence)} not tuple.'
        self._sequence = sequence

    # ....................{ DUNDERS                        }....................
    # Define all protocols mandated by ABCs subclassed by this generic.
    def __contains__(self, obj: object) -> bool:
        return obj in self._sequence

    def __iter__(self) -> Pep484Iterator[Pep484Tuple[S, T]]:
        return iter(self._sequence)

    def __len__(self) -> int:
        return len(self._sequence)
