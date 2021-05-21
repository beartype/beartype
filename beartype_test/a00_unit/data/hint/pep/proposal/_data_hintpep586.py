#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`586`**-compliant type hint test data.**
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype_test.a00_unit.data.hint.data_hintmeta import (
    PepHintMetadata,
    PepHintPithSatisfiedMetadata,
    PepHintPithUnsatisfiedMetadata,
)
from enum import Enum

# ....................{ ENUMERATIONS                      }....................
class _MasterlessDecreeVenomlessWhich(Enum):
    '''
    Arbitrary enumeration whose members are accessed below as literals.
    '''

    NOMENCLATURE_WEATHER_VANES_OF = 0
    NOMINALLY_UNSWAIN_AUTODIDACTIC_IDIOCRACY_LESS_A = 1

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :pep:`586`-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # If the active Python interpreter targets less than Python < 3.9, this
    # interpreter fails to support PEP 586. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_9:
        return
    # Else, the active Python interpreter targets at least Python >= 3.9 and
    # thus supports PEP 586.

    # ..................{ IMPORTS                           }..................
    # Defer Python >= 3.9-specific imports.
    from typing import (
        Literal,
    )

    # ..................{ TUPLES                            }..................
    # Add PEP 586-specific test type hints to this tuple global.
    data_module.HINTS_PEP_META.extend((
        # ................{ LITERALS                          }................
        # Literal "None" singleton. Look, this is ridiculous. What can you do?
        PepHintMetadata(
            hint=Literal[None],
            pep_sign=Literal,
            piths_satisfied_meta=(
                # "None" singleton defined by the same syntax.
                PepHintPithSatisfiedMetadata(None),
                # "None" singleton defined by different syntax but semantically
                # equal to the "None" singleton.
                PepHintPithSatisfiedMetadata(
                    {}.get('Looting Uncouth, ruddy Bȴood and')),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    pith='Worthily untrust-',
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(r'\bNone\b',),
                ),
            ),
        ),

        #
        # Literal arbitrary boolean. (Not that there are many of those...)
        PepHintMetadata(
            hint=Literal[True],
            pep_sign=Literal,
            piths_satisfied_meta=(
                # Boolean constant defined by the same syntax.
                PepHintPithSatisfiedMetadata(True),
                # Boolean constant defined by different syntax but semantically
                # equal to the same boolean.
                PepHintPithSatisfiedMetadata(data_module is data_module),
            ),
            piths_unsatisfied_meta=(
                # Boolean constant *NOT* equal to the same boolean.
                PepHintPithUnsatisfiedMetadata(
                    pith=False,
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected literal.
                    exception_str_match_regexes=(r'\bTrue\b',),
                ),
                # Integer constant semantically equal to the same boolean but
                # of a differing type.
                PepHintPithUnsatisfiedMetadata(
                    pith=1,
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(r'\bbool\b',),
                ),
            ),
        ),

        # Literal arbitrary integer.
        PepHintMetadata(
            hint=Literal[0x2a],
            pep_sign=Literal,
            piths_satisfied_meta=(
                # Integer constant defined by the same syntax.
                PepHintPithSatisfiedMetadata(0x2a),
                # Integer constant defined by different syntax but semantically
                # equal to the same integer.
                PepHintPithSatisfiedMetadata(42),
            ),
            piths_unsatisfied_meta=(
                # Integer constant *NOT* equal to the same integer.
                PepHintPithUnsatisfiedMetadata(
                    pith=41,
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected literal.
                    exception_str_match_regexes=(r'\b42\b',),
                ),
                # Floating-point constant semantically equal to the same
                # integer but of a differing type.
                PepHintPithUnsatisfiedMetadata(
                    pith=42.0,
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(r'\bint\b',),
                ),
            ),
        ),

        # Literal arbitrary byte string.
        PepHintMetadata(
            hint=Literal[
                b"Worthy, 'vain truthiness of (very invective-elected)"],
            pep_sign=Literal,
            piths_satisfied_meta=(
                # Byte string constant defined by the same syntax.
                PepHintPithSatisfiedMetadata(
                    b"Worthy, 'vain truthiness of (very invective-elected)"),
                # Byte string constant defined by different syntax but
                # semantically equal to the same byte string.
                PepHintPithSatisfiedMetadata(
                    b"Worthy, 'vain truthiness of "
                    b"(very invective-elected)"
                ),
            ),
            piths_unsatisfied_meta=(
                # Byte string constant *NOT* equal to the same byte string.
                PepHintPithUnsatisfiedMetadata(
                    pith=b"Thanes within",
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected literal.
                    exception_str_match_regexes=(r'\btruthiness\b',),
                ),
                # Unicode string constant semantically equal to the same byte
                # string but of a differing type.
                PepHintPithUnsatisfiedMetadata(
                    pith=(
                        "Worthy, 'vain truthiness of "
                        "(very invective-elected)"
                    ),
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(r'\bbytes\b',),
                ),
            ),
        ),

        # Literal arbitrary Unicode string.
        PepHintMetadata(
            hint=Literal['Thanklessly classed, nominal'],
            pep_sign=Literal,
            piths_satisfied_meta=(
                # Unicode string constant defined by the same syntax.
                PepHintPithSatisfiedMetadata('Thanklessly classed, nominal'),
                # Unicode string constant defined by different syntax but
                # semantically equal to the same Unicode string.
                PepHintPithSatisfiedMetadata(
                    'Thanklessly classed, '
                    'nominal'
                ),
            ),
            piths_unsatisfied_meta=(
                # Unicode string constant *NOT* equal to the same string.
                PepHintPithUnsatisfiedMetadata(
                    pith='Mass and',
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected literal.
                    exception_str_match_regexes=(r'\bnominal\b',),
                ),
                # Byte string constant semantically equal to the same Unicode
                # string but of a differing type.
                PepHintPithUnsatisfiedMetadata(
                    pith=b'Thanklessly classed, nominal',
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(r'\bstr\b',),
                ),
            ),
        ),

        # Literal arbitrary enumeration member.
        PepHintMetadata(
            hint=Literal[
                _MasterlessDecreeVenomlessWhich.NOMENCLATURE_WEATHER_VANES_OF],
            pep_sign=Literal,
            piths_satisfied_meta=(
                # Enumeration member accessed by the same syntax.
                PepHintPithSatisfiedMetadata(
                    _MasterlessDecreeVenomlessWhich.NOMENCLATURE_WEATHER_VANES_OF),
                # Enumeration member accessed by different syntax but
                # semantically equal to the same enumeration member.
                PepHintPithSatisfiedMetadata(
                    _MasterlessDecreeVenomlessWhich(0)),
            ),
            piths_unsatisfied_meta=(
                # Enumeration member *NOT* equal to the same member.
                PepHintPithUnsatisfiedMetadata(
                    pith=_MasterlessDecreeVenomlessWhich.NOMINALLY_UNSWAIN_AUTODIDACTIC_IDIOCRACY_LESS_A,
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected literal.
                    exception_str_match_regexes=(
                        r'\bNOMENCLATURE_WEATHER_VANES_OF\b',),
                ),
                # Integer constant semantically equal to the same index of this
                # enumeration member but of a differing type.
                PepHintPithUnsatisfiedMetadata(
                    pith=0,
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(
                        r'\b_MasterlessDecreeVenomlessWhich\b',),
                ),
            ),
        ),

        # ................{ LITERALS ~ nested                 }................
        # List of literal arbitrary Unicode strings.
        PepHintMetadata(
            hint=list[Literal[
                'ç‐omically gnomical whitebellied burden’s empathy of']],
            pep_sign=list,
            stdlib_type=list,
            is_pep585_builtin=True,
            piths_satisfied_meta=(
                # List of Unicode string constants semantically equal to the
                # same Unicode string.
                PepHintPithSatisfiedMetadata([
                    'ç‐omically gnomical whitebellied burden’s empathy of',
                    (
                        'ç‐omically gnomical '
                        'whitebellied burden’s '
                        'empathy of'
                    ),
                ]),
            ),
            piths_unsatisfied_meta=(
                # List of Unicode string constants *NOT* equal to the same
                # Unicode string.
                PepHintPithUnsatisfiedMetadata(
                    pith=[
                        'Earpiece‐piecemealed, mealy straw headpiece‐',
                        'Earned peace appeasement easements',
                    ],
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected literal.
                    exception_str_match_regexes=(r'\bgnomical\b',),
                ),
                # List of byte string constants.
                PepHintPithUnsatisfiedMetadata(
                    pith=[
                        b'Than',
                        b"Thankful strumpet's",
                    ],
                    # Match that the exception message raised for this object
                    # embeds the representation of the expected type.
                    exception_str_match_regexes=(r'\bstr\b',),
                ),
            ),
        ),

        # ................{ LITERALS ~ union                  }................
        # Literal union of two or more arbitrary literal objects.
        PepHintMetadata(
            hint=Literal[
                None,
                True,
                0x2a,
                b"Worthy, 'vain truthiness of (very invective-elected)",
                'Thanklessly classed, nominal',
                _MasterlessDecreeVenomlessWhich.NOMENCLATURE_WEATHER_VANES_OF,
            ],
            pep_sign=Literal,
            piths_satisfied_meta=(
                # Literal objects subscripting this literal union.
                PepHintPithSatisfiedMetadata(None),
                PepHintPithSatisfiedMetadata(True),
                PepHintPithSatisfiedMetadata(0x2a),
                PepHintPithSatisfiedMetadata(
                    b"Worthy, 'vain truthiness of (very invective-elected)"),
                PepHintPithSatisfiedMetadata('Thanklessly classed, nominal'),
                PepHintPithSatisfiedMetadata(
                    _MasterlessDecreeVenomlessWhich.NOMENCLATURE_WEATHER_VANES_OF),
            ),
            piths_unsatisfied_meta=(
                # Arbitrary object of the same type as one or more literal
                # objects subscripting this literal union but unequal to any
                # objects subscripting this literal union.
                PepHintPithUnsatisfiedMetadata(
                    pith='Empirism‐Tṙumpeted,',
                    # Match that the exception message raised for this object
                    # embeds the representation of all expected literals.
                    exception_str_match_regexes=(
                        r'\bNone\b',
                        r'\bTrue\b',
                        r'\b42\b',
                        r'\btruthiness\b',
                        r'\bnominal\b',
                        r'\bNOMENCLATURE_WEATHER_VANES_OF\b',
                    ),
                ),
                # Arbitrary object of a differing type as all literal objects
                # subscripting this literal union.
                # Integer constant semantically equal to the same index of this
                # enumeration member but of a differing type.
                PepHintPithUnsatisfiedMetadata(
                    pith=42.0,
                    # Match that the exception message raised for this object
                    # embeds the representation of all expected types.
                    exception_str_match_regexes=(
                        r'\bNone\b',
                        r'\bbool\b',
                        r'\bint\b',
                        r'\bbytes\b',
                        r'\bstr\b',
                        r'\b_MasterlessDecreeVenomlessWhich\b',
                    ),
                ),
            ),
        ),
    ))
