#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`pyinstaller` integration tests.

This submodule functionally tests the third-party PyInstaller fromework
successfully generates executable binaries containing arbitrary modules
registering :mod:`beartype.claw` import hooks.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('pyinstaller')
def test_pyinstaller(
    monkeypatch: 'pytest.MonkeyPatch', tmp_path: 'pathlib.Path') -> None:
    '''
    Integration test validating that the :mod:`beartype` package raises *no*
    unexpected exceptions when an arbitrary package bundled by the third-party
    PyInstaller framework into an exogenous executable binary registers a
    :mod:`beartype.claw` import hook, which conflicts with a competing
    PyInstaller-specific import hook required by PyInstaller to generate
    working binaries.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        :mod:`pytest` fixture allowing various state associated with the active
        Python process to be temporarily changed for the duration of this test.
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this test,
        created in the base temporary directory.

    See Also
    --------
    https://github.com/beartype/beartype/issues/599
        Non-trivial issue resolved by this test.
    https://github.com/zbowling/beartype-pyinstaller-repro
        Non-trivial minimal-length example strongly inspiring this test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.

    # ....................{ LOCALS                         }....................
