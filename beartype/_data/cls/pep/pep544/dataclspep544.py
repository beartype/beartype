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
from beartype._data.cls.pep.pep544._dataclspep544protocol import (
    Pep544IOMethodsOnly,
    Pep544IO,
    Pep544TextIO,
)
from beartype._data.typing.datatyping import (
    DictTypeToAny,
    TupleTypes,
)
from beartype._util.utilobjattr import is_object_attr_names_all

from typing import (
    Any,

    IO as typing_IO,  # <------------------ useless generic: *BARFING*
    BinaryIO as typing_BinaryIO,  # <------ useless generic: *GULPING*
    TextIO as typing_TextIO,  # <---------- useless generic: *OHNOES*
)

# ....................{ CLASSES ~ io                       }....................
class _IOMeta(type):
    '''
    :pep:`3119`-compliant **data-agnostic IO pseudo-protocol metaclass**
    enabling structural runtime type-checking of the :mod:`beartype`-specific
    :class:`.IO` protocol defined below, by defining the :pep:`3119`-compliant
    :meth:`.__instancecheck__` and :meth:`.__subclasscheck__` dunder methods.
    '''

    def __instancecheck__(cls: 'IO', obj: object) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed arbitrary object either:

        * Is an instance of the standard :pep:`484`-compliant :class:`typing.IO`
          type.
        * Satisfies the **data-agnostic IO protocol** (i.e., satisfies our
          non-standard :pep:`544`-compliant :class:`.Pep544IO` protocol).

        Parameters
        ----------
        obj: object
            Object to be tested.

        Returns
        -------
        bool
            :data:`True` only if this object satisfies this pseudo-protocol.
        '''

        # Return true if this object is an instance of any instance-oriented
        # "IO" superclass.
        return isinstance(obj, _IO_TYPES_INSTANCE)


    def __subclasscheck__(cls: 'IO', subclass: type) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed arbitrary type either:

        * Is a subclass of the standard :pep:`484`-compliant :class:`typing.IO`
          type.
        * Satisfying the **data-agnostic IO protocol** (i.e., satisfies our
          non-standard :pep:`544`-compliant :class:`.Pep544IO` protocol).

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

        # Return true only if either...
        return (
            # This type is a subclass of the standard PEP 484-compliant
            # "typing.IO" generic *OR*...
            #
            # Note that this test is significantly faster and thus intentionally
            # performed first. It is what we say it is, @beartype! Celebrate.
            issubclass(subclass, typing_IO) or
            (
                # This type defines all methods required by our non-standard PEP
                # 544-compliant "IO" protocol (and thus *MAY* satisfy our PEP
                # 544-compliant "IO" protocol) *AND*...
                #
                # Note that this test is somewhat faster and thus intentionally
                # performed first. It is what we say it is, @beartype! Yo, yo.
                issubclass(subclass, Pep544IOMethodsOnly) and  # type: ignore[misc]
                # This type defines *ALL* of the properties required by the
                # standard PEP 484-compliant "IO" generic.
                is_object_attr_names_all(
                    obj=subclass, attr_names_all=_IO_PROPERTY_NAMES)
            )
        )


#FIXME: Unit test us up, please. *sigh*
class IO(object, metaclass=_IOMeta):
    '''
    :pep:`3119`-compliant **data-agnostic IO pseudo-protocol** (i.e.,
    :mod:`beartype`-specific useful "mimic" protocol generalizing the
    :mod:`beartype`-agnostic useless :pep:`484`-compliant :class:`typing.IO`
    generic superclass with support for structural runtime type-checking).

    This pseudo-protocol transparently serves as:

    * A :pep:`3119`-compliant type hint matching file handles opened in either
      text or binary mode, typically via a call to the :func:`open` builtin.
    * The abstract base class (ABC) of the data-specific
      :class:`beartype._data.cls.pep.pep544.dataclspep544.BinaryIO` and
      :class:`beartype._data.cls.pep.pep544.dataclspep544.TextIO` protocol
      subclasses.
    '''

    pass

# ....................{ CLASSES ~ io : binary              }....................
class _BinaryIOMeta(type):
    '''
    :pep:`3119`-compliant **binary IO pseudo-protocol metaclass** enabling
    structural runtime type-checking of the :mod:`beartype`-specific
    :class:`.BinaryIO` protocol defined below, by defining the
    :pep:`3119`-compliant :meth:`.__instancecheck__` and
    :meth:`.__subclasscheck__` dunder methods.
    '''

    def __instancecheck__(cls: 'BinaryIO', obj: object) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed arbitrary object either:

        * Is an instance of the standard :pep:`484`-compliant
          :class:`typing.BinaryIO` type.
        * Satisfies the **binary IO pseudo-protocol** (i.e., satisfies our
          non-standard :pep:`544`-compliant :class:`.Pep544IO` protocol but
          *not* our non-standard :pep:`544`-compliant :class:`.Pep544TextIO`
          protocol).

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
            (
                # This object satisfies our non-standard PEP 544-compliant
                # "BinaryIO" protocol by defining all methods *AND* non-method
                # attributes (e.g., properties) required by this protocol
                # *AND*...
                isinstance(obj, Pep544IO) and  # type: ignore[misc]
                # This object does *NOT* satisfy our non-standard PEP
                # 544-compliant "TextIO" protocol *AND*...
                #
                # Note that these isinstance() tests are somewhat faster and
                # thus intentionally performed first. It is what we say it is!
                not isinstance(obj, Pep544TextIO) and  # type: ignore[misc]
                # The POSIX-compliant mode string with which this object was
                # initially opened contains the character "b", implying this
                # object to have been opened in binary rather than text mode.
                # See also the official documentation of the open() builtin:
                #     https://docs.python.org/3/library/functions.html#open
                'b' in obj.mode
            )
        )


    def __subclasscheck__(cls: 'BinaryIO', subclass: type) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed arbitrary type either:

        * Is a subclass of the standard :pep:`484`-compliant
          :class:`typing.BinaryIO` type.
        * Satisfying the **binary IO pseudo-protocol** (i.e., satisfies our
          non-standard :pep:`544`-compliant :class:`.Pep544IO` protocol but
          *not* our non-standard :pep:`544`-compliant :class:`.Pep544TextIO`
          protocol).

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
        elif issubclass(subclass, Pep544IOMethodsOnly):  # type: ignore[misc]
            # List of the names of *ALL* attributes bound to this type.
            subclass_dir = dir(subclass)
            # print(f'subclass_dir: {subclass_dir}')

            # Return true only if...
            return (
                # This type define *ALL* of the properties required by the
                # standard PEP 484-compliant "IO" generic superclass *AND*...
                is_object_attr_names_all(
                    obj=subclass,
                    obj_dir=subclass_dir,
                    attr_names_all=_IO_PROPERTY_NAMES,
                ) and
                # This type does *NOT* define *ALL* of the properties required
                # by the standard PEP 484-compliant "TextIO" generic. Why?
                # Suppose this type defines *ALL* of these properties. Then this
                # type would necessarily be semantically textual in nature and
                # thus *NOT*, by definition, semantically binary in nature.
                # Conversely, if this type defines less than *ALL* of these
                # properties, this type *CANNOT* be semantically textual in
                # nature. However, by the prior check, this type defines *ALL*
                # of the properties required by the standard PEP 484-compliant
                # "IO" generic and is thus a valid "IO" type, which *MUST* be
                # either semantically textual or binary in nature. It follows
                # that, since this type is *NOT* textual, it *MUST* be binary.
                not is_object_attr_names_all(
                    obj=subclass,
                    obj_dir=subclass_dir,
                    attr_names_all=_TEXTIO_PROPERTY_NAMES,
                )
            )
        # Else, this type fails to define all methods required by our
        # non-standard PEP 544-compliant "IO" protocol and thus *CANNOT* satisfy
        # our non-standard PEP 544-compliant "BinaryIO" protocol either.

        # Return false as a fallback.
        return False


class BinaryIO(object, metaclass=_BinaryIOMeta):
    '''
    :pep:`3119`-compliant **binary IO pseudo-protocol** (i.e.,
    :mod:`beartype`-specific useful "mimic" protocol inverting the runtime
    behaviour of the :mod:`beartype`-specific :class:`.Pep544TextIO` protocol).

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
    in both text *and* binary mode. As the following hypothetical ``BinaryIO``
    subclass demonstrates, the :class:`typing.IO` and :class:`typing.BinaryIO`
    APIs are identical except for method annotations:

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
    file handles are C-based and thus lack *any* annotations whatsoever. With
    respect to C-based file handles, these APIs are therefore identical.
    Ergo, the :class:`typing.BinaryIO` subprotocol is mostly useless at runtime.

    Note, however, that file handles are necessarily *always* opened in either
    text or binary mode. This strict dichotomy implies that any file handle
    (i.e., object matching the :class:`typing.IO` protocol) *not* opened in text
    mode (i.e., not matching the :class:`typing.TextIO` protocol) must
    necessarily be opened in binary mode instead.
    '''

    pass

# ....................{ CLASSES ~ io : textio              }....................
class _TextIOMeta(type):
    '''
    :pep:`3119`-compliant **text IO pseudo-protocol metaclass** enabling
    structural runtime type-checking of the :mod:`beartype`-specific
    :class:`.TextIO` protocol defined below, by defining the
    :pep:`3119`-compliant :meth:`.__instancecheck__` and
    :meth:`.__subclasscheck__` dunder methods.
    '''

    def __instancecheck__(cls: 'TextIO', obj: object) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed arbitrary object either:

        * Is an instance of the standard :pep:`484`-compliant
          :class:`typing.TextIO` type.
        * Satisfies the **text IO protocol** (i.e., satisfies our non-standard
          :pep:`544`-compliant :class:`.Pep544TextIO` protocol.

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
            # "typing.TextIO" generic *OR*...
            #
            # Note that this test is significantly faster and thus intentionally
            # performed first. It is what we say it is, @beartype! Celebrate.
            isinstance(obj, typing_TextIO) or
            (
                # This object satisfies our non-standard PEP 544-compliant
                # "TextIO" protocol by defining all methods *AND* non-method
                # attributes (e.g., properties) required by this protocol
                # *AND*...
                #
                # Note that this test is somewhat faster and thus intentionally
                # performed first. It is what we say it is, @beartype! Ugh.
                isinstance(obj, Pep544IO) and  # type: ignore[misc]
                # The POSIX-compliant mode string with which this object was
                # initially opened does *NOT* contain the character "b" (which
                # would imply this object to have been opened in binary rather
                # than text mode). By default, POSIX-compliant files (and thus
                # Python's POSIX-compliant open() builtin) open in text mode. A
                # POSIX-compliant mode string *NOT* containing the character "b"
                # thus implies this object to have been opened in text mode.
                # See also the official documentation of the open() builtin:
                #     https://docs.python.org/3/library/functions.html#open
                'b' not in obj.mode
            )
        )


    def __subclasscheck__(cls: 'TextIO', subclass: type) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed arbitrary type either:

        * Is a subclass of the standard :pep:`484`-compliant
          :class:`typing.TextIO` type.
        * Satisfying the **text IO protocol** (i.e., satisfies our non-standard
          :pep:`544`-compliant :class:`.Pep544TextIO` protocol).

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

        # Return true only if either...
        return (
            # This type is a subclass of the standard PEP 484-compliant
            # "typing.TextIO" generic *OR*...
            #
            # Note that this test is significantly faster and thus intentionally
            # performed first. It is what we say it is, @beartype! Celebrate.
            issubclass(subclass, typing_TextIO) or
            (
                # This type defines all methods required by our non-standard PEP
                # 544-compliant "IO" protocol (and thus *MAY* satisfy our PEP
                # 544-compliant "TextIO" protocol) *AND*...
                #
                # Note that this test is somewhat faster and thus intentionally
                # performed first. It is what we say it is, @beartype! Yo, yo.
                issubclass(subclass, Pep544IOMethodsOnly) and  # type: ignore[misc]
                # This type defines *ALL* of the properties required by both the
                # standard PEP 484-compliant "IO" *AND* "TextIO" generics.
                is_object_attr_names_all(
                    obj=subclass, attr_names_all=_IO_TEXTIO_PROPERTY_NAMES)
            )
        )


class TextIO(object, metaclass=_TextIOMeta):
    '''
    :pep:`3119`-compliant **text IO pseudo-protocol** (i.e.,
    :mod:`beartype`-specific useful "mimic" protocol inverting the runtime
    behaviour of the :mod:`beartype`-specific :class:`.Pep544TextIO` protocol).

    This pseudo-protocol transparently serves as:

    * A type hint matching file handles opened in text rather than binary mode.
    * A typed version of the return of the :func:`open` builtin in text mode.
    '''

    pass

# ....................{ MAPPINGS                           }....................
HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL: DictTypeToAny = {
    # Unsubscripted mappings.
    typing_IO:        IO,
    typing_BinaryIO:  BinaryIO,
    typing_TextIO:    TextIO,

    # Subscripted mappings, leveraging the useful observation that these types
    # all self-cache by design: e.g.,
    #     >>> import typing
    #     >>> typing.IO[str] is typing.IO[str]
    #     True
    #
    # Note that:
    # * We intentionally map:
    #   * "IO[Any]" to our unsubscripted "IO" protocol rather than a subscripted
    #     "IO[Any]" protocol. Although the two are semantically equivalent, the
    #     latter is marginally more space- and time-efficient to generate code
    #     for and thus preferable.
    #   * "IO[bytes]" to our unsubscripted "BinaryIO" protocol rather than our
    #     subscripted "IO[bytes]" protocol. Why? Because the former applies
    #     meaningful runtime constraints, whereas the latter does *NOT*.
    #   * "IO[str]" to our unsubscripted "TextIO" protocol rather than our
    #     subscripted "IO[str]" protocol (for the exact same reason).
    # * We intentionally avoid attempting to map parametrizations of "IO" by
    #   arbitrary other type variables. Since there exist a countably infinite
    #   number of such parametrizations, the parent
    #   reduce_hint_pep484_generic_io_to_pep544_protocol() function calling this
    #   function handles such parametrizations mostly intelligently.
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

# ....................{ PRIVATE ~ tuples : io              }....................
# Any object structurally satisfies the "IO" protocol and is thus a structural
# "IO" instance if that object either...
_IO_TYPES_INSTANCE: TupleTypes = (
    # Is an instance of the standard PEP 484-compliant "typing.IO" generic
    # *OR*...
    #
    # Note that this test is significantly faster and thus intentionally
    # performed first. It is what we say it is, @beartype! Celebrate.
    typing_IO,
    # Defines all methods *AND* non-method attributes (e.g., properties)
    # required by our non-standard PEP 544-compliant "IO" protocol.
    Pep544IO,
)
'''
Tuple of all **instance-oriented data-agnostic IO classes** (i.e., types such
that any object that is an instance of one or more of these types structurally
satisfies the :class:`.IO` protocol and is thus a structural :class:`.IO`
instance).
'''

# ....................{ PRIVATE ~ sets                     }....................
_IO_PROPERTY_NAMES = frozenset(('mode', 'closed',))
'''
Frozen set of the names of all properties directly required by our non-standard
:pep:`544`-compliant :class:`.IO` protocol.

Caveats
-------
This set intentionally excludes the ``name`` instance variable required by
the standard :pep:`484`-compliant :class:`typing.IO` generic and thus our
non-standard :pep:`544`-compliant :class:`.IO` protocol. Why? Because
real-world standard types that otherwise satisfy this protocol (e.g.,
:class:`io.FileIO`) fail to define this variable as a class variable: e.g.,

.. code-block:: pycon

   # Prove that "io.FileIO" fails to define the "name" non-method attribute as a
   # class variable.
   >>> from io import FileIO
   >>> dir(FileIO)
   ['__class__', '__del__', '__delattr__', '__dict__', '__dir__', '__doc__',
   '__enter__', '__eq__', '__exit__', '__format__', '__ge__',
   '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__',
   '__init_subclass__', '__iter__', '__le__', '__lt__', '__module__', '__ne__',
   '__new__', '__next__', '__reduce__', '__reduce_ex__', '__repr__',
   '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '_blksize',
   '_checkClosed', '_checkReadable', '_checkSeekable', '_checkWritable',
   '_dealloc_warn', '_finalizing', '_isatty_open_only', 'close', 'closed',
   'closefd', 'fileno', 'flush', 'isatty', 'mode', 'read', 'readable',
   'readall', 'readinto', 'readline', 'readlines', 'seek', 'seekable', 'tell',
   'truncate', 'writable', 'write', 'writelines']  # <-- no "name"!? wtf python
   >>> FileIO('/dev/null').name
   '/dev/null'  # <-- welp alrighty then

Including this variable in this set would thus induce :mod:`beartype` to
erroneously return false negatives for common use cases.
'''

# ....................{ PRIVATE ~ sets : textio            }....................
_TEXTIO_PROPERTY_NAMES = frozenset((
    'encoding',
    'errors',
    'line_buffering',
    'newlines',
))
'''
Frozen set of the names of all properties (which, sadly, is literally *all* of
them) directly required by our non-standard :pep:`544`-compliant
:class:`.TextIO` protocol.

Caveats
-------
This set intentionally excludes the ``buffer`` instance variable required by
the standard :pep:`484`-compliant :class:`typing.TextIO` generic and thus our
non-standard :pep:`544`-compliant :class:`.TextIO` protocol. Why? Because
real-world standard types that otherwise satisfy this protocol (e.g.,
:class:`io.StringIO`) fail to define this variable as a class variable: e.g.,

.. code-block:: pycon

   # Prove that "io.StringIO" fails to define the "buffer" non-method attribute
   # as either a class or instance variable.
   >>> from io import StringIO
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

Including this variable in this set would thus induce :mod:`beartype` to
erroneously return false negatives for common use cases. Indeed, the standard
:class:`io.TextIOBase` superclass of :class:`io.StringIO` explicitly documents
that this variable is only conditionally defined even as an instance variable:

    buffer
        The underlying binary buffer (a BufferedIOBase or RawIOBase instance)
        that TextIOBase deals with. This is not part of the TextIOBase API and
        may not exist in some implementations.
'''


_IO_TEXTIO_PROPERTY_NAMES = _IO_PROPERTY_NAMES | _TEXTIO_PROPERTY_NAMES
'''
Frozen set of the names of all properties (which, sadly, is literally *all* of
them) directly required by both our non-standard :pep:`544`-compliant
:class:`.IO` *and* :class:`.TextIO` protocols.

This set thus encompasses the names of all properties transitively required by
our :class:`.TextIO` protocol, which quietly inherits additional properties from
the :class:`.IO` superclass it subclasses.
'''
