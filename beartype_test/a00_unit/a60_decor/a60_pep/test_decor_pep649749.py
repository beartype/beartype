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
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than, skip

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.14.0')
def test_decor_pep649749_annotate() -> None:
    '''
    Test support for :pep:`649`- and :pep:`749`-compliant ``__annotate__()``
    dunder methods implemented in the :func:`beartype.beartype` decorator if the
    active Python interpreter targets Python >= 3.14 *or* skip otherwise.
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

# ....................{ TESTS ~ pep : (484|604)            }....................
# @skip('Currently brokey. *sigh*')
@skip_if_python_version_less_than('3.14.0')
def test_decor_pep649749_ref_pep484604_union() -> None:
    '''
    Test support for :pep:`649`- and :pep:`749`-compliant unquoted forward
    references transitively subscripting :pep:`484`- and :pep:`604`-compliant
    unions implemented in the :func:`beartype.beartype` decorator if the active
    Python interpreter targets Python >= 3.14 *or* skip otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype_test._util.error.pyterrraise import raises_uncached
    from typing import Union

    # ....................{ CALLABLES                      }....................
    @beartype
    def grows_lush(
        in_juicy_stalks: IWillSmoothlySteer | str,
        for_many_quiet_hours: Union['IWillSmoothlySteer', bytes],
    ) -> tuple[IWillSmoothlySteer | str, Union['IWillSmoothlySteer', bytes]]:
        '''
        Arbitrary :func:`.beartype`-decorated function intentionally annotated
        by both:

        * A :pep:`749`-compliant unquoted forward reference subscripting a
          :pep:`604`-compliant new-style union. Note that this exercises the
          edge case in which an unquoted forward reference is *not* the root
          type hint but instead subscripts a parent type hint.
        * A :pep:`484`-compliant quoted forward reference subscripting a
          :pep:`484`-compliant old-style union. Note that this exercises an
          additional edge case in which a callable is annotated by both quoted
          and unquoted forward references. Yes, this actually blew up on us.
          Because... of course it did. Right? I sigh.
        '''

        return in_juicy_stalks, for_many_quiet_hours

    # ....................{ CLASSES                        }....................
    class IWillSmoothlySteer(object):
        '''
        Arbitrary type referenced by the :pep:`749`-compliant unquoted forward
        reference annotating the function defined above.
        '''

        pass

    # Instance of this type.
    my_little_boat = IWillSmoothlySteer()

    # Arbitrary string and bytestring.
    WITH_STREAMS_THAT_DEEPEN = "Grows lush in juicy stalks, I'll smoothly steer"
    FRESHLY_INTO_BOWERS = b'With streams that deepen freshly into bowers.'

    # ....................{ PASS                           }....................
    # Assert that this callable when passed a valid object satisfying the hints
    # annotating this callable returns that same object.
    assert grows_lush(
        in_juicy_stalks=my_little_boat,
        for_many_quiet_hours=FRESHLY_INTO_BOWERS,
    ) == (my_little_boat, FRESHLY_INTO_BOWERS)
    assert grows_lush(
        in_juicy_stalks=WITH_STREAMS_THAT_DEEPEN,
        for_many_quiet_hours=my_little_boat,
    ) == (WITH_STREAMS_THAT_DEEPEN, my_little_boat)

    # ....................{ FAIL                           }....................
    # Assert that this callable when passed an invalid object violating the
    # hints annotating this callable raises the expected exception.
    with raises_uncached(BeartypeCallHintParamViolation):
        grows_lush(
            in_juicy_stalks=my_little_boat,
            for_many_quiet_hours=WITH_STREAMS_THAT_DEEPEN,
        )
    with raises_uncached(BeartypeCallHintParamViolation):
        grows_lush(
            in_juicy_stalks=FRESHLY_INTO_BOWERS,
            for_many_quiet_hours=my_little_boat,
        )
