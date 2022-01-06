#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant **class-specific utility function** unit
tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cls.pep.utilpep557` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_is_type_pep557() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.utilpep557.is_type_pep557` tester.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilTypeException
    from beartype._util.cls.pep.utilpep557 import is_type_pep557
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from pytest import raises

    # Assert this tester raises the expected exception when passed a non-type.
    with raises(_BeartypeUtilTypeException):
        is_type_pep557('The wilderness has a mysterious tongue')

    # Assert this tester returns false when passed a non-dataclass type.
    assert is_type_pep557(str) is False

    # If the active Python interpreter targets Python >= 3.8 and thus supports
    # PEP 557-compliant dataclasses...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from dataclasses import dataclass

        # Arbitrary dataclass.
        @dataclass
        class WhichTeachesAwfulDoubtOrFaithSoMild(object): pass

        # Assert this tester returns true when passed a dataclass type.
        assert is_type_pep557(WhichTeachesAwfulDoubtOrFaithSoMild) is True
