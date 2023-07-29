#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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

# ....................{ ADDERS                             }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :mod:`beartype`-specific PEP-noncompliant type hint test data to
    various global containers declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer data-specific imports.
    from beartype.plug import BeartypeHintable
    from beartype.vale import Is
    from beartype._util.module.lib.utiltyping import iter_typing_attrs
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintNonpepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ..................{ TUPLES                             }..................
    # Add beartype-specific PEP-noncompliant test type hints to this dictionary
    # global.
    data_module.HINTS_NONPEP_META.extend((
        # ................{ TUPLE UNION                        }................
        # Beartype-specific tuple unions (i.e., tuples containing one or more
        # isinstanceable classes).

        # Tuple union of one isinstanceable class.
        HintNonpepMetadata(
            hint=(str,),
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata('Pinioned coin tokens'),
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
        HintNonpepMetadata(
            hint=(int, str),
            piths_meta=(
                # Integer constant.
                HintPithSatisfiedMetadata(12),
                # String constant.
                HintPithSatisfiedMetadata('Smirk‐opined — openly'),
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
    ))

    # ..................{ VALIDATORS ~ is                    }..................
    # Beartype-specific validators defined as lambda functions.
    IsNonempty = Is[lambda text: bool(text)]

    # ..................{ FACTORIES                          }..................
    # For each "Annotated" type hint factory importable from a typing module...
    for Annotated in iter_typing_attrs('Annotated'):
        # ..................{ LOCALS ~ plugin                }..................
        # Local variables requiring an "Annotated" type hint factory
        # additionally exercising beartype's plugin API.

        class StringNonempty(str, BeartypeHintable):
            '''
            **Non-empty string** (i.e., :class:`str` subclass satisfying the
            :class:`BeartypeHintable` protocol by defining the
            :meth:`__beartype_hint__` class method to return a type hint
            constraining instances of this subclass to non-empty strings).
            '''

            @classmethod
            def __beartype_hint__(cls) -> object:
                '''
                Beartype type hint transform reducing to an annotated of this
                subclass validating instances of this subclass to be non-empty.
                '''

                # Munificent one-liner: I invoke thee!
                return Annotated[cls, IsNonempty]

        #FIXME: Uncomment after finalizing the "_plughintable" API, please.
        # # ................{ TUPLES                             }................
        # # Add PEP 593-specific test type hints to this tuple global.
        # data_module.HINTS_NONPEP_META.extend((
        #     # ..............{ ANNOTATED ~ beartype : is : plugin }..............
        #     # Note that beartype's plugin API straddles the fine line between
        #     # PEP-compliant and PEP-noncompliant type hints. Superficially, most
        #     # isinstanceable types are PEP-noncompliant and thus exercised in
        #     # unit tests via the "HintNonpepMetadata" dataclass. Semantically,
        #     # isinstanceable type satisfying the "BeartypeHintable" protocol
        #     # define __beartype_hint__() class methods returning PEP-compliant
        #     # type hints instead exercised in unit tests via the
        #     # "HintPepMetadata" dataclass. To avoid confusion, these types are:
        #     # Superficially accepted as PEP-noncompliant. Treating them instead
        #     # as PEP-compliant would be feasible but require non-trivial
        #     # replacement of these types with the type hints returned by their
        #     # __beartype_hint__() class methods. Doing so would also probably
        #     # break literally everything. Did we mention that?
        #
        #     # Isinstanceable type satisfying the "BeartypeHintable" protocol,
        #     # whose __beartype_hint__() class method returns an annotated of an
        #     # isinstanceable type annotated by one beartype-specific validator
        #     # defined as a lambda function.
        #     HintNonpepMetadata(
        #         hint=StringNonempty,
        #         piths_meta=(
        #             # String constant satisfying this validator.
        #             HintPithSatisfiedMetadata(
        #                 "Impell no pretty‐spoked fellahs’ prudently"),
        #             # Byte-string constant *NOT* an instance of the expected
        #             # type.
        #             HintPithUnsatisfiedMetadata(
        #                 pith=b'Impudent Roark-sparkful',
        #                 # Match that the exception message raised for this
        #                 # object embeds the code for this validator's lambda
        #                 # function.
        #                 exception_str_match_regexes=(
        #                     r'Is\[.*\bbool\(text\).*\]',),
        #             ),
        #             # Empty string constant violating this validator.
        #             HintPithUnsatisfiedMetadata(''),
        #         ),
        #     ),
        # ))
