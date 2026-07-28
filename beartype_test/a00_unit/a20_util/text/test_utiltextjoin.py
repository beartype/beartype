#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **string-joining utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextjoin` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ bulleted                   }....................
def test_join_strings_bulleted_unnumbered() -> None:
    '''
    Test the
    :func:`beartype._util.text.utiltextjoin.join_strings_bulleted_unnumbered`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextjoin import (
        join_strings_bulleted_unnumbered)

    # Assert that joining a sequence of no strings returns the empty string.
    assert join_strings_bulleted_unnumbered(()) == ''

    # Assert that joining a sequence of one string returns that string prefixed
    # by the bullet point delimiter.
    assert join_strings_bulleted_unnumbered(
        ('My life is but the life of winds and tides,',)) == (
        '\n* My life is but the life of winds and tides,')

    # Assert that joining a sequence of two or more strings returns these
    # strings prefixed by the bullet point delimiter.
    assert join_strings_bulleted_unnumbered(
        strings=(
            'No more than winds and tides can I avail:—',
            'But thou canst.—Be thou therefore in the van',
        ),
    ) == (
        '\n* No more than winds and tides can I avail:—'
        '\n* But thou canst.—Be thou therefore in the van'
    )

    # Assert that joining a sequence of two or more strings with additional
    # double-quoting returns these strings first double-quoted and then prefixed
    # by the bullet point delimiter.
    assert join_strings_bulleted_unnumbered(
        strings=(
            "Of circumstance; yea, seize the arrow's barb",
            'Before the tense string murmur.—To the earth!',
        ),
        is_double_quoted=True,
    ) == (
        "\n* \"Of circumstance; yea, seize the arrow's barb\""
        '\n* "Before the tense string murmur.—To the earth!"'
    )

    # Assert that joining a generator of three or more strings returns these
    # strings conditionally delimited by the appropriate delimiters.
    assert join_strings_bulleted_unnumbered(
        (str(integer) for integer in range(3))) == (
        '\n* 0'
        '\n* 1'
        '\n* 2'
    )

# ....................{ TESTS ~ commaed                    }....................
def test_join_strings_commaed_and() -> None:
    '''
    Test the
    :func:`beartype._util.text.utiltextjoin.join_strings_commaed_and`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextjoin import join_strings_commaed_and

    # Assert that joining a sequence of three and more substrings returns the
    # expected string comma-delimiting these substrings and additionally
    # delimiting the second and third such substrings by the conjunction "and".
    assert join_strings_commaed_and((
        'As thou canst move about, an evident God;',
        'And canst oppose to each malignant hour',
        'Ethereal presence:—I am but a voice;',
    )) == (
        'As thou canst move about, an evident God;, '
        'And canst oppose to each malignant hour, and '
        'Ethereal presence:—I am but a voice;'
    )


def test_join_strings_commaed_or() -> None:
    '''
    Test the
    :func:`beartype._util.text.utiltextjoin.join_strings_commaed_or`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextjoin import join_strings_commaed_or

    # Assert that joining a sequence of three or more substrings returns the
    # expected string comma-delimiting these substrings and additionally
    # delimiting the second and third such substrings by the disjunction "or".
    assert join_strings_commaed_or((
        'A mighty fountain momently was forced:',
        'Amid whose swift half-intermitted burst',
        'Huge fragments vaulted like rebounding hail,',
    )) == (
        'A mighty fountain momently was forced:, '
        'Amid whose swift half-intermitted burst, or '
        'Huge fragments vaulted like rebounding hail,'
    )

# ....................{ TESTS ~ delimited                  }....................
def test_join_strings_delimited() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextjoin.join_strings_delimited`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextjoin import join_strings_delimited

    # Assert that joining a sequence of no strings returns the empty string.
    assert join_strings_delimited(
        strings=(),
        delimiter_if_two='In Xanadu did Kubla Khan',
        delimiter_if_three_or_more_nonlast='A stately pleasure-dome decree:',
        delimiter_if_three_or_more_last='Where Alph, the sacred river, ran',
    ) == ''

    # Assert that joining a sequence of one string returns that string.
    assert join_strings_delimited(
        strings=('Through caverns measureless to man',),
        delimiter_if_two='Down to a sunless sea.',
        delimiter_if_three_or_more_nonlast=(
            'So twice five miles of fertile ground'),
        delimiter_if_three_or_more_last=(
            'With walls and towers were girdled round;'),
    ) == 'Through caverns measureless to man'

    # Assert that joining a sequence of two strings returns these strings
    # conditionally delimited by the appropriate delimiter.
    assert join_strings_delimited(
        strings=(
            'And there were gardens bright with sinuous rills,',
            'Where blossomed many an incense-bearing tree;',
        ),
        delimiter_if_two='And here were forests ancient as the hills,',
        delimiter_if_three_or_more_nonlast=(
            'Enfolding sunny spots of greenery.'),
        delimiter_if_three_or_more_last=(
            'But oh! that deep romantic chasm which slanted'),
    ) == (
        'And there were gardens bright with sinuous rills,'
        'And here were forests ancient as the hills,'
        'Where blossomed many an incense-bearing tree;'
    )

    # Assert that joining a sequence of two strings with additional
    # double-quoting returns these strings first double-quoted and then
    # conditionally delimited by the appropriate delimiter.
    assert join_strings_delimited(
        strings=(
            'For there thou wilt find Saturn and his woes.',
            'Meanwhile I will keep watch on thy bright sun,',
        ),
        delimiter_if_two='And of thy seasons be a careful nurse."—',
        delimiter_if_three_or_more_nonlast=(
            'Ere half this region-whisper had come down,'),
        delimiter_if_three_or_more_last='Hyperion arose, and on the stars',
        is_double_quoted=True,
    ) == (
        '"For there thou wilt find Saturn and his woes."'
        'And of thy seasons be a careful nurse."—'
        '"Meanwhile I will keep watch on thy bright sun,"'
    )

    # Assert that joining a sequence of three strings returns these strings
    # conditionally delimited by the appropriate delimiters.
    assert join_strings_delimited(
        strings=(
            'Down the green hill athwart a cedarn cover!',
            'A savage place! as holy and enchanted',
            'As e’er beneath a waning moon was haunted',
        ),
        delimiter_if_two='By woman wailing for her demon-lover!',
        delimiter_if_three_or_more_nonlast=(
            'And from this chasm, with ceaseless turmoil seething,'),
        delimiter_if_three_or_more_last=(
            'As if this earth in fast thick pants were breathing,'),
    ) == (
        'Down the green hill athwart a cedarn cover!'
        'And from this chasm, with ceaseless turmoil seething,'
        'A savage place! as holy and enchanted'
        'As if this earth in fast thick pants were breathing,'
        'As e’er beneath a waning moon was haunted'
    )

    # Assert that joining a generator of three or more strings returns these
    # strings conditionally delimited by the appropriate delimiters.
    assert join_strings_delimited(
        strings=(str(integer) for integer in range(3)),
        delimiter_if_two='; ',
        delimiter_if_three_or_more_nonlast=', ',
        delimiter_if_three_or_more_last=', and ',
    ) == '0, 1, and 2'
