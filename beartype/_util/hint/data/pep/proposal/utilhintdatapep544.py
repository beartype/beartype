#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype `PEP 544`_**-compliant type hint data.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 544:
    https://www.python.org/dev/peps/pep-0544
'''

# ....................{ IMPORTS                           }....................
from abc import abstractmethod
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES                           }....................
# Conditionally initialized by the add_data() function below.
_Pep544IO = None
'''
`PEP 544`_-compliant protocol base class for :class:`_Pep544TextIO` and
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

.. _PEP 544:
   https://www.python.org/dev/peps/pep-0544
.. _typeshed:
   https://github.com/python/typeshed/issues/3225#issuecomment-529277448
'''


# Conditionally initialized by the add_data() function below.
_Pep544BinaryIO = None
'''
Typed version of the return of open() in binary mode.
'''


# Conditionally initialized by the add_data() function below.
_Pep544TextIO = None
'''
Typed version of the return of open() in text mode.
'''

# ....................{ MAPPINGS                          }....................
_HINT_PEP544_IO_GENERIC_TO_PROTOCOL = {}
'''
Dictionary mapping from each :mod:`typing` **IO generic base class** (i.e.,
either :class:`typing.IO` itself *or* a subclass of :class:`typing.IO` defined
by the :mod:`typing` module) to the associated :mod:`beartype` **IO protocol**
(i.e., either :class:`_Pep544IO` itself *or* a subclass of :class:`_Pep544IO`
defined by this submodule).
'''

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 544`_**-compliant type hint data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 544:
        https://www.python.org/dev/peps/pep-0544
    '''

    # If the active Python interpreter does *NOT* target at least Python >= 3.8
    # and thus fails to support PEP 544, silently reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_8:
        return
    # Else, the active Python interpreter targets at least Python >= 3.9 and
    # thus supports PEP 593.

    # Defer Python version-specific imports.
    from typing import (
        Any,
        AnyStr,
        BinaryIO,
        IO,
        List,
        Optional,
        Protocol,
        Union,
        TextIO,
        runtime_checkable,
    )

    # Global classes to be redefined below.
    global \
        _HINT_PEP544_IO_GENERIC_TO_PROTOCOL, \
        _Pep544BinaryIO, \
        _Pep544IO, \
        _Pep544TextIO

    # ..................{ PROTOCOLS                         }..................
    @runtime_checkable
    class _Pep544IO(Protocol[AnyStr]):
        # The body of this class is copied wholesale from the existing
        # non-functional "typing.IO" class.

        __slots__ = ()

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
        def readlines(self, hint: int = -1) -> List[AnyStr]:
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
        def truncate(self, size: int = None) -> int:
            pass

        @abstractmethod
        def writable(self) -> bool:
            pass

        @abstractmethod
        def write(self, s: AnyStr) -> int:
            pass

        @abstractmethod
        def writelines(self, lines: List[AnyStr]) -> None:
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

        __slots__ = ()

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

        __slots__ = ()

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
    _HINT_PEP544_IO_GENERIC_TO_PROTOCOL = {
        IO:       _Pep544IO,
        BinaryIO: _Pep544BinaryIO,
        TextIO:   _Pep544TextIO,
    }

    # ..................{ SETS                              }..................
    # Register the version-specific signs introduced in this version.
    #
    # Note that ignoring the "typing.Protocol" superclass is vital here. For
    # unknown and presumably uninteresting reasons, *ALL* possible objects
    # satisfy this superclass. Ergo, this superclass is synonymous with the
    # "object" root superclass: e.g.,
    #     >>> import typing as t
    #     >>> isinstance(object(), t.Protocol)
    #     True
    #     >>> isinstance('ok', t.Protocol)
    #     True
    #     >>> isinstance(3333, t.Protocol)
    #     True
    data_module.HINT_PEP_SIGNS_SUPPORTED_DEEP.add(Protocol)
    data_module.HINT_PEP_SIGNS_IGNORABLE.add(Protocol)
