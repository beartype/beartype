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
from beartype._util.hint.nonpep.utilhintnonpeptest import die_unless_hint_nonpep

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


    def __missing__(self, hint: (type, tuple)) -> tuple:
        '''
        Dunder method explicitly called by the superclass
        :meth:`dict.__getitem__` method implicitly called on getting the passed
        missing key with ``[``- and ``]``-delimited syntax.

        Specifically, this method:

        * If a single type or string is passed:

          #. Creates a new 2-tuple containing only that object and the type of
             the ``None`` singleton.
          #. Maps the passed type to that 2-tuple.
          #. Returns that 2-tuple.

        * Else if a tuple of one or more types and/or strings is passed:

          #. Creates a new tuple appending the type of the ``None`` singleton
             to the passed tuple.
          #. Maps the passed type to the new tuple.
          #. Returns the new tuple.

        * Else, raises an exception.

        Parameters
        ----------
        hint : (type, str, tuple)
            Type, string, or tuple of one or more types and/or strings *not*
            currently cached by this factory.

        Returns
        ----------
        tuple
            Tuple of types appending the type of the ``None`` singleton to the
            passed type, string, or tuple of types and/or strings.

        Raises
        ----------
        BeartypeCaveNoneTypeOrKeyException
            If this key is neither:

            * A **string** (i.e., forward reference specified as either a
              fully-qualified or unqualified classname).
            * A **type** (i.e., class).
            * A **non-empty tuple** (i.e., semantic union of types) containing
              only strings and types.
        '''

        # If this missing key is *NOT* a PEP-noncompliant type hint, raise an
        # exception.
        die_unless_hint_nonpep(
            hint=hint,
            hint_label='"NoneTypeOr" key',
            exception_cls=BeartypeCaveNoneTypeOrKeyException,
        )

        # Tuple of types to be cached and returned by this call.
        hint_or_none = None

        # If this key is a type...
        if isinstance(hint, type):
            # If this type is "NoneType", reuse the existing "_NoneTypes" tuple
            # containing only this type.
            if hint is _NoneType:
                hint_or_none = _NoneTypes
            # Else, this type is *NOT* "NoneType". In this case, instantiate a
            # new tuple of types concatenating this type with "NoneType".
            else:
                hint_or_none = (hint, _NoneType)
        # Else if this key is a non-empty tuple...
        elif isinstance(hint, tuple):
            # If "NoneType" is already in this tuple, reuse this tuple as is.
            if _NoneType in hint:
                hint_or_none = hint
            # Else, "NoneType" is *NOT* already in this tuple. In this case,
            # instantiate a new tuple of types concatenating this tuple with
            # "NoneType".
            else:
                hint_or_none = hint + _NoneTypes
        # Else, this key is invalid. Thanks to the above call to the
        # die_unless_hint_nonpep() function, this should *NEVER* occur.
        # Nonetheless, raise a human-readable exception for sanity.
        else:
            raise BeartypeCaveNoneTypeOrKeyException(
                '"NoneTypeOr" key {!r} unsupported.'.format(hint))

        # Return this new tuple.
        #
        # The superclass dict.__getitem__() dunder method then implicitly maps
        # the passed missing key to this new tuple of types by effectively:
        #     self[hint] = hint_or_none
        return hint_or_none
