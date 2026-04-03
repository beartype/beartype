#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Hear beartype tests roar** as it handles errors and warnings.

This submodule defines hierarchies of :mod:`beartype_test`-specific exceptions
and warnings emitted by unit and integration tests and fixtures.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from abc import ABCMeta as _ABCMeta
from beartype.roar import BeartypeException

# ....................{ SUPERCLASS                         }....................
class BeartypeTestException(BeartypeException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype test exceptions.**

    Instances of subclasses of this exception are raised at test time from
    :mod:`beartype_test`-specific unit and integration tests and fixtures.
    '''

    pass


class BeartypeTestPathException(BeartypeTestException):
    '''
    **Beartype test path exception.**

    This exception is raised at test time from callables and classes defined by
    the :mod:`beartype_test._util.path` subpackage.
    '''

    pass



class BeartypeTestMarkException(BeartypeTestException):
    '''
    **Beartype test mark exception.**

    This exception is raised at test time from decorators defined by the
    :mod:`beartype_test._util.mark` subpackage.
    '''

    pass
