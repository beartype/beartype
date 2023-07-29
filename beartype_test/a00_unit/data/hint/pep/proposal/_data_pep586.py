#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`586`-compliant **type hint test data.**
'''

# ....................{ IMPORTS                            }....................
from beartype_test._util.module.pytmodtyping import is_typing_attrs

# ....................{ ADDERS                             }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :pep:`586`-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # If *NO* typing module declares a "Literal" factory, the active Python
    # interpreter fails to support PEP 586. In this case, reduce to a noop.
    if not is_typing_attrs('Literal'):
        # print('Ignoring "Literal"...')
        return
    # print('Testing "Literal"...')
    # Else, this interpreter supports PEP 586.

    # ..................{ IMPORTS                            }..................
    # Defer data-dependent imports.
    from beartype.typing import List
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignList,
        HintSignLiteral,
    )
    from beartype._util.module.lib.utiltyping import iter_typing_attrs
    from beartype_test.a00_unit.data.data_type import (
        MasterlessDecreeVenomlessWhich)
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ..................{ FACTORIES                          }..................
    # For each "Literal" type hint factory importable from a typing module...
    for Literal in iter_typing_attrs('Literal'):
        # Add PEP 586-specific test type hints to this tuple global.
        data_module.HINTS_PEP_META.extend((
            # ..............{ LITERALS                           }..............
            # Literal "None" singleton. Look, this is ridiculous. What you do?
            HintPepMetadata(
                hint=Literal[None],
                pep_sign=HintSignLiteral,
                is_args=True,
                piths_meta=(
                    # "None" singleton defined by the same syntax.
                    HintPithSatisfiedMetadata(None),
                    # "None" singleton defined by different syntax but
                    # semantically equal to the "None" singleton.
                    HintPithSatisfiedMetadata(
                        {}.get('Looting Uncouth, ruddy Bȴood and')),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        pith='Worthily untrust-',
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # type.
                        exception_str_match_regexes=(r'\bNone\b',),
                    ),
                ),
            ),

            # Literal arbitrary boolean. (Not that there are many of those...)
            HintPepMetadata(
                hint=Literal[True],
                pep_sign=HintSignLiteral,
                is_args=True,
                piths_meta=(
                    # Boolean constant defined by the same syntax.
                    HintPithSatisfiedMetadata(True),
                    # Boolean constant defined by different syntax but
                    # semantically equal to the same boolean.
                    HintPithSatisfiedMetadata(data_module is data_module),
                    # Boolean constant *NOT* equal to the same boolean.
                    HintPithUnsatisfiedMetadata(
                        pith=False,
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # literal.
                        exception_str_match_regexes=(r'\bTrue\b',),
                    ),
                    # Integer constant semantically equal to the same boolean
                    # but of a differing type.
                    HintPithUnsatisfiedMetadata(
                        pith=1,
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # type.
                        exception_str_match_regexes=(r'\bbool\b',),
                    ),
                ),
            ),

            # Literal arbitrary integer.
            HintPepMetadata(
                hint=Literal[0x2a],
                pep_sign=HintSignLiteral,
                is_args=True,
                piths_meta=(
                    # Integer constant defined by the same syntax.
                    HintPithSatisfiedMetadata(0x2a),
                    # Integer constant defined by different syntax but
                    # semantically equal to the same integer.
                    HintPithSatisfiedMetadata(42),
                    # Integer constant *NOT* equal to the same integer.
                    HintPithUnsatisfiedMetadata(
                        pith=41,
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # literal.
                        exception_str_match_regexes=(r'\b42\b',),
                    ),
                    # Floating-point constant semantically equal to the same
                    # integer but of a differing type.
                    HintPithUnsatisfiedMetadata(
                        pith=42.0,
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # type.
                        exception_str_match_regexes=(r'\bint\b',),
                    ),
                ),
            ),

            # Literal arbitrary byte string.
            HintPepMetadata(
                hint=Literal[
                    b"Worthy, 'vain truthiness of (very invective-elected)"],
                pep_sign=HintSignLiteral,
                is_args=True,
                piths_meta=(
                    # Byte string constant defined by the same syntax.
                    HintPithSatisfiedMetadata(
                        b"Worthy, 'vain truthiness of (very invective-elected)"),
                    # Byte string constant defined by different syntax but
                    # semantically equal to the same byte string.
                    HintPithSatisfiedMetadata(
                        b"Worthy, 'vain truthiness of "
                        b"(very invective-elected)"
                    ),
                    # Byte string constant *NOT* equal to the same byte string.
                    HintPithUnsatisfiedMetadata(
                        pith=b"Thanes within",
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # literal.
                        exception_str_match_regexes=(r'\btruthiness\b',),
                    ),
                    # Unicode string constant semantically equal to the same
                    # byte string but of a differing type.
                    HintPithUnsatisfiedMetadata(
                        pith=(
                            "Worthy, 'vain truthiness of "
                            "(very invective-elected)"
                        ),
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # type.
                        exception_str_match_regexes=(r'\bbytes\b',),
                    ),
                ),
            ),

            # Literal arbitrary Unicode string.
            HintPepMetadata(
                hint=Literal['Thanklessly classed, nominal'],
                pep_sign=HintSignLiteral,
                is_args=True,
                piths_meta=(
                    # Unicode string constant defined by the same syntax.
                    HintPithSatisfiedMetadata('Thanklessly classed, nominal'),
                    # Unicode string constant defined by different syntax but
                    # semantically equal to the same Unicode string.
                    HintPithSatisfiedMetadata(
                        'Thanklessly classed, '
                        'nominal'
                    ),
                    # Unicode string constant *NOT* equal to the same string.
                    HintPithUnsatisfiedMetadata(
                        pith='Mass and',
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # literal.
                        exception_str_match_regexes=(r'\bnominal\b',),
                    ),
                    # Byte string constant semantically equal to the same
                    # Unicode string but of a differing type.
                    HintPithUnsatisfiedMetadata(
                        pith=b'Thanklessly classed, nominal',
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # type.
                        exception_str_match_regexes=(r'\bstr\b',),
                    ),
                ),
            ),

            # Literal arbitrary enumeration member.
            HintPepMetadata(
                hint=Literal[
                    MasterlessDecreeVenomlessWhich.
                    NOMENCLATURE_WEATHER_VANES_OF
                ],
                pep_sign=HintSignLiteral,
                is_args=True,
                piths_meta=(
                    # Enumeration member accessed by the same syntax.
                    HintPithSatisfiedMetadata(
                        MasterlessDecreeVenomlessWhich.
                        NOMENCLATURE_WEATHER_VANES_OF
                    ),
                    # Enumeration member accessed by different syntax but
                    # semantically equal to the same enumeration member.
                    HintPithSatisfiedMetadata(
                        MasterlessDecreeVenomlessWhich(0)),
                    # Enumeration member *NOT* equal to the same member.
                    HintPithUnsatisfiedMetadata(
                        pith=(
                            MasterlessDecreeVenomlessWhich.
                            NOMINALLY_UNSWAIN_AUTODIDACTIC_IDIOCRACY_LESS_A
                        ),
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # literal.
                        exception_str_match_regexes=(
                            r'\bNOMENCLATURE_WEATHER_VANES_OF\b',),
                    ),
                    # Integer constant semantically equal to the same index of
                    # this enumeration member but of a differing type.
                    HintPithUnsatisfiedMetadata(
                        pith=0,
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # type.
                        exception_str_match_regexes=(
                            r'\bMasterlessDecreeVenomlessWhich\b',),
                    ),
                ),
            ),

            # ..............{ LITERALS ~ nested                  }..............
            # List of literal arbitrary Unicode strings.
            HintPepMetadata(
                hint=List[Literal[
                    'ç‐omically gnomical whitebellied burden’s empathy of']],
                pep_sign=HintSignList,
                isinstanceable_type=list,
                piths_meta=(
                    # List of Unicode string constants semantically equal to
                    # the same Unicode string.
                    HintPithSatisfiedMetadata([
                        'ç‐omically gnomical whitebellied burden’s empathy of',
                        (
                            'ç‐omically gnomical '
                            'whitebellied burden’s '
                            'empathy of'
                        ),
                    ]),
                    # List of Unicode string constants *NOT* equal to the same
                    # Unicode string.
                    HintPithUnsatisfiedMetadata(
                        pith=[
                            'Earpiece‐piecemealed, mealy straw headpiece‐',
                            'Earned peace appeasement easements',
                        ],
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # literal.
                        exception_str_match_regexes=(r'\bgnomical\b',),
                    ),
                    # List of byte string constants.
                    HintPithUnsatisfiedMetadata(
                        pith=[
                            b'Than',
                            b"Thankful strumpet's",
                        ],
                        # Match that the exception message raised for this
                        # object embeds the representation of the expected
                        # type.
                        exception_str_match_regexes=(r'\bstr\b',),
                    ),
                ),
            ),

            # ..............{ LITERALS ~ union                   }..............
            # Literal union of two or more arbitrary literal objects.
            HintPepMetadata(
                hint=Literal[
                    None,
                    True,
                    0x2a,
                    b"Worthy, 'vain truthiness of (very invective-elected)",
                    'Thanklessly classed, nominal',
                    (
                        MasterlessDecreeVenomlessWhich.
                        NOMENCLATURE_WEATHER_VANES_OF
                    ),
                ],
                pep_sign=HintSignLiteral,
                is_args=True,
                piths_meta=(
                    # Literal objects subscripting this literal union.
                    HintPithSatisfiedMetadata(None),
                    HintPithSatisfiedMetadata(True),
                    HintPithSatisfiedMetadata(0x2a),
                    HintPithSatisfiedMetadata(
                        b"Worthy, 'vain truthiness of (very invective-elected)"
                    ),
                    HintPithSatisfiedMetadata('Thanklessly classed, nominal'),
                    HintPithSatisfiedMetadata(
                        MasterlessDecreeVenomlessWhich.
                        NOMENCLATURE_WEATHER_VANES_OF
                    ),
                    # Arbitrary object of the same type as one or more literal
                    # objects subscripting this literal union but unequal to
                    # any objects subscripting this literal union.
                    HintPithUnsatisfiedMetadata(
                        pith='Empirism‐Tṙumpeted,',
                        # Match that the exception message raised for this
                        # object embeds the representation of all expected
                        # literals.
                        exception_str_match_regexes=(
                            r'\bNone\b',
                            r'\bTrue\b',
                            r'\b42\b',
                            r'\btruthiness\b',
                            r'\bnominal\b',
                            r'\bNOMENCLATURE_WEATHER_VANES_OF\b',
                        ),
                    ),
                    # Arbitrary object of a differing type from all literal
                    # objects subscripting this literal union.
                    HintPithUnsatisfiedMetadata(
                        pith=42.0,
                        # Match that the exception message raised for this
                        # object embeds the representation of all expected
                        # types.
                        exception_str_match_regexes=(
                            r'\bNone\b',
                            r'\bbool\b',
                            r'\bint\b',
                            r'\bbytes\b',
                            r'\bstr\b',
                            r'\bMasterlessDecreeVenomlessWhich\b',
                        ),
                    ),
                ),
            ),
        ))
