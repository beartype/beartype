#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hookable** :pep:`526` **exception submodule** (i.e., data
module containing *only* :pep:`526`-compliant annotated variable assignments
raising :class:`beartype.roar.BeartypeDoorHintViolation` violations, mimicking
real-world usage of the :func:`beartype.claw.beartype_package` import hook from
external callers).
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDoorHintViolation
from beartype.typing import (
    List,
    Union,
)
from beartype._util.text.utiltextrepr import represent_object
from pytest import raises

# Import another submodule of this subpackage implicitly installing different
# import hooks configured by another beartype configuration isolated to that
# submodule. Doing so exercises that beartype import hooks correctly support
# import hook composition (i.e., combinations of arbitrary import hooks).
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.beartype_this_package import (
    this_submodule)

# from beartype.claw._clawstate import claw_state
# print(f'this_submodule conf: {repr(claw_state.module_name_to_beartype_conf)}')

# ....................{ PEP 526                            }....................
# Validate that the import hook presumably installed by the caller implicitly
# appends all PEP 526-compliant annotated assignment statements in this
# submodule with calls to beartype's statement-level
# beartype.door.die_if_unbearable() exception-raiser.

# Assert that a PEP 526-compliant annotated assignment statement assigning an
# object satisfying the type hint annotating that statement raises *NO*
# exception.
and_winter_robing: int = len('And winter robing with pure snow and crowns')

# Assert that a PEP 526-compliant annotated statement lacking an assignment
# raises *NO* exception.
such_magic_as_compels_the_charmed_night: str

# Arbitrary object violating type hints below.
OF_STARRY_ICE = len('Of starry ice the grey grass and bare boughs;')

# Assert that a PEP 526-compliant annotated assignment statement assigning an
# object violating the type hint annotating that statement raises the expected
# exception.
with raises(BeartypeDoorHintViolation) as exception_info:
    of_starry_ice: Union[float, List[str]] = OF_STARRY_ICE

# Exception message raised by that assignment.
exception_message = str(exception_info.value)

# Truncated representation of the invalid object assigned by that assignment.
pith_repr = represent_object(OF_STARRY_ICE)

# Assert that this message contains a truncated representation of this pith.
assert pith_repr in exception_message

# Assert that this raiser successfully replaced the temporary
# placeholder previously prefixing this message.
assert 'global ' in exception_message.lower()
assert __name__ in exception_message
assert ' violates type hint ' in exception_message

# ....................{ CLASSES                            }....................
class ThePausesOfHerMusic(object):
    and_her_breath: int = 'The pauses of her music, and her breath'
    '''
    Class variable whose initial value violates the :pep:`526`-compliant type
    hint annotating this variable.

    This variable effectively validates that the import hook presumably
    installed by the caller ignores all :pep:`526`-compliant annotated class
    variable assignment statements by *not* implicitly appending these
    statements with calls to the statement-level
    :func:`beartype.door.die_if_unbearable` exception-raiser.
    '''

    pass

# ....................{ CALLABLES                          }....................
def beneath_the_cold_glare() -> None:
    '''
    Arbitrary callable whose body contains one or more :pep:`526`-compliant
    annotated variable assignments, exercising edge cases in
    :mod:`beartype.claw` import hooks handling these assignments.
    '''

    # Arbitrary object violating type hints below.
    OF_THE_DESOLATE_NIGHT = len('Beneath the cold glare of the desolate night,')

    # Assert that a PEP 526-compliant annotated assignment statement assigning
    # an object violating the type hint annotating that statement raises the
    # expected exception.
    with raises(BeartypeDoorHintViolation) as exception_info:
        through_tangled_swamps: Union[float, List[str]] = OF_THE_DESOLATE_NIGHT

    # Exception message raised by that assignment.
    local_exception_message = str(exception_info.value)

    # Truncated representation of the invalid object assigned by that assignment.
    local_pith_repr = represent_object(OF_THE_DESOLATE_NIGHT)

    # Assert that this message contains a truncated representation of this pith.
    assert local_pith_repr in local_exception_message

    # Assert that this raiser successfully replaced the temporary
    # placeholder previously prefixing this message.
    assert 'callable ' in local_exception_message.lower()
    assert __name__ in local_exception_message
    assert 'beneath_the_cold_glare() ' in local_exception_message
    assert ' violates type hint ' in local_exception_message
