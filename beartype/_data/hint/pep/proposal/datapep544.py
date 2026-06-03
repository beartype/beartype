#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant **type hint magical data** (i.e., global
constants defining or otherwise describing :pep:`544`-compliant protocols).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import abstractmethod
from beartype._data.typing.datatyping import DictTypeToAny
from beartype._util.utilobjattr import is_object_attr_names_all

from typing import (
    Any,
    AnyStr,
    Optional,

    IO as typing_IO,  # <------------------ useless generic: *BARFING*
    BinaryIO as typing_BinaryIO,  # <------ useless generic: *GULPING*
    TextIO as typing_TextIO,  # <---------- useless generic: *OHNOES*
)
from beartype.typing import Protocol  # <-- *OPTIMIZED PROTOCOL*! \o/

# ....................{ PROTOCOLS ~ superclass             }....................
class _IOMethodsOnly(Protocol[AnyStr]):
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

    @abstractmethod
    def close(self) -> None:
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
    def readlines(self, hint: int = -1) -> list[AnyStr]:
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
    def writelines(self, lines: list[AnyStr]) -> None:
        pass

    @abstractmethod
    def __enter__(self) -> 'IO[AnyStr]':  # pyright: ignore
        pass

    @abstractmethod
    def __exit__(self, cls, value, traceback) -> None:
        pass


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
class IO(_IOMethodsOnly[AnyStr], Protocol):
    '''
    :pep:`544`-compliant **IO protocol** (i.e., useful protocol copied wholesale
    from the existing useless :class:`typing.IO` generic).

    This protocol transparently serves as:

    * A type hint matching file handles opened in either text or binary mode.
    * The abstract base class (ABC) of both the :class:`.TextIO` and
      :class:`.BinaryIO` concrete protocol subclasses.

    This is an abstract generic version of the return of :func:`open`.

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
    @abstractmethod
    def mode(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def closed(self) -> bool:
        pass

# ....................{ PROTOCOLS ~ subclass : binary      }....................
# Note that the "BinaryIO" protocol is intentionally defined *BEFORE* the
# "TextIO" protocol, whose annotations reference the "BinaryIO" protocol and
# *MUST* thus be defined last.

class _BinaryIOMeta(type):
    '''
    :pep:`3119`-compliant **binary IO pseudo-protocol metaclass** (i.e.,
    :mod:`beartype`-specific useful "mimic" protocol metaclass inverting the
    runtime behaviour of the :mod:`beartype`-specific :class:`.TextIO`
    protocol by defining the :pep:`3119`-compliant :meth:`.__instancecheck__`
    and :meth:`.__subclasscheck__` dunder methods).
    '''

    def __instancecheck__(cls: 'BinaryIO', obj: object) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed arbitrary object either:

        * Is an instance of the standard :pep:`484`-compliant
          :class:`typing.BinaryIO` type.
        * Satisfies the **binary IO pseudo-protocol** (i.e., satisfies our
          non-standard :pep:`544`-compliant :class:`.IO` protocol but *not* our
          non-standard :pep:`544`-compliant :class:`.TextIO` protocol).

        Parameters
        ----------
        obj: object
            Object to be tested.

        Returns
        -------
        bool
            :data:`True` only if this object satisfies this pseudo-protocol.
        '''

        # Return true only if either...
        return (
            # This object is an instance of the standard PEP 484-compliant
            # "typing.BinaryIO" generic *OR*...
            #
            # Note that this test is significantly faster and thus intentionally
            # performed first. It is what we say it is, @beartype! Celebrate.
            isinstance(obj, typing_BinaryIO) or
            # This object satisfies our non-standard PEP 544-compliant "IO"
            # protocol but *NOT* our non-standard PEP 544-compliant "TextIO"
            # protocol. See also their docstrings for further details.
            (
                isinstance(obj, IO) and not  # type: ignore[misc]
                isinstance(obj, TextIO)  # type: ignore[misc]
            )
        )


    def __subclasscheck__(cls: 'BinaryIO', subclass: type) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed arbitrary type either:

        * Is a subclass of the standard :pep:`484`-compliant
          :class:`typing.BinaryIO` type.
        * Satisfying the **binary IO pseudo-protocol** (i.e., satisfies our
          non-standard :pep:`544`-compliant :class:`.IO` protocol but *not* our
          non-standard :pep:`544`-compliant :class:`.TextIO` protocol).

        This dunder method is memoized for efficiency.

        Parameters
        ----------
        subclass: type
            Type to be tested.

        Returns
        -------
        bool
            :data:`True` only if this object satisfies this pseudo-protocol.

        Raises
        ------
        TypeError
            If the passed type is *not* actually a type.
        '''

        # If this type is a subclass of the standard PEP 484-compliant
        # "typing.BinaryIO" generic, return true immediately.
        #
        # Note that this test is significantly faster and thus intentionally
        # performed first. It is what we say it is, @beartype! Celebrate.
        if issubclass(subclass, typing_BinaryIO):
            return True
        # Else, this type is *NOT* a subclass of the standard PEP 484-compliant
        # "typing.BinaryIO" generic.
        #
        # If this type defines all methods required by our non-standard PEP
        # 544-compliant "IO" protocol, this type *MAY* satisfy our PEP
        # 544-compliant "BinaryIO" protocol. In this case...
        elif issubclass(subclass, _IOMethodsOnly):  # type: ignore[misc]
            # Return either:
            # * If this subclass defines *ALL* of non-method attributes required
            #   by the standard PEP 484-compliant "TextIO" generic, false. Why?
            #   A subclass that is semantically textual in nature cannot, by
            #   definition, also be semantically binary in nature.
            # * If this subclass defines less than *ALL* of those attributes,
            #   true.
            return not is_object_attr_names_all(
                obj=subclass, attr_names_all=_TEXTIO_NONMETHOD_ATTR_NAMES)
        # Else, this type fails to define all methods required by our
        # non-standard PEP 544-compliant "IO" protocol and thus *CANNOT* satisfy
        # our non-standard PEP 544-compliant "BinaryIO" protocol either.

        # Return false as a fallback.
        return False


class BinaryIO(object, metaclass=_BinaryIOMeta):
    '''
    :pep:`3119`-compliant **binary IO pseudo-protocol** (i.e.,
    :mod:`beartype`-specific useful "mimic" protocol inverting the runtime
    behaviour of the :mod:`beartype`-specific :class:`.TextIO` protocol).

    This pseudo-protocol transparently serves as:

    * A type hint matching file handles opened in binary rather than text mode.
    * A typed version of the return of the :func:`open` builtin in binary mode.

    Motivation
    ----------
    This pseudo-protocol matches the abstract :class:`typing.IO` protocol ABC
    but *not* the concrete :class:`typing.TextIO` subprotocol subclassing that
    ABC. Whereas the concrete :class:`typing.TextIO` subprotocol unambiguously
    matches *only* file handles opened in text mode, the concrete
    :class:`typing.BinaryIO` subprotocol ambiguously matches file handles opened
    in both text *and* binary mode. As the following hypothetical
    :class:`BinaryIO` subclass demonstrates, the :class:`typing.IO` and
    :class:`typing.BinaryIO` APIs are identical except for method annotations:

    .. code-block:: python

       class BinaryIO(IO[bytes], Protocol):
           # The body of this class is copied wholesale from the existing
           # non-functional "typing.BinaryIO" class.

           __slots__: tuple = ()

           @abstractmethod
           def write(self, s: Union[bytes, bytearray]) -> int:
               pass

           @abstractmethod
           def __enter__(self) -> 'BinaryIO':
               pass

    Sadly, the method annotations that differ between these APIs are
    insufficient to disambiguate file handles at runtime. Why? Because most
    file handles are C-based and thus lack *ANY* annotations whatsoever. With
    respect to C-based file handles, these APIs are therefore identical.
    Ergo, the :class:`typing.BinaryIO` subprotocol is mostly useless at runtime.

    Note, however, that file handles are necessarily *always* opened in either
    text or binary mode. This strict dichotomy implies that any file handle
    (i.e., object matching the :class:`typing.IO` protocol) *not* opened in text
    mode (i.e., not matching the :class:`typing.TextIO` protocol) must
    necessarily be opened in binary mode instead.
    '''


# ....................{ PROTOCOLS ~ subclass : text        }....................
class TextIO(IO[str], Protocol):
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
    attributes. Whereas the :func:`issubclass`-friendly :class:`_IOMethodsOnly`
    superclass of the :func:`issubclass`-hostile :class:`.IO` superclass could
    be defined, *no* similar :func:`issubclass`-friendly ``_TextIOMethodsOnly``
    superclass of this :func:`issubclass`-hostile protocol can be defined. That
    superclass would be empty and thus effectively useless. Ergo, the *only*
    means of detecting whether a given type satisfies this protocol is to
    manually introspect the non-method attributes of that type. Python: "Ugh."
    '''

    @property
    @abstractmethod
    def buffer(self) -> BinaryIO:  # pyright: ignore
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

# ....................{ MAPPINGS                           }....................
HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL: DictTypeToAny = {
    # Unsubscripted mappings.
    typing_IO:        IO,
    typing_BinaryIO:  BinaryIO,
    typing_TextIO:    TextIO,

    # Subscripted mappings, leveraging the useful observation that these
    # classes all self-cache by design: e.g.,
    #     >>> import typing
    #     >>> typing.IO[str] is typing.IO[str]
    #     True
    #
    # Note that we intentionally map:
    # * "IO[Any]" to the unsubscripted "IO" rather than the
    #   subscripted "IO[Any]". Although the two are semantically
    #   equivalent, the latter is marginally more space- and time-efficient
    #   to generate code for and thus preferable.
    # * "IO[bytes]" to the unsubscripted "_Pep544Binary" rather than the
    #   subscripted "IO[bytes]". Why? Because the former applies
    #   meaningful runtime constraints, whereas the latter does *NOT*.
    # * "IO[str]" to the unsubscripted "_Pep544Text" rather than the
    #   subscripted "IO[str]" -- for the same reason.
    #
    # Note that we intentionally avoid mapping parametrizations of "IO" by
    # type variables. Since there exist a countably infinite number of
    # such parametrizations, the parent
    # reduce_hint_pep484_generic_io_to_pep544_protocol() function calling
    # this function handles such parametrizations mostly intelligently.
    typing_IO[Any]:   IO,
    typing_IO[bytes]: BinaryIO,
    typing_IO[str]:   TextIO,
}
'''
Frozen dictionary mapping from each :mod:`typing` **IO generic base class**
(i.e., either :class:`typing.IO` itself *or* a subclass of :class:`typing.IO`
defined by the :mod:`typing` module) to the associated :mod:`beartype` **IO
protocol** (i.e., either :class:`.IO` itself *or* a subclass of :class:`.IO`
defined by this submodule).

Note that this dictionary is intentionally left mutable (rather than coerced
into immutability by instantiating the :mod:`beartype`-specific type
:class:`beartype._util.kind.maplike.utilmapfrozen.FrozenDict` instead). Why?
Because external callables (e.g., the
:func:`beartype._check.convert._reduce._pep.redpep544.reduce_hint_pep484_generic_io_to_pep544_protocol`)
efficiently memoize themselves by caching into this dictionary. Just accept it.
'''

# ....................{ PRIVATE ~ sets                     }....................
_TEXTIO_NONMETHOD_ATTR_NAMES = frozenset((
    'encoding',
    'errors',
    'line_buffering',
    'newlines',
))
'''
Frozen set of the names of all non-method attributes (which, sadly, is literally
*all* of them) required by the :class:`.TextIO` protocol.

Caveats
-------
This set intentionally excludes the ``buffer`` non-method attribute required by
the standard :pep:`484`-compliant :class:`typing.TextIO` generic and thus our .
non-standard :pep:`544`-compliant :class:`.TextIO` protocol. Why? Because
real-world standard types that otherwise satisfy this protocol (e.g.,
:class:`io.StringIO`) fail to define this attribute as a class variable: e.g.,

.. code-block:: pycon

   # Prove that "io.StringIO" fails to define the "buffer" non-method attribute
   # as either a class or instance variable.
   >>> dir(StringIO)
   dir(StringIO): ['__class__', '__del__', '__delattr__', '__dict__', '__dir__',
   '__doc__', '__enter__', '__eq__', '__exit__', '__format__', '__ge__',
   '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__',
   '__init_subclass__', '__iter__', '__le__', '__lt__', '__module__', '__ne__',
   '__new__', '__next__', '__reduce__', '__reduce_ex__', '__repr__',
   '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__',
   '_checkClosed', '_checkReadable', '_checkSeekable', '_checkWritable',
   'close', 'closed', 'detach', 'encoding', 'errors', 'fileno', 'flush',
   'getvalue', 'isatty', 'line_buffering', 'newlines', 'read', 'readable',
   'readline', 'readlines', 'seek', 'seekable', 'tell', 'truncate', 'writable',
   'write', 'writelines'] # <-- no "buffer", huh? le sigh
   >>> StringIO().buffer
   AttributeError: '_io.StringIO' object has no attribute 'buffer'
   # ^--- still no "buffer", huh? more le sigh

Including this attribute in this set would thus induce :mod:`beartype` to
erroneously return false negatives for common use cases. Indeed, the standard
:class:`io.TextIOBase` superclass of :class:`io.StringIO` explicitly documents
that this attribute is only conditionally defined even as an instance variable:

    buffer
        The underlying binary buffer (a BufferedIOBase or RawIOBase instance)
        that TextIOBase deals with. This is not part of the TextIOBase API and
        may not exist in some implementations.
'''
