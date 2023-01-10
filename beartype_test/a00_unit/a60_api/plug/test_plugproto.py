#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype protocol unit tests.**

This submodule unit tests protocols defined by the private
:func:`beartype.plug._plugproto` submodule, most of which are publicly exported
to end users and thus critically important.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# .....................{ TESTS                             }....................
def test_beartypehintable() -> None:
    '''
    Test the :class:`beartype.plug._plugproto.BeartypeHintable` protocol.
    '''

    # .....................{ IMPORTS                       }....................
    # Defer test-specific imports.
    from beartype.plug._plugproto import BeartypeHintable

    # .....................{ CLASSES                       }....................
    class NorWhenTheFlakesBurn(BeartypeHintable):
        '''
        Arbitrary class explicitly satisfying the :class:`BeartypeHintable`
        protocol.
        '''

        @classmethod
        def __beartype_hint__(cls) -> object:
            '''
            Arbitrary beartype type hint transform reducing to an arbitrary
            PEP-compliant type hint.
            '''

            return str


    class InTheSinkingSun(object):
        '''
        Arbitrary class implicitly satisfying the :class:`BeartypeHintable`
        protocol.
        '''

        @classmethod
        def __beartype_hint__(cls) -> object:
            '''
            Arbitrary beartype type hint transform reducing to an arbitrary
            PEP-compliant type hint.
            '''

            return int


    class OrTheStarBeamsDartThroughThem(object):
        '''
        Arbitrary class violating the :class:`BeartypeHintable` protocol.
        '''

        pass

    # .....................{ ASSERTS                       }....................
    # Assert that classes satisfying this protocol actually do.
    assert isinstance(NorWhenTheFlakesBurn, BeartypeHintable)
    assert isinstance(InTheSinkingSun, BeartypeHintable)

    # Assert that classes violating this protocol actually do.
    assert not isinstance(OrTheStarBeamsDartThroughThem, BeartypeHintable)
