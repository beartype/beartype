#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import abstractmethod
from beartype.roar import BeartypeDecorHintPep544Exception
from beartype.typing import (
    Any,
    BinaryIO,
    Dict,
    IO,
    Optional,
    TextIO,
)
from beartype._data.cls.datacls import TYPES_PEP484_GENERIC_IO
from beartype._util.cls.utilclstest import is_type_builtin_or_fake
from typing import Protocol as typing_Protocol  # <-- unoptimized protocol

# ....................{ TESTERS                            }....................
def is_hint_pep484_generic_io(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a functionally useless
    :pep:`484`-compliant :mod:`typing` **IO generic superclass** (i.e., either
    :class:`typing.IO` itself *or* a subclass of :class:`typing.IO` defined by
    the :mod:`typing` module effectively unusable at runtime due to botched
    implementation details) that is losslessly replaceable with a useful
    :pep:`544`-compliant :mod:`beartype` **IO protocol** (i.e., either
    :class:`_Pep544IO` itself *or* a subclass of that class defined by this
    submodule intentionally designed to be usable at runtime).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`484`-compliant IO generic
        base class.

    See Also
    --------
    :class:`_Pep544IO`
        Further commentary.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_origin_type_or_none)

    # Type originating this hint, defined as Either:
    # * If this hint defines the "__origin__" dunder attribute...
    #   * Whose value is a type, that type (which is then said to "originate"
    #     this hint).
    #   * Whose value is *not* a type but this hint is a type, this hint itself
    #     (which is then said to "originate" itself).
    # * In all other cases, "None".
    hint_origin = get_hint_pep_origin_type_or_none(
        hint=hint, is_self_fallback=True)

    # Return true only if this originating type is either:
    # * An unsubscripted PEP 484-compliant IO generic base class
    #   (e.g., "typing.IO") *OR*....
    # * A subscripted PEP 484-compliant IO generic base class
    #   (e.g., "typing.IO[str]").
    return hint_origin in TYPES_PEP484_GENERIC_IO


def is_hint_pep544_protocol(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a :pep:`544`-compliant
    **protocol** (i.e., subclass of the :class:`typing.Protocol` superclass).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`544`-compliant protocol.
    '''

    # Return true only if this hint is...
    return (
        # A type *AND*...
        isinstance(hint, type) and
        # A PEP 544-compliant protocol *AND*...
        issubclass(hint, typing_Protocol) and  # type: ignore[arg-type]
        # *NOT* a builtin type. For unknown reasons, some but *NOT* all
        # builtin types erroneously present themselves to be PEP
        # 544-compliant protocols under Python >= 3.8: e.g.,
        #     >>> from typing import Protocol
        #     >>> issubclass(str, Protocol)
        #     False        # <--- this makes sense
        #     >>> issubclass(int, Protocol)
        #     True         # <--- this makes no sense whatsoever
        #
        # Since builtin types are obviously *NOT* PEP 544-compliant
        # protocols, explicitly exclude all such types. Why, Guido? Why?
        #
        # Do *NOT* ignore fake builtins for the purposes of this test. Why?
        # Because even fake builtins (e.g., "type(None)") erroneously
        # masquerade as PEP 544-compliant protocols! :o
        not is_type_builtin_or_fake(hint)  # pyright: ignore
    )

# ....................{ REDUCERS                           }....................
def reduce_hint_pep484_generic_io_to_pep544_protocol(
    hint: Any, exception_prefix: str) -> Any:
    '''
    :pep:`544`-compliant :mod:`beartype` **IO protocol** (i.e., either
    :class:`._Pep544IO` itself *or* a subclass of that class defined by this
    submodule intentionally designed to be usable at runtime) corresponding to
    the passed :pep:`484`-compliant :mod:`typing` **IO generic base class**
    (i.e., either :class:`typing.IO` itself *or* a subclass of
    :class:`typing.IO` defined by the :mod:`typing` module effectively unusable
    at runtime due to botched implementation details).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner thanks to caching internally performed by this
    reducer.

    Parameters
    ----------
    hint : type
        :pep:`484`-compliant :mod:`typing` IO generic base class to be replaced
        by the corresponding :pep:`544`-compliant :mod:`beartype` IO protocol.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    -------
    Protocol
        :pep:`544`-compliant :mod:`beartype` IO protocol corresponding to this
        :pep:`484`-compliant :mod:`typing` IO generic base class.

    Raises
    ------
    BeartypeDecorHintPep544Exception
        If this object is *not* a :pep:`484`-compliant IO generic base class.
    '''

    # If this object is *NOT* a PEP 484-compliant "typing" IO generic,
    # raise an exception.
    if not is_hint_pep484_generic_io(hint):
        raise BeartypeDecorHintPep544Exception(
            f'{exception_prefix}type hint {repr(hint)} not '
            f'PEP 484 IO generic base class '
            f'(i.e., "typing.IO", "typing.BinaryIO", or "typing.TextIO").'
        )
    # Else, this object is *NOT* a PEP 484-compliant "typing" IO generic.
    #
    # If this dictionary has yet to be initialized, this submodule has yet to be
    # initialized. In this case, do so.
    #
    # Note that this initialization is intentionally deferred until required.
    # Why? Because this initialization performs somewhat space- and
    # time-intensive work -- including importation of the "beartype.vale"
    # subpackage, which we strictly prohibit importing from global scope.
    elif not _HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL:
        _init()
    # In any case, this dictionary is now initialized.

    # PEP 544-compliant IO protocol implementing this PEP 484-compliant IO
    # generic if any *OR* "None" otherwise.
    pep544_protocol = _HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL.get(hint)

    # If *NO* PEP 544-compliant IO protocol implements this generic...
    if pep544_protocol is None:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.utilpepget import (
            get_hint_pep_origin_or_none,
            get_hint_pep_typevars,
        )

        # Tuple of zero or more type variables parametrizing this hint.
        hint_typevars = get_hint_pep_typevars(hint)

        #FIXME: Unit test us up, please.
        # If this hint is unparametrized, raise an exception.
        if not hint_typevars:
            raise BeartypeDecorHintPep544Exception(
                f'{exception_prefix}PEP 484 IO generic base class '
                f'{repr(hint)} invalid (i.e., not subscripted (indexed) by '
                f'either "str", "bytes", "typing.Any", or "typing.AnyStr").'
            )
        # Else, this hint is parametrized and thus defines the "__origin__"
        # dunder attribute whose value is the type originating this hint.

        #FIXME: Attempt to actually handle this type variable, please.
        # Reduce this parametrized hint (e.g., "typing.IO[typing.AnyStr]") to
        # the equivalent unparametrized hint (e.g., "typing.IO"), effectively
        # ignoring the type variable parametrizing this hint.
        hint_unparametrized: type = get_hint_pep_origin_or_none(hint)  # type: ignore[assignment]

        # PEP 544-compliant IO protocol implementing this unparametrized PEP
        # 484-compliant IO generic. For efficiency, we additionally cache this
        # mapping under the original parametrized hint to minimize the cost of
        # similar reductions under subsequent annotations.
        pep544_protocol = \
            _HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL[hint] = \
            _HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL[hint_unparametrized]
    # Else, some PEP 544-compliant IO protocol implements this generic.

    # Return this protocol.
    return pep544_protocol

# ....................{ PRIVATE ~ mappings                 }....................
# Conditionally initialized by the _init() function below.
_HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL: Dict[type, Any] = {}
'''
Dictionary mapping from each :mod:`typing` **IO generic base class** (i.e.,
either :class:`typing.IO` itself *or* a subclass of :class:`typing.IO` defined
by the :mod:`typing` module) to the associated :mod:`beartype` **IO protocol**
(i.e., either :class:`_Pep544IO` itself *or* a subclass of :class:`_Pep544IO`
defined by this submodule).
'''

# ....................{ PRIVATE ~ classes                  }....................
# Conditionally initialized by the _init() function below.
_Pep544IO: Any = None  # type: ignore[assignment]
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
------
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
_Pep544BinaryIO: Any = None  # type: ignore[assignment]
'''
Typed version of the return of :func:`open` in binary mode.
'''


# Conditionally initialized by the _init() function below.
_Pep544TextIO: Any = None  # type: ignore[assignment]
'''
Typed version of the return of :func:`open` in text mode.
'''

# ....................{ INITIALIZERS                       }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer function-specific imports.
    from beartype.typing import (
        Annotated,
        AnyStr,
        List,
        Protocol,
    )
    from beartype.vale import IsInstance

    # ..................{ GLOBALS                            }..................
    # Global attributes to be redefined below.
    global \
        _Pep544BinaryIO, \
        _Pep544IO, \
        _Pep544TextIO

    # ..................{ PROTOCOLS ~ protocol               }..................
    #FIXME: Declare these protocols at global scope, please.
    # PEP-compliant type hint matching file handles opened in either text or
    # binary mode.
    # @runtime_checkable
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
        def truncate(self, size: Optional[int] = None) -> int:
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
        def __enter__(self) -> '_Pep544IO[AnyStr]':  # pyright: ignore
            pass

        @abstractmethod
        def __exit__(self, cls, value, traceback) -> None:
            pass


    # PEP-compliant type hint matching file handles opened in text rather than
    # binary mode.
    #
    # Note that PEP 544 explicitly requires *ALL* protocols (including
    # protocols subclassing protocols) to explicitly subclass the "Protocol"
    # superclass, in violation of both sanity and usability. (Thanks, guys.)
    # @runtime_checkable
    class _Pep544TextIO(_Pep544IO[str], Protocol):
        # The body of this class is copied wholesale from the existing
        # non-functional "typing.TextIO" class.

        __slots__: tuple = ()

        @property
        @abstractmethod
        def buffer(self) -> _Pep544BinaryIO:  # pyright: ignore
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
        def __enter__(self) -> '_Pep544TextIO':  # pyright: ignore
            pass

    # ..................{ PROTOCOLS ~ validator              }..................
    # PEP-compliant type hint matching file handles opened in binary rather
    # than text mode. Specifically, this hint matches the abstract "typing.IO"
    # protocol ABC but *NOT* the concrete "typing.TextIO" subprotocol
    # subclassing that ABC. Whereas the concrete "typing.TextIO" subprotocol
    # unambiguously matches *ONLY* file handles opened in text mode, the
    # concrete "typing.BinaryIO" subprotocol ambiguously matches file handles
    # opened in both text *AND* binary mode. As the following hypothetical
    # "_Pep544BinaryIO" subclass demonstrates, the "typing.IO" and
    # "typing.BinaryIO" APIs are identical except for method annotations:
    #     class _Pep544BinaryIO(_Pep544IO[bytes], Protocol):
    #         # The body of this class is copied wholesale from the existing
    #         # non-functional "typing.BinaryIO" class.
    #
    #         __slots__: tuple = ()
    #
    #         @abstractmethod
    #         def write(self, s: Union[bytes, bytearray]) -> int:
    #             pass
    #
    #         @abstractmethod
    #         def __enter__(self) -> '_Pep544BinaryIO':
    #             pass
    #
    # Sadly, the method annotations that differ between these APIs are
    # insufficient to disambiguate file handles at runtime. Why? Because most
    # file handles are C-based and thus lack *ANY* annotations whatsoever. With
    # respect to C-based file handles, these APIs are therefore identical.
    # Ergo, the "typing.BinaryIO" subprotocol is mostly useless at runtime.
    #
    # Note, however, that file handles are necessarily *ALWAYS* opened in either
    # text or binary mode. This strict dichotomy implies that any file handle
    # (i.e., object matching the "typing.IO" protocol) *NOT* opened in text mode
    # (i.e., not matching the "typing.TextIO" protocol) must necessarily be
    # opened in binary mode instead.
    _Pep544BinaryIO = Annotated[_Pep544IO, ~IsInstance[_Pep544TextIO]]

    # ..................{ MAPPINGS                           }..................
    # Dictionary mapping from each "typing" IO generic base class to the
    # associated IO protocol defined above.
    #
    # Note this global is intentionally modified in-place rather than
    # reassigned to a new dictionary. Why? Because the higher-level
    # reduce_hint_pep484_generic_io_to_pep544_protocol() function calling this
    # lower-level initializer has already imported this global.
    _HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL.update({
        # Unsubscripted mappings.
        IO:        _Pep544IO,
        BinaryIO:  _Pep544BinaryIO,
        TextIO:    _Pep544TextIO,

        # Subscripted mappings, leveraging the useful observation that these
        # classes all self-cache by design: e.g.,
        #     >>> import typing
        #     >>> typing.IO[str] is typing.IO[str]
        #     True
        #
        # Note that we intentionally map:
        # * "IO[Any]" to the unsubscripted "_Pep544IO" rather than the
        #   subscripted "_Pep544IO[Any]". Although the two are semantically
        #   equivalent, the latter is marginally more space- and time-efficient
        #   to generate code for and thus preferable.
        # * "IO[bytes]" to the unsubscripted "_Pep544Binary" rather than the
        #   subscripted "_Pep544IO[bytes]". Why? Because the former applies
        #   meaningful runtime constraints, whereas the latter does *NOT*.
        # * "IO[str]" to the unsubscripted "_Pep544Text" rather than the
        #   subscripted "_Pep544IO[str]" -- for the same reason.
        #
        # Note that we intentionally avoid mapping parametrizations of "IO" by
        # type variables. Since there exist a countably infinite number of
        # such parametrizations, the parent
        # reduce_hint_pep484_generic_io_to_pep544_protocol() function calling
        # this function handles such parametrizations mostly intelligently.
        IO[Any]:   _Pep544IO,
        IO[bytes]: _Pep544BinaryIO,
        IO[str]:   _Pep544TextIO,
    })
