#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`593` **type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep593` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                    }....................
def test_is_hint_pep593_beartype() -> None:
    '''
    Test usage of the private
    :mod:`beartype._util.hint.pep.proposal.utilpep593.is_hint_pep593_beartype`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintPepException,
        BeartypeValeLambdaWarning,
    )
    from beartype.vale import Is
    from beartype._util.hint.pep.proposal.utilpep593 import (
        is_hint_pep593_beartype)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from pytest import raises, warns

    # If the active Python interpreter targets at least Python >= 3.9 and thus
    # supports PEP 593...
    if IS_PYTHON_AT_LEAST_3_9:
        # Defer version-specific imports.
        from typing import Annotated

        # Assert this tester accepts beartype-specific metahints.
        #
        # Unfortunately, this test actually induces an error in CPython, which
        # our codebase emits as a non-fatal warning. Specifically, CPython
        # reports the "func.__code__.co_firstlineno" attribute of the nested
        # lambda function defined below to be one less than the expected value.
        # Since this issue is unlikely to be resolved soon *AND* since we have
        # no means of monkey-patching CPython itself, we acknowledge the
        # existence of this warning by simply ignoring it. *sigh*
        with warns(BeartypeValeLambdaWarning):
            assert is_hint_pep593_beartype(Annotated[
                str, Is[lambda text: bool(text)]]) is True

        # Assert this tester rejects beartype-agnostic metahints.
        assert is_hint_pep593_beartype(Annotated[
            str, 'And may there be no sadness of farewell']) is False

    # Assert this tester raises the expected exception when passed a
    # non-metahint in either case.
    with raises(BeartypeDecorHintPepException):
        is_hint_pep593_beartype('When I embark;')
