#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype configuration unit tests.**

This submodule unit tests the subset of the public API of the :mod:`beartype`
package defined by the private :mod:`beartype._decor.conf` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_api_conf_strategy() -> None:
    '''
    Test the public :func:`beartype.BeartypeStrategy` enumeration.
    '''

    # Defer heavyweight imports.
    from beartype import BeartypeStrategy

    # Assert this enumeration declares the expected members.
    assert isinstance(BeartypeStrategy.O0, BeartypeStrategy)
    assert isinstance(BeartypeStrategy.O1, BeartypeStrategy)
    assert isinstance(BeartypeStrategy.Ologn, BeartypeStrategy)
    assert isinstance(BeartypeStrategy.On, BeartypeStrategy)


def test_api_conf_type() -> None:
    '''
    Test the public :func:`beartype.BeartypeConf` class.
    '''

    # Defer heavyweight imports.
    from beartype import BeartypeConf, BeartypeStrategy
    from beartype.roar import BeartypeConfException
    from pytest import raises

    # Assert beartype configurations to be self-memoizing across both
    # unparametrized and parametrized type instantiations.
    #
    # Note that the latter explicitly validates that the "strategy" parameter
    # may be passed positionally.
    assert BeartypeConf() is BeartypeConf()
    assert (
        BeartypeConf(BeartypeStrategy.On, is_debug=True) is
        BeartypeConf(BeartypeStrategy.On, is_debug=True)
    )

    # Default (i.e., unparametrized) beartype configuration.
    bear_conf_default = BeartypeConf()

    # Assert this configuration to default to the expected public fields.
    assert bear_conf_default.strategy is BeartypeStrategy.O1
    assert bear_conf_default.is_debug is False

    # Assert that attempting to modify any public raises the expected
    # exception.
    with raises(AttributeError):
        bear_conf_default.strategy = BeartypeStrategy.O0
    with raises(AttributeError):
        bear_conf_default.is_debug = True

    # Arbitrary parametrized beartype configuration.
    bear_conf_nondefault = BeartypeConf(
        strategy=BeartypeStrategy.Ologn, is_debug=True)

    # Assert two identical configurations to compare equal.
    assert bear_conf_default == BeartypeConf()
    assert bear_conf_nondefault == BeartypeConf(
        strategy=BeartypeStrategy.Ologn, is_debug=True)

    # Assert two differing configurations to compare unequal.
    assert bear_conf_default != bear_conf_nondefault

    # Assert two identical configurations to hash equal.
    assert hash(bear_conf_default) == hash(BeartypeConf())
    assert hash(bear_conf_nondefault) == hash(BeartypeConf(
        strategy=BeartypeStrategy.Ologn, is_debug=True))

    # Assert two differing configurations to hash unequal.
    assert hash(bear_conf_default) != hash(bear_conf_nondefault)

    # Machine-readable representation of an arbitrary configuration.
    bear_conf_repr = repr(bear_conf_nondefault)

    # Assert this representation to contain the names of this class and all
    # public fields of this class.
    assert 'BeartypeConf' in bear_conf_repr
    assert 'strategy' in bear_conf_repr
    assert 'is_debug' in bear_conf_repr

    # Assert that instantiating a configuration with invalid parameters raises
    # the expected exceptions.
    with raises(BeartypeConfException):
        BeartypeConf(strategy=(
            'By all, but which the wise, and great, and good'))
    with raises(BeartypeConfException):
        BeartypeConf(is_debug=(
            'Interpret, or make felt, or deeply feel.'))
