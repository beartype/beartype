#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype main error-handling unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._check.error.errget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ pith                       }....................
def test_get_func_pith_violation() -> None:
    '''
    Test the
    :func:`beartype._check.error.errget.get_func_pith_violation` getter.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.roar import (
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
        BeartypeDecorHintNonpepException,
    )
    from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
    from beartype.typing import (
        List,
        Tuple,
        Union,
    )
    from beartype._data.func.datafuncarg import ARG_NAME_RETURN
    from beartype._check.error.errget import get_func_pith_violation
    from beartype._check.metadata.metacheck import BeartypeCheckMeta
    from pytest import raises

    # ..................{ LOCALS                             }..................
    def forest_unknown(
        secret_orchard: List[str],
        achromatic_voice,
        to_bid_you_farewell: str,
        amaranth_symbol: 42,
    ) -> Union[int, Tuple[str, ...]]:
        '''
        Arbitrary callable exercised below.
        '''

        return achromatic_voice

    # Beartype type-checking call metadata reduced from this decorator metadata.
    check_meta = BeartypeCheckMeta.make_from_decor_meta_kwargs(
        func=forest_unknown, conf=BeartypeConf())

    # ..................{ PASS                               }..................
    # Assert this function returns the expected exception when passed a
    # parameter annotated by a PEP-compliant type hint failing to shallowly
    # satisfy the type of that type hint.
    violation = get_func_pith_violation(
        check_meta=check_meta,
        pith_name='secret_orchard',
        pith_value=(
            'You are in a forest unknown:',
            'The secret orchard.',
        ),
    )
    assert isinstance(violation, BeartypeCallHintParamViolation)

    # Assert this function returns the expected exception when passed a
    # parameter annotated by a PEP-compliant type hint failing to deeply satisfy
    # the type of that type hint.
    violation = get_func_pith_violation(
        check_meta=check_meta,
        pith_name='secret_orchard',
        pith_value=[
            b'I am awaiting the sunrise',
            b'Gazing modestly through the coldest morning',
        ],
        random_int=0,
    )
    assert isinstance(violation, BeartypeCallHintParamViolation)

    # Assert this function returns the expected exception when passed another
    # parameter annotated by a PEP-noncompliant type hint failing to shallowly
    # satisfy the type of that type hint.
    violation = get_func_pith_violation(
        check_meta=check_meta,
        pith_name='to_bid_you_farewell',
        pith_value=(
            b'Once it came you lied,'
            b"Embracing us over autumn's proud treetops."
        ),
        random_int=1,
    )
    assert isinstance(violation, BeartypeCallHintParamViolation)

    # Assert this function returns the expected exception when returning a
    # return value annotated by a PEP-compliant type hint failing to satisfy
    # that type hint.
    violation = get_func_pith_violation(
        check_meta=check_meta,
        pith_name=ARG_NAME_RETURN,
        pith_value=[
            'Sunbirds leave their dark recesses.',
            'Shadows glide the archways.',
        ],
        random_int=0,
    )
    assert isinstance(violation, BeartypeCallHintReturnViolation)

    # ..................{ FAIL                               }..................
    # Assert this function raises the expected exception when passed an
    # unannotated parameter.
    with raises(_BeartypeCallHintPepRaiseException):
        get_func_pith_violation(
            check_meta=check_meta,
            pith_name='achromatic_voice',
            pith_value=(
                'And your voice is vast and achromatic,'
                'But still so precious.'
            ),
            random_int=1,
        )

    # Assert this function raises the expected exception when passed a
    # parameter annotated by an object that is unsupported as a type hint
    # (i.e., is neither PEP-compliant nor -noncompliant).
    with raises(BeartypeDecorHintNonpepException):
        get_func_pith_violation(
            check_meta=check_meta,
            pith_name='amaranth_symbol',
            pith_value=(
                'I have kept it,'
                'The Amaranth symbol,'
                'Hidden inside the golden shrine'
                'Until we rejoice in the meadow'
                'Of the end.'
                'When we both walk the shadows,'
                'It will set ablaze and vanish.'
            ),
            random_int=5,
        )

# ....................{ TESTS ~ pith : conf                }....................
def test_get_func_pith_violation_conf_is_color() -> None:
    '''
    Test the
    :func:`beartype._check.error.errget.get_func_pith_violation` getter with
    respect to the :attr:`beartype.BeartypeConf.is_color` option.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.typing import (
        List,
        Tuple,
        Union,
    )
    from beartype._check.error.errget import get_func_pith_violation
    from beartype._check.metadata.metacheck import BeartypeCheckMeta
    from beartype._util.os.utilostty import is_stdout_terminal
    from beartype._util.text.utiltextansi import is_str_ansi

    # ..................{ LOCALS                             }..................
    def she_drew_back(
        a_while: List[str], then_yielding) -> Union[int, Tuple[str, ...]]:
        '''
        Arbitrary callable exercised below.
        '''

        return then_yielding


    # Keyword arguments to be unconditionally passed to *ALL* calls of the
    # get_func_pith_violation() getter below.
    kwargs = dict(
        pith_name='a_while',
        pith_value=(
            'With frantic gesture and short breathless cry',
            'Folded his frame in her dissolving arms.',
        ),
    )

    # ..................{ PASS                               }..................
    # Violation configured to contain ANSI escape sequences.
    violation = get_func_pith_violation(
        check_meta=BeartypeCheckMeta.make_from_decor_meta_kwargs(
            func=she_drew_back, conf=BeartypeConf(is_color=True)), **kwargs)

    # Assert this violation message contains ANSI escape sequences.
    assert is_str_ansi(str(violation)) is True

    # Violation configured to contain *NO* ANSI escape sequences.
    violation = get_func_pith_violation(
        check_meta=BeartypeCheckMeta.make_from_decor_meta_kwargs(
            func=she_drew_back, conf=BeartypeConf(is_color=False)), **kwargs)

    # Assert this violation message contains *NO* ANSI escape sequences.
    assert is_str_ansi(str(violation)) is False

    # Violation configured to conditionally contain ANSI escape sequences only
    # when standard output is attached to an interactive terminal.
    violation = get_func_pith_violation(
        check_meta=BeartypeCheckMeta.make_from_decor_meta_kwargs(
            func=she_drew_back, conf=BeartypeConf(is_color=None)), **kwargs)

    # Assert this violation message contains ANSI escape sequences only when
    # standard output is attached to an interactive terminal.
    assert is_str_ansi(str(violation)) is is_stdout_terminal()

# ....................{ TESTS ~ pith : conf : violation_*  }....................
def test_get_func_pith_violation_conf_violation_types() -> None:
    '''
    Test the
    :func:`beartype._check.error.errget.get_func_pith_violation` getter with
    respect to the
    :attr:`beartype.BeartypeConf.violation_param_type` and
    :attr:`beartype.BeartypeConf.violation_return_type` options.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.typing import (
        List,
        Tuple,
        Union,
    )
    from beartype._data.func.datafuncarg import ARG_NAME_RETURN
    from beartype._check.error.errget import get_func_pith_violation
    from beartype._check.metadata.metacheck import BeartypeCheckMeta

    # ..................{ LOCALS                             }..................
    class InvolvedAndSwallowed(Exception):
        '''
        Arbitrary exception subclass.
        '''

        pass


    def now_blackness(
        veiled_his: List[str], dizzy_eyes) -> Union[int, Tuple[str, ...]]:
        '''
        Arbitrary callable exercised below.
        '''

        return dizzy_eyes

    # ..................{ PASS                               }..................
    # Parameter violation configured to be a non-default exception subclass.
    param_violation = get_func_pith_violation(
        check_meta=BeartypeCheckMeta.make_from_decor_meta_kwargs(
            func=now_blackness, conf=BeartypeConf(
                violation_param_type=InvolvedAndSwallowed)),
        pith_name='veiled_his',
        pith_value=(
            'Now blackness veiled his dizzy eyes, and night',
            'Involved and swallowed up the vision; sleep,',
        ),
    )

    # Assert that this violation is the expected non-default exception subclass.
    assert type(param_violation) is InvolvedAndSwallowed

    # Return violation configured to be a non-default exception subclass.
    return_violation = get_func_pith_violation(
        check_meta=BeartypeCheckMeta.make_from_decor_meta_kwargs(
            func=now_blackness, conf=BeartypeConf(
                violation_return_type=InvolvedAndSwallowed)),
        pith_name=ARG_NAME_RETURN,
        pith_value=[
            'Like a dark flood suspended in its course',
            'Rolled back its impulse on his vacant brain.',
        ],
    )

    # Assert that this violation is the expected non-default exception subclass.
    assert type(return_violation) is InvolvedAndSwallowed


def test_get_func_pith_violation_conf_violation_verbosity() -> None:
    '''
    Test the
    :func:`beartype._check.error.errget.get_func_pith_violation` getter with
    respect to the
    :attr:`beartype.BeartypeConf.violation_verbosity` option.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        BeartypeViolationVerbosity,
    )
    from beartype.typing import (
        List,
        Tuple,
        Union,
    )
    from beartype._check.error.errget import get_func_pith_violation
    from beartype._check.metadata.metacheck import BeartypeCheckMeta

    # ..................{ LOCALS                             }..................
    def like_a_dark_flood(
        suspended_in: List[str], its_course) -> Union[int, Tuple[str, ...]]:
        '''
        Arbitrary callable exercised below.
        '''

        return its_course


    # Keyword arguments to be unconditionally passed to *ALL* calls of the
    # get_func_pith_violation() getter below.
    kwargs = dict(
        pith_name='suspended_in',
        pith_value=(
            'Roused by the shock he started from his trance—',
            'The cold white light of morning, the blue moon',
        ),
    )

    # ..................{ PASS                               }..................
    # Tuple of all otherwise equivalent violations produced by iteratively
    # increasing the level of violation verbosity.
    violations = tuple(
        # Violation whose message is configured to be this verbose...
        get_func_pith_violation(
            check_meta=BeartypeCheckMeta.make_from_decor_meta_kwargs(
                func=like_a_dark_flood, conf=BeartypeConf(
                    violation_verbosity=violation_verbosity)), **kwargs)
        # For each kind of violation verbosity.
        for violation_verbosity in BeartypeViolationVerbosity
    )

    # Previously iterated violation, defaulting to the minimally verbose (i.e.,
    # maximally terse) violation.
    violation_prev = violations[0]

    # For each increasingly verbose violation following the first...
    for violation in violations[1:]:
        # Assert that this violation message is more verbose than the last.
        assert len(str(violation)) > len(str(violation_prev))

        # Store the previously iterated violation for subsequent reference.
        violation_prev = violation

# ....................{ TESTS ~ pith                       }....................
def test_get_hint_object_violation() -> None:
    '''
    Test the
    :func:`beartype._check.error.errget.get_hint_object_violation` getter.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
    from beartype._data.func.datafuncarg import ARG_NAME_RETURN
    from beartype._check.error.errget import get_hint_object_violation
    from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
    from pytest import raises

    # ..................{ LOCALS                             }..................
    # Keyword arguments to be unconditionally passed to all getter calls below.
    kwargs = dict(
        obj='Frantic with dizzying anguish, her blind flight',
        hint=str,
        conf=BEARTYPE_CONF_DEFAULT,
    )

    # ..................{ FAIL                               }..................
    # Assert that this getter raises the expected exception when passed neither
    # an exception prefix *NOR* parameter name.
    with raises(_BeartypeCallHintPepRaiseException):
        get_hint_object_violation(**kwargs)

    # Assert that this getter raises the expected exception when passed both an
    # exception prefix *AND* parameter name.
    with raises(_BeartypeCallHintPepRaiseException):
        get_hint_object_violation(
            exception_prefix="O'er the wide aëry wilderness: thus driven",
            pith_name=ARG_NAME_RETURN,
            **kwargs
        )
