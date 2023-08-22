#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartypistry unit tests.**

This submodule unit tests the
:attr:`beartype._check.forward.fwdtype.bear_typistry` singleton.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ singleton                  }....................
def test_typistry_singleton_pass() -> None:
    '''
    Test successful usage of the
    :attr:`beartype._check.forward.fwdtype.bear_typistry` singleton.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeDecorBeartypistryException
    from beartype._check.forward.fwdtype import bear_typistry
    from beartype._util.utilobject import get_object_type_name
    from pytest import raises

    # Assert that dictionary syntax also implicitly registers a type. Since
    # this approach explicitly prohibits re-registration for safety, we define
    # a custom user-defined type guaranteed *NOT* to have been registered yet.
    class TestTypistrySingletonPassType(object): pass
    hint = TestTypistrySingletonPassType
    hint_name = get_object_type_name(hint)
    bear_typistry[hint_name] = hint
    assert bear_typistry.get(hint_name) is hint

    # Assert that the same type is *NOT* re-registrable via dictionary syntax.
    with raises(_BeartypeDecorBeartypistryException):
        bear_typistry[hint_name] = hint

    # Avoid asserting tuples are also registrable via dictionary syntax. While
    # they technically are, asserting so would require declaring a new
    # get_typistry_tuple_name() function, which would then require refactoring
    # the register_typistry_tuple_from_frozenset() function to call that
    # function, which would reduce performance. Moreover, since those two
    # functions would be operating on different tuple objects, it's unclear
    # whether that refactoring would even be feasible.


def test_typistry_singleton_fail() -> None:
    '''
    Test unsuccessful usage of the
    :attr:`beartype._check.forward.fwdtype.bear_typistry` singleton.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeDecorBeartypistryException
    from beartype._check.forward.fwdtype import bear_typistry
    from pytest import raises

    # Assert that keys that are *NOT* strings are *NOT* registrable.
    with raises(_BeartypeDecorBeartypistryException):
        bear_typistry[(
            'And what rough beast, its hour come round at last,',)] = (
            'Slouches towards Bethlehem to be born?',)

    # Assert that forward references are *NOT* registrable.
    with raises(_BeartypeDecorBeartypistryException):
        bear_typistry['Mere.anarchy.is.loosed.upon.the.world'] = (
            'The blood-dimmed tide is loosed, and everywhere')

    # Assert that unhashable objects are *NOT* registrable.
    with raises(_BeartypeDecorBeartypistryException):
        bear_typistry['Turning.and.turning.in.the.widening.gyre'] = {
            'The falcon cannot hear the falconer;': (
                'Things fall apart; the centre cannot hold;'),
        }

    # Assert that arbitrary non-classes are *NOT* registrable.
    with raises(_BeartypeDecorBeartypistryException):
        bear_typistry['The.ceremony.of.innocence.is.drowned'] = 0xDEADBEEF

# ....................{ PRIVATE ~ utility                  }....................
#FIXME: Currently unused but preserved purely out of unhealthy paranoia.
# def _eval_registered_expr(hint_expr: str) -> Union[type, Tuple[type, ...]]:
#     '''
#     Dynamically evaluate the passed Python expression (assumed to be a string
#     returned by either the
#     :func:`beartype._check.forward.fwdtype.register_typistry_type` or
#     :func:`beartype._check.forward.fwdtype.register_typistry_tuple` functions)
#     *and* return the resulting value (assumed to either be a type or tuple of
#     types).
#     '''
#     assert isinstance(hint_expr, str), '{repr(hint_expr)} not string.'
#
#     # Defer test-specific imports.
#     from beartype._check.forward.fwdtype import bear_typistry
#     from beartype._decor.wrap.wrapsnip import ARG_NAME_TYPISTRY
#
#     # Dictionary of all local variables required to evaluate this expression.
#     eval_locals = {ARG_NAME_TYPISTRY: bear_typistry}
#
#     # Evaluate this expression under these local variables and return the
#     # resulting value.
#     return eval(hint_expr, {}, eval_locals)
