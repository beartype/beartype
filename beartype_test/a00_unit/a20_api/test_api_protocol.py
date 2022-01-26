# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.


def test_caching_protocol_as_drop_in_replacement() -> None:
    import pytest
    from beartype import _protocol

    if not hasattr(_protocol, "_CachingProtocolMeta"):
        pytest.skip("_CachingProtocolMeta not available")

    from abc import abstractmethod

    from beartype import typing

    _T_co = typing.TypeVar("_T_co", covariant=True)

    # Can we really have it all?!
    @typing.runtime_checkable  # <-- unnecessary at runtime, but Mypy is confused without it
    class SupportsRoundFromScratch(
        typing.Protocol[_T_co],
    ):
        __slots__: typing.Union[str, typing.Iterable[str]] = ()

        @abstractmethod
        def __round__(self, ndigits: int = 0) -> _T_co:
            pass

    supports_round: SupportsRoundFromScratch = 0
    assert isinstance(supports_round, SupportsRoundFromScratch)
    assert issubclass(type(SupportsRoundFromScratch), _protocol._CachingProtocolMeta)


def test_caching_protocol_validation() -> None:
    import pytest
    from beartype import _protocol

    if not hasattr(_protocol, "_CachingProtocolMeta"):
        pytest.skip("_CachingProtocolMeta not available")

    from abc import abstractmethod

    from beartype import beartype, roar, typing

    class SupportsFish(typing.Protocol):
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

    with pytest.raises(roar.BeartypeException):
        _real_like_identity(RedSnapper())  # type: ignore [arg-type]

    @beartype
    def _lies_all_lies(arg: SupportsFish) -> typing.Tuple[str]:
        return (arg.fish(),)  # type: ignore [return-value]

    with pytest.raises(roar.BeartypeException):
        _lies_all_lies(OneFish())


def test_protocols_in_annotation_validators() -> None:
    import pytest
    from beartype import _protocol

    if not hasattr(_protocol, "_CachingProtocolMeta"):
        pytest.skip("_CachingProtocolMeta not available")

    from abc import abstractmethod

    from beartype import beartype, roar, typing, vale
    from beartype.typing import Annotated  # type: ignore[attr-defined]

    class SupportsOne(typing.Protocol):
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
        n: Annotated[SupportsOne, vale.Is[lambda x: x.one() == 1]],
    ) -> int:
        val = n.one()
        assert val == 1  # <-- should never fail because it's caught by beartype first
        return val

    _there_can_be_only_one(TallCoolOne())

    with pytest.raises(roar.BeartypeException):
        _there_can_be_only_one(FalseOne())

    with pytest.raises(roar.BeartypeException):
        _there_can_be_only_one(NotEvenOne())  # type: ignore [arg-type]


def test_caching_supports_protocols() -> None:
    import pytest
    from beartype import _protocol

    if not hasattr(_protocol, "_CachingProtocolMeta"):
        pytest.skip("_CachingProtocolMeta not available")

    from decimal import Decimal
    from fractions import Fraction

    from beartype import typing

    for supports_t in (
        typing.SupportsAbs,
        typing.SupportsBytes,
        typing.SupportsComplex,
        typing.SupportsFloat,
        typing.SupportsIndex,
        typing.SupportsInt,
        typing.SupportsRound,
    ):
        assert issubclass(type(supports_t), _protocol._CachingProtocolMeta)

    def _assert_isinstance(*types: type, target_t: type) -> None:
        assert issubclass(
            target_t.__class__, _protocol._CachingProtocolMeta
        ), f"{target_t.__class__} is not subclass of {_protocol._CachingProtocolMeta}"

        for t in types:
            v = t(0)
            assert isinstance(v, target_t), f"{t!r}, {target_t!r}"

    supports_abs: typing.SupportsAbs = 0
    _assert_isinstance(int, float, bool, Decimal, Fraction, target_t=typing.SupportsAbs)

    supports_complex: typing.SupportsComplex = Fraction(0, 1)
    _assert_isinstance(Decimal, Fraction, target_t=typing.SupportsComplex)

    supports_float: typing.SupportsFloat = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=typing.SupportsFloat
    )

    supports_int: typing.SupportsInt = 0
    _assert_isinstance(int, float, bool, target_t=typing.SupportsInt)

    supports_index: typing.SupportsIndex = 0
    _assert_isinstance(int, bool, target_t=typing.SupportsIndex)

    supports_round: typing.SupportsRound = 0
    _assert_isinstance(
        int, float, bool, Decimal, Fraction, target_t=typing.SupportsRound
    )
