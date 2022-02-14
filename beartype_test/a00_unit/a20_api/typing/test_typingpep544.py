#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`544` **optimization layer unit tests.**

This submodule unit tests both the public *and* private API of the private
:mod:`beartype.typing._typingpep544` subpackage for sanity.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_typingpep544_metaclass() -> None:
    '''
    Test the private
    :class:`beartype.typing._typingpep544._CachingProtocolMeta` metaclass.
    '''

    # Defer heavyweight imports.
    from beartype.typing import _typingpep544
    from pytest import skip

    # Skip this test if inapplicable.
    if not hasattr(_typingpep544, '_CachingProtocolMeta'):
        skip(
            '"beartype.typing._typingpep544._CachingProtocolMeta" metaclass '
            'undefined.'
        )

    # Defer version-specific imports.
    from abc import abstractmethod
    from beartype.typing import (
        Iterable,
        Protocol,
        TypeVar,
        Union,
        runtime_checkable,
    )

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
    assert issubclass(
        type(SupportsRoundFromScratch),
        _typingpep544._CachingProtocolMeta,
    )


def test_typingpep544_subclass() -> None:
    '''
    Test the core operation of the public :class:`beartype.typing.Protocol`
    subclass with respect to :pep:`544`-compliant protocols under the
    :func:`beartype.beartype` decorator.
    '''

    # Defer heavyweight imports.
    from beartype.typing import _typingpep544
    from pytest import skip

    # Skip this test if inapplicable.
    if not hasattr(_typingpep544, '_CachingProtocolMeta'):
        skip(
            '"beartype.typing._typingpep544._CachingProtocolMeta" metaclass '
            'undefined.'
        )

    # Defer version-specific imports.
    from abc import abstractmethod
    from beartype import beartype
    from beartype.roar import BeartypeException
    from beartype.typing import (
        Protocol,
        Tuple,
    )
    from pytest import raises

    class SupportsFish(Protocol):
        @abstractmethod
        def fish(self) -> int:
            pass

    class OneFish:
        def fish(self) -> int:
            return 1

    class TwoFish:
        def fish(self) -> int:
            return 2

    class RedSnapper:
        def oh(self) -> str:
            return "snap"

    @beartype
    def _real_like_identity(arg: SupportsFish) -> SupportsFish:
        return arg

    _real_like_identity(OneFish())
    _real_like_identity(TwoFish())

    with raises(BeartypeException):
        _real_like_identity(RedSnapper())  # type: ignore [arg-type]

    @beartype
    def _lies_all_lies(arg: SupportsFish) -> Tuple[str]:
        return (arg.fish(),)  # type: ignore [return-value]

    with raises(BeartypeException):
        _lies_all_lies(OneFish())



def test_typingpep544_subclass_caching() -> None:
    '''
    Test various caching optimizations implemented by the public
    :class:`beartype.typing.Protocol` subclass and user-defined subclasses of
    that subclass.
    '''

    # Defer heavyweight imports.
    from beartype.typing import _typingpep544
    from pytest import skip

    # Skip this test if inapplicable.
    if not hasattr(_typingpep544, '_CachingProtocolMeta'):
        skip(
            '"beartype.typing._typingpep544._CachingProtocolMeta" metaclass '
            'undefined.'
        )

    # Defer version-specific imports.
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

    supports_abs: SupportsAbs = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=SupportsAbs)

    supports_complex: SupportsComplex = Fraction(0, 1)
    _assert_isinstance(
        Decimal, Fraction, target_t=SupportsComplex)

    supports_float: SupportsFloat = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=SupportsFloat)

    supports_int: SupportsInt = 0
    _assert_isinstance(
        int, float, bool, target_t=SupportsInt)

    supports_index: SupportsIndex = 0
    _assert_isinstance(
        int, bool, target_t=SupportsIndex)

    supports_round: SupportsRound = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=SupportsRound)


def test_typingpep544_pep593_integration() -> None:
    '''
    Test the public :class:`beartype.typing.Protocol` subclass when nested
    within a :pep:`593`-compliant .
    '''

    # Defer heavyweight imports.
    from beartype import typing
    from beartype.typing import _typingpep544
    from pytest import skip

    #FIXME: Please generalize to support "typing_extensions.Annotated", too. :p
    # Skip this test if inapplicable.
    if not hasattr(typing, 'Annotated'):
        skip('Python < 3.9.0.')
    if not hasattr(_typingpep544, '_CachingProtocolMeta'):
        skip(
            '"beartype.typing._typingpep544._CachingProtocolMeta" metaclass '
            'undefined.'
        )

    # Defer version-specific imports.
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
