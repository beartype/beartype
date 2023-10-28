#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`604`-compliant **type hint test data.**
'''

# ....................{ FIXTURES                           }....................
def hints_pep_meta_pep604() -> 'List[HintPepMetadata]':
    '''
    Session-scoped fixture returning a list of :pep:`604`-compliant **type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific :pep:`604`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignList,
        HintSignUnion,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ..................{ LOCALS                             }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = []

    # ..................{ TUPLES                             }..................
    # If the active Python interpreter targets Python >= 3.10, this interpreter
    # support PEP 604s. In this case...
    if IS_PYTHON_AT_LEAST_3_10:
        # Add PEP 604-specific test type hints to this tuple global.
        hints_pep_meta.extend((
            # ................{ |-UNION                        }................
            # Union of one non-"typing" type and an originative "typing" type,
            # exercising a prominent edge case when raising human-readable
            # exceptions describing the failure of passed parameters or returned
            # values to satisfy this union.
            #
            # Interestingly, Python preserves this union as a PEP 604-compliant
            # |-style union rather than implicitly coercing this into a PEP
            # 484-compliant union: e.g.,
            #     >>> int | list[str]
            #     int | list[str]
            HintPepMetadata(
                hint=int | list[str],
                pep_sign=HintSignUnion,
                is_type_typing=False,
                piths_meta=(
                    # Integer constant.
                    HintPithSatisfiedMetadata(87),
                    # List of string items.
                    HintPithSatisfiedMetadata([
                        'Into, my myopic mandrake‐manhandling, '
                        'panhandling slakes of',
                        'Televisual, dis‐informative Lakes, unsaintly, of',
                    ]),
                    # Floating-point constant.
                    HintPithUnsatisfiedMetadata(
                        pith=10100.00101,
                        # Match that the exception message raised for this
                        # object declares the types *NOT* satisfied by this
                        # object.
                        exception_str_match_regexes=(
                            r'\blist\b',
                            r'\bint\b',
                        ),
                        # Match that the exception message raised for this
                        # object does *NOT* contain a newline or bullet
                        # delimiter.
                        exception_str_not_match_regexes=(
                            r'\n',
                            r'\*',
                        ),
                    ),

                    # List of integers.
                    HintPithUnsatisfiedMetadata(
                        pith=([1, 10, 271, 36995]),
                        # Match that the exception message raised for this
                        # object...
                        exception_str_match_regexes=(
                            # Contains a bullet point declaring the non-"typing"
                            # type *NOT* satisfied by this object.
                            r'\n\*\s.*\bint\b',
                            # Contains a bullet point declaring the index of the
                            # random list item *NOT* satisfying this hint.
                            r'\n\*\s.*\b[Ll]ist index \d+ item\b',
                        ),
                    ),
                ),
            ),

            # ................{ UNION ~ nested                 }................
            # Nested unions exercising edge cases induced by Python >= 3.8
            # optimizations leveraging PEP 572-style assignment expressions.

            # Nested union of multiple non-"typing" types.
            HintPepMetadata(
                hint=list[int | str],
                pep_sign=HintSignList,
                isinstanceable_type=list,
                is_pep585_builtin=True,
                piths_meta=(
                    # List containing a mixture of integer and string constants.
                    HintPithSatisfiedMetadata([
                        'Telemarketing affirmative‐mined Ketamine’s',
                        470,
                    ]),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        pith='Apolitically',
                        # Match that the exception message raised for this
                        # object declares the types *NOT* satisfied by this
                        # object.
                        exception_str_match_regexes=(
                            r'\bint\b',
                            r'\bstr\b',
                        ),
                        # Match that the exception message raised for this
                        # object does *NOT* contain a newline or bullet
                        # delimiter.
                        exception_str_not_match_regexes=(
                            r'\n',
                            r'\*',
                        ),
                    ),

                    # List of bytestring items.
                    HintPithUnsatisfiedMetadata(
                        pith=[
                            b'Apoplectic hints of',
                            b'Stenographically',
                        ],
                        # Match that the exception message raised for this
                        # object...
                        exception_str_match_regexes=(
                            # Declares all non-"typing" types *NOT* satisfied by
                            # a random list item *NOT* satisfying this hint.
                            r'\bint\b',
                            r'\bstr\b',
                            # Declares the index of the random list item *NOT*
                            # satisfying this hint.
                            r'\b[Ll]ist index \d+ item\b',
                        ),
                    ),
                ),
            ),

            # ................{ UNION ~ optional               }................
            # Optional isinstance()-able "typing" type.
            HintPepMetadata(
                hint=tuple[str, ...] | None,
                # Note that although Python >= 3.10 distinguishes equivalent PEP
                # 484-compliant "typing.Union[...]" and "typing.Optional[...]"
                # type hints via differing machine-readable representations, the
                # same does *NOT* apply to PEP 604-compliant |-style unions,
                # which remain PEP 604-compliant and thus unions rather than
                # optional. This includes PEP 604-compliant |-style unions
                # including the "None" singleton signifying an optional type
                # hint. Go figure.
                pep_sign=HintSignUnion,
                is_type_typing=False,
                piths_meta=(
                    # None singleton.
                    HintPithSatisfiedMetadata(None),
                    # Tuple of string items.
                    HintPithSatisfiedMetadata((
                        'Stentorian tenor of',
                        'Stunted numbness (in',
                    )),
                    # Floating-point constant.
                    HintPithUnsatisfiedMetadata(
                        pith=2397.7932,
                        # Match that the exception message raised for this
                        # object declares the types *NOT* satisfied by this
                        # object.
                        exception_str_match_regexes=(
                            r'\bNoneType\b',
                            r'\btuple\b',
                        ),
                        # Match that the exception message raised for this
                        # object does *NOT* contain a newline or bullet
                        # delimiter.
                        exception_str_not_match_regexes=(
                            r'\n',
                            r'\*',
                        ),
                    ),
                ),
            ),
        ))
    # Else, this interpreter supports PEP 604. In this case, return the empty
    # list.

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta

# ....................{ ADDERS                             }....................
#FIXME: Obsolete us up with a fixture-based approach, please.
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :pep:`604`-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10

    # If the active Python interpreter targets Python < 3.10, this interpreter
    # fails to support PEP 604. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_10:
        return
    # Else, this interpreter supports PEP 604.

    # ..................{ IMPORTS                            }..................
    # Defer attribute-dependent imports.
    from beartype.typing import Any

    # ..................{ SETS                               }..................
    # Add PEP 604-specific deeply ignorable test type hints to this set global.
    data_module.HINTS_PEP_IGNORABLE_DEEP.update((
        # "|"-style unions containing any ignorable type hint.
        #
        # Note that including *ANY* "typing"-based type hint (including
        # "typing.Any") in an "|"-style union causes Python to implicitly
        # produce a PEP 484- rather than PEP 604-compliant union (e.g.,
        # "typing.Union[Any, float, str]" in this case). Since that is more or
        # less fine in this context, we intentionally list such a deeply
        # ignorable hint here.
        Any | float | str,
        complex | int | object,
    ))
