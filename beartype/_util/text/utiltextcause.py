#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype text cause utilities** (i.e., callables generating human-readable
error messages describing the failure of an arbitrary object referred to as the
"pith" to satisfy the constraints implied by another object referred to as the
"hint").

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeCallHintRaiseException
from beartype._util.hint.nonpep.utilhintnonpeptest import (
    die_unless_hint_nonpep_tuple)
from beartype._util.text.utiltextjoin import join_delimited_disjunction_classes
from beartype._util.text.utiltextlabel import label_class
from beartype._util.text.utiltextrepr import represent_object
from typing import Tuple

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_object_representation(pith: object) -> str:
    '''
    Truncated machine-readable representation of the passed arbitrary object,
    intended to be embedded in a human-readable error message describing the
    failure of this object to satisfy one or more caller-defined constraints.

    Parameters
    ----------
    pith : object
        Object to be represented.

    Returns
    ----------
    str
        Truncated machine-readable representation of this object.
    '''

    # Return the machine-readable representation of this object.
    return f'value {represent_object(pith)}'

# ....................{ GETTERS ~ type                    }....................
#FIXME: Unit test us up.
def get_cause_object_not_type(pith: object, hint: type) -> str:
    '''
    Human-readable error message describing the failure of the passed arbitrary
    object to satisfy (i.e., be an instance of) the passed class.

    Parameters
    ----------
    pith : object
        Object to be described as *not* an instance of this class.
    hint : type
        Class to describe this object as *not* being an instance of.

    Returns
    ----------
    str
        Human-readable error message describing this failure.

    Raises
    ----------
    _BeartypeCallHintRaiseException
        If either:

        * This class is *not* actually a class.
        * This object is actually an instance of this class.
    '''

    # If this hint is *NOT* a class, raise an exception.
    if not isinstance(hint, type):
        raise _BeartypeCallHintRaiseException(
            f'Non-PEP type hint {repr(hint)} not class.')
    # Else, this hint is a class.
    #
    # If this pith is actually an instance of this class, raise an exception.
    elif isinstance(pith, hint):
        raise _BeartypeCallHintRaiseException(
            f'{represent_object(pith)} instance of '
            f'non-PEP type hint {repr(hint)}.'
        )
    # Else, this pith is *NOT* an instance of this type.

    # Return a substring describing this failure intended to be embedded in a
    # longer string.
    return f'{get_cause_object_representation(pith)} not {label_class(hint)}'


#FIXME: Unit test us up.
def get_cause_object_not_nonpep_tuple(
    pith: object, hint: Tuple[type, ...]) -> str:
    '''
    Human-readable error message describing the failure of the passed arbitrary
    object to satisfy (i.e., be an instance of at least one of the items of)
    the passed PEP-noncompliant tuple of classes.

    Parameters
    ----------
    pith : object
        Object to be described as *not* an instance of at least of the items of
        this tuple.
    hint : Tuple[type]
        Tuple of classes to describe this object as *not* being an instance of.

    Returns
    ----------
    str
        Human-readable error message describing this failure.

    Raises
    ----------
    _BeartypeCallHintRaiseException
        If either:

        * This tuple is *not* actually a tuple.
        * This tuple contains one or more non-classes.
        * This object is actually an instance of at least one items of this
          tuple.
    '''

    # If this hint is *NOT* a PEP-noncompliant tuple of classes, raise an
    # exception.
    die_unless_hint_nonpep_tuple(
        hint=hint,
        is_str_valid=False,
        exception_cls=_BeartypeCallHintRaiseException,
    )
    # Else, this hint is a PEP-noncompliant tuple of classes.

    # If this pith is an instance of one or more of the classes listed by this
    # tuple, raise an exception.
    if isinstance(pith, hint):
        raise _BeartypeCallHintRaiseException(
            f'{represent_object(pith)} instance of one or more '
            f'classes in non-PEP tuple union:\n{repr(hint)}'
        )
    # Else, this pith is *NOT* an instance of one or more of the classes listed
    # by this tuple.

    # Return a substring describing this failure intended to be embedded in a
    # longer string.
    return (
        f'{get_cause_object_representation(pith)} not '
        f'{join_delimited_disjunction_classes(hint)}'
    )
