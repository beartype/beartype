#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **data fixtures** (i.e.,
high-level session-scoped :mod:`pytest` fixtures exposing various :pep:`484`-
and :pep:`585`-compliant objects, exercising edge cases in unit tests requiring
these fixtures).
'''

# ....................{ IMPORTS                            }....................
from pytest import fixture

# ....................{ CLASSES                            }....................
class _Pep484585Generics(object):
    '''
    **Generics dataclass** (i.e., object yielded by the
    :func:`.pep484585_generics` fixture comprising various :pep:`484`- and
    :pep:`585`-compliant :class:`typing.Generic` subclasses of interest to
    downstream unit tests).

    Attributes
    ----------
    Nongeneric : type
        Arbitrary PEP-noncompliant non-generic type.
    Pep484GenericTypevaredSingle : Generic[S, T]
        :pep:`484`-compliant user-defined generic subclassing a single
        parametrized :mod:`typing` type.
    Pep484GenericUnsubscriptedSingle : typing.List
        :pep:`484`-compliant user-defined generic subclassing a single
        unsubscripted :mod:`typing` type.
    Pep484GenericUntypevaredShallowSingle : List[str]
        :pep:`484`-compliant user-defined generic subclassing a single
        unparametrized :mod:`typing` type.
    Pep484GenericUntypevaredDeepSingle : List[List[str]]
        :pep:`484`-compliant user-defined generic subclassing a single
        unparametrized :mod:`typing` type, itself subclassing a single
        unparametrized :mod:`typing` type.
    Pep484GenericUntypevaredMultiple : type
        :pep:`484`-compliant user-defined generic subclassing multiple
        unparametrized :mod:`typing` types *and* a non-:mod:`typing` abstract
        base class (ABC).
    Pep484GenericTypevaredShallowMultiple : type
        :pep:`484`-compliant user-defined generic subclassing multiple directly
        parametrized :mod:`typing` types.
    Pep484GenericTypevaredDeepMultiple : type
        :pep:`484`-compliant user-defined generic subclassing multiple
        indirectly parametrized :mod:`typing` types *and* a non-:mod:`typing`
        abstract base class (ABC).
    Pep484GenericST : Generic[S, T]
        Arbitrary :pep:`484`-compliant generic parametrized by two
        unconstrained type variables.
    Pep484585SequenceU : Sequence[U]
        Arbitrary :pep:`484`- or :pep:`585`-compliant generic sequence
        parametrized by one unconstrained type variable.
    Pep484585GenericSTSequenceU : type
        Arbitrary :pep:`484`- or :pep:`585`-compliant generic list parametrized
        by three unconstrained type variables.
    Pep484585GenericIntTSequenceU : type
        Arbitrary :pep:`484`- or :pep:`585`-compliant generic list parametrized
        by two unconstrained type variables.
    Pep484585GenericUUST : type
        Arbitrary :pep:`484`- or :pep:`585`-compliant generic list parametrized
        by three unconstrained type variables, one of which is repeated twice
        across two different pseudo-superclasses at different hierarchical
        nesting levels.
    Pep585GenericUIntT : Optional[type]
        Either:

        * If the active Python interpreter targets Python >= 3.9 and thus
          behaves sanely with respect to complex subscripted generics, an
          arbitrary :pep:`585`-compliant generic list parametrized by two
          unconstrained type variables, one of which is repeated twice
          across two different pseudo-superclasses at different
          hierarchical nesting levels.
        * Else, :data:`None`.
    '''

    # ....................{ INITIALIZERS                   }....................
    def __init__(self) -> None:
        '''
        Initialize this generics dataclass.
        '''

        # ..................{ IMPORTS                        }..................
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
            List as Pep484List,
            Sequence as Pep484Sequence,
            Tuple as Pep484Tuple,
        )

        # ....................{ PEP 484 ~ single           }....................
        class Pep484GenericTypevaredSingle(Generic[S, T]):
            '''
            :pep:`484`-compliant user-defined generic subclassing a single
            parametrized :mod:`typing` type.
            '''

            pass


        class Pep484GenericUnsubscriptedSingle(Pep484List):
            '''
            :pep:`484`-compliant user-defined generic subclassing a single
            unsubscripted :mod:`typing` type.
            '''

            pass


        class Pep484GenericUntypevaredShallowSingle(Pep484List[str]):
            '''
            :pep:`484`-compliant user-defined generic subclassing a single
            unparametrized :mod:`typing` type.
            '''

            pass


        class Pep484GenericUntypevaredDeepSingle(Pep484List[Pep484List[str]]):
            '''
            :pep:`484`-compliant user-defined generic subclassing a single
            unparametrized :mod:`typing` type, itself subclassing a single
            unparametrized :mod:`typing` type.
            '''

            pass

        # ....................{ PEP 484 ~ multiple         }....................
        class Pep484GenericUntypevaredMultiple(
            CallableABC, Pep484ContextManager[str], Pep484Sequence[str]):
            '''
            :pep:`484`-compliant user-defined generic subclassing multiple
            unparametrized :mod:`typing` types *and* a non-:mod:`typing`
            abstract base class (ABC).
            '''

            # ..................{ INITIALIZERS               }..................
            def __init__(self, sequence: tuple) -> None:
                '''
                Initialize this generic from the passed tuple.
                '''

                assert isinstance(sequence, tuple), (
                    f'{repr(sequence)} not tuple.')
                self._sequence = sequence

            # ..................{ ABCs                       }..................
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


        class Pep484GenericTypevaredShallowMultiple(
            Pep484Iterable[T], Pep484Container[T]):
            '''
            :pep:`484`-compliant user-defined generic subclassing multiple
            directly parametrized :mod:`typing` types.
            '''

            # ..................{ INITIALIZERS               }..................
            def __init__(self, iterable: tuple) -> None:
                '''
                Initialize this generic from the passed tuple.
                '''

                assert isinstance(iterable, tuple), (
                    f'{repr(iterable)} not tuple.')
                self._iterable = iterable

            # ..................{ ABCs                       }..................
            # Define all protocols mandated by ABCs subclassed by this generic.

            def __contains__(self, obj: object) -> bool:
                return obj in self._iterable

            def __iter__(self) -> bool:
                return iter(self._iterable)


        class Pep484GenericTypevaredDeepMultiple(
            SizedABC,
            Pep484Iterable[Pep484Tuple[S, T]],
            Pep484Container[Pep484Tuple[S, T]],
        ):
            '''
            :pep:`484`-compliant user-defined generic subclassing multiple
            indirectly parametrized :mod:`typing` types *and* a
            non-:mod:`typing` abstract base class (ABC).
            '''

            # ..................{ INITIALIZERS               }..................
            def __init__(self, iterable: tuple) -> None:
                '''
                Initialize this generic from the passed tuple.
                '''

                assert isinstance(iterable, tuple), (
                    f'{repr(iterable)} not tuple.')
                self._iterable = iterable

            # ..................{ ABCs                       }..................
            # Define all protocols mandated by ABCs subclassed by this generic.
            def __contains__(self, obj: object) -> bool:
                return obj in self._iterable

            def __iter__(self) -> bool:
                return iter(self._iterable)

            def __len__(self) -> bool:
                return len(self._iterable)

        # ..................{ PEP (484|585)                  }..................
        # Arbitrary PEP-noncompliant non-generic type.
        Nongeneric = Class

        # Arbitrary :pep:`484`-compliant generic parametrized by two
        # unconstrained type variables.
        Pep484GenericST = Pep484GenericTypevaredSingle

        class Pep484585SequenceU(Sequence[U]):
            '''
            Arbitrary :pep:`484`- or :pep:`585`-compliant generic sequence
            parametrized by one unconstrained type variable.
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
            Arbitrary :pep:`484`- or :pep:`585`-compliant generic list
            parametrized by three unconstrained type variables.
            '''

            pass


        class Pep484585GenericIntTSequenceU(Pep484585GenericSTSequenceU[float]):
            '''
            Arbitrary :pep:`484`- or :pep:`585`-compliant generic list
            parametrized by two unconstrained type variables.
            '''

            pass


        class Pep484585GenericUUST(
            # Order is *EXTREMELY* significant. Avoid modifying, please.
            Pep484585SequenceU, Pep484GenericST, List[U]):
            '''
            Arbitrary :pep:`484`- or :pep:`585`-compliant generic list
            parametrized by three unconstrained type variables, one of which is
            repeated twice across two different pseudo-superclasses at different
            hierarchical nesting levels.
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
                Arbitrary :pep:`585`-compliant generic list parametrized by two
                unconstrained type variables, one of which is repeated twice
                across two different pseudo-superclasses at different
                hierarchical nesting levels.
                '''

                pass

            # Classify all of the generics defined above as public instance
            # variables of this dataclass.
            self.Pep585GenericUIntT = Pep585GenericUIntT
        # Else, the active Python interpreter targets Python 3.8 and thus
        # behaves insanely with respect to complex subscripted generics. In this
        # case...
        else:
            # Classify all of the generics defined above as public instance
            # variables of this dataclass whose values are "None".
            self.Pep585GenericUIntT = None

        # ..................{ ATTRS                          }..................
        # Classify all of the generics defined above as public instance
        # variables of this dataclass.
        self.Nongeneric = Class
        self.Pep484GenericTypevaredSingle = Pep484GenericTypevaredSingle
        self.Pep484GenericUnsubscriptedSingle = Pep484GenericUnsubscriptedSingle
        self.Pep484GenericUntypevaredShallowSingle = (
            Pep484GenericUntypevaredShallowSingle)
        self.Pep484GenericUntypevaredDeepSingle = (
            Pep484GenericUntypevaredDeepSingle)
        self.Pep484GenericUntypevaredMultiple = Pep484GenericUntypevaredMultiple
        self.Pep484GenericTypevaredShallowMultiple = (
            Pep484GenericTypevaredShallowMultiple)
        self.Pep484GenericTypevaredDeepMultiple = (
            Pep484GenericTypevaredDeepMultiple)
        self.Pep484GenericST = Pep484GenericST
        self.Pep484585SequenceU = Pep484585SequenceU
        self.Pep484585GenericSTSequenceU = Pep484585GenericSTSequenceU
        self.Pep484585GenericIntTSequenceU = Pep484585GenericIntTSequenceU
        self.Pep484585GenericUUST = Pep484585GenericUUST

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def pep484585_generics() -> _Pep484585Generics:
    '''
    Session-scoped fixture yielding a **generics dataclass** (i.e.,
    object comprising various :pep:`484`- and :pep:`585`-compliant
    :class:`typing.Generic` subclasses of interest to higher-level unit tests).
    '''

    # ..................{ YIELD                              }..................
    # Yield a singleton instance of this generics dataclass.
    yield _Pep484585Generics()
