#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`810` unit tests.

This submodule unit tests :pep:`810` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ PRIVATE ~ globals                  }....................
_TARGET_MODULE_NAME = 'beartype_test_lazytarget810'
'''
Name of a synthetic module that nothing else imports, lazily imported below.
'''


_HOST_MODULE_SOURCE = f"""
from beartype import beartype

lazy from {_TARGET_MODULE_NAME} import Target

@beartype
def func(arg: Target) -> Target:
    return arg

@beartype
def func_nested(arg: list[Target] | None, other: Later) -> int:
    return len(arg or ())

@beartype
def func_str(arg: 'Target') -> 'Target':
    return arg

@beartype
class Klass(object):
    def method(self, arg: Target) -> Target:
        return arg

class Later(object):
    pass

class Opaque(object):
    def __call__(self, format):
        return {{'arg': int, 'return': int}}

def func_opaque(arg: Target) -> Target:
    return arg

func_opaque.__annotate__ = Opaque()
"""
'''
Source code of a module lazily importing the synthetic target module above.
'''

# ....................{ PRIVATE ~ fixtures                 }....................
def _make_host_module(tmp_path, monkeypatch):
    '''
    Module lazily importing a synthetic target module, whose callables are
    decorated by :func:`beartype.beartype`.
    '''

    # Defer test-specific imports.
    from sys import modules
    from types import ModuleType

    # Synthetic module lazily imported by the host module.
    (tmp_path / f'{_TARGET_MODULE_NAME}.py').write_text(
        'class Target(object):\n    pass\n', encoding='utf-8')
    monkeypatch.syspath_prepend(str(tmp_path))

    # Ensure this target module is unimported now and removed on test teardown.
    monkeypatch.setitem(modules, _TARGET_MODULE_NAME, None)
    monkeypatch.delitem(modules, _TARGET_MODULE_NAME)

    # Host module registered under its own name for beartype introspection.
    module = ModuleType('beartype_test_lazyhost810')
    monkeypatch.setitem(modules, module.__name__, module)
    exec(compile(_HOST_MODULE_SOURCE, '<lazyhost810>', 'exec'), module.__dict__)

    # Decorating this module's callables *MUST* preserve laziness.
    assert _TARGET_MODULE_NAME not in modules
    return module

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.15.0')
def test_decor_pep810(tmp_path, monkeypatch) -> None:
    '''
    Test :pep:`810` support implemented in the :func:`beartype.beartype`
    decorator, validating that decorating callables annotated by lazily
    imported type hints preserves the laziness of those imports.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeCallHintParamViolation
    from importlib import import_module
    from pytest import raises

    # Host module lazily importing the target module.
    host = _make_host_module(tmp_path, monkeypatch)

    # Calling decorated callables reifies this import and type-checks hints.
    Target = import_module(_TARGET_MODULE_NAME).Target
    obj = Target()
    assert host.func(obj) is obj
    assert host.func_str(obj) is obj
    assert host.Klass().method(obj) is obj
    assert host.func_nested([obj], host.Later()) == 1
    assert host.func_nested(None, host.Later()) == 0
    with raises(BeartypeCallHintParamViolation):
        host.func(1)
    with raises(BeartypeCallHintParamViolation):
        host.func_str(1)
    with raises(BeartypeCallHintParamViolation):
        host.Klass().method('a')
    with raises(BeartypeCallHintParamViolation):
        host.func_nested([1], host.Later())
    with raises(BeartypeCallHintParamViolation):
        host.func_nested(None, 'not Later')


@skip_if_python_version_less_than('3.15.0')
def test_pep810_getters(tmp_path, monkeypatch) -> None:
    '''
    Test the private :mod:`beartype._util.hint.pep.proposal.pep810` getters and
    the private getter of annotations for callables whose ``__annotate__()``
    dunder methods are not pure-Python functions.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal import pep810
    from beartype._util.hint.pep.proposal.pep749.pep649749annotate import (
        get_hintable_pep649749_annotations_or_none)
    from beartype._util.hint.pep.proposal.pep810 import (
        Pep810LiveGlobals,
        get_dictable_globals_or_none,
        get_scope_nonlazy_or_none,
        reduce_dictable_pep810_lazy_globals_to_pep484_refs,
    )
    from pytest import raises
    from sys import modules
    from types import ModuleType

    # Host module lazily importing the target module.
    host = _make_host_module(tmp_path, monkeypatch)
    host_globals = host.__dict__

    # Global scopes of modules, classes, and callables.
    assert get_dictable_globals_or_none(host) is host_globals
    assert get_dictable_globals_or_none(host.Klass) is host_globals
    assert get_dictable_globals_or_none(host.func) is host_globals

    # Global scope of a class declared by *NO* module is "None".
    cls_moduleless = type('Moduleless', (), {'__module__': 'does_not_exist'})
    assert get_dictable_globals_or_none(cls_moduleless) is None

    # Global scope of an object defining *NO* global scope is "None".
    assert get_dictable_globals_or_none(len) is None
    assert reduce_dictable_pep810_lazy_globals_to_pep484_refs(len) is None

    # Global scopes without lazy imports have no lazy-free counterpart.
    assert reduce_dictable_pep810_lazy_globals_to_pep484_refs(
        test_pep810_getters) is None

    # Annotating callables whose __annotate__() dunder methods are not
    # introspectable functions silently defers to the standard getter. (Note
    # this *MUST* be tested before any lazy import is reified below.)
    assert get_hintable_pep649749_annotations_or_none(host.func_opaque) == {
        'arg': int, 'return': int}

    # Annotating callables unannotated by lazy imports but annotated by
    # unresolvable unquoted forward references defers to the standard getter.
    plain = ModuleType('beartype_test_plainhost810')
    monkeypatch.setitem(modules, plain.__name__, plain)
    exec(compile('def func(arg: Undefined): pass', '<plain>', 'exec'),
         plain.__dict__)
    assert get_hintable_pep649749_annotations_or_none(plain.func)['arg'] != int

    # Global scopes with lazy imports have a lazy-free counterpart; those
    # without have none.
    nonlazy = get_scope_nonlazy_or_none(host_globals)
    assert nonlazy is not None
    assert 'Target' not in nonlazy
    assert 'func' in nonlazy
    assert get_scope_nonlazy_or_none({'a': 1}) is None
    assert _TARGET_MODULE_NAME not in modules

    # Live global scopes defer to the real scope, reifying lazy imports only
    # when looked up.
    live = reduce_dictable_pep810_lazy_globals_to_pep484_refs(host.func)
    assert isinstance(live, Pep810LiveGlobals)
    assert dict.__contains__(live, 'func')
    assert not dict.__contains__(live, 'Target')
    assert 'Later' in live
    assert 'Target' in live
    assert 'nonexistent' not in live
    assert live.get('nonexistent', 'default') == 'default'
    assert live['Later'] is host.Later
    assert _TARGET_MODULE_NAME not in modules
    assert live['Target'].__name__ == 'Target'
    assert _TARGET_MODULE_NAME in modules
    with raises(KeyError):
        live['nonexistent']


    # Lazy imports are unsupported if the type of lazy imports is undefined.
    monkeypatch.setattr(pep810, 'LazyImportType', None)
    assert reduce_dictable_pep810_lazy_globals_to_pep484_refs(host.func) is None
    assert get_scope_nonlazy_or_none(host_globals) is None
