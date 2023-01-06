#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**:mod:`pytest` context manager utilities.**
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTERS                            }....................
def is_ci() -> bool:
    '''
    ``True`` only if the active Python process is running under a remote
    continuous integration (CI) workflow.
    '''

    # One-liners for a brighter, bolder, better future... today.
    return is_ci_github_actions()


def is_ci_github_actions() -> bool:
    '''
    ``True`` only if the active Python process is running under a GitHub
    Actions-based continuous integration (CI) workflow.
    '''

    # Defer test-specific imports.
    from os import environ

    # Return true only if the current shell environment declares a GitHub
    # Actions-specific environment variable.
    return 'GITHUB_ACTIONS' in environ
