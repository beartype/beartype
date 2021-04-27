#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **string munging** utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextmunge` submodule.
'''

# ....................{ IMPORTS                           }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_represent_object():
    '''
    Test the :func:`beartype._util.text.utiltextrepr.represent_object`
    function.
    '''

    # Defer heavyweight imports.
    from beartype._util.text.utiltextrepr import represent_object

    # Arbitrary class defining an unpunctuated representation (i.e.,
    # representation *NOT* already suffixed by punctuation).
    class ToASkylark(object):
        def __repr__(self):
            return 'Like a cloud of fire;'

    # Arbitrary class defining an empty representation.
    class ThouDostFloatAndRun(object):
        def __repr__(self):
            return ''

    # Assert this representer preserves the representations of terse objects
    # already suffixed by punctuation as is.
    assert represent_object(b'Higher still and higher') == repr(
        b'Higher still and higher')
    assert represent_object('From the earth thou springest') == repr(
        'From the earth thou springest')
    assert represent_object(ToASkylark) == repr(ToASkylark)

    # Assert this representer punctuates the representations of terse objects
    # *NOT* already suffixed by punctuation.
    assert represent_object(ToASkylark()) == '"Like a cloud of fire;"'

    # Assert this representer double-quotes empty representations.
    assert represent_object(ThouDostFloatAndRun()) == '""'

    # Assert this representer truncates the representations of lengthy objects
    # exceeding a reasonable maximum length to that length.
    the_blue_deep_thou_wingest = represent_object(
        obj='And singing still dost soar,\nand soaring ever singest.',
        max_len=42,
    )
    assert len(the_blue_deep_thou_wingest) == 42

    # Assert this representer truncates the representations of any objects
    # exceeding an unreasonably small maximum length to that length.
    like_a_star_of_heaven = represent_object(
        obj='In the golden lightning\nOf the sunken sun,',
        max_len=2,
    )
    assert len(like_a_star_of_heaven) == 2
