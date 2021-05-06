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
from functools import wraps
from pytest import raises

# ....................{ DATA                              }....................
# Arbitrary pure-Python wrappee function.
def england_hath_need(of_thee: int, she_is_a_fen: int) -> int:
    return of_thee + she_is_a_fen

# Arbitrary pure-Python wrapper function.
@wraps(england_hath_need)
def we_are_selfish_men(*args, **kwargs) -> int:
    return england_hath_need(*args, **kwargs)

# Arbitrary pure-Python class.
class OfStagnantWaters(object):
    # Arbitrary pure-Python wrappee method.
    def altar(self, sword: str, and_pen: str) -> str:
        return sword + and_pen

    # Arbitrary pure-Python wrappee method.
    @wraps(altar)
    def and_give_us_manners_virtue_freedom_power(
        self, *args, **kwargs) -> str:
        return self.altar(*args, **kwargs)

# ....................{ TESTS                             }....................
def test_get_func_codeobj() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfunccodeobj import get_func_codeobj
    from beartype._cave._cavefast import CallableCodeObjectType

    # Instance of that class.
    fireside = OfStagnantWaters()

    # Assert this tester accepts pure-Python callables.
    the_heroic_wealth_of_hall_and_bower = get_func_codeobj(england_hath_need)
    assert isinstance(
        the_heroic_wealth_of_hall_and_bower, CallableCodeObjectType)
    assert isinstance(
        get_func_codeobj(fireside.altar), CallableCodeObjectType)

    # Assert this tester also accepts code objects.
    assert get_func_codeobj(
        the_heroic_wealth_of_hall_and_bower) is (
        the_heroic_wealth_of_hall_and_bower)

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
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfunccodeobj import get_func_codeobj_or_none
    from beartype._cave._cavefast import CallableCodeObjectType

    # Instance of that class.
    fireside = OfStagnantWaters()

    # Assert this tester accepts pure-Python callables.
    the_heroic_wealth_of_hall_and_bower = get_func_codeobj_or_none(
        england_hath_need)
    assert isinstance(
        the_heroic_wealth_of_hall_and_bower, CallableCodeObjectType)
    assert isinstance(
        get_func_codeobj_or_none(fireside.altar), CallableCodeObjectType)

    # Assert this tester also accepts code objects.
    assert get_func_codeobj_or_none(
        the_heroic_wealth_of_hall_and_bower) is (
        the_heroic_wealth_of_hall_and_bower)

    # Assert this tester rejects C-based builtins.
    assert get_func_codeobj_or_none(iter) is None

# ....................{ TESTS ~ unwrapped                 }....................
def test_get_func_unwrapped_codeobj() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunccodeobj.get_func_unwrapped_codeobj`
    function.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfunccodeobj import (
        get_func_codeobj,
        get_func_unwrapped_codeobj,
    )
    from beartype._cave._cavefast import CallableCodeObjectType

    # Instance of that class.
    fireside = OfStagnantWaters()

    # Assert this tester accepts pure-Python wrappee callables.
    the_heroic_wealth_of_hall_and_bower = get_func_unwrapped_codeobj(
        england_hath_need)
    have_forfeited_their_ancient_english_dower = get_func_unwrapped_codeobj(
        fireside.altar)
    assert isinstance(
        the_heroic_wealth_of_hall_and_bower, CallableCodeObjectType)
    assert isinstance(
        have_forfeited_their_ancient_english_dower, CallableCodeObjectType)

    # Assert this tester accepts pure-Python wrapper callables.
    assert (
        get_func_unwrapped_codeobj(we_are_selfish_men) is
        get_func_codeobj(england_hath_need)
    )
    assert (
        get_func_unwrapped_codeobj(
            fireside.and_give_us_manners_virtue_freedom_power) is
        get_func_codeobj(fireside.altar)
    )

    # Assert this tester also accepts code objects.
    assert get_func_unwrapped_codeobj(
        the_heroic_wealth_of_hall_and_bower) is (
        the_heroic_wealth_of_hall_and_bower)

    # Assert this tester rejects C-based callables.
    with raises(_BeartypeUtilCallableException):
        get_func_unwrapped_codeobj(iter)


def test_get_func_unwrapped_codeobj_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunccodeobj.get_func_unwrapped_codeobj_or_none`
    function.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfunccodeobj import (
        get_func_codeobj_or_none,
        get_func_unwrapped_codeobj_or_none,
    )
    from beartype._cave._cavefast import CallableCodeObjectType

    # Instance of that class.
    fireside = OfStagnantWaters()

    # Assert this tester accepts pure-Python wrappee callables.
    the_heroic_wealth_of_hall_and_bower = get_func_unwrapped_codeobj_or_none(
        england_hath_need)
    have_forfeited_their_ancient_english_dower = (
        get_func_unwrapped_codeobj_or_none(fireside.altar))
    assert isinstance(
        the_heroic_wealth_of_hall_and_bower, CallableCodeObjectType)
    assert isinstance(
        have_forfeited_their_ancient_english_dower, CallableCodeObjectType)

    # Assert this tester accepts pure-Python wrapper callables.
    assert (
        get_func_unwrapped_codeobj_or_none(we_are_selfish_men) is
        get_func_codeobj_or_none(england_hath_need)
    )
    assert (
        get_func_unwrapped_codeobj_or_none(
            fireside.and_give_us_manners_virtue_freedom_power) is
        get_func_codeobj_or_none(fireside.altar)
    )

    # Assert this tester also accepts code objects.
    assert get_func_unwrapped_codeobj_or_none(
        the_heroic_wealth_of_hall_and_bower) is (
        the_heroic_wealth_of_hall_and_bower)

    # Assert this tester rejects C-based builtins.
    assert get_func_unwrapped_codeobj_or_none(iter) is None
