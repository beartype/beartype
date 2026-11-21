#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator space consumption** unit tests.

This submodule unit tests space-specific concerns surrounding the
:func:`beartype.beartype` decorator as a safety guard against regressions back
to previously unsafe behaviour.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_space() -> None:
    '''
    Test that the :func:`beartype.decorator` decorator does *not* hold strong
    references to arbitrary user-defined callables and classes decorated by that
    decorator.

    This test guards against safety regressions in multiple intersecting issues.
    The :func:`beartype.beartype` decorator previously employed an overly eager
    memoization strategy. Doing so caused :mod:`beartype` to improperly hold
    strong references to arbitrary user-defined callables and classes decorated
    by that decorator, which then caused :mod:`beartype` to dangerously consume
    an unbounded amount of space.

    See Also
    --------
    https://github.com/beartype/beartype/issues/673
       Regression whose minimal reproducible example (MRE) inspired this test.
    https://github.com/beartype/beartype/issues/769
       Regression whose minimal reproducible example (MRE) inspired generalizing
       this test to cover :pep:`484`-compliant quoted forward references.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from gc import collect as gc_collect
    from weakref import ref as weakref_ref

    # ....................{ LOCALS                         }....................
    # List of weak references to all previously instantiated "UntilItCeased"
    # objects, intentionally defined *BEFORE* defining the
    # UntilItCeased.__init__() method accessing this list.
    until_it_ceased_refs_weak = []

    # ....................{ CLASSES                        }....................
    class UntilItCeased(object):
        '''
        Arbitrary trivial pure-Python class.
        '''

        def __init__(self) -> None:

            # Append a weak reference to this newly instantiated "UntilItCeased"
            # object to the list defined above.
            until_it_ceased_refs_weak.append(weakref_ref(self))

    # ....................{ CALLABLES                      }....................
    @beartype
    def and_still_he(were_the_same: int) -> int:
        '''
        Arbitrary pure-Python function internally defining a
        :func:`beartype.beartype`-decorated closure.
        '''

        # Arbitrary instance of an arbitrary pure-Python class, intentionally
        # re-instantiated on each call of this outer function to expose improper
        # attempts by the @beartype decorator to indirectly hold strong
        # references to this instance by directly holding strong references to
        # the @beartype-decorated closure defined below.
        kept_them_wide = UntilItCeased()

        @beartype
        def and_still_they(bright_patient_stars: 'int') -> int:
            '''
            :func:`beartype.beartype`-decorated closure annotated by one or more
            PEP-compliant type hints whose body intentionally accesses the
            arbitrary instance defined above, which then forces Python to
            implicitly hold a strong reference to this instance as a free
            variable (i.e., closure-specific object exposed via the low-level
            ``__code__.co_freevars`` dunder attribute).

            Note that one of these type hints is intentionally defined as a
            :pep:`484`-compliant quoted forward reference. Resolving such
            references is highly non-trivial and thus tends to enter more
            complicated internal code paths deep inside the :mod:`beartype`
            package *not* entered for normal type hints. Previously, a small
            proper subset of that machinery was improperly memoized. Although
            small, the improper memoization of that machinery ultimately
            resulted in unbounded space consumption *only* the edge case of
            closures annotated by one or more :pep:`484`-compliant quoted
            forward references.

            See Also
            --------
            https://github.com/beartype/beartype/issues/769
               Regression whose minimal reproducible example (MRE) inspired
               generalizing this test to cover these references.
            '''

            # Perform an arbitrary operation accessing the instance defined
            # above and thus implicitly forcing Python to hold a strong
            # reference to this instance for the lifetime of this closure.
            return (
                were_the_same +
                bright_patient_stars +
                (1 if kept_them_wide else 0)  # <-- arbitrary dumbness is smart
            )

        # Return the arbitrary result of calling the closure defined above.
        return and_still_they(were_the_same)

    # ....................{ GARBAGE COLLECT                }....................
    # Repeatedly call the closure defined above an arbitrary number of times.
    # This number has been intentionally selected so as to increase the
    # likelihood of exposing space consumption regressions in the @beartype
    # decorator specifically and across the "beartype" package generally.
    for i in range(2000):
        and_still_he(i)

    # Garbage-collect (i.e., free the space previously consumed by) all
    # currently dead objects (i.e., which are no longer referred to outside
    # those objects) that have yet to be garbage-collected.
    #
    # Ideally, the @beartype decorator has been safely implemented to avoid
    # holding strong references to the callables and classes it decorates. This
    # includes the @beartype-decorated closures defined above. Since those
    # closures hold strong references to the function-specific instances they
    # access, this implicitly includes those function-specific instances.
    # Assuming the @beartype decorator has avoided holding strong references to
    # those closures and thus those instances, those closures and thus those
    # instances should now be dead and thus collected by this collection.
    gc_collect()

    # Total number of strong references to "UntilItCeased" instances localized
    # to the and_still_he() function called above. Since these instances
    # *SHOULD* be function-local and thus dead (by the above discussion), there
    # *SHOULD* be no such strong references remaining.
    UNTIL_IT_CEASED_REFS_STRONG_LEN = sum(
        1
        for until_it_ceased_ref_weak in until_it_ceased_refs_weak
        if until_it_ceased_ref_weak() is not None
    )

    # ....................{ ASSERTS                        }....................
    # Assert that there are *NO* strong references to "UntilItCeased" instances
    # localized to the and_still_he() function called above remaining. In other
    # words, the @beartype decorator has properly avoided holding strong
    # references to the closures defined by calls to that function and thus
    # implicitly holding strong references to these instances internally
    # referenced as free variables in the body of those closures.
    assert UNTIL_IT_CEASED_REFS_STRONG_LEN == 0
