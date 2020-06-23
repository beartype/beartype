#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 484`_ **detection unit tests.**

This submodule unit tests `PEP 484`_ **detection support** (i.e., testing
whether arbitrary objects comply with `PEP 484`_).

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import typing

# ....................{ GLOBALS ~ typevar                 }....................
#FIXME: Test additional "typing" types.
#FIXME: Test various non-"typing" types.

T = typing.TypeVar('T')
'''
User-defined generic :mod:`typing` type variable.
'''

# ....................{ CLASSES                           }....................
class GenericUserDefined(typing.Generic[T]):
    '''
    User-defined generic :mod:`typing` type.
    '''

    pass

# ....................{ GLOBALS ~ typing                  }....................
P484_TYPES = (
    typing.Any,
    typing.Callable[[], str],
    typing.Dict[str, str],
    typing.List[float],
    typing.Tuple[str, int],
    T,
    GenericUserDefined,
)
'''
Various :mod:`typing` types of interest.
'''

# ....................{ TESTS ~ type                      }....................
def test_p484_detect() -> None:
    '''
    Test **PEP 563** (i.e., "Postponed Evaluation of Annotations") support
    implemented in the :func:`beartype.beartype` decorator if the active Python
    interpreter targets at least Python 3.7.0 (i.e., the first major Python
    version to support PEP 563) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype._decor.pep484.p484test import is_typing

    # Assert that various "typing" types are correctly detected as such.
    for p484_type in P484_TYPES:
        print('PEP 484 type: {!r}'.format(p484_type))
        assert is_typing(p484_type) is True

    # Assert that various non-"typing" types are correctly detected as such.
    # assert is_type_pep484(
