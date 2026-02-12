#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`544` **optimization layer** unit tests.

This submodule unit tests both the public *and* private API of the private
:mod:`beartype.typing._typingpep544` subpackage for sanity.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_typingpep544_metaclass() -> None:
    '''
    Test the private
    :class:`beartype.typing._typingpep544._CachingProtocolMeta` metaclass.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from abc import abstractmethod
    from beartype.typing import (
        Any,
        Protocol,
        TypeVar,
        runtime_checkable,
    )
    from beartype.typing._typingpep544 import _CachingProtocolMeta

    # ....................{ LOCALS                         }....................
    # Arbitrary type variable.
    _T_co = TypeVar('_T_co', covariant=True)

    # ....................{ CLASSES                        }....................
    # Can we really have it all?!
    @runtime_checkable  # <-- unnecessary at runtime, but Mypy is confused without it
    class SupportsRoundFromScratch(Protocol[_T_co]):
        __slots__: Any = ()
        @abstractmethod
        def __round__(self, ndigits: int = 0) -> _T_co:
            pass

    supports_round: SupportsRoundFromScratch = 0

    # ....................{ PASS                           }....................
    assert isinstance(supports_round, SupportsRoundFromScratch)
    assert issubclass(type(SupportsRoundFromScratch), _CachingProtocolMeta)


def test_typingpep544_superclass() -> None:
    '''
    Test the public :class:`beartype.typing.Protocol` superclass.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.typing import (
        Protocol as ProtocolFast,
        TypeVar,
    )
    from beartype.typing._typingpep544 import _ProtocolSlow as ProtocolSlow
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Arbitrary type variable.
    _T_co = TypeVar('_T_co', covariant=True)

    # Representations of protocols parametrized by one or more type variables.
    fast_repr = repr(ProtocolFast[_T_co])
    slow_repr = repr(ProtocolSlow[_T_co])

    # ....................{ PASS                           }....................
    # Assert that our caching protocol superclass memoizes subscriptions.
    assert ProtocolFast.__module__ == 'beartype.typing'
    assert ProtocolFast[_T_co] is ProtocolFast[_T_co]

    # Assert that the representation of a caching protocol is prefixed by the
    # expected prefix.
    assert fast_repr.startswith('beartype.typing.Protocol[')

    # Assert that these representation are suffixed by the same "["- and "]
    # "-delimited strings.
    fast_repr_suffix = fast_repr[fast_repr.rindex('['):]
    slow_repr_suffix = slow_repr[slow_repr.rindex('['):]
    assert fast_repr_suffix == slow_repr_suffix

    # ....................{ FAIL                           }....................
    # Assert that attempting to directly subscript the caching protocol
    # superclass by a non-type variable raises the expected exception.
    with raises(TypeError):
        ProtocolFast[str]


def test_typingpep544_subclass() -> None:
    '''
    Test expected behaviour of user-defined subclasses of the public
    :class:`beartype.typing.Protocol` superclass.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from abc import abstractmethod
    from beartype.typing import (
        AnyStr,
        Protocol,
        runtime_checkable
    )
    from pytest import raises

    # ....................{ CLASSES                        }....................
    class SupportsFeebleDreams(Protocol[AnyStr]):
        '''
        Arbitrary protocol directly subclassing the protocol superclass
        subscripted by one or more type variables, exercising subtle edge cases.
        '''

        @abstractmethod
        def torpor_of_the_year(self) -> AnyStr:
            pass


    class SupportsHiddenBuds(SupportsFeebleDreams[str]):
        '''
        Arbitrary protocol directly subclassing the above protocol superclass
        subscripted by one or more non-type variables satisfying the type
        variables subscripting that superclass, exercising subtle edge cases.
        '''

        @abstractmethod
        def dreamless_sleep(self) -> str:
            pass

    # ....................{ PASS                           }....................
    # Assert that optionally decorating protocols by the standard
    # @typing.runtime_checkable() decorator reduces to a noop.
    assert runtime_checkable(SupportsFeebleDreams) is SupportsFeebleDreams

    # Assert that a caching protocol subclass also memoizes subscriptions.
    assert SupportsFeebleDreams[str] is SupportsFeebleDreams[str]

    # Assert that optionally decorating abstract protocols by the standard
    # @typing.runtime_checkable() decorator reduces to a noop.
    assert runtime_checkable(SupportsFeebleDreams) is SupportsFeebleDreams

    # ....................{ FAIL                           }....................
    # Assert that attempting to decorate concrete protocol subclasses by
    # the same decorator raises the expected exception.
    with raises(TypeError):
        runtime_checkable(SupportsHiddenBuds)


def test_typingpep544_protocols_typing() -> None:
    '''
    Test the public retinue of ``beartype.typing.Supports*`` protocols with
    respect to both caching optimizations implemented by the public
    :class:`beartype.typing.Protocol` subclass *and* the private
    :class:`beartype.typing._typingpep544._CachingProtocolMeta` metaclass.
    '''

    # Defer test-specific imports.
    from decimal import Decimal
    from fractions import Fraction
    from beartype.typing import (
        SupportsAbs,
        SupportsBytes,
        SupportsComplex,
        SupportsFloat,
        SupportsIndex,
        SupportsInt,
        SupportsRound,
    )
    from beartype.typing._typingpep544 import _CachingProtocolMeta

    # Assert *ALL* standard protocols share the expected metaclass.
    for supports_t in (
        SupportsAbs,
        SupportsBytes,
        SupportsComplex,
        SupportsFloat,
        SupportsIndex,
        SupportsInt,
        SupportsRound,
    ):
        assert issubclass(type(supports_t), _CachingProtocolMeta)
        assert supports_t.__module__ == 'beartype.typing'

    def _assert_isinstance(*types: type, target_t: type) -> None:

        assert issubclass(
            target_t.__class__, _CachingProtocolMeta
        ), (
            f'{repr(target_t.__class__)} metaclass not '
            f'{repr(_CachingProtocolMeta)}.'
        )

        for t in types:
            v = t(0)
            assert isinstance(v, target_t), (
                f'{repr(t)} not instance of {repr(target_t)}.')


    # supports_abs: SupportsAbs = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=SupportsAbs)

    # supports_complex: SupportsComplex = Fraction(0, 1)
    _assert_isinstance(
        Decimal, Fraction, target_t=SupportsComplex)

    # supports_float: SupportsFloat = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=SupportsFloat)

    # supports_int: SupportsInt = 0
    _assert_isinstance(
        int, float, bool, target_t=SupportsInt)

    # supports_index: SupportsIndex = 0
    _assert_isinstance(
        int, bool, target_t=SupportsIndex)

    # supports_round: SupportsRound = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=SupportsRound)
