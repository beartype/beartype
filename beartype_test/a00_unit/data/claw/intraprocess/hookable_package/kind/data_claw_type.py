#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype import hookable class submodule** (i.e., data module
containing *only* annotated classes, mimicking real-world usage of the
:func:`beartype.claw.beartype_package` import hook from an external caller).
'''

# ....................{ IMPORTS                            }....................
from beartype import (
    BeartypeConf,
    # BeartypeStrategy,
    beartype,
)
from beartype.roar import (
    BeartypeCallHintParamViolation,
    BeartypeDoorHintViolation,
)
from beartype.typing import (
    Callable,
    List,
    Union,
)
from functools import wraps
from pytest import raises

# from beartype.claw._importlib.clawimpcache import module_name_to_beartype_conf
# print(f'this_submodule conf: {repr(module_name_to_beartype_conf)}')

# ....................{ CLASSES ~ default                  }....................
# Classes whose type-checking implicitly accepts the default beartype
# configuration.

#FIXME: Currently unused, but preserved for posterity.
# class AndSoDreamAllNight(object):
#     '''
#     Arbitrary class explicitly decorated by the :func:`beartype.beartype`
#     decorator assuming default parameters.
#     '''
#
#     pass

# ....................{ REFERENCES                         }....................
# Callables annotated by type hints referencing classes that have yet to be
# defined at callable definition time and are thus converted into
# beartype-specific forward references by the @beartype decorator.
#
# Note that:
# * This convoluted decorator logic exercises this non-trivial issue and is
#   thus convoluted intentionally. Attempting to simplify this logic would
#   erroneously hide this non-trivial issue:
#     https://github.com/beartype/beartype/issues/404

def coerce_func_return_to_subclass_instance(func) -> (
    'Callable[..., StrSubclass]'):
    '''
    Decorator coercing the object returned by the passed callable into an
    instance of the :class:`.StrSubclass` class that has yet to be defined at
    the time this decorator is defined.
    '''

    @wraps(func)
    def coerce_func_return_to_subclass_instance_method(
        self: 'StrSubclass', *args, **kwargs) -> 'StrSubclass':
        '''
        Method coercing the object returned by the passed callable into an
        instance of the :class:`.StrSubclass` class that has yet to be defined
        at the time this decorator is defined.
        '''

        # Coerce the value returned by that callable into an instance of the
        # type to which this method is bound.
        return type(self)(func(self, *args, **kwargs))

    # Return this method.
    return coerce_func_return_to_subclass_instance_method


class StrSubclass(str):
    '''
    Arbitrary string subclass.
    '''

    capitalize = coerce_func_return_to_subclass_instance(str.capitalize)
    '''
    :class:`str.capitalize` method coerced to return an instance of this
    :class:`.StrSubclass` subclass (rather than the :class:`str` superclass).
    '''


# Assert that the StrSubclass.capitalize() method behaves as expected.
assert StrSubclass(
    "and the night's noontide clearness, mutable").capitalize() == (
    "And the night's noontide clearness, mutable")

# ....................{ CLASSES ~ default                  }....................
# Classes whose type-checking implicitly accepts the default beartype
# configuration assumed by the remainder of this subpackage.

# ....................{ CLASSES ~ non-default              }....................
# Classes whose type-checking explicitly rejects the default beartype
# configuration assumed by the remainder of this subpackage (i.e., due to being
# decorated by the @beartype decorator explicitly configured by a non-default
# beartype configuration). In particular, these classes enable the PEP
# 484-compliant implicit numeric tower such that:
# * "float" is implicitly expanded to "float | int".
# * "complex" is implicitly expanded to "complex | float | int".

@beartype(conf=BeartypeConf(is_pep484_tower=True))  # <-- prefer non-defaults
# @beartype(conf=BeartypeConf(is_pep484_tower=True, is_debug=True))  # <-- prefer non-defaults
class HerFirstSweetKisses(object):
    '''
    Arbitrary class explicitly decorated by the :func:`beartype.beartype`
    decorator with non-default parameters.
    '''

    def if_no_bright_bird(
        self, insect_or_gentle_beast: Union[complex, str]) -> (
        Union[List[bytes], complex]):
        '''
        Arbitrary method accepting the passed object under the non-default
        beartype configuration decorating this class and returning that object
        as is, enabling callers to trivially test whether any call to this
        method violates the type hints annotating this method.
        '''

        # ....................{ PASS                       }....................
        # Implicitly assert that assigning a valid value to an annotated local
        # or global variable in a method raises *NO* exception.
        #
        # Note that this edge case is distinct from assigning to an annotated
        # instance or class variable in a method.
        his_wandering_step: int = len('More graceful than her own')

        # Implicitly assert that assigning a valid value to an annotated
        # instance or class variable in a method raises *NO* exception.
        #
        # Note that this edge case is distinct from assigning to an annotated
        # local or global variable in a method.
        self.the_awful_ruins: bytes = b'The awful ruins of the days of old:'

        # ....................{ FAIL                       }....................
        # Explicitly assert that assigning an invalid value to an annotated
        # local or global variable raises the expected exception.
        with raises(BeartypeDoorHintViolation):
            his_wandering_step: int = 'Obedient to high thoughts, has visited'

        # Explicitly assert that assigning an invalid value to an annotated
        # instance or class variable raises the expected exception.
        with raises(BeartypeDoorHintViolation):
            self.the_awful_ruins: bytes = (
                'Athens, and Tyre, and Balbec, and the waste')

        # Look, @beartype. Just do it!
        return insect_or_gentle_beast


    @beartype  # <-- prefer the default beartype configuration yet again
    def i_consciously_have_injured(
        self, but_still_loved: Union[complex, bool]) -> (
        Union[complex, List[bytes]]):
        '''
        Arbitrary method accepting the passed object under the default beartype
        configuration and returning that object as is, enabling callers to
        trivially test whether any call to this method violates the type hints
        annotating this method.
        '''

        # Look here, you. Just do it yet again!
        return but_still_loved

# ....................{ LOCALS                             }....................
# Arbitrary instances of these types defined above.
# save_from_one_gradual_solitary_gust = AndSoDreamAllNight()
and_cherished_these_my_kindred = HerFirstSweetKisses()

# ....................{ PASS                               }....................
# Assert that calling this method of this type passed an invalid parameter
# returns that parameter as is *WITHOUT* raising an exception.
assert and_cherished_these_my_kindred.if_no_bright_bird(
    len('This boast, belovèd brethren, and withdraw')) == 42

# ....................{ FAIL                               }....................
# Assert that calling the first method passed an invalid parameter raises the
# expected exception.
with raises(BeartypeCallHintParamViolation):
    and_cherished_these_my_kindred.if_no_bright_bird(
        b'No portion of your wonted favour now!')

# Assert that calling the second method passed an arbitrary complex number
# returns that complex number as is *WITHOUT* raising an exception.
assert and_cherished_these_my_kindred.i_consciously_have_injured(len(
    'Mother of this unfathomable world!') + 1j) == 34 + 1j

# Assert that calling the second method passed an invalid parameter raises the
# expected exception.
with raises(BeartypeCallHintParamViolation):
    and_cherished_these_my_kindred.i_consciously_have_injured(len(
        'Favour my solemn song, for I have loved'))
