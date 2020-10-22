#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 544`_ **unit tests.**

This submodule unit tests `PEP 544`_ support implemented in the
:func:`beartype.beartype` decorator.

.. _PEP 544:
   https://www.python.org/dev/peps/pep-0544
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than
from pytest import raises

# ....................{ TESTS ~ type                      }....................
@skip_if_python_version_less_than('3.8.0')
def test_pep544() -> None:
    '''
    Test `PEP 544`_ support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets at least Python 3.8.0
    (i.e., the first major Python version to support `PEP 544`_) *or* skip
    otherwise.

    .. _PEP 544:
       https://www.python.org/dev/peps/pep-0544
    '''

    # Defer heavyweight imports.
    from abc import abstractmethod
    from beartype import beartype
    from typing import Protocol

    # User-defined protocol declaring arbitrary methods, but intentionally
    # *NOT* decorated by the @typing.runtime_checkable decorator and thus
    # unusable at runtime by @beartype.
    class TwoTrees(Protocol):
        def holy_tree(self) -> str:
            return 'Beloved, gaze in thine own heart,'

        @abstractmethod
        def bitter_glass(self) -> str: pass

    # User-defined class structurally (i.e., implicitly) satisfying *WITHOUT*
    # explicitly subclassing this user-defined protocol.
    class TwoTreesStructural(object):
        def holy_tree(self) -> str:
            return 'The holy tree is growing there;'

        def bitter_glass(self) -> str:
            return 'Gaze no more in the bitter glass'

    # @beartype-decorated callable annotated by this user-defined protocol.
    @beartype
    def times_of_old(god_slept: TwoTrees) -> str:
        return god_slept.holy_tree() + god_slept.bitter_glass()

    # Assert that this callable raises the expected call-time exception.
    with raises(TypeError):
        times_of_old(TwoTreesStructural())
