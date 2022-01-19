#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator cache** (i.e., singleton dictionary mapping from each
beartype configuration to the corresponding configured beartype decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
# from beartype.roar import BeartypeCallHintForwardRefException,
from beartype.typing import Dict
from beartype._data.datatyping import BeartypeConfedDecorator
from beartype._decor.conf import BeartypeConf

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SINGLETONS                        }....................
bear_conf_to_decor: Dict[BeartypeConf, BeartypeConfedDecorator] = {}
'''
Non-thread-safe **beartype decorator cache.**

This cache is implemented as a singleton dictionary mapping from each
**beartype configuration** (i.e., self-caching dataclass encapsulating all
flags, options, settings, and other metadata configuring the current decoration
of the decorated callable or class) to the corresponding **configured beartype
decorator** (i.e., closure created and returned from the
:func:`beartype.beartype` decorator when passed a beartype configuration via
the optional ``conf`` parameter rather than an object to be decorated via
the optional ``obj`` parameter).

Caveats
----------
**This cache is not thread-safe.** Although rendering this cache thread-safe
would be trivial, doing so would needlessly reduce efficiency. This cache is
merely a runtime optimization and thus need *not* be thread-safe.
'''
