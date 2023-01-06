#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` and :pep:`585` **callable type hint utility unit
tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585.utilpep484585callable` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_get_hint_pep484585_callable_params_and_return() -> None:
    '''
    Test both the ``get_hint_pep484585_callable_params`` and
    ``get_hint_pep484585_callable_return`` getters declared by the
    :mod:`beartype._util.hint.pep.proposal.pep484585.utilpep484585callable`
    submodule.

    Since these getters are inextricably interrelated, this unit test exercises
    both within the same test to satisfy Don't Repeat Yourself (DRY).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype.typing import Any
    from beartype._data.hint.pep.sign.datapepsigns import HintSignCallable
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585callable import (
        get_hint_pep484585_callable_params,
        get_hint_pep484585_callable_return,
    )
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_LEAST_3_10,
        IS_PYTHON_AT_LEAST_3_9,
    )
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META
    from pytest import raises

    # ..................{ GENERIC                            }..................
    # General-purpose logic generically exercising these getters against all
    # globally defined type hints.

    # Assert these getters...
    for hint_pep_meta in HINTS_PEP_META:
        # Return zero or more arguments for PEP-compliant callable type hints.
        if hint_pep_meta.pep_sign is HintSignCallable:
            hint_callable_params = get_hint_pep484585_callable_params(
                hint_pep_meta.hint)
            hint_callable_return = get_hint_pep484585_callable_return(
                hint_pep_meta.hint)

            assert isinstance(hint_callable_params, tuple)
            assert hint_callable_return is not None
        # Raise an exception for concrete PEP-compliant type hints *NOT*
        # defined by the "typing" module.
        else:
            with raises(BeartypeDecorHintPep484585Exception):
                get_hint_pep484585_callable_params(hint_pep_meta.hint)
            with raises(BeartypeDecorHintPep484585Exception):
                get_hint_pep484585_callable_return(hint_pep_meta.hint)

    # Assert these getters raise the expected exception for non-PEP-compliant
    # type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPep484585Exception):
            get_hint_pep484585_callable_params(not_hint_pep)
        with raises(BeartypeDecorHintPep484585Exception):
            get_hint_pep484585_callable_return(not_hint_pep)

    # ..................{ PEP ~ 484                          }..................
    # Intentionally import the callable type hint factory from "typing" rather
    # than "beartype.typing" to guarantee PEP 484-compliance.
    from typing import Callable

    # List of 3-tuples "(callable_hint, callable_hint_params,
    # callable_hint_return)", where:
    # * "callable_hint" is a PEP-compliant callable type hint to be tested.
    # * "callable_hint_params" is the parameters type hint subscripting that
    #   callable type hint.
    # * "callable_hint_return" is the return type hint subscripting that
    #   callable type hint.
    CALLABLE_HINT_PARAMS_RETURN_CASES = [
        # PEP 484-compliant callable type hints.
        (Callable[[], Any], (), Any),
        (Callable[[int], bool], (int,), bool),
        (Callable[[int, bool], float], (int, bool), float),
        (Callable[..., bytes], Ellipsis, bytes),
    ]

    # ..................{ PEP ~ 585                          }..................
    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585...
    if IS_PYTHON_AT_LEAST_3_9:
        # Intentionally import the callable type hint factory from
        # "collections.abc" rather than "beartype.typing" to guarantee PEP
        # 585-compliance.
        from collections.abc import Callable

        # Extend this list with PEP 585-compliant callable type hints.
        CALLABLE_HINT_PARAMS_RETURN_CASES.extend((
            (Callable[[], Any], (), Any),
            (Callable[[int], bool], (int,), bool),
            (Callable[[int, bool], float], (int, bool), float),
            (Callable[..., bytes], Ellipsis, bytes),

            # Note this edge case is intentionally *NOT* tested above as a
            # PEP 484-compliant callable type hint, as the "typing.Callable"
            # factory refuses to accept the empty tuple here: e.g.,
            #     >>> from typing import Callable
            #     >>> Callable[[()], str]
            #     TypeError: Callable[[arg, ...], result]: each arg must be a
            #     type. Got ().
            (Callable[[()], str], (), str),
        ))

    # ..................{ PEP ~ 612                          }..................
    # If the active Python interpreter targets Python >= 3.10 and thus supports
    # PEP 612...
    if IS_PYTHON_AT_LEAST_3_10:
        # Defer version-specific imports.
        from beartype.typing import (
            Concatenate,
            ParamSpec,
        )

        # Arbitrary PEP 612-compliant child type hints.
        P = ParamSpec('P')
        str_plus_P = Concatenate[str, P]

        # Extend this list with PEP 585-compliant callable type hints.
        CALLABLE_HINT_PARAMS_RETURN_CASES.extend((
            (Callable[P, Any], P, Any),
            (Callable[str_plus_P, int], str_plus_P, int),
        ))

    # ..................{ PEP                                }..................
    # For each callable type hint defined above...
    for hint, hint_params, hint_return in CALLABLE_HINT_PARAMS_RETURN_CASES:
        # Parameters type hint returned by this getter for this hint.
        hint_params_actual = get_hint_pep484585_callable_params(hint)

        # If the parameters type hint subscripting this callable type hint is a
        # tuple, assert this tuple to be equal but *NOT* identical to this
        # actual tuple.
        if isinstance(hint_params, tuple):
            assert hint_params_actual == hint_params
        # Else, the parameters type hint subscripting this callable type hint is
        # a non-tuple. In this case, assert this non-tuple to be identical to
        # this actual non-tuple.
        else:
            assert hint_params_actual is hint_params

        # Assert this getter returns the expected return.
        assert get_hint_pep484585_callable_return(hint) is hint_return
