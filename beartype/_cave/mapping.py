#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype cave-specific abstract base classes (ABCs).**

This submodule declares non-standard ABCs subclassed by  implementing .
'''

# ....................{ TODO                              }....................
#FIXME: As with the parallel "beartype._cave.abc" submodule, refactor the
#contents of this private submodule into the newly proposed public
#"beartype.caver" submodule. To do so:
#
#* In the "beartype.caver" submodule:
#  * Define a new make_type() function copied from the
#    betse.util.type.classes.define_class() function (but renamed, obviously).
#  * Define a new make_type_defaultdict() function copied from the
#    betse.util.type.iterable.mapping.mapcls.DefaultDict() function, but with
#    signature resembling:
#    def make_type_defaultdict(
#        name: str,
#        missing_key_maker: CallableTypes,
#        items: (Iterable, type(None)),
#    ) -> type:
#    Internally, this function should call make_type() to do so.

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeCaveNoneTypeOrKeyException,
    BeartypeCaveNoneTypeOrMutabilityException,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_NoneType = type(None)
'''
Type of the ``None`` singleton, duplicated from the :mod:`beartype.cave`
submodule to prevent cyclic import dependencies.
'''


_NoneTypes = (_NoneType,)
'''
Tuple of only the type of the ``None`` singleton.
'''

# ....................{ CLASSES                           }....................
# This class is documented in the "beartype.cave" for readability.
class _NoneTypeOrType(dict):
    '''
    :class:`NoneType` **tuple factory type** (i.e., :class:`dict` subclass,
    instances of which are dictionaries mapping from arbitrary types or tuples
    of types to the same types or tuples of types concatenated with the type of
    the ``None`` singleton).

    See Also
    ----------
    :class:`beartype.cave.NoneTypeOr`
        Full documentation for this ad-hoc collection of
        :mod:`beartype`-specific types.
    '''

    # ..................{ DUNDERS                           }..................
    def __setitem__(self, key: object, value: object) -> None:
        '''
        Dunder method explicitly called by the superclass on setting the passed
        key-value pair with``[``- and ``]``-delimited syntax.

        Specifically, this method prohibits external attempts to explicitly set
        key-value pairs on this factory by unconditionally raising an
        exception.

        Parameters
        ----------
        key : object
            Key to map this value to.
        value : object
            Value to be mapped to.

        Raises
        ----------
        BeartypeCaveNoneTypeOrMutabilityException
            Unconditionally.
        '''

        raise BeartypeCaveNoneTypeOrMutabilityException(
            '{!r} externally immutable (i.e., not settable).'.format(self))


    def __missing__(self, type_or_types: (type, tuple)) -> tuple:
        '''
        Dunder method explicitly called by the superclass
        :meth:`dict.__getitem__` method implicitly called on getting the passed
        missing key with ``[``- and ``]``-delimited syntax.

        Specifically, this method:

        * If a single type is passed:

          #. Creates a new 2-tuple containing only that type and the type of
             the ``None`` singleton.
          #. Maps the passed type to that 2-tuple.
          #. Returns that 2-tuple.

        * Else if a tuple of one or more types is passed:

          #. Creates a new tuple appending the type of the ``None`` singleton
             to the passed tuple.
          #. Maps the passed type to the new tuple.
          #. Returns the new tuple.

        * Else, raises an exception.

        Parameters
        ----------
        type_or_types : (type, tuple)
            Type or tuple of types *not* currently cached by this factory.

        Returns
        ----------
        tuple
            Tuple of types appending the type of the ``None`` singleton to the
            passed type or tuple of types.

        Raises
        ----------
        BeartypeCaveNoneTypeOrKeyException
            If this key is either the empty tuple *or* neither a:

            * **Type** (i.e., :class:`beartype.cave.ClassType` instance).
            * **Tuple of types** (i.e., :class:`tuple` whose items are all
              :class:`beartype.cave.ClassType` instances).
        '''

        # Tuple of types to be cached and returned by this call.
        type_or_types_or_none = None

        # If this key is a type...
        if isinstance(type_or_types, type):
            # If this type is "NoneType", reuse the existing "_NoneTypes" tuple
            # containing only this type.
            if type_or_types is _NoneType:
                type_or_types_or_none = _NoneTypes
            # Else, this type is *NOT* "NoneType". In this case, instantiate a
            # new tuple of types concatenating this type with "NoneType".
            else:
                type_or_types_or_none = (type_or_types, _NoneType)
        # Else if this key is a tuple...
        elif isinstance(type_or_types, tuple):
            # If this tuple is empty, raise an exception.
            if not type_or_types:
                raise BeartypeCaveNoneTypeOrKeyException(
                    '"NoneTypeOr" key {!r} is empty tuple.'.format(
                        type_or_types))

            # If any item of this tuple is *NOT* a type...
            if any(not isinstance(item, type) for item in type_or_types):
                # For each item of this tuple...
                for item in type_or_types:
                    # If this is the first item of this tuple that is *NOT* a
                    # type, raise a human-readable exception.
                    if not isinstance(item, type):
                        raise BeartypeCaveNoneTypeOrKeyException(
                            '"NoneTypeOr" key {!r} item {!r} not a '
                            'type.'.format(type_or_types, item))
            # Else, all items of this tuple are types.

            # If "NoneType" is already in this tuple, use this tuple as is.
            if _NoneType in type_or_types:
                type_or_types_or_none = type_or_types
            # Else, "NoneType" is *NOT* already in this tuple. In this case,
            # instantiate a new tuple of types concatenating this tuple with
            # "NoneType".
            else:
                type_or_types_or_none = type_or_types + _NoneTypes
        # Else, this key is neither a type nor tuple and is thus invalid. In
        # this case, raise a human-readable exception.
        else:
            raise BeartypeCaveNoneTypeOrKeyException(
                '"NoneTypeOr" key {!r} neither a '
                'type nor tuple of types.'.format(type_or_types))

        # Return this new tuple of types.
        #
        # The superclass dict.__getitem__() dunder method then implicitly maps
        # the passed missing key to this new tuple of types by effectively:
        #     self[type_or_types] = type_or_types_or_none
        return type_or_types_or_none
