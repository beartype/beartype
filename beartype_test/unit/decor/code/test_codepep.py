#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP-compliant type hints** (i.e., :mod:`beartype`-agnostic annotations
generically compliant with annotation-centric PEPs).

See Also
----------
:mod:`beartype_test.unit.pep.p484`
    Subpackage specifically unit testing `PEP 484`_-compliant type hints.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.pyterror import raises_uncached
from collections import ChainMap
from re import search
from typing import Any, List, Union

# ....................{ TESTS                             }....................
def test_pep() -> None:
    '''
    Test usage of the :func:`beartype.beartype` decorator for a function call
    passed non-variadic positional and/or keyword parameters annotated with
    PEP-compliant type hints.

    This test **is the core test exercising end user decorator functionality.**
    Consequently, this test is mildly more involved than most unit tests and
    arguably qualifies as a functional rather than unit test. *Whatevah.*

    This test additionally attempts to avoid similar issues to a `prior issue
    <issue #5_>`__ of this decorator induced by repeated
    :func:`beartype.beartype` decorations of different callables annotated by
    one or more of the same PEP-compliant type hints.

    .. _issue #5:
       https://github.com/beartype/beartype/issues/5
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintPepException,
        BeartypeCallHintNonPepException,
    )
    from beartype._util.utilobject import is_object_context_manager
    from beartype_test.unit.data.hint.pep.data_hintpep import (
        HINT_PEP_TO_META,
        HINT_PEP_CLASSED_TO_META,
    )
    from beartype_test.unit.data.hint.pep.data_hintpepmeta import (
        PepHintPithSatisfiedMetadata,
        PepHintPithUnsatisfiedMetadata,
    )

    # Dictionary mapping various PEP-compliant type hints to "_PepHintMetadata"
    # instances detailing those hints with metadata applicable to testing
    # scenarios -- regardless of whether those hints are uniquely identified by
    # unsubscripted "typing" attributes or not.
    HINT_PEP_ALL_TO_META = ChainMap(HINT_PEP_TO_META, HINT_PEP_CLASSED_TO_META)

    # Tuple of two arbitrary values used to trivially iterate twice below.
    RANGE_2 = (None, None)

    # For each predefined PEP-compliant type hint and associated metadata...
    for hint_pep, hint_pep_meta in HINT_PEP_ALL_TO_META.items():
        # If this hint is currently unsupported, continue to the next.
        if not hint_pep_meta.is_supported:
            continue
        # Else, this hint is currently supported.

        # Repeat the following logic twice. Why? To exercise memoization across
        # repeated @beartype decorations on different callables annotated by
        # the same PEP hints.
        for _ in RANGE_2:
            # Dynamically define a callable both accepting a single parameter
            # and returning a value annotated by this hint whose implementation
            # trivially reduces to the identity function.
            @beartype
            def hint_peped(hint_peped_param: hint_pep) -> hint_pep:
                return hint_peped_param

            # Type of exception raised by this wrapper on type-check failures.
            exception_cls = (
                # If this hint is uniquely identified by an unsubscripted
                # "typing" attribute, this wrapper raises PEP-compliant
                # exceptions.
                BeartypeCallHintPepException
                if hint_pep_meta.pep_sign is not None else
                # Else, this hint reduces to a builtin type and is thus
                # detected as a PEP-noncompliant type hint. In this case, this
                # wrapper raises PEP-noncompliant exceptions.
                BeartypeCallHintNonPepException
            )

            # For each pith satisfying this hint...
            for pith_satisfied_meta in hint_pep_meta.piths_satisfied_meta:
                # Assert this metadata is an instance of the desired dataclass.
                assert isinstance(
                    pith_satisfied_meta, PepHintPithSatisfiedMetadata)
                # print('PEP-testing {!r} against {!r}...'.format(hint_pep, pith_satisfied))

                # Pith to be type-checked against this hint, defined as...
                pith = (
                    # If this pith is actually a pith factory (i.e., callable
                    # accepting *NO* parameters and dynamically creating and
                    # returning the value to be used as the desired pith), call
                    # this factory and localize its return value.
                    pith_satisfied_meta.pith()
                    if pith_satisfied_meta.is_pith_factory else
                    # Else, localize this pith as is.
                    pith_satisfied_meta.pith
                )

                # If...
                if (
                    # This pith is a context manager *AND*...
                    is_object_context_manager(pith) and
                    # This pith should be safely opened and closed as a
                    # context rather than preserved as a context manager...
                    not pith_satisfied_meta.is_context_manager
                # Then with this pith safely opened and closed as a context...
                ):
                    with pith as pith_context:
                        # Assert this wrapper function successfully type-checks
                        # this context against this hint *WITHOUT* modifying
                        # this context.
                        assert hint_peped(pith_context) is pith_context
                # Else, this object is *NOT* a context manager and thus safely
                # passable and returnable as is.
                else:
                    # Assert this wrapper function successfully type-checks
                    # this object against this hint *WITHOUT* modifying this
                    # object.
                    assert hint_peped(pith) is pith

            # For each pith *NOT* satisfying this hint...
            for pith_unsatisfied_meta in hint_pep_meta.piths_unsatisfied_meta:
                # Assert this metadata is an instance of the desired dataclass.
                assert isinstance(
                    pith_unsatisfied_meta, PepHintPithUnsatisfiedMetadata)

                # Assert that iterables of uncompiled regular expression
                # expected to match and *NOT* match this message are *NOT*
                # strings, as commonly occurs when accidentally omitting a
                # trailing comma in tuples containing only one string: e.g.,
                # * "('This is a tuple, yo.',)" is a 1-tuple containing one
                #   string.
                # * "('This is a string, bro.')" is a string *NOT* contained in
                #   a 1-tuple.
                assert not isinstance(
                    pith_unsatisfied_meta.exception_str_match_regexes, str)
                assert not isinstance(
                    pith_unsatisfied_meta.exception_str_not_match_regexes, str)

                # Assert this wrapper function raises the expected exception
                # when type-checking this pith against this hint.
                with raises_uncached(exception_cls) as exception_info:
                    hint_peped(pith_unsatisfied_meta.pith)

                # Exception message raised by this wrapper function.
                exception_str = str(exception_info.value)
                # print('exception message: {}'.format(exception_str))

                # For each uncompiled regular expression expected to match this
                # message, assert this expression actually does so.
                #
                # Note that the re.search() rather than re.match() function is
                # called. The latter is rooted at the start of the string and
                # thus *ONLY* matches prefixes, while the former is *NOT*
                # rooted at any string position and thus matches arbitrary
                # substrings as desired.
                for exception_str_match_regex in (
                    pith_unsatisfied_meta.exception_str_match_regexes):
                    assert search(
                        exception_str_match_regex, exception_str) is not None

                # For each uncompiled regular expression expected to *NOT*
                # match this message, assert this expression actually does so.
                for exception_str_not_match_regex in (
                    pith_unsatisfied_meta.exception_str_not_match_regexes):
                    assert search(
                        exception_str_not_match_regex, exception_str) is None

            # assert False is True

# ....................{ TESTS ~ pass : param : kind       }....................
def test_pep_param_kind_positional_or_keyword_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    function call passed non-variadic positional and/or keyword parameters
    annotated with `PEP 484`_-compliant type hints.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Defer heavyweight imports.
    from beartype import beartype

    # Decorated callable to be exercised.
    @beartype
    def special_plan(
        finally_gone: Union[str, List[Any]],
        finally_done: str,
    ) -> Union[bool, int, str]:
        return ''.join(finally_gone) + finally_done

    # Assert that calling this callable with both positional and keyword
    # arguments returns the expected return value.
    assert special_plan(
        ['When everyone ', 'you have ever loved ', 'is finally gone,'],
        finally_done=(
            'When everything you have ever wanted is finally done with,'),
    ) == (
        'When everyone you have ever loved is finally gone,' +
        'When everything you have ever wanted is finally done with,'
    )


def test_pep_param_kind_variadic_and_keyword_only_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    function call passed variadic positional parameters followed by a
    keyword-only parameter, all annotated with PEP-compliant type hints.
    '''

    # Defer heavyweight imports.
    from beartype import beartype

    # Decorated callable to be exercised.
    @beartype
    def shining_brainless_beacon(
        a_time_obscured: Union[bool, str],
        *all_of_your_nightmares: Union[float, str],
        your_special_plan: Union[int, str]
    ) -> Union[list, str]:
        return (
            a_time_obscured + '\n' +
            '\n'.join(all_of_your_nightmares) + '\n' +
            your_special_plan
        )

    # Assert that calling this callable with variadic positional parameters
    # followed by a keyword-only parameter returns the expected return value.
    assert shining_brainless_beacon(
        'When all of your nightmares are for a time obscured',
        'As by a shining brainless beacon',
        'Or a blinding eclipse of the many terrible shapes of this world,',
        'When you are calm and joyful',
        'And finally entirely alone,',
        'Then in a great new darkness',
        your_special_plan='You will finally execute your special plan',
    ) == '\n'.join((
        'When all of your nightmares are for a time obscured',
        'As by a shining brainless beacon',
        'Or a blinding eclipse of the many terrible shapes of this world,',
        'When you are calm and joyful',
        'And finally entirely alone,',
        'Then in a great new darkness',
        'You will finally execute your special plan',
    ))


def test_pep_param_kind_variadic_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for a
    function call passed variadic positional parameters annotated with
    PEP-compliant type hints.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintPepException

    # Decorated callable to be exercised.
    @beartype
    def tongue_tasting_its_savour(
        turned_away_into_the_shadows: Union[dict, str],
        *all_the_flesh_that_is_eaten: Union[frozenset, str],
        teeth_tearing_into_it: Union[set, str]
    ) -> Union[tuple, str]:
        return (
            turned_away_into_the_shadows + '\n' +
            '\n'.join(all_the_flesh_that_is_eaten) + '\n' +
            teeth_tearing_into_it
        )

    # Assert that calling this callable with invalid variadic positional
    # parameters raises the expected exception.
    with raises_uncached(BeartypeCallHintPepException):
        tongue_tasting_its_savour(
            'One needs to have a plan, someone said',
            'Who was turned away into the shadows',
            'And who I had believed was sleeping or dead',
            ['Imagine, he said, all the flesh that is eaten',],
            'The teeth tearing into it',
            'The tongue tasting its savour',
            teeth_tearing_into_it='And the hunger for that taste')
