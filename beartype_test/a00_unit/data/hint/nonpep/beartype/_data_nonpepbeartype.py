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

# ....................{ IMPORTS                            }....................
from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
    HintNonpepMetadata,
    HintPithSatisfiedMetadata,
    HintPithUnsatisfiedMetadata,
)

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

    #FIXME: Shift into a PEP-compliant beartype-specific submodule, please.
    #Doing so will enable us to detect that third-party beartype plugins are
    #correctly detected with respect to signs and so on.

    # # ..................{ IMPORTS                            }..................
    # # Defer data-specific imports.
    # from beartype.plug._plugproto import BeartypeHintable
    # from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    #
    # # If the active Python interpreter targets Python >= 3.9 and thus defines
    # # the PEP 593-compliant "typing.Annotated" type hint factory...
    # if IS_PYTHON_AT_LEAST_3_9:
    #     # Defer version-specific imports.
    #     from beartype.typing import Annotated
    #     from beartype.vale import Is
    #
    #     # .....................{ CLASSES                   }....................
    #     class StringNonempty(str, BeartypeHintable):
    #         '''
    #         **Non-empty string** (i.e., :class:`str` subclass satisfying the
    #         :class:`BeartypeHintable` protocol by defining the
    #         :meth:`__beartype_hint__` class method to return a type hint
    #         constraining instances of this subclass to non-empty strings).
    #         '''
    #
    #         @classmethod
    #         def __beartype_hint__(cls) -> object:
    #             '''
    #             Arbitrary beartype type hint transform reducing to an arbitrary
    #             PEP-compliant type hint.
    #             '''
    #
    #             # Magnificent one-liner: we invoke thee!
    #             return Annotated[StringNonempty, Is[lambda text: bool(text)]]

    # ..................{ TUPLES                             }..................
    # Add beartype-specific PEP-noncompliant test type hints to this dictionary
    # global.
    data_module.HINTS_NONPEP_META.extend((
        # ................{ PLUGIN                             }................
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
