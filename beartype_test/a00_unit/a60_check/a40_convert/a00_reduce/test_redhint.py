#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint reduction** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.convert._reduce.redmain` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytmark import ignore_warnings

# ....................{ TESTS ~ reducers                   }....................
#FIXME: This unit test is getting a bit long in the tooth. Consider splitting
#into smaller PEP-specific unit tests using the same pseudo-fixture approach as
#implemented by the "beartype_test.a00_unit.data.hint.pep.data_pepfixture"
#submodule.
def test_reduce_hint(
    hints_reduction_meta: (
        'tuple[beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta.HintReductionABC]')) -> None:
    '''
    Test the private
    :func:`beartype._check.convert._reduce.redmain.reduce_hint` reducer.

    Parameters
    ----------
    hints_reduction_meta : 'tuple[beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta.HintReductionABC]
        Tuple of all PEP-agnostic type hint reduction metadata to be tested.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype._check.convert._reduce.redmain import (
        reduce_hint_caller_external)
    from beartype._check.metadata.call.callmetadecormin import (
        minify_decor_meta_kwargs)
    from beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta import (
        HintReductionInvalid,
        HintReductionValid,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # For each reduction case...
    for hint_reduction_meta in hints_reduction_meta:
        #FIXME: *NON-IDEAL.* Refactor as follows:
        #* "hint_reduction_meta" should define a single "decor_meta_kwargs:
        #  DictStrToAny" instance variable rather than "cls_stack" and "conf",
        #  defaulting to the empty frozen dictionary.
        #* Then trivially pass that dictionary here as:
        #      call_meta = minify_decor_meta_kwargs(
        #          # Arbitrary callable annotated by one or more arbitrary type hints,
        #          # passed purely to satisfy API constraints.
        #          func=test_reduce_hint,
        #          **kwargs
        #      )

        # Beartype decorator call metadata, resolving forward references
        # relative to the body of this unit test for simplicity.
        call_meta = minify_decor_meta_kwargs(
            cls_stack=hint_reduction_meta.cls_stack,
            conf=hint_reduction_meta.conf,
            # Arbitrary callable annotated by one or more arbitrary type hints,
            # passed purely to satisfy API constraints.
            func=test_reduce_hint,
        )

        # If this is case encapsulates a valid reduction...
        if isinstance(hint_reduction_meta, HintReductionValid):
            # Sanified metadata encapsulating the reduction of this input hint.
            hint_reduced_sane = reduce_hint_caller_external(
                call_meta=call_meta,
                hint=hint_reduction_meta.hint_unreduced,
                conf=hint_reduction_meta.conf,
            )

            # Assert that this reduction produced the expected output hint.
            assert hint_reduced_sane.hint == hint_reduction_meta.hint_reduced
        # Else, this case encapsulates an invalid reduction by elimination.
        else:
            # Assert this to be the case.
            assert isinstance(hint_reduction_meta, HintReductionInvalid)

            # Assert that this reducer raises the expected type of exception
            # when passed this input hint.
            with raises(hint_reduction_meta.exception_type):
                reduce_hint_caller_external(
                    call_meta=call_meta,
                    hint=hint_reduction_meta.hint_unreduced,
                    conf=hint_reduction_meta.conf,
                )

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
    from beartype._check.convert._reduce.redmain import (
        reduce_hint_caller_external)
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP_UNIGNORABLE)

    # Assert this tester accepts ignorable type hints.
    for hint_ignorable in hints_ignorable:
        assert reduce_hint_caller_external(hint_ignorable) is (
            HINT_SANE_IGNORABLE)

    # Assert this tester rejects unignorable PEP-noncompliant type hints.
    for hint_unignorable in HINTS_NONPEP_UNIGNORABLE:
        assert reduce_hint_caller_external(hint_unignorable) is not (
            HINT_SANE_IGNORABLE)

    # Assert this tester:
    # * Accepts unignorable PEP-compliant type hints.
    # * Rejects ignorable PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        # True only if this hint reduces to the ignorable "Any" singleton.
        is_hint_ignorable = (
            reduce_hint_caller_external(hint_pep_meta.hint) is
            HINT_SANE_IGNORABLE
        )

        # Assert this hint is either ignorable or unignorable as expected.
        assert hint_pep_meta.is_ignorable == is_hint_ignorable
