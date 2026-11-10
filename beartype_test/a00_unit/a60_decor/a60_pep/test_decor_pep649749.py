#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`649`- and :pep:`749`-compliant **unit tests**.

This submodule unit tests the intersection of :pep:`649` and :pep:`749` support
implemented in the :func:`beartype.beartype` decorator with the standard
:mod:`annotationlib` module also conforming to those PEPs.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.14.0')
def test_decor_pep649749() -> None:
    '''
    Test :pep:`649` and :pep:`749` support implemented in the
    :func:`beartype.beartype` decorator if the active Python interpreter targets
    Python >= 3.14 *or* skip otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype._util.hint.pep.proposal.pep749.pep649749annotate import (
        get_hintable_pep649749_annotations)
    from annotationlib import (
        Format,
        get_annotations,
    )
    # from pytest import raises

    # ....................{ CALLABLES                      }....................
    @beartype
    def unused_to_bend(by_hard_compulsion_bent: 'SorrowOfTheTime') -> None:
        '''
        Arbitrary :func:`.beartype`-decorated function intentionally annotated
        by a :pep:`484`-compliant stringified relative forward reference
        referring to a type that has yet to be defined, which the
        :func:`.beartype` decorator internally coerces into a
        :mod:`beartype`-specific forward reference proxy and then replaces the
        prior C-based :pep:`749`-compliant ``__annotate__()`` dunder method
        implicitly defined by CPython on this function with a
        :mod:`beartype`-specific pure-Python ``__annotate__()`` dunder method
        hopefully also complying with :pep:`749`.
        '''

        pass

    # ....................{ CLASSES                        }....................
    class SorrowOfTheTime(object):
        '''
        Arbitrary type referenced by a :pep:`484`-compliant stringified relative
        forward reference annotating the function defined above.
        '''

        pass

    # ....................{ LOCALS                         }....................
    # Frozen set of all *PUBLIC* members of the PEP 749-compliant
    # "annotationlib.Format" enumeration (and thus intentionally ignoring the
    # *PRIVATE* "VALUE_WITH_FAKE_GLOBALS" member of that enumeration).
    HINT_FORMATS = frozenset(({
        hint_format
        for hint_format in Format
        if hint_format is not Format.VALUE_WITH_FAKE_GLOBALS
    }))

    # ....................{ ASSERTS                        }....................
    # For each public member of the PEP 749-compliant "annotationlib.Format"
    # enumeration...
    for hint_format in HINT_FORMATS:
        # "__annotations__" dunder dictionary expected to be returned by the
        # standard annotationlib.get_annotations() getter when passed that
        # function and enumeration member.
        annotations_expected = get_hintable_pep649749_annotations(
            hintable=unused_to_bend, hint_format=hint_format)

        # "__annotations__" dunder dictionary actually returned by that getter.
        annotations_returned = get_annotations(
            unused_to_bend, format=hint_format)

        # Assert that this dictionary is as expected.
        assert annotations_returned == annotations_expected
