#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`544` **optimization layer unit tests.**

This submodule unit tests both the public *and* private API of the private
:mod:`beartype.typing._typingpep544` subpackage for sanity.
'''

from beartype._util.py.utilpyversion import IS_PYTHON_3_7
# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import skip
from beartype.typing._typingpep544 import _import_typing_extensions
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_AT_LEAST_3_8,
)
from beartype_test.util.mark.pytskip import (
    skip_if_python_version_less_than,
    skip_unless_module,
)

# ....................{ TESTS                             }....................
# If the active Python interpreter targets Python < 3.7 and thus fails to
# support PEP 544, skip all tests declared below. For 3.7 in particular, each
# each test also skips itself if it is unable to load the typing_extensions
# module.

@skip_if_python_version_less_than('3.7.0')
def test_typingpep544_metaclass() -> None:
    '''
    Test the private
    :class:`beartype.typing._typingpep544._CachingProtocolMeta` metaclass.
    '''
    if IS_PYTHON_3_7 and _import_typing_extensions() is None:
        skip('typing-extensions required to support Protocols in Python 3.7')

    # Defer heavyweight imports.
    from abc import abstractmethod
    from beartype.typing import (
        Iterable,
        Protocol,
        TypeVar,
        Union,
        runtime_checkable,
    )
    from beartype.typing._typingpep544 import _CachingProtocolMeta

    # Arbitrary type variable.
    _T_co = TypeVar('_T_co', covariant=True)

    # Can we really have it all?!
    @runtime_checkable  # <-- unnecessary at runtime, but Mypy is confused without it
    class SupportsRoundFromScratch(Protocol[_T_co]):
        __slots__: Union[str, Iterable[str]] = ()
        @abstractmethod
        def __round__(self, ndigits: int = 0) -> _T_co:
            pass

    supports_round: SupportsRoundFromScratch = 0
    assert isinstance(supports_round, SupportsRoundFromScratch)
    assert issubclass(type(SupportsRoundFromScratch), _CachingProtocolMeta)


@skip_if_python_version_less_than('3.7.0')
def test_typingpep544_superclass() -> None:
    '''
    Test the public
    :class:`beartype.typing.Protocol` superclass.
    '''
    if IS_PYTHON_3_7:
        if _import_typing_extensions() is None:
            skip('typing-extensions required to support Protocols in Python 3.7')

        from typing_extensions import Protocol as ProtocolSlow
    else:
        from typing import Protocol as ProtocolSlow

    # Defer heavyweight imports.
    from beartype.typing import (
        Protocol as ProtocolFast,
        TypeVar,
    )
    from pytest import raises

    # Arbitrary type variable.
    _T_co = TypeVar('_T_co', covariant=True)

    # Assert that our caching protocol superclass memoizes subscriptions.
    assert ProtocolFast.__module__ == 'beartype.typing'
    assert ProtocolFast[_T_co] is ProtocolFast[_T_co]

    # Assert that the representation of a caching protocol parametrized by one
    # or more type variables contains the representation of a non-caching
    # protocol parametrized by those same variables.
    slow_repr = repr(ProtocolSlow[_T_co])
    slow_protocol_repr = slow_repr[slow_repr.rindex('.') :]
    fast_repr = repr(ProtocolFast[_T_co])
    fast_protocol_repr = fast_repr[fast_repr.rindex('.') :]

    assert fast_repr.startswith('beartype.typing.Protocol[')
    assert slow_protocol_repr == fast_protocol_repr

    # Assert that attempting to directly subscript the caching protocol
    # superclass by a non-type variable raises the expected exception.
    with raises(TypeError):
        ProtocolFast[str]


@skip_if_python_version_less_than('3.7.0')
def test_typingpep544_subclass() -> None:
    '''
    Test expected behaviour of user-defined subclasses of the public
    :class:`beartype.typing.Protocol` superclass.
    '''
    if IS_PYTHON_3_7 and _import_typing_extensions() is None:
        skip('typing-extensions required to support Protocols in Python 3.7')

    # Defer heavyweight imports.
    from abc import abstractmethod
    from beartype.typing import (
        AnyStr,
        Protocol,
        runtime_checkable
    )

    # Arbitrary protocol directly subclassing the protocol superclass
    # subscripted by one or more type variables, exercising subtle edge cases.
    class SupportsFeebleDreams(Protocol[AnyStr]):
        @abstractmethod
        def torpor_of_the_year(self) -> AnyStr:
            pass

    # Arbitrary protocol directly subclassing the above protocol superclass
    # subscripted by one or more non-type variables satisfying the type
    # variables subscripting that superclass, exercising subtle edge cases.
    class SupportsHiddenBuds(SupportsFeebleDreams[str]):
        @abstractmethod
        def dreamless_sleep(self) -> str:
            pass

    # Assert that a caching protocol subclass also memoizes subscriptions.
    assert SupportsFeebleDreams[str] is SupportsFeebleDreams[str]

    # Assert that optionally decorating protocols by the standard
    # @typing.runtime_checkable() decorator reduces to a noop.
    assert runtime_checkable(SupportsFeebleDreams) is SupportsFeebleDreams
    assert runtime_checkable(SupportsHiddenBuds) is SupportsHiddenBuds


@skip_if_python_version_less_than('3.7.0')
def test_typingpep544_protocols_typing() -> None:
    '''
    Test the public retinue of ``beartype.typing.Supports*`` protocols with
    respect to both caching optimizations implemented by the public
    :class:`beartype.typing.Protocol` subclass *and* the private
    :class:`beartype.typing._typingpep544._CachingProtocolMeta` metaclass.
    '''
    if IS_PYTHON_3_7 and _import_typing_extensions() is None:
        skip('typing-extensions required to support Protocols in Python 3.7')

    # Defer heavyweight imports.
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

# ....................{ TESTS ~ custom                    }....................
@skip_if_python_version_less_than('3.7.0')
def test_typingpep544_protocol_custom_direct() -> None:
    '''
    Test the core operation of the public :class:`beartype.typing.Protocol`
    subclass with respect to user-defined :pep:`544`-compliant protocols
    directly subclassing :class:`beartype.typing.Protocol` under the
    :func:`beartype.beartype` decorator.
    '''
    if IS_PYTHON_3_7 and _import_typing_extensions() is None:
        skip('typing-extensions required to support Protocols in Python 3.7')

    # Defer heavyweight imports.
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
    def _real_like_identity(arg: SupportsFish) -> SupportsFish:
        return arg

    # Assert that instances of classes satisfying this protocol *WITHOUT*
    # subclassing this protocol satisfy @beartype validation as expected.
    assert isinstance(_real_like_identity(OneFish()), SupportsFish)
    assert isinstance(_real_like_identity(TwoFish()), SupportsFish)

    # Assert that instances of classes violating this protocol violate
    # @beartype validation as expected.
    with raises(BeartypeCallHintParamViolation):
        _real_like_identity(RedSnapper())  # type: ignore [arg-type]

    # Arbitrary @beartype-decorated callable guaranteed to *ALWAYS* raise a
    # violation by returning an object that *NEVER* satisfies its type hint.
    @beartype
    def _lies_all_lies(arg: SupportsFish) -> Tuple[str]:
        return (arg.fish(),)  # type: ignore [return-value]

    # Assert this callable raises the expected exception when passed an
    # instance of a class otherwise satisfying this protocol.
    with raises(BeartypeCallHintReturnViolation):
        _lies_all_lies(OneFish())


@skip_if_python_version_less_than('3.7.0')
def test_typingpep544_protocol_custom_indirect() -> None:
    '''
    Test the core operation of the public :class:`beartype.typing.Protocol`
    subclass with respect to user-defined :pep:`544`-compliant protocols
    indirectly subclassing :class:`beartype.typing.Protocol` under the
    :func:`beartype.beartype` decorator.
    '''
    if IS_PYTHON_3_7 and _import_typing_extensions() is None:
        skip('typing-extensions required to support Protocols in Python 3.7')

    # Defer heavyweight imports.
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
    def _real_like_identity(arg: SupportsCod) -> SupportsCod:
        return arg

    # Assert that instances of classes satisfying this protocol *WITHOUT*
    # subclassing this protocol satisfy @beartype validation as expected.
    assert isinstance(_real_like_identity(OneCod()), SupportsCod)
    assert isinstance(_real_like_identity(TwoCod()), SupportsCod)

    # Assert that instances of classes violating this protocol violate
    # @beartype validation as expected.
    with raises(BeartypeCallHintParamViolation):
        _real_like_identity(PacificSnapper())  # type: ignore [arg-type]

    # Arbitrary @beartype-decorated callable guaranteed to *ALWAYS* raise a
    # violation by returning an object that *NEVER* satisfies its type hint.
    @beartype
    def _lies_all_lies(arg: SupportsCod) -> Tuple[int]:
        return (arg.dear_cod(),)  # type: ignore [return-value]

    # Assert this callable raises the expected exception when passed an
    # instance of a class otherwise satisfying this protocol.
    with raises(BeartypeCallHintReturnViolation):
        _lies_all_lies(OneCod())

# ....................{ TESTS ~ pep 593                   }....................
# If the active Python interpreter targets Python < 3.9 and thus fails to
# support PEP 593, skip all PEP 593-specific tests declared below.

#FIXME: Generalize to support "typing_extensions.Annotated" as well. *sigh*
@skip_if_python_version_less_than('3.9.0')
def test_typingpep544_pep593_integration() -> None:
    '''
    Test the public :class:`beartype.typing.Protocol` subclass when nested
    within a :pep:`593`-compliant .
    '''

    # Defer heavyweight imports.
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

# ....................{ TESTS ~ internal                   }....................
@skip_if_python_version_less_than('3.7.0')
def test_import_typing_extensions():
    if IS_PYTHON_AT_LEAST_3_7:
        skip_unless_module('typing_extensions')

        import os
        from unittest import mock
        from beartype.typing._typingpep544 import _import_typing_extensions

        with mock.patch.dict(os.environ, {'_BEARTYPE_PY_3_7_EXCLUDE_TYPING_EXTENSIONS': '1'}):
            assert _import_typing_extensions() is None

        with mock.patch.dict(os.environ, {'_BEARTYPE_PY_3_7_EXCLUDE_TYPING_EXTENSIONS': ''}):
            te = _import_typing_extensions()
            assert te is not None
            assert hasattr(te, 'Protocol')
            assert hasattr(te, 'runtime_checkable')
