#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`593`**-compliant type hint test data.**
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
    Add :pep:`593`-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # If the active Python interpreter targets less than Python < 3.9, this
    # interpreter fails to support PEP 593. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_9:
        return
    # Else, the active Python interpreter targets at least Python >= 3.9 and
    # thus supports PEP 593.

    # ..................{ IMPORTS                           }..................
    # Defer Python >= 3.9-specific imports.
    from beartype.vale import Is, IsAttr, IsEqual
    from typing import (
        Annotated,
        Any,
        NewType,
        Optional,
        Union,
    )

    # ..................{ VALIDATORS ~ is                   }..................
    # Beartype-specific data validators defined as lambda functions.
    IsLengthy = Is[lambda text: len(text) > 30]
    IsSentence = Is[lambda text: text and text[-1] == '.']

    # Beartype-specific data validators defined as non-lambda functions.
    def _is_quoted(text): return '"' in text or "'" in text
    IsQuoted = Is[_is_quoted]

    # Beartype-specific validator synthesized from the above validators
    # via the domain-specific language (DSL) implemented by those validators.
    IsLengthyOrUnquotedSentence = IsLengthy | (IsSentence & ~IsQuoted)

    # ..................{ VALIDATORS ~ isequal              }..................
    # Arbitrary list to validate equality against.
    AMPLY_IMPISH = ['Amply imp‐ish', 'blandishments to']

    # Beartype-specific validator validating equality against that list.
    IsEqualAmplyImpish = IsEqual[AMPLY_IMPISH]

    # ..................{ VALIDATORS ~ isattr               }..................
    class CathecticallyEnsconceYouIn(object):
        '''
        Arbitrary class defining an arbitrary attribute whose value has *no*
        accessible attributes but satisfies a validator tested below.
        '''

        def __init__(self) -> None:
            '''
            Initialize this object by defining this attribute.
            '''

            # Initialize this attribute to a shallow copy of this list rather
            # than this list itself to properly test equality comparison.
            self.this_mobbed_triste_of = AMPLY_IMPISH[:]

    # Beartype-specific validator validating equality against that attribute.
    IsAttrThisMobbedTristeOf = IsAttr[
        'this_mobbed_triste_of', IsEqual[AMPLY_IMPISH]]

    # Instance of this class satisfying this validator.
    BOSS_EMBOSSED_ORDERING = CathecticallyEnsconceYouIn()

    # Instance of this class *NOT* satisfying this validator.
    SORDIDLY_FLABBY_WRMCASTINGS = CathecticallyEnsconceYouIn()
    SORDIDLY_FLABBY_WRMCASTINGS.this_mobbed_triste_of = [
        'An atomical caroller', 'carousing Thanatos', '(nucl‐eating',]

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
    # Add PEP 593-specific test type hints to this tuple global.
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
        # validator defined as a lambda function.
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

        # Annotated of a listed of a nested non-"typing" type annotated by one
        # beartype-specific validator defined as a lambda function.
        PepHintMetadata(
            hint=list[Annotated[str, IsLengthy]],
            pep_sign=list,
            stdlib_type=list,
            is_pep585_builtin=True,
            piths_satisfied_meta=(
                # List of string constants satisfying this validator.
                PepHintPithSatisfiedMetadata([
                    'An‐atomically Island‐stranded, adrift land)',
                    'That You randily are That worm‐tossed crabapple of',
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant *NOT* an instance of the expected type.
                PepHintPithUnsatisfiedMetadata(
                    pith="Our Sturm‐sapped disorder's convolution of",
                    # Match that the exception message raised for this object
                    # embeds the code for this validator's lambda function.
                    exception_str_match_regexes=(
                        r'Is\[.*\blen\(text\) > 30\b.*\]',),
                ),
                # List of string constants violating this validator.
                PepHintPithUnsatisfiedMetadata([
                    'Volubly liable,',
                    'Drang‐rang aloofment –',
                    'ruthlessly',
                ]),
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
        # validator synthesized from all possible operators.
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

        # ................{ ANNOTATED ~ beartype : isequal    }................
        # Annotated of a non-"typing" type annotated by one beartype-specific
        # equality validator.
        PepHintMetadata(
            hint=Annotated[list[str], IsEqualAmplyImpish],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # Exact object subscripting this validator.
                PepHintPithSatisfiedMetadata(AMPLY_IMPISH),
                # Object *NOT* subscripting this validator but equal to this
                # object.
                PepHintPithSatisfiedMetadata(AMPLY_IMPISH[:]),
            ),
            piths_unsatisfied_meta=(
                # String constant *NOT* an instance of the expected type.
                PepHintPithUnsatisfiedMetadata(
                    pith='May Your coarsest, Incessantly cast‐off jobs of a',
                    # Match that the exception message raised for this object
                    # embeds a string in the expected list.
                    exception_str_match_regexes=(
                        r"IsEqual\[.*'Amply imp‐ish',.*\]",),
                ),
                # List of integer constants *NOT* instances of the expected
                # subtype.
                PepHintPithUnsatisfiedMetadata([1, 2, 3, 6, 7, 14, 21, 42,]),
                # List of string constants violating this validator.
                PepHintPithUnsatisfiedMetadata(
                    ['Hectic,', 'receptacle‐hybernacling caste so',]),
            ),
        ),

        # ................{ ANNOTATED ~ beartype : isattr     }................
        # Annotated of a non-"typing" type annotated by one beartype-specific
        # attribute validator.
        PepHintMetadata(
            hint=Annotated[
                CathecticallyEnsconceYouIn, IsAttrThisMobbedTristeOf],
            pep_sign=Annotated,
            piths_satisfied_meta=(
                # Instance of this class satisfying this validator.
                PepHintPithSatisfiedMetadata(BOSS_EMBOSSED_ORDERING),
            ),
            piths_unsatisfied_meta=(
                # String constant *NOT* an instance of this class.
                PepHintPithUnsatisfiedMetadata(
                    pith='An atoll nuclear broilers newly cleared of',
                    # Match that the exception message raised for this object
                    # embeds the name of the expected attribute.
                    exception_str_match_regexes=(
                        r"IsAttr\[.*'this_mobbed_triste_of',.*\]",),
                ),
                # Instance of this class *NOT* satisfying this validator.
                PepHintPithUnsatisfiedMetadata(SORDIDLY_FLABBY_WRMCASTINGS),
            ),
        ),
    ))
