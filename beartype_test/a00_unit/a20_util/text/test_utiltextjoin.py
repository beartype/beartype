#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **string-joining utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextjoin` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_join_strings_delimited() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextjoin.join_strings_delimited` function.
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


def test_join_strings_commaed_or() -> None:
    '''
    Test the
    :func:`beartype._util.text.utiltextjoin.join_strings_commaed_or`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextjoin import join_strings_commaed_or

    # Assert that joining a sequence of no strings returns the empty string.
    assert join_strings_commaed_or((
        'A mighty fountain momently was forced:',
        'Amid whose swift half-intermitted burst',
        'Huge fragments vaulted like rebounding hail,',
    )) == (
        'A mighty fountain momently was forced:, '
        'Amid whose swift half-intermitted burst, or '
        'Huge fragments vaulted like rebounding hail,'
    )
