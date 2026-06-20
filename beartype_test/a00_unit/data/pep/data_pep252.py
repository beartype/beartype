#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`252` **non-data and data descriptor types submodule.**

This submodule defines :pep:`252`-compliant:

* **Non-data descriptors** (i.e., pure-Python types defining the ``__get__()``
  dunder method implicitly called by Python when instances of these types are
  assigned to class variables and then subsequently accessed via those class
  variables on instances of those classes).
* **Data descriptors** (i.e., pure-Python types defining both the ``__get__()``
  *and* ``__set__()`` dunder method implicitly called by Python when instances
  of these types are assigned to class variables and then subsequently accessed
  or modified respectively via those class variables on instances of those
  classes).
'''

# ....................{ IMPORTS                            }....................
from typing import Optional

# ....................{ CLASSES ~ descriptor               }....................
class NondataDescriptor(object):
    '''
    **Non-data descriptor** (i.e., pure-Python type defining the
    :meth:`.__get__` dunder method implicitly called by Python when instances of
    this type are assigned to class variables and then subsequently accessed via
    those class variables on instances of those classes).

    Non-data descriptors encapsulate immutable instance and class variables
    whose values require dynamic computation but which cannot be externally
    modified.

    Attributes
    ----------
    _attr_name : str
        Unqualified basename of the attribute that this descriptor dynamically
        looks up on both classes and instances to which this descriptor is
        bound.
    '''

    def __init__(self, attr_name: str) -> None:
        '''
        Initialize this non-data descriptor.

        Parameters
        ----------
        attr_name : str
            Unqualified basename of the attribute that this descriptor
            dynamically looks up on both classes and instances to which this
            descriptor is bound.
        '''
        assert isinstance(attr_name, str), f'{repr(attr_name)} not string.'

        # Classify all passed parameters.
        self._attr_name = attr_name


    def __repr__(self) -> str:
        '''
        Machine-readable representation of this non-data descriptor.
        '''

        # Samsara by way of the one-liner.
        return f'NondataDescriptor({repr(self._attr_name)})'


    def __get__(
        self,
        obj: object,
        obj_type_if_instance_lookup: Optional[type] = None,
    ) -> object:
        '''
        Value of the attribute bound to the passed object whose unqualified
        basename is that of the basename with which this descriptor was
        initialized.

        Parameters
        ----------
        obj : object
            Object to retrieve this attribute from.
        obj_type_if_instance_lookup : Optional[type], default: None
            Either:

            * If this attribute was looked up as an **instance variable** (i.e.,
              on the instance of the pure-Python type to which this descriptor
              was bound as a class variable), that type.
            * If this attribute was looked up as a **class variable** (i.e., on
              the pure-Python type to which this descriptor was bound as a class
              variable), :data:`None`.

            This parameter thus enables this method to differentiate between
            instance and class variable lookup. Defaults to :data:`None`.
        '''

        # Trivialize it with conviviality, one-liner!
        return getattr(obj, self._attr_name)


class DataDescriptor(NondataDescriptor):
    '''
    **Data descriptor** (i.e., pure-Python type defining both the
    :meth:`.__get__` *and* :meth:`.__set__` dunder method implicitly called by
    Python when instances of this type are assigned to class variables and then
    subsequently accessed or modified respectively via those class variables on
    instances of those classes).

    Data descriptors encapsulate mutable instance and class variables whose
    values require dynamic computation and which can be externally modified.
    '''

    def __repr__(self) -> str:
        '''
        Machine-readable representation of this data descriptor.
        '''

        # A prison made of one-liners is no prison!
        return f'DataDescriptor({repr(self._attr_name)})'


    def __set__(self, obj: object, value: object) -> None:
        '''
        Set the value of the attribute bound to the passed object whose
        unqualified basename is that of the basename with which this descriptor
        was initialized to the passed value.

        Parameters
        ----------
        obj : object
            Object to modify this attribute on.
        value : object
            Value to modify this attribute to.
        '''

        # One-liner or it didn't happen.
        setattr(obj, self._attr_name, value)

# ....................{ CLASSES ~ descriptor : str         }....................
class DataDescriptorStrSelfSwapCase(object):
    '''
    **String case-swapping data descriptor** (i.e., pure-Python type defining
    both the :meth:`.__get__` *and* :meth:`.__set__` dunder method implicitly
    called by Python when instances of this type are assigned to class variables
    and then subsequently accessed or modified respectively via those class
    variables on instances of those classes such that that :meth:`.__get__`
    dunder method returns a string and that :meth:`.__set__` dunder method
    accepts a string whose case is swapped by that method).

    This data descriptor specifically **swaps case** (i.e., converts uppercase
    characters to lowercase and lowercase characters to uppercase) of the string
    passed to the :meth:`.__set__` dunder method, enabling callers to validate
    that that method performed meaningful work and was thus called.

    Attributes
    ----------
    _attr_name : str
        Unqualified basename of the attribute that this descriptor dynamically
        looks up on both classes and instances to which this descriptor is
        bound.
    _text_default : str, default: SENTINEL
        Default string with which to initialize this descriptor. Defaults to
        the sentinel placeholder, in which case this descriptor remains
        uninitialized by default.
    '''

    def __init__(self, text_default: Optional[str] = None) -> None:
        '''
        Initialize this string case-swapping data descriptor.

        Parameters
        ----------
        text_default : Optional[str], default: None
            Default string with which to initialize this descriptor. Defaults to
            :data:`None`, in which case this descriptor remains uninitialized by
            default.
        '''

        # Classify all passed parameters.
        self._text_default = text_default

        # If passed a default string with which to initialize this descriptor,
        # preserve this default string in case-swapped form for subsequent use.
        if self._text_default is not None:
            self._text_default = self._text_default.swapcase()


    def __set_name__(self, cls: type, attr_name: str) -> None:
        '''
        Set the unqualified basename of the attribute that this descriptor
        dynamically looks up on both classes and instances to which this
        descriptor is bound to the passed basename.

        The :class:`type.__new__` constructor explicitly calls this
        :pep:`487`-compliant dunder method on each class variable whose value is
        an instance of this descriptor *after* otherwise constructing that
        class.

        Parameters
        ----------
        cls : type
            Currently constructed class defining a class variable whose value is
            an instance of this descriptor.
        attr_name: str
            Value to modify this attribute to.
        '''

        # Classify this attribute name, privatized to avoid erroneously
        # overwriting the instance of this descriptor already defined as this
        # possibly public class variable.
        self._attr_name = f'_{attr_name}'


    def __repr__(self) -> str:
        '''
        Machine-readable representation of this data descriptor.
        '''

        # Aloft on the divine wing of a one-liner! Arise, we beg this!
        return f'DataDescriptorStrSelfSwapCase({repr(self._attr_name)})'


    def __get__(
        self,
        obj: object,
        obj_type_if_instance_lookup: Optional[type] = None,
    ) -> str:
        '''
        Case-swapped string value of the attribute bound to the passed object
        whose unqualified basename is that of the basename with which this
        descriptor was initialized.

        Parameters
        ----------
        obj : object
            Object to retrieve this attribute from.
        obj_type_if_instance_lookup : Optional[type], default: None
            Either:

            * If this attribute was looked up as an **instance variable** (i.e.,
              on the instance of the pure-Python type to which this descriptor
              was bound as a class variable), that type.
            * If this attribute was looked up as a **class variable** (i.e., on
              the pure-Python type to which this descriptor was bound as a class
              variable), :data:`None`.

            This parameter thus enables this method to differentiate between
            instance and class variable lookup. Defaults to :data:`None`.
        '''

        # If *NO* object was passed, this is an obscure calling convention that
        # we frankly do *NOT* understand. The PEP 557-compliant
        # @dataclasses.dataclass decorator (which we test by defining a
        # descriptor-typed field annotated by this descriptor and assigned an
        # instance of this descriptor) appears to profitably leverage this
        # obscurity by calling this dunder method on dataclass initialization
        # with an object explicitly set to "None", which this method is expected
        # to respond to by returning the default value with which this
        # descriptor was initialized. Ergo, we do just that. Ignorance is bliss.
        if self._text_default is not None:
            return self._text_default
        # Else, an object was passed. Thank the Pythonic Gods.
        #
        # If this attribute was looked up as a class variable, return this
        # descriptor instance as is.
        #
        # Note that returning this descriptor instance violates the return
        # hint annotating this dunder method. This enables callers to test
        # that type-checking is behaving as expected. It's intentional! Srsly.
        elif obj_type_if_instance_lookup is None:
            return self
        # Else, this attribute was looked up as an instance variable.

        # Return the current string value of the attribute bound to the passed
        # object.
        return getattr(obj, self._attr_name)


    def __set__(self, obj: object, text: str) -> None:
        '''
        Set the value of the attribute bound to the passed object whose
        unqualified basename is that of the basename with which this descriptor
        was initialized to the case-swapped variant of the passed string.

        Parameters
        ----------
        obj : object
            Object to modify this attribute on.
        text : str
            Value to modify this attribute to after case-swapping.
        '''

        # SO MUCH FOR TODAY.
        setattr(obj, self._attr_name, text.swapcase())

# ....................{ CLASSES ~ store                    }....................
class DataAndNondataDescriptorStore(object):
    '''
    **Data and non-data descriptor store** (i.e., arbitrary class defining class
    variables bound to instances of both data and non-data descriptors).
    '''

    var_readonly = NondataDescriptor(attr_name='attr_readonly')
    '''
    Arbitrary class variable bound to a data descriptor instance providing
    immutable dynamic access to the attribute with the initialized name on both
    this class and instances of this class.
    '''

    var_writable = DataDescriptor(attr_name='attr_writeable')
    '''
    Arbitrary class variable bound to a data descriptor instance providing
    mutable dynamic access to the attribute with the initialized name on both
    this class and instances of this class.
    '''
