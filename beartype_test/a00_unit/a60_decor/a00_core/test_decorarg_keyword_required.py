#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''Callable-specific wrapper signature and forwarding tests.'''

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


def test_decor_keyword_default_is_explicit_without_checking_omitted_default() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from inspect import CO_VARKEYWORDS
    import pytest

    @beartype
    def render(*, value: int = 'default') -> str:
        return str(value)

    assert render() == 'default'
    assert render(value=3) == '3'
    assert render.__code__.co_flags & CO_VARKEYWORDS == 0
    with pytest.raises(BeartypeCallHintParamViolation):
        render(value='wrong')


def test_decor_keyword_variadic_keyword_is_explicit() -> None:
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


async def test_decor_required_keyword_async_is_explicit() -> None:
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
    assert render.__code__.co_flags & CO_VARKEYWORDS == 0


def test_decor_required_keyword_generator_is_explicit() -> None:
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    import pytest

    @beartype
    def values(*, value: int):
        yield value

    assert list(values(value=3)) == [3]
    with pytest.raises(BeartypeCallHintParamViolation):
        list(values(value='wrong'))


def test_decor_positional_and_method_are_explicit() -> None:
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


async def test_decor_required_keyword_async_generator_is_explicit() -> None:
    '''Asynchronous generator factories preserve their native factory kind.'''
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
    assert values.__code__.co_flags & CO_VARKEYWORDS == 0
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


def test_decor_explicit_all_parameter_kinds() -> None:
    '''Every kind binds and forwards correctly, with arbitrary variadic names.'''
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from inspect import signature
    from pytest import raises

    def original(first: int, /, second: str = 'x', *rest: bytes,
                 required: float, optional: bool = False, **extra: complex):
        return first, second, rest, required, optional, extra

    checked = beartype(original)
    assert signature(checked) == signature(original)
    assert checked(1, required=2.0) == (1, 'x', (), 2.0, False, {})
    assert checked(1, second='y', required=2.0, optional=True) == (
        1, 'y', (), 2.0, True, {})
    assert checked(1, 'y', b'a', b'b', required=2.0, first=1j, other=2j) == (
        1, 'y', (b'a', b'b'), 2.0, False, {'first': 1j, 'other': 2j})
    assert tuple(signature(checked, follow_wrapped=False).parameters)[:5] == (
        'first', 'second', 'rest', 'required', 'optional')
    for invoke in (
        lambda: checked('bad', required=2.0),
        lambda: checked(1, second=2, required=2.0),
        lambda: checked(1, 'x', 'bad', required=2.0),
        lambda: checked(1, required='bad'),
        lambda: checked(1, required=2.0, optional='bad'),
        lambda: checked(1, required=2.0, other='bad'),
    ):
        with raises(BeartypeCallHintParamViolation):
            invoke()
    for invoke in (
        lambda: checked(required=2.0),
        lambda: checked(1),
        lambda: checked(1, 'x', second='duplicate', required=2.0),
        lambda: checked(first=1, required=2.0),
    ):
        with raises(TypeError):
            invoke()


def test_decor_explicit_optional_default_identity() -> None:
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


def test_decor_explicit_unrepresentable_default() -> None:
    '''Binding a default never evaluates its repr as generated source.'''
    from beartype import beartype

    class Default:
        def __repr__(self):
            raise RuntimeError('Do not represent defaults.')

    default = Default()

    @beartype
    def accepts(value=default) -> object:
        return value

    assert accepts() is default
    assert accepts(default) is default


def test_decor_explicit_named_args_and_kwargs() -> None:
    '''Fixed parameters named args and kwargs must not capture generic locals.'''
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


def test_decor_explicit_bound_methods() -> None:
    '''Binding omits the instance, including optional and positional-only self.'''
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from inspect import signature
    from pytest import raises

    class Methods:
        def positional(self, /, value: int = 3) -> int:
            return value

        def optional(self=None, value: int = 3) -> int:
            return value

        def variadic(*values: int) -> int:
            return sum(values[1:])

        @classmethod
        def class_method(cls, value: int = 3) -> int:
            return value

    instance = Methods()
    for method in (instance.positional, instance.optional, Methods.class_method):
        checked = beartype(method)
        assert checked() == 3
        assert checked(value=4) == 4
        assert signature(checked) == signature(method)
        assert checked.__code__.co_argcount == 1
        with raises(BeartypeCallHintParamViolation):
            checked('bad')
    checked_variadic = beartype(instance.variadic)
    assert checked_variadic(1, 2) == 3
    with raises(BeartypeCallHintParamViolation):
        checked_variadic('bad')


async def test_decor_explicit_async_optional_and_returns() -> None:
    '''Coroutines bind natively and check parameters and awaited results.'''
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintParamViolation, BeartypeCallHintReturnViolation)
    from inspect import iscoroutinefunction
    from pytest import raises
    from typing import NoReturn

    default = object()

    @beartype
    async def accepts(value: int = default, /, *values: int,
                      label: str = 'x', **named: int):
        return value, values, label, named

    assert iscoroutinefunction(accepts) is True
    assert await accepts() == (default, (), 'x', {})
    assert await accepts(1, 2, label='y', z=3) == (1, (2,), 'y', {'z': 3})
    with raises(BeartypeCallHintParamViolation):
        await accepts(default)
    with raises(BeartypeCallHintParamViolation):
        await accepts(1, 'bad')

    @beartype
    async def checked(value: int) -> str:
        return value

    @beartype
    async def noreturn(value: int) -> NoReturn:
        return value

    # Binding errors precede coroutine creation, while checks run on await.
    with raises(TypeError):
        checked()
    with raises(TypeError):
        checked(1, 2)
    with raises(BeartypeCallHintReturnViolation):
        await checked(1)
    with raises(BeartypeCallHintReturnViolation):
        await noreturn(1)


def test_decor_explicit_generator_protocol() -> None:
    '''Explicit forwarding preserves send, throw, close, and return values.'''
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


async def test_decor_explicit_async_generator_protocol() -> None:
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


def test_decor_explicit_live_default_values() -> None:
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
