#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **inline import hook unit tests** (i.e., exercising the
:attr:`beartype.BeartypeConf.claw_is_inline` option of :mod:`beartype.claw`
import hooks within the active Python process).
'''

# ....................{ IMPORTS                            }....................
import pytest

# ....................{ CONSTANTS                          }....................
PACKAGE_NAME = 'beartype_test.a00_unit.data.claw.intraprocess.inline_package'
'''
Name of the data package exercised below.
'''

# ....................{ TESTS                              }....................
@pytest.mark.run_in_subprocess
def test_claw_inline_on() -> None:
    '''
    Test that an import hook configured with ``claw_is_inline=True`` type-checks
    identically to the default wrapper-based approach while retaining *no*
    wrapper frames on the call stack.
    '''

    # Defer test-specific imports.
    import asyncio, sys
    from beartype import BeartypeConf
    from beartype.claw import beartype_package
    from beartype.roar import BeartypeCallHintViolation
    from pytest import raises

    beartype_package(PACKAGE_NAME, conf=BeartypeConf(claw_is_inline=True))
    from beartype_test.a00_unit.data.claw.intraprocess.inline_package import (
        inline_module as m)

    # Instrumented callables are returned as is, so have no wrapper.
    for func in (m.rec, m.later, m.Renderer.compact, m.doc, m.oneline):
        assert not hasattr(func, '__wrapped__')
    assert m.doc.__doc__ == 'Docstring.'

    # Generators are *NOT* instrumented but still checked. Functions merely
    # containing nested functions are instrumented (the nested ones are not).
    assert hasattr(m.gen, '__wrapped__')
    assert not hasattr(m.nested, '__wrapped__')
    # Callables decorated by foreign decorators are *NOT* instrumented.
    assert m.foreign_decorated(1) == 1
    with raises(BeartypeCallHintViolation):
        m.foreign_decorated('s')

    # Violations are raised for parameters and returns alike.
    renderer = m.Renderer()
    assert renderer.compact([1, [2]]) == '[1,[2]]'
    with raises(BeartypeCallHintViolation):
        renderer.compact('no')
    assert m.Renderer.stat(3) == 3
    with raises(BeartypeCallHintViolation):
        m.Renderer.stat('s')
    assert isinstance(m.Renderer.cm(1), m.Renderer)
    with raises(BeartypeCallHintViolation):
        m.Renderer.cm(0)
    with raises(BeartypeCallHintViolation):
        m.Renderer.cm('s')
    renderer.prop = 4
    assert renderer.prop == 4
    with raises(BeartypeCallHintViolation):
        renderer.prop = 's'
    renderer._p = 's'
    with raises(BeartypeCallHintViolation):
        renderer.prop

    # Forward references resolve lazily.
    assert isinstance(m.later(m.Later2()), m.Later2)
    with raises(BeartypeCallHintViolation):
        m.later(3)

    # Implicit and explicit returns.
    assert m.falls_off(1) == 'a'
    with raises(BeartypeCallHintViolation):
        m.falls_off(0)
    assert m.implicit_none(1) is None
    with raises(BeartypeCallHintViolation):
        m.implicit_none('s')
    with raises(BeartypeCallHintViolation):
        m.bad_none(1)
    assert m.bare_return(0) is None
    assert m.bare_return(1) is None
    with raises(ValueError):
        m.noret(1)
    with raises(BeartypeCallHintViolation):
        m.noret_bad(1)

    # Coroutines.
    assert asyncio.run(m.coro(0)) == 'ok'
    with raises(BeartypeCallHintViolation):
        asyncio.run(m.coro(5))
    with raises(BeartypeCallHintViolation):
        asyncio.run(m.coro('s'))

    # Defaults, variadics, and positional-only parameters.
    assert m.defaults() == (1, (), 'b', {})
    assert m.defaults(1, 2, 3, b='x', z=1.5) == (1, (2, 3), 'x', {'z': 1.5})
    with raises(BeartypeCallHintViolation):
        m.defaults('a')
    with raises(BeartypeCallHintViolation):
        m.defaults(1, b=3)
    with raises(BeartypeCallHintViolation):
        m.defaults(1, z='s')
    with raises(BeartypeCallHintViolation):
        m.defaults(1, 's')
    assert m.posonly(1, 2) == 3
    with raises(BeartypeCallHintViolation):
        m.posonly('s', 2)
    with raises(BeartypeCallHintViolation):
        m.posonly(1, b='s')
    assert m.untyped(object) is object
    assert m.nested(1) == 1
    assert list(m.gen(3)) == [3]
    assert m.oneline(1) == 1

    # Inline mode halves stack consumption: this recursion fails under
    # wrappers at the same limit (see the sibling test below).
    limit = sys.getrecursionlimit()
    sys.setrecursionlimit(1000)
    try:
        assert m.rec(700) == 700
    finally:
        sys.setrecursionlimit(limit)


@pytest.mark.run_in_subprocess
def test_claw_inline_off() -> None:
    '''
    Test that an import hook configured with the default ``claw_is_inline=False``
    still wraps callables (and thus retains wrapper frames).
    '''

    import sys
    from beartype.claw import beartype_package
    from beartype.roar import BeartypeCallHintViolation
    from pytest import raises

    beartype_package(PACKAGE_NAME)
    from beartype_test.a00_unit.data.claw.intraprocess.inline_package import (
        inline_module as m)

    assert hasattr(m.rec, '__wrapped__')
    with raises(BeartypeCallHintViolation):
        m.doc('s')

    limit = sys.getrecursionlimit()
    sys.setrecursionlimit(1000)
    try:
        with raises(RecursionError):
            m.rec(700)
    finally:
        sys.setrecursionlimit(limit)


@pytest.mark.run_in_subprocess
def test_claw_inline_unhooked_checkers() -> None:
    '''
    Test that an instrumented callable whose ``@beartype`` decoration never
    ran (e.g., ``@no_type_check``) still executes with its no-op checkers.
    '''

    from beartype import BeartypeConf, BeartypeStrategy
    from beartype._decor._nontype._inline.inlineinit import (
        is_func_inline_ready,
        noop_check_args,
        noop_check_return,
    )
    from beartype.claw import beartype_package

    beartype_package(PACKAGE_NAME, conf=BeartypeConf(
        claw_is_inline=True, strategy=BeartypeStrategy.O0))
    from beartype_test.a00_unit.data.claw.intraprocess.inline_package import (
        inline_module as m)

    # O(0) strategy disables checking entirely but must not crash.
    assert m.doc('s') == 's'
    assert noop_check_args() is None
    assert noop_check_return(5) == 5
    assert not is_func_inline_ready(lambda: None)
