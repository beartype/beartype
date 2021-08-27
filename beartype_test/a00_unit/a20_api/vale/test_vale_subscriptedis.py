#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable-based data validation unit tests.**

This submodule unit tests the private :mod:`beartype._vale._valesub` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS ~ class : subscriptedis     }....................
@skip_if_python_version_less_than('3.7.0')
def test_api_vale_subscriptedis_pass() -> None:
    '''
    Test successful usage of the private
    :mod:`beartype._vale._valesub._SubscriptedIs` class if the active Python
    interpreter targets Python >= 3.7 (and thus supports the
    ``__class_getitem__()`` dunder method) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype._vale._valesub import _SubscriptedIs

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

    # Assert the "_SubscriptedIs" class preserves delimited code as is.
    subscriptedis_delimited = _SubscriptedIs(
        is_valid_code=is_valid_code_delimited, **kwargs)
    assert subscriptedis_delimited._is_valid_code is is_valid_code_delimited

    # Assert the "_SubscriptedIs" class delimits undelimited code.
    subscriptedis_undelimited = _SubscriptedIs(
        is_valid_code=is_valid_code_undelimited, **kwargs)
    assert (
        subscriptedis_undelimited._is_valid_code ==
        f'({is_valid_code_undelimited})'
    )

    # Assert that the "_SubscriptedIs" class also accepts a string representer.
    subscriptedis_repr_str = _SubscriptedIs(
        is_valid_code=is_valid_code_delimited,
        get_repr='All that was left of them,',
        **kwargs_sans_get_repr
    )

    # Assert these objects have the expected representations.
    assert 'Someone had blundered.' in repr(subscriptedis_delimited)
    assert repr(subscriptedis_repr_str) == 'All that was left of them,'



@skip_if_python_version_less_than('3.7.0')
def test_api_vale_subscriptedis_fail() -> None:
    '''
    Test unsuccessful usage of the private
    :mod:`beartype._vale._valesub._SubscriptedIs` class if the active Python
    interpreter targets Python >= 3.7 (and thus supports the
    ``__class_getitem__()`` dunder method) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype._vale._valesub import _SubscriptedIs
    from pytest import raises

    # Arbitrary valid data validator.
    into_the_jaws_of_death = lambda text: bool('Into the mouth of hell')

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # non-string code raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(
            is_valid=into_the_jaws_of_death,
            is_valid_code=b'Into the jaws of Death,',
            is_valid_code_locals={'yum': into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # empty code raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(
            is_valid=into_the_jaws_of_death,
            is_valid_code='',
            is_valid_code_locals={'yum': into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # code *NOT* containing the substring "{obj}" raises the expected
    # exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(
            is_valid=into_the_jaws_of_death,
            is_valid_code='Came through the jaws of Death,',
            is_valid_code_locals={'yum': into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # valid code and non-dictionary code locals raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(
            is_valid=into_the_jaws_of_death,
            is_valid_code="{obj} == 'Back from the mouth of hell,'",
            is_valid_code_locals={'yum', into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Keyword arguments passing valid code and non-dictionary code locals.
    kwargs_good = dict(
        is_valid=into_the_jaws_of_death,
        is_valid_code="{obj} == 'Back from the mouth of hell,'",
        is_valid_code_locals={'yum': into_the_jaws_of_death},
    )

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # valid code and code locals but a representer of an invalid type raises
    # the expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(get_repr=b'All that was left of them,', **kwargs_good)

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # valid code and code locals but an empty-string representer raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(get_repr='', **kwargs_good)

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # valid code and code locals but a C-based representer raises the expected
    # exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(get_repr=iter, **kwargs_good)

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # valid code and code locals but a pure-Python representer accepting one or
    # more arguments raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(
            get_repr=lambda rode, the, six, hundred:
                'Into the valley of Death',
            **kwargs_good
        )
