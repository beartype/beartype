#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''Behavioral tests for calls to Beartype-decorated callables.'''


def test_decor_builtin_parameter_names() -> None:
    '''Builtin names remain valid parameter names without bypassing checks.'''
    from beartype import beartype, BeartypeConf
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises, warns

    @beartype
    def accepts(value: int, isinstance=None):
        return value

    assert accepts(1) == 1
    assert accepts(1, isinstance=lambda *args: True) == 1
    with raises(BeartypeCallHintParamViolation):
        accepts('wrong', isinstance=lambda *args: True)

    @beartype
    def container(value: list[int], /, len=None):
        return value

    assert container([1]) == [1]
    with raises(BeartypeCallHintParamViolation):
        container(['wrong'], lambda *args: 0)

    @beartype(conf=BeartypeConf(violation_param_type=UserWarning))
    def warning(value: int, *, str=None, type=None):
        return value

    with warns(UserWarning):
        assert warning('wrong') == 'wrong'


async def test_decor_async_generator_builtin_parameter_names() -> None:
    '''Generator protocol builtins remain callable despite matching names.'''
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from collections.abc import AsyncIterator
    from pytest import raises

    @beartype
    async def values(value: int, *, anext=1, BaseException=2,
                     GeneratorExit=3, StopAsyncIteration=4) -> AsyncIterator[int]:
        yield value

    assert [value async for value in values(1)] == [1]
    with raises(BeartypeCallHintParamViolation):
        assert [value async for value in values('wrong')] == []
    generator = values(2)
    assert await generator.asend(None) == 2
    await generator.aclose()


def test_decor_wrapper_consumes_extra_keyword() -> None:
    '''Decorator wrappers can consume keywords absent from the wrappee.'''
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
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
    with pytest.raises(BeartypeCallHintParamViolation):
        checked(value='wrong', prefix='x')


def test_decor_omitted_and_explicit_default_identity() -> None:
    '''Omission is distinct from explicitly passing the original default.'''
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    positional_default = object()
    flexible_default = object()
    keyword_default = object()
    mutable_default = []

    @beartype
    def accepts(positional: int = positional_default, /,
                flexible: int = flexible_default, *,
                keyword: int = keyword_default, mutable=mutable_default):
        return positional, flexible, keyword, mutable

    omitted = accepts()
    assert omitted[0] is positional_default
    assert omitted[1] is flexible_default
    assert omitted[2] is keyword_default
    assert omitted[3] is mutable_default
    omitted[3].append('same object')
    assert accepts()[3] == ['same object']
    assert accepts(1, 2, keyword=3) == (1, 2, 3, mutable_default)
    for invoke in (
        lambda: accepts(positional_default),
        lambda: accepts(flexible=flexible_default),
        lambda: accepts(keyword=keyword_default),
    ):
        with raises(BeartypeCallHintParamViolation):
            invoke()


def test_decor_fixed_args_and_kwargs_names() -> None:
    '''Fixed and variadic arguments are forwarded under their original names.'''
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    @beartype
    def accepts(args: int, /, kwargs: str = 'x', *values: bytes, **named: float):
        return args, kwargs, values, named

    assert accepts(1) == (1, 'x', (), {})
    assert accepts(1, 'y', b'z', args=2.0) == (1, 'y', (b'z',), {'args': 2.0})
    with raises(BeartypeCallHintParamViolation):
        accepts(1, 'x', bad='bad')


def test_decor_generator_protocol_and_return_value() -> None:
    '''Decorated generators preserve send, throw, close, and return values.'''
    from beartype import beartype
    from collections.abc import Generator
    from inspect import isgeneratorfunction
    from pytest import raises

    closed = []

    def original(value: int = 3, /, *, label: str = 'x'):
        try:
            try:
                received = yield value
            except ValueError:
                received = 'caught'
            yield label, received
            return 7
        finally:
            closed.append(True)

    for hint in (None, Generator[int, object, int]):
        original.__annotations__ = {'value': int, 'label': str}
        if hint is not None:
            original.__annotations__['return'] = hint
        checked = beartype(original)
        assert isgeneratorfunction(checked) is True
        gen = checked(4, label='y')
        assert next(gen) == 4
        assert gen.send('sent') == ('y', 'sent')
        with raises(StopIteration) as stopped:
            next(gen)
        assert stopped.value.value == 7
        gen = checked()
        assert next(gen) == 3
        assert gen.throw(ValueError()) == ('x', 'caught')
        gen.close()
    assert closed == [True, True, True, True]


async def test_decor_async_generator_protocol() -> None:
    '''Async generators preserve asend, athrow, and aclose with either return hint.'''
    from beartype import beartype
    from collections.abc import AsyncGenerator
    from inspect import isasyncgenfunction
    from pytest import raises

    closed = []

    async def original(value: int = 3, /, *, label: str = 'x'):
        try:
            try:
                received = yield value
            except ValueError:
                received = 'caught'
            yield label, received
        finally:
            closed.append(True)

    for hint in (None, AsyncGenerator[int, object]):
        original.__annotations__ = {'value': int, 'label': str}
        if hint is not None:
            original.__annotations__['return'] = hint
        checked = beartype(original)
        assert isasyncgenfunction(checked) is True
        gen = checked(4, label='y')
        assert await gen.__anext__() == 4
        assert await gen.asend('sent') == ('y', 'sent')
        with raises(StopAsyncIteration):
            await gen.__anext__()
        gen = checked()
        assert await gen.__anext__() == 3
        assert await gen.athrow(ValueError()) == ('x', 'caught')
        await gen.aclose()
    assert closed == [True, True, True, True]


def test_decor_live_default_values() -> None:
    '''Replacing default values on the original callable remains observable.'''
    from beartype import beartype

    def original(first: int = 'first', /, second: int = 'second', *,
                 third: int = 'third'):
        return first, second, third

    checked = beartype(original)
    assert checked() == ('first', 'second', 'third')
    original.__defaults__ = ('new first', 'new second')
    original.__kwdefaults__['third'] = 'new third'
    assert checked() == ('new first', 'new second', 'new third')
    assert checked(1, third=3) == (1, 'new second', 3)


def test_decor_missing_argument_messages() -> None:
    '''Missing-argument counts, ordering, and names match native binding.'''
    from beartype import beartype
    from pytest import raises

    def original(first: int, second: int, third: int, *,
                 one: int, two: int, three: int):
        raise AssertionError('Missing arguments must not execute the body.')

    checked = beartype(original)
    for args in ((), (1,), (1, 2), (1, 2, 3)):
        with raises(TypeError) as native:
            original(*args)
        with raises(TypeError) as wrapped:
            checked(*args)
        assert str(wrapped.value) == str(native.value)
    for kwargs in ({'one': 1}, {'one': 1, 'two': 2}):
        with raises(TypeError) as native:
            original(1, 2, 3, **kwargs)
        with raises(TypeError) as wrapped:
            checked(1, 2, 3, **kwargs)
        assert str(wrapped.value) == str(native.value)


def test_decor_bound_method_live_defaults() -> None:
    '''Live default indexes account for the implicitly supplied instance.'''
    from beartype import beartype
    from pytest import raises

    class Methods:
        def accepts(self, value: int, /, *, label: str):
            return value, label

    instance = Methods()
    original = instance.accepts
    checked = beartype(original)
    original.__func__.__defaults__ = (3,)
    original.__func__.__kwdefaults__ = {'label': 'x'}
    assert checked() == original() == (3, 'x')
    original.__func__.__defaults__ = None
    original.__func__.__kwdefaults__ = None
    with raises(TypeError) as native:
        original(label='x')
    with raises(TypeError) as wrapped:
        checked(label='x')
    assert str(wrapped.value) == str(native.value)
    assert checked(4, label='y') == (4, 'y')


async def test_decor_lazy_live_defaults() -> None:
    '''Coroutines and both generator kinds retain live-default behavior.'''
    from beartype import beartype
    from collections.abc import AsyncIterator, Iterator
    from pytest import raises

    async def coroutine(value: int) -> int:
        return value

    def generator(value: int) -> Iterator[int]:
        yield value

    async def async_generator(value: int) -> AsyncIterator[int]:
        yield value

    checked_coroutine = beartype(coroutine)
    checked_generator = beartype(generator)
    checked_async_generator = beartype(async_generator)
    for func in (coroutine, generator, async_generator):
        func.__defaults__ = (3,)
    assert await checked_coroutine() == 3
    assert list(checked_generator()) == [3]
    assert [value async for value in checked_async_generator()] == [3]
    for func in (coroutine, generator, async_generator):
        func.__defaults__ = None
    with raises(TypeError):
        await checked_coroutine()
    with raises(TypeError):
        next(checked_generator())
    with raises(TypeError):
        await checked_async_generator().__anext__()
