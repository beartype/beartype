#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype metadata API unit tests.**

This submodule unit tests the public API of the :mod:`beartype.meta` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_api_meta() -> None:
    '''
    Test the public API of the :mod:`beartype.meta` submodule.
    '''

    # Defer test-specific imports.
    from beartype import meta

    # Assert this submodule's public attributes to be of the expected types.
    assert isinstance(meta.NAME, str)
    assert isinstance(meta.PACKAGE_NAME, str)
    assert isinstance(meta.LICENSE, str)
    assert isinstance(meta.PYTHON_VERSION_MIN, str)
    assert isinstance(meta.PYTHON_VERSION_MINOR_MAX, int)
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
    assert isinstance(meta.LIBS_RUNTIME_OPTIONAL, tuple)
    assert isinstance(meta.LIBS_TESTTIME_MANDATORY, tuple)
    assert isinstance(meta.LIBS_TESTTIME_MANDATORY_TOX, tuple)
    assert isinstance(meta.LIBS_TESTTIME_OPTIONAL, tuple)
    assert isinstance(meta.LIBS_DOCTIME_MANDATORY, tuple)
    assert isinstance(meta.LIBS_DOCTIME_MANDATORY_RTD, tuple)
    assert isinstance(meta.LIBS_DEVELOPER_MANDATORY, tuple)
