#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`252` **non-data and data descriptor types** submodule.

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
from beartype._util.utilobjset import set_object_attr
from typing import Optional

# ....................{ EXCEPTIONS                         }....................
class TestDescriptorException(Exception):
    '''
    **Test descriptor exception.**

    This exception is raised from methods defined by test-specific data and
    non-data descriptors declared by this submodule.
    '''

    pass

# ....................{ DESCRIPTORS                        }....................
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
    :meth:`.__get__` *and* :meth:`.__set__` dunder methods implicitly called by
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
        set_object_attr(obj, self._attr_name, value)

# ....................{ DESCRIPTORS ~ str                  }....................
class DataDescriptorStr(object):
    '''
    **String data descriptor** (i.e., pure-Python type defining both the
    :meth:`.__get__` *and* :meth:`.__set__` dunder method implicitly called by
    Python when instances of this type are assigned to class variables and then
    subsequently accessed or modified respectively via those class variables
    whose values are strings on instances of those classes).

    String data descriptors encapsulate mutable instance and class variables
    whose string values require dynamic computation and which can be externally
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
        Initialize this string data descriptor.

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

        # A one-liner that invited disaster.
        return f'DataDescriptorStr({repr(self._attr_name)})'


    def __get__(
        self,
        obj: object,
        obj_type_if_instance_lookup: Optional[type] = None,
    ) -> str:
        '''
        String value of the attribute bound to the passed object whose
        unqualified basename is that of the basename with which this descriptor
        was initialized.

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

        # Through the storm, one-liner will find a way.
        return getattr(obj, self._attr_name)


    def __set__(self, obj: object, text: str) -> None:
        '''
        Set the string value of the attribute bound to the passed object whose
        unqualified basename is that of the basename with which this descriptor
        was initialized to the passed value.

        Parameters
        ----------
        obj : object
            Object to modify this attribute on.
        text : object
            Value to modify this attribute to.

        Raises
        ------
        TestDescriptorException
            If the passed value is *not* a string.
        '''

        # If the passed value is *NOT* a string, raise an exception.
        if not isinstance(text, str):
            raise TestDescriptorException(f'{repr(text)} not string.')
        # Else, this value is a string.

        # Set this string as the value of the attribute with this name bound to
        # the passed object.
        set_object_attr(obj, self._attr_name, text)

# ....................{ DESCRIPTORS ~ str : swap           }....................
class _Pep557CompatibleDataDescriptorABC(object):
    '''
    **Dataclass-compatible data descriptor abstract base class** (i.e.,
    superclass of concrete subclasses below satisfying the data descriptor
    protocol in a portable manner compatible with :pep:`557`-compliant
    dataclasses, whose obscure implementation imposes non-trivial constraints on
    descriptor-typed fields in particular).

    Data descriptors encapsulate mutable instance and class variables whose
    values require dynamic computation and which can be externally modified.
    This ABC defines both the :meth:`.__get__` *and* :meth:`.__set__` dunder
    methods implicitly called by Python when instances of this type are assigned
    to class variables and then subsequently accessed or modified respectively
    with those class variables on instances of those classes.

    Caveats
    -------
    **All methods defined by this ABC are intentionally left unannotated.**
    Doing so enables unit tests to explicitly test unannotated data descriptors,
    which tend to exhibit different semantics in common use cases (e.g.,
    descriptor-typed fields).

    Attributes
    ----------
    _attr_name : str
        Unqualified basename of the variable this descriptor dynamically
        accesses on both classes and instances to which this descriptor is
        bound.
    _default_value : str, default: SENTINEL
        Default value to which this descriptor initializes that lower-level
        variable. Defaults to the sentinel placeholder, in which case this
        descriptor remains uninitialized by default.
    '''

    def __init__(self, default_value = None):  # <-- look, ma! no type hints!
        '''
        Initialize this string case-swapping data descriptor.

        Parameters
        ----------
        default_value : Optional[str], default: None
            Default value to which this descriptor initializes the lower-level
            variable dynamically accessed by this descriptor. Defaults to
            :data:`None`, in which case this descriptor remains uninitialized by
            default.
        '''

        # Classify all passed parameters.
        self._default_value = default_value
        # print(f'default_value = {repr(default_value)}')

        # Nullify the "_attr_name" instance variable set by the __set_name__()
        # dunder method in a safe manner preserving that variable if already set
        # by a prior call of that method. Python: "It do be complicated."
        self._attr_name = getattr(self, '_attr_name', None)


    def __set_name__(self, cls, attr_name):  # <-- no sleep till type hints
        '''
        Set the unqualified basename of the variable that this descriptor
        dynamically accesses on both classes and instances to which this
        descriptor is bound to the passed basename.

        The standard :class:`type.__new__` constructor explicitly calls this
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


    def __repr__(self):
        '''
        Machine-readable representation of this data descriptor.
        '''

        # Aloft on the divine wing of a one-liner! Arise, we beg this!
        return f'{self.__class__.__name__}({repr(self._attr_name)})'


    def __get__(self, obj, obj_type_if_instance_lookup = None):  # *NO HINTS YO*
        '''
        Value of the variable bound to the passed object whose unqualified
        basename is that of the basename with which this descriptor was
        initialized.

        Parameters
        ----------
        obj : object
            Object to retrieve this variable from.
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
        if self._default_value is not None:
            # print(f'Returning default value {repr(self._default_value)}...')
            return self._default_value
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

        # Return the current value of the attribute bound to the passed object.
        value = getattr(obj, self._attr_name)
        # print(f'Getting attribute {repr(value)}...')
        return value


    def __set__(self, obj, value):  # <-- no hints, no qa, no service
        '''
        Set the value of the variable bound to the passed object whose
        unqualified basename is that of the basename with which this descriptor
        was initialized to the passed value.

        Parameters
        ----------
        obj : object
            Object to modify this variable on.
        value : object
            Value to modify this variable to.
        '''
        # print(f'Setting attribute to {repr(value)}...')

        # Safely set this object attribute to the passed value.
        set_object_attr(obj, self._attr_name, value)

        # Nullify any default value with which this descriptor was initialized,
        # preventing the next call to the __get__() dunder method from
        # erroneously returning this default value if previously defined.
        self._default_value = None


class Pep557FriendlyDataDescriptorUnhinted(_Pep557CompatibleDataDescriptorABC):
    '''
    **Unannotated data descriptor** (i.e., pure-Python type defining both the
    :meth:`.__get__` *and* :meth:`.__set__` dunder methods implicitly called by
    Python when instances of this type are assigned to class variables and then
    subsequently accessed or modified respectively via those class variables on
    instances of those classes, where those dunder methods are intentionally
    left unannotated by *any* type hints to enable unit tests defined elsewhere
    to exercise various edge cases).
    '''

    pass


class Pep557FriendlyDataDescriptorStrSwapCase(
    _Pep557CompatibleDataDescriptorABC):
    '''
    **String case-swapping data descriptor** (i.e., pure-Python type defining
    both the :meth:`.__get__` *and* :meth:`.__set__` dunder methods implicitly
    called by Python when instances of this type are assigned to class variables
    and then subsequently accessed or modified respectively with those class
    variables on instances of those classes such that that :meth:`.__get__`
    dunder method returns a string and that :meth:`.__set__` dunder method
    accepts a string whose case is swapped by that method).

    This data descriptor specifically **swaps case** (i.e., converts uppercase
    characters to lowercase and lowercase characters to uppercase) of the string
    passed to the :meth:`.__set__` dunder method, enabling callers to validate
    that that method performed meaningful work and was thus called.
    '''

    def __init__(self, default_value: Optional[str] = None) -> None:

        # If the caller explicitly passed a default string with which to
        # initialize this descriptor...
        if default_value is not None:
            # If the passed default value is *NOT* a string, raise an exception.
            if not isinstance(default_value, str):
                raise TestDescriptorException(
                    f'{repr(default_value)} not string.')
            # Else, this default value is a string.

            #FIXME: *NOPE*! Don't ask. We didn't. *shrug*
            # Preserve this string in case-swapped form for subsequent use.
            # default_value = default_value.swapcase()
        # Else, the caller passed *NO* such default.

        # Initialize our superclass with all passed parameters.
        super().__init__(default_value)


    def __set__(self, obj: object, value: str) -> None:
        '''
        Set the value of the variable bound to the passed object whose
        unqualified basename is that of the basename with which this descriptor
        was initialized to the case-swapped variant of the passed string.

        Parameters
        ----------
        obj : object
            Object to modify this variable on.
        value : str
            Value to modify this variable to after case-swapping.

        Raises
        ------
        TestDescriptorException
            If the passed value is *not* a string.
        '''

        # If the passed value is *NOT* a string, raise an exception.
        if not isinstance(value, str):
            raise TestDescriptorException(f'{repr(value)} not string.')
        # Else, this value is a string.

        # Swap the case of this string.
        value = value.swapcase()

        # Defer to our superclass implementation.
        super().__set__(obj, value)

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
