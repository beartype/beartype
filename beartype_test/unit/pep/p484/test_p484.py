#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP 484-compliant type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP 484-compliant type hints** (i.e., :mod:`beartype`-agnostic annotations
specifically compliant with `PEP 484`_).

See Also
----------
:mod:`beartype_test.unit.decor.code.test_code_pep`
    Submodule generically unit testing PEP-compliant type hints.

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
from typing import List

# ....................{ TESTS                             }....................
def test_p484() -> None:
    '''
    Test usage of the :func:`beartype.beartype` decorator for a function call
    passed non-variadic positional and/or keyword parameters annotated with
    `PEP 484`_-compliant type hints.

    This test additionally attempts to avoid similar issues to a `prior issue
    <issue #5_>`__ of this decorator induced by repeated
    :func:`beartype.beartype` decorations of different callables annotated by
    one or more of the same PEP-compliant type hints.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    .. _issue #5:
       https://github.com/beartype/beartype/issues/5
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallCheckPepException,
        BeartypeCallCheckNonPepException,
    )
    from beartype_test.unit.data.data_hint import (
        PEP_HINT_TO_META, PEP_HINT_NONATTR_TO_META)
    from beartype_test.unit.data._data_hint_pep import (
        _PepHintPithUnsatisfiedMetadata)

    # Dictionary mapping various PEP-compliant type hints to "_PepHintMetadata"
    # instances detailing those hints with metadata applicable to testing
    # scenarios -- regardless of whether those hints are uniquely identified by
    # argumentless "typing" attributes or not.
    PEP_HINT_ALL_TO_META = ChainMap(PEP_HINT_TO_META, PEP_HINT_NONATTR_TO_META)

    # Tuple of two arbitrary values used to trivially iterate twice below.
    RANGE_2 = (None, None)

    # For each predefined PEP-compliant type hint and associated metadata...
    for pep_hint, pep_hint_meta in PEP_HINT_ALL_TO_META.items():
        # If this hint is currently unsupported, continue to the next.
        if not pep_hint_meta.is_supported:
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
            def pep_hinted(pep_hinted_param: pep_hint) -> pep_hint:
                return pep_hinted_param

            # Type of exception raised by this wrapper on type-check failures.
            exception_cls = (
                # If this hint is uniquely identified by an argumentless
                # "typing" attribute, this wrapper raises PEP-compliant
                # exceptions.
                BeartypeCallCheckPepException
                if pep_hint_meta.typing_attr is not None else
                # Else, this hint reduces to a builtin type and is thus
                # detected as a PEP-noncompliant type hint. In this case, this
                # wrapper raises PEP-noncompliant exceptions.
                BeartypeCallCheckNonPepException
            )

            # For each object satisfying this hint...
            for pith_satisfied in pep_hint_meta.piths_satisfied:
                # Assert this wrapper function successfully type-checks this
                # object against this hint *WITHOUT* modifying this object.
                # print('PEP-testing {!r} against {!r}...'.format(pep_hint, pith_satisfied))
                assert pep_hinted(pith_satisfied) is pith_satisfied

            # For each object *NOT* satisfying this hint...
            for pith_unsatisfied_meta in pep_hint_meta.piths_unsatisfied_meta:
                # Assert this metadata is an instance of the desired dataclass.
                assert isinstance(
                    pith_unsatisfied_meta, _PepHintPithUnsatisfiedMetadata)

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
                # when type-checking this object against this hint.
                with raises_uncached(exception_cls) as exception_info:
                    pep_hinted(pith_unsatisfied_meta.pith)

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

# ....................{ TESTS ~ issue                     }....................
def test_p484_sequence_standard_cached() -> None:
    '''
    Test that a `subtle issue <issue #5_>`__ of the :func:`beartype.beartype`
    decorator with respect to metadata describing **PEP-compliant standard
    sequence hints** (e.g., :attr:`typing.List`) cached via memoization across
    calls to that decorator has been resolved and *not* regressed.

    Note that the more general-purpose :func:`test_p484` test *should* already
    exercise this issue, but that this issue was sufficiently dire to warrant
    special-purposed testing exercising this exact issue.

    .. _issue #5:
       https://github.com/beartype/beartype/issues/5
    '''

    # Defer heavyweight imports.
    from beartype import beartype

    # Callable annotated by an arbitrary PEP 484 standard sequence type hint.
    @beartype
    def fern_hill(prince_of_the_apple_towns: List[str]) -> str:
        return prince_of_the_apple_towns[0]

    # A different callable annotated by the same hint and another arbitrary
    # non-"typing" type hint.
    @beartype
    def apple_boughs(
        famous_among_the_barns: List[str], first_spinning_place: str) -> str:
        return famous_among_the_barns[-1] + first_spinning_place

    # Validate that these callables behave as expected.
    assert fern_hill([
        'Now as I was young and easy under the apple boughs',
        'About the lilting house and happy as the grass was green,'
        '  The night above the dingle starry,',
        '    Time let me hail and climb',
        '  Golden in the heydays of his eyes,',
        'And honoured among wagons I was prince of the apple towns',
        'And once below a time I lordly had the trees and leaves',
        '    Trail with daisies and barley',
        '  Down the rivers of the windfall light. ',
    ]) == 'Now as I was young and easy under the apple boughs'
    assert apple_boughs([
        'And as I was green and carefree, famous among the barns',
        'About the happy yard and singing as the farm was home,',
        '  In the sun that is young once only,',
        '    Time let me play and be',
        '  Golden in the mercy of his means,',
        'And green and golden I was huntsman and herdsman, the calves',
        'Sang to my horn, the foxes on the hills barked clear and cold,',
        '    And the sabbath rang slowly',
        '  In the pebbles of the holy streams.',
    ], 'All the sun long it was running, it was lovely, the hay') == (
        '  In the pebbles of the holy streams.'
        'All the sun long it was running, it was lovely, the hay')
