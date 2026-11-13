# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Sphinx configuration exercising runtime checks in an unnamed namespace.

Do not import this file as a module: Sphinx must execute it as ``conf.py``.
There is deliberately no future import, matching the original issue #487.
Explicit string annotations also exercise forward references on Sphinx versions
that do not implicitly enable postponed annotations.
'''

from pathlib import Path
from pytest import raises
from sphinx.application import Sphinx
from beartype import beartype
from beartype.roar import (
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
)

project = 'beartype_conf'
extensions = []
html_theme = 'basic'

# A named forward reference must resolve from the dynamically executed globals.
# Unlike the original None-only example, this failed before commit 729cee81.
ConfigPath = Path


@beartype
def checked_path(value: 'ConfigPath') -> 'Path':
    return value


@beartype
def checked_none() -> None:
    pass


@beartype
def checked_stringified_none() -> 'None':
    pass


@beartype
def unchecked_path() -> 'ConfigPath':
    return 'not a path'


assert checked_none() is None
assert checked_stringified_none() is None
assert checked_path(Path('conf.py')) == Path('conf.py')

with raises(BeartypeCallHintParamViolation):
    checked_path('not a path')

with raises(BeartypeCallHintReturnViolation):
    unchecked_path()


@beartype
def on_builder_inited(app: 'Sphinx') -> None:
    # The same checks must remain active after Sphinx has finished exec(conf.py).
    assert checked_path(Path(app.outdir)) == Path(app.outdir)
    with raises(BeartypeCallHintParamViolation):
        checked_path('not a path')
    with raises(BeartypeCallHintReturnViolation):
        unchecked_path()
    (Path(app.outdir) / 'beartype-conf-checked.txt').write_text('checked')


@beartype
def setup(app: 'Sphinx') -> None:
    app.connect('builder-inited', on_builder_inited)
