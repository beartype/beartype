#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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

# ....................{ TODO                               }....................
#FIXME: *WOOPS.* We should have read the standards a bit closer. Neither
#"typing.NamedTuple" or "typing.TypedDict" are intended for direct use as type
#hints. To quote official "typing" documentation:
#    These are not used in annotations. They are building blocks for declaring
#    types.
#
#Of course, all types *ARE* valid type hints. "typing.NamedTuple" and
#"typing.TypedDict" subclasses are types and thus also valid type hints. So, the
#superficial testing we perform below is certainly useful; we just don't need to
#do anything further, really. Phew!

# ....................{ ADDERS                             }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :pep:`484`-compliant PEP-noncompliant type hint test data to various
    global containers declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    import sys
    from beartype import BeartypeConf
    from beartype.typing import (
        NamedTuple,
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
    from beartype_test.a00_unit.data.data_type import Class
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintNonpepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ....................{ LOCALS                         }....................
    # PEP-compliant user-defined "collections.namedtuple" instance typed with
    # PEP-compliant type hints.
    NamedTupleType = NamedTuple(
        'NamedTupleType', [('fumarole', str), ('enrolled', int)])

    # ..................{ TUPLES                             }..................
    # Add PEP 484-specific (albeit technically PEP-noncompliant from the
    # @beartype perspective) test type hints to this dictionary global.
    data_module.HINTS_NONPEP_META.extend((
        # ................{ NAMEDTUPLE                         }................
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

        # ................{ TYPEDDICT                          }................
        # "TypedDict" instances transparently reduce to dicts.
        #FIXME: Implement us up, but note when doing so that:
        #* We currently unconditionally reduce "TypeDict" to "Mapping".
        #* "TypedDict" was first introduced with Python 3.8.

        # ................{ TYPE ~ builtin                     }................
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
                        # The double-quoted name of this builtin type.
                        r'"str"',
                    ),
                ),
            ),
        ),

        # ................{ TYPE ~ builtin : tower             }................
        # Types pertaining to the implicit numeric tower (i.e., optional PEP
        # 484-compliant (sub)standard in which type hints defined as broad
        # numeric types implicitly match all narrower numeric types as well by
        # enabling the "beartype.BeartypeConf.is_pep484_tower" parameter). When
        # enabled, @beartype implicitly expands:
        # * "float" to "float | int".
        # * "complex" to "complex | float | int".
        #
        # See also the "data_pep484" submodule, which defines additional
        # PEP 484-compliant type hints nesting type hints pertaining to the
        # implicit numeric tower (e.g., "Union[float, str]").

        # Floating-point number with the implicit numeric tower disabled.
        HintNonpepMetadata(
            hint=float,
            conf=BeartypeConf(is_pep484_tower=False),
            piths_meta=(
                # Floating-point number constant.
                HintPithSatisfiedMetadata(0.110001),
                # Integer constant.
                HintPithUnsatisfiedMetadata(
                    pith=110001,
                    # Match that the exception message raised for this pith
                    # contains...
                    exception_str_match_regexes=(
                        # The type *NOT* satisfied by this object.
                        r'\bfloat\b',
                    ),
                    # Match that the exception message raised for this pith
                    # does *NOT* contain...
                    exception_str_not_match_regexes=(
                        # A newline.
                        r'\n',
                        # A bullet delimiter.
                        r'\*',
                        # The double-quoted name of this builtin type.
                        r'"float"',
                    ),
                ),
            ),
        ),

        # Floating-point number with the implicit numeric tower enabled.
        HintNonpepMetadata(
            hint=float,
            conf=BeartypeConf(is_pep484_tower=True),
            piths_meta=(
                # Floating-point number constant.
                HintPithSatisfiedMetadata(0.577215664901532860606512090082),
                # Integer constant.
                HintPithSatisfiedMetadata(5772),
                # Complex number constant.
                HintPithUnsatisfiedMetadata(
                    pith=(1566 + 4901j),
                    # Match that the exception message raised for this pith
                    # contains...
                    exception_str_match_regexes=(
                        # The type *NOT* satisfied by this object.
                        r'\bfloat\b',
                    ),
                    # Match that the exception message raised for this pith
                    # does *NOT* contain...
                    exception_str_not_match_regexes=(
                        # A newline.
                        r'\n',
                        # A bullet delimiter.
                        r'\*',
                        # The double-quoted name of this builtin type.
                        r'"float"',
                    ),
                ),
            ),
        ),

        # Complex number with the implicit numeric tower disabled.
        HintNonpepMetadata(
            hint=complex,
            conf=BeartypeConf(is_pep484_tower=False),
            piths_meta=(
                # Complex number constant.
                HintPithSatisfiedMetadata(1.787 + 2316.5j),
                # Floating-point number constant.
                HintPithUnsatisfiedMetadata(
                    pith=0.300330000000000330033,
                    # Match that the exception message raised for this pith
                    # contains...
                    exception_str_match_regexes=(
                        # The type *NOT* satisfied by this object.
                        r'\bcomplex\b',
                    ),
                    # Match that the exception message raised for this pith
                    # does *NOT* contain...
                    exception_str_not_match_regexes=(
                        # A newline.
                        r'\n',
                        # A bullet delimiter.
                        r'\*',
                        # The double-quoted name of this builtin type.
                        r'"complex"',
                    ),
                ),
            ),
        ),

        # Complex number with the implicit numeric tower enabled.
        HintNonpepMetadata(
            hint=complex,
            conf=BeartypeConf(is_pep484_tower=True),
            piths_meta=(
                # Complex number constant.
                HintPithSatisfiedMetadata(2.622 + 575.5j),
                # Floating-point number constant.
                HintPithSatisfiedMetadata(0.8346268),
                # Integer constant.
                HintPithSatisfiedMetadata(1311),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith='Park-ed trails',
                    # Match that the exception message raised for this pith
                    # contains...
                    exception_str_match_regexes=(
                        # The type *NOT* satisfied by this object.
                        r'\bcomplex\b',
                    ),
                    # Match that the exception message raised for this pith
                    # does *NOT* contain...
                    exception_str_not_match_regexes=(
                        # A newline.
                        r'\n',
                        # A bullet delimiter.
                        r'\*',
                        # The double-quoted name of this builtin type.
                        r'"complex"',
                    ),
                ),
            ),
        ),

        # ................{ TYPE ~ builtin : fake              }................
        # Fake builtin types (i.e., types that are *NOT* builtin but which
        # nonetheless erroneously masquerade as being builtin), exercising edge
        # cases in @beartype code generation.
        #
        # See also:
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
