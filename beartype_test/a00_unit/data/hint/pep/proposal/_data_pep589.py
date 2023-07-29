#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`589`-compliant **type hint test data.**
'''

# ....................{ IMPORTS                           }....................
from beartype_test._util.module.pytmodtyping import (
    import_typing_attr_or_none_safe)

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :pep:`589`-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # "TypedDict" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    TypedDict = import_typing_attr_or_none_safe('TypedDict')

    # If this factory is unimportable, the active Python interpreter fails to
    # support PEP 589. In this case, reduce to a noop.
    if TypedDict is None:
        return
    # Else, this interpreter supports PEP 589.

    # ..................{ IMPORTS                           }..................
    # Defer attribute-dependent imports.
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignList,
        HintSignTypedDict,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from typing import List, Type, Union

    # ..................{ SUBCLASSES                        }..................
    class ISeemAsInATranceSublimeAndStrange(TypedDict):
        '''
        Arbitrary empty typed dictionary annotated to require *NO* key-value
        pairs.

        While patently absurd, this dictionary exercises an uncommon edge case
        in :pep:`589`.
        '''

        pass


    class DizzyRavine(ISeemAsInATranceSublimeAndStrange):
        '''
        Arbitrary non-empty typed dictionary annotated to require arbitrary
        key-value pairs, intentionally subclassing the empty typed dictionary
        subclass :class:`ISeemAsInATranceSublimeAndStrange` to trivially
        exercise subclassability.
        '''

        # Arbitrary key whose value is annotated to be a PEP-noncompliant
        # instance of an isinstanceable type.
        and_when: str

        # Arbitrary key whose value is annotated to be a PEP-compliant union of
        # either a subclass of an issubclassable type or a PEP-noncompliant
        # instance of an isinstanceable type.
        I_gaze_on_thee: Union[bytes, Type[Exception]]


    #FIXME: Note that even this fails to suffice, thanks to *CRAY-CRAY*
    #subclassing logic that absolutely no one has ever exercised, but which
    #we'll nonetheless need to support. And I quoth:
    #    The totality flag only applies to items defined in the body of the
    #    TypedDict definition. Inherited items won't be affected, and instead
    #    use totality of the TypedDict type where they were defined. This makes
    #    it possible to have a combination of required and non-required keys in
    #    a single TypedDict type.
    #Ergo, we need to additionally declare yet another new class subclassing
    #"ToMuse" but *NOT* explicitly subclassed with a "total" keyword parameter.
    #This clearly gets *EXTREMELY* ugly *EXTREMELY* fast, as we'll now need to
    #iterate over "hint.__mro__" in our code generation algorithm. Well, I
    #suppose we technically needed to do that anyway... but still. Yikes!
    class ToMuse(TypedDict, total=False):
        '''
        Arbitrary non-empty typed dictionary annotated to require zero or more
        arbitrary key-value pairs.
        '''

        # Arbitrary key whose value is annotated to be a PEP-noncompliant
        # instance of an isinstanceable type.
        on_my_own: str

        # Arbitrary key whose value is annotated to be a PEP-compliant union of
        # either a subclass of an issubclassable type or a PEP-noncompliant
        # instance of an isinstanceable type.
        separate_fantasy: Union[Type[Exception], bytes]

    # ..................{ TUPLES                            }..................
    # Add PEP 586-specific test type hints to this tuple global.
    data_module.HINTS_PEP_META.extend((
        # ................{ TYPEDDICT                         }................
        # Empty typed dictionary. Look, this is ridiculous. What can you do?
        HintPepMetadata(
            hint=ISeemAsInATranceSublimeAndStrange,
            pep_sign=HintSignTypedDict,
            is_type_typing=False,
            piths_meta=(
                # Empty dictionary instantiated with standard Python syntax.
                HintPithSatisfiedMetadata({}),
                # Empty dictionary instantiated from this typed dictionary.
                HintPithSatisfiedMetadata(ISeemAsInATranceSublimeAndStrange()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith='Hadithian bodies kindle Bodkin deathbeds',
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(r'\bMapping\b',),
                ),
                #FIXME: Uncomment *AFTER* deeply type-checking "TypedDict".
                # # Non-empty dictionary.
                # HintPithSatisfiedMetadata({
                #     'Corinthian bodachean kinslayers lay': (
                #         'wedded weal‐kith with in‐'),
                # }),
            ),
        ),

        # Non-empty totalizing typed dictionary.
        HintPepMetadata(
            hint=DizzyRavine,
            pep_sign=HintSignTypedDict,
            is_type_typing=False,
            piths_meta=(
                # Non-empty dictionary of the expected keys and values.
                HintPithSatisfiedMetadata({
                    'and_when': 'Corrigible‐ragged gun corruptions within',
                    'I_gaze_on_thee': b"Hatross-ev-olved eleven imp's",
                }),
                # Non-empty dictionary of the expected keys and values
                # instantiated from this typed dictionary.
                HintPithSatisfiedMetadata(DizzyRavine(
                    and_when=(
                        'Machiavellian‐costumed, tumid stock fonts of a'),
                    I_gaze_on_thee=RuntimeError,
                )),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith='Matross‐elevated elven velvet atrocities of',
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(r'\bMapping\b',),
                ),
                # #FIXME: Uncomment *AFTER* deeply type-checking "TypedDict".
                # # Empty dictionary.
                # HintPithUnsatisfiedMetadata(
                #     pith={},
                #     # Match that the exception message raised for this object
                #     # embeds the expected number of key-value pairs.
                #     exception_str_match_regexes=(r'\b2\b',),
                # ),
                # # Non-empty dictionary of the expected keys but *NOT* values.
                # HintPithUnsatisfiedMetadata(
                #     pith={
                #         'and_when': 'Matricidally',
                #         'I_gaze_on_thee': (
                #             'Hatchet‐cachepotting, '
                #             'Scossetting mock misrule by'
                #         ),
                #     },
                #     # Match that the exception message raised for this object
                #     # embeds:
                #     # * The name of the unsatisfied key.
                #     # * The expected types of this key's value.
                #     exception_str_match_regexes=(
                #         r'\bI_gaze_on_thee\b',
                #         r'\bbytes\b',
                #     ),
                # ),
            ),
        ),

        # Non-empty non-totalizing typed dictionary.
        HintPepMetadata(
            hint=ToMuse,
            pep_sign=HintSignTypedDict,
            is_type_typing=False,
            piths_meta=(
                # Empty dictionary.
                HintPithSatisfiedMetadata({}),
                # Non-empty dictionary defining only one of the expected keys.
                HintPithSatisfiedMetadata({
                    'on_my_own': (
                        'Spurned Court‐upturned, upper gladness, '
                        'edifyingly humidifying'),
                }),
                # Non-empty dictionary defining *ALL* of the expected keys,
                # instantiated from this typed dictionary.
                HintPithSatisfiedMetadata(ToMuse(
                    on_my_own=(
                        'Sepulchral epic‐âpostatizing home tombs metem‐'),
                    separate_fantasy=b'Macroglia relics',
                )),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith=(
                        'Psychotically tempered Into temporal '
                        'afterwork‐met portals portending a'
                    ),
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(r'\bMapping\b',),
                ),
                # #FIXME: Uncomment *AFTER* deeply type-checking "TypedDict".
                # # Non-empty dictionary of the expected keys but *NOT* values.
                # HintPithUnsatisfiedMetadata(
                #     pith={
                #         'on_my_own': (
                #             'Psyche’s Maidenly‐enladened, '
                #             'aidful Lads‐lickspittling Potenc‐ies —',
                #         ),
                #         'separate_fantasy': (
                #             'Psychedelic metal‐metastasized, glib'),
                #     },
                #     # Match that the exception message raised for this object
                #     # embeds:
                #     # * The name of the unsatisfied key.
                #     # * The expected types of this key's value.
                #     exception_str_match_regexes=(
                #         r'\bseparate_fantasy\b',
                #         r'\bbytes\b',
                #     ),
                # ),
            ),
        ),

        # ................{ LITERALS ~ nested                 }................
        # List of non-empty totalizing typed dictionaries.
        HintPepMetadata(
            hint=List[DizzyRavine],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            piths_meta=(
                # List of dictionaries of the expected keys and values.
                HintPithSatisfiedMetadata([
                    {
                        'and_when': (
                            'Matriculating ‘over‐sized’ '
                            'research urchin Haunts of',
                        ),
                        'I_gaze_on_thee': b"Stands - to",
                    },
                    {
                        'and_when': (
                            'That resurrected, Erectile reptile’s '
                            'pituitary capitulations to',
                        ),
                        'I_gaze_on_thee': b"Strand our under-",
                    },
                ]),
                # List of string constants.
                HintPithUnsatisfiedMetadata(
                    pith=[
                        'D-as K-apital, '
                        'notwithstanding Standard adiós‐',
                    ],
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(r'\bMapping\b',),
                ),
                # #FIXME: Uncomment *AFTER* deeply type-checking "TypedDict".
                # # List of empty dictionaries.
                # HintPithUnsatisfiedMetadata(
                #     pith=[{}, {},],
                #     # Match that the exception message raised for this object
                #     # embeds the expected number of key-value pairs.
                #     exception_str_match_regexes=(r'\b2\b',),
                # ),
                # # List of non-empty dictionaries, only one of which fails to
                # # define both the expected keys and values.
                # HintPithUnsatisfiedMetadata(
                #     pith=[
                #         {
                #             'and_when': (
                #                 'Diased capitalization of (or into)'),
                #             'I_gaze_on_thee': (
                #                 b'Witheringly dithering, dill husks of'),
                #         },
                #         {
                #             'and_when': (
                #                 'Will, like Whitewash‐ed, musky'),
                #             'I_gaze_on_thee': 'Likenesses injecting',
                #         },
                #     ],
                #     # Match that the exception message raised for this object
                #     # embeds:
                #     # * The index of the unsatisfied dictionary.
                #     # * The name of the unsatisfied key.
                #     # * The expected types of this key's value.
                #     exception_str_match_regexes=(
                #         r'\b1\b',
                #         r'\bI_gaze_on_thee\b',
                #         r'\bbytes\b',
                #     ),
                # ),
            ),
        ),
    ))
