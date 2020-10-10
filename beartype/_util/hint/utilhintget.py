#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint getter utilities** (i.e., callables querying
arbitrary objects for attributes specific to PEP-agnostic type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintException
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTR_TO_TYPE_ORIGIN_GET)
from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_typing

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ IMPORTS                           }....................
def get_hint_type_origin(hint: object) -> type:
    '''
    **Origin type** (i.e., :func:`isinstance`-able class suitable for shallowly
    type-checking all parameters and return values annotated with the passed
    PEP-agnostic type hint by passing those parameters or return values and
    that class to the :func:`isinstance` builtin) of this hint if this hint
    originates from such a class *or* raise an exception otherwise (i.e.,
    if this hint originates from *no* such class).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient test.

    Design
    ----------
    :func:`isinstance`-able classes are passable as the second parameter to the
    :func:`isinstance` builtin. These include:

    * Classes *not* defining the ``__subclasscheck__`` dunder method.
    * Classes defining that method to *always* return boolean values rather
      than raise exceptions.

    Most :mod:`typing` classes define the ``__subclasscheck__`` dunder method
    to *always* raise exceptions and are thus *not* :func:`isinstance`-able.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    type
        If this object is either:

        * A non-:mod:`typing` class (e.g., :class:`str`), this object as is.
        * An argumentless :mod:`typing` object originating from an
          :func:`isinstance`-able class (e.g., :attr:`typing.Dict`, originating
          from the builtin :class:`dict` class), that class.

    Raises
    ----------
    BeartypeDecorHintException
        If this object does *not* originate from an :func:`isinstance`-able
        class.
    '''

    # Non-"typing" superclass from which this object originates if any *OR*
    # "None" otherwise.
    hint_type_origin = get_hint_type_origin_or_none(hint)

    # If this superclass exists, return this superclass.
    if hint_type_origin is not None:
        return hint_type_origin

    # Else, no such superclass exists. In this case, raise an exception.
    raise BeartypeDecorHintException(
        'PEP-agnostic type hint {!r} '
        'originates from no non-"typing" type (i.e., due to being neither '
        'an argumentless "typing" attribute nor '
        'a non-"typing" type).'.format(hint))


#FIXME: Actually, it technically *IS* feasible to define a new
#beartype._util.hint.pep.utilhintpeptest.is_hint_pep_typing_attr() tester
#distinguishing argumentless "typing" attributes from standard "typing" objects
#in robust space- and time-efficient manner. First, note that the set of all
#argumentless "typing" attributes is finite (and actually quite small). Given
#that, we can then define a new global frozenset of these attributes based on a
#superset of the keys of the current "TYPING_ATTR_TO_TYPE_ORIGIN". The
#principal issue here is that this frozenset will first need to be defined as a
#mutable set (probably in a module-scoped _init() function) iteratively
#expended:with "typing" attributes that conditionally depend on various major
#Python versions, which is then eventually coerced into a frozenset. Feasible,
#but just *UGH.* Anyway, it would resemble something like:
#    # In "beartype._util.hint.pep.utilhintpepdata"
#    TYPING_ATTRS = None
#    def _init() -> None:
#        global TYPING_ATTRS
#        TYPING_ATTRS = set((...))
#        TYPING_ATTRS.update()
#        TYPING_ATTRS = frozenset(TYPING_ATTRS)
#
#So, that's feasible but non-trivial. Given that, we then define:
#    # In "beartype._util.hint.pep.utilhintpeptest"
#    def is_hint_pep_typing_attr(hint: object) -> bool:
#         return hint in TYPING_ATTRS
#
#So, that's trivial, too. Given that, we then define the corresponding
#die_unless_hint_pep_typing_attr() validator, called below like so:
#   # If this object is a "typing" attribute, return the
#   # isinstance()-able class originating this attribute if any or "None".
#   # Note this condition is intentionally tested *BEFORE* testing whether
#   # this object is a type, as most "typing" attributes that are types
#   # also define __subclasscheck__() dunder methods that unconditionally
#   # raise exceptions and are thus *NOT* isinstance()-able.
#   if is_hint_pep_typing(hint):
#        die_unless_hint_pep_typing_attr(hint)
#        return TYPING_ATTR_TO_TYPE_ORIGIN_GET(hint, None)
#
#   return (
#       # Else if this object is a non-"typing" class, this class as is.
#       hint if isinstance(hint, type) else
#       # Else, "None".
#       None
#   )
#
#So, that's trivial, too. We just lack sufficient interest at the moment, as
#this will require testing and gains us little except a bit of safety during
#development time. *shrug*
def get_hint_type_origin_or_none(hint: object) -> 'NoneTypeOr[type]':
    '''
    **Origin type** (i.e., :func:`isinstance`-able class suitable for shallowly
    type-checking all parameters and return values annotated with the passed
    PEP-agnostic type hint by passing those parameters or return values and
    that class to the :func:`isinstance` builtin) of this hint if this hint
    originates from such a class *or* ``None`` otherwise (i.e., if this hint
    originates from *no* such class).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient series of simple tests.

    Caveats
    ----------
    **This function assumes the caller to have already reduced the passed type
    hint if PEP-compliant to its argumentless** :mod:`typing` **attribute**
    (e.g., from ``typing.Union[int, str]`` to merely ``typing.Union``),
    typically by externally calling the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_typing_attr`
    function beforehand. Since there exists no robust space- and time-efficient
    means of distinguishing argumentless :mod:`typing` attributes from standard
    :mod:`typing` objects, this function does *not* validate this to be the
    case on your behalf.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    (type, None)
        Either:

        * If this object is:

          * A non-:mod:`typing` class (e.g., :class:`str`), this object as is.
          * An argumentless :mod:`typing` object originating from an
            :func:`isinstance`-able class (e.g., :attr:`typing.Dict`, originating
            from the builtin :class:`dict` class), that class.

        * Else, ``None``.

    See Also
    ----------
    :func:`get_hint_type_origin`
        Further details.
    '''

    # Return either...
    return (
        # If this object is a "typing" attribute, the
        # isinstance()-able class originating this attribute if any or "None".
        # Note this condition is intentionally tested *BEFORE* testing whether
        # this object is a type, as most "typing" attributes that are types
        # also define __subclasscheck__() dunder methods that unconditionally
        # raise exceptions and are thus *NOT* isinstance()-able.
        TYPING_ATTR_TO_TYPE_ORIGIN_GET(hint, None)
        if is_hint_pep_typing(hint) else
        # Else if this object is a non-"typing" class, this class as is.
        hint if isinstance(hint, type) else
        # Else, "None".
        None
    )
