#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
:mod:`pytest` **PEP-agnostic type hint utilities.**
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ CLASSES                            }....................
class HintPithMetadata(object):
    '''
    Dataclass encapsulating all relevant type hint- and pith-specific metadata
    iteratively yielded by each iteration of the :func:`iter_hints_piths_meta`
    generator.

    Attributes
    ----------
    hint_meta : HintNonpepMetadata
        Metadata describing the currently iterated type hint.
    pith_meta : HintPithSatisfiedMetadata
        Metadata describing this pith.
    pith : object
        Object either satisfying or violating this hint.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        hint_meta: 'HintNonpepMetadata',
        pith_meta: 'HintPithSatisfiedMetadata',
        pith: object,
    ) -> None:
        '''
        Initialize this dataclass.

        Parameters
        ----------
        hint_meta : HintNonpepMetadata
            Metadata describing the currently iterated type hint.
        pith_meta : Union[HintPithSatisfiedMetadata, HintPithUnsatisfiedMetadata]
            Metadata describing this pith.
        pith : object
            Object either satisfying or violating this hint.
        '''

        # Classify all passed parameters. For simplicity, avoid validating
        # these parameters; we simply *CANNOT* be bothered at the moment.
        self.hint_meta = hint_meta
        self.pith_meta = pith_meta
        self.pith = pith

# ....................{ ITERATORS                          }....................
def iter_hints_piths_meta() -> 'Generator[HintPithMetadata]':
    '''
    Generator iteratively yielding test-specific type hints with metadata
    leveraged by various testing scenarios -- including both PEP-compliant and
    -noncompliant type hints.

    Yields
    ----------
    HintPithMetadata
        Metadata describing the currently iterated hint.
    '''

    # Defer test-specific imports.
    from beartype._util.utilobject import is_object_context_manager
    from beartype_test.a00_unit.data.hint.data_hint import HINTS_META
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from beartype_test._util.pytcontext import noop_context_manager

    # Tuple of two arbitrary values used to trivially iterate twice below.
    RANGE_2 = (None, None)

    # For each predefined PEP-compliant type hint and associated metadata...
    for hint_meta in HINTS_META:
        # print(f'Type-checking PEP type hint {repr(hint_meta.hint)}...')

        # If this hint is currently unsupported, continue to the next.
        if not hint_meta.is_supported:
            continue
        # Else, this hint is currently supported.

        # Repeat the following logic twice. Why? To exercise memoization across
        # repeated @beartype decorations on different callables annotated by
        # the same hints.
        for _ in RANGE_2:
            # For each pith either satisfying or violating this hint...
            for pith_meta in hint_meta.piths_meta:
                # Assert this metadata is an instance of the desired dataclass.
                assert isinstance(pith_meta, HintPithSatisfiedMetadata)

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
                    if isinstance(pith_meta, HintPithUnsatisfiedMetadata):
                        # Assert that iterables of uncompiled regular
                        # expression expected to match and *NOT* match this
                        # message are *NOT* strings, as commonly occurs when
                        # accidentally omitting a trailing comma in tuples
                        # containing only one string: e.g.,
                        # * "('This is a tuple, yo.',)" is a 1-tuple containing
                        #   one string.
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
