#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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

# Arbitrary pure-Python generator.
def thou_hadst_a_voice():
    yield 'whose sound was like the sea:'

# ....................{ TESTS                             }....................
def test_get_func_codeobj() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj` function.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._cave._cavefast import CallableCodeObjectType
    from beartype._util.func.utilfunccodeobj import get_func_codeobj
    from pytest import raises

    # ..................{ UNWRAPPING ~ false                }..................
    # Instance of that class.
    fireside = OfStagnantWaters()

    # Assert this tester accepts pure-Python callables.
    the_heroic_wealth_of_hall_and_bower = get_func_codeobj(england_hath_need)
    assert isinstance(
        the_heroic_wealth_of_hall_and_bower, CallableCodeObjectType)
    assert isinstance(
        get_func_codeobj(fireside.altar), CallableCodeObjectType)

    # Assert this tester accepts pure-Python generators.
    assert isinstance(
        get_func_codeobj(thou_hadst_a_voice), CallableCodeObjectType)

    # Assert this tester also accepts code objects.
    assert get_func_codeobj(
        the_heroic_wealth_of_hall_and_bower) is (
        the_heroic_wealth_of_hall_and_bower)

    # Assert this tester rejects C-based callables.
    with raises(_BeartypeUtilCallableException):
        get_func_codeobj(iter)

    # ..................{ UNWRAPPING ~ true                 }..................
    # Assert this tester accepts pure-Python wrappee callables.
    the_heroic_wealth_of_hall_and_bower = get_func_codeobj(
        func=england_hath_need, is_unwrap=True)
    have_forfeited_their_ancient_english_dower = get_func_codeobj(
        func=fireside.altar, is_unwrap=True)
    assert isinstance(
        the_heroic_wealth_of_hall_and_bower, CallableCodeObjectType)
    assert isinstance(
        have_forfeited_their_ancient_english_dower, CallableCodeObjectType)

    # Assert this tester accepts pure-Python wrapper callables.
    assert (
        get_func_codeobj(func=we_are_selfish_men, is_unwrap=True) is
        get_func_codeobj(func=england_hath_need, is_unwrap=False)
    )
    assert get_func_codeobj(
        func=fireside.and_give_us_manners_virtue_freedom_power,
        is_unwrap=True
    ) is get_func_codeobj(func=fireside.altar, is_unwrap=False)

    # Assert this tester also accepts code objects.
    assert get_func_codeobj(
        the_heroic_wealth_of_hall_and_bower, is_unwrap=True) is (
        the_heroic_wealth_of_hall_and_bower)

    # Assert this tester rejects C-based callables.
    with raises(_BeartypeUtilCallableException):
        get_func_codeobj(iter, is_unwrap=True)


def test_get_func_codeobj_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj_or_none`
    function.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._cave._cavefast import CallableCodeObjectType
    from beartype._util.func.utilfunccodeobj import get_func_codeobj_or_none

    # ..................{ UNWRAPPING ~ false                }..................
    # Instance of that class.
    fireside = OfStagnantWaters()

    # Assert this tester accepts pure-Python non-generator callables.
    the_heroic_wealth_of_hall_and_bower = get_func_codeobj_or_none(
        england_hath_need)
    assert isinstance(
        the_heroic_wealth_of_hall_and_bower, CallableCodeObjectType)
    assert isinstance(
        get_func_codeobj_or_none(fireside.altar), CallableCodeObjectType)

    # Assert this tester accepts pure-Python generators.
    assert isinstance(
        get_func_codeobj_or_none(thou_hadst_a_voice), CallableCodeObjectType)

    # Assert this tester also accepts code objects.
    assert get_func_codeobj_or_none(
        the_heroic_wealth_of_hall_and_bower) is (
        the_heroic_wealth_of_hall_and_bower)

    # Assert this tester rejects C-based builtins.
    assert get_func_codeobj_or_none(iter) is None

    # ..................{ UNWRAPPING ~ true                 }..................
    # Assert this tester accepts pure-Python wrappee callables.
    the_heroic_wealth_of_hall_and_bower = get_func_codeobj_or_none(
        func=england_hath_need, is_unwrap=True)
    have_forfeited_their_ancient_english_dower = get_func_codeobj_or_none(
        func=fireside.altar, is_unwrap=True)
    assert isinstance(
        the_heroic_wealth_of_hall_and_bower, CallableCodeObjectType)
    assert isinstance(
        have_forfeited_their_ancient_english_dower, CallableCodeObjectType)

    # Assert this tester accepts pure-Python wrapper callables.
    assert (
        get_func_codeobj_or_none(we_are_selfish_men, is_unwrap=True) is
        get_func_codeobj_or_none(england_hath_need, is_unwrap=False)
    )
    assert get_func_codeobj_or_none(
        func=fireside.and_give_us_manners_virtue_freedom_power,
        is_unwrap=True,
    ) is get_func_codeobj_or_none(fireside.altar, is_unwrap=False)

    # Assert this tester also accepts code objects.
    assert get_func_codeobj_or_none(
        func=the_heroic_wealth_of_hall_and_bower, is_unwrap=True) is (
        the_heroic_wealth_of_hall_and_bower)

    # Assert this tester rejects C-based builtins.
    assert get_func_codeobj_or_none(iter, is_unwrap=True) is None
