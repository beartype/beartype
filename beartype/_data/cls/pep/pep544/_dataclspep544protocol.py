#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant **protocols.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Protocol  # <-- *OPTIMIZED PROTOCOL FOR VICTORY* \o/
from typing import (
    Any,
    AnyStr,
    Optional,
)

# ....................{ PROTOCOLS ~ superclass             }....................
class Pep544IOMethodsOnly(Protocol[AnyStr]):
    '''
    **Methods-only IO protocol** (i.e., useful :mod:`beartype`-specific
    :pep:`544`-compliant protocol defining *only* the abstract methods defined
    by the existing useless :mod:`beartype`-agnostic :pep:`484`-compliant
    :class:`typing.IO` generic).

    This protocol intentionally excludes *all* non-method attributes defined by
    :class:`typing.IO`. Why? Because the :func:`issubclass` builtin.
    :mod:`beartype` type-checks each :pep:`484`- or :pep:`585`-compliant
    subclass type hint (e.g., ``typing.Type[...]``, ``type[...]``)  by
    dynamically generating code passing the single child hint subscripting that
    subclass type hint as the second parameter to :func:`issubclass`. However,
    protocols defining one or more non-methods are prohibited from being passed
    as the second parameter to :func:`issubclass`. Ergo, the *only* means of
    type-checking subclass type hints of the form ``typing.Type[typing.IO]`` or
    ``type[typing.IO]`` is to internally reduce the standard :class:`typing.IO`
    generic to this non-standard protocol omitting all non-method attributes:

    .. code-block:: python

       >>> from beartype._data.hint.pep.proposal.datapep544 import IO
       >>> issubclass(object, IO)
       TypeError: Protocols with non-method members don't support issubclass().
       Non-method members: 'closed', 'mode', 'name'.

    See Also
    --------
    :class:`.IO`
        Further details.
    '''

    def close(self) -> None: ...
    def fileno(self) -> int: ...
    def flush(self) -> None: ...
    def isatty(self) -> bool: ...
    def read(self, n: int = -1) -> AnyStr: ...
    def readable(self) -> bool: ...
    def readline(self, limit: int = -1) -> AnyStr: ...
    def readlines(self, hint: int = -1) -> list[AnyStr]: ...
    def seek(self, offset: int, whence: int = 0) -> int: ...
    def seekable(self) -> bool: ...
    def tell(self) -> int: ...
    def truncate(self, size: int | None = None) -> int: ...
    def writable(self) -> bool: ...
    def write(self, s: bytes | bytearray) -> int: ...
    def writelines(self, lines: list[AnyStr]) -> None: ...

    def __enter__(self) -> 'Pep544IO[AnyStr]':  # pyright: ignore
        ...

    def __exit__(self, cls, value, traceback) -> None: ...


# Note that:
# * PEP 544 explicitly requires *ALL* protocols (including protocols subclassing
#   protocols) to explicitly subclass the "Protocol" superclass, in violation of
#   both sanity and usability. (Thanks, guys.)
# * The beartype-agnostic "typing.Protocol" superclass underlying the
#   beartype-specific "beartype.typing.Protocol" superclass implicitly requires
#   that *ALL* subscriptable protocol superclasses in a type hierarchy
#   explicitly subclass the "Protocol" superclass subscripted by the exact same
#   PEP 484-compliant type variable (e.g., "AnyStr" in this case). Why? Because
#   The "typing.Protocol" superclass is hostile to runtime usability, clearly.
#   If this arbitrary stricture is disobeyed, then *ALL* parametrized subclasses
#   of this superclass erroneously raise a "TypeError" resembling the following
#   on subclass declaration:
#       TypeError: <class 'beartype._data.hint.pep.proposal.datapep544.IO'> is
#       not a generic class
class Pep544IO(Pep544IOMethodsOnly[AnyStr], Protocol):
    '''
    :pep:`544`-compliant **IO protocol** (i.e., useful protocol copied wholesale
    from the existing useless :class:`typing.IO` generic).

    This protocol is an abstract generic version of the return of :func:`open`.

    NOTE: This does not distinguish between the different possible classes (text
    vs. binary, read vs. write vs. read/write, append-only, unbuffered). The
    :class:`typing.TextIO` and :class:`typing.BinaryIO` subclasses below capture
    the distinctions between text vs. binary, which is pervasive in the
    interface; however we currently do not offer a way to track the other
    distinctions in the type system.

    Design
    ------
    This base class intentionally duplicates the contents of the existing
    :class:`typing.IO` generic base class by substituting the useless
    :class:`typing.Generic` superclass of the latter with the useful
    :class:`typing.Protocol` superclass of the former. Why? Because *no* stdlib
    classes (excluding those defined by the :mod:`typing` module itself)
    subclass :class:`typing.IO`. However, :class:`typing.IO` leverages neither
    the :class:`abc.ABCMeta` metaclass *nor* the :class:`typing.Protocol`
    superclass needed to support structural subtyping. Therefore, *no* stdlib
    objects (including those returned by the :func:`open` builtin) satisfy
    either :class:`typing.IO` itself or any subclasses of :class:`typing.IO`
    (e.g., :class:`typing.BinaryIO`, :class:`typing.TextIO`). Therefore,
    :class:`typing.IO` and all subclasses thereof are functionally useless for
    all practical intents. The conventional excuse `given by Python maintainers
    to justify this abhorrent nonsensicality is as follows <typeshed_>`__:

        There are a lot of "file-like" classes, and the typing IO classes are
        meant as "protocols" for general files, but they cannot actually be
        protocols because the file protocol isn't very well defined—there are
        lots of methods that exist on some but not all filelike classes.

    Like most :mod:`typing`-oriented confabulation, that, of course, is
    bollocks. Refactoring the family of :mod:`typing` IO classes from inveterate
    generics into pragmatic protocols is both technically trivial and
    semantically useful, because that is exactly what :mod:`beartype` does. It
    works. It necessitates modifying three lines of existing code. It preserves
    backward compatibility. In short, it should have been done a decade ago. If
    the file protocol "isn't very well defined," the solution is to define that
    protocol with a rigorous type hierarchy satisfying all possible edge cases.
    The solution is *not* to pretend that no solutions exist, that the existing
    non-solution suffices, and instead do nothing. Welcome to :mod:`typing`,
    where no one cares that nothing works as advertised (or at all)... *and no
    one ever will.*

    .. _typeshed:
       https://github.com/python/typeshed/issues/3225#issuecomment-529277448
    '''

    @property
    def mode(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def closed(self) -> bool: ...

# ....................{ PROTOCOLS ~ subclass : text        }....................
class Pep544TextIO(Pep544IO[str], Protocol):
    '''
    :pep:`544`-compliant **text IO protocol** (i.e., :mod:`beartype-specific
    useful protocol copied wholesale from the :mod:`beartype-agnostic existing
    useless :class:`typing.TextIO` generic).

    This protocol transparently serves as:

    * A type hint matching file handles opened in text rather than binary mode.
    * A typed version of the return of the :func:`open` builtin in text mode.

    Caveats
    -------
    **This protocol is unsuitable for passing as the second parameter to the**
    :func:`issubclass` **builtin.** Moreover, the uniquely subclass-specific
    attributes required by this protocol subclass are *all* non-method
    attributes. Whereas the :func:`issubclass`-friendly
    :class:`Pep544IOMethodsOnly` superclass of the :func:`issubclass`-hostile
    :class:`.IO` superclass could be defined, *no* similar hypothetical
    :func:`issubclass`-friendly ``Pep544TextIOMethodsOnly`` superclass of this
    :func:`issubclass`-hostile protocol can be defined. That superclass would be
    empty and thus effectively useless. Ergo, the *only* means of detecting
    whether a given type satisfies this protocol is to manually introspect the
    non-method attributes of that type. Python: "Ugh."
    '''

    @property
    def buffer(self) -> 'beartype._data.cls.pep.pep544.dataclspep544.BinaryIO':  # type: ignore[name-defined]
        ...

    @property
    def encoding(self) -> str: ...

    @property
    def errors(self) -> Optional[str]: ...

    @property
    def line_buffering(self) -> bool: ...

    @property
    def newlines(self) -> Any: ...
