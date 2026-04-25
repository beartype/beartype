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
    def warns_warnings_expected(self) -> 'collections.abc.Iterable':
        '''
        Context manager asserting that an arbitrary :mod:`beartype`
        **type-checker** (i.e., either a call to the
        :func:`beartype.door.die_if_unbearable` or
        :func:`beartype.door.is_bearable` statement-level type-checkers *or* a
        decoration of an arbitrary callable or type by the
        :func:`beartype.beartype` decorator) performed by the caller in the body
        of this context manager either does or does not issue the expected
        warnings.

        Caveats
        -------
        This context manager should be called *only* from warnings-specific
        tests intentionally isolated from all other warnings-agnostic tests.
        Testing that a type-checker issues the expected warnings when confronted
        with a given type hint in a robust, portable, and idempotent manner
        necessarily requires clearing *all* :mod:`beartype`-specific caches on
        each test iteration. Clearing those caches effectively undoes *all*
        memoization previously performed by that type-checker, preventing the
        parent test from testing that that memoization behaves as expected.
        Testing that memoization behaves as expected is critical, however!
        Warnings-agnostic tests are thus implicitly responsible for testing that
        memoization behaves as expected, which then precludes those tests from
        also clearing caches and thus testing warnings. QA: it do be like that.
        '''

        # ..................{ IMPORTS                            }..................
        # Defer test-specific imports.
        from beartype._util.cache.utilcacheclear import clear_caches
        from beartype_test._util.error.pyterrwarn import warns_uncached
        from warnings import (
            catch_warnings,
            simplefilter,
        )

        # ....................{ SETUP                      }....................
        # Force pytest to temporarily allow deprecation warnings to be caught by
        # the warns() context manager for the duration of this test. By default,
        # pytest simply "passes through" all deprecation warnings for subsequent
        # reporting if tests otherwise successfully pass. Deprecation warnings
        # include:
        # * "DeprecationWarning".
        # * "FutureWarning".
        # * "PendingDeprecationWarning".
        simplefilter('always')

        # Preserve test idempotence by explicitly clearing *ALL* internal caches
        # leveraged throughout the main @beartype codebase. Doing so effectively
        # resets this codebase back to its initial state.
        clear_caches()

        # ....................{ LOCALS                     }....................
        # Type of warning expected to be issued by any type-checker when
        # confronted with this hint if any *OR* "None" otherwise.
        warning_type = self.hint_meta.warning_type

        # ....................{ ASSERTS                    }....................
        # If the type-checker performed by the caller in the body of this
        # context manager is expected to issue one or more warnings when
        # confronted with this hint...
        if warning_type is not None:
            # Assert that that type-checker issues one or more warnings of the
            # expected type when type-checking this pith against this hint.
            with warns_uncached(warning_type) as warning_info:
                yield

            #FIXME: Uncomment *AFTER* we properly define the "warnings_len"
            #instance variable for all relevant test-specific type hints. *sigh*
            # # Assert that this tester issued the expected number of warnings.
            # assert len(warning_info) == hint_meta.warnings_len
        # Else, that type-checker is expected to issue *NO* warnings when
        # confronted by this hint. In this case...
        else:
            # With a context manager catching *ALL* unexpected warnings issued
            # by that type-checker, defer to that type-checker.
            with catch_warnings(record=True) as warning_info:
                yield

            # Assert that *NO* warnings were issued by that type-checker above.
            assert not warning_info


    @contextmanager
    def raises_violation_expected_if_any(self) -> 'collections.abc.Iterable':
        '''
        Context manager asserting that an arbitrary :mod:`beartype`
        **violation-raising type-checking call** (i.e., call to either the
        :func:`beartype.door.die_if_unbearable` statement-level type-checker or
        a :func:`beartype.beartype`-decorated type-checking wrapper function)
        performed by the caller in the body of this context manager either does
        or does not raise the expected :mod:`beartype` **violation** (i.e.,
        :exc:`beartype.roar.BeartypeCallHintViolation` exception).

        This context manager requires the caller to explicitly perform this call
        in the body of this context manager. Why? Lexical scope. While awkward,
        this approach trivially enables callers to control the scope under which
        this call is performed (e.g., to validate that :pep:`484`-compliant
        stringified relative type hints are resolved as expected against some
        previously undefined type hint confined to this same scope).

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

        # ....................{ SATISFY                    }....................
        # If this pith satisfies this hint, defer to caller logic asserting that
        # the type-checking call performed by the caller successfully
        # type-checks this pith against this hint *WITHOUT* raising exceptions.
        if not isinstance(pith_meta, PithUnsatisfiedMetadata):
            yield
        # ....................{ VIOLATE                    }....................
        # Else, this pith violates this hint. In this case...
        else:
            # ....................{ EXCEPTION ~ type       }....................
            # Assert that the type-checking call performed by the caller
            # raises a violation of the expected type when type-checking this
            # pith against this hint.
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
