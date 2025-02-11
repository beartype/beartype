#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant **type hint test data.**
'''

# ....................{ FIXTURES                           }....................
def hints_pep695_meta() -> 'List[HintPepMetadata]':
    '''
    List of :pep:`695`-compliant **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific :pep:`695`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12

    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = []

    # If the active Python interpreter targets Python < 3.12, this interpreter
    # fails to support PEP 695. In this case, return the empty list.
    if not IS_PYTHON_AT_LEAST_3_12:
        return hints_pep_meta
    # Else, the active Python interpreter targets Python >= 3.12 and thus
    # supports PEP 695.

    # ..................{ IMPORTS ~ version                  }..................
    # Defer version-specific imports.
    from beartype import (
        BeartypeConf,
        BeartypeHintOverrides,
    )
    from beartype.typing import Any
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignPep695TypeAliasSubscripted,
        HintSignPep695TypeAliasUnsubscripted,
    )
    from beartype_test.a00_unit.data.data_type import (
        Class,
        Subclass,
        OtherClass,
        OtherSubclass,
        NonIsinstanceableMetaclass,
    )
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasSimple,
        AliasPep484604,
        AliasPep484604Depth1,
        AliasPep484604Depth1T,
        AliasPep585Dict,
        AliasPep585IterableTContainerT,
        AliasPep585IterableTupleSTContainerTupleST,
        AliasPep585TupleFixed,
        AliasPep585Type,
        AliasPep593,
        Pep585IterableTContainerT,
        Pep585IterableTupleSTContainerTupleST,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ..................{ LISTS                              }..................
    # Add PEP 695-specific test type hints to this list.
    hints_pep_meta.extend((
        # ................{ NON-PEP                            }................
        # Unsubscripted non-generic type alias aliasing a standard type hint
        # containing *NO* syntax or semantics unique to PEP 695-compliant type
        # aliases (e.g., *NO* forward references, recursion, or type variables).
        HintPepMetadata(
            hint=AliasSimple,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_type_typing=True,
            is_typing=False,
            piths_meta=(
                # Integer constant.
                HintPithSatisfiedMetadata(0xFACE0FFF),
                # List of string items.
                HintPithSatisfiedMetadata([
                    'His inmost sense suspended in its web',
                    'Of many-coloured woof and shifting hues.',
                ]),
                # Floating-point constant.
                HintPithUnsatisfiedMetadata(
                    pith=70700.00707,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\blist\b',
                        r'\bint\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # ................{ PEP (484|604)                      }................
        # Unsubscripted type alias aliasing a PEP 484- and 604-compliant union.
        HintPepMetadata(
            hint=AliasPep484604,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_type_typing=True,
            # PEP 695-compliant parametrized type aliases are parametrized by
            # type variables implicitly instantiated only "on the fly" by Python
            # itself. These variables are *NOT* explicitly defined and thus
            # *NOT* safely accessible here outside of these aliases.
            is_typevars=True,
            is_typing=False,
            piths_meta=(
                # Dictionary mapping from arbitrary objects all of the same type
                # to yet more arbitrary objects all of the same type.
                HintPithSatisfiedMetadata({
                    'When on the threshold': 'of the green recess',
                    "The wanderer's footsteps fell,": 'he knew that death',
                }),
                # Frozen set of arbitrary objects all of the same type.
                HintPithSatisfiedMetadata(frozenset((
                    b'Nor ever more offer at thy dark shrine',
                    b'The unheeded tribute of a broken heart.',
                ))),
                # List of arbitrary objects all of the same type.
                HintPithSatisfiedMetadata([
                    'Knowledge and truth and virtue were her theme,',
                    'And lofty hopes of divine liberty,',
                ]),
                # Set of arbitrary objects all of the same type.
                HintPithSatisfiedMetadata({
                    b'Thoughts the most dear to him, and poesy,',
                    b'Herself a poet. Soon the solemn mood',
                }),
                # Integer constant.
                HintPithUnsatisfiedMetadata(
                    pith=0xFACECAFE,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bdict\b',
                        r'\bfloat\b',
                        r'\bfrozenset\b',
                        r'\blist\b',
                        r'\bset\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # Subscripted type alias aliasing a PEP 484- and 604-compliant union.
        HintPepMetadata(
            hint=AliasPep484604[str],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Floating-point constant.
                HintPithSatisfiedMetadata(70.319),
                # Dictionary mapping from arbitrary objects all of the same
                # valid type to yet more arbitrary objects all of that type.
                HintPithSatisfiedMetadata({
                    'When on the threshold': 'of the green recess',
                    "The wanderer's footsteps fell,": 'he knew that death',
                }),
                # Frozen set of arbitrary objects all of the same valid type.
                HintPithSatisfiedMetadata(frozenset((
                    'Nor ever more offer at thy dark shrine',
                    'The unheeded tribute of a broken heart.',
                ))),
                # List of arbitrary objects all of the same valid type.
                HintPithSatisfiedMetadata([
                    'Knowledge and truth and virtue were her theme,',
                    'And lofty hopes of divine liberty,',
                ]),
                # Set of arbitrary objects all of the same valid type.
                HintPithSatisfiedMetadata({
                    'Thoughts the most dear to him, and poesy,',
                    'Herself a poet. Soon the solemn mood',
                }),
                # Dictionary mapping from arbitrary objects all of the same
                # invalid type to yet more arbitrary objects all of that type.
                HintPithUnsatisfiedMetadata({
                    b'Was on him.': b'Yet a little, ere it fled,',
                    b'id he resign': b'his high and holy soul',
                }),
                # Frozen set of arbitrary objects all of the same invalid type.
                HintPithUnsatisfiedMetadata(frozenset((
                    b'To images of the majestic past,',
                    b'That paused within his passive being now,',
                ))),
                # List of arbitrary objects all of the same invalid type.
                HintPithUnsatisfiedMetadata([
                    b'Like winds that bear sweet music, when they breathe',
                    b'Through some dim latticed chamber. He did place',
                ]),
                # Set of arbitrary objects all of the same invalid type.
                HintPithUnsatisfiedMetadata({
                    b'His pale lean hand upon the rugged trunk',
                    b'Of the old pine. Upon an ivied stone',
                }),
                # Integer constant.
                HintPithUnsatisfiedMetadata(
                    pith=0xFACECAFE,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bdict\b',
                        r'\bfloat\b',
                        r'\bfrozenset\b',
                        r'\blist\b',
                        r'\bset\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # Subscripted generic type alias testing type variable mappings across
        # PEP 484- and 604-compliant union hints configured by a hint override
        # recursively mapping a child hint of this union to yet another union of
        # that child hint and another hint, exercising a subtle edge case.
        HintPepMetadata(
            hint=AliasPep484604[complex],
            conf=BeartypeConf(hint_overrides=BeartypeHintOverrides(
                {float: int | float})),
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Integer constant.
                HintPithSatisfiedMetadata(0xBEEFCAFE),
                # Floating-point constant.
                HintPithSatisfiedMetadata(70.319),
                # Complex constant.
                HintPithUnsatisfiedMetadata(
                    pith=27 + 4j,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bdict\b',
                        r'\bfloat\b',
                        r'\bfrozenset\b',
                        r'\blist\b',
                        r'\bset\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # ................{ PEP (484|604) ~ depth : unparam    }................
        # Unsubscripted type alias aliasing a PEP 604-compliant union deeply
        # nesting a PEP 484-compliant union deeply nesting a non-union hint.
        HintPepMetadata(
            hint=AliasPep484604Depth1,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_type_typing=True,
            is_typing=False,
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata(
                    'Of influence benign on planets pale,'),
                # Integer constant.
                HintPithSatisfiedMetadata(0xDEAFCAFE),
                # Floating-point constant.
                HintPithSatisfiedMetadata(85.94701),
                # Byte string constant.
                HintPithUnsatisfiedMetadata(
                    pith=b'Of admonitions to the winds and seas',
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bstr\b',
                        r'\bint\b',
                        r'\bfloat\b',
                    ),
                ),
            ),
        ),

        # ................{ PEP (484|604) ~ depth : param      }................
        # Unsubscripted type alias aliasing a PEP 604-compliant union deeply
        # nesting a PEP 484-compliant union deeply nesting a non-union hint, all
        # parametrized by a single type variable.
        HintPepMetadata(
            hint=AliasPep484604Depth1T,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_type_typing=True,
            # PEP 695-compliant parametrized type aliases are parametrized by
            # type variables implicitly instantiated only "on the fly" by Python
            # itself. These variables are *NOT* explicitly defined and thus
            # *NOT* safely accessible here outside of these aliases.
            is_typevars=True,
            is_typing=False,
            # This unsubscripted alias transitively aliases an ignorable type
            # variable and is thus itself ignorable.
            is_ignorable=True,
        ),

        # Subscripted type alias aliasing a PEP 604-compliant union deeply
        # nesting a PEP 484-compliant union deeply nesting a non-union hint, all
        # parametrized by a single type variable.
        HintPepMetadata(
            hint=AliasPep484604Depth1T[int],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata(
                    "Of peaceful sway above man's harvesting,"),
                # Integer constant.
                HintPithSatisfiedMetadata(0xBEEFDEAF),
                # Floating-point constant.
                HintPithSatisfiedMetadata(1.074958),
                # Byte string constant.
                HintPithUnsatisfiedMetadata(
                    pith=b'And all those acts which Deity supreme',
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bstr\b',
                        r'\bint\b',
                        r'\bfloat\b',
                    ),
                ),
            ),
        ),

        # ................{ PEP 585 ~ generic : T              }................
        # Unsubscripted type alias aliasing a PEP 604-compliant union over a
        # type variable, a PEP 585-compliant generic subscripted by that same
        # type variable, and "None".
        HintPepMetadata(
            hint=AliasPep585IterableTContainerT,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_ignorable=True,
            is_type_typing=True,
            # PEP 695-compliant parametrized type aliases are parametrized by
            # type variables implicitly instantiated only "on the fly" by Python
            # itself. These variables are *NOT* explicitly defined and thus
            # *NOT* safely accessible here outside of these aliases.
            is_typevars=True,
            is_typing=False,
            piths_meta=(
                # Instance of this generic containing one or more items.
                HintPithSatisfiedMetadata(Pep585IterableTContainerT((
                    'So came these words and went;', 'the while in tears',))),
                # String constant.
                HintPithSatisfiedMetadata(
                    "She touch'd her fair large forehead to the ground,"),
            ),
        ),

        # Subscripted type alias aliasing a PEP 604-compliant union over a type
        # variable, a PEP 585-compliant generic subscripted by that same type
        # variable, and "None".
        HintPepMetadata(
            hint=AliasPep585IterableTContainerT[str],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Generic container whose items satisfy this child hint.
                HintPithSatisfiedMetadata(Pep585IterableTContainerT((
                    'Just where her falling hair', 'might be outspread',))),
                # String constant.
                HintPithSatisfiedMetadata(
                    'Her silver seasons four upon the night,'),
                # "None" singleton.
                HintPithSatisfiedMetadata(None),
                # Generic container whose items violate this child hint.
                HintPithUnsatisfiedMetadata(Pep585IterableTContainerT((
                    b'A soft and silken mat', b"for Saturn's feet.",))),
                # Byte string constant.
                HintPithUnsatisfiedMetadata(
                    b"One moon, with alteration slow, had shed"),
            ),
        ),

        # ................{ PEP 585 ~ generic : S, T           }................
        # Unsubscripted type alias aliasing a PEP 585-compliant generic
        # parametrized by two type variables.
        HintPepMetadata(
            hint=AliasPep585IterableTupleSTContainerTupleST,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_type_typing=True,
            # PEP 695-compliant parametrized type aliases are parametrized by
            # type variables implicitly instantiated only "on the fly" by Python
            # itself. These variables are *NOT* explicitly defined and thus
            # *NOT* safely accessible here outside of these aliases.
            is_typevars=True,
            is_typing=False,
            piths_meta=(
                # Instance of this generic containing one or more items.
                HintPithSatisfiedMetadata(Pep585IterableTupleSTContainerTupleST((
                    ('How beautiful,', b'if sorrow had not made',),
                    ('Sorrow more beautiful than', b"Beauty's self.",),
                ))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'There was a listening fear in her regard,'),
            ),
        ),

        # Subscripted type alias aliasing a PEP 585-compliant generic.
        HintPepMetadata(
            hint=AliasPep585IterableTupleSTContainerTupleST[str, bytes],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Generic container whose items satisfy this child hint.
                HintPithSatisfiedMetadata(Pep585IterableTupleSTContainerTupleST((
                    ('As if calamity', b'had but begun;',),
                    ('As if the vanward clouds', b'of evil days;',),
                ))),
                # Generic container whose items violate this child hint.
                HintPithUnsatisfiedMetadata(Pep585IterableTupleSTContainerTupleST((
                    (b'Had spent their malice,', 'and the sullen rear',),
                    (b'Was with its stored thunder', 'labouring up.',),
                ))),
                # Byte string constant.
                HintPithUnsatisfiedMetadata(
                    b"One hand she press'd upon that aching spot"),
            ),
        ),

        # ................{ PEP 585 ~ mapping                  }................
        # Unsubscripted type alias aliasing a PEP 585-compliant dictionary.
        HintPepMetadata(
            hint=AliasPep585Dict,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_type_typing=True,
            # PEP 695-compliant parametrized type aliases are parametrized by
            # type variables implicitly instantiated only "on the fly" by Python
            # itself. These variables are *NOT* explicitly defined and thus
            # *NOT* safely accessible here outside of these aliases.
            is_typevars=True,
            is_typing=False,
            piths_meta=(
                # Dictionary of key-value pairs of arbitrary types.
                HintPithSatisfiedMetadata({
                    'Would come in these like accents;': b'O how frail',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'To that large utterance of the early Gods!'),
            ),
        ),

        # Subscripted type alias aliasing a PEP 585-compliant dictionary of
        # ignorable key-value pairs.
        HintPepMetadata(
            hint=AliasPep585Dict[object, object],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping arbitrary hashables to arbitrary objects.
                HintPithSatisfiedMetadata({
                    '"Saturn, look up!': b'though wherefore, poor old King?',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'I have no comfort for thee, no not one'),
            ),
        ),

        # Subscripted type alias aliasing a PEP 585-compliant dictionary of
        # ignorable keys and unignorable values.
        HintPepMetadata(
            hint=AliasPep585Dict[object, str],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping arbitrary hashables to strings.
                HintPithSatisfiedMetadata({
                    0xFADEFEED: 'I cannot say, "O wherefore sleepest thou?"',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'For heaven is parted from thee, and the earth'),
                # Dictionary mapping arbitrary hashables to bytestrings.
                HintPithUnsatisfiedMetadata({
                    'Knows thee not,': b'thus afflicted, for a God;',}),
            ),
        ),

        # Subscripted type alias aliasing a PEP 585-compliant dictionary of
        # unignorable keys and ignorable values.
        HintPepMetadata(
            hint=AliasPep585Dict[str, object],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping strings to arbitrary objects.
                HintPithSatisfiedMetadata({
                    'And ocean too,': b'with all its solemn noise,',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    "Has from thy sceptre pass'd; and all the air"),
                # Dictionary mapping bytestrings to arbitrary objects.
                HintPithUnsatisfiedMetadata({
                    b'Of Parthian kings': 'scatter to every wind',}),
            ),
        ),

        # Subscripted type alias aliasing a PEP 585-compliant dictionary of
        # unignorable key-value pairs.
        HintPepMetadata(
            hint=AliasPep585Dict[int, str],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping integers to strings.
                HintPithSatisfiedMetadata({
                    1: 'Is emptied of thine hoary majesty.',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Thy thunder, conscious of the new command,'),
                # Dictionary mapping strings to strings.
                HintPithUnsatisfiedMetadata({
                    "Rumbles reluctant o'er our fallen house;": 48,}),
            ),
        ),

        # ................{ PEP 585 ~ tuple : fixed            }................
        # Unsubscripted type alias aliasing a PEP 585-compliant fixed-length
        # tuple type hint.
        HintPepMetadata(
            hint=AliasPep585TupleFixed,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_type_typing=True,
            # PEP 695-compliant parametrized type aliases are parametrized by
            # type variables implicitly instantiated only "on the fly" by Python
            # itself. These variables are *NOT* explicitly defined and thus
            # *NOT* safely accessible here outside of these aliases.
            is_typevars=True,
            is_typing=False,
            piths_meta=(
                # 2-tuple of items of arbitrary types.
                HintPithSatisfiedMetadata((
                    'Where beats the human heart,', 'as if just there,',)),
                # Empty tuple.
                HintPithUnsatisfiedMetadata(()),
                # 1-tuple of items of arbitrary types.
                HintPithUnsatisfiedMetadata((
                    'Though an immortal, she felt cruel pain:',)),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    "The other upon Saturn's bended neck"),
            ),
        ),

        # Subscripted type alias aliasing a PEP 585-compliant fixed-length
        # tuple type hint.
        HintPepMetadata(
            hint=AliasPep585TupleFixed[str, bytes],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # 2-tuple of items whose types satisfy these child hints.
                HintPithSatisfiedMetadata((
                    'She laid,', b'and to the level of his ear,',)),
                # 2-tuple of items whose types violate these child hints.
                HintPithUnsatisfiedMetadata((
                    'Leaning with parted lips,', 'some words she spake',)),
                # Empty tuple.
                HintPithUnsatisfiedMetadata(()),
                # 3-tuple of items of arbitrary types.
                HintPithUnsatisfiedMetadata((
                    'In solemn tenour', 'and deep', 'organ tone:',)),
                # Byte string constant.
                HintPithUnsatisfiedMetadata(
                    b"Some mourning words, which in our feeble tongue"),
            ),
        ),

        # ................{ PEP 585 ~ subclass                 }................
        # Unsubscripted type alias aliasing a PEP 585-compliant arbitrary type.
        HintPepMetadata(
            hint=AliasPep585Type,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_type_typing=True,
            # PEP 695-compliant parametrized type aliases are parametrized by
            # type variables implicitly instantiated only "on the fly" by Python
            # itself. These variables are *NOT* explicitly defined and thus
            # *NOT* safely accessible here outside of these aliases.
            is_typevars=True,
            is_typing=False,
            piths_meta=(
                # Arbitrary type.
                HintPithSatisfiedMetadata(complex),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Why should I ope thy melancholy eyes?'),
            ),
        ),

        # Any type, semantically equivalent under PEP 484 to the unsubscripted
        # "Type" singleton.
        HintPepMetadata(
            hint=AliasPep585Type[Any],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Arbitrary class.
                HintPithSatisfiedMetadata(bool),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Saturn, sleep on! while at thy feet I weep."'),
            ),
        ),

        # "type" superclass.
        HintPepMetadata(
            hint=AliasPep585Type[type],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Arbitrary metaclass.
                HintPithSatisfiedMetadata(NonIsinstanceableMetaclass),
                # Arbitrary class.
                HintPithUnsatisfiedMetadata(int),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'As when, upon a tranced summer-night,'),
            ),
        ),

        # Specific class.
        HintPepMetadata(
            hint=AliasPep585Type[Class],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Subclass of this class.
                HintPithSatisfiedMetadata(Subclass),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    "Those green-rob'd senators of mighty woods,"),
                # Non-subclass of this class.
                HintPithUnsatisfiedMetadata(bytes),
            ),
        ),

        # Two or more specific classes.
        HintPepMetadata(
            hint=AliasPep585Type[Class | OtherClass],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Arbitrary subclass of one class subscripting this hint.
                HintPithSatisfiedMetadata(Subclass),
                # Arbitrary subclass of another class subscripting this hint.
                HintPithSatisfiedMetadata(OtherSubclass),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Tall oaks, branch-charmed by the earnest stars,'),
                # Non-subclass of any classes subscripting this hint.
                HintPithUnsatisfiedMetadata(frozenset),
            ),
        ),

        # ................{ PEP 593                            }................
        # Unsubscripted type alias aliasing a PEP 593-compliant metahint.
        #
        # Note that:
        # * The child hint annotated by this metahint is "T | bytes".
        # * The type variable "T" in this child hint maps to *NO* concrete hint.
        # * Unmapped type variables are semantically meaningless and thus
        #   ignorable.
        # * A union over one or more ignorable child hints is itself ignorable.
        # * Ergo, the child hint annotated by this metahint is ignorable.
        # * However, the beartype validator validating this metahint is still
        #   unignorable. This validator validates that the current pith
        #   evaluates to true (i.e., is non-empty and non-zero), as defined by
        #   the following lambda tester:
        #       Is[lambda obj: bool(obj)]
        HintPepMetadata(
            hint=AliasPep593,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_type_typing=True,
            # PEP 695-compliant parametrized type aliases are parametrized by
            # type variables implicitly instantiated only "on the fly" by Python
            # itself. These variables are *NOT* explicitly defined and thus
            # *NOT* safely accessible here outside of these aliases.
            is_typevars=True,
            is_typing=False,
            piths_meta=(
                # Non-empty byte string.
                HintPithSatisfiedMetadata(
                    b"And thy sharp lightning in unpractis'd hands"),
                # Non-empty string constant.
                HintPithSatisfiedMetadata(
                    'Scorches and burns our once serene domain.'),
                # Empty byte string.
                HintPithUnsatisfiedMetadata(b''),
                # Empty string.
                HintPithUnsatisfiedMetadata(''),
            ),
        ),

        # Subscripted type alias aliasing a PEP 593-compliant metahint
        # annotating an ignorable child hint.
        HintPepMetadata(
            hint=AliasPep593[object],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Non-empty byte string.
                HintPithSatisfiedMetadata(
                    b'O aching time! O moments big as years!'),
                # Non-empty string constant.
                HintPithSatisfiedMetadata(
                    'All as ye pass swell out the monstrous truth,'),
                # Empty byte string.
                HintPithUnsatisfiedMetadata(b''),
                # Empty string.
                HintPithUnsatisfiedMetadata(''),
            ),
        ),

        # Subscripted type alias aliasing a PEP 593-compliant metahint
        # annotating an unignorable child hint.
        HintPepMetadata(
            hint=AliasPep593[int],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Non-zero integer.
                HintPithSatisfiedMetadata(0xFADEFACE),
                # Non-empty byte string.
                HintPithSatisfiedMetadata(
                    b'And press it so upon our weary griefs'),
                # Zero.
                HintPithUnsatisfiedMetadata(0),
                # Empty byte string.
                HintPithUnsatisfiedMetadata(b''),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'That unbelief has not a space to breathe.'),
            ),
        ),
    ))

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta
