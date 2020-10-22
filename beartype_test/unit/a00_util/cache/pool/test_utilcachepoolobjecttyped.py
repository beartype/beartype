#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype utility fixed list pool unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.pool.utilcachepoolobjecttyped` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from io import StringIO
from pytest import raises

# ....................{ TESTS ~ pool                      }....................
def test_objecttyped_pool_pass() -> None:
    '''
    Test successful usage of the
    :mod:`beartype._util.cache.pool.utilcachepoolobjecttyped` submodule.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.pool.utilcachepoolobjecttyped import (
        acquire_object_typed, release_object_typed)

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

    # Acquire an arbitrary string buffer.
    public_service_announcement = acquire_object_typed(cls=StringIO)

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
    know_your_rights = acquire_object_typed(cls=StringIO)

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
    release_object_typed(public_service_announcement)

    # Reacquire the same buffer again.
    public_service_announcement_too = acquire_object_typed(cls=StringIO)

    # Assert this to be the same buffer.
    assert public_service_announcement is public_service_announcement_too

    # Assert the second buffer to *NOT* be the same buffer.
    assert public_service_announcement is not know_your_rights

    # Release these buffers back to their parent pools (in acquisition order).
    release_object_typed(public_service_announcement)
    release_object_typed(know_your_rights)


def test_objecttyped_pool_fail() -> None:
    '''
    Test unsuccessful usage of the
    :mod:`beartype._util.cache.pool.utilcachepoolobjecttyped` submodule.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.pool.utilcachepoolobjecttyped import (
        acquire_object_typed)
    from beartype.roar import _BeartypeUtilCachedObjectTypedException

    # Assert that typed objects may only be acquired with types.
    with raises(_BeartypeUtilCachedObjectTypedException):
        acquire_object_typed((
            'You have the right to free speech',
            'As long as',
            "You're not dumb enough to actually try it.",
        ))
    with raises(_BeartypeUtilCachedObjectTypedException):
        acquire_object_typed(1977)
