#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 593`_**-compliant type hint test data.**

.. _PEP 593:
    https://www.python.org/dev/peps/pep-0593
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype_test.a00_unit.data.hint.data_hintmeta import (
    PepHintMetadata,
    PepHintPithSatisfiedMetadata,
    PepHintPithUnsatisfiedMetadata,
)

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 593`_**-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 593:
        https://www.python.org/dev/peps/pep-0593
    '''

    # If the active Python interpreter targets less than Python < 3.9, this
    # interpreter fails to support PEP 593. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_9:
        return
    # Else, the active Python interpreter targets at least Python >= 3.9 and
    # thus supports PEP 593.

    # ..................{ IMPORTS                           }..................
    # Defer Python >= 3.9-specific imports.
    from beartype.vale import Is
    from typing import (
        Annotated,
        Any,
        NewType,
        Optional,
        Union,
    )

    # ..................{ IMPORTS                           }..................
    # Beartype-specific data validators defined as lambda functions.
    IsLengthy = Is[lambda text: len(text) > 30]
    IsSentence = Is[lambda text: text and text[-1] == '.']

    # Beartype-specific data validators defined as non-lambda functions.
    def _is_quoted(text): return '"' in text or "'" in text
    IsQuoted = Is[_is_quoted]

    # Beartype-specific data validator synthesized from the above validators
    # via the domain-specific language (DSL) implemented by those validators.
    IsLengthyOrUnquotedSentence = IsLengthy | (IsSentence & ~IsQuoted)

    # ..................{ SETS                              }..................
    # Add PEP 593-specific deeply ignorable test type hints to that set global.
    data_module.HINTS_PEP_IGNORABLE_DEEP.update((
        # Annotated of shallowly ignorable type hints.
        Annotated[Any, int],
        Annotated[object, int],

        # Annotated of ignorable unions and optionals.
        Annotated[Union[Any, float, str,], int],
        Annotated[Optional[Any], int],

        # Unions and optionals of ignorable annotateds.
        Union[complex, int, Annotated[Any, int]],
        Optional[Annotated[object, int]],

        # Deeply ignorable PEP 484-, 585-, and 593-compliant type hint
        # exercising numerous edge cases broken under prior releases.
        Union[str, list[int], NewType('MetaType', Annotated[object, 53])],
    ))

    # Add PEP 593-specific invalid non-generic types to that set global.
    data_module.HINTS_PEP_INVALID_CLASS_NONGENERIC.update((
        # The "Annotated" class as is does *NOT* constitute a valid type hint.
        Annotated,
    ))

    # ..................{ TUPLES                            }..................
    # Add PEP 593-specific test type hints to this dictionary global.
    data_module.HINTS_PEP_META.extend((
        # ................{ ANNOTATED                         }................
        # Hashable annotated of a non-"typing" type annotated by an arbitrary
        # hashable object.
        PepHintMetadata(
            hint=Annotated[str, int],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # String constant.
                PepHintPithSatisfiedMetadata(
                    'Towards a timely, wines‐enticing gate'),
            ),
            piths_unsatisfied_meta=(
                # List of string constants.
                PepHintPithUnsatisfiedMetadata([
                    'Of languished anger’s sap‐spated rushings',]),
            ),
        ),

        # Unhashable annotated of a non-"typing" type annotated by an
        # unhashable mutable container.
        PepHintMetadata(
            hint=Annotated[str, []],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # String constant.
                PepHintPithSatisfiedMetadata(
                    'Papally Ľust‐besmirched Merchet laws'),
            ),
            piths_unsatisfied_meta=(
                # List of string constants.
                PepHintPithUnsatisfiedMetadata([
                    "Of our ôver‐crowdedly cowed crowd's opinion‐",]),
            ),
        ),

        # Annotated of a "typing" type.
        PepHintMetadata(
            hint=Annotated[list[str], int],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # List of string constants.
                PepHintPithSatisfiedMetadata([
                    'MINERVA‐unnerving, verve‐sapping enervations',
                    'Of a magik-stoned Shinto rivery',
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Of a Spicily sated',),
            ),
        ),

        # ................{ ANNOTATED ~ beartype : is         }................
        # Annotated of a non-"typing" type annotated by one beartype-specific
        # data validator defined as a lambda function.
        PepHintMetadata(
            hint=Annotated[str, IsLengthy],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # String constant satisfying this validator.
                PepHintPithSatisfiedMetadata(
                    'To Ɯṙaith‐like‐upwreathed ligaments'),
            ),
            piths_unsatisfied_meta=(
                # Byte-string constant *NOT* an instance of the expected type.
                PepHintPithUnsatisfiedMetadata(
                    pith=b'Down-bound',
                    # Match that the exception message raised for this object
                    # embeds the code for this validator's lambda function.
                    exception_str_match_regexes=(
                        r'Is\[.*\blen\(text\) > 30\b.*\]',),
                ),
                # String constant violating this validator.
                PepHintPithUnsatisfiedMetadata('To prayer'),
            ),
        ),

        # Annotated of a non-"typing" type annotated by two or more
        # beartype-specific data validators all defined as functions, specified
        # with comma-delimited list syntax.
        PepHintMetadata(
            hint=Annotated[str, IsLengthy, IsSentence, IsQuoted],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # String constant satisfying these validators.
                PepHintPithSatisfiedMetadata(
                    '"Into piezo‐electrical, dun‐dappled lights" and...'),
            ),
            piths_unsatisfied_meta=(
                # Byte-string constant *NOT* an instance of the expected type.
                PepHintPithUnsatisfiedMetadata(
                    pith=b'Joy.',
                    # Match that the exception message raised...
                    exception_str_match_regexes=(
                        # Embeds the code for this validator's lambdas.
                        r'Is\[.*\blen\(text\) > 30\b.*\]',
                        r"Is\[.*\btext and text\[-1\] == '\.'.*\]",
                        # Embeds the name of this validator's named function.
                        r'Is\[.*\b_is_quoted\b.*\]',
                    ),
                ),
                # String constant violating only the first of these validators.
                PepHintPithUnsatisfiedMetadata(
                    pith='"Conduct my friar’s wheel"...',
                    # Match that the exception message raised documents the
                    # exact validator violated by this string.
                    exception_str_match_regexes=(
                        r'\bviolates\b.*\bIs\[.*\blen\(text\) > 30\b.*\]',)
                ),
            ),
        ),

        # Annotated of a non-"typing" type annotated by two or more
        # beartype-specific data validators all defined as functions, specified
        # with "&"-delimited operator syntax.
        PepHintMetadata(
            hint=Annotated[str, IsLengthy & IsSentence & IsQuoted],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # String constant satisfying these validators.
                PepHintPithSatisfiedMetadata(
                    '"Into piezo‐electrical, dun‐dappled lights" and...'),
            ),
            piths_unsatisfied_meta=(
                # Byte-string constant *NOT* an instance of the expected type.
                PepHintPithUnsatisfiedMetadata(
                    pith=b'Joy.',
                    # Match that the exception message raised...
                    exception_str_match_regexes=(
                        # Embeds the code for this validator's lambdas.
                        r'Is\[.*\blen\(text\) > 30\b.*\]',
                        r"Is\[.*\btext and text\[-1\] == '\.'.*\]",
                        # Embeds the name of this validator's named function.
                        r'Is\[.*\b_is_quoted\b.*\]',
                    ),
                ),
                # String constant violating only the first of these validators.
                PepHintPithUnsatisfiedMetadata(
                    pith='"Conduct my friar’s wheel"...',
                    # Match that the exception message raised documents the
                    # exact validator violated by this string.
                    exception_str_match_regexes=(
                        r'\bviolates\b.*\bIs\[.*\blen\(text\) > 30\b.*\]',)
                ),
            ),
        ),

        # Annotated of a non-"typing" type annotated by one beartype-specific
        # data validator synthesized from all possible operators.
        PepHintMetadata(
            hint=Annotated[str, IsLengthyOrUnquotedSentence],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # String constant satisfying these validators.
                PepHintPithSatisfiedMetadata(
                    'Dialectical, eclectic mind‐toys'),
            ),
            piths_unsatisfied_meta=(
                # Byte-string constant *NOT* an instance of the expected type.
                PepHintPithUnsatisfiedMetadata(
                    pith=b'Of Cycladic impoverishment, cyclically unreeling',
                    # Match that the exception message raised...
                    exception_str_match_regexes=(
                        # Embeds the code for this validator's lambdas.
                        r'Is\[.*\blen\(text\) > 30\b.*\]',
                        r"Is\[.*\btext and text\[-1\] == '\.'.*\]",
                        # Embeds the name of this validator's named function.
                        r'Is\[.*\b_is_quoted\b.*\]',
                    ),
                ),
                # String constant violating all of these validators.
                PepHintPithUnsatisfiedMetadata(
                    pith='Stay its course, and',
                    # Match that the exception message raised documents the
                    # first validator violated by this string.
                    exception_str_match_regexes=(
                        r'\bviolates\b.*\bIs\[.*\blen\(text\) > 30\b.*\]',)
                ),
            ),
        ),
    ))
