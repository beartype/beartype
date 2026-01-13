#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646`-compliant **type hint test data.**
'''

# ....................{ FIXTURES ~ meta                    }....................
def hints_pep646_meta() -> (
    'list[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPepMetadata]'):
    '''
    List of :pep:`646`-compliant **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPepMetadata`
    instances describing test-specific :pep:`646`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = []

    # If the active Python interpreter targets Python < 3.11, this interpreter
    # fails to support PEP 646. In this case, return the empty list.
    if not IS_PYTHON_AT_LEAST_3_11:
        return hints_pep_meta
    # Else, the active Python interpreter targets Python >= 3.11 and thus
    # supports PEP 646.

    # ..................{ IMPORTS ~ version                  }..................
    # Defer version-specific imports.
    from beartype.typing import NewType
    from beartype._data.hint.sign.datahintsigns import (
        HintSignPep484585GenericSubbed,
        HintSignPep646TupleFixedVariadic,
        HintSignPep646TupleUnpacked,
        HintSignPep646TypeVarTupleUnpacked,
    )
    from beartype._util.hint.pep.proposal.pep646692 import (
        make_hint_pep646_tuple_unpacked_prefix,
        make_hint_pep646_tuple_unpacked_subbed,
        # make_hint_pep646_typevartuple_unpacked_prefix,
        # make_hint_pep646_typevartuple_unpacked_subbed,
    )
    from beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta import (
        HintPepMetadata,
        PithSatisfiedMetadata,
        PithUnsatisfiedMetadata,
    )
    from beartype_test.a00_unit.data.pep.generic.data_pep646generic import (
        Array,
        #FIXME: Test against these when time permits. So, never. *yawn*
        # DType,
        # Shape,
    )
    from beartype_test.a00_unit.data.pep.data_pep646 import (
        Ts,
        Ts_unpacked_prefix,
        Ts_unpacked_subbed,
        tuple_fixed_str_bytes_unpacked_prefix,
        tuple_fixed_str_bytes_unpacked_subbed,
        tuple_variadic_strs_unpacked_prefix,
        tuple_variadic_strs_unpacked_subbed,
    )

    # ..................{ LOCALS                             }..................
    # PEP 484-compliant aliases defined by PEP 646's "Summary Examples" section.
    Height = NewType('Height', int)
    Width = NewType('Width', int)

    # ..................{ LISTS                              }..................
    # Add PEP 646-specific test type hints to this list.
    hints_pep_meta.extend((
        # ................{ UNPACKED ~ tuple                   }................
        # PEP 646-compliant unpacked child tuple type hints in both:
        # * Sugar-free "*"-prefixed flavour.
        # * Sugar-free "typing.Unpack[...]"-subscripted flavour.
        #
        # Since unpacked child hints are contextually valid *ONLY* when
        # subscripting PEP 646-compliant parent tuple type hints, this metadata
        # exists mostly just to validate that beartype correctly disambiguates
        # the signs of these hints.
        HintPepMetadata(
            hint=make_hint_pep646_tuple_unpacked_prefix((int, str,)),
            pep_sign=HintSignPep646TupleUnpacked,
            is_pep585_builtin_subbed=True,
            is_supported=False,
        ),
        HintPepMetadata(
            hint=make_hint_pep646_tuple_unpacked_subbed((bytes, float,)),
            pep_sign=HintSignPep646TupleUnpacked,
            is_supported=False,
        ),

        # ................{ UNPACKED ~ typevartuple            }................
        # PEP 646-compliant unpacked child type variable tuple hints in both:
        # * Sugar-free "*"-prefixed flavour.
        # * Sugar-free "typing.Unpack[...]"-subscripted flavour.
        #
        # Since unpacked child hints are contextually valid *ONLY* when
        # subscripting PEP 646-compliant parent tuple type hints, this metadata
        # exists mostly just to validate that beartype correctly disambiguates
        # the signs of these hints.
        HintPepMetadata(
            hint=Ts_unpacked_prefix,
            pep_sign=HintSignPep646TypeVarTupleUnpacked,
            is_args=True,
            is_ignorable=True,
            is_supported=False,
            typeargs_packed=(Ts,),
        ),
        HintPepMetadata(
            hint=Ts_unpacked_subbed,
            pep_sign=HintSignPep646TypeVarTupleUnpacked,
            is_args=True,
            is_ignorable=True,
            is_supported=False,
            typeargs_packed=(Ts,),
        ),

        # ................{ TUPLE ~ tuple                      }................
        #FIXME: Test all possible combinations of:
        #* Fixed- and variable-length child unpacked tuple hints.
        #* Parent tuple hints either:
        #  * Prefixed by either one or more *OR* no other child hints.
        #  * Suffixed by either one or more *OR* no other child hints.
        #
        #Since there are *TONS* of different combinations, we currently only
        #guard against regressions by testing combinations known to have
        #previously failed. *shrug*

        # PEP 585-compliant tuple hint subscripted by (in order):
        # * One or more arbitrary PEP-noncompliant child hints.
        # * A PEP 646-compliant child unpacked fixed-length tuple hints in both:
        #   * Sugar-free "*"-prefixed flavour.
        #   * Sugar-free "typing.Unpack[...]"-subscripted flavour.
        HintPepMetadata(
            hint=tuple[int, float, tuple_variadic_strs_unpacked_prefix],
            pep_sign=HintSignPep646TupleFixedVariadic,
            is_pep585_builtin_subbed=True,
            isinstanceable_type=tuple,
            piths_meta=(
                # Tuple deeply satisfying this hint.
                PithSatisfiedMetadata((
                    91, 0.11382,
                    'Held struggle with his throat', 'but came not forth;',
                )),
                #FIXME: Also test tuples *NOT* satisfying this hint *AFTER*
                #deeply type-checking PEP 646-compliant tuple hints.
                # String constant.
                PithUnsatisfiedMetadata('For as in the theatres of crowded men'),
            ),
        ),
        HintPepMetadata(
            hint=tuple[int, float, tuple_variadic_strs_unpacked_subbed],
            pep_sign=HintSignPep646TupleFixedVariadic,
            is_pep585_builtin_subbed=True,
            isinstanceable_type=tuple,
            piths_meta=(
                # Tuple deeply satisfying this hint.
                PithSatisfiedMetadata((
                    91, 0.11382,
                    'Held struggle with his throat', 'but came not forth;',
                )),
                #FIXME: Also test tuples *NOT* satisfying this hint *AFTER*
                #deeply type-checking PEP 646-compliant tuple hints.
                # String constant.
                PithUnsatisfiedMetadata('For as in the theatres of crowded men'),
            ),
        ),

        # PEP 585-compliant tuple hint subscripted by (in order):
        # * One or more arbitrary PEP-noncompliant child hints.
        # * A PEP 646-compliant child unpacked fixed-length tuple hints in both:
        #   * Sugar-free "*"-prefixed flavour.
        #   * Sugar-free "typing.Unpack[...]"-subscripted flavour.
        # * One or more arbitrary PEP-noncompliant child hints.
        HintPepMetadata(
            hint=tuple[
                int, float,
                tuple_fixed_str_bytes_unpacked_prefix,
                bool, complex,
            ],
            pep_sign=HintSignPep646TupleFixedVariadic,
            is_pep585_builtin_subbed=True,
            isinstanceable_type=tuple,
            piths_meta=(
                # Tuple deeply satisfying this hint.
                PithSatisfiedMetadata((
                    4, 7.80147,
                    "He spake, and ceas'd,", b'the while a heavier threat',
                    False, 9 + 1j,
                )),
                #FIXME: Also test tuples *NOT* satisfying this hint *AFTER*
                #deeply type-checking PEP 646-compliant tuple hints.
                # String constant.
                PithUnsatisfiedMetadata(
                    'And bid old Saturn take his throne again."—'),
            ),
        ),
        HintPepMetadata(
            hint=tuple[
                int, float,
                tuple_fixed_str_bytes_unpacked_subbed,
                bool, complex,
            ],
            pep_sign=HintSignPep646TupleFixedVariadic,
            is_pep585_builtin_subbed=True,
            isinstanceable_type=tuple,
            piths_meta=(
                # Tuple deeply satisfying this hint.
                PithSatisfiedMetadata((
                    4, 7.80147,
                    "He spake, and ceas'd,", b'the while a heavier threat',
                    False, 9 + 1j,
                )),
                #FIXME: Also test tuples *NOT* satisfying this hint *AFTER*
                #deeply type-checking PEP 646-compliant tuple hints.
                # String constant.
                PithUnsatisfiedMetadata(
                    'And bid old Saturn take his throne again."—'),
            ),
        ),

        # ................{ GENERICS ~ multiple                }................
        # PEP 646-compliant generic subclassing the standard PEP 484-compliant
        # "typing.Generic" superclass parametrized by a PEP 484-compliant type
        # variable followed by a PEP 646-compliant unpacked type variable tuple
        # subscripted by one builtin type and two PEP 484-compliant aliases.
        #
        # This example derives from PEP 646's "Summary Examples" section.
        HintPepMetadata(
            hint=Array[float, Height, Width],
            pep_sign=HintSignPep484585GenericSubbed,
            generic_type=Array,
            is_type_typing=True,
            is_typing=False,
            piths_meta=(
                # Generic instance.
                PithSatisfiedMetadata(Array()),
                # String constant.
                PithUnsatisfiedMetadata(
                    'Or the familiar visiting of one'),
            ),
        ),
    ))

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta


def hints_pep646_reduction_meta() -> (
    'list[beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta.HintReductionABC]'):
    '''
    List of :pep:`646`-compliant **type hint reduction metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta.HintReductionABC`
    instances describing test-specific :pep:`646`-compliant sample type hints
    with metadata generically leveraged by PEP-agnostic unit tests validating
    the :func:`beartype._check.convert.reduce.redmain.reduce_hint` function).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

    # ....................{ CLASSES                        }....................
    # class GloomBird(TypedDict):
    #     '''
    #     Arbitrary :pep:`589`-compliant typed dictionary.
    #     '''
    #
    #     pass

    # ....................{ LOCALS                         }....................
    # List of all PEP-specific type hint reduction metadata to be returned.
    hints_pep_reduction_meta = []

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # ....................{ IMPORTS                    }....................
        # Defer version-specific imports.
        from beartype.roar import BeartypeDecorHintPep646Exception
        from beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta import (
            HintReductionInvalid,
            HintReductionValid,
        )
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            Ts_unpacked,
            Ts_unpacked_prefix,
            Ts_unpacked_subbed,
            Us_unpacked,
            tuple_fixed_str_bytes_unpacked_prefix,
            tuple_fixed_str_bytes_unpacked_subbed,
            tuple_variadic_strs_unpacked_prefix,
            tuple_variadic_strs_unpacked_subbed,
        )

        # ....................{ LOCALS                     }....................
        # List of all PEP-specific type hint reduction metadata to be returned.
        hints_pep_reduction_meta.extend((
            # ..................{ VALID                      }..................
            # A PEP 646-compliant tuple hint subscripted by *ONLY* a single PEP
            # 646-compliant unpacked type variable tuple in both prefixed and
            # subscripted flavours reduces to the semantically equivalent
            # builtin "tuple" type.
            HintReductionValid(
                hint_unreduced=tuple[Ts_unpacked_prefix], hint_reduced=tuple),
            HintReductionValid(
                hint_unreduced=tuple[Ts_unpacked_subbed], hint_reduced=tuple),

            # A PEP 646-compliant tuple hint subscripted by *ONLY* a single PEP
            # 646-compliant unpacked child variable-length tuple hint in both
            # prefixed and subscripted flavours reduces to the semantically
            # equivalent PEP 585-compliant variable-length tuple hint
            # subscripted by the same child hints as that unpacked child hint.
            HintReductionValid(
                hint_unreduced=tuple[tuple_variadic_strs_unpacked_prefix],
                hint_reduced=tuple[str, ...],
            ),
            HintReductionValid(
                hint_unreduced=tuple[tuple_variadic_strs_unpacked_subbed],
                hint_reduced=tuple[str, ...],
            ),

            # A PEP 646-compliant tuple hint subscripted by a PEP 646-compliant
            # unpacked child fixed-length tuple hint in both prefixed and
            # subscripted flavours reduces to the semantically equivalent PEP
            # 585-compliant fixed-length tuple hint.
            HintReductionValid(
                hint_unreduced=tuple[
                    int, tuple_fixed_str_bytes_unpacked_prefix, float],
                hint_reduced=tuple[int, str, bytes, float],
            ),
            HintReductionValid(
                hint_unreduced=tuple[
                    int, tuple_fixed_str_bytes_unpacked_subbed, float],
                hint_reduced=tuple[int, str, bytes, float],
            ),

            # ..................{ INVALID                    }..................
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
                    tuple_fixed_str_bytes_unpacked_prefix,
                    bool,
                    tuple_fixed_str_bytes_unpacked_subbed,
                    bytes,
                ],
                exception_type=BeartypeDecorHintPep646Exception,
            ),

            # A PEP 646-compliant tuple hint subscripted by two PEP
            # 646-compliant unpacked type variable tuples separated by other
            # unrelated child hints is invalid.
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
                    tuple_fixed_str_bytes_unpacked_prefix,
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
                    tuple_fixed_str_bytes_unpacked_subbed,
                    bytes,
                ],
                exception_type=BeartypeDecorHintPep646Exception,
            ),
        ))
    # Else, the active Python interpreter targets Python < 3.11 and thus fails
    # to support PEP 646.

    # ....................{ RETURN                         }....................
    # Return this list.
    return hints_pep_reduction_meta
