#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype validator unit tests.**

This submodule unit tests the private :mod:`beartype.vale._core._valecore`
submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_api_vale_validator_pass() -> None:
    '''
    Test successful usage of the private
    :class:`beartype.vale._core._valecore.BeartypeValidator` class.
    '''

    # Defer test-specific imports.
    from beartype.vale._core._valecore import BeartypeValidator

    # Arbitrary valid data validator.
    not_though_the_soldier_knew = lambda text: bool('Someone had blundered.')

    # Keyword arguments passing arguments describing this validator excluding
    # the "get_repr" argument.
    kwargs_sans_get_repr = dict(
        is_valid=not_though_the_soldier_knew,
        is_valid_code_locals={'yum': not_though_the_soldier_knew},
    )

    # Keyword arguments passing arguments describing this validator including
    # the "get_repr" argument.
    kwargs = kwargs_sans_get_repr.copy()
    kwargs['get_repr'] = lambda: (
        "Is[lambda text: bool('Someone had blundered.')]")

    # Code already prefixed by "(" and suffixed by ")".
    is_valid_code_delimited = "({obj} == 'Was there a man dismayed?')"

    # Code *NOT* already prefixed by "(" and suffixed by ")".
    is_valid_code_undelimited = "{obj} == 'All in the valley of Death'"

    # Assert that a beartype validator preserves delimited code as is.
    validator_delimited = BeartypeValidator(
        is_valid_code=is_valid_code_delimited, **kwargs)
    assert validator_delimited._is_valid_code is is_valid_code_delimited

    # Assert that this validator reports the expected diagnosis.
    validator_delimited_diagnosis = validator_delimited.get_diagnosis(
        obj='Flashed all their sabres bare,',
        indent_level_outer='    ',
        indent_level_inner='',
    )
    assert 'True' in validator_delimited_diagnosis
    assert 'Someone had blundered.' in validator_delimited_diagnosis

    # Assert that a beartype validator delimits undelimited code as well as
    # providing non-default validation diagnoses.
    validator_undelimited = BeartypeValidator(
        is_valid_code=is_valid_code_undelimited, **kwargs)
    assert (
        validator_undelimited._is_valid_code ==
        f'({is_valid_code_undelimited})'
    )

    # Assert that a beartype validator also accepts a string representer.
    validator_repr_str = BeartypeValidator(
        is_valid_code=is_valid_code_delimited,
        get_repr='All that was left of them,',
        **kwargs_sans_get_repr
    )

    # Assert these objects have the expected representations.
    assert 'Someone had blundered.' in repr(validator_delimited)
    assert repr(validator_repr_str) == 'All that was left of them,'


def test_api_vale_validator_fail() -> None:
    '''
    Test unsuccessful usage of the private
    :class:`beartype.vale._core._valecore.BeartypeValidator` class.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype.vale._core._valecore import BeartypeValidator
    from pytest import raises

    # Arbitrary valid data validator.
    into_the_jaws_of_death = lambda text: bool('Into the mouth of hell')

    # Assert that attempting to instantiate the "BeartypeValidator" class with
    # non-string code raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        BeartypeValidator(
            is_valid=into_the_jaws_of_death,
            is_valid_code=b'Into the jaws of Death,',
            is_valid_code_locals={'yum': into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Assert that attempting to instantiate the "BeartypeValidator" class with
    # empty code raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        BeartypeValidator(
            is_valid=into_the_jaws_of_death,
            is_valid_code='',
            is_valid_code_locals={'yum': into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Assert that attempting to instantiate the "BeartypeValidator" class with
    # code *NOT* containing the substring "{obj}" raises the expected
    # exception.
    with raises(BeartypeValeSubscriptionException):
        BeartypeValidator(
            is_valid=into_the_jaws_of_death,
            is_valid_code='Came through the jaws of Death,',
            is_valid_code_locals={'yum': into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Assert that attempting to instantiate the "BeartypeValidator" class with
    # valid code and non-dictionary code locals raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        BeartypeValidator(
            is_valid=into_the_jaws_of_death,
            is_valid_code="{obj} == 'Back from the mouth of hell,'",
            is_valid_code_locals={'yum', into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Keyword arguments passing valid code and non-dictionary code locals.
    kwargs_is_valid = dict(
        is_valid=into_the_jaws_of_death,
        is_valid_code="{obj} == 'Back from the mouth of hell,'",
        is_valid_code_locals={'yum': into_the_jaws_of_death},
    )

    # Assert that attempting to instantiate the "BeartypeValidator" class with
    # valid code and code locals but a representer of an invalid type raises
    # the expected exception.
    with raises(BeartypeValeSubscriptionException):
        BeartypeValidator(
            get_repr=b'All that was left of them,', **kwargs_is_valid)

    # Assert that attempting to instantiate the "BeartypeValidator" class with
    # valid code and code locals but an empty-string representer raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        BeartypeValidator(get_repr='', **kwargs_is_valid)

    # Assert that attempting to instantiate the "BeartypeValidator" class with
    # valid code and code locals but a C-based representer raises the expected
    # exception.
    with raises(BeartypeValeSubscriptionException):
        BeartypeValidator(get_repr=iter, **kwargs_is_valid)

    # Assert that attempting to instantiate the "BeartypeValidator" class with
    # valid code and code locals but a pure-Python representer accepting one or
    # more parameters raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        BeartypeValidator(
            get_repr=lambda rode, the, six, hundred:
                'Into the valley of Death',
            **kwargs_is_valid
        )

    #FIXME: Uncomment when inevitably needed again. *sigh*
    # # Keyword arguments passing valid code, non-dictionary code locals, and a
    # # representer.
    # kwargs_is_valid_get_repr = dict(
    #     get_repr='Spread far around and inaccessibly',
    #     **kwargs_is_valid
    # )
