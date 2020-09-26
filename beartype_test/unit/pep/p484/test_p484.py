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

# ....................{ TESTS ~ pass : param : kind       }....................
def test_p484() -> None:
    '''
    Test usage of the :func:`beartype.beartype` decorator for a function call
    passed non-variadic positional and/or keyword parameters annotated with
    `PEP 484`_-compliant type hints.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallCheckPepException,
        BeartypeCallCheckNonPepException,
    )
    from beartype_test.unit.data.data_hint import (
        PEP_HINT_TO_META, PEP_HINT_NONATTR_TO_META)

    # Dictionary mapping various PEP-compliant type hints to "_PepHintMetadata"
    # instances detailing those hints with metadata applicable to testing
    # scenarios -- regardless of whether those hints are uniquely identified by
    # argumentless "typing" attributes or not.
    PEP_HINT_ALL_TO_META = ChainMap(PEP_HINT_TO_META, PEP_HINT_NONATTR_TO_META)

    # For each predefined PEP-compliant type hint and associated metadata...
    for pep_hint, pep_hint_meta in PEP_HINT_ALL_TO_META.items():
        # If this hint is currently unsupported, continue to the next.
        if not pep_hint_meta.is_supported:
            continue
        # Else, this hint is currently supported.

        # Dynamically define a callable both accepting a single parameter and
        # returning a value annotated by this hint whose implementation
        # trivially reduces to the identity function.
        @beartype
        def pep_hinted(pep_hinted_param: pep_hint) -> pep_hint:
            return pep_hinted_param

        # Type of exception raised by this wrapper on type-check failures.; else, this
        # wrapper
        # Note that these hints all .
        exception_cls = (
            # If this hint is uniquely identified by an argumentless "typing"
            # attribute, this wrapper raises PEP-compliant exceptions.
            BeartypeCallCheckPepException
            if pep_hint_meta.typing_attr is not None else
            # Else, this hint reduces to a builtin type and is thus detected as
            # a PEP-noncompliant type hint. In this case, this wrapper raises
            # PEP-noncompliant exceptions.
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
            # Assert that iterables of uncompiled regular expression expected
            # to match and *NOT* match this message are *NOT* strings, as
            # commonly occurs when accidentally omitting a trailing comma in
            # tuples containing only one string: e.g.,
            # * "('This is a tuple, yo.',)" is a 1-tuple containing one string.
            # * "('This is a string, bro.')" is a string *NOT* contained in a
            #   1-tuple.
            assert not isinstance(
                pith_unsatisfied_meta.exception_str_match_regexes, str)
            assert not isinstance(
                pith_unsatisfied_meta.exception_str_not_match_regexes, str)

            # Assert this wrapper function raises the expected exception when
            # type-checking this object against this hint.
            with raises_uncached(exception_cls) as exception_info:
                pep_hinted(pith_unsatisfied_meta.pith)

            # Exception message raised by this wrapper function.
            exception_str = str(exception_info.value)
            # print('exception message: {}'.format(exception_str))

            # For each uncompiled regular expression expected to match this
            # message, assert this expression actually does so.
            #
            # Note that the re.search() rather than re.match() function is
            # called. The latter is rooted at the start of the string and thus
            # *ONLY* matches prefixes, while the former is *NOT* rooted at any
            # string position and thus matches arbitrary substrings as desired.
            for exception_str_match_regex in (
                pith_unsatisfied_meta.exception_str_match_regexes):
                assert search(
                    exception_str_match_regex, exception_str) is not None

            # For each uncompiled regular expression expected to *NOT* match
            # this message, assert this expression actually does so.
            for exception_str_not_match_regex in (
                pith_unsatisfied_meta.exception_str_not_match_regexes):
                assert search(
                    exception_str_not_match_regex, exception_str) is None

        # assert False is True
