#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype configuration unit tests.**

This submodule unit tests the subset of the public API of the :mod:`beartype`
package defined by the private :mod:`beartype._conf` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_api_conf_strategy() -> None:
    '''
    Test the public :func:`beartype.BeartypeStrategy` enumeration.
    '''

    # Defer test-specific imports.
    from beartype import BeartypeStrategy

    # Assert this enumeration declares the expected members.
    assert isinstance(BeartypeStrategy.O0, BeartypeStrategy)
    assert isinstance(BeartypeStrategy.O1, BeartypeStrategy)
    assert isinstance(BeartypeStrategy.Ologn, BeartypeStrategy)
    assert isinstance(BeartypeStrategy.On, BeartypeStrategy)


def test_api_conf_dataclass() -> None:
    '''
    Test the public :func:`beartype.BeartypeConf` class.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        BeartypeStrategy,
    )
    from beartype.roar import BeartypeConfException
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Tuple of all substrings to assert as trivially contained within the string
    # returned by the BeartypeConf.__repr__() dunder method, including:
    # * The unqualified basename of this class.
    # * The unqualified basenames of and all public fields of this class.
    BEAR_CONF_REPR_SUBSTRS = (
        'BeartypeConf',
        'claw_is_pep526',
        'is_color',
        'is_debug',
        'is_pep484_tower',
        'strategy',
    )

    # Default (i.e., unparametrized) beartype configuration.
    BEAR_CONF_DEFAULT = BeartypeConf()

    # All possible keyword arguments initialized to non-default values with
    # which to instantiate a non-default beartype configuration.
    BEAR_CONF_NONDEFAULT_KWARGS = dict(
        claw_is_pep526=False,
        is_color=True,
        is_debug=True,
        is_pep484_tower=True,
        strategy=BeartypeStrategy.Ologn,
        warning_cls_on_decorator_exception=None,
    )

    # Arbitrary parametrized beartype configuration.
    BEAR_CONF_NONDEFAULT = BeartypeConf(**BEAR_CONF_NONDEFAULT_KWARGS)

    # # Tuple of these beartype configurations.
    # BEAR_CONFS = (BEAR_CONF_DEFAULT, BEAR_CONF_NONDEFAULT)

    # ....................{ PASS                           }....................
    # Assert beartype configurations to be self-memoizing across both
    # unparametrized and parametrized type instantiations.
    #
    # Note that the latter explicitly validates that this memoization ignores
    # the order in which parameters are passed.
    assert BeartypeConf() is BeartypeConf()
    assert (
        BeartypeConf(strategy=BeartypeStrategy.On, claw_is_pep526=False, is_debug=True, is_color=True, is_pep484_tower=True) is
        BeartypeConf(is_pep484_tower=True, is_color=True, is_debug=True, claw_is_pep526=False, strategy=BeartypeStrategy.On)
    )

    # Assert that the default configuration contains the expected fields.
    assert BEAR_CONF_DEFAULT.claw_is_pep526 is True
    assert BEAR_CONF_DEFAULT.is_color is None
    assert BEAR_CONF_DEFAULT.is_debug is False
    assert BEAR_CONF_DEFAULT.is_pep484_tower is False
    assert BEAR_CONF_DEFAULT.strategy is BeartypeStrategy.O1
    assert BEAR_CONF_DEFAULT.warning_cls_on_decorator_exception is None
    assert BEAR_CONF_DEFAULT._is_warning_cls_on_decorator_exception_set is False

    # Assert that the non-default configuration contains the expected fields.
    assert BEAR_CONF_NONDEFAULT.claw_is_pep526 is False
    assert BEAR_CONF_NONDEFAULT.is_color is True
    assert BEAR_CONF_NONDEFAULT.is_debug is True
    assert BEAR_CONF_NONDEFAULT.is_pep484_tower is True
    assert BEAR_CONF_NONDEFAULT.strategy is BeartypeStrategy.Ologn
    assert BEAR_CONF_NONDEFAULT.warning_cls_on_decorator_exception is None
    assert BEAR_CONF_NONDEFAULT._is_warning_cls_on_decorator_exception_set is (
        True)

    # Assert that two differing configurations compare unequal.
    assert BEAR_CONF_DEFAULT != BEAR_CONF_NONDEFAULT

    # Assert that two identical configurations compare equal.
    assert BEAR_CONF_DEFAULT == BeartypeConf()
    assert BEAR_CONF_NONDEFAULT == BeartypeConf(**BEAR_CONF_NONDEFAULT_KWARGS)

    # Assert that two identical configurations hash equal.
    assert hash(BEAR_CONF_DEFAULT) == hash(BeartypeConf())
    assert hash(BEAR_CONF_NONDEFAULT) == hash(
        BeartypeConf(**BEAR_CONF_NONDEFAULT_KWARGS))

    # Assert that two differing configurations hash unequal.
    assert hash(BEAR_CONF_DEFAULT) != hash(BEAR_CONF_NONDEFAULT)

    # Machine-readable representation of an arbitrary configuration.
    BEAR_CONF_REPR = repr(BEAR_CONF_NONDEFAULT)

    # Assert that this representation to contain the names of this class and all
    # public fields of this class.
    for BEAR_CONF_REPR_SUBSTR in BEAR_CONF_REPR_SUBSTRS:
        assert BEAR_CONF_REPR_SUBSTR in BEAR_CONF_REPR

    # ....................{ FAIL                           }....................
    # Assert that instantiating a configuration with an invalid parameter raises
    # the expected exception.
    with raises(BeartypeConfException):
        BeartypeConf(claw_is_pep526=(
            'The fountains mingle with the river'))
    with raises(BeartypeConfException):
        BeartypeConf(is_color=(
            'And many sounds, and much of life and death.'))
    with raises(BeartypeConfException):
        BeartypeConf(is_debug=(
            'Interpret, or make felt, or deeply feel.'))
    with raises(BeartypeConfException):
        BeartypeConf(is_pep484_tower=(
            'In the calm darkness of the moonless nights,'))
    with raises(BeartypeConfException):
        BeartypeConf(strategy=(
            'By all, but which the wise, and great, and good'))

    # Assert that attempting to modify any public raises the expected exception.
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.claw_is_pep526 = True
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.is_color = True
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.is_debug = True
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.is_pep484_tower = True
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.strategy = BeartypeStrategy.O0
