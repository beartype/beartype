#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
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
def test_pep544_pass() -> None:
    '''
    Test successful usage of `PEP 544`_ support implemented in the
    :func:`beartype.beartype` decorator if the active Python interpreter
    targets at least Python 3.8.0 (i.e., the first major Python version to
    support `PEP 544`_) *or* skip otherwise.

    .. _PEP 544:
       https://www.python.org/dev/peps/pep-0544
    '''

    # Defer heavyweight imports.
    from abc import abstractmethod
    from beartype import beartype
    from typing import Protocol, runtime_checkable

    # User-defined runtime protocol declaring arbitrary methods.
    @runtime_checkable
    class Easter1916(Protocol):
        def i_have_met_them_at_close_of_day(self) -> str:
            return 'Coming with vivid faces'

        @abstractmethod
        def from_counter_or_desk_among_grey(self) -> str: pass

    # User-defined class structurally (i.e., implicitly) satisfying *WITHOUT*
    # explicitly subclassing this user-defined protocol.
    class Easter1916Structural(object):
        def i_have_met_them_at_close_of_day(self) -> str:
            return 'Eighteenth-century houses.'

        def from_counter_or_desk_among_grey(self) -> str:
            return 'I have passed with a nod of the head'

    # @beartype-decorated callable annotated by this user-defined protocol.
    @beartype
    def or_polite_meaningless_words(lingered_awhile: Easter1916) -> str:
        return (
            lingered_awhile.i_have_met_them_at_close_of_day() +
            lingered_awhile.from_counter_or_desk_among_grey()
        )

    # Assert this callable returns the expected string when passed this
    # user-defined class structurally satisfying this protocol.
    assert or_polite_meaningless_words(Easter1916Structural()) == (
        'Eighteenth-century houses.'
        'I have passed with a nod of the head'
    )


@skip_if_python_version_less_than('3.8.0')
def test_pep544_fail() -> None:
    '''
    Test unsuccessful usage of `PEP 544`_ support implemented in the
    :func:`beartype.beartype` decorator if the active Python interpreter
    targets at least Python 3.8.0 (i.e., the first major Python version to
    support `PEP 544`_) *or* skip otherwise.

    .. _PEP 544:
       https://www.python.org/dev/peps/pep-0544
    '''

    # Defer heavyweight imports.
    from abc import abstractmethod
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep3119Exception
    from typing import Protocol

    # User-defined protocol declaring arbitrary methods, but intentionally
    # *NOT* decorated by the @typing.runtime_checkable decorator and thus
    # unusable at runtime by @beartype.
    class TwoTrees(Protocol):
        def holy_tree(self) -> str:
            return 'Beloved, gaze in thine own heart,'

        @abstractmethod
        def bitter_glass(self) -> str: pass

    # @beartype-decorated callable annotated by this user-defined protocol.
    with raises(BeartypeDecorHintPep3119Exception):
        @beartype
        def times_of_old(god_slept: TwoTrees) -> str:
            return god_slept.holy_tree() + god_slept.bitter_glass()

# ....................{ TESTS ~ protocol                  }....................
def test_is_hint_pep544_protocol() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.utilhintpep544.is_hint_pep544_protocol`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.proposal.utilhintpep544 import (
        is_hint_pep544_protocol)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from beartype_test.a00_unit.data.data_type import CLASSES_BUILTIN
    from typing import (
        SupportsAbs,
        SupportsBytes,
        SupportsComplex,
        SupportsFloat,
        SupportsInt,
        SupportsRound,
        Union,
    )

    # Set of all PEP 544-compliant "typing" protocols.
    TYPING_PROTOCOLS = {
        SupportsAbs,
        SupportsBytes,
        SupportsComplex,
        SupportsFloat,
        SupportsInt,
        SupportsRound,
    }

    # Assert this tester accepts these classes *ONLY* if the active Python
    # interpreter targets at least Python >= 3.8 and thus supports PEP 544.
    for typing_protocol in TYPING_PROTOCOLS:
        assert is_hint_pep544_protocol(typing_protocol) is (
            IS_PYTHON_AT_LEAST_3_8)

    # Assert this tester rejects all builtin types. For unknown reasons, some
    # but *NOT* all builtin types (e.g., "int") erroneously present themselves
    # to be PEP 544-compliant protocols. *sigh*
    for class_builtin in CLASSES_BUILTIN:
        assert is_hint_pep544_protocol(class_builtin) is False

    # Assert this tester rejects standard type hints in either case.
    assert is_hint_pep544_protocol(Union[int, str]) is False

# ....................{ TESTS ~ io generic                }....................
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

    # Assert this tester accepts these classes *ONLY* if the active Python
    # interpreter targets at least Python >= 3.8 and thus supports PEP 544.
    for typing_io_generic in TYPING_IO_GENERICS:
        assert is_hint_pep544_io_generic(typing_io_generic) is (
            IS_PYTHON_AT_LEAST_3_8)

    # Assert this tester rejects standard type hints in either case.
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
