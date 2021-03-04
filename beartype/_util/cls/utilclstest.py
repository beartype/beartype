#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Package-wide **unmemoized class tester utilities** (i.e., unmemoized and thus
efficient callables testing various properties of arbitrary classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import _BeartypeUtilTypeException
from typing import Type

# ....................{ CONSTANTS                          }....................
_MODULE_NAME_BUILTINS = 'builtins'
'''
Fully-qualified name of the module declaring all **builtins** (i.e., objects
defined by the standard :mod:`builtins` module and thus globally available by
default *without* requiring explicit importation).
'''


_MODULE_NAME_BUILTINS_DOTTED = f'{_MODULE_NAME_BUILTINS}.'
'''
Fully-qualified name of the module declaring all builtins followed by a ``.``,
defined purely as a trivial optimization for the frequently accessed
:class:`beartype._decor._cache.cachetype.Beartypistry.__setitem__` dunder
method.
'''

# ....................{ VALIDATORS                        }....................
def die_unless_type(
    # Mandatory parameters.
    cls: object,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilTypeException,
) -> None:
    '''
    Raise an exception unless the passed object is a class.

    Parameters
    ----------
    cls : object
        Object to be validated.
    exception_cls : Type[Exception]
        Type of exception to be raised. Defaults to
        :exc:`_BeartypeUtilTypeException`.

    Raises
    ----------
    exception_cls
        If this object is *not* a class.
    '''

    # If this object is *NOT* a class, raise an exception.
    if not isinstance(cls, type):
        assert isinstance(exception_cls, type), (
            'f{repr(exception_cls)} not exception class.')
        raise exception_cls(f'{repr(cls)} not class.')

# ....................{ TESTERS ~ builtin                 }....................
def is_type_builtin(cls: type) -> bool:
    '''
    ``True`` only if the passed class is **builtin** (i.e., globally accessible
    C-based type requiring *no* explicit importation).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this class is builtin.

    Raises
    ----------
    _BeartypeUtilTypeException
        If this object is *not* a class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.py.utilpymodule import (
        get_object_type_module_name_or_none)

    # If this object is *NOT* a class, raise an exception.
    die_unless_type(cls)
    # Else, this object is a class.

    # If the unqualified basename of this class is "NoneType", this is the
    # class of the "None" singleton. In this case, return false. Unlike all
    # other builtin classes, this class is globally inaccessible despite being
    # declared to be builtin:
    #     >>> import builtins
    #     >>> type(None).__name__
    #     'NoneType'
    #     >>> type(None).__module__
    #     'builtins'
    #     >>> NoneType
    #     NameError: name 'NoneType' is not defined   <---- this is balls
    #
    # This inconsistency almost certainly constitutes a bug in the CPython
    # interpreter, but it seems doubtful anyone else would see it that way and
    # almost certain everyone else would defend this edge case.
    #
    # We're *NOT* dying on that lonely hill. We obey the Law of Guido.
    if cls.__name__ == 'NoneType':
        return False
    # Else, this is *NOT* the class of the "None" singleton.

    # Fully-qualified name of the module defining this class if this class is
    # defined by a module *OR* "None" otherwise (i.e., if this class is
    # dynamically defined in-memory).
    cls_module_name = get_object_type_module_name_or_none(cls)

    # This return true only if this name is that of the "builtins" module
    # declaring all builtin classes.
    return cls_module_name == _MODULE_NAME_BUILTINS


def is_classname_builtin(classname: str) -> bool:
    '''
    ``True`` only if the passed fully-qualified classname is that of a
    **builtin type** (i.e., globally accessible C-based type requiring *no*
    explicit importation).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    classname: str
        Classname to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this classname is that of a builtin type.
    '''

    # Return true only if...
    return (
        # This classname is prefixed by "builtins." *AND*...
        classname.startswith(_MODULE_NAME_BUILTINS_DOTTED) and
        # This classname is *NOT* that of the type of the "None" singleton. See
        # is_type_builtin() for further commentary.
        classname != 'builtins.NoneType'
    )

# ....................{ TESTERS ~ isinstanceable          }....................
def is_type_isinstanceable(cls: object) -> bool:
    '''
    ``True`` only if the passed type cls is an **isinstanceable class** (i.e.,
    class whose metaclass does *not* define an ``__instancecheck__()`` dunder
    method that raises an exception).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Although the implementation does *not*
    trivially reduce to an efficient one-liner, the inefficient branch of this
    implementation *only* applies to erroneous edge cases resulting in raised
    exceptions and is thus largely ignorable.

    Caveats
    ----------
    **This tester may return false positives in unlikely edge cases.**
    Internally, this tester tests whether this class is isinstanceable by
    detecting whether passing the ``None`` singleton and this class to the
    :func:`isinstance` builtin raises an exception. If that call raises *no*
    exception, this class is probably but *not* necessarily isinstanceable.
    Since the metaclass of this class could define an ``__instancecheck__()``
    dunder method to conditionally raise exceptions except when passed the
    ``None`` singleton, there exists *no* means of ascertaining whether a class
    is fully isinstanceable in the general case. Since most classes that are
    *not* isinstanceable are unconditionally isinstanceable (i.e., the
    metaclasses of those classes define an ``__instancecheck__()`` dunder
    method to unconditionally raise exceptions), this distinction is generally
    meaningless in the real world. This test thus generally suffices.

    Parameters
    ----------
    cls : object
        Object to be tested.

    Returns
    ----------
    bool
        ``True`` only if this object is an isinstanceable class.

    See Also
    ----------
    :func:`beartype._util.hint.utilhinttest.die_unless_hint_type_isinstanceable`
        Further details.
    '''

    # If this object is *NOT* a class, return false.
    if not isinstance(cls, type):
        return False

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with die_unless_hint_type_isinstanceable().
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Attempt to pass this class as the second parameter to the isinstance()
    # builtin to decide whether or not this class is safely usable as a
    # standard class or not.
    #
    # Note that this leverages an EAFP (i.e., "It is easier to ask forgiveness
    # than permission") approach and thus imposes a minor performance penalty,
    # but that there exists *NO* faster alternative applicable to arbitrary
    # user-defined classes, whose metaclasses may define an __instancecheck__()
    # dunder method to raise exceptions and thus prohibit being passed as the
    # second parameter to the isinstance() builtin, the primary means employed
    # by @beartype wrapper functions to check arbitrary types.
    try:
        isinstance(None, cls)

        # If the prior function call raised *NO* exception, this class is
        # probably but *NOT* necessarily isinstanceable.
        return True
    # If the prior function call raised an exception, this class is *NOT*
    # isinstanceable. In this case, return false.
    except:
        return False
