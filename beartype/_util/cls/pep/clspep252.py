#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`252`-compliant **descriptor utilities** (i.e., low-level
callables introspecting various properties of both non-data descriptor types
defining *only* the ``__get__()`` dunder method *and* data descriptor types
defining both that and the ``__set__()`` dunder method).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.cls.pep.pep544.dataclspep544descriptor import (
    Pep544DescriptorData,
    Pep544DescriptorNondata,
)
from beartype._data.typing.datatypingport import TypeIs

# ....................{ HINTS                              }....................
TypePep252DescriptorData = type[Pep544DescriptorData]
'''
:pep:`585`-compliant type hint matching a :pep:`252`-compliant **data
descriptor** (i.e., type defining both the ``__get__`` and ``__set__`` dunder
methods required to satisfy the data descriptor protocol).
'''


TypePep252DescriptorNondata = type[Pep544DescriptorNondata]
'''
:pep:`585`-compliant type hint matching a :pep:`252`-compliant **non-data
descriptor** (i.e., type defining only the ``__get__`` but *not* ``__set__``
dunder methods required to satisfy the non-data descriptor protocol).
'''

# ....................{ TESTERS ~ type                     }....................
def is_type_pep252_descriptor_data(
    cls: type) -> TypeIs[TypePep252DescriptorData]:
    '''
    :data:`True` only if the passed type is a :pep:`252`-compliant **data
    descriptor** (i.e., type defining both the ``__get__`` and ``__set__``
    dunder methods required to satisfy the data descriptor protocol).

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this type is a data descriptor.

    See Also
    --------
    https://docs.python.org/3/howto/descriptor.html
        Python's official descriptor guide.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'

    # Return true only if this type satisfies the data descriptor protocol by
    # defining both the __get__() and __set__() dunder methods.
    return issubclass(cls, Pep544DescriptorData)  # type: ignore[misc]


def is_type_pep252_descriptor_nondata(
    cls: type) -> TypeIs[TypePep252DescriptorNondata]:
    '''
    :data:`True` only if the passed type is a :pep:`252`-compliant **non-data
    descriptor** (i.e., type defining only the ``__get__`` but *not* ``__set__``
    dunder methods required to satisfy the non-data descriptor protocol).

    Parameters
    ----------
    cls : type
        Type to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this type is a non-data descriptor.

    See Also
    --------
    https://docs.python.org/3/howto/descriptor.html
        Python's official descriptor guide.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'

    # Return true only if...
    return (
        # This type satisfies the non-data descriptor protocol by defining at
        # least the __get__() dunder method *AND*...
        issubclass(cls, Pep544DescriptorNondata) and not  # type: ignore[misc]
        # This type violates the data descriptor protocol by failing to also
        # define the __set__() dunder method.
        issubclass(cls, Pep544DescriptorData)  # type: ignore[misc]
    )

# ....................{ TESTERS ~ instance                 }....................
def is_object_pep252_descriptor_data_instance(
    obj: object) -> TypeIs[Pep544DescriptorData]:
    '''
    :data:`True` only if the passed object is a :pep:`252`-compliant **data
    descriptor instance** (i.e., object whose type defines both the ``__get__``
    and ``__set__`` dunder methods required to satisfy the data descriptor
    protocol).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a data descriptor.

    See Also
    --------
    https://docs.python.org/3/howto/descriptor.html
        Python's official descriptor guide.
    '''

    # Return true only if this object satisfies the data descriptor protocol by
    # defining both the __get__() and __set__() dunder methods.
    return isinstance(obj, Pep544DescriptorData)  # type: ignore[misc]


def is_object_pep252_descriptor_nondata_instance(
    obj: object) -> TypeIs[Pep544DescriptorNondata]:
    '''
    :data:`True` only if the passed object is a :pep:`252`-compliant **non-data
    descriptor instance** (i.e., object whose type defines only the ``__get__``
    but *not* ``__set__`` dunder methods required to satisfy the non-data
    descriptor protocol).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a non-data descriptor.

    See Also
    --------
    https://docs.python.org/3/howto/descriptor.html
        Python's official descriptor guide.
    '''

    # Return true only if...
    return (
        # This object satisfies the non-data descriptor protocol by defining at
        # least the __get__() dunder method *AND*...
        isinstance(obj, Pep544DescriptorNondata) and not  # type: ignore[misc]
        # This object violates the data descriptor protocol by failing to also
        # define the __set__() dunder method.
        isinstance(obj, Pep544DescriptorData)  # type: ignore[misc]
    )
