#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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
    from beartype.typing import (
        Union,
    )
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignPep695TypeAliasSubscripted,
        HintSignPep695TypeAliasUnsubscripted,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ..................{ LOCALS ~ concrete                  }..................
    # Simple type alias whose value is a standard type hint containing *NO*
    # syntax or semantics unique to PEP 695-compliant type aliases (e.g., *NO*
    # forward references, recursion, or type variables).
    type AliasSimple = int | list[str]

    # ..................{ LOCALS ~ generic                   }..................
    # Generic type alias support is unavoidably implemented in an *EXTREMELY*
    # fragile manner throughout the @beartype codebase. Recursively "bubbling
    # up" the concrete child type hints subscripting a generic type alias into
    # the lower-level target type hint aliased by that generic type alias is so
    # non-trivial that it necessitates implementing manual support for "bubbling
    # up" across both all hint-specific dynamic code generators *AND* all
    # hint-specific dynamic exception raisers: which is to say, basically the
    # *ENTIRE* "beartype._check" subpackage.
    #
    # Generic type alias support is so widely distributed that the *ONLY* valid
    # means of testing this support is to exhaustively define here and
    # subsequently use below at least one generic type alias for *EACH* other
    # PEP standard supported by @beartype. Non-trivial, thy name is PEP 695.

    # Generic type alias whose value is a PEP 604-compliant new union of:
    # * Two or more generic type hints parametrized by the same type variable
    #   subscripting this alias *AND*...
    # * A PEP 484-compliant old union of (...waitforit) two or more generic type
    #   hints parametrized by the same type variable subscripting this alias.
    #
    # This alias thus tests that dynamic code generation for PEP 484- and
    # 604-compliant unions preserves PEP 484-compliant type variable mappings
    # while also flattening directly nested unions into the top-level union.
    type AliasPep484604[T] = (
        # PEP 604-compliant new union of two or more generic type hints
        # parametrized by the same type variable subscripting this alias.
        list[T] | set[T] |
        # PEP 484-compliant old union of (...waitforit) two or more generic type
        # hints parametrized by the same type variable subscripting this alias.
        Union[dict[T, T] | frozenset[T]]
    )

    # ..................{ LISTS                              }..................
    # Add PEP 604-specific test type hints to this list.
    hints_pep_meta.extend((
        # ................{ TYPE ALIAS ~ unsubscripted         }................
        # Unsubscripted non-generic type alias whose value is a standard type
        # hint containing *NO* syntax or semantics unique to PEP 695-compliant
        # type aliases (e.g., *NO* forward references, recursion, or type
        # variables).
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

        # Arbitrary unsubscripted generic type alias.
        HintPepMetadata(
            hint=AliasPep484604,
            pep_sign=HintSignPep695TypeAliasUnsubscripted,
            is_type_typing=True,
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

        # ................{ TYPE ALIAS ~ subscripted           }................
        # Subscripted generic type alias testing type variable mappings across
        # PEP 484- and 604-compliant union hints.
        HintPepMetadata(
            hint=AliasPep484604[str],
            pep_sign=HintSignPep695TypeAliasSubscripted,
            is_pep585_builtin_subscripted=True,
            # is_type_typing=True,
            # is_typevars=False,
            # is_typing=False,
            piths_meta=(
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
                HintPithSatisfiedMetadata({
                    b'Was on him.': b'Yet a little, ere it fled,',
                    b'id he resign': b'his high and holy soul',
                }),
                # Frozen set of arbitrary objects all of the same invalid type.
                HintPithSatisfiedMetadata(frozenset((
                    b'To images of the majestic past,',
                    b'That paused within his passive being now,',
                ))),
                # List of arbitrary objects all of the same invalid type.
                HintPithSatisfiedMetadata([
                    b'Like winds that bear sweet music, when they breathe',
                    b'Through some dim latticed chamber. He did place',
                ]),
                # Set of arbitrary objects all of the same invalid type.
                HintPithSatisfiedMetadata({
                    b'His pale lean hand upon the rugged trunk',
                    b'Of the old pine. Upon an ivied stone',
                }),
                # Integer constant.
                HintPithUnsatisfiedMetadata(
                    pith=0xFACECAFE,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
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
    ))

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta
