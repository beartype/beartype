#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''Real-subprocess integration tests for PEP 420 namespace import hooks.'''

import pytest


@pytest.mark.parametrize('target', ('claw_namespace', 'claw_namespace.team._private'))
@pytest.mark.parametrize('reverse_roots', (False, True))
def test_claw_namespace_packages(tmp_path, target, reverse_roots) -> None:
    '''Hook deep namespaces across roots without replacing namespace semantics.'''
    from pathlib import Path
    from textwrap import dedent
    import beartype

    roots = [tmp_path / name for name in ('first', 'second', 'later')]
    module_source = dedent('''\
        def identity(value: int) -> int:
            return value

        def invalid_return() -> int:
            return 'not an integer'
    ''')
    for root, name in zip(roots, ('first', 'second', 'later')):
        directory = root / 'claw_namespace' / 'team' / '_private'
        directory.mkdir(parents=True)
        (directory / f'{name}.py').write_text(module_source, encoding='utf-8')

    # Both selected and excluded modules live under the same implicit package.
    (roots[0] / 'claw_namespace/team/_private/skipped.py').write_text(
        module_source, encoding='utf-8')
    (roots[0] / 'unselected.py').write_text(module_source, encoding='utf-8')
    initial_roots = roots[:2][::-1] if reverse_roots else roots[:2]
    script = dedent(f'''\
        import importlib
        import sys
        from pathlib import Path
        sys.path[:0] = {list(map(str, initial_roots))!r}
        import beartype
        assert str(Path(beartype.__file__).resolve()) == {str(Path(beartype.__file__).resolve())!r}
        from beartype import BeartypeConf
        from beartype.claw import beartype_package
        from beartype.roar import BeartypeCallHintParamViolation, BeartypeCallHintReturnViolation

        beartype_package({target!r}, conf=BeartypeConf(
            claw_skip_package_names=('claw_namespace.team._private.skipped',)))

        first = importlib.import_module('claw_namespace.team._private.first')
        second = importlib.import_module('claw_namespace.team._private.second')
        package = importlib.import_module('claw_namespace.team._private')
        assert package.__spec__.origin is None
        assert getattr(package, '__file__', None) is None
        assert list(package.__path__) == {list(map(lambda root: str(root / 'claw_namespace/team/_private'), initial_roots))!r}
        assert package.__spec__.submodule_search_locations is package.__path__

        # PEP 420 paths must still discover a new portion added after import.
        sys.path.append({str(roots[2])!r})
        importlib.invalidate_caches()
        later = importlib.import_module('claw_namespace.team._private.later')
        assert list(package.__path__)[-1] == {str(roots[2] / 'claw_namespace/team/_private')!r}
        for module in (first, second, later):
            assert module.identity(7) == 7
            try:
                module.identity('wrong')
            except BeartypeCallHintParamViolation:
                pass
            else:
                raise AssertionError('namespace callable parameter was not checked')
            try:
                module.invalid_return()
            except BeartypeCallHintReturnViolation:
                pass
            else:
                raise AssertionError('namespace callable return was not checked')

        for name in ('claw_namespace.team._private.skipped', 'unselected'):
            module = importlib.import_module(name)
            assert module.identity('unchecked') == 'unchecked'
            assert module.invalid_return() == 'not an integer'
        assert importlib.import_module(first.__name__) is first
    ''')
    # Fresh interpreters exercise cold compilation and reuse of generated pyc.
    _run_namespace_script(script, tmp_path)
    cache_files = tuple(tmp_path.rglob('*.pyc'))
    for root, name in zip(roots, ('first', 'second', 'later')):
        cache_dir = root / 'claw_namespace/team/_private/__pycache__'
        assert tuple(cache_dir.glob(f'{name}.*.pyc'))
    cached_before = {path: (path.read_bytes(), path.stat().st_mtime_ns)
                     for path in cache_files}
    _run_namespace_script(script, tmp_path)
    assert set(tmp_path.rglob('*.pyc')) == set(cache_files)
    assert {path: (path.read_bytes(), path.stat().st_mtime_ns)
            for path in cache_files} == cached_before


def test_claw_namespace_registration_order(tmp_path) -> None:
    '''Already-imported modules remain untouched; later namespace siblings hook.'''
    from textwrap import dedent

    directory = tmp_path / 'claw_order' / 'nested'
    directory.mkdir(parents=True)
    for name in ('before', 'after'):
        (directory / f'{name}.py').write_text(
            'def identity(value: int) -> int:\n    return value\n',
            encoding='utf-8')
    script = dedent(f'''\
        import importlib
        import sys
        sys.path.insert(0, {str(tmp_path)!r})
        before = importlib.import_module('claw_order.nested.before')
        from beartype.claw import beartype_package
        from beartype.roar import BeartypeCallHintParamViolation
        beartype_package('claw_order')
        after = importlib.import_module('claw_order.nested.after')
        assert before.identity('not retroactive') == 'not retroactive'
        assert importlib.import_module(before.__name__) is before
        assert after.identity(5) == 5
        try:
            after.identity('wrong')
        except BeartypeCallHintParamViolation:
            pass
        else:
            raise AssertionError('later namespace sibling was not checked')
    ''')
    _run_namespace_script(script, tmp_path)


def test_claw_namespace_regular_subpackage(tmp_path) -> None:
    '''A regular package inside namespace parents can register its own hook.'''
    from textwrap import dedent

    directory = tmp_path / 'claw_mixed' / 'team' / 'application'
    directory.mkdir(parents=True)
    (directory / '__init__.py').write_text(
        'from beartype.claw import beartype_this_package\n'
        'beartype_this_package()\n', encoding='utf-8')
    private = directory / '_private'
    private.mkdir()
    (private / 'library.py').write_text(
        'def identity(value: int) -> int:\n    return value\n',
        encoding='utf-8')
    script = dedent(f'''\
        import importlib
        import sys
        sys.path.insert(0, {str(tmp_path)!r})
        from beartype.roar import BeartypeCallHintParamViolation
        module = importlib.import_module('claw_mixed.team.application._private.library')
        assert module.identity(9) == 9
        try:
            module.identity('wrong')
        except BeartypeCallHintParamViolation:
            pass
        else:
            raise AssertionError('regular package hook did not cover namespace child')
        for name in ('claw_mixed', 'claw_mixed.team', 'claw_mixed.team.application._private'):
            assert importlib.import_module(name).__spec__.origin is None
        assert importlib.import_module('claw_mixed.team.application').__spec__.origin.endswith('__init__.py')
    ''')
    _run_namespace_script(script, tmp_path)


def _run_namespace_script(script, directory) -> None:
    '''Run only this fixture with the same interpreter and checkout as pytest.'''
    import os
    from pathlib import Path
    import subprocess
    import sys
    import beartype

    environment = os.environ.copy()
    environment.pop('PYTHONDONTWRITEBYTECODE', None)
    environment.pop('PYTHONPYCACHEPREFIX', None)
    environment['PYTHONPATH'] = str(Path(beartype.__file__).resolve().parent.parent)
    result = subprocess.run(
        [sys.executable, '-c',
         f'import sys; sys.path.insert(0, {environment["PYTHONPATH"]!r})\n' + script],
        cwd=directory, env=environment,
        capture_output=True, text=True, timeout=30, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
