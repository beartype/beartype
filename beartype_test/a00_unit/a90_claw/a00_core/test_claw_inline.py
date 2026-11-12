#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **inline abstract syntax tree (AST) transformation unit tests**
(i.e., exercising the :attr:`beartype.BeartypeConf.claw_is_inline` option of
the :mod:`beartype.claw` AST transformer *without* importing anything).
'''

# ....................{ IMPORTS                            }....................
import ast
import pytest
import warnings

# ....................{ HELPERS                            }....................
def _transform(source: str, **conf_kwargs) -> str:
    '''
    Source code transformed from the passed source by the inline AST
    transformer, unparsed back into a string.
    '''

    from beartype import BeartypeConf
    from beartype.claw._ast.clawastmain import BeartypeNodeTransformer

    tree = BeartypeNodeTransformer(
        module_name='m',
        conf=BeartypeConf(claw_is_inline=True, **conf_kwargs),
    ).visit(ast.parse(source))
    ast.fix_missing_locations(tree)

    # Transformed code *MUST* compile without warnings (e.g., the constant
    # conditional placeholders must not raise "SyntaxWarning").
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        compile(tree, '<m>', 'exec')
    return ast.unparse(tree)


ARGS = "('__beartype_inline_check_args__' if True else None)"
RETURN = "('__beartype_inline_check_return__' if True else None)"
INIT = '@__beartype_inline_init__'

# ....................{ TESTS                              }....................
def test_claw_inline_ast_params_and_returns() -> None:
    '''
    Test instrumentation of all parameter kinds and of explicit, bare, and
    implicit returns.
    '''

    out = _transform(
        'def f(a: int, /, b: str, *c: int, k: float = 1.0, **kw: int) -> str:\n'
        '    """doc"""\n'
        '    if a:\n'
        '        return b\n'
        '    for i in c:\n'
        '        return\n')

    assert INIT in out
    # Docstring stays first; call forwards every parameter kind.
    assert out.index('"""doc"""') < out.index('__beartype_inline_check_args__')
    assert f'{ARGS}(a, b, *c, k=k, **kw)' in out
    assert f'return {RETURN}(b)' in out
    # Bare and implicit returns check None.
    assert out.count(f'return {RETURN}(None)') == 2


def test_claw_inline_ast_methods() -> None:
    '''
    Test instrumentation of methods, whitelisted decorators, and exclusion of
    callables decorated by unknown decorators, generators, and callables
    nested in other callables.
    '''

    out = _transform(
        'class K:\n'
        '    def m(self, x: int) -> None:\n'
        '        return\n'
        '    @staticmethod\n'
        '    def s(x: int) -> int: return x\n'
        '    @classmethod\n'
        '    def c(cls, x: int) -> int: return x\n'
        '    @property\n'
        '    def p(self) -> int: return 1\n'
        '    @p.setter\n'
        '    def p(self, v: int): pass\n'
        '    @other\n'
        '    def o(self, v: int): pass\n'
        '    def g(self, v: int) -> int:\n'
        '        yield v\n'
        '    def u(self, v):\n'
        '        return v\n'
        '    async def a(self, v: int) -> int:\n'
        '        return v\n')

    # Instrumented: m, s, c, p (getter and setter), a.
    assert out.count(INIT) == 6
    # Excluded: the unknown decorator, the generator, and the untyped method.
    body_o = out[out.index('def o('):]
    assert INIT not in body_o.split('def g(')[0]
    assert INIT not in out[out.index('def g('):out.index('def u(')]
    assert INIT not in out[
        out.index('def u('):out.rindex(INIT, 0, out.index('async def a('))]


def test_claw_inline_ast_nested() -> None:
    '''
    Test that functions nested in other functions are *not* instrumented while
    their enclosing functions are.
    '''

    out = _transform(
        'def outer(x: int) -> int:\n'
        '    def inner(y: int) -> int:\n'
        '        return y\n'
        '    return inner(x)\n')

    assert out.count(INIT) == 1
    # The nested return is untouched.
    assert 'return y' in out
    assert f'return {RETURN}(inner(x))' in out


def test_claw_inline_ast_off() -> None:
    '''
    Test that the default configuration leaves the AST uninstrumented.
    '''

    from beartype import BeartypeConf
    from beartype.claw._ast.clawastmain import BeartypeNodeTransformer

    tree = BeartypeNodeTransformer(
        module_name='m', conf=BeartypeConf()).visit(
        ast.parse('def f(x: int) -> int:\n    return x\n'))
    assert '__beartype_inline' not in ast.unparse(ast.fix_missing_locations(tree))


def test_claw_inline_is_node_callable_generator() -> None:
    '''
    Test :func:`beartype._util.ast.utilasttest.is_node_callable_generator`.
    '''

    from beartype._util.ast.utilasttest import is_node_callable_generator

    def parse(source: str):
        return ast.parse(source).body[0]

    assert is_node_callable_generator(parse('def f():\n    yield 1\n'))
    assert is_node_callable_generator(parse('def f():\n    yield from x\n'))
    assert is_node_callable_generator(parse('async def f():\n    yield 1\n'))
    assert not is_node_callable_generator(parse('def f():\n    return 1\n'))
    # A yield in a nested scope does not make the outer callable a generator.
    assert not is_node_callable_generator(parse(
        'def f():\n    def g():\n        yield 1\n    return g\n'))
    assert not is_node_callable_generator(parse(
        'def f():\n    return lambda: (yield)\n'))


def test_claw_inline_cache_from_source() -> None:
    '''
    Test that inline bytecode caches are distinct from default caches.
    '''

    from beartype.claw._importlib.clawimpcache import (
        cache_from_source_beartype_inline)

    path = cache_from_source_beartype_inline('/tmp/some_module.py')
    assert 'beartype_inline' in path or 'inline' in path
    assert path.endswith('.pyc')


def _exec_inline(source: str, **conf_kwargs) -> dict:
    '''
    Namespace of a module transformed by the inline AST transformer from the
    passed source and then executed in the active process.
    '''

    from beartype import BeartypeConf
    from beartype.claw._clawstate import claw_state

    import sys
    from types import ModuleType

    conf = BeartypeConf(claw_is_inline=True, **conf_kwargs)
    claw_state.module_name_to_beartype_conf['m'] = conf

    # Importable module, required to resolve forward references.
    module = ModuleType('m')
    sys.modules['m'] = module
    try:
        out = _transform(source, **conf_kwargs)
        exec(compile(out, '<m>', 'exec'), module.__dict__)
    finally:
        del claw_state.module_name_to_beartype_conf['m']
    return module.__dict__


@pytest.fixture(autouse=True)
def _unregister_module():
    '''
    Unregister the importable module registered by :func:`._exec_inline` after
    each test, which must outlive that function to resolve forward references.
    '''

    import sys
    yield
    sys.modules.pop('m', None)


def test_claw_inline_exec() -> None:
    '''
    Test the inline decorator end to end by executing transformed code.
    '''

    from beartype.roar import BeartypeCallHintViolation
    from pytest import raises

    ns = _exec_inline(
        'def args_only(x: int): return x\n'
        'def ret_only(x) -> int: return x\n'
        'def both(x: int, *, k: str = "k") -> int: return x\n'
        'def fwd(x: int) -> "Later": return Later()\n'
        'class Later: pass\n'
        'def noret(x: int) -> "NoReturn":\n'
        '    raise ValueError\n'
        'from typing import NoReturn\n'
    )

    both = ns['both']
    assert not hasattr(both, '__wrapped__')
    assert both(1) == 1
    with raises(BeartypeCallHintViolation):
        both('s')
    with raises(BeartypeCallHintViolation):
        both(1, k=2)
    assert ns['args_only'](1) == 1
    with raises(BeartypeCallHintViolation):
        ns['args_only']('s')
    assert ns['ret_only'](1) == 1
    with raises(BeartypeCallHintViolation):
        ns['ret_only']('s')
    assert isinstance(ns['fwd'](1), ns['Later'])
    with raises(ValueError):
        ns['noret'](1)


def test_claw_inline_exec_fallbacks() -> None:
    '''
    Test that conf-disabled or opted-out instrumented callables still run.
    '''

    from beartype import BeartypeStrategy
    from beartype.roar import BeartypeCallHintViolation
    from pytest import raises

    # Callables with nothing to check preserve their no-ops.
    ns = _exec_inline('def f(x): return x\n')
    assert ns['f'](1) == 1

    # The O(0) strategy checks nothing but must still run.
    ns = _exec_inline(
        'def f(x: int) -> int: return x\n', strategy=BeartypeStrategy.O0)
    assert ns['f']('s') == 's'

    # @no_type_check opts out.
    ns = _exec_inline(
        'from typing import no_type_check\n'
        '@no_type_check\n'
        'def f(x: int) -> int: return x\n')
    assert ns['f']('s') == 's'

    # Unwhitelisted decorators are never instrumented but still wrapped.
    ns = _exec_inline(
        'def deco(f): return f\n'
        '@deco\n'
        'def f(x: int) -> int: return x\n')
    with raises(BeartypeCallHintViolation):
        ns['f']('s')


def test_claw_inline_init_non_function() -> None:
    '''
    Test that the inline initializer ignores non-functions.
    '''

    from beartype._decor._nontype._inline.inlineinit import (
        beartype_inline_init)

    assert beartype_inline_init(len) is len


def test_claw_inline_cache_markers() -> None:
    '''
    Test the default and inline bytecode cache path factories.
    '''

    from beartype.claw._importlib.clawimpcache import (
        cache_from_source_beartype,
        cache_from_source_beartype_inline,
    )

    path_default = cache_from_source_beartype('some_module.py')
    path_inline = cache_from_source_beartype_inline('some_module.py')
    assert path_default != path_inline


def test_claw_inline_checker_helpers() -> None:
    '''
    Test the low-level inline checker helpers.
    '''

    from beartype._decor._nontype._inline.inlineinit import (
        is_func_inline_ready,
        noop_check_args,
        noop_check_return,
        swap_inline_checkers,
    )

    assert noop_check_args(1, k=2) is None
    assert noop_check_return(5) == 5
    # Ordinary callables are never ready.
    assert not is_func_inline_ready(lambda: None)
    assert not is_func_inline_ready(len)
