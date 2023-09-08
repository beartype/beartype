#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`591` unit tests.

This submodule unit tests :pep:`591` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_pep591() -> None:
    '''
    Test :pep:`557` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.8 *or* skip
    otherwise.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype.typing import Final
    from dataclasses import dataclass
    from pytest import raises

    # ..................{ LOCALS                             }..................
    @beartype
    @dataclass
    class WildSpirit(object):
        '''
        Arbitrary dataclass type-checked by :func:`beartype.beartype`.
        '''

        which_art_moving_everywhere: Final[str] = (
            'Destroyer and preserver; hear, oh hear!')
        '''
        Field annotated by the :obj:`typing.Final` type hint factory subscripted
        by an arbitrary child type hint, passed by the :func:`.dataclass`
        decorator to :meth:`.__init__`.
        '''

        heaven_and_ocean: Final = (
            b'Shook from the tangled boughs of Heaven and Ocean,')
        '''
        Field annotated by the unsubscripted :obj:`typing.Final` type hint
        factory, passed by the :func:`.dataclass` decorator to
        :meth:`.__init__`.
        '''

    # Arbitrary instance of this dataclass exercising all edge cases.
    destroyer_and_preserver = WildSpirit()

    # ..................{ PASS                               }..................
    # Assert this dataclass defines the expected attributes.
    assert destroyer_and_preserver.which_art_moving_everywhere == (
        'Destroyer and preserver; hear, oh hear!')
    assert destroyer_and_preserver.heaven_and_ocean == (
        b'Shook from the tangled boughs of Heaven and Ocean,')

    #FIXME: Refactor this to test that redefinition fails *AFTER* @beartype
    #fully supports PEP 591. *sigh*
    # Assert that attempting to redefine this final field currently silently
    # succeeds, despite technically violating PEP 591.
    destroyer_and_preserver.which_art_moving_everywhere = (
        "Loose clouds like earth's decaying leaves are shed,")

    # ..................{ FAIL                               }..................
    # Assert that attempting to instantiate an instance of this dataclass with a
    # parameter violating the corresponding type hint annotating the field of
    # the same name raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        WildSpirit(which_art_moving_everywhere=(
            b"Thou on whose stream, mid the steep sky's commotion,"))
