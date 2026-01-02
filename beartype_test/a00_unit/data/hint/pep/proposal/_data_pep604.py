#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`604`-compliant **union type hint test data.**

**Unions** are intentionally tested in this submodule rather than in the
:mod:`beartype_test.a00_unit.data.hint.pep.proposal._data_pep484` submodule
despite being specified by :pep:`484` and available under Python < 3.10. Why?
Because CPython now implicitly reduces *all* unions -- including older
:pep:`484`-compliant ``typing.Union[...]`` and ``typing.Optional[...]`` hints --
to newer :pep:`604`-compliant ``|``-delimited unions under Python >= 3.14.
Centralizing union logic into a single test submodule reflects the
centralization now performed by CPython itself.
'''

# ....................{ FIXTURES                           }....................
def hints_pep604_meta() -> 'List[HintPepMetadata]':
    '''
    Session-scoped fixture returning a list of :pep:`604`-compliant **type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPepMetadata`
    instances describing test-specific :pep:`604`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS ~ version                  }..................
    # Defer version-specific imports.
    from beartype import BeartypeConf
    from beartype.door import (
        UnionTypeHint,
    )
    from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
    from beartype._data.hint.sign.datahintsigns import (
        HintSignList,
        HintSignMutableSequence,
        HintSignOptional,
        HintSignSequence,
        HintSignUnion,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_14
    from beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta import (
        HintPepMetadata,
        PithSatisfiedMetadata,
        PithUnsatisfiedMetadata,
    )
    from beartype_test.a00_unit.data.pep.data_pep484 import (
        S,
        T,
    )
    from collections.abc import (
        Callable as CallableABC,
        MutableSequence as MutableSequenceABC,
        Sequence as SequenceABC,
    )

    # Intentionally import from the standard "typing" module rather than the
    # non-standard "beartype.typing" subpackage to ensure PEP 484-compliance.
    from typing import (
        Iterable,
        List,
        MutableSequence,
        Optional,
        Sequence,
        Tuple,
        Union,
    )

    # ..................{ CONSTANTS                          }..................
    # Sign uniquely identifying "typing.Optional[...]" hints. Specifically:
    # * Under Python >= 3.14, "typing.Optional[...]" hints trivially reduce to
    #   "typing.Union[...]" hints additionally subscripted by "None" and are
    #   thus identified by the "HintSignUnion" sign.
    # * Under Python <= 3.13, "typing.Optional[...]" hints do *NOT* reduce to
    #   "typing.Union[...]" hints additionally subscripted by "None". The two
    #   have distinct string representations and are thus partially distinct.
    #   Ergo, the former are thus identified by the "HintSignOptional" sign.
    _HINT_SIGN_OPTIONAL = (
        HintSignUnion if IS_PYTHON_AT_LEAST_3_14 else HintSignOptional)

    #
    # True only if the type of *ALL* PEP 604-compliant union hints is defined by
    # the standard "typing" module or not. The module defining this type differs
    # depending on Python version. Specifically:
    # * If the active Python interpreter targets Python >= 3.14, the
    #   canonical definition resides at "typing.Union".
    # * If the active Python interpreter targets Python <= 3.13, the
    #   canonical definition resides at "types.UnionType".
    _PEP604_IS_TYPING = IS_PYTHON_AT_LEAST_3_14

    # ..................{ TUPLES                             }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = [
        # ................{ NEW UNION                          }................
        # Union of one non-"typing" type and an originative "typing" type,
        # exercising a prominent edge case when raising human-readable
        # exceptions describing the failure of passed parameters or returned
        # values to satisfy this union.
        #
        # Interestingly, Python preserves this union as a PEP 604-compliant
        # new-style union rather than implicitly coercing this into a PEP
        # 484-compliant old-style union: e.g.,
        #     >>> int | list[str]
        #     int | list[str]
        HintPepMetadata(
            hint=int | list[str],
            pep_sign=HintSignUnion,
            is_type_typing=_PEP604_IS_TYPING,
            piths_meta=(
                # Integer constant.
                PithSatisfiedMetadata(87),
                # List of string items.
                PithSatisfiedMetadata([
                    'Into, my myopic mandrake‐manhandling, '
                    'panhandling slakes of',
                    'Televisual, dis‐informative Lakes, unsaintly, of',
                ]),
                # Floating-point constant.
                PithUnsatisfiedMetadata(
                    pith=10100.00101,
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

                # List of integers.
                PithUnsatisfiedMetadata(
                    pith=([1, 10, 271, 36995]),
                    # Match that the exception message raised for this object...
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

        # ................{ NEW UNION ~ nested                 }................
        # Nested unions exercising edge cases induced by Python >= 3.8
        # optimizations leveraging PEP 572-style assignment expressions.

        # Nested union of multiple non-"typing" types.
        HintPepMetadata(
            hint=list[int | str],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin_subbed=True,
            piths_meta=(
                # List containing a mixture of integer and string constants.
                PithSatisfiedMetadata([
                    'Telemarketing affirmative‐mined Ketamine’s',
                    470,
                ]),
                # String constant.
                PithUnsatisfiedMetadata(
                    pith='Apolitically',
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bint\b',
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # List of bytestring items.
                PithUnsatisfiedMetadata(
                    pith=[
                        b'Apoplectic hints of',
                        b'Stenographically',
                    ],
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by a
                        # random list item *NOT* satisfying this hint.
                        r'\bint\b',
                        r'\bstr\b',
                        # Declares the index of the random list item *NOT*
                        # satisfying this hint.
                        r'\b[Ll]ist index \d+ item\b',
                    ),
                ),
            ),
        ),

        # ................{ NEW UNION ~ optional               }................
        # Optional isinstance()-able "typing" type.
        HintPepMetadata(
            hint=tuple[str, ...] | None,
            # Note that although Python >= 3.10 distinguishes equivalent PEP
            # 484-compliant "typing.Union[...]" and "typing.Optional[...]" type
            # hints via differing machine-readable representations, the same
            # does *NOT* apply to PEP 604-compliant |-style unions, which remain
            # PEP 604-compliant and thus unions rather than optional. This
            # includes PEP 604-compliant |-style unions including the "None"
            # singleton signifying an optional type hint. Go figure.
            pep_sign=HintSignUnion,
            is_type_typing=_PEP604_IS_TYPING,
            piths_meta=(
                # None singleton.
                PithSatisfiedMetadata(None),
                # Tuple of string items.
                PithSatisfiedMetadata((
                    'Stentorian tenor of',
                    'Stunted numbness (in',
                )),
                # Floating-point constant.
                PithUnsatisfiedMetadata(
                    pith=2397.7932,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bNoneType\b',
                        r'\btuple\b',
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

        # ................{ OLD UNION                          }................
        # Note that unions of one argument (e.g., "Union[str]") *CANNOT* be
        # listed here, as the "typing" module implicitly reduces these unions
        # to only that argument (e.g., "str") on our behalf.
        #
        # Thanks. Thanks alot, "typing".

        # Ignorable unsubscripted "Union" attribute.
        HintPepMetadata(
            hint=Union,
            pep_sign=HintSignUnion,
            typehint_cls=UnionTypeHint,
            is_ignorable=True,
        ),

        # Union of one non-"typing" type and an originative "typing" type,
        # exercising a prominent edge case when raising human-readable
        # exceptions describing the failure of passed parameters or returned
        # values to satisfy this union.
        HintPepMetadata(
            hint=Union[int, Sequence[str]],
            pep_sign=HintSignUnion,
            typehint_cls=UnionTypeHint,
            warning_type=BeartypeDecorHintPep585DeprecationWarning,
            piths_meta=(
                # Integer constant.
                PithSatisfiedMetadata(21),
                # Sequence of string items.
                PithSatisfiedMetadata((
                    'To claim all ͼarth a number, penumbraed'
                    'By blessed Pendragon’s flagon‐bedraggling constancies',
                )),
                # Floating-point constant.
                #
                # Note that a string constant is intentionally *NOT* listed
                # here, as strings are technically sequences of strings of
                # length one commonly referred to as Unicode code points or
                # simply characters.
                PithUnsatisfiedMetadata(
                    pith=802.11,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bSequence\b',
                        r'\bint\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # Tuple of integers.
                PithUnsatisfiedMetadata(
                    pith=(1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89,),
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Contains a bullet point declaring the non-"typing"
                        # type *NOT* satisfied by this object.
                        r'\n\*\s.*\bint\b',
                        # Contains a bullet point declaring the index of the
                        # random tuple item *NOT* satisfying this hint.
                        r'\n\*\s.*\b[Tt]uple index \d+ item\b',
                    ),
                ),
            ),
        ),

        # Union of three non-"typing" types and an originative "typing" type of
        # a union of three non-"typing" types and an originative "typing" type,
        # exercising a prominent edge case when raising human-readable
        # exceptions describing the failure of passed parameters or returned
        # values to satisfy this union.
        HintPepMetadata(
            hint=Union[dict, float, int,
                Sequence[Union[dict, float, int, MutableSequence[str]]]],
            pep_sign=HintSignUnion,
            warning_type=BeartypeDecorHintPep585DeprecationWarning,
            typehint_cls=UnionTypeHint,
            piths_meta=(
                # Empty dictionary.
                PithSatisfiedMetadata({}),
                # Floating-point number constant.
                PithSatisfiedMetadata(777.777),
                # Integer constant.
                PithSatisfiedMetadata(777),
                # Sequence of dictionary, floating-point number, integer, and
                # sequence of string constant items.
                PithSatisfiedMetadata((
                    # Non-empty dictionary.
                    {
                        'Of': 'charnal memories,',
                        'Or': 'coterminously chordant‐disarmed harmonies',
                    },
                    # Floating-point number constant.
                    666.666,
                    # Integer constant.
                    666,
                    # Mutable sequence of string constants.
                    [
                        'Ansuded scientifically pontifical grapheme‐',
                        'Denuded hierography, professedly, to emulate ascen-',
                    ],
                )),
                # Complex number constant.
                PithUnsatisfiedMetadata(
                    pith=356+260j,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bSequence\b',
                        r'\bdict\b',
                        r'\bfloat\b',
                        r'\bint\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # Sequence of bytestring items.
                PithUnsatisfiedMetadata(
                    pith=(b"May they rest their certainties' Solicitousness to",),
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Contains a bullet point declaring one of the
                        # non-"typing" types *NOT* satisfied by this object.
                        r'\n\*\s.*\bint\b',
                        # Contains a bullet point declaring the index of the
                        # random tuple item *NOT* satisfying this hint.
                        r'\n\*\s.*\b[Tt]uple index \d+ item\b',
                    ),
                ),

                # Sequence of mutable sequences of bytestring items.
                PithUnsatisfiedMetadata(
                    pith=([b'Untaint these ties',],),
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Contains an unindented bullet point declaring one of
                        # the non-"typing" types unsatisfied by this object.
                        r'\n\*\s.*\bfloat\b',
                        # Contains an indented bullet point declaring one of
                        # the non-"typing" types unsatisfied by this object.
                        r'\n\s+\*\s.*\bint\b',
                        # Contains an unindented bullet point declaring the
                        # index of the random tuple item *NOT* satisfying
                        # this hint.
                        r'\n\*\s.*\b[Tt]uple index \d+ item\b',
                        # Contains an indented bullet point declaring the index
                        # of the random list item *NOT* satisfying this hint.
                        r'\n\s+\*\s.*\b[Ll]ist index \d+ item\b',
                    ),
                ),
            ),
        ),

        # Union of one non-"typing" type and one concrete generic.
        HintPepMetadata(
            hint=Union[str, Iterable[Tuple[S, T]]],
            pep_sign=HintSignUnion,
            typehint_cls=UnionTypeHint,
            typeargs_packed=(S, T,),
            warning_type=BeartypeDecorHintPep585DeprecationWarning,
            piths_meta=(
                # String constant.
                PithSatisfiedMetadata(
                    "O'er the wide aëry wilderness: thus driven"),
                # Iterable of 2-tuples of arbitrary items.
                PithSatisfiedMetadata([
                    ('By the bright shadow', 'of that lovely dream,',),
                    (b'Beneath the cold glare', b'of the desolate night,'),
                ]),
                # Integer constant.
                PithUnsatisfiedMetadata(
                    pith=0xCAFEFEED,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bstr\b',
                        r'\bIterable\b',
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

        # Union of *ONLY* subscripted type hints, exercising an edge case.
        HintPepMetadata(
            hint=Union[List[str], Tuple[bytes, ...]],
            pep_sign=HintSignUnion,
            typehint_cls=UnionTypeHint,
            warning_type=BeartypeDecorHintPep585DeprecationWarning,
            piths_meta=(
                # List of string items.
                PithSatisfiedMetadata(
                    ['Through tangled swamps', 'and deep precipitous dells,']),
                # Tuples of bytestring items.
                PithSatisfiedMetadata(
                    (b'Startling with careless step', b'the moonlight snake,')),
                # Integer constant.
                PithUnsatisfiedMetadata(
                    pith=0xFEEDBEEF,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\blist\b',
                        r'\btuple\b',
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

        # ................{ UNION ~ nested                     }................
        # Nested unions exercising edge cases induced by Python >= 3.8
        # optimizations leveraging PEP 572-style assignment expressions.

        # Nested union of multiple non-"typing" types.
        HintPepMetadata(
            hint=List[Union[int, str,]],
            pep_sign=HintSignList,
            warning_type=BeartypeDecorHintPep585DeprecationWarning,
            isinstanceable_type=list,
            piths_meta=(
                # List containing a mixture of integer and string constants.
                PithSatisfiedMetadata([
                    'Un‐seemly preening, pliant templar curs; and',
                    272,
                ]),
                # String constant.
                PithUnsatisfiedMetadata(
                    pith='Un‐seemly preening, pliant templar curs; and',
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bint\b',
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # List of bytestring items.
                PithUnsatisfiedMetadata(
                    pith=[
                        b'Blamelessly Slur-chastened rights forthwith, affrighting',
                        b"Beauty's lurid, beleaguered knolls, eland-leagued and",
                    ],
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by a
                        # random list item *NOT* satisfying this hint.
                        r'\bint\b',
                        r'\bstr\b',
                        # Declares the index of the random list item *NOT*
                        # satisfying this hint.
                        r'\b[Ll]ist index \d+ item\b',
                    ),
                ),
            ),
        ),

        # Nested union of one non-"typing" type and one "typing" type.
        HintPepMetadata(
            hint=Sequence[Union[str, bytes]],
            pep_sign=HintSignSequence,
            warning_type=BeartypeDecorHintPep585DeprecationWarning,
            isinstanceable_type=SequenceABC,
            piths_meta=(
                # Sequence of string and bytestring constants.
                PithSatisfiedMetadata((
                    b'For laconically formulaic, knavish,',
                    u'Or sordidly sellsword‐',
                    f'Horded temerities, bravely unmerited',
                )),
                # Integer constant.
                PithUnsatisfiedMetadata(
                    pith=7898797,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bbytes\b',
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # Sequence of integer items.
                PithUnsatisfiedMetadata(
                    pith=((144, 233, 377, 610, 987, 1598, 2585, 4183, 6768,)),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by a
                        # random tuple item *NOT* satisfying this hint.
                        r'\bbytes\b',
                        r'\bstr\b',
                        # Declares the index of the random tuple item *NOT*
                        # satisfying this hint.
                        r'\b[Tt]uple index \d+ item\b',
                    ),
                ),
            ),
        ),

        # Nested union of *NO* isinstanceable type and multiple "typing" types.
        HintPepMetadata(
            hint=MutableSequence[Union[bytes, CallableABC]],
            pep_sign=HintSignMutableSequence,
            warning_type=BeartypeDecorHintPep585DeprecationWarning,
            isinstanceable_type=MutableSequenceABC,
            piths_meta=(
                # Mutable sequence of string and bytestring constants.
                PithSatisfiedMetadata([
                    b"Canonizing Afrikaans-kennelled Mine canaries,",
                    lambda: 'Of a floridly torrid, hasty love — that league',
                ]),
                # String constant.
                PithUnsatisfiedMetadata(
                    pith='Effaced.',
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bbytes\b',
                        r'\bCallable\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # Mutable sequence of string constants.
                PithUnsatisfiedMetadata(
                    pith=[
                        'Of genteel gentle‐folk — that that Ƹsper',
                        'At my brand‐defaced, landless side',
                    ],
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by a
                        # random list item *NOT* satisfying this hint.
                        r'\bbytes\b',
                        r'\bCallable\b',
                        # Declares the index of the random list item *NOT*
                        # satisfying this hint.
                        r'\b[Ll]ist index \d+ item\b',
                    ),
                ),
            ),
        ),

        # ................{ UNION ~ optional                   }................
        # Ignorable unsubscripted "Optional" attribute.
        HintPepMetadata(
            hint=Optional,
            # The unsubscripted "Optional" attribute is *ALWAYS* identified by
            # its own unique sign, even under Python >= 3.14 where subscripted
            # "Optional[...]" hints are identified by the "HintSignUnion" sign.
            pep_sign=HintSignOptional,
            typehint_cls=UnionTypeHint,
            is_ignorable=True,
        ),

        # Optional isinstance()-able "typing" type.
        HintPepMetadata(
            hint=Optional[Sequence[str]],
            # Subscriptions of the "Optional" attribute reduce to
            # fundamentally different unsubscripted typing attributes depending
            # on Python version.
            pep_sign=_HINT_SIGN_OPTIONAL,
            warning_type=BeartypeDecorHintPep585DeprecationWarning,
            typehint_cls=UnionTypeHint,
            piths_meta=(
                # None singleton.
                PithSatisfiedMetadata(None),
                # Sequence of string items.
                PithSatisfiedMetadata((
                    'Of cuticular currents (...wide, wildly articulate,',
                    'And canting free, physico-stipulatingly) -',
                )),
                # Floating-point constant.
                #
                # Note that a string constant is intentionally *NOT* listed
                # here, as strings are technically sequences of strings of
                # length one commonly referred to as Unicode code points or
                # simply characters.
                PithUnsatisfiedMetadata(
                    pith=802.2,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bNoneType\b',
                        r'\bSequence\b',
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

        # ................{ UNION ~ tower                      }................
        # Type hints pertaining to the implicit numeric tower (i.e., optional
        # PEP 484-compliant (sub)standard in which type hints defined as broad
        # numeric types implicitly match all narrower numeric types as well by
        # enabling the "beartype.BeartypeConf.is_pep484_tower" parameter). When
        # enabled, @beartype implicitly expands:
        # * "float" to "float | int".
        # * "complex" to "complex | float | int".
        #
        # See also the "_data_nonpep484" submodule, which defines additional
        # PEP 484-compliant raw types pertaining to the implicit numeric tower
        # (e.g., "float", "complex").

        # Implicit numeric tower type *AND* an arbitrary type hint outside the
        # implicit numeric tower with the implicit numeric tower disabled.
        HintPepMetadata(
            hint=Union[float, Sequence[str]],
            pep_sign=HintSignUnion,
            warning_type=BeartypeDecorHintPep585DeprecationWarning,
            typehint_cls=UnionTypeHint,
            piths_meta=(
                # Floating-point constant.
                PithSatisfiedMetadata(42.4242424242424242),
                # Sequence of string items.
                PithSatisfiedMetadata((
                    'No sister-flower would be forgiven',
                    'If it disdained its brother;',
                )),
                # Integer constant.
                PithUnsatisfiedMetadata(
                    pith=0xBABEBABE,  # <-- 3133061822
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bfloat\b',
                        r'\bSequence\b',
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

        # Implicit numeric tower type *AND* an arbitrary type hint outside the
        # implicit numeric tower with the implicit numeric tower enabled.
        HintPepMetadata(
            hint=Union[float, Sequence[str]],
            conf=BeartypeConf(is_pep484_tower=True),
            pep_sign=HintSignUnion,
            warning_type=BeartypeDecorHintPep585DeprecationWarning,
            typehint_cls=UnionTypeHint,
            piths_meta=(
                # Floating-point constant.
                PithSatisfiedMetadata(24.2424242424242424),
                # Integer constant.
                PithSatisfiedMetadata(0xABBAABBA),  # <-- 2881137594
                # Sequence of string items.
                PithSatisfiedMetadata((
                    'And the sunlight clasps the earth',
                    'And the moonbeams kiss the sea:',
                )),
                # Complex constant.
                PithUnsatisfiedMetadata(
                    pith=42 + 24j,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object as well
                    # as a newline and bullet delimiter.
                    exception_str_match_regexes=(
                        r'\bfloat\b',
                        r'\bSequence\b',
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),
    ]

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta


def hints_pep604_ignorable_deep() -> list:
    '''
    List of :pep:`604`-compliant **deeply ignorable type hints** (i.e.,
    ignorable only on the non-trivial basis of their nested child type hints).
    '''

    # ..................{ IMPORTS                            }..................
    from typing import Any

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific deeply ignorable type hints.
    return [
        # New-style unions containing any ignorable type hint.
        #
        # Note that including *ANY* "typing"-based type hint (including
        # "typing.Any") in an "|"-style union causes Python to implicitly
        # produce a PEP 484- rather than PEP 604-compliant union (e.g.,
        # "typing.Union[Any, float, str]" in this case). Since that is more or
        # less fine in this context, we intentionally list such a deeply
        # ignorable hint here.
        Any | float | str,
        complex | int | object,
    ]
