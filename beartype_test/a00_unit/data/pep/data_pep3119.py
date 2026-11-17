#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`3119` **types** (i.e., pure-Python classes whose metaclasses
override the :pep:`3119`-compliant ``__instancecheck__()`` and/or
``__subclasscheck__()`` dunder methods).
'''

# ....................{ IMPORTS                            }....................

# ....................{ CLASSES ~ __instancecheck__()      }....................
class Pep3119NonIsinstanceableMetaclass(type):
    '''
    Metaclass overriding the :pep:`3119`-compliant ``__instancecheck__()``
    dunder method to unconditionally raise an exception, preventing classes with
    this metaclass from being passed as the second parameter to the
    :func:`isinstance` builtin.
    '''

    def __instancecheck__(self, obj: object) -> bool:
        raise TypeError(
            f'{self} not passable as second parameter to isinstance().')


class Pep3119NonIsinstanceableClass(
    object, metaclass=Pep3119NonIsinstanceableMetaclass):
    '''
    Class whose metaclass overrides the :pep:`3119`-compliant
    ``__instancecheck__()`` dunder method to unconditionally raise an exception,
    preventing this class from being passed as the second parameter to the
    :func:`isinstance` builtin.
    '''

    pass

# ....................{ CLASSES ~ __instancecheck_str__()  }....................
class _BeartypeInstancecheckStrMetaclass(type):
    '''
    Arbitrary metaclass defining the PEP-noncompliant :mod:`beartype`-specific
    ``__instancecheck_str__()`` dunder method.

    Although PEP-noncompliant, this metaclass and its subclass are intentionally
    defined in this :pep:`3119`-specific data submodule for orthogonality with
    their sibling :pep:`3119`-compliant ``__instancecheck__()`` dunder method.
    '''

    def __instancecheck_str__(
        cls: 'BeartypeInstancecheckStrClass', obj: object) -> str:
        '''
        Arbitrary ``__instancecheck_str__()`` implementation intentionally
        returning a string containing a trivially detectable substring.
        '''

        # Return the passed object coerced into a string.
        return (
            f'object {repr(obj)} not instance of '
            f'"{cls.__module__}.{cls.__name__}"; '
            f'Gaze on the empty scene as vacantly'
        )


class BeartypeInstancecheckStrClass(
    object, metaclass=_BeartypeInstancecheckStrMetaclass):
    '''
    Arbitrary class whose metaclass defines the PEP-noncompliant
    :mod:`beartype`-specific ``__instancecheck_str__()`` dunder method.
    '''

    pass

# ....................{ CLASSES ~ __subclasscheck__()      }....................
class Pep3119NonIssubclassableMetaclass(type):
    '''
    Metaclass overriding the :pep:`3119`-compliant ``__subclasscheck__()``
    dunder method to unconditionally raise an exception, preventing classes with
    this metaclass from being passed as the second parameter to the
    :func:`issubclass` builtin.
    '''

    def __subclasscheck__(self, obj: object) -> bool:
        raise TypeError(
            f'{self} not passable as second parameter to issubclass().')


class Pep3119NonIssubclassableClass(
    object, metaclass=Pep3119NonIssubclassableMetaclass):
    '''
    Class whose metaclass overrides the :pep:`3119`-compliant
    ``__subclasscheck__()`` dunder method to unconditionally raise an exception,
    preventing this class from being passed as the second parameter to the
    :func:`issubclass` builtin.
    '''

    pass
