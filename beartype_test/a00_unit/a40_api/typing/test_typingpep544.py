#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

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

# ....................{ TESTS ~ custom : direct            }....................
def test_typingpep544_protocol_custom_direct() -> None:
    '''
    Test the core operation of the public :class:`beartype.typing.Protocol`
    subclass with respect to user-defined :pep:`544`-compliant protocols
    directly subclassing :class:`beartype.typing.Protocol` under the
    :func:`beartype.beartype` decorator.
    '''

    # Defer test-specific imports.
    from abc import abstractmethod
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
    )
    from beartype.typing import (
        Protocol,
        Tuple,
    )
    from pytest import raises

    # Arbitrary direct protocol.
    class SupportsFish(Protocol):
        @abstractmethod
        def fish(self) -> int:
            pass

    # Arbitrary classes satisfying this protocol *WITHOUT* explicitly
    # subclassing this protocol.
    class OneFish:
        def fish(self) -> int:
            return 1

    class TwoFish:
        def fish(self) -> int:
            return 2

    # Arbitrary classes violating this protocol.
    class RedSnapper:
        def oh(self) -> str:
            return 'snap'

    # Arbitrary @beartype-decorated callable validating both parameters and
    # returns to be instances of arbitrary classes satisfying this protocol.
    @beartype
    def _supports_fish_identity(arg: SupportsFish) -> SupportsFish:
        return arg

    # Assert that instances of classes satisfying this protocol *WITHOUT*
    # subclassing this protocol satisfy @beartype validation as expected.
    assert isinstance(_supports_fish_identity(OneFish()), SupportsFish)
    assert isinstance(_supports_fish_identity(TwoFish()), SupportsFish)

    # Assert that instances of classes violating this protocol violate
    # @beartype validation as expected.
    with raises(BeartypeCallHintParamViolation):
        _supports_fish_identity(RedSnapper())  # type: ignore [arg-type]

    # Arbitrary @beartype-decorated callable guaranteed to *ALWAYS* raise a
    # violation by returning an object that *NEVER* satisfies its type hint.
    @beartype
    def _lies_all_lies(arg: SupportsFish) -> Tuple[str]:
        return (arg.fish(),)  # type: ignore [return-value]

    # Assert this callable raises the expected exception when passed an
    # instance of a class otherwise satisfying this protocol.
    with raises(BeartypeCallHintReturnViolation):
        _lies_all_lies(OneFish())


def test_typingpep544_protocol_custom_direct_typevar() -> None:
    '''
    Test the core operation of the public :class:`beartype.typing.Protocol`
    subclass with respect to user-defined :pep:`544`-compliant protocols
    directly subclassing :class:`beartype.typing.Protocol` and parametrized by
    one or more type variables under the :func:`beartype.beartype` decorator.
    '''

    # Defer test-specific imports.
    from abc import abstractmethod
    from beartype import beartype
    from beartype.typing import (
        Any,
        Protocol,
        TypeVar,
        runtime_checkable,
    )

    # Arbitrary type variable.
    _T_co = TypeVar('_T_co', covariant=True)

    # Arbitrary direct protocol subscripted by this type variable.
    @runtime_checkable
    class SupportsAbsToo(Protocol[_T_co]):
        __slots__: Any = ()

        @abstractmethod
        def __abs__(self) -> _T_co:
            pass

    # Arbitrary @beartype-decorated callable validating a parameter to be an
    # instance of arbitrary classes satisfying this protocol.
    @beartype
    def myabs(arg: SupportsAbsToo[_T_co]) -> _T_co:
        return abs(arg)

    # Assert @beartype wrapped this callable with the expected type-checking.
    assert myabs(-1) == 1

# ....................{ TESTS ~ custom : indirect          }....................
def test_typingpep544_protocol_custom_indirect() -> None:
    '''
    Test the core operation of the public :class:`beartype.typing.Protocol`
    subclass with respect to user-defined :pep:`544`-compliant protocols
    indirectly subclassing :class:`beartype.typing.Protocol` under the
    :func:`beartype.beartype` decorator.
    '''

    # Defer test-specific imports.
    from abc import abstractmethod
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
    )
    from beartype.typing import (
        Protocol,
        Tuple,
    )
    from pytest import raises

    # Arbitrary direct protocol.
    class SupportsFish(Protocol):
        @abstractmethod
        def fish(self) -> int:
            pass

    # Arbitrary indirect protocol subclassing the above direct protocol.
    class SupportsCod(SupportsFish):
        @abstractmethod
        def dear_cod(self) -> str:
            pass

    # Arbitrary classes satisfying this protocol *WITHOUT* explicitly
    # subclassing this protocol.
    class OneCod:
        def fish(self) -> int:
            return 1

        def dear_cod(self) -> str:
            return 'Not bad, cod do better...'

    class TwoCod:
        def fish(self) -> int:
            return 2

        def dear_cod(self) -> str:
            return "I wouldn't be cod dead in that."

    # Arbitrary classes violating this protocol.
    class PacificSnapper:
        # def fish(self) -> int:
        #     return 0xFEEDBEEF

        def dear_cod(self) -> str:
            return 'Cod you pass the butterfish?'

        def berry_punny(self) -> str:
            return 'Had a girlfriend, I lobster. But then I flounder!'

    # Arbitrary @beartype-decorated callable validating both parameters and
    # returns to be instances of arbitrary classes satisfying this protocol.
    @beartype
    def _supports_cod_identity(arg: SupportsCod) -> SupportsCod:
        return arg

    # Assert that instances of classes satisfying this protocol *WITHOUT*
    # subclassing this protocol satisfy @beartype validation as expected.
    assert isinstance(_supports_cod_identity(OneCod()), SupportsCod)
    assert isinstance(_supports_cod_identity(TwoCod()), SupportsCod)

    # Assert that instances of classes violating this protocol violate
    # @beartype validation as expected.
    with raises(BeartypeCallHintParamViolation):
        _supports_cod_identity(PacificSnapper())  # type: ignore [arg-type]

    # Arbitrary @beartype-decorated callable guaranteed to *ALWAYS* raise a
    # violation by returning an object that *NEVER* satisfies its type hint.
    @beartype
    def _lies_all_lies(arg: SupportsCod) -> Tuple[int]:
        return (arg.dear_cod(),)  # type: ignore [return-value]

    # Assert this callable raises the expected exception when passed an
    # instance of a class otherwise satisfying this protocol.
    with raises(BeartypeCallHintReturnViolation):
        _lies_all_lies(OneCod())

# ....................{ TESTS ~ pep 593                    }....................
# If the active Python interpreter targets Python < 3.9 and thus fails to
# support PEP 593, skip all PEP 593-specific tests declared below.

#FIXME: Generalize to support "typing_extensions.Annotated" as well. *sigh*
@skip_if_python_version_less_than('3.9.0')
def test_typingpep544_pep593_integration() -> None:
    '''
    Test the public :class:`beartype.typing.Protocol` subclass when nested
    within a :pep:`593`-compliant .
    '''

    # Defer test-specific imports.
    from abc import abstractmethod
    from beartype import beartype
    from beartype.roar import BeartypeException
    from beartype.typing import (
        Annotated,
        Protocol,
    )
    from beartype.vale import Is
    from pytest import raises

    class SupportsOne(Protocol):
        @abstractmethod
        def one(self) -> int:
            pass

    class TallCoolOne:
        def one(self) -> int:
            return 1

    class FalseOne:
        def one(self) -> int:
            return 0

    class NotEvenOne:
        def two(self) -> str:
            return "two"

    @beartype
    def _there_can_be_only_one(
        n: Annotated[SupportsOne, Is[lambda x: x.one() == 1]],  # type: ignore[name-defined]
    ) -> int:
        val = n.one()
        assert val == 1  # <-- should never fail because it's caught by beartype first
        return val

    _there_can_be_only_one(TallCoolOne())

    with raises(BeartypeException):
        _there_can_be_only_one(FalseOne())

    with raises(BeartypeException):
        _there_can_be_only_one(NotEvenOne())  # type: ignore [arg-type]
