#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
:mod:`pytest` **PEP-agnostic type hint utilities.**
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ CLASSES                            }....................
class HintPithMetadata(object):
    '''
    Dataclass encapsulating all relevant type hint- and pith-specific metadata
    iteratively yielded by each iteration of the :func:`.iter_hints_piths_meta`
    generator.

    Attributes
    ----------
    hint_meta : HintNonpepMetadata
        Metadata describing the currently iterated type hint.
    pith_meta : HintPithSatisfiedMetadata
        Metadata describing this ``pith``.
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
            Metadata describing this ``pith``.
        pith : object
            Object either satisfying or violating this hint.
        '''

        # Classify all passed parameters. For simplicity, avoid validating
        # these parameters; we simply *CANNOT* be bothered at the moment.
        self.hint_meta = hint_meta
        self.pith_meta = pith_meta
        self.pith = pith

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    hint_meta={repr(self.hint_meta)},',
            f'    pith_meta={repr(self.pith_meta)},',
            f'    pith={repr(self.pith)},',
            f')',
        ))

# ....................{ ITERATORS                          }....................
@fixture(scope='session')
def iter_hints_piths_meta(hints_meta) -> (
    'Callable[[], Iterable[HintPithMetadata]]'):
    '''
    Session-scoped fixture yielding a **PEP-agnostic type hint-pith metadata
    generator** (i.e., factory function creating and returning a generator
    iteratively yielding :class:`.HintPithMetadata` instances, each describing a
    sample type hint exercising an edge case in the :mod:`beartype` codebase
    paired with a related object either satisfying or violating this hint --
    including both PEP-compliant and -noncompliant type hints).

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
    hints_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintNonpepMetadata]
        List of PEP-agnostic type hint metadata describing sample PEP-agnostic
        type hints exercising edge cases in the :mod:`beartype` codebase.

    Yields
    ------
    Callable[[], Iterable[HintPithMetadata]]
        PEP-agnostic type hint-pith metadata generator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.utilobject import is_object_context_manager
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from beartype_test._util.pytcontext import noop_context_manager

    # Tuple of two arbitrary values used to trivially iterate twice below.
    RANGE_2 = (None, None)

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

    # ....................{ YIELD                          }....................
    # Yield this closure.
    yield hints_piths_meta
