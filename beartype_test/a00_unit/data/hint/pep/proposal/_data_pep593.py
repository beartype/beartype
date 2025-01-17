#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`593`-compliant **type hint test data.**
'''

# ....................{ ADDERS                             }....................
def hints_pep593_meta() -> 'List[HintPepMetadata]':
    '''
    Session-scoped fixture returning a list of :pep:`593`-compliant **type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific :pep:`593`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype.typing import (
        List,
        Sequence,
        TypeVar,
        Union,
    )
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
        HintSignUnion,
    )
    from beartype._util.api.standard.utiltyping import get_typing_attrs
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
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
    from functools import partial

    # ..................{ CLASSES                            }..................
    class TruthSeeker(object):
        def __call__(self, obj: object) -> bool:
            '''
            Tester method returning :data:`True` only if the passed object
            evaluates to :data:`True` when coerced into a boolean and whose
            first parameter is ignorable.
            '''

            return bool(obj)

    # ..................{ CALLABLES                          }..................
    def is_true(ignorable_arg, obj):
        '''
        Tester function returning :data:`True` only if the passed object
        evaluates to :data:`True` when coerced into a boolean and whose first
        parameter is ignorable.
        '''

        return bool(obj)


    # Partial of the is_true() tester defined above, effectively ignoring the
    # "ignorable_arg" parameter accepted by that tester.
    is_true_partial = partial(
        is_true, 'Drank its inspiring radiance, and the wind')

    # ..................{ VALIDATORS ~ is                    }..................
    # PEP 484-compliant union of all builtin scalar types.
    Number = Union[int, float, complex]

    # Generic beartype validators defined as lambda functions.
    IsNonEmpty = Is[lambda obj: bool(obj)]

    # Numeric beartype validators defined as lambda functions.
    IsNonNegative = Is[lambda number: number >= 0]
    IsIntNonZero = Is[lambda number: isinstance(number, int) and number != 0]

    # Textual beartype validators defined as lambda functions.
    IsLengthy = Is[lambda text: len(text) > 30]
    IsSentence = Is[lambda text: text and text[-1] == '.']

    # Textual beartype validators defined as non-lambda functions.
    def _is_quoted(text):
        return '"' in text or "'" in text
    def _is_exceptional(obj):
        raise ValueError(f'Colonial. {repr(obj)}')
    IsQuoted = Is[_is_quoted]
    IsExceptional = Is[_is_exceptional]

    # Textual beartype validator synthesized from the above validators via the
    # domain-specific language (DSL) implemented by those validators.
    IsLengthyOrUnquotedSentence = IsLengthy | (IsSentence & ~IsQuoted)

    # ..................{ VALIDATORS ~ isattr                }..................
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

    # ..................{ LOCALS                             }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = []

    # ..................{ FACTORIES                          }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module...
    for Annotated in get_typing_attrs('Annotated'):
        # print(f'Exercising PEP 593 {repr(Annotated)}...')

        # ..................{ LOCALS                         }..................
        # Local variables requiring an "Annotated" type hint factory.

        # Annotated of an isinstanceable type annotated by one beartype-specific
        # validator defined as a lambda function.
        AnnotatedStrIsLength = Annotated[str, IsLengthy]

        # Validator matching any sequence of strings that is itself *NOT* a
        # string. Technically, a string is itself a sequence of characters,
        # which are themselves strings of length 1 in Python. Pragmatically, a
        # string is rarely considered to be a "sequence of strings" in the
        # common sense of that term. Validators, save us from the sins of Guido!
        SequenceNonstrOfStr = Annotated[Sequence[str], ~IsInstance[str]]

        # Type variable bounded by a beartype validator defined as a lambda
        # function.
        T_IsIntNonZero = TypeVar(
            'T_IsIntNonZero', bound=Annotated[object, IsIntNonZero])

        # Type variable bounded by two beartype validators, one defined as a
        # lambda function and one not.
        T_IsIntNonZero = TypeVar(
            'T_IsIntNonZero',
            bound=Annotated[object, IsInstance[int], IsNonEmpty],
        )

        # ................{ TUPLES                             }................
        # Add PEP 593-specific test type hints to this tuple global.
        hints_pep_meta.extend((
            # ..............{ ANNOTATED                          }..............
            # Annotated of an arbitrary isinstanceable type annotated by an
            # arbitrary hashable object.
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

            # Annotated of an arbitrary nested type hint.
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

            # ..............{ ANNOTATED ~ beartype : is          }..............
            # Annotated of the root "object" superclass annotated by a beartype
            # validator defined as a lambda function.
            HintPepMetadata(
                hint=Annotated[object, Is[
                    lambda obj: hasattr(obj, 'this_mobbed_triste_of')]],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # Objects defining attributes with the above name.
                    HintPithSatisfiedMetadata(BOSS_EMBOSSED_ORDERING),
                    HintPithSatisfiedMetadata(SORDIDLY_FLABBY_WRMCASTINGS),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Her timid steps to gaze upon a form'),
                ),
            ),

            # Annotated of the root "object" superclass annotated by a beartype
            # validator defined as a callable object.
            HintPepMetadata(
                hint=Annotated[object, Is[TruthSeeker()]],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # Objects evaluating to "True" when coerced into booleans.
                    HintPithSatisfiedMetadata(True),
                    HintPithSatisfiedMetadata(
                        'Leaped in the boat, he spread his cloak aloft'),
                    # Empty string.
                    HintPithUnsatisfiedMetadata(''),
                ),
            ),

            # Annotated of the root "object" superclass annotated by a beartype
            # validator defined as a partial function.
            HintPepMetadata(
                hint=Annotated[object, Is[is_true_partial]],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # Objects evaluating to "True" when coerced into booleans.
                    HintPithSatisfiedMetadata(True),
                    HintPithSatisfiedMetadata(
                        'Swept strongly from the shore, blackening the waves.'),
                    # Empty string.
                    HintPithUnsatisfiedMetadata(''),
                ),
            ),

            # Annotated of an isinstanceable type annotated by a beartype
            # validator defined as a lambda function.
            HintPepMetadata(
                hint=AnnotatedStrIsLength,
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # String constant satisfying this validator.
                    HintPithSatisfiedMetadata(
                        'To Ɯṙaith‐like‐upwreathed ligaments'),
                    # Byte-string constant *NOT* an instance of the expected
                    # type.
                    HintPithUnsatisfiedMetadata(
                        pith=b'Down-bound',
                        # Match that the exception message raised for this
                        # object embeds the code for this validator's lambda
                        # function.
                        exception_str_match_regexes=(
                            r'Is\[.*\blen\(text\)\s*>\s*30\b.*\]',),
                    ),
                    # String constant violating this validator.
                    HintPithUnsatisfiedMetadata('To prayer'),
                ),
            ),

            # Annotated of an isinstanceable type annotated by two or more
            # beartype validators all defined as functions, specified with
            # comma-delimited list syntax.
            HintPepMetadata(
                hint=Annotated[str, IsLengthy, IsSentence, IsQuoted],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # String constant satisfying these validators.
                    HintPithSatisfiedMetadata(
                        '"Into piezo‐electrical, dun‐dappled lights" and...'),
                    # Byte-string constant *NOT* an instance of the expected
                    # type.
                    HintPithUnsatisfiedMetadata(
                        pith=b'Joy.',
                        # Match that the exception message raised...
                        exception_str_match_regexes=(
                            # Embeds the code for this validator's lambdas.
                            r'Is\[.*\blen\(text\)\s*>\s*30\b.*\]',
                            r"Is\[.*\btext and text\[-1\]\s*==\s*'\.'.*\]",
                            # Embeds the name of this validator's named
                            # function.
                            r'Is\[.*\b_is_quoted\b.*\]',
                        ),
                    ),
                    # String constant violating only the first of these
                    # validators.
                    HintPithUnsatisfiedMetadata(
                        pith='"Conduct my friar’s wheel"...',
                        # Match that the exception message raised documents the
                        # exact validator violated by this string.
                        exception_str_match_regexes=(
                            r'\bviolates\b.*\bIs\[.*\blen\(text\)\s*>\s*30\b.*\]',)
                    ),
                ),
            ),

            # Annotated of an isinstanceable type annotated by one beartype
            # validator synthesized from all possible operators.
            HintPepMetadata(
                hint=Annotated[str, IsLengthyOrUnquotedSentence],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # String constant satisfying these validators.
                    HintPithSatisfiedMetadata(
                        'Dialectical, eclectic mind‐toys'),
                    # Byte-string constant *NOT* an instance of the expected
                    # type.
                    HintPithUnsatisfiedMetadata(
                        pith=b'Of Cycladic impoverishment, cyclically unreeling',
                        # Match that the exception message raised...
                        exception_str_match_regexes=(
                            # Embeds the code for this validator's lambdas.
                            r'Is\[.*\blen\(text\)\s*>\s*30\b.*\]',
                            r"Is\[.*\btext and text\[-1\]\s*==\s*'\.'.*\]",
                            # Embeds the name of this validator's named
                            # function.
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

            # ..............{ ANNOTATED ~ beartype : is : &      }..............
            # Annotated of an isinstanceable type annotated by two or more
            # beartype validators all defined as functions, specified with
            # "&"-delimited operator syntax.
            HintPepMetadata(
                hint=Annotated[str, IsLengthy & IsSentence & IsQuoted],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # String constant satisfying these validators.
                    HintPithSatisfiedMetadata(
                        '"Into piezo‐electrical, dun‐dappled lights" and...'),
                    # Byte-string constant *NOT* an instance of the expected
                    # type.
                    HintPithUnsatisfiedMetadata(
                        pith=b'Joy.',
                        # Match that the exception message raised...
                        exception_str_match_regexes=(
                            # Embeds the code for this validator's lambdas.
                            r'Is\[.*\blen\(text\)\s*>\s*30\b.*\]',
                            r"Is\[.*\btext and text\[-1\]\s*==\s*'\.'.*\]",
                            # Embeds the name of this validator's named
                            # function.
                            r'Is\[.*\b_is_quoted\b.*\]',
                        ),
                    ),
                    # String constant violating only the first of these
                    # validators.
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
            # beartype validators all defined as functions, specified with
            # "&"-delimited operator syntax such that the first such validator
            # short-circuits all subsequent such validators, which all
            # intentionally raise exceptions to prove they are silently ignored.
            #
            # Note this hint is *NOT* safely satisfiable. Ergo, we
            # intentionally do *NOT* validate this hint to be satisfied.
            HintPepMetadata(
                hint=Annotated[str, IsLengthy & IsExceptional],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # Byte-string constant *NOT* an instance of the expected
                    # type.
                    HintPithUnsatisfiedMetadata(
                        b'Lone ignorance concentrations a-'),
                    # String constant violating the first validator.
                    HintPithUnsatisfiedMetadata('Long a'),
                ),
            ),

            # ..............{ ANNOTATED ~ beartype : is : |      }..............
            # Annotated of an isinstanceable type annotated by two or more
            # beartype validators all defined as functions, specified with
            # "|"-delimited operator syntax such that the first such validator
            # short-circuits all subsequent such validators, which all
            # intentionally raise exceptions to prove they are silently ignored.
            #
            # Note this hint is *NOT* safely unsatisfiable. Ergo, we
            # intentionally do *NOT* validate this hint to be unsatisfied.
            HintPepMetadata(
                hint=Annotated[str, IsLengthy | IsExceptional],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # String constant satisfying the first validator.
                    HintPithSatisfiedMetadata(
                        "Longhouse-ignifluous, "
                        "superfluousness-rambling academic's"
                    ),
                    # Byte-string constant *NOT* an instance of the expected
                    # type.
                    HintPithUnsatisfiedMetadata(b'Intra-convivial loci of'),
                ),
            ),

            # ..............{ ANNOTATED ~ beartype : is : nest   }..............
            # Annotated of an annotated of an isinstanceable type, each
            # annotated by a beartype validator defined as a function.
            HintPepMetadata(
                hint=Annotated[Annotated[str, IsLengthy], IsSentence],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # String constant satisfying these validators.
                    HintPithSatisfiedMetadata(
                        'Antisatellite‐dendroidal, Θṙbital Cemetery orbs — '
                        'of Moab.'
                    ),
                    # Byte-string constant *NOT* an instance of the expected
                    # type.
                    HintPithUnsatisfiedMetadata(b'Then, and'),
                    # String constant violating only the first of these
                    # validators.
                    HintPithUnsatisfiedMetadata('Though a...'),
                ),
            ),

            # List of annotateds of isinstanceable types annotated by one
            # beartype validator defined as a lambda function.
            HintPepMetadata(
                hint=List[AnnotatedStrIsLength],
                pep_sign=HintSignList,
                isinstanceable_type=list,
                is_pep585_builtin_subscripted=List is list,
                piths_meta=(
                    # List of string constants satisfying this validator.
                    HintPithSatisfiedMetadata([
                        'An‐atomically Island‐stranded, adrift land)',
                        'That You randily are That worm‐tossed crabapple of',
                    ]),
                    # String constant *NOT* an instance of the expected type.
                    HintPithUnsatisfiedMetadata(
                        pith="Our Sturm‐sapped disorder's convolution of",
                        # Match that the exception message raised for this
                        # object embeds the code for this validator's lambda
                        # function.
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

            # List of lists of annotateds of an ignorable type hint annotated by
            # a type variable bounded by a beartype validator defined as a
            # lambda function.
            HintPepMetadata(
                hint=List[List[T_IsIntNonZero]],
                pep_sign=HintSignList,
                isinstanceable_type=list,
                is_pep585_builtin_subscripted=List is list,
                typevars=(T_IsIntNonZero,),
                piths_meta=(
                    # List of lists of non-zero integer constants.
                    HintPithSatisfiedMetadata([[16, 17, 20], [21, 64, 65, 68]]),
                    # String constant *NOT* an instance of the expected type.
                    HintPithUnsatisfiedMetadata(
                        'The waves arose. Higher and higher still'),
                    # List of lists of non-integers and zeroes.
                    HintPithUnsatisfiedMetadata([
                        [
                            'Their fierce necks writhed',
                            "beneath the tempest's scourge",
                        ],
                        [0, 0, 0, 0],
                    ]),
                ),
            ),

            # List of lists of annotateds of an ignorable type hint annotated by
            # a type variable bounded by two beartype validators, one defined as
            # a lambda function and one not.
            HintPepMetadata(
                hint=List[List[T_IsIntNonZero]],
                pep_sign=HintSignList,
                isinstanceable_type=list,
                is_pep585_builtin_subscripted=List is list,
                typevars=(T_IsIntNonZero,),
                piths_meta=(
                    # List of lists of non-zero integer constants.
                    HintPithSatisfiedMetadata([[16, 17, 20], [21, 64, 65, 68]]),
                    # String constant *NOT* an instance of the expected type.
                    HintPithUnsatisfiedMetadata(
                        'The waves arose. Higher and higher still'),
                    # List of lists of non-integers and zeroes.
                    HintPithUnsatisfiedMetadata([
                        [
                            'Their fierce necks writhed',
                            "beneath the tempest's scourge",
                        ],
                        [0, 0, 0, 0],
                    ]),
                ),
            ),

            # ..............{ ANNOTATED ~ beartype : isattr      }..............
            # Annotated of an isinstanceable type annotated by one beartype
            # attribute validator.
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
                        # Match that the exception message raised for this
                        # object embeds the name of the expected attribute.
                        exception_str_match_regexes=(
                            r"IsAttr\[.*'this_mobbed_triste_of',.*\]",),
                    ),
                    # Instance of this class *NOT* satisfying this validator.
                    HintPithUnsatisfiedMetadata(SORDIDLY_FLABBY_WRMCASTINGS),
                ),
            ),

            # ..............{ ANNOTATED ~ beartype : isequal     }..............
            # Annotated of an isinstanceable type annotated by one beartype
            # equality validator.
            HintPepMetadata(
                hint=Annotated[List[str], IsEqual[AMPLY_IMPISH]],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # Exact object subscripting this validator.
                    HintPithSatisfiedMetadata(AMPLY_IMPISH),
                    # Object *NOT* subscripting this validator but equal to
                    # this object.
                    HintPithSatisfiedMetadata(AMPLY_IMPISH[:]),
                    # String constant *NOT* an instance of the expected type.
                    HintPithUnsatisfiedMetadata(
                        pith='May Your coarsest, Incessantly cast‐off jobs of a',
                        # Match that the exception message raised for this
                        # object embeds a string in the expected list.
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

            # ..............{ ANNOTATED ~ beartype : isinstance  }..............
            # Annotated of an isinstanceable type annotated by one beartype type
            # instance validator.
            HintPepMetadata(
                hint=Annotated[Class, ~IsInstance[SubclassSubclass]],
                pep_sign=HintSignAnnotated,
                piths_meta=(
                    # Instance of the class subscripting this validator.
                    HintPithSatisfiedMetadata(Class()),
                    # Instance of the subclass subclassing the class
                    # subscripting this validator.
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
                        # Match that the exception message raised for this
                        # object embeds a classname in the expected list.
                        exception_str_match_regexes=(r'\bClass\b',),
                    ),
                ),
            ),

            # Type hint matching *ANY* sequence of strings, defined as the union
            # of a beartype validator matching any sequence of strings that is
            # *NOT* itself a string with a string. Although odd, this exercises
            # an obscure edge case in code generation.
            HintPepMetadata(
                hint=Union[SequenceNonstrOfStr, str],
                pep_sign=HintSignUnion,
                piths_meta=(
                    # String constant.
                    HintPithSatisfiedMetadata(
                        'Caught the impatient wandering of his gaze.'),
                    # Tuple of string constants.
                    HintPithSatisfiedMetadata((
                        'Swayed with the undulations of the tide.',
                        'A restless impulse urged him to embark',
                    )),
                    # Byte string constant.
                    HintPithUnsatisfiedMetadata(
                        pith=b'It had been long abandoned, for its sides',
                        # Match that the exception message raised for this
                        # object embeds a classname in the expected list.
                        exception_str_match_regexes=(r'\bbytes\b',),
                    ),
                    # Tuple of byte string constants.
                    HintPithUnsatisfiedMetadata(
                        pith=(
                            b'Gaped wide with many a rift,',
                            b'and its frail joints',
                        ),
                        # Match that the exception message raised for this
                        # object embeds a classname in the expected list.
                        exception_str_match_regexes=(r'\btuple\b',),
                    ),
                ),
            ),

            # ..............{ ANNOTATED ~ beartype : issubclass  }..............
            # Annotated of an isinstanceable type annotated by one beartype type
            # inheritance validator.
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
                        # Match that the exception message raised for this
                        # object embeds a classname in the expected list.
                        exception_str_match_regexes=(r'\bClass\b',),
                    ),
                ),
            ),
        ))

        # ..................{ VERSION                        }..................
        # If the active Python interpreter targets Python >= 3.10, the
        # "typing.Annotated" type factory supports the "|" operator. In this
        # case, defined unions of annotateds with this operator.
        if IS_PYTHON_AT_LEAST_3_10:
            # annotated by a type variable bounded by a union of beartype
            # validators defined as lambda functions.
            T_IsNumberNonNegativeOrStrNonEmpty = TypeVar(
                'T_IsNumberNonNegativeOrStrNonEmpty',
                bound=(
                    Annotated[Number, IsNonNegative] |
                    Annotated[str, IsNonEmpty]
                ),
            )

            # Add PEP 593-specific test type hints to this tuple global.
            hints_pep_meta.extend((
                # ..............{ ANNOTATED ~ beartype : is : nes}..............
                # List of lists of annotateds of a union of isinstanceable types
                # annotated by a type variable bounded by a union of beartype
                # validators defined as lambda functions.
                HintPepMetadata(
                    hint=List[List[T_IsNumberNonNegativeOrStrNonEmpty]],
                    pep_sign=HintSignList,
                    isinstanceable_type=list,
                    is_pep585_builtin_subscripted=List is list,
                    typevars=(T_IsNumberNonNegativeOrStrNonEmpty,),
                    piths_meta=(
                        # List of lists of positive number constants.
                        HintPithSatisfiedMetadata([
                            [11, 0.11], [1, 110, 1101100]]),
                        # List of lists of non-empty string constants.
                        HintPithSatisfiedMetadata([
                            ['The straining boat.', '—A whirlwind swept it on,'],
                            ['With fierce gusts and', 'precipitating force,'],
                        ]),
                        # String constant *NOT* an instance of the expected type.
                        HintPithUnsatisfiedMetadata(
                            'Through the white ridges of the chafèd sea.'),
                        # List of lists of negative numbers and empty strings.
                        HintPithUnsatisfiedMetadata([[-1, '', -0.4], ['', -5, '']]),
                    ),
                ),
            ))
        # Else, the active Python interpreter targets Python < 3.10. In this
        # case, the "typing.Annotated" type factory fails to support the "|"
        # operator.

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta


def hints_pep593_ignorable_deep() -> list:
    '''
    List of :pep:`593`-compliant **deeply ignorable type hints** (i.e.,
    ignorable only on the non-trivial basis of their nested child type hints).
    '''

    # ..................{ IMPORTS                            }..................
    from beartype.typing import (
        Any,
        List,
        NewType,
        Optional,
        Union,
    )
    from beartype._util.api.standard.utiltyping import get_typing_attrs

    # ..................{ LOCALS                             }..................
    # List of all PEP-specific deeply ignorable type hints to be returned.
    hints_pep_ignorable_deep = []

    # ..................{ LISTS                              }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module...
    for Annotated in get_typing_attrs('Annotated'):
        # ................{ SETS                               }................
        # Add PEP 593-specific deeply ignorable test type hints to that global.
        hints_pep_ignorable_deep.extend((
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

    # ..................{ RETURN                             }..................
    # Return this list.
    return hints_pep_ignorable_deep
