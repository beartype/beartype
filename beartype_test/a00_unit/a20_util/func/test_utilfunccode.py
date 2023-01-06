#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable source code utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.utilfunccode` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ code                       }....................
def test_get_func_code_or_none() -> None:
    '''
    Test usage of the
    :func:`beartype._util.func.utilfunccode.get_func_code_or_none`
    function.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype.roar._roarwarn import _BeartypeUtilCallableWarning
    from beartype._util.func.utilfunccode import get_func_code_or_none
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_LEAST_3_9,
        IS_PYTHON_AT_LEAST_3_11,
    )
    from beartype_test.a00_unit.data.util.func.data_utilfunccode import (
        of_vapours,
        will_be_the_dome,
        thou_dirge,
        yellow,
    )
    from collections.abc import Callable
    from pytest import warns
    from re import escape, search

    # ..................{ NON-LAMBDA                         }..................
    # Assert this getter accepts C-based callables with "None"
    assert get_func_code_or_none(iter) is None

    # Assert this getter accepts a dynamically declared callable with "None".
    assert get_func_code_or_none(of_vapours) is None

    # Assert this getter accepts a physically declared pure-Python non-lambda
    # callable with the full definition of that callable.
    assert get_func_code_or_none(will_be_the_dome) == """def will_be_the_dome():
    '''
    Arbitrary non-lambda function physically declared by this submodule.
    '''

    return 'of a vast sepulchre'
"""

    # ..................{ LAMBDA                             }..................
    def _assert_lambda_args_0_body_is(
        func: Callable,
        func_code_body: str,
    ) -> None:
        '''
        Test-specific function asserting that the body of the passed
        **argumentless lambda function** (i.e., lambda function accepting *no*
        parameters) is exactly the passed string.

        This function enables the bodies of lambda functions to be portably
        tested across distinct Python versions.

        Parameters
        ----------
        func : Callable
            Lambda function to test this string against.
        func_code_body : str
            Expected body of this lambda function to be tested for.
        '''

        # Regular expression matching the leading prefix of the source code
        # underlying this lambda.
        LAMBDA_ARGS_0_CODE_PREFIX = (
            # Under Python >= 3.11, this code is no longer erroneously prefixed
            # by an assignment statement globalizing this lambda.
            r'lambda: '
            if IS_PYTHON_AT_LEAST_3_11 else
            # Under Python 3.9 and 3.10, this code is typically erroneously
            # prefixed by an assignment statement globalizing this lambda but
            # nonetheless has an accidental space inserted inappropriately.
            r'lambda : '
            if IS_PYTHON_AT_LEAST_3_9 else
            # Under Python < 3.9, this code is typically erroneously prefixed
            # by an assignment statement globalizing this lambda.
            r'(.*? = )lambda: '
        )

        # Regular expression matching this prefix followed by this body,
        # escaped to avoid unsafe interpretation as regular expressions.
        func_code_regex = (
            fr'^{LAMBDA_ARGS_0_CODE_PREFIX}{escape(func_code_body)}$')

        # Original source code of this lambda.
        func_code = get_func_code_or_none(func)

        # Assert this code is prefixed by the expected substring followed by the
        # passed body of this lambda.
        assert search(pattern=func_code_regex, string=func_code) is not None


    # If the active Python interpreter targets Python >= 3.9 and thus defines
    # requisite AST machinery enabling this getter to return exact rather than
    # inexact definitions for lambda functions...
    if IS_PYTHON_AT_LEAST_3_9:
        # Assert this getter accepts a physically declared pure-Python lambda
        # function in which only one lambda is declared on its source code line
        # with the embedded definition of that function.
        _assert_lambda_args_0_body_is(
            func=thou_dirge,
            func_code_body="'Of the dying year, to which this closing night'",
        )

        # Assert this getter accepts a physically declared pure-Python lambda
        # functions in which multiple lambdas are declared on the same source
        # code line with the embedded definition of the first such function and
        # a non-fatal warning disclosing this inconvenience to the caller.
        with warns(_BeartypeUtilCallableWarning):
            _assert_lambda_args_0_body_is(
                func=yellow[0],
                func_code_body="'and black,'",
            )
    # Else, the active Python interpreter targets only Python < 3.9 and thus
    # does *NOT* define that machinery. In this case...
    else:
        # Assert this getter accepts a physically declared pure-Python lambda
        # function in which only one lambda is declared on its source code line
        # with the entire line.
        _assert_lambda_args_0_body_is(
            func=thou_dirge,
            func_code_body="'Of the dying year, to which this closing night'\n",
        )

# ....................{ TESTS ~ label                      }....................
#FIXME: This getter no longer has a sane reason to exist. Consider excising.
# def test_get_func_code_label() -> None:
#     '''
#     Test usage of the
#     :func:`beartype._util.func.utilfunccode.get_func_code_label` function.
#     '''
#
#     # Defer test-specific imports.
#     from beartype.roar._roarexc import _BeartypeUtilCallableException
#     from beartype._util.func.utilfunccode import get_func_code_label
#     from beartype_test.a00_unit.data.data_type import (
#         CALLABLES_C,
#         CALLABLES_PYTHON,
#         MODULE_FILENAME,
#         NON_CALLABLES,
#     )
#
#     # Assert this getter returns the expected label for pure-Python callables.
#     for callable_python in CALLABLES_PYTHON:
#         assert get_func_code_label(callable_python) == MODULE_FILENAME
#
#     # Assert this getter returns the expected label for C-based callables.
#     for callable_c in CALLABLES_C:
#         assert get_func_code_label(callable_c) == '<C-based>'
#
#     # Assert this getter raises the expected exception for non-callables.
#     for non_callable in NON_CALLABLES:
#         with raises(_BeartypeUtilCallableException):
#             get_func_code_label(non_callable)
