#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype import hookable function submodule** (i.e., data
module containing *only* annotated functions, mimicking real-world usage of the
:func:`beartype.claw.beartype_package` import hook from an external caller).
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
)
from beartype.typing import (
    Optional,
    Union,
)
from pytest import raises

# from beartype.claw._importlib.clawimpcache import module_name_to_beartype_conf
# print(f'this_submodule conf: {repr(module_name_to_beartype_conf)}')

# ....................{ FUNCTIONS                          }....................
def thee_ever_and_thee_only(i_have_watched: Union[float, bytes]) -> (
    Optional[complex]):
    '''
    Arbitrary method either returning the passed float first doubled and then
    coerced into a complex number with imaginary component ``1`` if this float
    is non-zero *or* raising a :exc:`.BeartypeCallHintParamViolation` exception
    otherwise (i.e., if this float is zero), exercising that beartype import
    hooks decorate global functions as expected.
    '''

    def thy_shadow(and_the_darkness_of_thy_steps: Optional[float]) -> (
        Union[complex, str]):
        '''
        Arbitrary closure either returning the passed float first doubled and
        then coerced into a complex number with imaginary component ``1`` if
        this float is non-:data:`None` *or* raising a
        :exc:`.BeartypeCallHintReturnViolation` exception otherwise (i.e., if
        this float is :data:`None`), exercising that beartype import hooks
        decorate closures as expected.
        '''

        # Return either...
        return (
            # If this float is "None", explicitly force this
            # @beartype-decorated closure to raise a
            # "BeartypeCallHintReturnViolation" exception;
            None
            if and_the_darkness_of_thy_steps is None else
            # Else, this float is non-"None". In this case, return this float
            # doubled and then coerced into a complex number with imaginary
            # component "1". Why? Just because. *THIS IS BEARTYPE.* Graaaah!
            i_have_watched + and_the_darkness_of_thy_steps + 1j
        )

    # Return either...
    return (
        # If this float is zero, explicitly force this @beartype-decorated
        # closure to raise a "BeartypeCallHintReturnViolation" exception.
        thy_shadow(None)
        if i_have_watched == 0.0 else
        # Else, this integer is non-zero. In this case, return this integer
        # doubled and then coerced into a complex number with imaginary
        # component "1". Why? Just because. *THIS IS BEARTYPE.* Graaaah!
        thy_shadow(i_have_watched)
    )


# Assert that calling this function passed an arbitrary float returns the
# expected complex number *WITHOUT* raising an exception.
assert thee_ever_and_thee_only(
    len('And my heart ever gazes on the depth') + 0.0) == (
    72 + 1j)

# Assert that calling this function passed an invalid parameter raises the
# expected exception.
with raises(BeartypeCallHintParamViolation):
    thee_ever_and_thee_only(len('Of thy deep mysteries. I have made my bed'))

# Assert that calling this function passed zero raises the expected exception
# from the closure defined and called by this function.
with raises(BeartypeCallHintReturnViolation):
    thee_ever_and_thee_only(
        len('In and on coffins') - len('where black death') + 0.0)
