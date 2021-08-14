#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from abc import abstractmethod
from beartype.roar import BeartypeDecorHintPep544Exception
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._util.cls.utilclstest import is_type_builtin
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from beartype._util.utilobject import is_object_subclass
from typing import Any, Dict, Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ PRIVATE ~ mappings                }....................
# Conditionally initialized by the _init() function below.
_HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL: Dict[type, type] = {}
'''
Dictionary mapping from each :mod:`typing` **IO generic base class** (i.e.,
either :class:`typing.IO` itself *or* a subclass of :class:`typing.IO` defined
by the :mod:`typing` module) to the associated :mod:`beartype` **IO protocol**
(i.e., either :class:`_Pep544IO` itself *or* a subclass of :class:`_Pep544IO`
defined by this submodule).
'''

# ....................{ PRIVATE ~ classes                 }....................
# Conditionally initialized by the _init() function below.
_Pep544IO: Any = None
'''
:pep:`544`-compliant protocol base class for :class:`_Pep544TextIO` and
:class:`_Pep544BinaryIO`.

This is an abstract, generic version of the return of open().

NOTE: This does not distinguish between the different possible classes (text
vs. binary, read vs. write vs. read/write, append-only, unbuffered). The TextIO
and BinaryIO subclasses below capture the distinctions between text vs. binary,
which is pervasive in the interface; however we currently do not offer a way to
track the other distinctions in the type system.

Design
----------
This base class intentionally duplicates the contents of the existing
:class:`typing.IO` generic base class by substituting the useless
:class:`typing.Generic` superclass of the latter with the useful
:class:`typing.Protocol` superclass of the former. Why? Because *no* stdlib
classes excluding those defined by the :mod:`typing` module itself subclass
:class:`typing.IO`. However, :class:`typing.IO` leverages neither the
:class:`abc.ABCMeta` metaclass *nor* the :class:`typing.Protocol` superclass
needed to support structural subtyping. Therefore, *no* stdlib objects
(including those returned by the :func:`open` builtin) satisfy either
:class:`typing.IO` itself or any subclasses of :class:`typing.IO` (e.g.,
:class:`typing.BinaryIO`, :class:`typing.TextIO`). Therefore,
:class:`typing.IO` and all subclasses thereof are functionally useless for all
practical intents. The conventional excuse `given by Python maintainers to
justify this abhorrent nonsensicality is as follows <typeshed_>`__:

    There are a lot of "file-like" classes, and the typing IO classes are meant
    as "protocols" for general files, but they cannot actually be protocols
    because the file protocol isn't very well defined—there are lots of methods
    that exist on some but not all filelike classes.

Like most :mod:`typing`-oriented confabulation, that, of course, is bollocks.
Refactoring the family of :mod:`typing` IO classes from inveterate generics
into pragmatic protocols is both technically trivial and semantically useful,
because that is exactly what :mod:`beartype` does. It works. It necessitates
modifying three lines of existing code. It preserves backward compatibility. In
short, it should have been done a decade ago. If the file protocol "isn't very
well defined," the solution is to define that protocol with a rigorous type
hierarchy satisfying all possible edge cases. The solution is *not* to pretend
that no solutions exist, that the existing non-solution suffices, and instead
do nothing. Welcome to :mod:`typing`, where no one cares that nothing works as
advertised (or at all)... *and no one ever will.*

.. _typeshed:
   https://github.com/python/typeshed/issues/3225#issuecomment-529277448
'''


# Conditionally initialized by the _init() function below.
_Pep544BinaryIO: Any = None
'''
Typed version of the return of open() in binary mode.
'''


# Conditionally initialized by the _init() function below.
_Pep544TextIO: Any = None
'''
Typed version of the return of open() in text mode.
'''

# ....................{ TESTERS                           }....................
# If the active Python interpreter targets at least Python >= 3.8 and thus
# supports PEP 544, define these functions appropriately.
if IS_PYTHON_AT_LEAST_3_8:
    def is_hint_pep544_ignorable_or_none(
        hint: object, hint_sign: HintSign) -> Optional[bool]:

        # Return either:
        # * If this hint is the "typing.Protocol" superclass directly
        #   parametrized by one or more type variables (e.g.,
        #   "typing.Protocol[S, T]"), true. For unknown and presumably
        #   uninteresting reasons, *ALL* possible objects satisfy this
        #   superclass. Ergo, this superclass and *ALL* parametrizations of
        #   this superclass are synonymous with the "object" root superclass.
        # * Else, "None".
        return repr(hint).startswith('typing.Protocol[') or None


    def is_hint_pep484_generic_io(hint: object) -> bool:

        # Attempt to...
        try:
            # Return true only if this hint is a PEP 484-compliant IO generic
            # base class.
            return hint in _HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL
        # If this hint is unhashable, this hint is by definition *NOT* a PEP
        # 484-compliant IO generic base class. In this case, return false.
        except TypeError:
            return False


    def is_hint_pep544_protocol(hint: object) -> bool:

        # Defer version-dependent imports.
        from typing import Protocol

        # Return true only if this hint is...
        return (
            # A PEP 544-compliant protocol *AND*...
            is_object_subclass(hint, Protocol) and  # type: ignore[arg-type]
            # *NOT* a builtin type. For unknown reasons, some but *NOT* all
            # builtin types erroneously present themselves to be PEP
            # 544-compliant protocols under Python >= 3.8: e.g.,
            #     >>> from typing import Protocol
            #     >>> isinstance(str, Protocol)
            #     False        # <--- this makes sense
            #     >>> isinstance(int, Protocol)
            #     True         # <--- this makes no sense whatsoever
            #
            # Since builtin types are obviously *NOT* PEP 544-compliant
            # protocols, explicitly exclude all such types. Why, Guido? Why?
            not (isinstance(hint, type) and is_type_builtin(hint))
        )


# Else, the active Python interpreter targets at most Python < 3.8 and thus
# fails to support PEP 544. In this case, fallback to declaring this function
# to unconditionally return False.
else:
    def is_hint_pep544_ignorable_or_none(
        hint: object, hint_sign: HintSign) -> Optional[bool]:
        return None


    def is_hint_pep484_generic_io(hint: object) -> bool:
        return False


    def is_hint_pep544_protocol(hint: object) -> bool:
        return False

# ....................{ TESTERS ~ doc                     }....................
is_hint_pep544_ignorable_or_none.__doc__ = '''
    ``True`` only if the passed object is a :pep:`544`-compliant **ignorable
    type hint,** ``False`` only if this object is a :pep:`544`-compliant
    unignorable type hint, and ``None`` if this object is *not* `PEP
    544`_-compliant.

    Specifically, this tester function returns ``True`` only if this object is
    a deeply ignorable :pep:`544`-compliant type hint, including:

    * A parametrization of the :class:`typing.Protocol` abstract base class
      (ABC) by one or more type variables. As the name implies, this ABC is
      generic and thus fails to impose any meaningful constraints. Since a type
      variable in and of itself also fails to impose any meaningful
      constraints, these parametrizations are safely ignorable in all possible
      contexts: e.g.,

      .. code-block:: python

         from typing import Protocol, TypeVar
         T = TypeVar('T')
         def noop(param_hint_ignorable: Protocol[T]) -> T: pass

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as this tester is only safely callable
    by the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    hint_sign : HintSign
        **Sign** (i.e., arbitrary object uniquely identifying this hint).

    Returns
    ----------
    Optional[bool]
        Either:

        * If this object is :pep:`544`-compliant:

          * If this object is a ignorable, ``True``.
          * Else, ``False``.

        * If this object is *not* :pep:`544`-compliant, ``None``.
    '''


is_hint_pep484_generic_io.__doc__ = '''
    ``True`` only if the passed object is a functionally useless
    :pep:`484`-compliant :mod:`typing` **IO generic superclass** (i.e., either
    :class:`typing.IO` itself *or* a subclass of :class:`typing.IO` defined by
    the :mod:`typing` module effectively unusable at runtime due to botched
    implementation details) that is losslessly replaceable with a useful
    :pep:`544`-compliant :mod:`beartype` **IO protocol** (i.e., either
    :class:`beartype._data.hint.pep.proposal.datapep544._Pep544IO` itself
    *or* a subclass of that class defined by this submodule intentionally
    designed to be usable at runtime).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a :pep:`484`-compliant IO generic base
        class.

    See Also
    ----------
    :class:`beartype._data.hint.pep.proposal.datapep544._Pep544IO`
        Further commentary.
    '''


is_hint_pep544_protocol.__doc__ = '''
    ``True`` only if the passed object is a :pep:`544`-compliant **protocol**
    (i.e., subclass of the :class:`typing.Protocol` superclass).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a :pep:`544`-compliant protocol.
    '''

# ....................{ REDUCERS                          }....................
def reduce_hint_pep484_generic_io_to_pep544_protocol(hint: type) -> type:
    '''
    :pep:`544`-compliant :mod:`beartype` **IO protocol** (i.e., either
    :class:`beartype._data.hint.pep.proposal.datapep544._Pep544IO`
    itself *or* a subclass of that class defined by this submodule
    intentionally designed to be usable at runtime) corresponding to the passed
    :pep:`484`-compliant :mod:`typing` **IO generic base class** (i.e., either
    :class:`typing.IO` itself *or* a subclass of :class:`typing.IO` defined by
    the :mod:`typing` module effectively unusable at runtime due to botched
    implementation details).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : type
        :pep:`484`-compliant :mod:`typing` IO generic base class to be replaced
        by the corresponding :pep:`544`-compliant :mod:`beartype` IO protocol.

    Returns
    ----------
    Protocol
        :pep:`544`-compliant :mod:`beartype` IO protocol corresponding to this
        :pep:`484`-compliant :mod:`typing` IO generic base class.

    Raises
    ----------
    BeartypeDecorHintPep544Exception
        If this object is *not* a :pep:`484`-compliant IO generic base class.

    See Also
    ----------
    :class:`beartype._data.hint.pep.proposal.datapep544._Pep544IO`
        Further commentary.
    '''

    # If this object is *NOT* a PEP 484-compliant "typing" IO generic,
    # raise an exception.
    if not is_hint_pep484_generic_io(hint):
        raise BeartypeDecorHintPep544Exception(
            f'Type hint {repr(hint)} not '
            f'PEP 484-compliant "typing" IO generic base class '
            f'(i.e., "typing.IO", "typing.BinaryIO", or "typing.TextIO").'
        )
    # Else, this object is *NOT* a PEP 484-compliant "typing" IO generic.

    # Return the corresponding PEP 544-compliant IO protocol.
    return _HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL[hint]

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ..................{ VERSIONS                          }..................
    # If the active Python interpreter only targets Python < 3.8 and thus fails
    # to support PEP 544, silently reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_8:
        return
    # Else, the active Python interpreter targets Python >= 3.8 and thus
    # supports PEP 593.

    # ..................{ IMPORTS                           }..................
    # Defer Python version-specific imports.
    from beartype._util.hint.pep.utilpepattr import HINT_ATTR_LIST
    from typing import (
        AnyStr,
        BinaryIO,
        IO,
        Protocol,
        Union,
        TextIO,
        runtime_checkable,
    )

    # ..................{ GLOBALS                           }..................
    # Global attributes to be redefined below.
    global \
        _HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL, \
        _Pep544BinaryIO, \
        _Pep544IO, \
        _Pep544TextIO

    # ..................{ PROTOCOLS                         }..................
    @runtime_checkable
    class _Pep544IO(Protocol[AnyStr]):
        # The body of this class is copied wholesale from the existing
        # non-functional "typing.IO" class.

        __slots__: tuple = ()

        @property
        @abstractmethod
        def mode(self) -> str:
            pass

        @property
        @abstractmethod
        def name(self) -> str:
            pass

        @abstractmethod
        def close(self) -> None:
            pass

        @property
        @abstractmethod
        def closed(self) -> bool:
            pass

        @abstractmethod
        def fileno(self) -> int:
            pass

        @abstractmethod
        def flush(self) -> None:
            pass

        @abstractmethod
        def isatty(self) -> bool:
            pass

        @abstractmethod
        def read(self, n: int = -1) -> AnyStr:
            pass

        @abstractmethod
        def readable(self) -> bool:
            pass

        @abstractmethod
        def readline(self, limit: int = -1) -> AnyStr:
            pass

        @abstractmethod
        def readlines(self, hint: int = -1) -> HINT_ATTR_LIST[AnyStr]:
            pass

        @abstractmethod
        def seek(self, offset: int, whence: int = 0) -> int:
            pass

        @abstractmethod
        def seekable(self) -> bool:
            pass

        @abstractmethod
        def tell(self) -> int:
            pass

        @abstractmethod
        def truncate(self, size: Optional[int] = None) -> int:
            pass

        @abstractmethod
        def writable(self) -> bool:
            pass

        @abstractmethod
        def write(self, s: AnyStr) -> int:
            pass

        @abstractmethod
        def writelines(self, lines: HINT_ATTR_LIST[AnyStr]) -> None:
            pass

        @abstractmethod
        def __enter__(self) -> '_Pep544IO[AnyStr]':
            pass

        @abstractmethod
        def __exit__(self, cls, value, traceback) -> None:
            pass


    # Note that PEP 544 explicitly requires *ALL* protocols (including
    # protocols subclassing protocols) to explicitly subclass the "Protocol"
    # superclass, in violation of both sanity and usability. (Thanks, guys.)
    @runtime_checkable
    class _Pep544BinaryIO(_Pep544IO[bytes], Protocol):
        # The body of this class is copied wholesale from the existing
        # non-functional "typing.BinaryIO" class.

        __slots__: tuple = ()

        @abstractmethod
        def write(self, s: Union[bytes, bytearray]) -> int:
            pass

        @abstractmethod
        def __enter__(self) -> '_Pep544BinaryIO':
            pass


    # Note that PEP 544 explicitly requires *ALL* protocols (including
    # protocols subclassing protocols) to explicitly subclass the "Protocol"
    # superclass, in violation of both sanity and usability. (Thanks, guys.)
    @runtime_checkable
    class _Pep544TextIO(_Pep544IO[str], Protocol):
        # The body of this class is copied wholesale from the existing
        # non-functional "typing.TextIO" class.

        __slots__: tuple = ()

        @property
        @abstractmethod
        def buffer(self) -> _Pep544BinaryIO:
            pass

        @property
        @abstractmethod
        def encoding(self) -> str:
            pass

        @property
        @abstractmethod
        def errors(self) -> Optional[str]:
            pass

        @property
        @abstractmethod
        def line_buffering(self) -> bool:
            pass

        @property
        @abstractmethod
        def newlines(self) -> Any:
            pass

        @abstractmethod
        def __enter__(self) -> '_Pep544TextIO':
            pass

    # ..................{ MAPPINGS                          }..................
    # Dictionary mapping from each "typing" IO generic base class to the
    # associated IO protocol defined above.
    _HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL = {
        IO:       _Pep544IO,
        BinaryIO: _Pep544BinaryIO,
        TextIO:   _Pep544TextIO,
    }


# Initialize this submodule.
_init()
