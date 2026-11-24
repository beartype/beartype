#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''Per-parameter opt-out tests exercising real decorated Python callables.'''


def test_ignore_arg_names_configuration() -> None:
    '''Names are validated and frozen before configuration memoization.'''
    from beartype import BeartypeConf
    from beartype.roar import BeartypeConfParamException
    from pytest import raises

    names = ['ignored', 'other', 'ignored']
    conf = BeartypeConf(ignore_arg_names=names)
    names.append('later')
    assert conf.ignore_arg_names == frozenset(('ignored', 'other'))
    assert conf is BeartypeConf(ignore_arg_names={'other', 'ignored'})
    assert conf is BeartypeConf(ignore_arg_names={'ignored': None, 'other': 1})
    assert BeartypeConf(**conf.kwargs).ignore_arg_names == conf.ignore_arg_names
    assert 'ignore_arg_names' in repr(conf)
    assert BeartypeConf(ignore_arg_names=[]) is BeartypeConf()
    with raises(AttributeError):
        conf.ignore_arg_names = frozenset()
    for invalid in (None, 1, 'arg', b'arg', iter(['arg']), [1], [[]],
                    [''], ['a.b'], ['*args'], ['return'], ['class']):
        with raises(BeartypeConfParamException):
            BeartypeConf(ignore_arg_names=invalid)


def test_ignore_arg_names_fixed_parameters() -> None:
    '''Skipping fixed parameters leaves positions and excess kwargs intact.'''
    from beartype import BeartypeConf, beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    def original(first: int, /, ignored: int, checked: int, *, option: int,
                 **extras: int) -> int:
        return checked + sum(extras.values())

    annotations = original.__annotations__.copy()
    decorated = beartype(original, conf=BeartypeConf(
        ignore_arg_names=['first', 'ignored', 'option', 'absent']))
    assert decorated('skip', 'skip', 3, option='skip', extra=4) == 7
    assert decorated('skip', ignored='skip', checked=3, option='skip') == 3
    assert original.__annotations__ == annotations
    with raises(BeartypeCallHintParamViolation):
        decorated('skip', 'skip', 'bad', option='skip')
    with raises(BeartypeCallHintParamViolation):
        decorated('skip', 'skip', 3, option='skip', extra='bad')
    with raises(TypeError):
        decorated('skip', 'skip', 3)


def test_ignore_arg_names_variadic_parameters() -> None:
    '''Variadic declaration names, not caller keyword names, select opt-outs.'''
    from beartype import BeartypeConf, beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    def original(checked: int, *items: int, **options: int) -> int:
        return checked

    skip_items = beartype(original, conf=BeartypeConf(ignore_arg_names=['items']))
    assert skip_items(1, 'unchecked', valid=2) == 1
    with raises(BeartypeCallHintParamViolation):
        skip_items(1, 'unchecked', invalid='bad')
    skip_options = beartype(original, conf=BeartypeConf(ignore_arg_names=['options']))
    assert skip_options(1, 2, anything='unchecked') == 1
    with raises(BeartypeCallHintParamViolation):
        skip_options(1, 'bad')
    skip_both = beartype(original, conf=BeartypeConf(ignore_arg_names=['items', 'options']))
    assert skip_both(1, 'unchecked', anything='unchecked') == 1
    with raises(BeartypeCallHintParamViolation):
        skip_both('bad')
    # Naming an excess keyword does not opt it out of its **options annotation.
    unknown = beartype(original, conf=BeartypeConf(ignore_arg_names=['anything']))
    with raises(BeartypeCallHintParamViolation):
        unknown(1, anything='bad')


def test_ignore_arg_names_hints_and_returns() -> None:
    '''Opted-out unsupported hints are not reduced; returns still fail.'''
    from beartype import BeartypeConf, beartype
    from beartype.roar import BeartypeCallHintReturnViolation
    from pytest import raises

    def original(ignored: 42, checked: int) -> int:
        return checked

    conf = BeartypeConf(ignore_arg_names=['ignored'])
    assert beartype(original, conf=conf)(object(), 3) == 3
    assert original.__annotations__['ignored'] == 42

    def forward(ignored: 'UnresolvableOptOutAnnotation') -> int:
        return 3
    assert beartype(forward, conf=conf)(object()) == 3

    def bad_return(ignored: int) -> int:
        return 'bad'
    with raises(BeartypeCallHintReturnViolation):
        beartype(bad_return, conf=conf)('unchecked')


def test_ignore_arg_names_methods_and_coroutines() -> None:
    '''Class decoration, defaults, and async calls honor the same setting.'''
    import asyncio
    from beartype import BeartypeConf, beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    conf = BeartypeConf(ignore_arg_names=['ignored'])

    @beartype(conf=conf)
    class Example:
        def method(self, ignored: int, checked: int = 2) -> int:
            return checked

        @classmethod
        def class_method(cls, ignored: int, checked: int) -> int:
            return checked

        @staticmethod
        def static_method(ignored: int, checked: int) -> int:
            return checked

    example = Example()
    assert example.method('unchecked') == 2
    for method in (example.method, Example.class_method, Example.static_method):
        assert method('unchecked', 3) == 3
        with raises(BeartypeCallHintParamViolation):
            method('unchecked', 'bad')

    @beartype(conf=conf)
    async def coroutine(ignored: int, checked: int) -> int:
        return checked
    loop = asyncio.new_event_loop()
    try:
        assert loop.run_until_complete(coroutine('unchecked', 3)) == 3
        with raises(BeartypeCallHintParamViolation):
            loop.run_until_complete(coroutine('unchecked', 'bad'))
    finally:
        loop.close()


def test_ignore_arg_names_default_and_reserved() -> None:
    '''Default checking and reserved-name validation remain unchanged.'''
    from beartype import BeartypeConf, beartype
    from beartype.roar import (
        BeartypeCallHintParamViolation, BeartypeDecorParamNameException)
    from pytest import raises

    @beartype
    def checked(value: int) -> int:
        return value
    with raises(BeartypeCallHintParamViolation):
        checked('bad')

    def reserved(__bear_reserved: int) -> int:
        return 1
    with raises(BeartypeDecorParamNameException):
        beartype(reserved, conf=BeartypeConf(ignore_arg_names=['__bear_reserved']))


def test_ignore_arg_names_claw(tmp_path) -> None:
    """A real import hook passes the option through to generated decorators."""
    import os
    import subprocess
    import sys

    import beartype
    from pathlib import Path

    package = tmp_path / 'optout_fixture'
    package.mkdir()
    (package / '__init__.py').write_text(
        'def run(ignored: int, checked: int) -> int:\n'
        '    return checked\n'
        'def other(checked: int) -> int:\n'
        '    return checked\n'
        'def bad_return(ignored: int) -> int:\n'
        '    return "bad"\n', encoding='utf-8')
    script = """
from beartype import BeartypeConf
from beartype.claw import beartype_package
from beartype.roar import BeartypeCallHintParamViolation, BeartypeCallHintReturnViolation
beartype_package('optout_fixture', conf=BeartypeConf(ignore_arg_names=['ignored']))
import optout_fixture
assert optout_fixture.run('unchecked', 3) == 3
assert optout_fixture.other(3) == 3
for call, exception in (
    (lambda: optout_fixture.run('unchecked', 'bad'), BeartypeCallHintParamViolation),
    (lambda: optout_fixture.other('bad'), BeartypeCallHintParamViolation),
    (lambda: optout_fixture.bad_return('unchecked'), BeartypeCallHintReturnViolation),
):
    try:
        call()
    except exception:
        pass
    else:
        raise AssertionError('unignored check did not run')
"""
    # Use a fresh normal interpreter, not multiprocessing/forkserver machinery.
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join((str(Path(beartype.__file__).resolve().parent.parent), str(tmp_path)))
    result = subprocess.run(
        [sys.executable, '-c', script], env=env, capture_output=True,
        text=True, check=False, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
