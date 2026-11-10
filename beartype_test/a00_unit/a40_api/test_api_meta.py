#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Package metadata API** unit tests.

This submodule unit tests the public API of the :mod:`beartype.meta` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_api_meta() -> None:
    '''
    Test the public API of the :mod:`beartype.meta` submodule.
    '''

    # Defer test-specific imports.
    from beartype import meta
    from importlib.metadata import (
        PackageNotFoundError,
        metadata,
    )
    from pytest import skip

    # If this package is not installed (e.g., because tests are being run
    # directly from a source checkout), no distribution metadata exists for the
    # beartype.meta submodule to introspect. In this case, that submodule
    # intentionally falls back to "None" for metadata-derived attributes (e.g.,
    # "PYTHON_VERSION_MIN"), which this test cannot meaningfully validate.
    try:
        metadata(meta.PACKAGE_NAME)
    except PackageNotFoundError:
        skip(
            f'Package "{meta.PACKAGE_NAME}" not installed '
            f'(e.g., via "pip install -e .").'
        )

    # Assert this submodule's public attributes to be of the expected types.
    assert isinstance(meta.NAME, str)
    assert isinstance(meta.PACKAGE_NAME, str)
    assert isinstance(meta.LICENSE, str)
    assert isinstance(meta.PYTHON_VERSION_MIN, str)
    assert isinstance(meta.PYTHON_VERSION_MIN_PARTS, tuple)
    assert isinstance(meta.VERSION, str)
    assert isinstance(meta.VERSION_PARTS, tuple)
    assert isinstance(meta.SYNOPSIS, str)
    assert isinstance(meta.AUTHORS, str)
    assert isinstance(meta.AUTHOR_EMAIL, str)
    assert isinstance(meta.COPYRIGHT, str)
    assert isinstance(meta.URL_HOMEPAGE, str)
    assert isinstance(meta.URL_DOWNLOAD, str)
    assert isinstance(meta.URL_ISSUES, str)
