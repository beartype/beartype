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
from pytest import MonkeyPatch

# ....................{ TESTS                              }....................
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
    from beartype.roar import BeartypeConfParamException
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
    with raises(BeartypeConfParamException):
        BeartypeConf(claw_is_pep526=(
            'The fountains mingle with the river'))
    with raises(BeartypeConfParamException):
        BeartypeConf(is_color=(
            'And many sounds, and much of life and death.'))
    with raises(BeartypeConfParamException):
        BeartypeConf(is_debug=(
            'Interpret, or make felt, or deeply feel.'))
    with raises(BeartypeConfParamException):
        BeartypeConf(is_pep484_tower=(
            'In the calm darkness of the moonless nights,'))
    with raises(BeartypeConfParamException):
        BeartypeConf(strategy=(
            'By all, but which the wise, and great, and good'))
    with raises(BeartypeConfParamException):
        BeartypeConf(warning_cls_on_decorator_exception=(
            'He lived, he died, he sung, in solitude.'))

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

# ....................{ TESTS ~ arg                        }....................
def test_api_conf_is_color(monkeypatch: MonkeyPatch) -> None:
    '''
    Test the``is_color`` parameter accepted by the
    :class:`beartype.BeartypeConf` class with respect to the external
    ``${BEARTYPE_IS_COLOR}`` shell environment variable also respected by that
    class, which interact in non-trivial ways.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        :mod:`pytest` fixture allowing various state associated with the active
        Python process to be temporarily changed for the duration of this test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.roar import (
        BeartypeConfShellVarException,
        BeartypeConfShellVarWarning,
    )
    from beartype._data.os.dataosshell import (
        SHELL_VAR_CONF_IS_COLOR_NAME)
    from pytest import (
        raises,
        warns,
    )

    # ....................{ PASS                           }....................
    # Temporarily enable the ${BEARTYPE_IS_COLOR} environment variable.
    monkeypatch.setenv(SHELL_VAR_CONF_IS_COLOR_NAME, 'True')

    # Non-default beartype configuration masquerading as the default
    # beartype configuration.
    bear_conf = BeartypeConf()

    # Assert that this configuration enabled the "is_color" parameter
    # despite the above instantiation *NOT* passing that parameter.
    assert bear_conf.is_color is True

    # Temporarily disable the ${BEARTYPE_IS_COLOR} environment variable.
    monkeypatch.setenv(SHELL_VAR_CONF_IS_COLOR_NAME, 'False')

    # Non-default beartype configuration masquerading as the default
    # beartype configuration.
    bear_conf = BeartypeConf()

    # Assert that this configuration disabled the "is_color" parameter
    # despite the above instantiation *NOT* passing that parameter.
    assert bear_conf.is_color is False

    # Temporarily nullify the ${BEARTYPE_IS_COLOR} environment variable.
    monkeypatch.setenv(SHELL_VAR_CONF_IS_COLOR_NAME, 'None')

    # Non-default beartype configuration masquerading as the default
    # beartype configuration.
    bear_conf = BeartypeConf()

    # Assert that this configuration nullified the "is_color" parameter
    # despite the above instantiation *NOT* passing that parameter.
    assert bear_conf.is_color is None

    # Non-default beartype configuration explicitly passing the same value for
    # the "is_color" parameter as the ${BEARTYPE_IS_COLOR} environment variable
    # is also currently set to.
    bear_conf = BeartypeConf(is_color=None)

    # Assert that this configuration nullified the "is_color" parameter.
    assert bear_conf.is_color is None

    # ....................{ FAIL                           }....................
    # Assert that attempting to instantiate a beartype configuration when the
    # ${BEARTYPE_IS_COLOR} environment variable is set to a valid string value
    # differing from the valid non-string value passed for the "is_color"
    # parameter emits the expected non-fatal warning.
    with warns(BeartypeConfShellVarWarning):
        # Non-default beartype configuration explicitly passing a differing
        # value for the "is_color" parameter as the ${BEARTYPE_IS_COLOR}
        # environment variable is currently set to.
        bear_conf = BeartypeConf(is_color=True)

        # Assert that this configuration override the passed value of the
        # "is_color" parameter in favour of the corresponding value of the
        # ${BEARTYPE_IS_COLOR} environment variable.
        assert bear_conf.is_color is None

    # Assert that attempting to instantiate a beartype configuration when the
    # ${BEARTYPE_IS_COLOR} environment variable is set to invalid string value
    # raises the expected exception.
    with raises(BeartypeConfShellVarException) as exception_info:
        # Temporarily set ${BEARTYPE_IS_COLOR} to an invalid value.
        monkeypatch.setenv(
            SHELL_VAR_CONF_IS_COLOR_NAME,
            'Strangers have wept to hear his passionate notes,',
        )

        # Attempt to instantiate a beartype configuration.
        BeartypeConf()

    # Assert that this exception message contains an expected substring, whose
    # construction is non-trivial and thus liable to improper construction.
    assert '"True", "False", or "None"' in str(exception_info.value)


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
