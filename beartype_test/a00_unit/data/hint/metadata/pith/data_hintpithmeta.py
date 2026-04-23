#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Testing-specific **PEP-agnostic type hint metadata class hierarchy** (i.e.,
hierarchy of classes encapsulating sample type hints regardless of whether those
hints comply with PEP standards or not, instances of which are typically
contained in containers yielded by session-scoped fixtures defined by the
:mod:`beartype_test.a00_unit.data.hint.data_hintfixture` submodule).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.a00_unit.data.hint.metadata.pith.data_pithmeta import (
    PithSatisfiedMetadata,
    PithUnsatisfiedMetadata,
)
from beartype_test.a00_unit.data.hint.metadata.pith.data_hintmeta import (
    HintNonpepMetadata)
from contextlib import contextmanager

# ....................{ CLASSES ~ hint-pith                }....................
class HintPithMetadata(object):
    '''
    Dataclass encapsulating all relevant type hint- and pith-specific metadata
    iteratively yielded by each iteration of the
    :func:`beartype_test.a00_unit.data.hint.data_hintfixture.iter_hints_piths_meta`
    fixture generator.

    Attributes
    ----------
    hint_meta : HintNonpepMetadata
        Metadata describing the currently iterated type hint.
    pith_meta : PithSatisfiedMetadata
        Metadata describing this ``pith``.
    pith : object
        Object either satisfying or violating this type hint.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        hint_meta: HintNonpepMetadata,
        pith_meta: PithSatisfiedMetadata,
        pith: object,
    ) -> None:
        '''
        Initialize this dataclass.

        Parameters
        ----------
        hint_meta : HintNonpepMetadata
            Metadata describing the currently iterated type hint.
        pith_meta : Union[PithSatisfiedMetadata, PithUnsatisfiedMetadata]
            Metadata describing this ``pith``.
        pith : object
            Object either satisfying or violating this hint.
        '''
        assert isinstance(hint_meta, HintNonpepMetadata), (
            f'{repr(hint_meta)} not "HintNonpepMetadata" object.')
        assert isinstance(pith_meta, PithSatisfiedMetadata), (
            f'{repr(pith_meta)} not "PithSatisfiedMetadata" object.')

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

    # ..................{ CHECKERS                           }..................
    @contextmanager
    def beartyped_func_checking(
        self, beartyped_func: 'collections.abc.Callable[[object], object]',
    ) -> 'collections.abc.Iterable':
        '''
        Context manager asserting that the passed
        :func:`beartype.beartype`-decorated type-checking wrapper function
        constrained to trivially accept an arbitrary object and return that same
        object such that both that parameter and return are annotated by the
        type hint encapsulated by this metadata type-checks as expected when
        passed the pith encapsulated by this metadata.

        This context manager expects the caller to explicitly call this same
        function in the body of this context manager. Why? Lexical scope.
        Although awkward, this approach trivially enables callers to control the
        scope under which this function is called (e.g., to validate that
        :pep:`484`-compliant stringified relative type hints are resolved as
        expected against some previously undefined type hint confined to this
        same scope).

        Parameters
        ----------
        beartyped_func : Callable[[object], object]
            :func:`beartype.beartype`-decorated function to be tested.
        '''

        # ....................{ IMPORTS                    }....................
        # Defer method-specific imports.
        from beartype.roar import BeartypeCallHintViolation
        from beartype._util.text.utiltextansi import strip_str_ansi
        from beartype_test._util.error.pyterrraise import raises_uncached
        from re import search

        # ....................{ LOCALS                     }....................
        # Object to type-check against this hint.
        pith = self.pith

        # Metadata describing this pith.
        pith_meta = self.pith_meta
        # print(f'Type-checking PEP type hint {repr(hint_meta.hint)}...')

        # ....................{ VIOLATE                    }....................
        # If this pith violates this hint...
        if isinstance(pith_meta, PithUnsatisfiedMetadata):
            # ....................{ EXCEPTION ~ type       }....................
            # Assert this wrapper function raises the expected exception when
            # type-checking this pith against this hint.
            with raises_uncached(BeartypeCallHintViolation) as exception_info:
                yield

            # Exception captured by the prior call to this wrapper function.
            exception = exception_info.value

            # Exception type localized for debuggability. Sadly, the
            # pytest.ExceptionInfo.__repr__() dunder method fails to usefully
            # describe its exception metadata.
            exception_type = exception_info.type

            # Assert this exception metadata describes the expected exception
            # as a sanity check against upstream pytest issues and/or issues
            # with our raises_uncached() context manager.
            assert issubclass(exception_type, BeartypeCallHintViolation)

            # Assert this exception to be public rather than private. The
            # @beartype decorator should *NEVER* raise a private exception.
            assert exception_type.__name__[0] != '_'

            # ....................{ EXCEPTION ~ culprits   }....................
            # Tuple of the culprits responsible for this exception, localized to
            # avoid inefficiently recomputing these culprits on each access.
            exception_culprits = exception.culprits

            # Assert that this tuple both exists *AND* is non-empty.
            assert isinstance(exception_culprits, tuple)
            assert exception_culprits

            # First culprit, which *SHOULD* be either:
            # * If this pith can be weakly referenced, this pith.
            # * Else, this pith *CANNOT* be weakly referenced. In this case,
            #   fallback to the truncated representation of this pith.
            culprit_pith = exception_culprits[0]

            # If the first culprit is a string...
            if isinstance(culprit_pith, str):
                # Assert that this string is non-empty.
                assert culprit_pith
            # Else, the first culprit is *NOT* a string. In this case...
            else:
                # Assert that the first culprit is this pith.
                assert culprit_pith is pith

                # If two or more culprits were responsible...
                if len(exception_culprits) >= 2:
                    # For each culprit following the first...
                    for culprit_nonpith in exception_culprits[1:]:
                        # Assert that this subsequent culprit is *NOT* the pith.
                        assert culprit_nonpith is not pith

            # ....................{ EXCEPTION ~ message    }....................
            # Exception message raised by this wrapper function.
            exception_str = strip_str_ansi(str(exception))
            # print('exception message: {}'.format(exception_str))

            # Assert this exception message is prefixed by a substring
            # identifying the decorated callable with a human-readable label.
            assert exception_str.startswith('Function ')

            # Assert that iterables of uncompiled regular expression expected
            # to match and *NOT* match this message are *NOT* strings, as
            # commonly occurs when accidentally omitting a trailing comma in
            # tuples containing only one string: e.g.,
            # * "('This is a tuple, yo.',)" is a 1-tuple containing one string.
            # * "('This is a string, bro.')" is a string *NOT* contained in a
            #   1-tuple.
            assert not isinstance(
                pith_meta.exception_str_match_regexes, str)
            assert not isinstance(
                pith_meta.exception_str_not_match_regexes, str)

            # For each uncompiled regular expression expected to match this
            # message, assert this expression actually does so.
            #
            # Note that the re.search() rather than re.match() function is
            # called. The latter is rooted at the start of the string and thus
            # *ONLY* matches prefixes, while the former is *NOT* rooted at any
            # string position and thus matches arbitrary substrings as desired.
            for exception_str_match_regex in (
                pith_meta.exception_str_match_regexes):
                assert search(
                    exception_str_match_regex, exception_str) is not None

            # For each uncompiled regular expression expected to *NOT* match
            # this message, assert this expression actually does so.
            for exception_str_not_match_regex in (
                pith_meta.exception_str_not_match_regexes):
                assert search(
                    exception_str_not_match_regex, exception_str) is None
        # ....................{ SATISFY                    }....................
        # Else, this pith satisfies this hint. In this case...
        else:
            # Assert this wrapper function successfully type-checks this pith
            # against this hint *WITHOUT* modifying this pith.
            yield
