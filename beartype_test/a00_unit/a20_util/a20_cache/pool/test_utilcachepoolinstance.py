#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype utility fixed list pool unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.pool.utilcachepoolinstance` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from io import StringIO
from pytest import raises

# ....................{ TESTS                              }....................
def test_utilcachepool_instance() -> None:
    '''
    Test successful usage of the
    :mod:`beartype._util.cache.pool.utilcachepoolinstance` submodule.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.cache.pool.utilcachepoolinstance import (
        acquire_instance,
        release_instance,
    )

    # ....................{ CONSTANTS                      }....................
    # Culturally relevant Clash lyrics to be tested below.
    PUBLIC_SERVICE_ANNOUNCEMENT = '\n'.join((
        'You have the right not to be killed.',
        'Murder is a crime,',
        'Unless it was done',
        'By a policeman',
        'Or an aristocrat.',
    ))
    KNOW_YOUR_RIGHTS = '\n'.join((
        'You have the right to food money --',
        'Providing, of course, you',
        "Don't mind a little",
        'Investigation, humiliation,',
        'And (if you cross your fingers)',
        'Rehabilitation.',
    ))

    # ....................{ PASS ~ container               }....................
    # Repeat this test twice, thus asserting that builtin mutable containers are
    # necessarily cleared by the acquire_instance() function.
    for _ in range(2):
        # Acquire an arbitrary dictionary.
        look_up = acquire_instance(dict)

        # Assert this dictionary to be empty.
        assert not look_up

        # Add arbitrary key-value pairs to this dictionary.
        look_up.update({
            'Look up,': 'and let me see our doom in it;',
            'Look up, and': 'tell me if this feeble shape.',
        })

        # Release this dictionary.
        release_instance(look_up)

    # Repeat this test twice, thus asserting that builtin mutable containers are
    # necessarily cleared by the acquire_instance() function.
    for _ in range(2):
        # Acquire an arbitrary list.
        is_saturns = acquire_instance(list)

        # Assert this list to be empty.
        assert not is_saturns

        # Add arbitrary key-value pairs to this list.
        is_saturns.extend((
            "Is Saturn's;", 'tell me,', "if thou hear'st the voice",))

        # Release this list.
        release_instance(is_saturns)

    # Repeat this test twice, thus asserting that builtin mutable containers are
    # necessarily cleared by the acquire_instance() function.
    for _ in range(2):
        # Acquire an arbitrary set.
        of_saturn = acquire_instance(set)

        # Assert this set to be empty.
        assert not of_saturn

        # Add arbitrary key-value pairs to this set.
        of_saturn.update({
            'Of Saturn;', 'tell me,', 'if this wrinkling brow,',})

        # Release this set.
        release_instance(of_saturn)

    # ....................{ PASS ~ stringio                }....................
    # Acquire an arbitrary string buffer.
    public_service_announcement = acquire_instance(StringIO)

    # Clear this buffer and reset its position to the start.
    public_service_announcement.truncate(0)
    public_service_announcement.seek(0)

    # Write a series of culturally relevant Clash lyrics to this buffer.
    public_service_announcement.write('You have the right not to be killed.\n')
    public_service_announcement.write('Murder is a crime,\n')
    public_service_announcement.write('Unless it was done\n')
    public_service_announcement.write('By a policeman\n')
    public_service_announcement.write('Or an aristocrat.')

    # Acquire another arbitrary string buffer.
    know_your_rights = acquire_instance(StringIO)

    # Clear this buffer and reset its position to the start.
    know_your_rights.truncate(0)
    know_your_rights.seek(0)

    # Write another series of culturally relevant Clash lyrics to this buffer.
    know_your_rights.write('You have the right to food money --\n')
    know_your_rights.write('Providing, of course, you\n')
    know_your_rights.write("Don't mind a little\n")
    know_your_rights.write('Investigation, humiliation,\n')
    know_your_rights.write('And (if you cross your fingers)\n')
    know_your_rights.write('Rehabilitation.')

    # Assert the contents of these buffers to still be as expected.
    assert (
        public_service_announcement.getvalue() == PUBLIC_SERVICE_ANNOUNCEMENT)
    assert know_your_rights.getvalue() == KNOW_YOUR_RIGHTS

    # Release the first buffer back to its parent pool.
    release_instance(public_service_announcement)

    # Reacquire the same buffer again.
    public_service_announcement_too = acquire_instance(StringIO)

    # Assert this to be the same buffer.
    assert public_service_announcement is public_service_announcement_too

    # Assert the second buffer to *NOT* be the same buffer.
    assert public_service_announcement is not know_your_rights

    # Release these buffers back to their parent pools (in acquisition order).
    release_instance(public_service_announcement)
    release_instance(know_your_rights)

    # ....................{ FAIL                           }....................
    # Assert that typed objects may only be acquired with types.
    with raises(AssertionError):
        acquire_instance((
            'You have the right to free speech',
            'As long as',
            "You're not dumb enough to actually try it.",
        ))
    with raises(AssertionError):
        acquire_instance(1977)
