#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **type hint fixtures.**

This submodule defines session-scoped fixtures yielding tuples of various
categories of related type hints. The :func:`beartype_test.a00_unit.conftest`
submodule imports and exposes these fixtures to *all* unit tests, which may then
reference these fixtures in the standard :mod:`pytest` way (i.e., as parameters
of the same names).
'''

# ....................{ IMPORTS                            }....................
from pytest import fixture

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def hints_meta(hints_pep_meta, hints_nonpep_meta) -> (
    'Tuple[HintNonpepMetadata]'):
    '''
    Session-scoped fixture yielding a tuple of **PEP-agnostic type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintNonpepMetadata`
    instances, each describing a sample type hint exercising an edge case in the
    :mod:`beartype` codebase -- including both PEP-compliant and -noncompliant
    type hints).

    Parameters
    ----------
    hints_pep_meta : Tuple[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        Tuple of PEP-compliant type hint metadata describing PEP-compliant type
        hints exercising edge cases in the :mod:`beartype` codebase.
    hints_nonpep_meta : Tuple[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintNonpepMetadata]
        Tuple of PEP-noncompliant type hint metadata describing PEP-noncompliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # One world. One-liner. Let's get together and code alright.
    yield hints_pep_meta + hints_nonpep_meta


@fixture(scope='session')
def hints_ignorable(
    hints_pep_ignorable_shallow,
    hints_pep_ignorable_deep,
) -> frozenset:
    '''
    Session-scoped fixture yielding a frozen set of **ignorable
    PEP-agnostic type hints,** including both PEP-compliant *and* -noncompliant
    and shallowly *and* deeply ignorable type hints.

    Parameters
    ----------
    hints_pep_ignorable_shallow : frozenset
        Frozen set of all shallowly ignorable PEP-compliant type hints.
    hints_pep_ignorable_deep : frozenset
        Frozen set of all deeply ignorable PEP-compliant type hints.
    '''

    # I code the one-liner, but I did not code the two-liner.
    yield (
        hints_pep_ignorable_shallow |
        hints_pep_ignorable_deep
    )

# ....................{ FIXTURES ~ not : sets              }....................
@fixture(scope='session')
def not_hints_nonpep(hints_pep_hashable) -> frozenset:
    '''
    Session-scoped fixture yielding a frozen set of various objects that are
    *not* PEP-noncompliant type hints exercising well-known edge cases.

    Parameters
    ----------
    hints_pep_hashable : frozenset
        Tuple of PEP-compliant type hint metadata describing PEP-compliant type
        hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer fixture-specific imports.
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_HASHABLE
    from beartype._cave._cavefast import NoneType

    # Yield a frozen set of...
    yield frozenset((
        # Set comprehension of tuples containing PEP-compliant type hints. Although
        # tuples containing PEP-noncompliant type hints are themselves valid
        # PEP-noncompliant type hints supported by @beartype, tuples containing
        # PEP-compliant type hints are invalid and thus unsupported.
        {
            # Tuple containing this PEP-compliant type hint...
            (int, hint_pep_hashable, NoneType,)
            # For each hashable PEP-compliant type hint...
            for hint_pep_hashable in hints_pep_hashable
            # That is neither:
            # * An isinstanceable class.
            # * A string-based forward reference.
            #
            # Both are unique edge cases supported as both PEP 484-compliant outside
            # tuples *AND* beartype-specific inside tuples. Including these hints
            # here would erroneously cause tests to treat tuples containing these
            # hints as *NOT* tuple type hints.
            if not isinstance(hint_pep_hashable, (str, type))
        } |
        # Set comprehension of hashable PEP-compliant non-class type hints.
        hints_pep_hashable |
        # Hashable objects invalid as type hints (e.g., scalars).
        NOT_HINTS_HASHABLE
    ))
