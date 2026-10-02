#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''Required keyword-only wrapper specialization tests.'''

def test_decor_required_keyword_signature_and_validation() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from inspect import CO_VARARGS, CO_VARKEYWORDS
    import pytest

    seen = []

    @beartype
    def render(*, value: int, label: str) -> str:
        seen.append((value, label))
        return label * value

    assert render(value=2, label='x') == 'xx'
    assert seen == [(2, 'x')]
    assert render.__code__.co_flags & (CO_VARARGS | CO_VARKEYWORDS) == 0
    with pytest.raises(BeartypeCallHintParamViolation):
        render(value='wrong', label='x')
    assert seen == [(2, 'x')]
    for invoke in (
        lambda: render(label='x'),
        lambda: render(value=2),
        lambda: render(value=2, label='x', extra=1),
        lambda: render(2, label='x'),
        # Native binding errors precede type checking of malformed calls.
        lambda: render(value='wrong'),
        lambda: render(value='wrong', label='x', extra=1),
    ):
        with pytest.raises(TypeError):
            invoke()
    assert seen == [(2, 'x')]


def test_decor_required_keyword_return_violation() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintReturnViolation
    import pytest

    @beartype
    def bad_return(*, value: int) -> str:
        return value

    with pytest.raises(BeartypeCallHintReturnViolation):
        bad_return(value=1)


def test_decor_required_keyword_container_validation() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    import pytest

    @beartype
    def accept(*, values: list[tuple[str, str]]) -> str:
        return str(values)

    assert accept(values=[('a', 'b')]) == "[('a', 'b')]"
    with pytest.raises(BeartypeCallHintParamViolation):
        accept(values=[('a', 1)])


def test_decor_required_keyword_unannotated_parameter_is_forwarded() -> None:
    from beartype import beartype

    @beartype
    def render(*, value: int, prefix) -> str:
        return f'{prefix}{value}'

    assert render(value=3, prefix='x') == 'x3'


def test_decor_required_keyword_required_object_parameter_remains_ignorable() -> None:
    from beartype import beartype

    @beartype
    def render(*, value: object) -> str:
        return str(value)

    assert render(value=123) == '123'


def test_decor_required_keyword_default_falls_back_without_checking_omitted_default() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from inspect import CO_VARKEYWORDS
    import pytest

    @beartype
    def render(*, value: int = 'default') -> str:
        return str(value)

    assert render() == 'default'
    assert render(value=3) == '3'
    assert render.__code__.co_flags & CO_VARKEYWORDS == CO_VARKEYWORDS
    with pytest.raises(BeartypeCallHintParamViolation):
        render(value='wrong')


def test_decor_required_keyword_variadic_keyword_fallback() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    import pytest

    @beartype
    def total(*, value: int, **extra: int) -> int:
        return value + sum(extra.values())

    assert total(value=1, a=2, b=3) == 6
    with pytest.raises(BeartypeCallHintParamViolation):
        total(value=1, a='wrong')


def test_decor_required_keyword_transparent_wrapper_fallback() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from inspect import CO_VARKEYWORDS
    from functools import wraps
    import pytest

    def render(*, value: int) -> str:
        return str(value)

    @wraps(render)
    def interceptor(*args, **kwargs):
        prefix = kwargs.pop('prefix', '')
        return prefix + render(*args, **kwargs)

    checked = beartype(interceptor)
    assert checked(value=3, prefix='x') == 'x3'
    assert checked.__code__.co_flags & CO_VARKEYWORDS == CO_VARKEYWORDS
    with pytest.raises(BeartypeCallHintParamViolation):
        checked(value='wrong', prefix='x')


async def test_decor_required_keyword_async_fallback() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from inspect import CO_VARKEYWORDS
    import pytest

    @beartype
    async def render(*, value: int) -> str:
        return str(value)

    assert await render(value=3) == '3'
    with pytest.raises(BeartypeCallHintParamViolation):
        await render(value='wrong')
    assert render.__code__.co_flags & CO_VARKEYWORDS == CO_VARKEYWORDS


def test_decor_required_keyword_generator_fallback() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    import pytest

    @beartype
    def values(*, value: int):
        yield value

    assert list(values(value=3)) == [3]
    with pytest.raises(BeartypeCallHintParamViolation):
        list(values(value='wrong'))


def test_decor_required_keyword_positional_and_method_fallback() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    import pytest

    @beartype
    def render(value: int, /, *, label: str) -> str:
        return label * value

    @beartype
    class Renderer:
        def render(self, *, value: int) -> str:
            return str(value)

    assert render(2, label='x') == 'xx'
    assert Renderer().render(value=3) == '3'
    with pytest.raises(BeartypeCallHintParamViolation):
        Renderer().render(value='wrong')


def test_decor_required_keyword_unchecked_return_and_metadata() -> None:
    '''Explicit forwarding also supports unannotated returns and unusual names.'''
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from inspect import CO_VARARGS, CO_VARKEYWORDS
    from pytest import raises

    @beartype
    def render(*, args: int, kwargs: str):
        return args, kwargs

    assert render(args=1, kwargs='x') == (1, 'x')
    assert render.__annotations__ == {'args': int, 'kwargs': str}
    assert render.__code__.co_flags & (CO_VARARGS | CO_VARKEYWORDS) == 0
    with raises(BeartypeCallHintParamViolation):
        render(args='wrong', kwargs='x')


def test_decor_required_keyword_noreturn() -> None:
    '''Both successful and unsuccessful NoReturn calls forward named arguments.'''
    from beartype import beartype
    from beartype.roar import BeartypeCallHintReturnViolation
    from typing import NoReturn
    from pytest import raises

    @beartype
    def raises_normally(*, value: int) -> NoReturn:
        raise RuntimeError(str(value))

    @beartype
    def returns_illegally(*, value: int) -> NoReturn:
        return value

    with raises(RuntimeError, match='3'):
        raises_normally(value=3)
    with raises(BeartypeCallHintReturnViolation):
        returns_illegally(value=3)


def test_decor_required_keyword_warning_policy() -> None:
    '''Type violations configured as warnings remain warnings.'''
    from beartype import beartype, BeartypeConf
    from pytest import warns

    @beartype(conf=BeartypeConf(violation_param_type=UserWarning))
    def accepts_after_warning(*, value: int) -> str:
        return str(value)

    @beartype(conf=BeartypeConf(violation_return_type=UserWarning))
    def returns_after_warning(*, value: int) -> str:
        return value

    with warns(UserWarning):
        assert accepts_after_warning(value='wrong') == 'wrong'
    with warns(UserWarning):
        assert returns_after_warning(value=3) == 3


async def test_decor_required_keyword_async_generator_fallback() -> None:
    '''Asynchronous generator factories keep their generic wrapper.'''
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from inspect import CO_VARKEYWORDS
    from collections.abc import AsyncIterator
    from pytest import raises

    @beartype
    async def values(*, value: int) -> AsyncIterator[int]:
        yield value

    async def consume(value):
        return [item async for item in values(value=value)]

    assert await consume(3) == [3]
    assert values.__code__.co_flags & CO_VARKEYWORDS == CO_VARKEYWORDS
    with raises(BeartypeCallHintParamViolation):
        await consume('wrong')


def test_decor_required_keyword_reserved_unannotated_fallback() -> None:
    '''Unannotated reserved names retain their existing generic behavior.'''
    from beartype import beartype
    from inspect import CO_VARKEYWORDS

    @beartype
    def render(*, value: int, __beartype_private) -> str:
        return str(value) + __beartype_private

    assert render(value=3, __beartype_private='x') == '3x'
    assert render.__code__.co_flags & CO_VARKEYWORDS == CO_VARKEYWORDS
