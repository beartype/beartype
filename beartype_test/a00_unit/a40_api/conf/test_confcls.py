#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype configuration unit tests.**

This submodule unit tests the subset of the public API of the :mod:`beartype`
package defined by the private :mod:`beartype._conf.confcls` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_conf_dataclass() -> None:
    '''
    Test the public :func:`beartype.BeartypeConf` class.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        BeartypeDecorationPosition,
        BeartypeHintOverrides,
        BeartypeStrategy,
        BeartypeViolationVerbosity,
    )
    from beartype.roar import (
        BeartypeConfParamException,
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
        BeartypeDoorHintViolation,
    )
    from beartype.typing import Union
    from beartype._conf.confoverrides import (
        BEARTYPE_HINT_OVERRIDES_EMPTY,
        beartype_hint_overrides_pep484_tower,
    )
    from beartype._util.utilobject import get_object_type_basename
    from pytest import raises

    # ....................{ CLASSES                        }....................
    class FakeBool(object):
        '''
        Fake boolean class, just because. Look. Just accept it.
        '''

        def __bool__(self) -> bool:
            return False

    # ....................{ LOCALS                         }....................
    # Tuple of all substrings to assert as trivially contained within the string
    # returned by the BeartypeConf.__repr__() dunder method, including:
    # * The unqualified basename of this class.
    # * The unqualified basenames of and all public fields of this class.
    BEAR_CONF_REPR_SUBSTRS = (
        'BeartypeConf',
        'claw_decoration_position_funcs',
        'claw_decoration_position_types',
        'claw_is_pep526',
        'claw_skip_package_names',
        'hint_overrides',
        'is_color',
        'is_debug',
        'is_pep484_tower',
        'strategy',
        'violation_door_type',
        'violation_param_type',
        'violation_return_type',
        'violation_type',
        'violation_verbosity',
        'warning_cls_on_decorator_exception',
    )

    # Default (i.e., unparametrized) beartype configuration.
    BEAR_CONF_DEFAULT = BeartypeConf()

    # Non-empty hint overrides mapping one or more arbitrary source type hints
    # to corresponding arbitrary target type hints.
    BEAR_HINT_OVERRIDES_NONEMPTY = BeartypeHintOverrides({bool: FakeBool})

    # All possible keyword arguments initialized to non-default values with
    # which to instantiate a non-default beartype configuration.
    BEAR_CONF_NONDEFAULT_KWARGS = dict(
        claw_decoration_position_funcs=BeartypeDecorationPosition.FIRST,
        claw_decoration_position_types=BeartypeDecorationPosition.FIRST,
        claw_is_pep526=False,
        claw_skip_package_names=('Made_contrast_with', 'the_universe',),
        hint_overrides=BEAR_HINT_OVERRIDES_NONEMPTY,
        is_color=True,
        is_debug=True,
        is_pep484_tower=True,
        strategy=BeartypeStrategy.Ologn,
        violation_door_type=RuntimeError,
        violation_param_type=TypeError,
        violation_return_type=ValueError,
        violation_type=AttributeError,
        violation_verbosity=BeartypeViolationVerbosity.MINIMAL,
        warning_cls_on_decorator_exception=None,
    )

    # Arbitrary parametrized beartype configuration.
    BEAR_CONF_NONDEFAULT = BeartypeConf(**BEAR_CONF_NONDEFAULT_KWARGS)

    # Arbitrary parametrized beartype configurations setting all possible
    # combinations of a default violation type and another violation type.
    BEAR_CONF_NONDEFAULT_VIOLATION_DOOR = BeartypeConf(
        violation_type=AttributeError, violation_door_type=RuntimeError)
    BEAR_CONF_NONDEFAULT_VIOLATION_PARAM = BeartypeConf(
        violation_type=AttributeError, violation_param_type=TypeError)
    BEAR_CONF_NONDEFAULT_VIOLATION_RETURN = BeartypeConf(
        violation_type=AttributeError, violation_return_type=ValueError)

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
        BeartypeConf(
            claw_decoration_position_funcs=BeartypeDecorationPosition.FIRST,
            claw_decoration_position_types=BeartypeDecorationPosition.LAST,
            claw_is_pep526=False,
            claw_skip_package_names=('Made_contrast_with', 'the_universe',),
            hint_overrides=BEAR_HINT_OVERRIDES_NONEMPTY,
            is_debug=True,
            is_color=True,
            is_pep484_tower=True,
            strategy=BeartypeStrategy.On,
            violation_door_type=RuntimeError,
            violation_param_type=TypeError,
            violation_return_type=ValueError,
            violation_type=AttributeError,
            violation_verbosity=BeartypeViolationVerbosity.MINIMAL,
            warning_cls_on_decorator_exception=UserWarning,
        ) is
        BeartypeConf(
            warning_cls_on_decorator_exception=UserWarning,
            violation_verbosity=BeartypeViolationVerbosity.MINIMAL,
            violation_type=AttributeError,
            violation_return_type=ValueError,
            violation_param_type=TypeError,
            violation_door_type=RuntimeError,
            strategy=BeartypeStrategy.On,
            is_pep484_tower=True,
            is_color=True,
            is_debug=True,
            hint_overrides=BEAR_HINT_OVERRIDES_NONEMPTY,
            claw_is_pep526=False,
            claw_skip_package_names=('Made_contrast_with', 'the_universe',),
            claw_decoration_position_types=BeartypeDecorationPosition.LAST,
            claw_decoration_position_funcs=BeartypeDecorationPosition.FIRST,
        )
    )

    # ....................{ PASS ~ properties              }....................
    # Assert that the default configuration contains the expected fields.
    assert BEAR_CONF_DEFAULT.claw_decoration_position_funcs is (
        BeartypeDecorationPosition.LAST)
    assert BEAR_CONF_DEFAULT.claw_decoration_position_types is (
        BeartypeDecorationPosition.LAST)
    assert BEAR_CONF_DEFAULT.claw_is_pep526 is True
    assert BEAR_CONF_DEFAULT.claw_skip_package_names == ()
    assert BEAR_CONF_DEFAULT.hint_overrides is BEARTYPE_HINT_OVERRIDES_EMPTY
    assert BEAR_CONF_DEFAULT.is_color is None
    assert BEAR_CONF_DEFAULT.is_debug is False
    assert BEAR_CONF_DEFAULT.is_pep484_tower is False
    assert BEAR_CONF_DEFAULT.strategy is BeartypeStrategy.O1
    assert BEAR_CONF_DEFAULT.violation_door_type is (
        BeartypeDoorHintViolation)
    assert BEAR_CONF_DEFAULT.violation_param_type is (
        BeartypeCallHintParamViolation)
    assert BEAR_CONF_DEFAULT.violation_return_type is (
        BeartypeCallHintReturnViolation)
    assert BEAR_CONF_DEFAULT.violation_type is None
    assert BEAR_CONF_DEFAULT.violation_verbosity is (
        BeartypeViolationVerbosity.DEFAULT)
    assert BEAR_CONF_DEFAULT.warning_cls_on_decorator_exception is None
    assert BEAR_CONF_DEFAULT._is_warning_cls_on_decorator_exception_set is False

    # Assert that the non-default configuration contains the expected fields.
    assert BEAR_CONF_DEFAULT.claw_decoration_position_funcs is (
        BeartypeDecorationPosition.LAST)
    assert BEAR_CONF_DEFAULT.claw_decoration_position_types is (
        BeartypeDecorationPosition.LAST)
    assert BEAR_CONF_NONDEFAULT.claw_is_pep526 is False
    assert BEAR_CONF_NONDEFAULT.claw_skip_package_names == (
        'Made_contrast_with', 'the_universe',)
    assert BEAR_CONF_NONDEFAULT.hint_overrides == (
        BEAR_HINT_OVERRIDES_NONEMPTY | beartype_hint_overrides_pep484_tower())
    assert BEAR_CONF_NONDEFAULT.is_color is True
    assert BEAR_CONF_NONDEFAULT.is_debug is True
    assert BEAR_CONF_NONDEFAULT.is_pep484_tower is True
    assert BEAR_CONF_NONDEFAULT.strategy is BeartypeStrategy.Ologn
    assert BEAR_CONF_NONDEFAULT.violation_door_type is RuntimeError
    assert BEAR_CONF_NONDEFAULT.violation_param_type is TypeError
    assert BEAR_CONF_NONDEFAULT.violation_return_type is ValueError
    assert BEAR_CONF_NONDEFAULT.violation_type is AttributeError
    assert BEAR_CONF_NONDEFAULT.violation_verbosity is (
        BeartypeViolationVerbosity.MINIMAL)
    assert BEAR_CONF_NONDEFAULT.warning_cls_on_decorator_exception is None
    assert BEAR_CONF_NONDEFAULT._is_warning_cls_on_decorator_exception_set is (
        True)

    # Assert that the non-default violation-specific configurations contain the
    # expected fields.
    assert BEAR_CONF_NONDEFAULT_VIOLATION_DOOR.violation_type is AttributeError
    assert BEAR_CONF_NONDEFAULT_VIOLATION_DOOR.violation_door_type is (
        RuntimeError)
    assert BEAR_CONF_NONDEFAULT_VIOLATION_DOOR.violation_param_type is (
        AttributeError)
    assert BEAR_CONF_NONDEFAULT_VIOLATION_DOOR.violation_return_type is (
        AttributeError)
    assert BEAR_CONF_NONDEFAULT_VIOLATION_PARAM.violation_type is AttributeError
    assert BEAR_CONF_NONDEFAULT_VIOLATION_PARAM.violation_door_type is (
        AttributeError)
    assert BEAR_CONF_NONDEFAULT_VIOLATION_PARAM.violation_param_type is (
        TypeError)
    assert BEAR_CONF_NONDEFAULT_VIOLATION_PARAM.violation_return_type is (
        AttributeError)
    assert BEAR_CONF_NONDEFAULT_VIOLATION_RETURN.violation_type is (
        AttributeError)
    assert BEAR_CONF_NONDEFAULT_VIOLATION_RETURN.violation_door_type is (
        AttributeError)
    assert BEAR_CONF_NONDEFAULT_VIOLATION_RETURN.violation_param_type is (
        AttributeError)
    assert BEAR_CONF_NONDEFAULT_VIOLATION_RETURN.violation_return_type is (
        ValueError)

    # ....................{ PASS ~ equals                  }....................
    # Assert that two differing configurations compare unequal.
    assert BEAR_CONF_DEFAULT != BEAR_CONF_NONDEFAULT

    # Assert that two identical configurations compare equal.
    assert BEAR_CONF_DEFAULT == BeartypeConf()
    assert BEAR_CONF_NONDEFAULT == BeartypeConf(**BEAR_CONF_NONDEFAULT_KWARGS)

    # ....................{ PASS ~ hash                    }....................
    # Assert that two identical configurations hash equal.
    assert hash(BEAR_CONF_DEFAULT) == hash(BeartypeConf())
    assert hash(BEAR_CONF_NONDEFAULT) == hash(
        BeartypeConf(**BEAR_CONF_NONDEFAULT_KWARGS))

    # Assert that two differing configurations hash unequal.
    assert hash(BEAR_CONF_DEFAULT) != hash(BEAR_CONF_NONDEFAULT)

    # ....................{ PASS ~ repr                    }....................
    # Unqualified basename of the class of all beartype configurations.
    BEAR_CONF_BASENAME = get_object_type_basename(BEAR_CONF_DEFAULT)

    # Machine-readable representation of the default configuration.
    BEAR_CONF_DEFAULT_REPR = repr(BEAR_CONF_DEFAULT)

    # Assert that this representation is simply the unqualified basename of the
    # class of this configuration followed by empty parens.
    assert BEAR_CONF_DEFAULT_REPR == f'{BEAR_CONF_BASENAME}()'

    # Machine-readable representation of a non-default configuration.
    BEAR_CONF_NONDEFAULT_REPR = repr(BEAR_CONF_NONDEFAULT)

    # Assert that this representation is prefixed by the unqualified basename of
    # the class of this configuration followed by an opening parens.
    assert BEAR_CONF_NONDEFAULT_REPR.startswith(f'{BEAR_CONF_BASENAME}(')

    # Assert that this representation is suffixed by a closing parens.
    assert BEAR_CONF_NONDEFAULT_REPR.endswith(')')

    # Assert that this representation is *NOT* suffixed by a
    # whitespace-delimited comma followed by a closing parens.
    assert not BEAR_CONF_NONDEFAULT_REPR.endswith(', )')

    # Assert that this representation embeds the names and values of all public
    # non-default fields of this configuration.
    for bear_conf_repr_substr in BEAR_CONF_REPR_SUBSTRS:
        assert bear_conf_repr_substr in BEAR_CONF_NONDEFAULT_REPR

    # ....................{ FAIL                           }....................
    # Assert that instantiating a configuration with an invalid parameter raises
    # the expected exception.
    with raises(BeartypeConfParamException):
        BeartypeConf(claw_decoration_position_funcs=(
            "High 'mid the shifting domes of sheeted spray"))
    with raises(BeartypeConfParamException):
        BeartypeConf(claw_decoration_position_types=(
            "That canopied his path o'er the waste deep;"))
    with raises(BeartypeConfParamException):
        BeartypeConf(claw_is_pep526=(
            'The fountains mingle with the river'))
    with raises(BeartypeConfParamException):
        BeartypeConf(claw_skip_package_names=('A pine,', 'Rock-rooted,'))
    with raises(BeartypeConfParamException):
        BeartypeConf(claw_skip_package_names=(
            'stretched_athwart', b'the vacancy'))
    with raises(BeartypeConfParamException):
        BeartypeConf(claw_skip_package_names=(
            'Yielding_one.only_response.at.each_pause', ''))
    with raises(BeartypeConfParamException):
        BeartypeConf(claw_skip_package_names=(
            package_name
            for package_name in (
                'Its_swinging_boughs', 'to_each_inconstant_blast',)
        ))
    with raises(BeartypeConfParamException):
        BeartypeConf(hint_overrides=(
            'Wildered, and wan, and panting, she returned.'))
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
        BeartypeConf(violation_door_type=(
            'A vision to the sleep of him who spurned'))
    with raises(BeartypeConfParamException):
        BeartypeConf(violation_door_type=bool)
    with raises(BeartypeConfParamException):
        BeartypeConf(violation_param_type=(
            'His strong heart sunk and sickened with excess'))
    with raises(BeartypeConfParamException):
        BeartypeConf(violation_param_type=str)
    with raises(BeartypeConfParamException):
        BeartypeConf(violation_return_type=(
            'Of love. He reared his shuddering limbs and quelled'))
    with raises(BeartypeConfParamException):
        BeartypeConf(violation_return_type=int)
    with raises(BeartypeConfParamException):
        BeartypeConf(violation_type=(
            'Her choicest gifts. He eagerly pursues'))
    with raises(BeartypeConfParamException):
        BeartypeConf(violation_type=complex)
    with raises(BeartypeConfParamException):
        BeartypeConf(violation_verbosity=(
            'His gasping breath, and spread his arms to meet'))
    with raises(BeartypeConfParamException):
        BeartypeConf(warning_cls_on_decorator_exception=(
            'He lived, he died, he sung, in solitude.'))
    with raises(BeartypeConfParamException):
        BeartypeConf(warning_cls_on_decorator_exception=RuntimeError)

    # Assert that instantiating a configuration with conflicting
    # "is_pep484_tower" and "hint_overrides" parameters raises the expected
    # exception.
    with raises(BeartypeConfParamException):
        BeartypeConf(
            is_pep484_tower=True,
            hint_overrides=BeartypeHintOverrides({float: complex})
        )
    with raises(BeartypeConfParamException):
        BeartypeConf(
            is_pep484_tower=True,
            hint_overrides=BeartypeHintOverrides({complex: int})
        )

    # Assert that attempting to modify any public read-only property of this
    # dataclass raises the expected exception.
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.claw_decoration_position_funcs = (
            BeartypeDecorationPosition.FIRST)
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.claw_decoration_position_types = (
            BeartypeDecorationPosition.FIRST)
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.claw_is_pep526 = True
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.claw_skip_package_names = ('q','w','e')
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.hint_overrides = {}
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.is_color = True
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.is_debug = True
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.is_pep484_tower = True
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.strategy = BeartypeStrategy.O0
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.violation_door_type = RuntimeError
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.violation_param_type = TypeError
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.violation_return_type = ValueError
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.violation_type = AttributeError
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.violation_verbosity = (
            BeartypeViolationVerbosity.MINIMAL)
    with raises(AttributeError):
        BEAR_CONF_DEFAULT.warning_cls_on_decorator_exception = None

# ....................{ TESTS ~ arg                        }....................
def test_conf_is_color(monkeypatch: 'pytest.MonkeyPatch') -> None:
    '''
    Test the ``is_color`` parameter accepted by the
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
