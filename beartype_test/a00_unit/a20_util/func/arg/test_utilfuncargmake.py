#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''Callable-specific signature generation tests.'''

def test_make_func_signature_parameter_kinds() -> None:
    '''Compile signatures and compare their binding against existing fixtures.'''
    from beartype import BeartypeConf
    from beartype._util.func.arg.utilfuncargmake import make_func_signature
    from beartype_test.a00_unit.data.func.data_func import (
        ClassOfMethods,
        func_args_0,
        func_args_1_flex_mandatory,
        func_args_1_varpos,
        func_args_1_kwonly_mandatory,
        func_args_2_kwonly_mixed,
        func_args_3_flex_mandatory_optional_varkw,
        func_args_5_flex_mandatory_varpos_kwonly_varkw,
    )
    from beartype_test.a00_unit.data.func.data_pep570 import (
        func_args_2_posonly_mixed,
        func_args_10_all_except_flex_mandatory,
    )
    from inspect import Parameter, signature

    methods = ClassOfMethods()
    for func in (
        func_args_0,
        func_args_1_flex_mandatory,
        func_args_1_varpos,
        func_args_1_kwonly_mandatory,
        func_args_2_kwonly_mixed,
        func_args_3_flex_mandatory_optional_varkw,
        func_args_5_flex_mandatory_varpos_kwonly_varkw,
        func_args_2_posonly_mixed,
        func_args_10_all_except_flex_mandatory,
        methods.meth_args_6_flex_mandatory_varpos_kwonly_varkw,
    ):
        scope = {'__beartype_hidden': object()}
        code = make_func_signature(
            func, scope, BeartypeConf(), func_name='generated')
        exec(f'{code}    return locals()\n', scope)
        generated = scope['generated']
        original_signature = signature(func)
        generated_signature = signature(generated)
        visible_parameters = {
            name: parameter
            for name, parameter in generated_signature.parameters.items()
            if not name.startswith('__beartype_')
        }
        assert visible_parameters == original_signature.parameters
        assert generated_signature.return_annotation == (
            original_signature.return_annotation)
        assert generated_signature.parameters['__beartype_hidden'].kind == (
            Parameter.KEYWORD_ONLY)

        positional = []
        keywords = {}
        for parameter in original_signature.parameters.values():
            if parameter.kind in (
                Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
                positional.append(object())
            elif parameter.kind is Parameter.KEYWORD_ONLY:
                keywords[parameter.name] = object()
            elif parameter.kind is Parameter.VAR_POSITIONAL:
                positional.extend((object(), object()))
            elif parameter.kind is Parameter.VAR_KEYWORD:
                keywords['extra'] = object()
        expected = original_signature.bind(*positional, **keywords)
        expected.apply_defaults()
        actual = generated(*positional, **keywords)
        assert {name: actual[name] for name in visible_parameters} == (
            expected.arguments)


def test_make_func_signature_default_and_annotation_identity() -> None:
    '''Defaults and annotations are bound objects, including None and strings.'''
    from beartype import BeartypeConf
    from beartype._util.func.arg.utilfuncargmake import make_func_signature
    from inspect import signature

    class Unrepresentable(object):
        def __repr__(self):
            raise RuntimeError('Defaults must not be represented as source.')

    default = Unrepresentable()
    mutable = []

    def original(value=default, /, *, items=mutable):
        pass

    original.__annotations__ = {'value': None, 'items': 'Undeclared', 'return': None}
    scope = {}
    code = make_func_signature(original, scope, BeartypeConf())
    exec(f'{code}    return value, items\n', scope)
    generated = scope['original']
    assert generated() == (default, mutable)
    assert signature(generated).parameters['value'].default is default
    assert signature(generated).parameters['items'].default is mutable
    assert generated.__annotations__ == original.__annotations__


async def test_make_func_signature_coroutine_and_actual_wrapper() -> None:
    '''Asynchronicity and arguments come from the actual callable.'''
    from beartype import BeartypeConf
    from beartype._util.func.arg.utilfuncargmake import make_func_signature
    from functools import wraps
    from inspect import iscoroutinefunction, signature

    async def coroutine(*, value: int) -> int:
        return value

    scope = {}
    code = make_func_signature(coroutine, scope, BeartypeConf())
    exec(f'{code}    return value\n', scope)
    assert iscoroutinefunction(scope['coroutine']) is True
    assert await scope['coroutine'](value=3) == 3

    @wraps(coroutine)
    def synchronous(*args, **kwargs):
        return args, kwargs

    scope = {}
    code = make_func_signature(synchronous, scope, BeartypeConf())
    exec(f'{code}    return args, kwargs\n', scope)
    generated = scope['coroutine']
    assert iscoroutinefunction(generated) is False
    assert generated(1, unrelated=2) == ((1,), {'unrelated': 2})
    assert tuple(signature(generated).parameters) == ('args', '__beartype_object_' + str(id(int)), 'kwargs')


def test_make_func_signature_debug_and_unannotated() -> None:
    '''Debug comments are optional and annotation copying can be disabled.'''
    from beartype import BeartypeConf
    from beartype._util.func.arg.utilfuncargmake import make_func_signature

    def original(*, value: int) -> int:
        return value

    scope = {'__beartype_hidden': 5}
    code = make_func_signature(
        original, scope, BeartypeConf(is_debug=True), is_annotated=False)
    assert code == (
        'def original(\n'
        '    *,\n'
        '    value,\n'
        '    __beartype_hidden=__beartype_hidden, # is 5\n'
        '):\n'
    )
    exec(f'{code}    return value\n', scope)
    assert scope['original'].__annotations__ == {}


def test_make_func_signature_reserved_names() -> None:
    '''Reject names that conflict with private wrapper variables.'''
    from beartype import BeartypeConf
    from beartype.roar import BeartypeDecorParamNameException
    from beartype._util.func.arg.utilfuncargmake import make_func_signature
    from pytest import raises

    def reserved(*, __beartype_hidden):
        return __beartype_hidden

    with raises(BeartypeDecorParamNameException):
        make_func_signature(reserved, {}, BeartypeConf())
    with raises(BeartypeDecorParamNameException):
        make_func_signature(lambda: None, {}, BeartypeConf(), func_name='def')

    scope = {}
    code = make_func_signature(lambda: None, scope, BeartypeConf())
    exec(f'{code}    return 1\n', scope)
    assert scope['__beartype_wrapper']() == 1


def test_make_func_signature_bound_positional_only() -> None:
    '''The implicit instance is omitted even when positional-only or optional.'''
    from beartype import BeartypeConf
    from beartype._util.func.arg.utilfuncargmake import make_func_signature
    from inspect import signature

    class Methods(object):
        def positional(self, value=1, /, *, label='x'):
            return value, label

        def optional(self=None, value=1):
            return value

    methods = Methods()
    for method in (methods.positional, methods.optional):
        scope = {}
        code = make_func_signature(method, scope, BeartypeConf())
        exec(f'{code}    return value\n', scope)
        generated = scope[method.__name__]
        assert {
            name: parameter for name, parameter in signature(generated).parameters.items()
            if not name.startswith('__beartype_')
        } == signature(method).parameters
        assert generated() == 1


def test_make_func_signature_c_callable_rejected() -> None:
    '''Unsupported C callables raise the existing callable exception.'''
    from beartype import BeartypeConf
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargmake import make_func_signature
    from pytest import raises

    with raises(_BeartypeUtilCallableException):
        make_func_signature(len, {}, BeartypeConf())
