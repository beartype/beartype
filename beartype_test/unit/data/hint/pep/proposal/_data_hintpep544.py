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
        Generic,
        Protocol,
        SupportsInt,
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
        # ................{ PROTOCOLS                         }................
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
            piths_satisfied=(protocol_custom_structural,),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('For durance needs.'),
            ),
        ),

        # User-defined protocol parametrized by a type variable.
        ProtocolCustomTypevared: PepHintMetadata(
            pep_sign=Generic,
            piths_satisfied=(protocol_custom_structural,),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Machist-'),
            ),
        ),

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
    })

    # Add PEP 484-specific deeply ignorable test type hints to that set global.
    data_module.HINTS_PEP_IGNORABLE_DEEP.update((
        # Parametrizations of the "typing.Protocol" abstract base class (ABC).
        Protocol[S, T],
    ))
