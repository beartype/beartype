#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **platform tester** (i.e., functions detecting the current
platform the active Python interpreter is running under) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.cache.utilcachecall import callable_cached
from platform import system as platform_system
# from sys import platform as sys_platform

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
@callable_cached
def is_os_macos() -> bool:
    '''
    ``True`` only if the current platform is **Apple macOS**, the operating
    system previously known as "OS X."

    This tester is memoized for efficiency.
    '''

    return platform_system() == 'Darwin'


#FIXME: Uncomment if we ever want this.
# @callable_cached
# def is_os_windows_vanilla() -> bool:
#     '''
#     ``True`` only if the current platform is **vanilla Microsoft Windows**
#     (i.e., *not* running the Cygwin POSIX compatibility layer).
#
#     This tester is memoized for efficiency.
#     '''
#
#     return sys_platform == 'win32'
