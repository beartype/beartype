#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator mypy-compliant type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to :mod:`mypy`-compliant type hints (i.e., type hints that are *not* explicitly
PEP-compliant but are effectively PEP-compliant due to being accepted by
:mod:`mypy`, the *de facto* type-hinting standard).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_mypy_notimplemented() -> None:
    '''
    Test the :func:`beartype.beartype` decorator against :mod:`mypy` compliant
    usage of the :data:`NotImplemented` singleton, which is contextually
    permissible *only* as an unsubscripted return annotation of binary dunder
    methods.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintReturnViolation
    from beartype_test._util.pytroar import raises_uncached

    # ..................{ LOCALS                             }..................
    # Without this, the forward reference in the return type of
    # TheCloud.__add__ (below) will fail because bear desperately yearns to
    # find it at the module level. And who are we to be so cruel as to hide the
    # object of her desires any more deeply than that?
    global TheCloud

    # ..................{ CLASSES                            }..................
    class TheCloud:
        '''
        Arbitrary class declaring a method exercising this test.
        '''

        @beartype
        def __eq__(self, other: object) -> bool:
            '''
            Arbitrary binary dunder method correctly returning the
            ``NotImplemented`` singleton.
            '''

            # If the passed object is an instance of the same class, return
            # true only if that object is exactly this object.
            if isinstance(other, TheCloud):
                return self is other

            # Else, return the "NotImplemented" singleton.
            return NotImplemented


        @beartype
        def __add__(self, other: object) -> "TheCloud":
            '''
            Another arbitrary binary dunder method correctly returning the
            ``NotImplemented`` singleton.
            '''
            # Create a new cloud when trying to add two clouds,
            # because...erm...math! No, wait. Because this is an entirely
            # contrived example for testing purposes and neither intends nor
            # offers any commentary about the subtle tensions between
            # uniqueness, individualism, connectedness, and community. Such
            # matters are left for quiet contemplation by the reader.
            if isinstance(other, TheCloud):
                return TheCloud()
            # Apparently these clouds do not enjoy the company of non-clouds.
            # While such isolationist tendencies may sadden us, we nonetheless
            # respect each cloud's autonomy.
            return NotImplemented


        @beartype
        def is_equal(self, other: object) -> bool:
            '''
            Arbitrary non-dunder method erroneously returning the
            ``NotImplemented`` singleton.
            '''

            # If the passed object is an instance of the same class, return
            # true only if that object is exactly this object.
            if isinstance(other, TheCloud):
                return self is other

            # Else, return the "NotImplemented" singleton.
            return NotImplemented

    # Pair of instances of this class.
    the_seas    = TheCloud()
    the_streams = TheCloud()

    # ..................{ ASSERTS                            }..................
    # Assert each instance compares equal to itself.
    assert the_seas    == the_seas
    assert the_streams == the_streams

    # Assert each instance compares unequal to the other instance.
    assert the_seas    != the_streams
    assert the_streams != the_seas

    # Assert each instance compares unequal to objects of different classes.
    assert the_seas    != 'I bring fresh showers for the thirsting flowers,'
    assert the_streams != 'From the seas and the streams;'

    # Assert explicit methods of each instance also compares equal to itself.
    assert the_seas.is_equal(the_seas)
    assert the_streams.is_equal(the_streams)

    # Assert explicit methods of each instance also compares unequal to the
    # other instance.
    assert not the_seas.is_equal(the_streams)
    assert not the_streams.is_equal(the_seas)

    # Assert the special case in @beartype-generated wrappers implicitly
    # type-checking binary dunder methods annotated as, e.g., returning "bool" to
    # instead effectively return "Union[bool, type(NotImplemented)]" does *NOT*
    # apply to standard methods -- even those with the exact same method body.
    with raises_uncached(BeartypeCallHintReturnViolation):
        the_seas.is_equal('I bear light shade for the leaves when laid')

    # Assert we can "__add__" two cloud instances...
    assert isinstance(the_seas + the_streams, TheCloud)

    # ...but not a cloud instance with an instance of another class *AND* that
    # the attempt results in a "TypeError" (the intended side effect of
    # returning "NotImplemented" from a binary dunder method).
    with raises_uncached(TypeError):
        the_seas + 'I bear light shade for the leaves when laid'
