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

# ....................{ CONSTANTS                          }....................
_MODULE_SOURCE = '''
import sys
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation

# Standard module that neither @beartype nor this script otherwise imports.
lazy from fractions import Fraction

@beartype
def func(arg: Fraction) -> Fraction:
    return arg

@beartype
def func_nested(arg: list[Fraction] | None, other: Later) -> int:
    return len(arg or ())

@beartype
class Klass(object):
    def method(self, arg: Fraction) -> Fraction:
        return arg

class Later(object):
    pass

# Decoration alone *MUST* preserve the laziness of this import.
assert 'fractions' not in sys.modules, 'Decoration reified lazy import.'

# Calling a decorated callable *MUST* reify this import to type-check it.
from fractions import Fraction as RealFraction
half = RealFraction(1, 2)
assert func(half) == half
assert Klass().method(half) == half
assert func_nested([half], Later()) == 1
assert func_nested(None, Later()) == 0

for bad in (
    lambda: func(1),
    lambda: Klass().method('a'),
    lambda: func_nested([1], Later()),
    lambda: func_nested(None, 'not Later'),
):
    try:
        bad()
    except BeartypeCallHintParamViolation:
        pass
    else:
        raise AssertionError('No violation raised.')
print('OK')
'''

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.15.0')
def test_decor_pep810(tmp_path) -> None:
    '''
    Test :pep:`810` support implemented in the :func:`beartype.beartype`
    decorator, validating that decorating callables annotated by lazily
    imported type hints preserves the laziness of those imports.
    '''

    # Defer test-specific imports.
    import beartype
    from os import environ
    from pathlib import Path
    from subprocess import run
    from sys import executable

    # Script exercising lazy imports, run in a subprocess for isolation from
    # the already imported modules of this test suite.
    script_path = tmp_path / 'lazy_script.py'
    script_path.write_text(_MODULE_SOURCE, encoding='utf-8')

    # Run this script with the main directory of this repository importable.
    result = run(
        [executable, str(script_path)],
        capture_output=True,
        text=True,
        env={**environ, 'PYTHONPATH': str(Path(beartype.__file__).parent.parent)},
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'OK'
