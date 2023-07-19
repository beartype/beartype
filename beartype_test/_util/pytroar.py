#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Hear beartype tests roar** as it handles errors and warnings.

This submodule defines hierarchies of :mod:`beartype_test`-specific exceptions
and warnings emitted by unit and functional tests and fixtures.
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
from beartype._data.hint.datahinttyping import TypeException
from contextlib import contextmanager
from pytest import raises

# ....................{ CONTEXTS                           }....................
@contextmanager
def raises_uncached(exception_cls: TypeException) -> 'ExceptionInfo':
    '''
    Context manager validating that the block exercised by this manager raises
    a **cached exception** (i.e., whose message previously containing one or
    more instances of the magic
    :data:`beartype._util.error.utilerror.EXCEPTION_PLACEHOLDER`
    substring since replaced by the
    :func:`beartype._util.error.utilerror.reraise_exception_placeholder`
    function) of the passed type.

    Parameters
    ----------
    exception_cls : str
        Type of cached exception expected to be raised by this block.

    Returns
    ----------
    :class:`pytest.nodes.ExceptionInfo`
        :mod:`pytest`-specific object collecting metadata on the cached
        exception of this type raised by this block.

    See Also
    ----------
    https://docs.pytest.org/en/stable/reference.html#pytest._code.ExceptionInfo
        Official :class:`pytest.nodes.ExceptionInfo` documentation.
    '''

    # Defer test-specific imports.
    from beartype._util.error.utilerror import (
        EXCEPTION_PLACEHOLDER)

    # Within a "pytest"-specific context manager validating this contextual
    # block to raise an exception of this type, perform the body of that block.
    with raises(exception_cls) as exception_info:
        yield exception_info

    # Exception message raised by the body of that block.
    exception_message = str(exception_info.value)

    # Assert this exception message does *NOT* contain this magic substring.
    assert EXCEPTION_PLACEHOLDER not in exception_message

    #FIXME: Inadvisable in the general case, but preserved for posterity.
    # Assert this exception message does *NOT* contain two concurrent spaces,
    # implying an upstream failure in substring concatenation.
    # assert '  ' not in exception_message

# ....................{ SUPERCLASS                         }....................
class BeartypeTestException(BeartypeException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype test exceptions.**

    Instances of subclasses of this exception are raised at test time from
    :mod:`beartype_test`-specific unit and functional tests and fixtures.
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
