#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype plugin mixin unit tests.**

This submodule unit tests protocols defined by the private
:func:`beartype.plug._plughintable` submodule, most of which are publicly exported
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
    Test the :class:`beartype.plug._plughintable.BeartypeHintable` mixin.
    '''

    # .....................{ IMPORTS                       }....................
    # Defer test-specific imports.
    from beartype.plug import BeartypeHintable
    from pytest import raises

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

    # .....................{ ASSERTS                       }....................
    # Assert that calling a concrete __beartype_hint__() class method of a
    # "BeartypeHintable" subclass returns the expected type hint.
    assert NorWhenTheFlakesBurn.__beartype_hint__() is str

    # Assert that calling the abstract __beartype_hint__() class method raises
    # the expected exception.
    with raises(NotImplementedError):
        BeartypeHintable.__beartype_hint__()
