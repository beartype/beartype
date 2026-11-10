#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :mod:`beartype.claw` ``if TYPE_CHECKING:`` unit tests.

This submodule unit tests the transformation of :pep:`484`-compliant
``if TYPE_CHECKING:`` blocks by :mod:`beartype.claw` import hooks.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ PRIVATE ~ globals                  }....................
_MODULE_SOURCE = '''
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fractions import Fraction
    import decimal
    x = 1
else:
    y = 2

if not TYPE_CHECKING:
    import this_is_untouched
'''

_PACKAGE_MODULE_SOURCE = '''
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fractions import Fraction

def func(arg: Fraction) -> Fraction:
    return arg
'''

# ....................{ PRIVATE ~ helpers                  }....................
def _transform(source: str) -> str:
    '''
    Source code transformed from the passed source code by the
    :mod:`beartype.claw` AST transformer.
    '''

    # Defer test-specific imports.
    from ast import (
        fix_missing_locations,
        parse,
        unparse,
    )
    from beartype import BeartypeConf
    from beartype.claw._ast.clawastmain import BeartypeNodeTransformer

    node = BeartypeNodeTransformer(
        module_name='muh_module', conf=BeartypeConf()).visit(parse(source))
    return unparse(fix_missing_locations(node))

# ....................{ TESTS                              }....................
def test_claw_type_checking_warn(monkeypatch) -> None:
    '''
    Test that :mod:`beartype.claw` warns about, but preserves as is, imports in
    ``if TYPE_CHECKING:`` blocks when lazy imports are unavailable.
    '''

    # Defer test-specific imports.
    from ast import parse, unparse
    from beartype.roar import BeartypeClawTypeCheckingWarning
    from beartype.claw._ast._kind import clawastif
    from pytest import warns

    # Pretend the active Python interpreter lacks lazy imports.
    monkeypatch.setattr(clawastif, 'IS_PYTHON_AT_LEAST_3_15', False)

    # Assert one warning is issued for the one such block and that the source
    # code is otherwise preserved.
    with warns(BeartypeClawTypeCheckingWarning, match='PEP 810'):
        source_new = _transform(_MODULE_SOURCE)
    assert unparse(parse(_MODULE_SOURCE)) in source_new
    assert 'lazy' not in source_new


@skip_if_python_version_less_than('3.15.0')
def test_claw_type_checking_lazy() -> None:
    '''
    Test that :mod:`beartype.claw` hoists imports in ``if TYPE_CHECKING:``
    blocks as :pep:`810`-compliant lazy imports under Python >= 3.15.
    '''

    # Defer test-specific imports.
    from warnings import catch_warnings, simplefilter

    # Transform this source code, asserting no warnings are issued.
    with catch_warnings():
        simplefilter('error')
        source_new = _transform(_MODULE_SOURCE)

    # Assert these imports were hoisted as lazy imports, that the remainder of
    # this block (including its "else" branch) was preserved, and that a block
    # testing something else was untouched.
    assert 'lazy from fractions import Fraction' in source_new
    assert 'lazy import decimal' in source_new
    assert 'if TYPE_CHECKING:\n    x = 1\nelse:\n    y = 2' in source_new
    assert 'import this_is_untouched' in source_new
    assert 'lazy import this_is_untouched' not in source_new

    # Assert a block containing only imports is removed entirely.
    source_new = _transform(
        'from typing import TYPE_CHECKING\n'
        'if TYPE_CHECKING:\n    from fractions import Fraction\n')
    assert 'lazy from fractions import Fraction' in source_new
    assert 'if TYPE_CHECKING' not in source_new

    # Assert a block containing only imports and an "else" branch preserves
    # that branch (under an otherwise empty block).
    source_new = _transform(
        'from typing import TYPE_CHECKING\n'
        'if TYPE_CHECKING:\n    from fractions import Fraction\n'
        'else:\n    Fraction = None\n')
    assert 'lazy from fractions import Fraction' in source_new
    assert 'if TYPE_CHECKING:\n    pass\nelse:\n    Fraction = None' in (
        source_new)

    # Assert star imports (which cannot be lazy) are preserved with a warning.
    from beartype.roar import BeartypeClawTypeCheckingWarning
    from pytest import warns
    with warns(BeartypeClawTypeCheckingWarning):
        source_new = _transform(
            'from typing import TYPE_CHECKING\n'
            'if TYPE_CHECKING:\n    from fractions import *\n')
    assert 'lazy' not in source_new


@skip_if_python_version_less_than('3.15.0')
def test_claw_type_checking_lazy_import_hook(tmp_path) -> None:
    '''
    Test that a :mod:`beartype.claw` import hook transparently supports
    stringified type hints imported in ``if TYPE_CHECKING:`` blocks while
    preserving the laziness of those imports until first type-checked.
    '''

    # Defer test-specific imports.
    import beartype
    from os import environ
    from pathlib import Path
    from subprocess import run
    from sys import executable

    # Package importable by the script below.
    package_dir = tmp_path / 'tcpkg'
    package_dir.mkdir()
    (package_dir / '__init__.py').write_text('', encoding='utf-8')
    (package_dir / 'mod.py').write_text(_PACKAGE_MODULE_SOURCE, encoding='utf-8')

    # Script installing the import hook and importing that package.
    script_path = tmp_path / 'run.py'
    script_path.write_text(
        'import sys\n'
        'from beartype.claw import beartype_package\n'
        'from beartype.roar import BeartypeCallHintParamViolation\n'
        "beartype_package('tcpkg')\n"
        'import tcpkg.mod\n'
        "assert 'fractions' not in sys.modules\n"
        'from fractions import Fraction\n'
        'half = Fraction(1, 2)\n'
        'assert tcpkg.mod.func(half) == half\n'
        'try:\n'
        '    tcpkg.mod.func(1)\n'
        'except BeartypeCallHintParamViolation:\n'
        '    print("OK")\n',
        encoding='utf-8',
    )

    # Run this script with this repository and package importable.
    repo_dir = str(Path(beartype.__file__).parent.parent)
    result = run(
        [executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
        env={**environ, 'PYTHONPATH': repo_dir + ';' + str(tmp_path)},
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'OK'
