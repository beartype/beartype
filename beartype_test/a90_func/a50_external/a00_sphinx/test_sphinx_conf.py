#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Sphinx configuration integration tests.

This submodule functionally tests the :func:`beartype.beartype` decorator with
respect to the third-party Sphinx documentation build toolchain.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import mark
from beartype_test._util.mark.pytskip import skip_unless_package

# Keep these fixtures local to this module so that deleting the legacy Sphinx
# conftest.py does not disable the conf.py regression test.
try:
    from sphinx.testing.fixtures import make_app, test_params
except ImportError:
    pass

# ....................{ TESTS                              }....................
# Keep compatibility with Sphinx 5.x while the doc-rtd extra requires Sphinx
# < 6 and the dev extra includes doc-rtd. This lets this regression test merge
# before the legacy documentation is removed. Once the following PR removes
# those dependencies, this warning filter and the legacy path conversion below
# can be removed:
#     https://github.com/beartype/beartype/pull/722
# Sphinx 5.x imports imghdr, deprecated in Python 3.11.
@mark.filterwarnings(
    "ignore:^'imghdr' is deprecated and slated for removal in Python 3\\.13$:"
    "DeprecationWarning:^sphinx\\.util\\.images$")
@skip_unless_package('sphinx')
def test_sphinx_conf(make_app, tmp_path) -> None:
    '''
    Sphinx builds documentation with type-checked ``conf.py`` functions.

    Exercise the unnamed namespace in which Sphinx executes ``conf.py`` through
    an actual HTML build, including runtime checks in a Sphinx event callback.
    See https://github.com/beartype/beartype/issues/487.
    '''

    # Defer test-specific imports.
    from io import StringIO
    from pathlib import Path
    from shutil import copytree
    from sphinx import version_info
    from beartype_test._util.path.pytpathtest import (
        get_test_func_data_external_dir)

    # SphinxTestApp builds beneath its source directory by default. Copy the
    # document tree so that all build artifacts remain in the temporary tree.
    source_dir = tmp_path / 'source'
    copytree(get_test_func_data_external_dir() / 'sphinx_conf', source_dir)

    # Sphinx < 7.2 requires its legacy path type rather than pathlib.Path.
    if version_info < (7, 2):
        from sphinx.testing.path import path
        source_dir = path(str(source_dir))

    warnings = StringIO()
    app = make_app(
        srcdir=source_dir,
        buildername='html',
        freshenv=True,
        warning=warnings,
    )
    app.build()

    assert app.statuscode == 0
    # Checking the captured warnings also supports older SphinxTestApp versions
    # that do not accept the warningiserror keyword argument.
    assert warnings.getvalue() == ''
    output_dir = Path(app.outdir)

    # The marker proves that Sphinx invoked the decorated callback and that its
    # runtime checks ran, rather than merely accepting the configuration.
    assert (output_dir / 'beartype-conf-checked.txt').read_text() == 'checked'
    assert (output_dir / 'index.html').is_file()
