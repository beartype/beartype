#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type-checkers.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Split this into multiple submodules to avoid the usual accidental
#exportation-of-imports API quandary. *sigh*

# ....................{ IMPORTS                           }....................
from beartype import beartype
from beartype.roar import BeartypeCallHintPepReturnException

# ....................{ VALIDATORS                        }....................
#FIXME: Implement us up, please.
#FIXME: Unit test us up, please.
#FIXME: Document us up, please.
#def die_if_bearable(obj, annotation):

# ....................{ TESTERS                           }....................
#FIXME: Unit test us up, please.
#FIXME: Document us up, please.
#FIXME: Optimize us up, please. See this discussion for voluminous details:
#    https://github.com/beartype/beartype/issues/87#issuecomment-1020856517
def is_bearable(obj, annotation):
    @beartype
    def _is_bearable_slow(o) -> annotation:
        return o

    try:
        _is_bearable_slow(obj)
        return True
    except BeartypeCallHintPepReturnException as exc:
        pass

    return False
