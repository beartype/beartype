#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator** `PEP 484`_ **testers.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
# from beartype.cave import (ClassType,)
from beartype.roar import BeartypeDecorPep484TypeUnsupportedException
from beartype._util import utilobj
from beartype._util.utilcache import callable_cached
# from beartype._util.utilobj import SENTINEL
from typing import TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ EXCEPTIONS                        }....................
def die_if_typing_unsupported(obj: object) -> None:
    '''
    Raise an exception if the passed object is a `PEP 484`_ type (i.e., class
    or object declared by the stdlib :mod:`typing` module) currently
    unsupported by the :func:`beartype.beartype` decorator.

    This includes:

    * **Type variables** (i.e., instances of the :mod:`typing.TypeVar` class).
    * `PEP 484`_ types parametrized by one or more type variables (e.g.,
      ``typing.List[typing.TypeVar['T']]``).

    Parameters
    ----------
    obj : object
        Object to be validated.

    Raises
    ----------
    BeartypeDecorPep484TypeUnsupportedException
        If this object is an unsupported `PEP 484`_ type.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Template for exception messages raised by this function.
    EXCEPTION_MESSAGE_TEMPLATE = '{} currently unsupported by @beartype.'

    # If this object is either a PEP 484 type variable *OR* PEP 484 type
    # parametrized by one or more such variables, raise an exception.
    if is_typing_typevar(obj):
        raise BeartypeDecorPep484TypeUnsupportedException(
            EXCEPTION_MESSAGE_TEMPLATE.format(
                'Type variable {!r}'.format(obj)))
    # Else if this object is a PEP 484 type parametrized by one or more such
    # variables, raise an exception.
    elif is_typing_args_typevar(obj):
        raise BeartypeDecorPep484TypeUnsupportedException(
            EXCEPTION_MESSAGE_TEMPLATE.format(
                'Generic parametrized by '
                'one or more type variables {!r}'.format(obj)))

# ....................{ TESTERS                           }....................
#FIXME: Detect functions created by "typing.NewType(subclass_name, superclass)"
#somehow, either here or elsewhere. These functions are simply the identity
#function at runtime and thus a complete farce. They're not actually types!
#Ideally, we would replace each such function by the underlying "superclass"
#type originally passed to that function, but we have no idea if that's even
#feasible. Welcome to "typing", friends.

@callable_cached
def is_typing(obj: object) -> bool:
    '''
    ``True`` only if the passed object is a `PEP 484`_ type (i.e., class or
    object declared by the stdlib :mod:`typing` module).

    For efficiency, this tester is memoized.

    Motivation
    ----------
    Standard types allow callers to test for compliance with protocols,
    interfaces, and abstract base classes by calling either the
    :func:`isinstance` or :func:`issubclass` builtins. This is the
    well-established Pythonic standard for deciding conformance to an API.

    Insanely, `PEP 484`_ *and* the :mod:`typing` module implementing `PEP 484`_
    reject community standards by explicitly preventing callers from calling
    either the :func:`isinstance` or :func:`issubclass` builtins on `PEP
    484`_ types. Moreover, neither `PEP 484`_ nor :mod:`typing` implement
    public APIs for testing whether arbitrary objects comply with `PEP 484`_ or
    :mod:`typing`.

    Thus this tester function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a `PEP 484`_ type.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    obj_type = utilobj.get_obj_type(obj)

    # If this type is defined by the stdlib "typing" module, return true.
    #
    # Note that there might exist an alternate means of deciding this boolean,
    # documented here merely for completeness:
    #
    #     try:
    #         isinstance(obj, object)
    #         return False
    #     except TypeError as type_error:
    #         return str(type_error).endswith(
    #             'cannot be used with isinstance()')
    #
    # The above effectively implements an Aikido throw by using the fact that
    # "typing" types prohibit isinstance() calls against those types. While
    # clever (and deliciously obnoxious), the above logic:
    #
    # * Requires catching exceptions in the common case and is thus *MUCH* less
    #   efficient than the preferable approach implemented here.
    # * Assumes that *ALL* "typing" types prohibit such calls. Sadly, only a
    #   proper subset of such types prohibit such calls.
    # * Assumes that those "typing" types that do prohibit such calls raise
    #   exceptions with reliable messages across *ALL* Python versions.
    #
    # In short, there is no general-purpose clever solution. *sigh*
    if utilobj.get_obj_module_name_or_none(obj_type) == 'typing':
        return True

    # For each superclass of this class...
    #
    # This edge case is required to handle user-defined subclasses declared in
    # user-defined modules of superclasses declared by the "typing" module:
    #
    #    # In a user-defined module...
    #    from typing import TypeVar, Generic
    #    T = TypeVar('T')
    #    class UserDefinedGeneric(Generic[T]): pass
    for obj_type_supertype in obj_type.__mro__:
        # If this superclass is defined by "typing", return true.
        if utilobj.get_obj_module_name_or_none(obj_type_supertype) == 'typing':
            return True

    # Else, neither this type nor any superclass of this type is defined by the
    # "typing" module. Ergo, this is *NOT* a PEP 484-compliant type.
    return False

# ....................{ TESTERS ~ typevar                 }....................
#FIXME: Consider excising. Unsure if we actually require this. *sigh*
@callable_cached
def is_typing_typevarish(obj: object) -> bool:
    '''
    ``True`` only if the passed object is either a `PEP 484`_ **type variable**
    (i.e., instance of the :mod:`typing.TypeVar` class) *or* a `PEP 484`_ type
    parametrized by one or more type variables (e.g.,
    ``typing.List[typing.TypeVar['T']]``).

    For efficiency, this tester is memoized.

    Motivation
    ----------
    Since type variables are not themselves types but rather placeholders
    dynamically replaced with types by type checkers according to various
    arcane heuristics, both type variables and types parametrized by type
    variables warrant special-purpose handling.

    Parameters
    ----------
    obj : object
        Object type to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is either a type variable or `PEP 484`_
        type parametrized by one or more type variables.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Return true only if this type either...
    return (
        # Is a type variable *OR*...
        is_typing_typevar(obj) or
        # This is a "typing" type parametrized by one or more type variables.
        is_typing_args_typevar(obj)
    )


def is_typing_typevar(obj: object) -> bool:
    '''
    ``True`` only if the passed object either is a `PEP 484`_ **type variable**
    (i.e., instance of the :mod:`typing.TypeVar` class).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a type variable.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Return true only if this is a type variable.
    return isinstance(obj, TypeVar)


@callable_cached
def is_typing_args_typevar(obj: object) -> bool:
    '''
    ``True`` only if the passed object is a `PEP 484`_ type parametrized by one
    or more type variables (e.g., ``typing.List[typing.TypeVar['T']]``).

    For efficiency, this tester is memoized.

    Parameters
    ----------
    obj : object
        Object type to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is `PEP 484`_ type parametrized by one or
        more type variables.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Return true only if this is a "typing" type parametrized by one or more
    # type variables, trivially detected by testing whether the tuple of all
    # type variables parametrizing this "typing" type if this type is a generic
    # (e.g., "typing._GenericAlias" subtype) *OR* the empty tuple otherwise is
    # non-empty.
    #
    # Note that the "typing._GenericAlias.__parameters__" dunder attribute
    # tested here is defined by the typing._collect_type_vars() function at
    # subtype declaration time. Yes, this is insane. Yes, this is PEP 484.
    return is_typing(obj) and len(getattr(obj, '__parameters__', ())) > 0
