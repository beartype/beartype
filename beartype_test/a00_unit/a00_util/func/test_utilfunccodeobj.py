#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable code object utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfunccodeobj` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ DATA                              }....................
# Arbitrary pure-Python function.
def england_hath_need(of_thee: int, she_is_a_fen: int) -> int:
    return of_thee + she_is_a_fen

# Arbitrary pure-Python class.
class of_stagnant_waters(object):
    # Arbitrary pure-Python method.
    def altar(self, sword: str, and_pen: str) -> str:
        return sword + and_pen

# ....................{ TESTS                             }....................
def test_get_func_codeobj() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfunccodeobj import get_func_codeobj
    from beartype.cave import CallableCodeObjectType
    from beartype.roar import _BeartypeUtilCallableException

    # Instance of this class.
    fireside = of_stagnant_waters()

    # Assert this tester accepts pure-Python callables.
    assert isinstance(
        get_func_codeobj(england_hath_need), CallableCodeObjectType)
    assert isinstance(
        get_func_codeobj(fireside.altar), CallableCodeObjectType)

    # Assert this tester rejects C-based callables.
    with raises(_BeartypeUtilCallableException):
        get_func_codeobj(iter)


def test_get_func_codeobj_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj_or_none`
    function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfunccodeobj import get_func_codeobj_or_none
    from beartype.cave import CallableCodeObjectType
    from beartype.roar import _BeartypeUtilCallableException

    # Instance of this class.
    fireside = of_stagnant_waters()

    # Assert this tester accepts pure-Python callables.
    assert isinstance(
        get_func_codeobj_or_none(england_hath_need), CallableCodeObjectType)
    assert isinstance(
        get_func_codeobj_or_none(fireside.altar), CallableCodeObjectType)

    # Assert this tester rejects C-based builtins.
    assert get_func_codeobj_or_none(iter) is None
