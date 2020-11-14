#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Hear beartype tests roar** as they handle errors and warnings.

This submodule defines hierarchies of :mod:`beartype_test`-specific exceptions
and warnings emitted by unit and functional tests and fixtures.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from abc import ABCMeta as _ABCMeta
from beartype.roar import BeartypeException

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SUPERCLASS                        }....................
class BeartypeTestException(BeartypeException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype test exceptions.**

    Instances of subclasses of this exception are raised at test time from
    :mod:`beartype_test`-specific unit and functional tests and fixtures.
    '''

    pass

# ....................{ MARK                              }....................
class BeartypeTestMarkException(BeartypeTestException):
    '''
    **Beartype test mark exceptions.**

    This exception is raised at test time from decorators defined by the
    :mod:`beartype_test.util.mark` submodule.
    '''

    pass
