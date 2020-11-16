#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 544`_**-compliant type hint test data.**

.. _PEP 544:
    https://www.python.org/dev/peps/pep-0544
'''

# ....................{ TODO                              }....................
#FIXME: Test user-defined multiple-inherited protocols (i.e., user-defined
#classes directly subclassing the "typing.Protocol" ABC and one or more other
#superclasses) once @beartype supports these protocols as well.

# ....................{ IMPORTS                           }....................
import pathlib
from abc import abstractmethod
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from beartype_test.unit.data.hint.pep.data_hintpepmeta import (
    PepHintMetadata,
    PepHintPithUnsatisfiedMetadata,
)

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 544`_**-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 544:
        https://www.python.org/dev/peps/pep-0544
    '''

    # If the active Python interpreter targets less than Python < 3.8, this
    # interpreter fails to support PEP 544. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_8:
        return
    # Else, the active Python interpreter targets at least Python >= 3.8 and
    # thus supports PEP 544.

    # Defer Python >= 3.8-specific imports.
    from typing import (
        BinaryIO,
        Generic,
        IO,
        Protocol,
        SupportsAbs,
        SupportsBytes,
        SupportsComplex,
        SupportsFloat,
        SupportsIndex,
        SupportsInt,
        SupportsRound,
        TextIO,
        TypeVar,
        runtime_checkable,
    )

    # Type variables.
    S = TypeVar('S')
    T = TypeVar('T')

    # User-defined protocol parametrized by *NO* type variables declaring
    # arbitrary concrete and abstract methods.
    @runtime_checkable
    class ProtocolCustomUntypevared(Protocol):
        def alpha(self) -> str:
            return 'Of a Spicily sated'

        @abstractmethod
        def omega(self) -> str: pass

    # User-defined protocol parametrized by a type variable declaring arbitrary
    # concrete and abstract methods.
    @runtime_checkable
    class ProtocolCustomTypevared(Protocol[T]):
        def alpha(self) -> str:
            return 'Gainfully ungiving criticisms, schismatizing Ŧheo‐'

        @abstractmethod
        def omega(self) -> str: pass

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
    # versions < 3.8 are *NOT* safely type-checkable at runtime. For safety
    # , tests against *ALL* protocols including these previously predefined
    # protocols *MUST* be isolated to this submodule.
    class ProtocolSupportsInt(object):
        def __int__(self) -> int:
            return 42

    # Add PEP 544-specific test type hints to this dictionary global.
    data_module.HINT_PEP_TO_META.update({
        # ................{ GENERICS ~ io                     }................
        #FIXME: These ABCs are useless as currently defined at runtime, as they
        #fail to subclass either "ABCMeta" or "typing.Protocol", despite
        #decorating methods with @abstractmethod -- which frankly seems like an
        #egregious error. It's doubtful that we'd be able to sanely
        #monkey-patch these classes; instead, what we should probably do is:
        #* In "_pephint":
        #  * Call is_hint_pep544_io_generic() and
        #    get_hint_pep544_io_protocol_from_generic() somewhere -- probably
        #    where we currently perform PEP 593 reduction. Note that this
        #    should be done *ONLY* if the current hint is the root hint. Why?
        #    Because we want to permit users to subclass their own classes from
        #    these ABCs and preserve correct semantics when doing so.
        #* In "_peperrorsleuth":
        #  * Refactor similarly.
        #* Shift the hints below into the "data_hintpep544" submodule.

        # # Unsubscripted "IO" abstract base class (ABC).
        # IO: PepHintMetadata(
        #     pep_sign=Generic,
        #     is_typevared=True,
        #     piths_satisfied=(
        #         # String buffer.
        #         io.StringIO('Scows'),
        #     ),
        #     piths_unsatisfied_meta=(
        #         # String constant.
        #         PepHintPithUnsatisfiedMetadata(
        #             'To piously magistrate, dis‐empower, and'),
        #     ),
        # ),
        #
        # # Unsubscripted "TextIO" abstract base class (ABC).
        # BinaryIO: PepHintMetadata(
        #     pep_sign=Generic,
        #     piths_satisfied=(
        #         # Bytestring buffer.
        #         io.BytesIO(b'Of a magik-stoned Shinto rivery'),
        #     ),
        #     piths_unsatisfied_meta=(
        #         # Bytestring constant.
        #         PepHintPithUnsatisfiedMetadata(
        #             b"Of a thieved imagination's reveries"),
        #     ),
        # ),
        #
        # # Unsubscripted "TextIO" abstract base class (ABC).
        # TextIO: PepHintMetadata(
        #     pep_sign=Generic,
        #     piths_satisfied=(
        #         # String buffer.
        #         io.StringIO('Statist'),
        #     ),
        #     piths_unsatisfied_meta=(
        #         # String constant.
        #         PepHintPithUnsatisfiedMetadata(
        #             'Statistician’s anthemed meme athame'),
        #     ),
        # ),

        # ................{ PROTOCOLS ~ supports              }................
        # Unsubscripted "SupportsAbs" abstract base class (ABC).
        SupportsAbs: PepHintMetadata(
            pep_sign=Generic,
            # Oddly, some but *NOT* all "typing.Supports*" ABCs are
            # parametrized by type variables. *shrug*
            is_typevared=True,
            piths_satisfied=(
                # Integer constant.
                73,
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Scour Our flowering'),
            ),
        ),

        # Unsubscripted "SupportsBytes" abstract base class (ABC).
        SupportsBytes: PepHintMetadata(
            pep_sign=Generic,
            piths_satisfied=(
                # Platform-agnostic filesystem path object constant.
                #
                # Note that exceedingly few stdlib types actually define the
                # __bytes__() dunder method. Among the few include classes
                # defined by the "pathlib" module, which is why we instantiate
                # such an atypical class here. See also:
                #     https://stackoverflow.com/questions/45522536/where-can-the-bytes-method-be-found
                pathlib.Path('/'),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Fond suburb’s gibbet‐ribbed castrati'),
            ),
        ),

        #FIXME: Uncomment after we determine whether or not any stdlib classes
        #actually define the __complex__() dunder method. There don't appear to
        #be any, suggesting that the only means of testing this would be to
        #define a new custom "ProtocolSupportsComplex" class as we do above for
        #the "ProtocolSupportsInt" class. *shrug*
        # # Unsubscripted "SupportsComplex" abstract base class (ABC).
        # SupportsComplex: PepHintMetadata(
        #     pep_sign=Generic,
        #     piths_satisfied=(
        #         # Integer constant.
        #         108,
        #     ),
        #     piths_unsatisfied_meta=(
        #         # String constant.
        #         PepHintPithUnsatisfiedMetadata('Fondled ΘuroƂorus-'),
        #     ),
        # ),

        # Unsubscripted "SupportsFloat" abstract base class (ABC).
        SupportsFloat: PepHintMetadata(
            pep_sign=Generic,
            piths_satisfied=(
                # Integer constant.
                92,
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Be’yond a'),
            ),
        ),

        # Unsubscripted "SupportsIndex" abstract base class (ABC) first
        # introduced by Python 3.8.0.
        SupportsIndex: PepHintMetadata(
            pep_sign=Generic,
            piths_satisfied=(
                # Integer constant.
                29,
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Self-ishly'),
            ),
        ),

        # Unsubscripted "SupportsInt" abstract base class (ABC).
        SupportsInt: PepHintMetadata(
            pep_sign=Generic,
            piths_satisfied=(
                # Floating-point number constant.
                25.78,
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Ungentlemanly self‐righteously, and'),
            ),
        ),

        # Unsubscripted "SupportsRound" abstract base class (ABC).
        SupportsRound: PepHintMetadata(
            pep_sign=Generic,
            # Oddly, some but *NOT* all "typing.Supports*" ABCs are
            # parametrized by type variables. *shrug*
            is_typevared=True,
            piths_satisfied=(
                # Floating-point number constant.
                87.52,
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Our Fathers vowed, indulgently,'),
            ),
        ),

        # ................{ PROTOCOLS ~ supports : user       }................
        # Predefined "typing" protocol.
        SupportsInt: PepHintMetadata(
            pep_sign=Generic,
            piths_satisfied=(
                # Structurally subtyped instance.
                ProtocolSupportsInt(),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('For durance needs.'),
            ),
        ),

        # ................{ PROTOCOLS ~ user                  }................
        # Despite appearances, protocols implicitly subclass "typing.Generic"
        # and thus do *NOT* transparently reduce to standard types.
        #
        # Note that the "data_hintpep484" submodule already exercises
        # predefined "typing" protocols (e.g., "typing.SupportsInt"), which
        # were technically introduced with PEP 484 and thus available since
        # Python >= 3.4 or so.

        # User-defined protocol parametrized by *NO* type variables.
        ProtocolCustomUntypevared: PepHintMetadata(
            pep_sign=Generic,
            is_typing=False,
            piths_satisfied=(protocol_custom_structural,),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('For durance needs.'),
            ),
        ),

        # User-defined protocol parametrized by a type variable.
        ProtocolCustomTypevared: PepHintMetadata(
            pep_sign=Generic,
            is_typevared=True,
            is_typing=False,
            piths_satisfied=(protocol_custom_structural,),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Machist-'),
            ),
        ),
    })

    # Add PEP 484-specific deeply ignorable test type hints to that set global.
    data_module.HINTS_PEP_IGNORABLE_DEEP.update((
        # Parametrizations of the "typing.Protocol" abstract base class (ABC).
        Protocol[S, T],
    ))
