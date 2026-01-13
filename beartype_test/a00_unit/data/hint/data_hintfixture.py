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
def hints_ignorable(
    hints_pep_ignorable_shallow,
    hints_pep_ignorable_deep,
) -> frozenset:
    '''
    Session-scoped fixture yielding a frozen set of **ignorable PEP-agnostic
    type hints,** including both PEP-compliant *and* -noncompliant and shallowly
    *and* deeply ignorable type hints.

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

# ....................{ FIXTURES ~ hints : meta            }....................
@fixture(scope='session')
def hints_meta(hints_pep_meta, hints_nonpep_meta) -> (
    'tuple[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintNonpepMetadata]'):
    '''
    Session-scoped fixture yielding a tuple of **PEP-agnostic type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintNonpepMetadata`
    instances, each describing a sample type hint exercising an edge case in the
    :mod:`beartype` codebase -- including both PEP-compliant and -noncompliant
    type hints).

    Parameters
    ----------
    hints_pep_meta : tuple[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPepMetadata]
        Tuple of PEP-compliant type hint metadata describing PEP-compliant type
        hints exercising edge cases in the :mod:`beartype` codebase.
    hints_nonpep_meta : Tuple[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintNonpepMetadata]
        Tuple of PEP-noncompliant type hint metadata describing PEP-noncompliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # One world. One-liner. Let's get together and code alright.
    yield hints_pep_meta + hints_nonpep_meta


@fixture(scope='session')
def hints_reduction_meta() -> (
    'tuple[beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta.HintReductionABC]'):
    '''
    Session-scoped fixture yielding a tuple of **PEP-agnostic type hint
    reduction metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta.HintReductionABC`
    instances, each describing a sample type hint exercising an edge case with
    respect to the :func:`beartype._check.convert.reduce.redmain.reduce_hint`
    function -- including both PEP-compliant and -noncompliant type hints).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype_test.a00_unit.data.hint.metadata.data_hintreducemeta import (
        HintReductionABC)
    from beartype_test._util.kind.pytkindmake import make_container_from_funcs

    # ..................{ LOCALS                             }..................
    # List of all type hint reduction metadata to be returned, iteratively
    # defined by dynamically importing and calling each factory function listed
    # below and adding the items of the container created and returned by that
    # function to this list.
    _hints_reduction_meta = make_container_from_funcs((
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep484.hints_pep484_reduction_meta',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep557.hints_pep557_reduction_meta',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep593.hints_pep593_reduction_meta',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep646.hints_pep646_reduction_meta',
    ))

    # ..................{ YIELD                              }..................
    # Assert this list contains *ONLY* instances of the expected dataclass.
    assert (
        isinstance(hint_reduction_meta, HintReductionABC)
        for hint_reduction_meta in _hints_reduction_meta
    ), (
        f'{repr(_hints_reduction_meta)} not '
        f'iterable of "HintReductionABC" instances.'
    )

    # Yield a tuple coerced from this list.
    yield tuple(_hints_reduction_meta)


@fixture(scope='session')
def iter_hints_piths_meta(hints_meta) -> (
    'collections.abc.Callable[[], collections.abc.Iterable[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPithMetadata]]'):
    '''
    Session-scoped fixture yielding a **PEP-agnostic type hint-pith metadata
    generator** (i.e., factory function creating and returning a generator
    iteratively yielding
    :class:`beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPithMetadata`
    instances, each describing a sample type hint exercising an edge case in the
    :mod:`beartype` codebase paired with a related object either satisfying or
    violating this hint -- including both PEP-compliant and -noncompliant type
    hints).

    Caveats
    -------
    This fixture *cannot* be directly iterated. Instead, this fixture must be
    first called and then iterated by callers. Why? Because
    :mod:`pytest.fixture`. By design, pytest ignores all ``yield`` statements in
    a fixture except the first. Ergo, the only means of defining a fixture
    generator is to define a fixture returning a generator closure. See also
    `this relevant StackOverflow answer <answer_>`__.

    .. _answer:
       https://stackoverflow.com/a/66397211/2809027

    Parameters
    ----------
    hints_meta : List[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintNonpepMetadata]
        List of PEP-agnostic type hint metadata describing sample PEP-agnostic
        type hints exercising edge cases in the :mod:`beartype` codebase.

    Yields
    ------
    collections.abc.Callable[[], collections.abc.Iterable[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPithMetadata]]
        PEP-agnostic type hint-pith metadata generator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.utilobject import is_object_context_manager
    from beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta import (
        HintPithMetadata,
        PithSatisfiedMetadata,
        PithUnsatisfiedMetadata,
    )
    from beartype_test._util.pytcontext import noop_context_manager

    # Tuple of two arbitrary values used to trivially iterate twice below.
    RANGE_2 = (None, None,)

    # ....................{ CLOSURE                        }....................
    def hints_piths_meta() -> 'Iterable[HintPithMetadata]':
        '''
        **PEP-agnostic type hint-pith metadata generator** (i.e., factory
        function creating and returning a generator iteratively yielding
        :class:`.HintPithMetadata` instances, each describing a sample type hint
        exercising an edge case in the :mod:`beartype` codebase paired with a
        related object either satisfying or violating this hint -- including
        both PEP-compliant and -noncompliant type hints).
        '''

        # For each predefined type hint and associated metadata...
        for hint_meta in hints_meta:
            # print(f'Type-checking type hint {repr(hint_meta.hint)}...')

            # If this hint is currently unsupported, continue to the next.
            if not hint_meta.is_supported:
                continue
            # Else, this hint is currently supported.

            # Repeat the following logic twice. Why? To exercise memoization
            # across repeated @beartype decorations on different callables
            # annotated by the same hints.
            for _ in RANGE_2:
                # For each pith either satisfying or violating this hint...
                for pith_meta in hint_meta.piths_meta:
                    # Assert this metadata is an instance of the desired dataclass.
                    assert isinstance(pith_meta, PithSatisfiedMetadata)

                    # Pith to be type-checked against this hint, defined as...
                    pith = (
                        # If this pith is actually a pith factory (i.e., callable
                        # accepting *NO* parameters and dynamically creating and
                        # returning the value to be used as the desired pith), call
                        # this factory and localize its return value.
                        pith_meta.pith()
                        if pith_meta.is_pith_factory else
                        # Else, localize this pith as is.
                        pith_meta.pith
                    )
                    # print(f'Type-checking PEP type hint {repr(hint_meta.hint)} against {repr(pith)}...')

                    # Context manager under which to validate this pith against
                    # this hint, defined as either...
                    pith_context_manager = (
                        # This pith itself if both...
                        pith
                        if (
                            # This pith is a context manager *AND*...
                            is_object_context_manager(pith) and
                            # This pith should be safely opened and closed as a
                            # context rather than preserved as a context manager...
                            not pith_meta.is_context_manager
                        ) else
                        # Else, the noop context manager yielding this pith.
                        noop_context_manager(pith)
                    )

                    # With this pith safely opened and closed as a context...
                    with pith_context_manager as pith_context:
                        # If this pith does *NOT* satisfy this hint...
                        if isinstance(pith_meta, PithUnsatisfiedMetadata):
                            # Assert that iterables of uncompiled regular
                            # expression expected to match and *NOT* match this
                            # message are *NOT* strings, as commonly occurs when
                            # accidentally omitting a trailing comma in tuples
                            # containing only one string: e.g.,
                            # * "('This is a tuple, yo.',)" is a 1-tuple
                            #   containing one string.
                            # * "('This is a string, bro.')" is a string *NOT*
                            #   contained in a 1-tuple.
                            assert not isinstance(
                                pith_meta.exception_str_match_regexes, str)
                            assert not isinstance(
                                pith_meta.exception_str_not_match_regexes, str)

                        # Yield this metadata to the caller.
                        yield HintPithMetadata(
                            hint_meta=hint_meta,
                            pith_meta=pith_meta,
                            pith=pith_context,
                        )

    # ....................{ YIELD                          }....................
    # Yield this closure.
    yield hints_piths_meta

# ....................{ FIXTURES ~ hints : non-pep         }....................
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

    # Frozen set of tuples of PEP-compliant type hints. Although tuples of
    # PEP-noncompliant type hints are themselves valid PEP-noncompliant type
    # hints supported by @beartype, tuples of PEP-compliant type hints are *NOT*
    # and thus remain unsupported.
    hints_pep_tuple = frozenset((
        # Tuple containing this PEP-compliant type hint...
        (int, hint_pep_hashable, NoneType,)
        # For each hashable PEP-compliant type hint...
        for hint_pep_hashable in hints_pep_hashable
        # That is neither:
        # * An isinstanceable class.
        # * A string-based forward reference.
        #
        # Both are unique edge cases supported as both PEP 484-compliant
        # outside tuples *AND* beartype-specific inside tuples. Including
        # these hints here would erroneously cause tests to treat tuples
        # containing these hints as *NOT* tuple type hints.
        if not isinstance(hint_pep_hashable, (str, type))
    ))

    # Yield a frozen set of...
    yield frozenset((
        # Frozen set of tuples of PEP-compliant type hints.
        hints_pep_tuple |
        # Frozen set of hashable PEP-compliant non-class type hints.
        hints_pep_hashable |
        # Frozen set of hashable objects invalid as type hints (e.g., scalars).
        NOT_HINTS_HASHABLE
    ))
