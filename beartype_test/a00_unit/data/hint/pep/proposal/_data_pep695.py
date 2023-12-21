#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant **type hint test data.**
'''

# ....................{ FIXTURES                           }....................
def hints_pep695_meta() -> 'List[HintPepMetadata]':
    '''
    Session-scoped fixture returning a list of :pep:`695`-compliant **type hint
    metadata** (i.e.,
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
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignList,
        HintSignPep695TypeAlias,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )

    # ..................{ LOCALS                             }..................
    # Simple type alias whose value is a standard type hint containing *NO*
    # syntax or semantics unique to PEP 695-compliant type aliases (e.g., *NO*
    # forward references, recursion, or type variables).
    type AliasSimple = int | list[str]

    #FIXME: Test us up tomorrow, please.
    # type alias_generic[T] = list[T] | set[T]

    # ..................{ TUPLES                             }..................
    # Add PEP 604-specific test type hints to this tuple global.
    hints_pep_meta.extend((
        # ................{ TYPE ALIAS                         }................
        # Simple type alias whose value is a standard type hint containing *NO*
        # syntax or semantics unique to PEP 695-compliant type aliases (e.g.,
        # *NO* forward references, recursion, or type variables).
        HintPepMetadata(
            hint=AliasSimple,
            pep_sign=HintSignPep695TypeAlias,
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
    ))

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta


#FIXME: Actually call this list factory *AFTER* implementing the appropriate PEP
#695-specific ignorer, please.
def hints_pep695_ignorable_deep() -> list:
    '''
    List of :pep:`695`-compliant **deeply ignorable type hints** (i.e.,
    ignorable only on the non-trivial basis of their nested child type hints).
    '''

    # ..................{ IMPORTS                            }..................
    from beartype.typing import Any
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12

    # If the active Python interpreter targets Python < 3.12, this interpreter
    # fails to support PEP 695. In this case, return the empty list.
    if not IS_PYTHON_AT_LEAST_3_12:
        return []
    # Else, this interpreter supports PEP 695.

    # ..................{ LOCALS                             }..................
    # Type alias whose value is shallowly ignorable. Note that, although this
    # value is shallowly ignorable, deciding whether or not a type alias is
    # ignorable requires deep inspection into the value of that alias. Ergo,
    # *ALL* type aliases that are ignorable are only deeply ignorable; there
    # exist *NO* shallowly ignorable type aliases.
    type AliasIgnorableShallow = object

    # Type alias whose value is deeply ignorable.
    type AliasIgnorableDeep = float | str | Any

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific deeply ignorable type hints.
    return [
        AliasIgnorableShallow,
        AliasIgnorableDeep,
    ]
