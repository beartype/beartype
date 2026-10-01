#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant PEP-noncompliant type hint test data.

:pep:`695`-compliant type hints *mostly* indistinguishable from
PEP-noncompliant type hints include:

* :func:`typing.TypeAliasType`, the C-based type of all :pep:`695`-compliant
  type aliases and itself a valid type hint.
'''

# ....................{ FIXTURES                           }....................
def hints_nonpep695_meta() -> (
    'list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintNonpepMetadata]'):
    '''
    List of :pep:`695`-sorta-compliant **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintNonpepMetadata`
    instances describing test-specific :pep:`695`-sorta-compliant sample type
    hints with metadata generically leveraged by various PEP-agnostic unit
    tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from beartype_test.a00_unit.data.hint.cls.pith.data_clshint import (
        HintNonpepMetadata)
    from beartype_test.a00_unit.data.hint.cls.pith.data_clspith import (
        PithSatisfiedMetadata,
        PithUnsatisfiedMetadata,
    )

    # List of all PEP-noncompliant type hint metadata to be returned.
    hints_piths_nonpep_meta = []

    # If the active Python interpreter targets Python < 3.12, this interpreter
    # fails to support PEP 695. In this case, return the empty list.
    if not IS_PYTHON_AT_LEAST_3_12:
        return hints_piths_nonpep_meta
    # Else, the active Python interpreter targets Python >= 3.12 and thus
    # supports PEP 695.

    # ..................{ LISTS                              }..................
    # Defer version-specific imports.
    from beartype._util.api.standard.utiltyping import (
        import_module_attr_or_none)
    from beartype_test.a00_unit.data.pep.pep695.data_pep695hint import (
        AliasSimple)
    from typing import TypeAliasType

    # Add PEP 695-specific (albeit technically PEP-noncompliant from the
    # beartype perspective) test type hints to this list.
    hints_piths_nonpep_meta.extend((
        HintNonpepMetadata(
            hint=TypeAliasType,
            piths_meta=(
                # Arbitrary PEP 695-compliant type alias.
                PithSatisfiedMetadata(AliasSimple),
                # PithSatisfiedMetadata(AliasSimple),
                # String constant.
                PithUnsatisfiedMetadata(
                    pith='And diamond-paved lustrous long arcades,',
                    # Match that the exception message raised for this pith
                    # contains...
                    exception_str_match_regexes=(
                        # The type *NOT* satisfied by this object.
                        r'\btyping\.TypeAliasType\b',
                    ),
                    # Match that the exception message raised for this pith
                    # does *NOT* contain...
                    exception_str_not_match_regexes=(
                        # A newline.
                        r'\n',
                        # A bullet delimiter.
                        r'\*',
                    ),
                ),
            ),
        ),
    ))

    # Third-party "typing_extensions.TypeAliasType" type if that type is
    # importable *OR* "None" otherwise.
    typing_extensions_TypeAliasType = import_module_attr_or_none(
        attr_name='typing_extensions.TypeAliasType')

    # If...
    if (
        # That type is importable *AND*...
        typing_extensions_TypeAliasType is not None and
        # That type is *NOT* simply a trivial alias of "typing.TypeAliasType"...
        typing_extensions_TypeAliasType is not TypeAliasType
    ):
        # Arbitrary PEP 695-compliant type alias manually constructed via
        # standard type instantiation syntax rather than sugary "type" syntax.
        typing_extensions_alias_simple = typing_extensions_TypeAliasType(
            'alias_simple', int | list[str])

        # Add PEP 695-specific (albeit technically PEP-noncompliant from the
        # beartype perspective) test type hints to this list.
        hints_piths_nonpep_meta.extend((
            HintNonpepMetadata(
                hint=typing_extensions_TypeAliasType,
                piths_meta=(
                    # Arbitrary PEP 695-compliant type alias.
                    PithSatisfiedMetadata(typing_extensions_alias_simple),
                    # PithSatisfiedMetadata(AliasSimple),
                    # String constant.
                    PithUnsatisfiedMetadata(
                        pith='With the green world they live in; and clear rills',
                        # Match that the exception message raised for this pith
                        # contains...
                        exception_str_match_regexes=(
                            # The type *NOT* satisfied by this object.
                            r'\btyping_extensions\.TypeAliasType\b',
                        ),
                        # Match that the exception message raised for this pith
                        # does *NOT* contain...
                        exception_str_not_match_regexes=(
                            # A newline.
                            r'\n',
                            # A bullet delimiter.
                            r'\*',
                        ),
                    ),
                ),
            ),
        ))

    # # For each unsubscripted "typing.TypeAliasType" type of *ALL* PEP
    # # 695-compliant type aliases...
    # #
    # # Note that this type is a valid type and thus a valid hint, despite
    # # defining a PEP-noncompliant "__parameters__" dunder attribute.
    # for TypeAliasType in get_typing_attrs('TypeAliasType'):
    #     #FIXME: *LOL*. Doesn't work at the moment. In all likelihood, @beartype
    #     #currently fails to support the manual construction approach. *sigh*
    #     # # Arbitrary PEP 695-compliant type alias manually constructed via
    #     # # standard type instantiation syntax rather than sugary "type" syntax.
    #     # alias_simple = HintPep695TypeAlias('alias_simple', int | list[str])


    # ..................{ RETURN                             }..................
    # Return this list of all PEP-noncompliant type hint metadata.
    return hints_piths_nonpep_meta
