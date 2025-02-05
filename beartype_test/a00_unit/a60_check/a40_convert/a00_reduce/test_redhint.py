#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint reduction** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.convert._reduce.redhint` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytmark import ignore_warnings

# ....................{ TESTS ~ reducers                   }....................
def test_reduce_hint() -> None:
    '''
    Test the private
    :func:`beartype._check.convert._reduce.redhint.reduce_hint` reducer.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintNonpepNumpyException
    from beartype.typing import (
        Annotated,
    )
    from beartype.vale import IsEqual
    from beartype._cave._cavefast import NoneType
    from beartype._check.convert._reduce.redhint import reduce_hint
    from beartype._conf.confcls import BeartypeConf
    from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
    from beartype._data.cls.datacls import TYPES_PEP484_GENERIC_IO
    from beartype._data.hint.datahinttyping import (
        Pep484TowerComplex,
        Pep484TowerFloat,
    )
    from beartype._data.hint.pep.sign.datapepsigns import HintSignAnnotated
    from beartype._util.hint.pep.proposal.pep593 import is_hint_pep593
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    # from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
    #     T_int,
    #     T_str_or_bytes,
    # )
    from beartype_test._util.module.pytmodtest import is_package_numpy
    from dataclasses import InitVar
    from pytest import raises

    # Intentionally import PEP 484-specific type hint factories.
    from typing import Protocol

    # ..................{ LOCALS                             }..................
    # Keyword arguments to be passed to all calls to reduce_hints() below.
    kwargs = {
        'conf': BEARTYPE_CONF_DEFAULT,
    }

    # ..................{ CORE                               }..................
    # Assert this reducer preserves an isinstanceable type as is.
    assert reduce_hint(hint=int, **kwargs) is int

    # Assert this reducer reduces "None" to "type(None)".
    assert reduce_hint(hint=None, **kwargs) is NoneType

    # ..................{ PEP 484 ~ tower                    }..................
    # Assert this reducer expands the builtin "float" and "complex" types to
    # their corresponding numeric towers when configured to do so.
    assert reduce_hint(
        hint=float,
        conf=BeartypeConf(is_pep484_tower=True),
    ) is Pep484TowerFloat
    assert reduce_hint(
        hint=complex,
        conf=BeartypeConf(is_pep484_tower=True),
    ) is Pep484TowerComplex

    # Assert this reducer preserves the builtin "float" and "complex" types as
    # is when configured to disable the implicit numeric tower.
    assert reduce_hint(
        hint=float,
        conf=BeartypeConf(is_pep484_tower=False),
    ) is float
    assert reduce_hint(
        hint=complex,
        conf=BeartypeConf(is_pep484_tower=False),
    ) is complex

    #FIXME: Excise us up, please. We no longer reduce type variables. *sigh*
    # # ..................{ PEP 484 ~ typevar                  }..................
    # # Assert this reducer preserves unbounded type variables as is.
    # assert reduce_hint(hint=T, **kwargs) is T
    #
    # # Assert this reducer reduces bounded type variables to their upper bound.
    # assert reduce_hint(hint=T_int, **kwargs) is int
    #
    # # Union of all constraints parametrizing a constrained type variable,
    # # reduced from that type variable.
    # typevar_constraints_union = reduce_hint(hint=T_str_or_bytes, **kwargs)
    #
    # # Assert this union contains all constraints parametrizing this variable.
    # assert str   in typevar_constraints_union.__args__
    # assert bytes in typevar_constraints_union.__args__

    # ..................{ PEP 544                            }..................
    # For each PEP 484-compliant "typing" IO generic superclass...
    for pep484_generic_io in TYPES_PEP484_GENERIC_IO:
        # Equivalent protocol reduced from this generic.
        pep544_protocol_io = reduce_hint(hint=pep484_generic_io, **kwargs)

        # Assert this protocol is either...
        assert (
            # A PEP 593-compliant type metahint generalizing a protocol
            # *OR*...
            is_hint_pep593(pep544_protocol_io) or
            # A PEP 544-compliant protocol.
            issubclass(pep544_protocol_io, Protocol)
        )

    # ..................{ PEP 557                            }..................
    # Assert this reducer reduces an "InitVar" to its subscripted argument.
    assert reduce_hint(hint=InitVar[str], **kwargs) is str

    # ..................{ PEP 593                            }..................
    # Assert this reducer reduces a beartype-agnostic metahint to the
    # lower-level hint it annotates.
    assert reduce_hint(hint=Annotated[int, 42], **kwargs) is int

    # Assert this reducer preserves a beartype-specific metahint as is.
    leaves_when_laid = Annotated[str, IsEqual['In their noonday dreams.']]
    assert reduce_hint(hint=leaves_when_laid, **kwargs) is leaves_when_laid

    # ..................{ NUMPY                              }..................
    # If a recent version of NumPy is importable...
    if is_package_numpy():
        # Defer third party imports.
        from numpy import float64
        from numpy.typing import NDArray

        # Beartype validator reduced from such a hint.
        ndarray_reduced = reduce_hint(hint=NDArray[float64], **kwargs)

        # Assert this validator is a "typing{_extensions}.Annotated" hint.
        assert get_hint_pep_sign(ndarray_reduced) is HintSignAnnotated

        # Assert that reducing a "numpy.typing.NDArray" type hint
        # erroneously subscripted by an object *NOT* reducible to a data
        # type raises the expected exception.
        with raises(BeartypeDecorHintNonpepNumpyException):
            reduce_hint(
                hint=NDArray['From_my_wings_are_shaken_the_dews_that_waken'],
                **kwargs
            )

# ....................{ TESTS ~ raiser                     }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by this test. Urgh!
@ignore_warnings(DeprecationWarning)
def test_reduce_hint_ignorable(hints_pep_meta, hints_ignorable) -> None:
    '''
    Test the private
    :func:`beartype._check.convert._reduce.redhint.reduce_hint` reducer with
    respect to ignorable hints.

    Parameters
    ----------
    hints_pep_meta : tuple[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        Tuple of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    hints_ignorable : frozenset
        Frozen set of ignorable PEP-agnostic type hints.
    '''

    # Defer test-specific imports.
    from beartype.typing import Any
    from beartype._check.convert._reduce.redhint import reduce_hint
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP_UNIGNORABLE)

    # Assert this tester accepts ignorable type hints.
    for hint_ignorable in hints_ignorable:
        assert reduce_hint(hint_ignorable) is Any

    # Assert this tester rejects unignorable PEP-noncompliant type hints.
    for hint_unignorable in HINTS_NONPEP_UNIGNORABLE:
        assert reduce_hint(hint_unignorable) is not Any

    # Assert this tester:
    # * Accepts unignorable PEP-compliant type hints.
    # * Rejects ignorable PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        # True only if this hint reduces to the ignorable "Any" singleton.
        is_hint_ignorable = reduce_hint(hint_pep_meta.hint) is Any

        # Assert this hint is either ignorable or unignorable as expected.
        assert hint_pep_meta.is_ignorable == is_hint_ignorable
