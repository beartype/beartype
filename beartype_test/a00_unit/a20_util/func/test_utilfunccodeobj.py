#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable code object utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfunccodeobj` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from functools import wraps

# ....................{ DATA                               }....................
#FIXME: Refactor as follows for sanity, please
#* Shift into the "beartype_test.a00_unit.data.data_type" submodule.
#* Rename this class to something suitably generic -- say, "ClassWithWrappers".
#  Or perhaps just shift these methods into an existing class of that submodule?
#* Import this class into tests below.

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

# ....................{ TESTS                              }....................
def test_get_func_codeobj() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj` function.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._cave._cavefast import CallableCodeObjectType
    from beartype._util.func.utilfunccodeobj import get_func_codeobj
    from beartype_test.a00_unit.data.data_type import (
        function,
        sync_generator_factory,
        wrapper_isomorphic,
    )
    from pytest import raises

    # ..................{ UNWRAPPING ~ false                 }..................
    # Instance of that class.
    fireside = OfStagnantWaters()

    # Assert this tester accepts pure-Python callables.
    function_codeobj = get_func_codeobj(function)
    assert isinstance(function_codeobj, CallableCodeObjectType)
    assert isinstance(get_func_codeobj(fireside.altar), CallableCodeObjectType)

    # Assert this tester accepts pure-Python generators.
    assert isinstance(
        get_func_codeobj(sync_generator_factory), CallableCodeObjectType)

    # Assert this tester also accepts code objects.
    assert get_func_codeobj(function_codeobj) is function_codeobj

    # Assert this tester rejects C-based callables.
    with raises(_BeartypeUtilCallableException):
        get_func_codeobj(iter)

    # ..................{ UNWRAPPING ~ true                  }..................
    # Assert this tester accepts pure-Python wrappee callables.
    function_codeobj = get_func_codeobj(
        func=function, is_unwrap=True)
    have_forfeited_their_ancient_english_dower = get_func_codeobj(
        func=fireside.altar, is_unwrap=True)
    assert isinstance(
        function_codeobj, CallableCodeObjectType)
    assert isinstance(
        have_forfeited_their_ancient_english_dower, CallableCodeObjectType)

    # Assert this tester accepts pure-Python wrapper callables.
    assert (
        get_func_codeobj(func=wrapper_isomorphic, is_unwrap=True) is
        get_func_codeobj(func=function, is_unwrap=False)
    )
    assert get_func_codeobj(
        func=fireside.and_give_us_manners_virtue_freedom_power,
        is_unwrap=True
    ) is get_func_codeobj(func=fireside.altar, is_unwrap=False)

    # Assert this tester also accepts code objects.
    assert get_func_codeobj(
        function_codeobj, is_unwrap=True) is function_codeobj

    # Assert this tester rejects C-based callables.
    with raises(_BeartypeUtilCallableException):
        get_func_codeobj(iter, is_unwrap=True)


def test_get_func_codeobj_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj_or_none`
    function.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._cave._cavefast import CallableCodeObjectType
    from beartype._util.func.utilfunccodeobj import get_func_codeobj_or_none
    from beartype_test.a00_unit.data.data_type import (
        function,
        sync_generator_factory,
        wrapper_isomorphic,
    )

    # ..................{ UNWRAPPING ~ false                 }..................
    # Instance of that class.
    fireside = OfStagnantWaters()

    # Assert this tester accepts pure-Python non-generator callables.
    function_codeobj = get_func_codeobj_or_none(function)
    assert isinstance(function_codeobj, CallableCodeObjectType)
    assert isinstance(
        get_func_codeobj_or_none(fireside.altar), CallableCodeObjectType)

    # Assert this tester accepts pure-Python generators.
    assert isinstance(
        get_func_codeobj_or_none(sync_generator_factory),
        CallableCodeObjectType,
    )

    # Assert this tester also accepts code objects.
    assert get_func_codeobj_or_none(function_codeobj) is function_codeobj

    # Assert this tester rejects C-based builtins.
    assert get_func_codeobj_or_none(iter) is None

    # ..................{ UNWRAPPING ~ true                  }..................
    # Assert this tester accepts pure-Python wrappee callables.
    function_codeobj = get_func_codeobj_or_none(
        func=function, is_unwrap=True)
    have_forfeited_their_ancient_english_dower = get_func_codeobj_or_none(
        func=fireside.altar, is_unwrap=True)
    assert isinstance(function_codeobj, CallableCodeObjectType)
    assert isinstance(
        have_forfeited_their_ancient_english_dower, CallableCodeObjectType)

    # Assert this tester accepts pure-Python wrapper callables.
    assert (
        get_func_codeobj_or_none(wrapper_isomorphic, is_unwrap=True) is
        get_func_codeobj_or_none(function, is_unwrap=False)
    )
    assert get_func_codeobj_or_none(
        func=fireside.and_give_us_manners_virtue_freedom_power,
        is_unwrap=True,
    ) is get_func_codeobj_or_none(fireside.altar, is_unwrap=False)

    # Assert this tester also accepts code objects.
    assert get_func_codeobj_or_none(
        func=function_codeobj, is_unwrap=True) is function_codeobj

    # Assert this tester rejects C-based builtins.
    assert get_func_codeobj_or_none(iter, is_unwrap=True) is None
