#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype plugin mixin unit tests.**

This submodule unit tests protocols defined by the private
:func:`beartype.plug._plugmixin` submodule, most of which are publicly exported
to end users and thus critically important.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_beartypehintable() -> None:
    '''
    Test the :class:`beartype.plug._plugmixin.BeartypeHintable` mixin.
    '''

    # .....................{ IMPORTS                       }....................
    # Defer test-specific imports.
    from beartype.plug import BeartypeHintable
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8

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
    #FIXME: Repair us up, please.
    # # If the active Python interpreter targets Python >= 3.8 and thus supports
    # # PEP 544-compliant protocols via the "typing.Protocol" superclass...
    # if IS_PYTHON_AT_LEAST_3_8:
    #     # Assert that classes explicitly satisfying this protocol actually do.
    #     assert isinstance(NorWhenTheFlakesBurn, BeartypeHintable)
    #
    #     # Assert that classes implicitly satisfying this protocol actually do.
    #     assert isinstance(InTheSinkingSun, BeartypeHintable)
    #
    #     # Assert that classes violating this protocol actually do.
    #     assert not isinstance(OrTheStarBeamsDartThroughThem, BeartypeHintable)
    # # Else, the active Python interpreter targets Python < 3.7 and thus fails to
    # # support PEP 544-compliant protocols via the "typing.Protocol" superclass.
    # # In this case...
    # else:
    #     # Assert that classes explicitly satisfying this protocol actually do --
    #     # albeit via standard subclass relations rather than full-blown
    #     # structural subtyping.
    #     assert issubclass(NorWhenTheFlakesBurn, BeartypeHintable)
    #
    #     # Assert that classes implicitly satisfying this protocol do *NOT*, as
    #     # Python <= 3.7 lacks support for structural subtyping.
    #     assert not issubclass(InTheSinkingSun, BeartypeHintable)
    #
    #     # Assert that classes violating this protocol actually do.
    #     assert not issubclass(OrTheStarBeamsDartThroughThem, BeartypeHintable)
