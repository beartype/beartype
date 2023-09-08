#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant **type hint test data.**
'''

# ....................{ TODO                               }....................
#FIXME: Generalize this submodule to transparently test all hints against both
#the "typing.Protocol" *AND* "beartype.typing.Protocol" superclasses. Doing so
#will, in turn, require defining a new "HintPepMetadata.hints" instance
#variable required to be a sequence of one or more hints.

#FIXME: Test user-defined multiple-inherited protocols (i.e., user-defined
#classes directly subclassing the "typing.Protocol" ABC and one or more other
#superclasses) once @beartype supports these protocols as well.

# ....................{ IMPORTS                            }....................

# ....................{ PRIVATE ~ constants                }....................
_DATA_HINTPEP544_FILENAME = __file__
'''
Absolute filename of this data submodule, to be subsequently opened for
cross-platform IO testing purposes by the :func:`add_data` function.
'''

# ....................{ ADDERS                             }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :pep:`544`-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # ..................{ IMPORTS                            }..................
    import pathlib
    from abc import (
        ABC,
        abstractmethod,
    )
    from beartype.typing import (
        Any,
        AnyStr,
        TypeVar,
        runtime_checkable,
    )
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignBinaryIO,
        HintSignGeneric,
        HintSignIO,
        HintSignTextIO,
    )
    # from beartype._data.module.datamodtyping import TYPING_MODULE_NAMES_STANDARD
    from beartype._util.module.lib.utiltyping import iter_typing_attrs
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from beartype_test._util.module.pytmodtest import (
        is_package_beartype_vale_usable)

    # Type variables.
    S = TypeVar('S')
    T = TypeVar('T')

    # ..................{ CALLABLES                          }..................
    def open_file_text():
        '''
        Function returning an open read-only file handle in text mode.
        '''
        return open(_DATA_HINTPEP544_FILENAME, 'r', encoding='utf8')


    def open_file_binary():
        '''
        Function returning an open read-only file handle in binary mode.
        '''
        return open(_DATA_HINTPEP544_FILENAME, 'rb')

    # List of one or more "HintPithUnsatisfiedMetadata" instances validating
    # objects *NOT* satisfied by either "typing.BinaryIO" *OR*
    # "typing.IO[bytes]". This list conditionally depends on the active Python
    # interpreter and thus *CANNOT* be defined as a standard tuple.
    binaryio_piths_meta = [
        # Open read-only binary file handle to this submodule.
        HintPithSatisfiedMetadata(
            pith=open_file_binary, is_pith_factory=True),
        # Bytestring constant.
        HintPithUnsatisfiedMetadata(
            b"Of a thieved imagination's reveries"),
    ]

    # If beartype validators are usable under the active Python interpreter...
    if is_package_beartype_vale_usable():
        # Add a "HintPithUnsatisfiedMetadata" instance validating open
        # read-only text file handles to violate both "typing.BinaryIO" *AND*
        # "typing.IO[bytes]" type hints. This validation requires beartype
        # validators, as the only means of differentiating objects satisfying
        # the "typing.BinaryIO" protocol from those satisfying the "typing.IO"
        # protocol is with an inverted instance check. Cue beartype validators.
        binaryio_piths_meta.append(
            HintPithUnsatisfiedMetadata(
                pith=open_file_text, is_pith_factory=True))

    # ..................{ PROTOCOLS ~ structural             }..................
    # User-defined class structurally (i.e., implicitly) satisfying *WITHOUT*
    # explicitly subclassing this user-defined protocol.
    class ProtocolCustomStructural(object):
        def alpha(self) -> str:
            return "Sufferance's humus excursion, humility’s endurance, an"

        def omega(self) -> str:
            return 'Surfeit need'

    # Instance of this class.
    protocol_custom_structural = ProtocolCustomStructural()

    # User-defined protocol structurally (i.e., implicitly) satisfying
    # *WITHOUT* explicitly subclassing the predefined "typing.SupportsInt"
    # abstract base class (ABC).
    #
    # Note that the implementations of this and *ALL* other predefined "typing"
    # protocols (e.g., "typing.SupportsFloat") bundled with older Python
    # versions < 3.8 are *NOT* safely type-checkable at runtime. For safety,
    # tests against *ALL* protocols including these previously predefined
    # protocols *MUST* be isolated to this submodule.
    class ProtocolSupportsInt(object):
        def __int__(self) -> int:
            return 42

    # ..................{ ATTRS ~ non-protocol               }..................
    # For each PEP 544-specific attribute *EXCEPT* the "Protocol" superclass
    # importable from any typing module...
    #
    # Note that "typing_extensions" currently defines the "Protocol" superclass
    # but fails to define most of these other attributes. Ergo, the two *MUST*
    # be iterated over independently.
    for (
        BinaryIO,
        IO,
        SupportsAbs,
        SupportsBytes,
        SupportsFloat,
        SupportsIndex,
        SupportsInt,
        SupportsRound,
        TextIO,
    ) in iter_typing_attrs(
        typing_attr_basenames=(
            'BinaryIO',
            'IO',
            'SupportsAbs',
            'SupportsBytes',
            'SupportsFloat',
            'SupportsIndex',
            'SupportsInt',
            'SupportsRound',
            'TextIO',
        ),
    ):
        # ................{ TUPLES                             }................
        # Add PEP 544-specific test type hints to that tuple.
        data_module.HINTS_PEP_META.extend((
            # ..............{ GENERICS ~ io : unsubscripted      }..............
            # Unsubscripted "IO" abstract base class (ABC).
            HintPepMetadata(
                hint=IO,
                pep_sign=HintSignIO,
                generic_type=IO,
                is_typevars=True,
                piths_meta=(
                    # Open read-only text file handle to this submodule.
                    HintPithSatisfiedMetadata(
                        pith=open_file_text, is_pith_factory=True),
                    # Open read-only binary file handle to this submodule.
                    HintPithSatisfiedMetadata(
                        pith=open_file_binary, is_pith_factory=True),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'To piously magistrate, dis‐empower, and'),
                ),
            ),

            # Unsubscripted "BinaryIO" abstract base class (ABC).
            HintPepMetadata(
                hint=BinaryIO,
                pep_sign=HintSignBinaryIO,
                generic_type=BinaryIO,
                piths_meta=binaryio_piths_meta,
            ),

            # Unsubscripted "TextIO" abstract base class (ABC).
            HintPepMetadata(
                hint=TextIO,
                pep_sign=HintSignTextIO,
                generic_type=TextIO,
                piths_meta=(
                    # Open read-only text file handle to this submodule.
                    HintPithSatisfiedMetadata(
                        pith=open_file_text, is_pith_factory=True),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Statistician’s anthemed meme athame'),
                    # Open read-only binary file handle to this submodule.
                    HintPithUnsatisfiedMetadata(
                        pith=open_file_binary, is_pith_factory=True),
                ),
            ),

            # ..............{ GENERICS ~ io : subscripted        }..............
            # All possible subscriptions of the "IO" abstract base class (ABC).
            HintPepMetadata(
                hint=IO[Any],
                pep_sign=HintSignIO,
                generic_type=IO,
                piths_meta=(
                    # Open read-only binary file handle to this submodule.
                    HintPithSatisfiedMetadata(
                        pith=open_file_binary, is_pith_factory=True),
                    # Open read-only text file handle to this submodule.
                    HintPithSatisfiedMetadata(
                        pith=open_file_text, is_pith_factory=True),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Stoicly Anti‐heroic, synthetic'),
                ),
            ),
            HintPepMetadata(
                hint=IO[bytes],
                pep_sign=HintSignIO,
                generic_type=IO,
                piths_meta=binaryio_piths_meta,
            ),
            HintPepMetadata(
                hint=IO[str],
                pep_sign=HintSignIO,
                generic_type=IO,
                piths_meta=(
                    # Open read-only text file handle to this submodule.
                    HintPithSatisfiedMetadata(
                        pith=open_file_text, is_pith_factory=True),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Thism‐predestined City’s pestilentially '
                        'celestial dark of'
                    ),
                    # Open read-only binary file handle to this submodule.
                    HintPithUnsatisfiedMetadata(
                        pith=open_file_binary, is_pith_factory=True),
                ),
            ),

            # Parametrization of the "IO" abstract base class (ABC).
            HintPepMetadata(
                hint=IO[AnyStr],
                pep_sign=HintSignIO,
                generic_type=IO,
                is_typevars=True,
                piths_meta=(
                    # Open read-only binary file handle to this submodule.
                    HintPithSatisfiedMetadata(
                        pith=open_file_binary, is_pith_factory=True),
                    # Open read-only text file handle to this submodule.
                    HintPithSatisfiedMetadata(
                        pith=open_file_text, is_pith_factory=True),
                    # String constant.
                    HintPithUnsatisfiedMetadata('Starkness'),
                ),
            ),

            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsAbs" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsAbs,
                pep_sign=HintSignGeneric,
                generic_type=SupportsAbs,
                # Oddly, some but *NOT* all "typing.Supports*" ABCs are
                # parametrized by type variables. *shrug*
                is_typevars=True,
                piths_meta=(
                    # Integer constant.
                    HintPithSatisfiedMetadata(777),  # <-- what can this mean!?!?!?
                    # String constant.
                    HintPithUnsatisfiedMetadata('Scour Our flowering'),
                ),
            ),

            # Unsubscripted "SupportsBytes" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsBytes,
                pep_sign=HintSignGeneric,
                generic_type=SupportsBytes,
                piths_meta=(
                    # Platform-agnostic filesystem path object constant.
                    #
                    # Note that exceedingly few stdlib types actually define
                    # the __bytes__() dunder method. Among the few include
                    # classes defined by the "pathlib" module, which is why we
                    # instantiate such an atypical class here. See also:
                    #     https://stackoverflow.com/questions/45522536/where-can-the-bytes-method-be-found
                    HintPithSatisfiedMetadata(
                        pith=lambda: pathlib.Path('/'),
                        is_context_manager=True,
                        is_pith_factory=True,
                    ),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Fond suburb’s gibbet‐ribbed castrati'),
                ),
            ),

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
            #         HintPithUnsatisfiedMetadata('Fondled ΘuroƂorus-'),
            #     ),
            # ),

            # Unsubscripted "SupportsFloat" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsFloat,
                pep_sign=HintSignGeneric,
                generic_type=SupportsFloat,
                piths_meta=(
                    # Integer constant.
                    HintPithSatisfiedMetadata(92),
                    # String constant.
                    HintPithUnsatisfiedMetadata('Be’yond a'),
                ),
            ),

            # Unsubscripted "SupportsIndex" abstract base class (ABC) first
            # introduced by Python 3.8.0.
            HintPepMetadata(
                hint=SupportsIndex,
                pep_sign=HintSignGeneric,
                generic_type=SupportsIndex,
                piths_meta=(
                    # Integer constant.
                    HintPithSatisfiedMetadata(29),
                    # String constant.
                    HintPithUnsatisfiedMetadata('Self-ishly'),
                ),
            ),

            # Unsubscripted "SupportsInt" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsInt,
                pep_sign=HintSignGeneric,
                generic_type=SupportsInt,
                piths_meta=(
                    # Floating-point number constant.
                    HintPithSatisfiedMetadata(25.78),
                    # Structurally subtyped instance.
                    HintPithSatisfiedMetadata(ProtocolSupportsInt()),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Ungentlemanly self‐righteously, and'),
                ),
            ),

            # Unsubscripted "SupportsRound" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsRound,
                pep_sign=HintSignGeneric,
                generic_type=SupportsRound,
                # Oddly, some but *NOT* all "typing.Supports*" ABCs are
                # parametrized by type variables. *shrug*
                is_typevars=True,
                piths_meta=(
                    # Floating-point number constant.
                    HintPithSatisfiedMetadata(87.52),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Our Fathers vowed, indulgently,'),
                ),
            ),
        ))

    # ..................{ ATTRS ~ protocol                   }..................
    # For the PEP 544-specific "Protocol" superclass importable from any typing
    # module...
    for Protocol in iter_typing_attrs(
        typing_attr_basenames='Protocol', is_warn=True):
        # ................{ PROTOCOLS ~ user                   }................
        @runtime_checkable
        class ProtocolCustomUntypevared(Protocol):
            '''
            User-defined protocol parametrized by *NO* type variables declaring
            arbitrary concrete and abstract methods.
            '''

            def alpha(self) -> str:
                return 'Of a Spicily sated'

            @abstractmethod
            def omega(self) -> str: pass


        @runtime_checkable
        class ProtocolCustomTypevared(Protocol[T]):
            '''
            User-defined protocol parametrized by a type variable declaring
            arbitrary concrete and abstract methods.
            '''

            def alpha(self) -> str:
                return 'Gainfully ungiving criticisms, schismatizing Ŧheo‐'

            @abstractmethod
            def omega(self) -> str: pass

        # ................{ PROTOCOLS ~ user : abc             }................
        @runtime_checkable
        class ProtocolCustomSuperclass(Protocol):
            '''
            User-defined protocol superclass.
            '''

            instance_variable: int


        class ProtocolCustomABC(ProtocolCustomSuperclass, ABC):
            '''
            User-defined abstract protocol subclassing both this superclass
            *and* the standard abstract base class (ABC) superclass, exercising
            a prior issue with respect to non-trivial protocol hierarchies.

            See also:
                https://github.com/beartype/beartype/issues/117
            '''

            instance_variable = 42

            def concrete_method(self) -> str:
                return (
                    'Lit, Faux-Phonetician Grecian predilection derelictions '
                    'predi‐sposed to'
                )

            @abstractmethod
            def abstract_method(self) -> str: pass


        class ProtocolCustomSubclass(ProtocolCustomABC):
            '''
            User-defined protocol subclass concretely subclassing this ABC.
            '''

            def abstract_method(self) -> str:
                return 'Concrete‐shambling,'

        # ................{ SETS                               }................
        # Add PEP 544-specific shallowly ignorable test type hints to that set
        # global.
        data_module.HINTS_PEP_IGNORABLE_SHALLOW.update((
            # Note that ignoring the "typing.Protocol" superclass is vital
            # here. For unknown and presumably uninteresting reasons, *ALL*
            # possible objects satisfy this superclass. Ergo, this superclass
            # is synonymous with the "object" root superclass: e.g.,
            #     >>> import typing as t
            #     >>> isinstance(object(), t.Protocol)
            #     True
            #     >>> isinstance('wtfbro', t.Protocol)
            #     True
            #     >>> isinstance(0x696969, t.Protocol)
            #     True
            Protocol,
        ))

        # Add PEP 544-specific deeply ignorable test type hints to that set.
        data_module.HINTS_PEP_IGNORABLE_DEEP.update((
            # Parametrizations of the "typing.Protocol" abstract base class.
            Protocol[S, T],
        ))

        # ................{ TUPLES                             }................
        # Add PEP 544-specific test type hints to that tuple.
        data_module.HINTS_PEP_META.extend((
            # ..............{ PROTOCOLS ~ user                   }..............
            # Despite appearances, protocols implicitly subclass
            # "typing.Generic" and thus do *NOT* transparently reduce to
            # standard types.
            #
            # Note that the "data_pep484" submodule already exercises
            # predefined "typing" protocols (e.g., "typing.SupportsInt"), which
            # were technically introduced with PEP 484 and thus available since
            # Python >= 3.4 or so.

            # User-defined protocol parametrized by *NO* type variables.
            HintPepMetadata(
                hint=ProtocolCustomUntypevared,
                pep_sign=HintSignGeneric,
                generic_type=ProtocolCustomUntypevared,
                is_type_typing=False,
                piths_meta=(
                    # Unrelated object satisfying this protocol.
                    HintPithSatisfiedMetadata(protocol_custom_structural),
                    # String constant.
                    HintPithUnsatisfiedMetadata('For durance needs.'),
                ),
            ),

            # User-defined protocol parametrized by a type variable.
            HintPepMetadata(
                hint=ProtocolCustomTypevared,
                pep_sign=HintSignGeneric,
                generic_type=ProtocolCustomTypevared,
                is_typevars=True,
                is_type_typing=False,
                piths_meta=(
                    # Unrelated object satisfying this protocol.
                    HintPithSatisfiedMetadata(protocol_custom_structural),
                    # String constant.
                    HintPithUnsatisfiedMetadata('Machist-'),
                ),
            ),

            # User-defined protocol parametrized by a type variable, itself
            # parametrized by the same type variables in the same order.
            HintPepMetadata(
                hint=ProtocolCustomTypevared[T],
                pep_sign=HintSignGeneric,
                generic_type=ProtocolCustomTypevared,
                is_typevars=True,
                is_typing=False,
                piths_meta=(
                    # Unrelated object satisfying this protocol.
                    HintPithSatisfiedMetadata(protocol_custom_structural),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Black and white‐bit, bilinear linaements'),
                ),
            ),

            # User-defined protocol parametrized by a type variable, itself
            # parametrized by a concrete type satisfying this type variable.
            HintPepMetadata(
                hint=ProtocolCustomTypevared[str],
                pep_sign=HintSignGeneric,
                generic_type=ProtocolCustomTypevared,
                is_typing=False,
                piths_meta=(
                    # Unrelated object satisfying this protocol.
                    HintPithSatisfiedMetadata(protocol_custom_structural),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'We are as clouds that veil the midnight moon;'),
                ),
            ),

            # User-defined abstract protocol subclassing the ABC superclass.
            HintPepMetadata(
                hint=ProtocolCustomABC,
                pep_sign=HintSignGeneric,
                generic_type=ProtocolCustomABC,
                is_type_typing=False,
                piths_meta=(
                    # Unrelated object satisfying this protocol.
                    HintPithSatisfiedMetadata(ProtocolCustomSubclass()),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Conspiratorially oratory‐fawning faces'),
                ),
            ),

        ))
