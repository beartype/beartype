#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **external command exit status** (i.e., integer signifying whether
a process terminated successfully or unsuccessfully) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ CONSTANTS                          }....................
SUCCESS = 0
'''
Exit status signifying a process to have terminated successfully.
'''


FAILURE_DEFAULT = 1
'''
Exit status typically signifying a process to have terminated prematurely with
a fatal error.

Although any exit status in the range ``[1, 255]`` signifies failure, this
particular exit status is the most common and thus preferred default.
'''

# ....................{ TESTERS                            }....................
def is_success(exit_status: int) -> bool:
    '''
    ``True`` only if the passed exit status signifies success.
    '''

    assert isinstance(exit_status, int), f'{exit_status} not integer.'
    return exit_status == SUCCESS


def is_failure(exit_status: int) -> bool:
    '''
    ``True`` only if the passed exit status signifies failure.
    '''

    assert isinstance(exit_status, int), f'{exit_status} not integer.'
    return exit_status != SUCCESS
