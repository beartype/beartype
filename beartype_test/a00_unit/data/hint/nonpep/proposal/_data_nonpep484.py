#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant PEP-noncompliant type hint test data.

:pep:`484`-compliant type hints *mostly* indistinguishable from
PEP-noncompliant type hints include:

* :func:`typing.NamedTuple`, a high-level factory function deferring to the
  lower-level :func:`collections.namedtuple` factory function creating and
  returning :class:`tuple` instances annotated by PEP-compliant type hints.
* :func:`typing.TypedDict`, a high-level factory function creating and
  returning :class:`dict` instances annotated by PEP-compliant type hints.
'''

# ....................{ IMPORTS                           }....................
import sys
from beartype._cave._cavefast import (
    EllipsisType,
    FunctionType,
    FunctionOrMethodCType,
    MethodBoundInstanceOrClassType,
    ModuleType,
    NoneType,
    NotImplementedType,
)
from beartype_test.a00_unit.data.data_type import Class
from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
    HintNonpepMetadata,
    HintPithSatisfiedMetadata,
    HintPithUnsatisfiedMetadata,
)
from typing import (
    NamedTuple,
)

# ....................{ GLOBALS                           }....................
NamedTupleType = NamedTuple(
    'NamedTupleType', [('fumarole', str), ('enrolled', int)])
'''
PEP-compliant user-defined :func:`collections.namedtuple` instance typed with
PEP-compliant annotations.
'''

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :pep:`484`**-compliant PEP-noncompliant type hint test data to various
    global containers declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # ..................{ TUPLES                            }..................
    # Add PEP 484-specific PEP-noncompliant test type hints to this dictionary
    # global.
    data_module.HINTS_NONPEP_META.extend((
        # ................{ NAMEDTUPLE                        }................
        # "NamedTuple" instances transparently reduce to standard tuples and
        # *MUST* thus be handled as non-"typing" type hints.
        HintNonpepMetadata(
            hint=NamedTupleType,
            piths_meta=(
                # Named tuple containing correctly typed items.
                HintPithSatisfiedMetadata(
                    NamedTupleType(fumarole='Leviathan', enrolled=37)),
                # String constant.
                HintPithUnsatisfiedMetadata('Of ͼarthen concordance that'),
                #FIXME: Uncomment after implementing "NamedTuple" support.
                # # Named tuple containing incorrectly typed items.
                # HintPithUnsatisfiedMetadata(
                #     pith=NamedTupleType(fumarole='Leviathan', enrolled=37),
                #     # Match that the exception message raised for this object...
                #     exception_str_match_regexes=(
                #         # Declares the name of this tuple's problematic item.
                #         r'\s[Ll]ist item 0\s',
                #     ),
                # ),
            ),
        ),

        # ................{ TYPEDDICT                         }................
        # "TypedDict" instances transparently reduce to dicts.
        #FIXME: Implement us up, but note when doing so that:
        #* We currently unconditionally reduce "TypeDict" to "Mapping".
        #* "TypedDict" was first introduced with Python 3.8.

        # ................{ TYPE ~ builtin                    }................
        # Integer.
        HintNonpepMetadata(
            hint=int,
            piths_meta=(
                # Integer constant.
                HintPithSatisfiedMetadata(42),  # <-- we went there, folks
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith='Introspectively ‘allein,’ dealigning consangui-',
                    # Match that the exception message raised for this pith
                    # contains...
                    exception_str_match_regexes=(
                        # The type *NOT* satisfied by this object.
                        r'\bint\b',
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
                        r'"int"',
                    ),
                ),
            ),
        ),

        # Unicode string.
        HintNonpepMetadata(
            hint=str,
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata('Glassily lassitudinal bȴood-'),
                # Byte-string constant.
                HintPithUnsatisfiedMetadata(
                    pith=b'Stains, disdain-fully ("...up-stairs!"),',
                    # Match that the exception message raised for this pith
                    # contains...
                    exception_str_match_regexes=(
                        # The type *NOT* satisfied by this object.
                        r'\bstr\b',
                        # The representation of this object preserved as is.
                        r'\sb\'Stains, disdain-fully \("...up-stairs!"\),\'\s',
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
                # Integer constant.
                HintPithUnsatisfiedMetadata(
                    pith=666,  # <-- number of the beast, yo
                    # Match that the exception message raised for this pith
                    # contains...
                    exception_str_match_regexes=(
                        # The type *NOT* satisfied by this object.
                        r'\bstr\b',
                        # The representation of this object preserved as is.
                        r'\s666\s',
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
        HintNonpepMetadata(
            hint=EllipsisType,
            piths_meta=(
                # Ellipsis singleton.
                HintPithSatisfiedMetadata(...),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Masterless decree, venomless, which'),
            ),
        ),

        # Fake builtin pure-Python function type.
        HintNonpepMetadata(
            hint=FunctionType,
            piths_meta=(
                # Pure-Python function.
                HintPithSatisfiedMetadata(add_data),
                # String constant.
                HintPithUnsatisfiedMetadata('Nomenclature weather‐vanes of'),
            ),
        ),

        # Fake builtin C-based function type.
        HintNonpepMetadata(
            hint=FunctionOrMethodCType,
            piths_meta=(
                # C-based function.
                HintPithSatisfiedMetadata(len),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Nominally unswain, autodidactic idiocracy, less a'),
            ),
        ),

        # Fake builtin bound method type.
        HintNonpepMetadata(
            hint=MethodBoundInstanceOrClassType,
            piths_meta=(
                # Bound method.
                HintPithSatisfiedMetadata(Class().instance_method),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'ç‐omically gnomical whitebellied burden’s empathy of'),
            ),
        ),

        # Fake builtin module type.
        HintNonpepMetadata(
            hint=ModuleType,
            piths_meta=(
                # Imported module.
                HintPithSatisfiedMetadata(sys),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Earpiece‐piecemealed, mealy straw headpiece-'),
            ),
        ),

        # Fake builtin "None" singleton type.
        HintNonpepMetadata(
            hint=NoneType,
            piths_meta=(
                # "None" singleton.
                HintPithSatisfiedMetadata(None),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Earned peace appeasement easements'),
            ),
        ),

        # Fake builtin "NotImplemented" type.
        HintNonpepMetadata(
            hint=NotImplementedType,
            piths_meta=(
                # "NotImplemented" singleton.
                HintPithSatisfiedMetadata(NotImplemented),
                # String constant.
                HintPithUnsatisfiedMetadata('Than'),
            ),
        ),
    ))
