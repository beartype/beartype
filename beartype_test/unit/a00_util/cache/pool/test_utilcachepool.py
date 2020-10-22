#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype key pool unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.pool.utilcachepool` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from io import StringIO
from pytest import raises

# ....................{ TESTS                             }....................
def test_key_pool_pass() -> None:
    '''
    Test successful usage of the
    :class:`beartype._util.cache.pool.utilcachepool.KeyPool` type.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.pool.utilcachepool import KeyPool

    # Key pool to be tested, seeding empty pools keyed on the "newline"
    # parameter passed to the StringIO.__init__() method with a new "StringIO"
    # instance initialized to that parameter.
    #
    # Note that the "initial_value" parameter is currently unavailable under
    # "pypy3" and *MUST* thus be omitted here:
    #     $ pypy3
    #     >>> from io import StringIO
    #     >>> StringIO(initial_value='', newline=newline)
    #     TypeError: __init__() got an unexpected keyword argument 'initial_value'
    key_pool = KeyPool(item_maker=lambda newline: StringIO(newline=newline))

    # Acquire a new "StringIO" buffer writing Windows-style newlines.
    windows_stringio = key_pool.acquire(key='\r\n')

    # Stanzas delimited by Windows-style newlines to be tested below.
    THE_DEAD_SHALL_BE_RAISED_INCORRUPTIBLE = '\r\n'.join((
        'My stomach, which has digested',
        'four hundred treaties giving the Indians',
        'eternal right to their land, I give to the Indians,',
        'I throw in my lungs which have spent four hundred years',
        'sucking in good faith on peace pipes.',
    ))
    BOOK_OF_NIGHTMARES = '\r\n'.join((
        'To the last man surviving on earth',
        'I give my eyelids worn out by fear, to wear',
        'in his long nights of radiation and silence,',
        'so that his eyes can’t close, for regret',
        'is like tears seeping through closed eyelids.',
    ))

    # Write a series of POSIX-style lines to this buffer.
    windows_stringio.write('My stomach, which has digested\n')
    windows_stringio.write('four hundred treaties giving the Indians\n')
    windows_stringio.write('eternal right to their land, I give to the Indians,\n')
    windows_stringio.write('I throw in my lungs which have spent four hundred years\n')
    windows_stringio.write('sucking in good faith on peace pipes.')

    # Assert that this buffer implicitly converted all POSIX- to Windows-style
    # newlines in the resulting string.
    assert (
        windows_stringio.getvalue() == THE_DEAD_SHALL_BE_RAISED_INCORRUPTIBLE)

    # Release this buffer back to its parent pool.
    key_pool.release(key='\r\n', item=windows_stringio)

    # Reacquire the same buffer again.
    windows_stringio_too = key_pool.acquire(key='\r\n')

    # Assert this to be the same buffer.
    assert windows_stringio is windows_stringio_too

    # Acquire another new "StringIO" buffer writing Windows-style newlines.
    windows_stringio_new = key_pool.acquire(key='\r\n')

    # Assert this to *NOT* be the same buffer.
    assert windows_stringio is not windows_stringio_new

    # Write a series of POSIX-style lines to this new buffer.
    windows_stringio_new.write('To the last man surviving on earth\n')
    windows_stringio_new.write('I give my eyelids worn out by fear, to wear\n')
    windows_stringio_new.write('in his long nights of radiation and silence,\n')
    windows_stringio_new.write('so that his eyes can’t close, for regret\n')
    windows_stringio_new.write('is like tears seeping through closed eyelids.')

    # Assert that this new buffer also implicitly converted all POSIX- to
    # Windows-style newlines in the resulting string.
    assert windows_stringio_new.getvalue() == BOOK_OF_NIGHTMARES

    # Release these buffers back to their parent pools (in acquisition order).
    key_pool.release(key='\r\n', item=windows_stringio)
    key_pool.release(key='\r\n', item=windows_stringio_new)


def test_key_pool_fail() -> None:
    '''
    Test unsuccessful usage of the
    :class:`beartype._util.cache.pool.utilcachepool.KeyPool` type.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.pool.utilcachepool import KeyPool

    # Key pool to be tested, seeding empty pools with the identity function.
    key_pool = KeyPool(item_maker=lambda key: key)

    # Assert that attempting to acquire a new object with an unhashable key
    # raises the expected exception.
    with raises(TypeError):
        key_pool.acquire(['Lieutenant!', 'This corpse will not stop burning!'])
