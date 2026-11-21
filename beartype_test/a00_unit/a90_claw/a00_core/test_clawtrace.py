#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''Real isolated import tracing tests, without multiprocessing.'''


def _run(tmp_path, script):
    import os
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[4]
    return subprocess.run(
        [sys.executable, '-c', script], cwd=tmp_path,
        env={**os.environ, 'PYTHONPATH': str(root) + os.pathsep + str(tmp_path)},
        text=True, capture_output=True, check=True,
    )


def _package(tmp_path, name, files):
    package = tmp_path / name
    package.mkdir()
    (package / '__init__.py').write_text('', encoding='utf-8')
    for filename, source in files.items():
        (package / filename).write_text(source, encoding='utf-8')


def test_claw_trace_cold_and_warm(tmp_path) -> None:
    _package(tmp_path, 'tracepkg', {
        'child.py': 'import sys\nprint("BODY", file=sys.stderr)\n'
                    'def checked(value: int) -> int:\n    return value\n',
        'hidden.py': 'def unchecked(value: int):\n    return value\n',
    })
    script = '''
from beartype import BeartypeConf
from beartype.claw import beartype_package
from beartype.roar import BeartypeCallHintParamViolation
beartype_package('tracepkg', conf=BeartypeConf(
    claw_is_trace_imports=True, claw_skip_package_names=('tracepkg.hidden',)))
{warm_guard}
import tracepkg.child
import tracepkg.hidden
assert tracepkg.child.checked(1) == 1
try:
    tracepkg.child.checked('bad')
except BeartypeCallHintParamViolation:
    pass
else:
    raise AssertionError('hook did not type-check')
assert tracepkg.hidden.unchecked('bad') == 'bad'
import tracepkg.child  # sys.modules cache must not trace a second time.
'''
    cold = _run(tmp_path, script.format(warm_guard=''))
    expected = [
        '[beartype.claw] Type-checking module tracepkg.',
        '[beartype.claw] Type-checking module tracepkg.child.',
        'BODY',
    ]
    assert cold.stderr.splitlines() == expected
    assert cold.stdout == ''
    assert list((tmp_path / 'tracepkg' / '__pycache__').glob('*.pyc'))
    warm_guard = '''
from beartype.claw._importlib._clawimpfileloader import BeartypeSourceFileLoader
original = BeartypeSourceFileLoader.source_to_code
def reject_compile(self, *args, **kwargs):
    if self._module_name and self._module_name.startswith('tracepkg'):
        raise AssertionError('warm import unexpectedly compiled source')
    return original(self, *args, **kwargs)
BeartypeSourceFileLoader.source_to_code = reject_compile
'''
    warm = _run(tmp_path, script.format(warm_guard=warm_guard))
    assert warm.stderr.splitlines() == expected
    assert warm.stdout == ''


def test_claw_trace_default_and_mixed_configs(tmp_path) -> None:
    for name in ('silentpkg', 'loudpkg', 'unhookedpkg'):
        _package(tmp_path, name, {'child.py': 'value: int = 1\n'})
    result = _run(tmp_path, '''
import contextlib
import io
from beartype import BeartypeConf
from beartype.claw import beartype_package
beartype_package('silentpkg')
beartype_package('loudpkg', conf=BeartypeConf(claw_is_trace_imports=True))
class Stream(io.StringIO):
    flush_count = 0
    def flush(self):
        self.flush_count += 1
        return super().flush()
stream = Stream()
with contextlib.redirect_stderr(stream):
    import silentpkg.child
    import loudpkg.child
    import unhookedpkg.child
assert stream.getvalue().splitlines() == [
    '[beartype.claw] Type-checking module loudpkg.',
    '[beartype.claw] Type-checking module loudpkg.child.',
]
assert stream.flush_count == 2
''')
    assert result.stderr == result.stdout == ''


def test_claw_trace_import_errors(tmp_path) -> None:
    _package(tmp_path, 'brokenpkg', {
        'syntax.py': 'def invalid(:\n',
        'runtime.py': 'raise RuntimeError("original failure")\n',
    })
    result = _run(tmp_path, '''
import importlib
from beartype import BeartypeConf
from beartype.claw import beartype_package
beartype_package('brokenpkg', conf=BeartypeConf(claw_is_trace_imports=True))
for name, exception in [('syntax', SyntaxError), ('runtime', RuntimeError)]:
    try:
        importlib.import_module('brokenpkg.' + name)
    except exception as error:
        if name == 'runtime':
            assert str(error) == 'original failure'
    else:
        raise AssertionError('import error was swallowed')
''')
    assert result.stdout == ''
    assert result.stderr.splitlines() == [
        '[beartype.claw] Type-checking module brokenpkg.',
        '[beartype.claw] Type-checking module brokenpkg.syntax.',
        '[beartype.claw] Type-checking module brokenpkg.runtime.',
    ]


def test_claw_trace_without_stderr(tmp_path) -> None:
    _package(tmp_path, 'nostderrpkg', {'child.py': 'value: int = 1\n'})
    result = _run(tmp_path, """
import sys
from beartype import BeartypeConf
from beartype.claw import beartype_package
beartype_package('nostderrpkg', conf=BeartypeConf(claw_is_trace_imports=True))
sys.stderr = None
import nostderrpkg.child
assert nostderrpkg.child.value == 1
""")
    assert result.stdout == result.stderr == ''
