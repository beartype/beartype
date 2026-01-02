#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint reduction** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.convert._reduce.redmain` submodule.
'''

# ....................{ TODO                               }....................
#FIXME: We've currently split some PEP-specific hint_reduce() unit tests into
#PEP-specific submodules of this subpackage (e.g., "pep.test_redpep695"). The
#the test_reduce() unit test defined below is dramatically superior, however.
#Why? Internal dataclass machinery uniquely implemented in this test automates
#away associated unpleasantness. Thus, for maintainability, *ALL* of those
#submodules should be:
#* Integrated into the sole test_reduce_hint() unit test defined below. Yes,
#  this test will begin to become uncomfortably long. Who cares? Well,
#  technically, *WE* care -- but not that much. Long tests can later be
#  subdivided. The critical point is that test_reduce() machinery is superior.
#* Subsequently removed.

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytmark import ignore_warnings

# ....................{ TESTS ~ reducers                   }....................
#FIXME: This unit test is getting a bit long in the tooth. Consider splitting
#into smaller PEP-specific unit tests using the same pseudo-fixture approach as
#implemented by the "beartype_test.a00_unit.data.hint.pep.data_pepfixture" submodule.
def test_reduce_hint() -> None:
    '''
    Test the private
    :func:`beartype._check.convert._reduce.redmain.reduce_hint` reducer.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.typing import (
        Annotated,
    )
    from beartype.vale import IsEqual
    from beartype._cave._cavefast import NoneType
    from beartype._check.convert._reduce.redmain import reduce_hint
    from beartype._conf.confmain import BeartypeConf
    from beartype._data.cls.datacls import TYPES_PEP484_GENERIC_IO
    from beartype._data.typing.datatyping import (
        Pep484TowerComplex,
        Pep484TowerFloat,
    )
    from beartype._data.hint.sign.datahintsigns import HintSignAnnotated
    from beartype._util.hint.pep.proposal.pep484604 import (
        make_hint_pep484604_union)
    from beartype._util.hint.pep.proposal.pep593 import is_hint_pep593
    from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta import (
        HintReductionInvalid,
        HintReductionValid,
    )
    from beartype_test.a00_unit.data.pep.data_pep484 import (
        T_str_or_bytes)
    # from beartype_test._util.kind.pytkindmake import make_container_from_funcs
    from beartype_test._util.module.pytmodtest import is_package_numpy
    from dataclasses import InitVar
    from pytest import raises

    # Intentionally import PEP 484-specific type hint factories.
    from typing import Protocol

    # ..................{ LOCALS                             }..................
    # List of all valid reduction cases to be tested.
    hint_reductions_valid = [
        # ..................{ PEP 484                        }..................
        # An isinstanceable type is preserved as is without reduction.
        HintReductionValid(int),

        # The builtin "None" singleton reduces to its type (i.e., "type(None)").
        HintReductionValid(hint_unreduced=None, hint_reduced=NoneType),

        # ..................{ PEP 484 ~ tower                }..................
        # The builtin "float" and "complex" types reduce to their corresponding
        # numeric towers when configured to do so.
        HintReductionValid(
            hint_unreduced=float,
            hint_reduced=Pep484TowerFloat,
            conf=BeartypeConf(is_pep484_tower=True),
        ),
        HintReductionValid(
            hint_unreduced=complex,
            hint_reduced=Pep484TowerComplex,
            conf=BeartypeConf(is_pep484_tower=True),
        ),

        # The builtin "float" and "complex" types are preserved as is without
        # being reduced when configured to do so.
        HintReductionValid(
            hint_unreduced=float,
            hint_reduced=float,
            conf=BeartypeConf(is_pep484_tower=False),
        ),
        HintReductionValid(
            hint_unreduced=complex,
            hint_reduced=complex,
            conf=BeartypeConf(is_pep484_tower=False),
        ),

        # ..................{ PEP 484 ~ typevar              }..................
        # A PEP 484-compliant constrained type variable reduces to the PEP 484-
        # or 604-compliant union of those constraints.
        HintReductionValid(
            hint_unreduced=T_str_or_bytes,
            hint_reduced=make_hint_pep484604_union((str, bytes,)),
        ),

        # ..................{ PEP 557                        }..................
        # A PEP 557-compliant "InitVar" is reduced to its child hint.
        HintReductionValid(hint_unreduced=InitVar[str], hint_reduced=str),

        # ..................{ PEP 593                        }..................
        # A PEP 593-compliant beartype-agnostic metahint is reduced to the
        # lower-level hint it annotates.
        HintReductionValid(hint_unreduced=Annotated[int, 42], hint_reduced=int),

        # A PEP 593-compliant beartype-specific metahint is preserved as is.
        HintReductionValid(Annotated[str, IsEqual['In their noonday dreams.']]),
    ]

    # List of all invalid reduction cases to be tested.
    hint_reductions_invalid = []

    # ..................{ PEP 646                            }..................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # ....................{ IMPORTS                    }....................
        # Defer PEP-specific imports.
        from beartype.roar import BeartypeDecorHintPep646Exception
        from beartype._util.hint.pep.proposal.pep646692 import (
            make_hint_pep646_tuple_unpacked_prefix)
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            Ts_unpacked,
            Us_unpacked,
        )

        # ....................{ CLASSES                    }....................
        # class GloomBird(TypedDict):
        #     '''
        #     Arbitrary :pep:`589`-compliant typed dictionary.
        #     '''
        #
        #     pass

        # ....................{ LOCALS                     }....................
        # Extend this list with PEP 646-compliant valid reduction cases.
        hint_reductions_valid.extend((
            # A PEP 646-compliant tuple hint subscripted by *ONLY* a single PEP
            # 646-compliant unpacked type variable tuple reduces to the
            # semantically equivalent builtin "tuple" type.
            HintReductionValid(
                hint_unreduced=tuple[Ts_unpacked], hint_reduced=tuple),

            # A PEP 646-compliant tuple hint subscripted by *ONLY* a single PEP
            # 646-compliant unpacked child variable-length tuple hint reduces to
            # the semantically equivalent PEP 585-compliant variable-length
            # tuple hint subscripted by the same child hints as that unpacked
            # child hint.
            HintReductionValid(
                hint_unreduced=(
                    tuple[make_hint_pep646_tuple_unpacked_prefix((str, ...))]),
                hint_reduced=tuple[str, ...],
            ),

            # A PEP 646-compliant tuple hint subscripted by a PEP 646-compliant
            # unpacked child fixed-length tuple hint reduces to the semantically
            # equivalent PEP 585-compliant fixed-length tuple hint.
            HintReductionValid(
                hint_unreduced=tuple[
                    int,
                    make_hint_pep646_tuple_unpacked_prefix((str, bool)),
                    float,
                ],
                hint_reduced=tuple[int, str, bool, float],
            ),
        ))

        # Extend this list with PEP 646-compliant invalid reduction cases.
        hint_reductions_invalid.extend((
            #FIXME: *UNCOMMENT*, please. This is totally invalid but no longer
            #covered by the current implementation of this reducer. Whatevahs!
            # # A PEP 646-compliant tuple hint subscripted by a PEP 692-compliant
            # # unpacked type dictionary is invalid.
            # (
            #     tuple[Unpack[GloomBird]],
            #     BeartypeDecorHintPep646Exception,
            # ),

            # A PEP 646-compliant tuple hint subscripted by two PEP
            # 646-compliant unpacked child fixed-length tuple hint separated by
            # other unrelated child hints is invalid.
            HintReductionInvalid(
                hint_unreduced=tuple[
                    str,
                    make_hint_pep646_tuple_unpacked_prefix((int, float)),
                    bool,
                    make_hint_pep646_tuple_unpacked_prefix((complex, list)),
                    bytes,
                ],
                exception_type=BeartypeDecorHintPep646Exception,
            ),

            # A PEP 646-compliant tuple hint subscripted by two PEP 646-compliant
            # unpacked type variable tuples separated by other unrelated child hints
            # is invalid.
            HintReductionInvalid(
                hint_unreduced=(
                    tuple[str, Ts_unpacked, bool, Us_unpacked, bytes]),
                exception_type=BeartypeDecorHintPep646Exception,
            ),

            # A PEP 646-compliant tuple hint subscripted by one PEP
            # 646-compliant unpacked child variable-length tuple hint *AND* one
            # PEP 646-compliant unpacked child type variable tuple separated by
            # other unrelated child hints is invalid.
            #
            # Order is probably insignificant -- but could be. Ergo, we test
            # both orders for fuller coverage.
            HintReductionInvalid(
                hint_unreduced=tuple[
                    str,
                    make_hint_pep646_tuple_unpacked_prefix((complex, float)),
                    bool,
                    Ts_unpacked,
                    bytes,
                ],
                exception_type=BeartypeDecorHintPep646Exception,
            ),
            HintReductionInvalid(
                hint_unreduced=tuple[
                    str,
                    Ts_unpacked,
                    bool,
                    make_hint_pep646_tuple_unpacked_prefix((float, int)),
                    bytes,
                ],
                exception_type=BeartypeDecorHintPep646Exception,
            ),
        ))
    # Else, the active Python interpreter targets Python < 3.11 and thus fails
    # to support PEP 646.

    # List of all reduction cases to be tested, intentionally heterogeneously
    # mixing both valid and invalid cases.
    hint_reductions = hint_reductions_valid + hint_reductions_invalid

    # ....................{ PASS                           }....................
    # For each reduction case...
    for hint_reduction in hint_reductions:
        # If this is case encapsulates a valid reduction...
        if isinstance(hint_reduction, HintReductionValid):
            # Sanified metadata encapsulating the reduction of this input hint.
            hint_reduced_sane = reduce_hint(
                hint=hint_reduction.hint_unreduced,
                conf=hint_reduction.conf,
            )

            # Assert that this reduction produced the expected output hint.
            assert hint_reduced_sane.hint == hint_reduction.hint_reduced
        # Else, this case encapsulates an invalid reduction by elimination.
        else:
            # Assert this to be the case.
            assert isinstance(hint_reduction, HintReductionInvalid)

            # Assert that this reducer raises the expected type of exception
            # when passed this input hint.
            with raises(hint_reduction.exception_type):
                reduce_hint(
                    hint=hint_reduction.hint_unreduced,
                    conf=hint_reduction.conf,
                )

    # ..................{ PEP 544                            }..................
    # For each PEP 484-compliant "typing" IO generic superclass...
    for pep484_generic_io in TYPES_PEP484_GENERIC_IO:
        # Metadata encapsulating the equivalent PEP 544-compliant protocol
        # reduced from this generic.
        pep544_protocol_io_sane = reduce_hint(pep484_generic_io)

        # This protocol.
        pep544_protocol_io = pep544_protocol_io_sane.hint

        # Assert this protocol is either...
        assert (
            # A PEP 593-compliant type metahint generalizing a protocol *OR*...
            is_hint_pep593(pep544_protocol_io) or
            # A PEP 544-compliant protocol.
            issubclass(pep544_protocol_io, Protocol)
        )

    # ..................{ API ~ numpy                        }..................
    # If a recent version of NumPy is importable...
    if is_package_numpy():
        # Defer API-specific imports.
        from beartype.roar import BeartypeDecorHintNonpepNumpyException
        from numpy import float64
        from numpy.typing import NDArray

        # Metadata encapsulating the reduction of a NumPy array type hint to a
        # beartype validator.
        ndarray_reduced_sane = reduce_hint(NDArray[float64])

        # This beartype validator.
        ndarray_reduced = ndarray_reduced_sane.hint

        # Assert this validator is a "typing{_extensions}.Annotated" hint.
        assert get_hint_pep_sign(ndarray_reduced) is HintSignAnnotated

        # Assert that reducing a "numpy.typing.NDArray" type hint
        # erroneously subscripted by an object *NOT* reducible to a data
        # type raises the expected exception.
        with raises(BeartypeDecorHintNonpepNumpyException):
            reduce_hint(NDArray['From_my_wings_are_shaken_the_dews_that_waken'])
    # Else, a recent version of NumPy is *NOT* importable.

# ....................{ TESTS ~ raiser                     }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by this test. Urgh!
@ignore_warnings(DeprecationWarning)
def test_reduce_hint_ignorable(hints_pep_meta, hints_ignorable) -> None:
    '''
    Test the private
    :func:`beartype._check.convert._reduce.redmain.reduce_hint` reducer with
    respect to ignorable hints.

    Parameters
    ----------
    hints_pep_meta : tuple[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPepMetadata]
        Tuple of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    hints_ignorable : frozenset
        Frozen set of ignorable PEP-agnostic type hints.
    '''

    # Defer test-specific imports.
    from beartype._check.metadata.hint.hintsane import HINT_SANE_IGNORABLE
    from beartype._check.convert._reduce.redmain import reduce_hint
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP_UNIGNORABLE)

    # Assert this tester accepts ignorable type hints.
    for hint_ignorable in hints_ignorable:
        assert reduce_hint(hint_ignorable) is HINT_SANE_IGNORABLE

    # Assert this tester rejects unignorable PEP-noncompliant type hints.
    for hint_unignorable in HINTS_NONPEP_UNIGNORABLE:
        assert reduce_hint(hint_unignorable) is not HINT_SANE_IGNORABLE

    # Assert this tester:
    # * Accepts unignorable PEP-compliant type hints.
    # * Rejects ignorable PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        # True only if this hint reduces to the ignorable "Any" singleton.
        is_hint_ignorable = reduce_hint(hint_pep_meta.hint) is HINT_SANE_IGNORABLE

        # Assert this hint is either ignorable or unignorable as expected.
        assert hint_pep_meta.is_ignorable == is_hint_ignorable
