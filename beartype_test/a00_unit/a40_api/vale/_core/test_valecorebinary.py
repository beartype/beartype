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
#FIXME: Uncomment after refactoring "BeartypeValidatorBinaryABC", please.
# def test_api_vale_validator_conjunction() -> None:
#     '''
#     Test successful usage of the private
#     :class:`beartype.vale._core._valecore.BeartypeValidatorConjunction` class.
#     '''
#
#     # Defer test-specific imports.
#     from beartype.roar import BeartypeValeSubscriptionException
#     from beartype.vale._core._valecore import BeartypeValidator
#     from beartype.vale._core._valecorebinary import (
#         BeartypeValidatorConjunction)
#     from pytest import raises
#
#     not_though_the_soldier_knew = lambda text: bool('Someone had blundered.')
#     validator_operand_1 = BeartypeValidator(
#         is_valid_code="({obj} == 'Was there a man dismayed?')",
#         is_valid=not_though_the_soldier_knew,
#         is_valid_code_locals={'yum': not_though_the_soldier_knew},
#         get_repr=lambda: "Is[lambda text: bool('Someone had blundered.')]",
#     )
#
#     # Assert that a beartype validator preserves delimited code as is.
#     validator_delimited = BeartypeValidatorConjunction(
#         validator_operand_1=validator_operand_1,
#     )
#
#     # Assert that attempting to instantiate the "BeartypeValidator" class with
#     # non-string code raises the expected exception.
#     with raises(BeartypeValeSubscriptionException):
         
