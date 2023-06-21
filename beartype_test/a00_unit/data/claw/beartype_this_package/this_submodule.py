#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **generic types data** submodule.

This submodule predefines low-level class constants exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
    BeartypeDoorHintViolation,
)
from beartype.typing import (
    # Iterable,
    List,
    Optional,
    Union,
)
from pytest import raises

# ....................{ PEP 526                            }....................
# Validate that the beartype_this_package() import hook installed by the parent
# "beartype_this_package.__init__" submodule implicitly appends all PEP
# 562-compliant annotated assignment statements in other submodules of this
# "beartype_this_package" subpackage with calls to beartype's statement-level
# beartype.door.die_if_unbearable() exception-raiser.

# Assert that a PEP 562-compliant assignment statement assigning an object
# satisfying the type hint annotating that statement raises *NO* exception.
#
# Note that this type hint is intentionally annotated as "float" rather than
# either "int" *OR* "Union[int, float]", exercising that that import hook
# successfully associated this and *ALL* other submodules of the
# "beartype_this_package" subpackage with a non-default beartype configuration
# enabling the PEP 484-compliant implicit numeric tower (i.e.,
# "is_pep484_tower=True").
loves_philosophy: float = len('The fountains mingle with the river')

# Assert that a PEP 562-compliant assignment statement assigning an object
# violating the type hint annotating that statement raises the expected
# exception.
with raises(BeartypeDoorHintViolation):
    and_the_rivers_with_the_ocean: List[str] = (
        'The winds of heaven mix for ever')

# ....................{ FUNCTIONS                          }....................
def nothing_in_the_world(is_single: Union[float, bytes]) -> Optional[complex]:
    '''
    Arbitrary method either returning the passed integer first doubled and then
    coerced into a complex number with imaginary component ``1`` if this integer
    is non-zero *or* raising a :exc:`.BeartypeCallHintParamViolation` exception
    otherwise (i.e., if this integer is zero), exercising that beartype import
    hooks decorate global functions as expected.
    '''

    def in_one_spirit(meet_and_mingle: Optional[float]) -> Union[complex, str]:
        '''
        Arbitrary closure either returning the passed integer first doubled and then
        coerced into a complex number with imaginary component ``1`` if this
        integer is non-:data:`None` *or* raising a
        :exc:`.BeartypeCallHintReturnViolation` exception otherwise (i.e., if
        this integer is :data:`None`), exercising that beartype import hooks
        decorate closures as expected.
        '''

        # Return either...
        return (
            # If this integer is "None", explicitly force this
            # @beartype-decorated closure to raise a
            # "BeartypeCallHintReturnViolation" exception;
            None
            if meet_and_mingle is None else
            # Else, this integer is non-zero. In this case, return this integer
            # doubled and then coerced into a complex number with imaginary
            # component "1". Why? Just because. *THIS IS BEARTYPE.* Graaaah!
            is_single + meet_and_mingle + 1j
        )

    # Return either...
    return (
        # If this integer is zero, explicitly force this @beartype-decorated
        # closure to raise a "BeartypeCallHintReturnViolation" exception.
        in_one_spirit(None)
        if is_single == 0 else
        # Else, this integer is non-zero. In this case, return this integer
        # doubled and then coerced into a complex number with imaginary
        # component "1". Why? Just because. *THIS IS BEARTYPE.* Graaaah!
        in_one_spirit(is_single)
    )

# Assert that calling this function passed an arbitrary integer returns the
# expected complex number *WITHOUT* raising an exception.
assert nothing_in_the_world(len('Why not I with thine?')) == 42 + 1j

# Assert that calling this function passed an invalid parameter raises the
# expected exception.
with raises(BeartypeCallHintParamViolation):
    nothing_in_the_world('See the mountains kiss high heaven')

# Assert that calling this function passed zero raises the expected exception
# from the clojure defined and called by this function.
with raises(BeartypeCallHintReturnViolation):
    nothing_in_the_world(len('And the waves') - len('clasp another'))

# ....................{ CLASSES                            }....................
# class WithASweetEmotion(object):
#     '''
#     Arbitrary class to be implicitly decorated by the :func:`beartype.beartype`
#     decorator by the :func:`beartype.claw.beartype_this_package` import hook
#     installed by the parent ``beartype_this_package.__init__`` submodule.
#     '''
#
#     def nothing_in_the_world(self, is_single: int) -> Optional[complex]:
#         '''
#         Arbitrary method returning the passed object as is, enabling callers to
#         trivially test whether any call to this method violates the type hint
#         annotating the return of this method.
#         '''
#
#         def in_one_spirit(meet_and_mingle: complex)
#
#         # Look, @beartype. Just do it!
#         return is_single + 1j
