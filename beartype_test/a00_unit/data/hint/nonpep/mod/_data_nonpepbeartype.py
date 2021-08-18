#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype-specific PEP-noncompliant type hints** (i.e., unofficial type hints
supported *only* by the :mod:`beartype.beartype` decorator) test data.

These hints include:

* **Fake builtin types** (i.e., types that are *not* builtin but which
  nonetheless erroneously masquerade as being builtin).
* **Tuple unions** (i.e., tuples containing *only* standard classes and
  forward references to standard classes).
'''

# ....................{ IMPORTS                           }....................
import sys
from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
    HintNonPepMetadata,
    HintPithSatisfiedMetadata,
    HintPithUnsatisfiedMetadata,
)
from beartype._cave._cavefast import (
    EllipsisType,
    FunctionType,
    FunctionOrMethodCType,
    MethodBoundInstanceOrClassType,
    ModuleType,
    NoneType,
    NotImplementedType,
)

# ....................{ CLASSES                           }....................
class ThankfulStrumpet(object):
    '''
    Arbitrary class.
    '''

    def empirism_trumpeted(self) -> None:
        '''
        Arbitrary method.
        '''

        pass

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :mod:`beartype`-specific PEP-noncompliant type hint test data to
    various global containers declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # Arbitrary instance of an arbitrary class.
    manky_crumpet = ThankfulStrumpet()

    # ..................{ TUPLES                            }..................
    # Add beartype-specific PEP-noncompliant test type hints to this dictionary
    # global.
    data_module.HINTS_NONPEP_META.extend((
        # ................{ TUPLE UNION                       }................
        # Beartype-specific tuple unions (i.e., tuples containing one or more
        # isinstanceable classes).

        # Tuple union of one isinstanceable class.
        HintNonPepMetadata(
            hint=(str,),
            piths_satisfied_meta=(
                # String constant.
                HintPithSatisfiedMetadata('Pinioned coin tokens'),
            ),
            piths_unsatisfied_meta=(
                # Byte-string constant.
                HintPithUnsatisfiedMetadata(
                    pith=b'Murkily',
                    # Match that the exception message raised for this pith
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this pith
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # Tuple union of two or more isinstanceable classes.
        HintNonPepMetadata(
            hint=(int, str),
            piths_satisfied_meta=(
                # Integer constant.
                HintPithSatisfiedMetadata(12),
                # String constant.
                HintPithSatisfiedMetadata('Smirk‐opined — openly'),
            ),
            piths_unsatisfied_meta=(
                # Byte-string constant.
                HintPithUnsatisfiedMetadata(
                    pith=b'Betokening',
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
            ),
        ),

        # ................{ TYPE ~ builtin                    }................
        # Builtin type.
        HintNonPepMetadata(
            hint=str,
            piths_satisfied_meta=(
                # String constant.
                HintPithSatisfiedMetadata('Glassily lassitudinal bȴood-'),
            ),
            piths_unsatisfied_meta=(
                # Byte-string constant.
                HintPithUnsatisfiedMetadata(
                    pith=b'Stains, disdain-fully ("...up-stairs!"),',
                    # Match that the exception message raised for this pith
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this pith
                    # does *NOT* contain...
                    exception_str_not_match_regexes=(
                        # A newline.
                        r'\n',
                        # A bullet delimiter.
                        r'\*',
                        # Descriptive terms applied only to non-builtin types.
                        r'\bprotocol\b',
                        # The double-quoted name of this builtin type.
                        r'"str"',
                    ),
                ),
            ),
        ),

        # ................{ TYPE ~ builtin : fake             }................
        # Fake builtin types (i.e., types that are *NOT* builtin but which
        # nonetheless erroneously masquerade as being builtin), exercising edge
        # cases in @beartype code generation. See also:
        # * The "beartype._data.cls.datacls.TYPES_BUILTIN_FAKE" set.

        # Fake builtin ellipsis type.
        HintNonPepMetadata(
            hint=EllipsisType,
            piths_satisfied_meta=(
                # Ellipsis singleton.
                HintPithSatisfiedMetadata(...),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Masterless decree, venomless, which'),
            ),
        ),

        # Fake builtin pure-Python function type.
        HintNonPepMetadata(
            hint=FunctionType,
            piths_satisfied_meta=(
                # Pure-Python function.
                HintPithSatisfiedMetadata(add_data),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Nomenclature weather‐vanes of'),
            ),
        ),

        # Fake builtin C-based function type.
        HintNonPepMetadata(
            hint=FunctionOrMethodCType,
            piths_satisfied_meta=(
                # C-based function.
                HintPithSatisfiedMetadata(len),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Nominally unswain, autodidactic idiocracy, less a'),
            ),
        ),

        # Fake builtin bound method type.
        HintNonPepMetadata(
            hint=MethodBoundInstanceOrClassType,
            piths_satisfied_meta=(
                # Bound method.
                HintPithSatisfiedMetadata(manky_crumpet.empirism_trumpeted),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'ç‐omically gnomical whitebellied burden’s empathy of'),
            ),
        ),

        # Fake builtin module type.
        HintNonPepMetadata(
            hint=ModuleType,
            piths_satisfied_meta=(
                # Imported module.
                HintPithSatisfiedMetadata(sys),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Earpiece‐piecemealed, mealy straw headpiece-'),
            ),
        ),

        # Fake builtin "None" singleton type.
        HintNonPepMetadata(
            hint=NoneType,
            piths_satisfied_meta=(
                # "None" singleton.
                HintPithSatisfiedMetadata(None),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Earned peace appeasement easements'),
            ),
        ),

        # Fake builtin  type.
        HintNonPepMetadata(
            hint=NotImplementedType,
            piths_satisfied_meta=(
                # "NotImplemented" singleton.
                HintPithSatisfiedMetadata(NotImplemented),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Than'),
            ),
        ),
    ))
