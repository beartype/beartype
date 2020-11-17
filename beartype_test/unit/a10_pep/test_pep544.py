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

# ....................{ TESTS                             }....................
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

# ....................{ TESTS ~ callable                  }....................
def test_is_hint_pep484_generic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.utilhintpep544.is_hint_pep484_generic`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.proposal.utilhintpep544 import (
        is_hint_pep544_io_generic)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from typing import BinaryIO, IO, TextIO, Union

    # Set of all PEP 484-compliant "typing" IO generic base classes.
    TYPING_IO_GENERICS = {BinaryIO, IO, TextIO}

    for typing_io_generic in TYPING_IO_GENERICS:
        # Assert this function accepts these classes *ONLY* if the active
        # Python interpreter targets at least Python >= 3.8 and thus supports
        # PEP 544.
        assert is_hint_pep544_io_generic(typing_io_generic) is (
            IS_PYTHON_AT_LEAST_3_8)

    # Assert this function rejects standard type hints in either case.
    assert is_hint_pep544_io_generic(Union[int, str]) is False


def test_is_hint_pep544_io_generic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.utilhintpep544.is_hint_pep544_io_generic`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.proposal.utilhintpep544 import (
        is_hint_pep544_io_generic)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from typing import BinaryIO, IO, TextIO, Union

    # Set of all PEP 484-compliant "typing" IO generic base classes.
    TYPING_IO_GENERICS = {BinaryIO, IO, TextIO}

    for typing_io_generic in TYPING_IO_GENERICS:
        # Assert this function accepts these classes *ONLY* if the active
        # Python interpreter targets at least Python >= 3.8 and thus supports
        # PEP 544.
        assert is_hint_pep544_io_generic(typing_io_generic) is (
            IS_PYTHON_AT_LEAST_3_8)

    # Assert this function rejects standard type hints in either case.
    assert is_hint_pep544_io_generic(Union[int, str]) is False


def test_get_hint_pep544_io_protocol_from_generic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.utilhintpep544.get_hint_pep544_io_protocol_from_generic`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPep544Exception
    from beartype._util.hint.pep.proposal.utilhintpep544 import (
        get_hint_pep544_io_protocol_from_generic)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from beartype._util.utilobject import is_object_subclass
    from typing import BinaryIO, IO, TextIO, Union

    # Set of all PEP 484-compliant "typing" IO generic base classes.
    TYPING_IO_GENERICS = {BinaryIO, IO, TextIO}

    for typing_io_generic in TYPING_IO_GENERICS:
        # If the active Python interpreter targets at least Python >= 3.8 and
        # thus supports PEP 544...
        if IS_PYTHON_AT_LEAST_3_8:
            # Defer version-dependent imports.
            from typing import Protocol

            # Beartype-specific PEP 544-compliant protocol implementing this
            # PEP 484-compliant "typing" IO generic base class.
            io_protocol = get_hint_pep544_io_protocol_from_generic(
                typing_io_generic)

            # Assert this function returns a protocol.
            assert is_object_subclass(io_protocol, Protocol)
        # Else, assert this function raises an exception.
        else:
            with raises(BeartypeDecorHintPep544Exception):
                get_hint_pep544_io_protocol_from_generic(typing_io_generic)

    # Assert this function rejects standard type hints in either case.
    with raises(BeartypeDecorHintPep544Exception):
        get_hint_pep544_io_protocol_from_generic(Union[int, str])
