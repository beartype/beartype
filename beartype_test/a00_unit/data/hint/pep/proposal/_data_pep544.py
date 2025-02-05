#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant **type hint test data.**
'''

# ....................{ TODO                               }....................
#FIXME: Test user-defined multiple-inherited protocols (i.e., user-defined
#classes directly subclassing the "typing.Protocol" ABC and one or more other
#superclasses) once @beartype supports these protocols as well.

# ....................{ FIXTURES                           }....................
def hints_pep544_meta() -> 'List[HintPepMetadata]':
    '''
    List of :pep:`544`-compliant **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific :pep:`544`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from abc import (
        ABC,
        abstractmethod,
    )
    from beartype.typing import (
        Any,
        AnyStr,
        runtime_checkable,
    )
    from beartype._data.hint.datahinttyping import T
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignBinaryIO,
        HintSignPep484585GenericSubscripted,
        HintSignPep484585GenericUnsubscripted,
        HintSignTextIO,
    )
    from beartype._util.api.standard.utiltyping import get_typing_attrs
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from pathlib import Path

    # ..................{ LOCALS                             }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = []

    # Absolute filename of this data submodule, to be subsequently opened for
    # cross-platform IO testing purposes.
    SUBMODULE_FILENAME = __file__

    # ..................{ CALLABLES                          }..................
    def open_file_text():
        '''
        Function returning an open read-only file handle in text mode.
        '''

        return open(SUBMODULE_FILENAME, 'r', encoding='utf8')


    def open_file_binary():
        '''
        Function returning an open read-only file handle in binary mode.
        '''

        return open(SUBMODULE_FILENAME, 'rb')


    # List of one or more "HintPithUnsatisfiedMetadata" instances validating
    # objects *NOT* satisfied by either "typing.BinaryIO" *OR*
    # "typing.IO[bytes]". This list conditionally depends on the active Python
    # interpreter and thus *CANNOT* be defined as a standard tuple.
    binaryio_piths_meta = [
        # Open read-only binary file handle to this submodule.
        HintPithSatisfiedMetadata(pith=open_file_binary, is_pith_factory=True),
        # Bytestring constant.
        HintPithUnsatisfiedMetadata(b"Of a thieved imagination's reveries"),
        # "HintPithUnsatisfiedMetadata" instance validating open
        # read-only text file handles to violate both "typing.BinaryIO" *AND*
        # "typing.IO[bytes]" type hints. This validation requires beartype
        # validators, as the only means of differentiating objects satisfying
        # the "typing.BinaryIO" protocol from those satisfying the "typing.IO"
        # protocol is with an inverted instance check. Cue beartype validators.
        HintPithUnsatisfiedMetadata(pith=open_file_text, is_pith_factory=True),
    ]

    # ..................{ PROTOCOLS ~ structural             }..................
    class ProtocolCustomStructural(object):
        '''
        User-defined class structurally (i.e., implicitly) satisfying *without*
        explicitly subclassing this user-defined protocol.
        '''

        def alpha(self) -> str:
            return "Sufferance's humus excursion, humility’s endurance, an"

        def omega(self) -> str:
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

    # ..................{ FACTORIES ~ Protocol               }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module...
    for Protocol in get_typing_attrs('Protocol'):
        # ................{ PROTOCOLS ~ user                   }................
        @runtime_checkable
        class ProtocolCustomUntypevared(Protocol):
            '''
            User-defined protocol parametrized by *no* type variables declaring
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

        # ................{ LISTS                              }................
        # Add PEP-specific type hint metadata to this list.
        hints_pep_meta.extend((
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
                pep_sign=HintSignPep484585GenericUnsubscripted,
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
                pep_sign=HintSignPep484585GenericUnsubscripted,
                generic_type=ProtocolCustomTypevared,
                is_type_typing=False,
                typevars=(T,),
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
                pep_sign=HintSignPep484585GenericSubscripted,
                generic_type=ProtocolCustomTypevared,
                typevars=(T,),
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
                pep_sign=HintSignPep484585GenericSubscripted,
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
                pep_sign=HintSignPep484585GenericUnsubscripted,
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

    # ..................{ FACTORIES ~ BinaryIO               }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for BinaryIO in get_typing_attrs('BinaryIO'):
        hints_pep_meta.append(
            # ..............{ GENERICS ~ io : unsubscripted      }..............
            # Unsubscripted "BinaryIO" abstract base class (ABC).
            HintPepMetadata(
                hint=BinaryIO,
                pep_sign=HintSignBinaryIO,
                generic_type=BinaryIO,
                piths_meta=binaryio_piths_meta,
            )
        )

    # ..................{ FACTORIES ~ TextIO                 }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for TextIO in get_typing_attrs('TextIO'):
        hints_pep_meta.append(
            # ..............{ GENERICS ~ io : unsubscripted      }..............
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
            )
        )

    # ..................{ FACTORIES ~ IO                     }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for IO in get_typing_attrs('IO'):
        hints_pep_meta.extend((
            # ..............{ GENERICS ~ io : unsubscripted      }..............
            # Unsubscripted "IO" abstract base class (ABC).
            HintPepMetadata(
                hint=IO,
                pep_sign=HintSignPep484585GenericUnsubscripted,
                generic_type=IO,
                typevars=(AnyStr,),
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

            # ..............{ GENERICS ~ io : subscripted        }..............
            # All possible subscriptions of the "IO" abstract base class (ABC).
            HintPepMetadata(
                hint=IO[Any],
                pep_sign=HintSignPep484585GenericSubscripted,
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
                pep_sign=HintSignPep484585GenericSubscripted,
                generic_type=IO,
                piths_meta=binaryio_piths_meta,
            ),
            HintPepMetadata(
                hint=IO[str],
                pep_sign=HintSignPep484585GenericSubscripted,
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
                pep_sign=HintSignPep484585GenericSubscripted,
                generic_type=IO,
                typevars=(AnyStr,),
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
        ))

    # ..................{ FACTORIES ~ SupportsAbs            }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsAbs in get_typing_attrs('SupportsAbs'):
        hints_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsAbs" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsAbs,
                pep_sign=HintSignPep484585GenericUnsubscripted,
                generic_type=SupportsAbs,
                # Oddly, some but *NOT* all "typing.Supports*" ABCs are
                # parametrized by type variables. However, these type variables
                # have nondescript names (e.g., "T") *NOT* officially exported
                # as public global variables by the "typing" module. To reduce
                # the likelihood of unexpected breakage under future Python
                # versions, we avoid asserting these exact type variables.
                is_typevars=True,
                piths_meta=(
                    # Integer constant.
                    HintPithSatisfiedMetadata(777),  # <-- what can this mean!?!?!?
                    # String constant.
                    HintPithUnsatisfiedMetadata('Scour Our flowering'),
                ),
            )
        )

    # ..................{ FACTORIES ~ SupportsBytes          }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsBytes in get_typing_attrs('SupportsBytes'):
        hints_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsBytes" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsBytes,
                pep_sign=HintSignPep484585GenericUnsubscripted,
                generic_type=SupportsBytes,
                piths_meta=(
                    # Platform-agnostic filesystem path object constant.
                    #
                    # Note that exceedingly few stdlib types actually define the
                    # __bytes__() dunder method. Among the few are classes
                    # defined by the "pathlib" module, which is why we
                    # instantiate such an atypical class here. See also:
                    #     https://stackoverflow.com/questions/45522536/where-can-the-bytes-method-be-found
                    HintPithSatisfiedMetadata(
                        pith=lambda: Path('/'),
                        is_context_manager=True,
                        is_pith_factory=True,
                    ),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
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
            #         HintPithUnsatisfiedMetadata('Fondled ΘuroƂorus-'),
            #     ),
            # ),
        )

    # ..................{ FACTORIES ~ SupportsFloat          }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsFloat in get_typing_attrs('SupportsFloat'):
        hints_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsFloat" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsFloat,
                pep_sign=HintSignPep484585GenericUnsubscripted,
                generic_type=SupportsFloat,
                piths_meta=(
                    # Integer constant.
                    HintPithSatisfiedMetadata(92),
                    # String constant.
                    HintPithUnsatisfiedMetadata('Be’yond a'),
                ),
            )
        )

    # ..................{ FACTORIES ~ SupportsIndex          }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsIndex in get_typing_attrs('SupportsIndex'):
        hints_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsIndex" abstract base class (ABC) first
            # introduced by Python 3.8.0.
            HintPepMetadata(
                hint=SupportsIndex,
                pep_sign=HintSignPep484585GenericUnsubscripted,
                generic_type=SupportsIndex,
                piths_meta=(
                    # Integer constant.
                    HintPithSatisfiedMetadata(29),
                    # String constant.
                    HintPithUnsatisfiedMetadata('Self-ishly'),
                ),
            )
        )

    # ..................{ FACTORIES ~ SupportsInt            }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsInt in get_typing_attrs('SupportsInt'):
        hints_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsInt" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsInt,
                pep_sign=HintSignPep484585GenericUnsubscripted,
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
            )
        )

    # ..................{ FACTORIES ~ SupportsRound          }..................
    # For each PEP-specific type hint factory importable from each currently
    # importable "typing" module, add PEP-specific type hint metadata.
    for SupportsRound in get_typing_attrs('SupportsRound'):
        hints_pep_meta.append(
            # ..............{ PROTOCOLS ~ supports               }..............
            # Unsubscripted "SupportsRound" abstract base class (ABC).
            HintPepMetadata(
                hint=SupportsRound,
                pep_sign=HintSignPep484585GenericUnsubscripted,
                generic_type=SupportsRound,
                # Oddly, some but *NOT* all "typing.Supports*" ABCs are
                # parametrized by type variables. See "SupportsAbs" above.
                is_typevars=True,
                piths_meta=(
                    # Floating-point number constant.
                    HintPithSatisfiedMetadata(87.52),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Our Fathers vowed, indulgently,'),
                ),
            )
        )

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta


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
    from beartype._data.hint.datahinttyping import (
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
