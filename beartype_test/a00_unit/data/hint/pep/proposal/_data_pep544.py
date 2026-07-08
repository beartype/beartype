#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant **type hint test data.**
'''

# ....................{ TODO                               }....................
#FIXME: Test user-defined multiple-inherited protocols (i.e., user-defined
#classes directly subclassing the "typing.Protocol" ABC and one or more other
#superclasses) once @beartype supports these protocols as well.

# ....................{ FIXTURES                           }....................
def hints_pep544_meta() -> (
    'list[beartype_test.a00_unit.data.hint.metadata.pith.data_hintpithmeta.HintPepMetadata]'):
    '''
    List of :pep:`544`-compliant **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.metadata.pith.data_hintpithmeta.HintPepMetadata`
    instances describing test-specific :pep:`544`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from abc import (
        ABC,
        abstractmethod,
    )
    from beartype._data.hint.sign.datahintsigns import (
        HintSignBinaryIO,
        HintSignPep484585GenericSubbed,
        HintSignPep484585GenericUnsubbed,
        HintSignTextIO,
        HintSignType,
    )
    from beartype._util.api.standard.utiltyping import get_typing_attrs
    from beartype_test.a00_unit.data.hint.metadata.pith.data_hintmeta import (
        HintPepMetadata)
    from beartype_test.a00_unit.data.hint.metadata.pith.data_pithmeta import (
        PithSatisfiedMetadata,
        PithUnsatisfiedMetadata,
    )
    from beartype_test.a00_unit.data.pep.pep484.data_pep484 import T
    from io import (
        BytesIO,
        FileIO,
        StringIO,
    )
    from pathlib import Path
    from typing import (
        Any,
        AnyStr,
        BinaryIO,
        TextIO,
        runtime_checkable,
    )

    # ..................{ LOCALS                             }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_piths_pep_meta = []

    # Absolute filename of this data submodule, to be subsequently opened for
    # cross-platform IO testing purposes.
    SUBMODULE_FILENAME = __file__

    # ..................{ FACTORIES ~ binary                 }..................
    def open_binary_bytesio() -> BytesIO:
        '''
        Factory returning an open read-only quasi-file handle in binary mode via
        the standard C-based :class:`io.BytesIO` type.
        '''

        return BytesIO()


    def open_binary_file() -> BinaryIO:
        '''
        Factory returning an open read-only file handle in binary mode via the
        :func:`open` builtin.
        '''

        return open(SUBMODULE_FILENAME, 'rb')


    def open_binary_fileio() -> BinaryIO:
        '''
        Factory returning an open read-only file handle in binary mode via the
        standard C-based :class:`io.FileIO` type.
        '''

        return FileIO(SUBMODULE_FILENAME, 'rb')

    # ..................{ FACTORIES ~ text                   }..................
    def open_text_file() -> TextIO:
        '''
        Factory returning an open read-only file handle in text mode via the
        :func:`open` builtin.
        '''

        return open(SUBMODULE_FILENAME, 'r', encoding='utf8')


    def open_text_stringio() -> StringIO:
        '''
        Factory returning an open read-only quasi-file handle in text mode via
        the standard C-based :class:`io.StringIO` type.
        '''

        return StringIO()

    # ..................{ GENERICS                           }..................
    class BinaryIOFile(BinaryIO):
        '''
        Useful concrete subclass of the mostly useless standard pure-Python
        :pep:`484`-compliant :class:`typing.BinaryIO` generic, implementing all
        abstract methods and properties defined by the latter in terms of the
        standard C-based :class:`io.FileIO` type.

        Attributes
        ----------
        _file_io : FileIO
            :class:`io.FileIO` object underlying this concrete implementation.
        '''

        def __init__(self, *args, **kwargs) -> None:
            '''
            Initialize this object by passing all parameters as is to the
            :meth:`FileIO.__init__` constructor.
            '''

            # Note that this instance variable is currently intentionally left
            # undefined (to avoid unnecessary complications with respect to
            # open file handles left unclosed).

            # # Object to which this concrete subclass proxies *ALL* logic. \o/
            # self._file_io = FileIO(*args, **kwargs)

        @property
        def mode(self) -> str:
            return self._file_io.mode

        @property
        def name(self) -> str:
            return self._file_io.name

        def close(self) -> None:
            return self._file_io.close()

        @property
        def closed(self) -> bool:
            return self._file_io.closed

        def fileno(self) -> int:
            return self._file_io.fileno()

        def flush(self) -> None:
            return self._file_io.flush()

        def isatty(self) -> bool:
            return self._file_io.isatty()

        def read(self, n: int = -1) -> AnyStr:
            return self._file_io.read(n)

        def readable(self) -> bool:
            return self._file_io.readable()

        def readline(self, limit: int = -1) -> AnyStr:
            return self._file_io.readline(limit)

        def readlines(self, hint: int = -1) -> list[AnyStr]:
            return self._file_io.readlines(hint)

        def seek(self, offset: int, whence: int = 0) -> int:
            return self._file_io.seek(offset, whence)

        def seekable(self) -> bool:
            return self._file_io.seekable()

        def tell(self) -> int:
            return self._file_io.tell()

        def truncate(self, size: int | None = None) -> int:
            return self._file_io.truncate(size)

        def writable(self) -> bool:
            return self._file_io.writable()

        def write(self, s: bytes | bytearray) -> int:
            return self._file_io.write(s)

        def writelines(self, lines: list[AnyStr]) -> None:
            return self._file_io.writelines(lines)

        # Note that the following context manager-specific methods are currently
        # intentionally left as noops (to avoid issues inside our test
        # automation, which does actually invoke these methods).
        def __enter__(self) -> BinaryIO:
            # return self._file_io.__enter__()
            return self  # <-- pretend this makes sense

        def __exit__(self, cls, value, traceback) -> None:
            # return self._file_io.__exit__(cls, value, traceback)
            pass


    class TextIOConcrete(TextIO):
        '''
        Concrete subclass of the mostly useless standard pure-Python
        :pep:`484`-compliant :class:`typing.TextIO` abstract generic.

        This subclass is useless in practice and thus *only* defined to
        superficially test that :mod:`beartype` handles this abstract generic in
        the expected manner. Since there exists *no* existing type in Python's
        standard library that could be used to trivially implement this abstract
        generic, this concrete subclass trivially defines all abstract methods
        and properties defined by :class:`typing.TextIO` to be empty noops.
        '''

        @property
        def mode(self) -> str:
            pass

        @property
        def name(self) -> str:
            pass

        def close(self) -> None: ...

        @property
        def closed(self) -> bool:
            pass

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

        # Note that the following context manager-specific methods are currently
        # intentionally left as noops (to avoid issues inside our test
        # automation, which does actually invoke these methods).
        def __enter__(self) -> TextIO:
            return self  # <-- pretend this makes sense

        def __exit__(self, cls, value, traceback) -> None: ...

        @property
        def buffer(self) -> BinaryIO:
            pass

        @property
        def encoding(self) -> str:
            pass

        @property
        def errors(self) -> str | None:
            pass

        @property
        def line_buffering(self) -> bool:
            pass

        @property
        def newlines(self) -> Any:
            pass

    # ..................{ INSTANCES                          }..................
    # Instance of the concrete "BinaryIO" subclass defined above, referring to
    # this submodule itself. Note that it probably does *not* matter. We never
    # actually call methods on this instance and thus *never* open this
    # submodule via this instance.
    binary_io_file = BinaryIOFile(SUBMODULE_FILENAME)

    # Instance of the concrete "TextIO" subclass defined above. Note that we
    # never actually call methods on this instance and thus *never* open this
    # submodule via this instance.
    text_io_concrete = TextIOConcrete()

    # ..................{ TUPLES                             }..................
    # Tuple of one or more "PithUnsatisfiedMetadata" instances validating
    # objects either satisfying or violating either "typing.BinaryIO" *OR* its
    # subscripted alias "typing.IO[bytes]".
    PITHS_META_BINARYIO = (
        # Instance of the concrete "BinaryIOFile" subclass defined above.
        PithSatisfiedMetadata(binary_io_file),
        # Open read-only binary file handle instantiated by the open() builtin.
        PithSatisfiedMetadata(pith=open_binary_file, is_pith_factory=True),
        # Open read-only binary file handle instantiated by the standard C-based
        # "io.FileIO" type.
        PithSatisfiedMetadata(pith=open_binary_fileio, is_pith_factory=True),

        # Bytestring constant.
        PithUnsatisfiedMetadata(b"Of a thieved imagination's reveries"),
        # Instance of the concrete "TextIOConcrete" subclass defined above.
        PithUnsatisfiedMetadata(text_io_concrete),
        # Open read-only text file handle instantiated by the open() builtin.
        # This validation requires dynamism and thus either beartype-specific
        # validators *OR* beartype-agnostic PEP 3119-compliant metaclasses
        # defining the __instancecheck__() dunder method, as the only means of
        # differentiating objects satisfying the "typing.BinaryIO" protocol from
        # those satisfying the "typing.IO" protocol is with an inverted instance
        # check. Guess which beartype now prefers? *sigh*
        PithUnsatisfiedMetadata(pith=open_text_file, is_pith_factory=True),
        # Unrelated C-based "io.BytesIO" object, which *ALMOST* satisfies the
        # PEP 544-compliant protocol implied by the "BinaryIO" generic. Notably,
        # "io.BytesIO" fails to define *ANY* of the properties required by that
        # protocol (e.g., "closed", "mode", "name").
        PithUnsatisfiedMetadata(pith=open_binary_bytesio, is_pith_factory=True),
        # Unrelated C-based "io.StringIO" object, which *ALMOST* satisfies the
        # PEP 544-compliant protocol implied by the "TextIO" generic while
        # obviously violating that implied by the "BinaryIO" generic. Is
        # everybody suitably confused yet? *lengthy sighing is heard*
        PithUnsatisfiedMetadata(pith=open_text_stringio, is_pith_factory=True),
    )

    #FIXME: Use us up below, please. *sigh*
    # Tuple of one or more "PithUnsatisfiedMetadata" instances validating
    # objects either satisfying or violating either "typing.TextIO" *OR* its
    # subscripted alias "typing.IO[str]".
    PITHS_META_TEXTIO = (
        # Instance of the concrete "TextIO" subclass defined above.
        PithSatisfiedMetadata(text_io_concrete),
        # Open read-only text file handle instantiated by the open() builtin.
        PithSatisfiedMetadata(pith=open_text_file, is_pith_factory=True),

        # String constant.
        PithUnsatisfiedMetadata('Statistician’s anthemed meme athame'),
        # Instance of the concrete "BinaryIO" subclass defined above.
        PithUnsatisfiedMetadata(binary_io_file),
        # Open read-only binary file handle instantiated by the open() builtin.
        PithUnsatisfiedMetadata(pith=open_binary_file, is_pith_factory=True),
        # Unrelated C-based "io.BytesIO" object, which *ALMOST* satisfies the
        # PEP 544-compliant protocol implied by the "BinaryIO" generic. Notably,
        # "io.BytesIO" fails to define *ANY* of the properties required by that
        # protocol (e.g., "closed", "mode", "name").
        PithUnsatisfiedMetadata(pith=open_binary_bytesio, is_pith_factory=True),
        # Unrelated C-based "io.StringIO" object, which *ALMOST* satisfies the
        # PEP 544-compliant protocol implied by the "TextIO" generic. Notably,
        # "io.StringIO" fails to define *ANY* of the file-oriented properties
        # required by that protocol (e.g., "closed", "mode", "name").
        PithUnsatisfiedMetadata(pith=open_text_stringio, is_pith_factory=True),
    )

    # ..................{ PROTOCOLS ~ structural             }..................
    class ProtocolCustomStructural(object):
        '''
        Arbitrary user-defined class structurally (i.e., implicitly) satisfying
        *without* explicitly subclassing both the :pep:`544`-compliant
        :class:`.ProtocolCustomUntypevared` *and*
        :class:`.ProtocolCustomTypevared` protocols defined below.
        '''

        def alpha(self) -> str:
            '''
            Arbitrary instance method required by these protocols.
            '''

            return "Sufferance's humus excursion, humility’s endurance, an"


        def omega(self) -> str:
            '''
            Arbitrary instance method required by these protocols.
            '''

            return 'Surfeit need'


    class ProtocolSupportsInt(object):
        '''
        User-defined protocol structurally (i.e., implicitly) satisfying
        *without* explicitly subclassing the predefined
        :class:`typing.SupportsInt` abstract base class (ABC).

        Note that the implementations of this and *all* other predefined
        :mod:`typing` protocols (e.g., :class:`typing.SupportsFloat`) bundled
        with older Python versions < 3.8 are *not* safely type-checkable at
        runtime. For safety, tests against *all* protocols including these
        previously predefined protocols *must* be isolated to this submodule.
        '''

        def __int__(self) -> int:
            return 42

    # Instance of the custom protocol defined above.
    protocol_custom_structural = ProtocolCustomStructural()

    # ..................{ FACTORIES ~ protocol               }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module...
    for Protocol in get_typing_attrs('Protocol'):
        # ................{ PROTOCOLS ~ user                   }................
        @runtime_checkable
        class ProtocolCustomUntypevared(Protocol):
            '''
            Arbitrary user-defined protocol parametrized by *no* type variables
            declaring arbitrary concrete and abstract methods.
            '''

            def alpha(self) -> str:
                '''
                Arbitrary concrete instance method.
                '''

                return 'Of a Spicily sated'


            @abstractmethod
            def omega(self) -> str:
                '''
                Arbitrary abstract instance method.
                '''

                pass


        @runtime_checkable
        class ProtocolCustomTypevared(Protocol[T]):
            '''
            Arbitrary user-defined protocol parametrized by a type variable
            declaring arbitrary concrete and abstract methods.
            '''

            def alpha(self) -> str:
                '''
                Arbitrary concrete instance method.
                '''

                return 'Gainfully ungiving criticisms, schismatizing Ŧheo‐'

            @abstractmethod
            def omega(self) -> str:
                '''
                Arbitrary abstract instance method.
                '''

                pass

        # ................{ PROTOCOLS ~ user : abc             }................
        @runtime_checkable
        class ProtocolCustomSuperclass(Protocol):
            '''
            Arbitrary user-defined protocol superclass.
            '''

            instance_variable: int
            '''
            Arbitrary instance variable assigned *NO* default value.
            '''


        class ProtocolCustomABC(ProtocolCustomSuperclass, ABC):
            '''
            User-defined abstract protocol subclassing both that superclass
            *and* the standard abstract base class (ABC) superclass, exercising
            a prior issue with respect to non-trivial protocol hierarchies.

            See also:
                https://github.com/beartype/beartype/issues/117
            '''

            instance_variable = 42
            '''
            Arbitrary instance variable assigned a default value.
            '''


            def concrete_method(self) -> str:
                '''
                Arbitrary concrete instance method.
                '''

                return (
                    'Lit, Faux-Phonetician Grecian predilection derelictions '
                    'predi‐sposed to'
                )


            @abstractmethod
            def abstract_method(self) -> str:
                '''
                Arbitrary abstract instance method.
                '''


        class ProtocolCustomSubclass(ProtocolCustomABC):
            '''
            Arbitrary user-defined protocol subclass concretely subclassing that
            protocol ABC.
            '''

            def abstract_method(self) -> str:
                return 'Concrete‐shambling,'

        # ................{ LISTS                              }................
        # Add PEP-specific type hint metadata to this list.
        hints_piths_pep_meta.extend((
            # ..............{ PROTOCOLS ~ user                   }..............
            # Despite appearances, protocols implicitly subclass
            # "typing.Generic" and thus do *NOT* transparently reduce to
            # standard types.
            #
            # Note that the "_data_pep484" submodule already exercises
            # predefined "typing" protocols (e.g., "typing.SupportsInt"), which
            # were technically introduced with PEP 484 and thus available since
            # Python >= 3.4 or so.

            # User-defined protocol parametrized by *NO* type variables.
            HintPepMetadata(
                hint=ProtocolCustomUntypevared,
                pep_sign=HintSignPep484585GenericUnsubbed,
                generic_type=ProtocolCustomUntypevared,
                is_type_typing=False,
                piths_meta=(
                    # Unrelated object satisfying this protocol.
                    PithSatisfiedMetadata(protocol_custom_structural),
                    # String constant.
                    PithUnsatisfiedMetadata('For durance needs.'),
                ),
            ),

            # User-defined protocol parametrized by a type variable.
            HintPepMetadata(
                hint=ProtocolCustomTypevared,
                pep_sign=HintSignPep484585GenericUnsubbed,
                generic_type=ProtocolCustomTypevared,
                is_type_typing=False,
                typeargs_packed=(T,),
                piths_meta=(
                    # Unrelated object satisfying this protocol.
                    PithSatisfiedMetadata(protocol_custom_structural),
                    # String constant.
                    PithUnsatisfiedMetadata('Machist-'),
                ),
            ),

            # User-defined protocol parametrized by a type variable, itself
            # parametrized by the same type variables in the same order.
            HintPepMetadata(
                hint=ProtocolCustomTypevared[T],
                pep_sign=HintSignPep484585GenericSubbed,
                generic_type=ProtocolCustomTypevared,
                is_typing=False,
                typeargs_packed=(T,),
                piths_meta=(
                    # Unrelated object satisfying this protocol.
                    PithSatisfiedMetadata(protocol_custom_structural),
                    # String constant.
                    PithUnsatisfiedMetadata(
                        'Black and white‐bit, bilinear linaements'),
                ),
            ),

            # User-defined protocol parametrized by a type variable, itself
            # parametrized by a concrete type satisfying this type variable.
            HintPepMetadata(
                hint=ProtocolCustomTypevared[str],
                pep_sign=HintSignPep484585GenericSubbed,
                generic_type=ProtocolCustomTypevared,
                is_typing=False,
                typeargs_packed=(T,),
                piths_meta=(
                    # Unrelated object satisfying this protocol.
                    PithSatisfiedMetadata(protocol_custom_structural),
                    # String constant.
                    PithUnsatisfiedMetadata(
                        'We are as clouds that veil the midnight moon;'),
                ),
            ),

            # User-defined abstract protocol subclassing the ABC superclass.
            HintPepMetadata(
                hint=ProtocolCustomABC,
                pep_sign=HintSignPep484585GenericUnsubbed,
                generic_type=ProtocolCustomABC,
                is_type_typing=False,
                piths_meta=(
                    # Unrelated object satisfying this protocol.
                    PithSatisfiedMetadata(ProtocolCustomSubclass()),
                    # String constant.
                    PithUnsatisfiedMetadata(
                        'Conspiratorially oratory‐fawning faces'),
                ),
            ),
        ))

    # ..................{ FACTORIES ~ BinaryIO               }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for BinaryIO in get_typing_attrs('BinaryIO'):
        hints_piths_pep_meta.extend((
            # ..............{ PEP 484                            }..............
            # "BinaryIO" generic.
            HintPepMetadata(
                hint=BinaryIO,
                pep_sign=HintSignBinaryIO,
                generic_type=BinaryIO,
                piths_meta=PITHS_META_BINARYIO,
            ),

            # ................{ PEP 585 ~ subclass             }................
            # Any subclass of the "BinaryIO" generic.
            HintPepMetadata(
                hint=type[BinaryIO],
                pep_sign=HintSignType,
                isinstanceable_type=type,
                is_pep585_builtin_subbed=True,
                piths_meta=(
                    # "BinaryIO" generic.
                    PithSatisfiedMetadata(BinaryIO),
                    # Arbitrary concrete subclass of the "BinaryIO" generic.
                    PithSatisfiedMetadata(BinaryIOFile),
                    # Unrelated C-based "io.FileIO" type.
                    PithSatisfiedMetadata(FileIO),

                    # String constant.
                    PithUnsatisfiedMetadata(
                        'Distinct, and visible; symbols divine'),
                    # Instance of that arbitrary concrete subclass.
                    PithUnsatisfiedMetadata(binary_io_file),
                    # Unrelated C-based "io.BytesIO" type, which *ALMOST*
                    # satisfies the PEP 544-compliant protocol implied by the
                    # "BinaryIO" generic. Notably, "io.BytesIO" fails to define
                    # *ANY* of the properties required by that protocol (e.g.,
                    # "closed", "mode", "name").
                    PithUnsatisfiedMetadata(BytesIO),
                    # Unrelated C-based "io.StringIO" type, which *ALMOST*
                    # satisfies the PEP 544-compliant protocol implied by the
                    # "TextIO" generic while obviously violating that implied by
                    # the "BinaryIO" generic. Is everybody suitably confused?
                    PithUnsatisfiedMetadata(StringIO),
                ),
            ),
        ))

    # ..................{ FACTORIES ~ TextIO                 }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for TextIO in get_typing_attrs('TextIO'):
        hints_piths_pep_meta.extend((
            # ..............{ GENERICS ~ io : unsubscripted      }..............
            # Unsubscripted "TextIO" abstract base class (ABC).
            HintPepMetadata(
                hint=TextIO,
                pep_sign=HintSignTextIO,
                generic_type=TextIO,
                piths_meta=PITHS_META_TEXTIO,
            ),

            # ................{ PEP 585 ~ subclass             }................
            # Any subclass of the "TextIO" generic.
            HintPepMetadata(
                hint=type[TextIO],
                pep_sign=HintSignType,
                isinstanceable_type=type,
                is_pep585_builtin_subbed=True,
                piths_meta=(
                    # "TextIO" generic.
                    PithSatisfiedMetadata(TextIO),
                    # Arbitrary concrete subclass of the "TextIO" generic.
                    PithSatisfiedMetadata(TextIOConcrete),

                    # String constant.
                    PithUnsatisfiedMetadata('Starkness'),
                    # Instance of that arbitrary concrete subclass.
                    PithUnsatisfiedMetadata(binary_io_file),
                    # Unrelated C-based "io.FileIO" type.
                    PithUnsatisfiedMetadata(FileIO),
                    # Unrelated C-based "io.BytesIO" type.
                    PithUnsatisfiedMetadata(BytesIO),
                    # Unrelated C-based "io.StringIO" type, which *ALMOST*
                    # satisfies the PEP 544-compliant protocol implied by the
                    # "TextIO" generic. Notably, "io.StringIO" fails to define
                    # *ANY* of the file-oriented properties required by that
                    # protocol (e.g., "closed", "mode", "name").
                    PithUnsatisfiedMetadata(StringIO),
                ),
            ),
        ))

    # ..................{ FACTORIES ~ IO                     }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for IO in get_typing_attrs('IO'):
        hints_piths_pep_meta.extend((
            # ..............{ GENERICS ~ io : unsubscripted      }..............
            # Unsubscripted "IO" abstract base class (ABC).
            HintPepMetadata(
                hint=IO,
                pep_sign=HintSignPep484585GenericUnsubbed,
                generic_type=IO,
                typeargs_packed=(AnyStr,),
                piths_meta=(
                    # Open read-only text file handle to this submodule.
                    PithSatisfiedMetadata(
                        pith=open_text_file, is_pith_factory=True),
                    # Open read-only binary file handle to this submodule.
                    PithSatisfiedMetadata(
                        pith=open_binary_file, is_pith_factory=True),
                    # String constant.
                    PithUnsatisfiedMetadata(
                        'To piously magistrate, dis‐empower, and'),
                ),
            ),

            # ..............{ GENERICS ~ io : subscripted        }..............
            # All possible subscriptions of the "IO" abstract base class (ABC).

            # "IO" subscripted by "Any", equivalent to merely that ABC.
            HintPepMetadata(
                hint=IO[Any],
                pep_sign=HintSignPep484585GenericSubbed,
                generic_type=IO,
                typeargs_packed=(AnyStr,),
                piths_meta=(
                    # Open read-only binary file handle to this submodule.
                    PithSatisfiedMetadata(
                        pith=open_binary_file, is_pith_factory=True),
                    # Open read-only text file handle to this submodule.
                    PithSatisfiedMetadata(
                        pith=open_text_file, is_pith_factory=True),
                    # String constant.
                    PithUnsatisfiedMetadata(
                        'Stoicly Anti‐heroic, synthetic'),
                ),
            ),

            # "IO" parametrized by the same type variable already parametrizing
            # that ABC, equivalent to merely that ABC.
            HintPepMetadata(
                hint=IO[AnyStr],
                pep_sign=HintSignPep484585GenericSubbed,
                generic_type=IO,
                typeargs_packed=(AnyStr,),
                piths_meta=(
                    # Open read-only binary file handle to this submodule.
                    PithSatisfiedMetadata(
                        pith=open_binary_file, is_pith_factory=True),
                    # Open read-only text file handle to this submodule.
                    PithSatisfiedMetadata(
                        pith=open_text_file, is_pith_factory=True),
                    # String constant.
                    PithUnsatisfiedMetadata(
                        'Thism‐predestined City’s pestilentially '
                        'celestial dark of'
                    ),
                ),
            ),

            # "IO" subscripted by "bytes", equivalent to "BinaryIO".
            HintPepMetadata(
                hint=IO[bytes],
                pep_sign=HintSignPep484585GenericSubbed,
                generic_type=IO,
                typeargs_packed=(AnyStr,),
                piths_meta=PITHS_META_BINARYIO,
            ),

            # "IO" subscripted by "str", equivalent to "TextIO".
            HintPepMetadata(
                hint=IO[str],
                pep_sign=HintSignPep484585GenericSubbed,
                generic_type=IO,
                typeargs_packed=(AnyStr,),
                piths_meta=PITHS_META_TEXTIO,
            ),

            # ................{ PEP 585 ~ subclass             }................
            # Any subclass of the "IO" generic.
            HintPepMetadata(
                hint=type[IO],
                pep_sign=HintSignType,
                isinstanceable_type=type,
                is_pep585_builtin_subbed=True,
                piths_meta=(
                    # "IO" generic.
                    PithSatisfiedMetadata(IO),
                    # Arbitrary concrete subclasses of the "IO" generic.
                    PithSatisfiedMetadata(BinaryIOFile),
                    PithSatisfiedMetadata(TextIOConcrete),
                    # Unrelated C-based "io.FileIO" type.
                    PithSatisfiedMetadata(FileIO),

                    # String constant.
                    PithUnsatisfiedMetadata(
                        'Distinct, and visible; symbols divine'),
                    # Instances of these arbitrary concrete subclasses.
                    PithUnsatisfiedMetadata(binary_io_file),
                    PithUnsatisfiedMetadata(text_io_concrete),
                    # Unrelated C-based "io.BytesIO" type, which *ALMOST*
                    # satisfies the PEP 544-compliant protocol implied by the
                    # "IO" generic. Notably, "io.BytesIO" fails to define *ANY*
                    # of the properties required by that protocol (e.g.,
                    # "closed", "mode", "name").
                    PithUnsatisfiedMetadata(BytesIO),
                    # Unrelated C-based "io.StringIO" type, which *ALMOST*
                    # satisfies the PEP 544-compliant protocol implied by the
                    # "IO" generic while obviously violating that implied by the
                    # "BinaryIO" generic. Is everybody suitably confused?
                    PithUnsatisfiedMetadata(StringIO),
                ),
            ),
        ))

    # ..................{ FACTORIES ~ SupportsAbs            }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsAbs in get_typing_attrs('SupportsAbs'):
        hints_piths_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsAbs" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsAbs,
                pep_sign=HintSignPep484585GenericUnsubbed,
                generic_type=SupportsAbs,
                # Oddly, some but *NOT* all "typing.Supports*" ABCs are
                # parametrized by type variables. However, these type variables
                # have nondescript names (e.g., "T") *NOT* officially exported
                # as public global variables by the "typing" module. To reduce
                # the likelihood of unexpected breakage under future Python
                # versions, we avoid asserting these exact type variables.
                is_typeargs=True,
                piths_meta=(
                    # Integer constant.
                    PithSatisfiedMetadata(777),  # <-- what can this mean!?!?!?
                    # String constant.
                    PithUnsatisfiedMetadata('Scour Our flowering'),
                ),
            )
        )

    # ..................{ FACTORIES ~ SupportsBytes          }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsBytes in get_typing_attrs('SupportsBytes'):
        hints_piths_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsBytes" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsBytes,
                pep_sign=HintSignPep484585GenericUnsubbed,
                generic_type=SupportsBytes,
                piths_meta=(
                    # Platform-agnostic filesystem path object constant.
                    #
                    # Note that exceedingly few stdlib types actually define the
                    # __bytes__() dunder method. Among the few are classes
                    # defined by the "pathlib" module, which is why we
                    # instantiate such an atypical class here. See also:
                    #     https://stackoverflow.com/questions/45522536/where-can-the-bytes-method-be-found
                    PithSatisfiedMetadata(
                        pith=lambda: Path('/'),
                        is_context_manager=True,
                        is_pith_factory=True,
                    ),
                    # String constant.
                    PithUnsatisfiedMetadata(
                        'Fond suburb’s gibbet‐ribbed castrati'),
                ),
            )

            #FIXME: Uncomment after we determine whether or not any stdlib
            #classes actually define the __complex__() dunder method. There
            #don't appear to be any, suggesting that the only means of testing
            #this would be to define a new custom "ProtocolSupportsComplex"
            #class as we do above for the "ProtocolSupportsInt" class. *shrug*
            # # Unsubscripted "SupportsComplex" abstract base class (ABC).
            # SupportsComplex: HintPepMetadata(
            #     pep_sign=Generic,
            #     piths_meta=(
            #         # Integer constant.
            #         108,
            #         # String constant.
            #         PithUnsatisfiedMetadata('Fondled ΘuroƂorus-'),
            #     ),
            # ),
        )

    # ..................{ FACTORIES ~ SupportsFloat          }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsFloat in get_typing_attrs('SupportsFloat'):
        hints_piths_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsFloat" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsFloat,
                pep_sign=HintSignPep484585GenericUnsubbed,
                generic_type=SupportsFloat,
                piths_meta=(
                    # Integer constant.
                    PithSatisfiedMetadata(92),
                    # String constant.
                    PithUnsatisfiedMetadata('Be’yond a'),
                ),
            )
        )

    # ..................{ FACTORIES ~ SupportsIndex          }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsIndex in get_typing_attrs('SupportsIndex'):
        hints_piths_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsIndex" abstract base class (ABC) first
            # introduced by Python 3.8.0.
            HintPepMetadata(
                hint=SupportsIndex,
                pep_sign=HintSignPep484585GenericUnsubbed,
                generic_type=SupportsIndex,
                piths_meta=(
                    # Integer constant.
                    PithSatisfiedMetadata(29),
                    # String constant.
                    PithUnsatisfiedMetadata('Self-ishly'),
                ),
            )
        )

    # ..................{ FACTORIES ~ SupportsInt            }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsInt in get_typing_attrs('SupportsInt'):
        hints_piths_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsInt" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsInt,
                pep_sign=HintSignPep484585GenericUnsubbed,
                generic_type=SupportsInt,
                piths_meta=(
                    # Floating-point number constant.
                    PithSatisfiedMetadata(25.78),
                    # Structurally subtyped instance.
                    PithSatisfiedMetadata(ProtocolSupportsInt()),
                    # String constant.
                    PithUnsatisfiedMetadata(
                        'Ungentlemanly self‐righteously, and'),
                ),
            )
        )

    # ..................{ FACTORIES ~ SupportsRound          }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsRound in get_typing_attrs('SupportsRound'):
        hints_piths_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsRound" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsRound,
                pep_sign=HintSignPep484585GenericUnsubbed,
                generic_type=SupportsRound,
                # Oddly, some but *NOT* all "typing.Supports*" ABCs are
                # parametrized by type variables. See "SupportsAbs" above.
                is_typeargs=True,
                piths_meta=(
                    # Floating-point number constant.
                    PithSatisfiedMetadata(87.52),
                    # String constant.
                    PithUnsatisfiedMetadata(
                        'Our Fathers vowed, indulgently,'),
                ),
            )
        )

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_piths_pep_meta


def hints_pep544_ignorable_shallow() -> list:
    '''
    List of :pep:`544`-compliant **shallowly ignorable type hints** (i.e.,
    ignorable on the trivial basis of their machine-readable representations).
    '''

    # ..................{ IMPORTS                            }..................
    from beartype._util.api.standard.utiltyping import get_typing_attrs

    # ..................{ LOCALS                             }..................
    # List of all PEP-specific shallowly ignorable type hints to be returned.
    hints_pep_ignorable_shallow = []

    # ..................{ LISTS                              }..................
    # For the PEP 544-specific "Protocol" superclass importable from any typing
    # module...
    for Protocol in get_typing_attrs('Protocol'):
        # ................{ SETS                               }................
        # Add PEP-specific shallowly ignorable type hints to this list.
        hints_pep_ignorable_shallow.append(
            # Ignoring the "typing.Protocol" superclass is vital. For unknown
            # and probably uninteresting reasons, *ALL* possible objects satisfy
            # this superclass. Ergo, this superclass is synonymous with the
            # root "object" superclass: e.g.,
            #     >>> import typing as t
            #     >>> isinstance(object(), t.Protocol)
            #     True  # <-- wat
            #     >>> isinstance('wtfbro', t.Protocol)
            #     True  # <-- WAT
            #     >>> isinstance(0x696969, t.Protocol)
            #     True  # <-- i'm outta here.
            Protocol,
        )

    # ..................{ RETURN                             }..................
    # Return this list.
    return hints_pep_ignorable_shallow


def hints_pep544_ignorable_deep() -> list:
    '''
    List of :pep:`544`-compliant **deeply ignorable type hints** (i.e.,
    ignorable only on the non-trivial basis of their nested child type hints).
    '''

    # ..................{ IMPORTS                            }..................
    from beartype._util.api.standard.utiltyping import get_typing_attrs
    from beartype_test.a00_unit.data.pep.pep484.data_pep484 import (
        S,
        T,
    )

    # ..................{ LOCALS                             }..................
    # List of all PEP-specific deeply ignorable type hints to be returned.
    hints_pep_ignorable_deep = []

    # ..................{ LISTS                              }..................
    # For the PEP 544-specific "Protocol" superclass importable from any typing
    # module...
    for Protocol in get_typing_attrs('Protocol'):
        # ................{ SETS                               }................
        # Add PEP-specific deeply ignorable type hints to this list.
        hints_pep_ignorable_deep.append(
            # Parametrizations of the "typing.Protocol" abstract base class.
            Protocol[S, T],
        )

    # ..................{ RETURN                             }..................
    # Return this list.
    return hints_pep_ignorable_deep
