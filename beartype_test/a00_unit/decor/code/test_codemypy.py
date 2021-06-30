#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator mypy-compliant type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to :mod:`mypy`-compliant type hints (i.e., type hints that are *not* explicitly
PEP-compliant but are effectively PEP-compliant due to being accepted by
:mod:`mypy`, the de-facto type-hinting standard).
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.pyterror import raises_uncached

# ....................{ TESTS ~ decor : no_type_check     }....................
def test_decor_mypy_notimplemented() -> None:
    '''
    Test the :func:`beartype.beartype` decorator against :mod:`mypy` compliant
    usage of the ``NotImplemented`` singleton, which is contextually
    permissible *only* as an unsubscripted return annotation of binary dunder
    methods.
    '''
    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintPepReturnException

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
    # type-checking binary dunder methods annotated as returning "bool" to
    # instead effectively return "Union[bool, type(NotImplemented)]" does *NOT*
    # apply to standard methods -- even those with the exact same method body.
    with raises_uncached(BeartypeCallHintPepReturnException):
        the_seas.is_equal('I bear light shade for the leaves when laid')
