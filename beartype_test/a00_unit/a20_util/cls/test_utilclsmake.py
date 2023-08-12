#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class factory** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cls.utilclsmake` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_make_type() -> None:
    '''
    Test the :func:`beartype._util.cls.utilclsmake.make_type` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilTypeException
    from beartype._util.cls.utilclsmake import make_type
    from beartype._util.cls.utilclstest import is_type_subclass
    from pytest import raises

    # ....................{ LOCALS                         }....................
    class TooEnamouredOfThatVoice(object):
        '''
        Arbitrary base class from which to subclass classes defined below.
        '''

    # ....................{ PASS                           }....................
    # Assert this factory creates and returns the expected class when the passed
    # name is a valid unqualified Python identifier.
    AndSilence = make_type(type_name='AndSilence')
    assert isinstance(AndSilence, type)
    assert AndSilence.__name__ == 'AndSilence'

    # Assert this factory creates and returns the expected class when passed a
    # tuple of one or more base classes.
    BySolemnVision = make_type(
        type_name='BySolemnVision', type_bases=(TooEnamouredOfThatVoice,))
    assert is_type_subclass(BySolemnVision, TooEnamouredOfThatVoice)

    # Assert this factory creates and returns the expected class when passed a
    # dictionary of one or more class attributes.
    BrightSilverDream = make_type(type_name='BrightSilverDream', type_scope={
        'every_sight': 'His infancy was nurtured.',
        'and_sound': lambda self: self.every_sight,
    })
    assert (
        BrightSilverDream.every_sight ==
        BrightSilverDream().and_sound() == 'His infancy was nurtured.'
    )

    # Assert this factory creates and returns the expected class when the passed
    # module name is a valid Python identifier.
    SentToHisHeart = make_type(
        type_name='SentToHisHeart', type_module_name='its_choicest.impulses')
    assert SentToHisHeart.__module__ == 'its_choicest.impulses'

    # Assert this factory creates and returns the expected class when passed a
    # docstring.
    TheFountains = make_type(
        type_name='TheFountains', type_doc='of divine philosophy')
    assert TheFountains.__doc__ == 'of divine philosophy'

    # ....................{ FAIL                           }....................
    # Assert this factory raises the expected exception when the passed name is
    # the empty string.
    with raises(_BeartypeUtilTypeException):
        make_type('')

    # Assert this factory raises the expected exception when the passed name is
    # *NOT* a valid Python identifier.
    with raises(_BeartypeUtilTypeException):
        make_type('And wasted for fond love of his wild eyes.')

    # Assert this factory raises the expected exception when the passed name is
    # a valid Python identifier that is fully-qualified (i.e., contains one or
    # more "." characters).
    with raises(_BeartypeUtilTypeException):
        make_type('The_fire.of.those_soft_orbs.has_ceased.to_burn')

    # Assert this factory raises the expected exception when the passed module
    # name is the empty string.
    with raises(_BeartypeUtilTypeException):
        make_type(type_name='And_Silence', type_module_name='')

    # Assert this factory raises the expected exception when the passed module
    # name is *NOT* a valid Python identifier.
    with raises(_BeartypeUtilTypeException):
        make_type(
            type_name='And_Silence',
            type_module_name='Locks its mute music in her rugged cell.',
        )
