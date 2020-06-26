#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator** `PEP 484`_ **getters.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
# from beartype.cave import (ClassType,)
from beartype._util import utilobj
from beartype._util.utilcache import callable_cached
# from beartype._util.utilobj import SENTINEL
from typing import TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
@callable_cached
def is_typing(obj: object) -> bool:
    '''
    ``True`` only if the passed object is a `PEP 484`_-specific type (i.e.,
    public class defined by the stdlib :mod:`typing` module).

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
    484`_-specific types. Moreover, neither `PEP 484`_ nor :mod:`typing`
    provide public APIs for testing whether arbitrary objects comply with
    `PEP 484`_ or :mod:`typing`.

    Thus this tester function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    obj : object
        Object to be inspected for `PEP 484` compliance.

    Returns
    ----------
    bool
        ``True`` only if this object is a `PEP 484`_-specific type.

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


@callable_cached
def is_typing_typevar(obj: object) -> bool:
    '''
    ``True`` only if the passed object either is a `PEP 484`_-specific **type
    variable** (i.e., instance of the :mod:`typing.TypeVar` class) *or* is a
    `PEP 484`_-specific type parametrized by one or more type variables (e.g.,
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
        `PEP 484`_-specific type to be inspected for type variables.

    Returns
    ----------
    bool
        ``True`` only if this type either is a type variable or has been
        parametrized by one or more type variables.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Return true only if this type either...
    return (
        # Is a type variable *OR*...
        isinstance(obj, TypeVar) or
        # Has been parametrized by one or more type variables, trivially
        # equivalent to whether the tuple of all type variables parametrizing
        # this "typing" type if this type is a generic (e.g.,
        # "typing._GenericAlias" subtype) *OR* the empty tuple otherwise is
        # non-empty.
        #
        # Note that the "typing._GenericAlias.__parameters__" dunder attribute
        # tested here is defined by the typing._collect_type_vars() function at
        # subtype declaration time.
        len(getattr(obj, '__parameters__', ())) > 0
    )
