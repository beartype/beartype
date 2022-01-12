#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`593`-compliant **type hint test data.**
'''

# ....................{ IMPORTS                           }....................
from beartype_test.util.mod.pytmodimport import (
    import_module_typing_any_attr_or_none_safe)

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

    # "Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_module_typing_any_attr_or_none_safe('Annotated')

    # If this factory is unimportable, the active Python interpreter fails to
    # support PEP 593. In this case, reduce to a noop.
    if Annotated is None:
        return
    # Else, this interpreter supports PEP 593.

    # ..................{ IMPORTS                           }..................
    # Defer attribute-dependent imports.
    from beartype.typing import List
    from beartype.vale import (
        Is,
        IsAttr,
        IsEqual,
        IsInstance,
        IsSubclass,
    )
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignAnnotated,
        HintSignList,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
    from beartype_test.a00_unit.data.data_type import (
        Class,
        Subclass,
        SubclassSubclass,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from typing import (
        Any,
        NewType,
        Optional,
        Union,
    )

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
        Union[str, List[int], NewType('MetaType', Annotated[object, 53])],
    ))

    # ..................{ TUPLES                            }..................
    # Add PEP 593-specific test type hints to this tuple global.
    data_module.HINTS_PEP_META.extend((
        # ................{ ANNOTATED                         }................
        # Hashable annotated of an isinstanceable type annotated by an arbitrary
        # hashable object.
        HintPepMetadata(
            hint=Annotated[str, int],
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata(
                    'Towards a timely, wines‐enticing gate'),
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    'Of languished anger’s sap‐spated rushings',]),
            ),
        ),

        # Annotated of a "typing" type.
        HintPepMetadata(
            hint=Annotated[List[str], int],
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # List of string constants.
                HintPithSatisfiedMetadata([
                    'MINERVA‐unnerving, verve‐sapping enervations',
                    'Of a magik-stoned Shinto rivery',
                ]),
                # String constant.
                HintPithUnsatisfiedMetadata('Of a Spicily sated',),
            ),
        ),

    ))

    # ..................{ VALIDATORS ~ is                   }..................
    # Beartype-specific validators defined as lambda functions.
    IsLengthy = Is[lambda text: len(text) > 30]
    IsSentence = Is[lambda text: text and text[-1] == '.']

    # Beartype-specific validators defined as non-lambda functions.
    def _is_quoted(text): return '"' in text or "'" in text
    IsQuoted = Is[_is_quoted]

    # Beartype-specific validator synthesized from the above validators
    # via the domain-specific language (DSL) implemented by those validators.
    IsLengthyOrUnquotedSentence = IsLengthy | (IsSentence & ~IsQuoted)

    # Annotated of an isinstanceable type annotated by one beartype-specific
    # validator defined as a lambda function.
    AnnotatedStrIsLength = Annotated[str, IsLengthy]

    # ..................{ VALIDATORS ~ isattr               }..................
    # Arbitrary list to validate equality against below.
    AMPLY_IMPISH = ['Amply imp-ish', 'blandishments to']

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

    # ..................{ VALIDATORS ~ tuples               }..................
    # Add PEP 593-specific test type hints to this tuple global.
    data_module.HINTS_PEP_META.extend((
        # ................{ ANNOTATED ~ beartype : is         }................
        # Annotated of an isinstanceable type annotated by one beartype-specific
        # validator defined as a lambda function.
        HintPepMetadata(
            hint=AnnotatedStrIsLength,
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # String constant satisfying this validator.
                HintPithSatisfiedMetadata(
                    'To Ɯṙaith‐like‐upwreathed ligaments'),
                # Byte-string constant *NOT* an instance of the expected type.
                HintPithUnsatisfiedMetadata(
                    pith=b'Down-bound',
                    # Match that the exception message raised for this object
                    # embeds the code for this validator's lambda function.
                    exception_str_match_regexes=(
                        r'Is\[.*\blen\(text\)\s*>\s*30\b.*\]',),
                ),
                # String constant violating this validator.
                HintPithUnsatisfiedMetadata('To prayer'),
            ),
        ),

        # Annotated of an isinstanceable type annotated by two or more
        # beartype-specific validators all defined as functions, specified
        # with comma-delimited list syntax.
        HintPepMetadata(
            hint=Annotated[str, IsLengthy, IsSentence, IsQuoted],
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # String constant satisfying these validators.
                HintPithSatisfiedMetadata(
                    '"Into piezo‐electrical, dun‐dappled lights" and...'),
                # Byte-string constant *NOT* an instance of the expected type.
                HintPithUnsatisfiedMetadata(
                    pith=b'Joy.',
                    # Match that the exception message raised...
                    exception_str_match_regexes=(
                        # Embeds the code for this validator's lambdas.
                        r'Is\[.*\blen\(text\)\s*>\s*30\b.*\]',
                        r"Is\[.*\btext and text\[-1\]\s*==\s*'\.'.*\]",
                        # Embeds the name of this validator's named function.
                        r'Is\[.*\b_is_quoted\b.*\]',
                    ),
                ),
                # String constant violating only the first of these validators.
                HintPithUnsatisfiedMetadata(
                    pith='"Conduct my friar’s wheel"...',
                    # Match that the exception message raised documents the
                    # exact validator violated by this string.
                    exception_str_match_regexes=(
                        r'\bviolates\b.*\bIs\[.*\blen\(text\)\s*>\s*30\b.*\]',)
                ),
            ),
        ),

        # Annotated of an isinstanceable type annotated by two or more
        # beartype-specific validators all defined as functions, specified
        # with "&"-delimited operator syntax.
        HintPepMetadata(
            hint=Annotated[str, IsLengthy & IsSentence & IsQuoted],
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # String constant satisfying these validators.
                HintPithSatisfiedMetadata(
                    '"Into piezo‐electrical, dun‐dappled lights" and...'),
                # Byte-string constant *NOT* an instance of the expected type.
                HintPithUnsatisfiedMetadata(
                    pith=b'Joy.',
                    # Match that the exception message raised...
                    exception_str_match_regexes=(
                        # Embeds the code for this validator's lambdas.
                        r'Is\[.*\blen\(text\)\s*>\s*30\b.*\]',
                        r"Is\[.*\btext and text\[-1\]\s*==\s*'\.'.*\]",
                        # Embeds the name of this validator's named function.
                        r'Is\[.*\b_is_quoted\b.*\]',
                    ),
                ),
                # String constant violating only the first of these validators.
                HintPithUnsatisfiedMetadata(
                    pith='"Conduct my friar’s wheel"...',
                    # Match that the exception message raised documents the
                    # exact validator violated by this string.
                    exception_str_match_regexes=(
                        r'\bviolates\b.*\bIs\[.*\blen\(text\)\s*>\s*30\b.*\]',)
                ),
            ),
        ),

        # Annotated of an isinstanceable type annotated by one beartype-specific
        # validator synthesized from all possible operators.
        HintPepMetadata(
            hint=Annotated[str, IsLengthyOrUnquotedSentence],
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # String constant satisfying these validators.
                HintPithSatisfiedMetadata(
                    'Dialectical, eclectic mind‐toys'),
                # Byte-string constant *NOT* an instance of the expected type.
                HintPithUnsatisfiedMetadata(
                    pith=b'Of Cycladic impoverishment, cyclically unreeling',
                    # Match that the exception message raised...
                    exception_str_match_regexes=(
                        # Embeds the code for this validator's lambdas.
                        r'Is\[.*\blen\(text\)\s*>\s*30\b.*\]',
                        r"Is\[.*\btext and text\[-1\]\s*==\s*'\.'.*\]",
                        # Embeds the name of this validator's named function.
                        r'Is\[.*\b_is_quoted\b.*\]',
                    ),
                ),
                # String constant violating all of these validators.
                HintPithUnsatisfiedMetadata(
                    pith='Stay its course, and',
                    # Match that the exception message raised documents the
                    # first validator violated by this string.
                    exception_str_match_regexes=(
                        r'\bviolates\b.*\bIs\[.*\blen\(text\)\s*>\s*30\b.*\]',)
                ),
            ),
        ),

        # ................{ ANNOTATED ~ beartype : is : nest  }................
        # Annotated of an annotated of an isinstanceable type, each annotated
        # by a beartype-specific validator defined as a function.
        HintPepMetadata(
            hint=Annotated[Annotated[str, IsLengthy], IsSentence],
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # String constant satisfying these validators.
                HintPithSatisfiedMetadata(
                    'Antisatellite‐dendroidal, Θṙbital Cemetery orbs — '
                    'of Moab.'
                ),
                # Byte-string constant *NOT* an instance of the expected type.
                HintPithUnsatisfiedMetadata(b'Then, and'),
                # String constant violating only the first of these validators.
                HintPithUnsatisfiedMetadata('Though a...'),
            ),
        ),

        # List of annotateds of isinstanceable types annotated by one
        # beartype-specific validator defined as a lambda function.
        HintPepMetadata(
            hint=List[AnnotatedStrIsLength],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin=List is list,
            piths_meta=(
                # List of string constants satisfying this validator.
                HintPithSatisfiedMetadata([
                    'An‐atomically Island‐stranded, adrift land)',
                    'That You randily are That worm‐tossed crabapple of',
                ]),
                # String constant *NOT* an instance of the expected type.
                HintPithUnsatisfiedMetadata(
                    pith="Our Sturm‐sapped disorder's convolution of",
                    # Match that the exception message raised for this object
                    # embeds the code for this validator's lambda function.
                    exception_str_match_regexes=(
                        r'Is\[.*\blen\(text\)\s*>\s*30\b.*\]',),
                ),
                # List of string constants violating this validator.
                HintPithUnsatisfiedMetadata([
                    'Volubly liable,',
                    'Drang‐rang aloofment –',
                    'ruthlessly',
                ]),
            ),
        ),

        # ................{ ANNOTATED ~ beartype : isattr     }................
        # Annotated of an isinstanceable type annotated by one
        # beartype-specific attribute validator.
        HintPepMetadata(
            hint=Annotated[
                CathecticallyEnsconceYouIn, IsAttrThisMobbedTristeOf],
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # Instance of this class satisfying this validator.
                HintPithSatisfiedMetadata(BOSS_EMBOSSED_ORDERING),
                # String constant *NOT* an instance of this class.
                HintPithUnsatisfiedMetadata(
                    pith='An atoll nuclear broilers newly cleared of',
                    # Match that the exception message raised for this object
                    # embeds the name of the expected attribute.
                    exception_str_match_regexes=(
                        r"IsAttr\[.*'this_mobbed_triste_of',.*\]",),
                ),
                # Instance of this class *NOT* satisfying this validator.
                HintPithUnsatisfiedMetadata(SORDIDLY_FLABBY_WRMCASTINGS),
            ),
        ),

        # ................{ ANNOTATED ~ beartype : isequal    }................
        # Annotated of an isinstanceable type annotated by one
        # beartype-specific equality validator.
        HintPepMetadata(
            hint=Annotated[List[str], IsEqual[AMPLY_IMPISH]],
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # Exact object subscripting this validator.
                HintPithSatisfiedMetadata(AMPLY_IMPISH),
                # Object *NOT* subscripting this validator but equal to this
                # object.
                HintPithSatisfiedMetadata(AMPLY_IMPISH[:]),
                # String constant *NOT* an instance of the expected type.
                HintPithUnsatisfiedMetadata(
                    pith='May Your coarsest, Incessantly cast‐off jobs of a',
                    # Match that the exception message raised for this object
                    # embeds a string in the expected list.
                    exception_str_match_regexes=(r"'Amply imp-ish'",),
                ),
                # List of integer constants *NOT* instances of the expected
                # subtype.
                HintPithUnsatisfiedMetadata([1, 2, 3, 6, 7, 14, 21, 42,]),
                # List of string constants violating this validator.
                HintPithUnsatisfiedMetadata(
                    ['Hectic,', 'receptacle‐hybernacling caste so',]),
            ),
        ),

        # ................{ ANNOTATED ~ beartype : isinstance }................
        # Annotated of an isinstanceable type annotated by one
        # beartype-specific type instance validator.
        HintPepMetadata(
            hint=Annotated[Class, ~IsInstance[SubclassSubclass]],
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # Instance of the class subscripting this validator.
                HintPithSatisfiedMetadata(Class()),
                # Instance of the subclass subclassing the class subscripting
                # this validator.
                HintPithSatisfiedMetadata(Subclass()),
                # Instance of the subsubclass subclassing the subclass
                # subclassing the class subscripting this validator.
                HintPithUnsatisfiedMetadata(SubclassSubclass()),
                # Class subscripting this validator.
                HintPithUnsatisfiedMetadata(Class),
                # String constant *NOT* an instance of the expected type.
                HintPithUnsatisfiedMetadata(
                    pith=(
                        'Architrave‐contravening, '
                        'indigenously chitinous tactilities) of'
                    ),
                    # Match that the exception message raised for this object
                    # embeds a classname in the expected list.
                    exception_str_match_regexes=(r'\bClass\b',),
                ),
            ),
        ),

        # ................{ ANNOTATED ~ beartype : issubclass }................
        # Annotated of an isinstanceable type annotated by one
        # beartype-specific type inheritance validator.
        HintPepMetadata(
            hint=Annotated[type, IsSubclass[Class]],
            pep_sign=HintSignAnnotated,
            piths_meta=(
                # Class subscripting this validator.
                HintPithSatisfiedMetadata(Class),
                # Class subclassing the class subscripting this validator.
                HintPithSatisfiedMetadata(Subclass),
                # Class *NOT* subclassing the class subscripting this
                # validator.
                HintPithUnsatisfiedMetadata(str),
                # String constant *NOT* an instance of the expected type.
                HintPithUnsatisfiedMetadata(
                    pith='May Your coarsest, Incessantly cast‐off jobs of a',
                    # Match that the exception message raised for this object
                    # embeds a classname in the expected list.
                    exception_str_match_regexes=(r'\bClass\b',),
                ),
            ),
        ),
    ))

    # If the active Python interpreter targets Python >= 3.7, the "typing"
    # module is sufficiently sane to support subscripting the third-party
    # "typing_extensions.Literal" factory by unhashable objects. Under Python
    # 3.6, these type hints fail at subscription time with non-human-readable
    # exceptions resembling:
    #     TypeError: unhashable type: 'list'
    if IS_PYTHON_AT_LEAST_3_7:
        data_module.HINTS_PEP_META.extend((
            # Unhashable annotated of an isinstanceable type annotated by an
            # unhashable mutable container.
            HintPepMetadata(
                hint=Annotated[str, []],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # String constant.
                    HintPithSatisfiedMetadata(
                        'Papally Ľust‐besmirched Merchet laws'),
                    # List of string constants.
                    HintPithUnsatisfiedMetadata([
                        "Of our ôver‐crowdedly cowed crowd's opinion‐",]),
                ),
            ),
        ))
