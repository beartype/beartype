#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 585`_**-compliant type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''

# ....................{ IMPORTS                           }....................
from beartype.cave import HintPep585Type
from beartype.roar import BeartypeDecorHintPep585Exception
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ VALIDATORS                        }....................
def die_unless_hint_pep585_generic(hint: object) -> None:
    '''
    Raise an exception unless the passed object is a `PEP 585`_-compliant
    **generic** (i.e., class superficially subclassing at least one subscripted
    `PEP 585`_-compliant pseudo-superclass).

    Parameters
    ----------
    hint : object
        Object to be validated.

    Raises
    ----------
    BeartypeDecorHintPep585Exception
        If this hint is *not* a `PEP 585`_-compliant generic.

    .. _PEP 585:
       https://www.python.org/dev/peps/pep-0585
    '''

    # If this hint is *NOT* a PEP 585-compliant generic, raise an exception
    if not is_hint_pep585_generic(hint):
        raise BeartypeDecorHintPep585Exception(
            f'PEP type hint "{repr(hint)}" not PEP 585 generic.')

# ....................{ TESTERS                           }....................
# If the active Python interpreter targets at least Python >= 3.9 and thus
# supports PEP 585, correctly declare this function.
if IS_PYTHON_AT_LEAST_3_9:
    def is_hint_pep585(hint: object) -> bool:
        return isinstance(hint, HintPep585Type)


    @callable_cached
    def is_hint_pep585_generic(hint: object) -> bool:

        # Unsurprisingly, PEP 585-compliant generics have absolutely *NO*
        # commonality with PEP 484-compliant generics. While the latter are
        # trivially detectable as subclassing "typing.Generic" after type
        # erasure, the former are *NOT*. The only means of deterministically
        # deciding whether or not any given class is a PEP 585-compliant
        # generic is as follows:
        # * That class defines both the __class_getitem__() dunder method *AND*
        #   the "__orig_bases__" instance variable. Note that this condition in
        #   and of itself is insufficient to decide PEP 585-compliance as a
        #   generic. Why? Because these dunder attributes have been
        #   standardized under various PEPs and may thus be implemented by
        #   *ANY* arbitrary classes.
        # * The "__orig_bases__" instance variable is a non-empty tuple.
        # * One or more objects listed in that tuple are PEP 585-compliant
        #   objects.
        #
        # Return true only if this hint satisfies *ALL* of the above conditions.
        # Specifically, return true only if...
        return (
            # This hint defines the "__orig_bases__" dunder instance variable
            # listing all pseudo-superclasses originally subclassed by this
            # hint *AND*...
            #
            # Note that we could technically also test that this hint defines
            # the __class_getitem__() dunder method. Since the subsequent
            # condition suffices to ensure that this hint is a PEP
            # 585-compliant generic, however, there exists little benefit to
            # doing so.
            hasattr(hint, '__orig_bases__') and
            # At least one pseudo-superclass originally subclassed by this hint
            # is a PEP 585-compliant type hint.
            any(
                is_hint_pep585(hint_base_erased)
                for hint_base_erased in hint.__orig_bases__
            )
        )

# Else, the active Python interpreter targets at most Python < 3.9 and thus
# fails to support PEP 585. In this case, fallback to declaring this function
# to unconditionally return False.
else:
    def is_hint_pep585(hint: object) -> bool:
        return False

    def is_hint_pep585_generic(hint: object) -> bool:
        return False

# ....................{ TESTERS ~ doc                     }....................
# Docstring for this function regardless of implementation details.
# Docstring for this function regardless of implementation details.
is_hint_pep585.__doc__ = '''
    ``True`` only if the passed object is a C-based `PEP 585`_-compliant **type
    hint** (i.e., C-based type hint instantiated by subscripting either a
    concrete builtin container class like :class:`list` or :class:`tuple` *or*
    an abstract base class (ABC) declared by the :mod:`collections.abc`
    submodule like :class:`collections.abc.Iterable` or
    :class:`collections.abc.Sequence`).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This test returns false for** `PEP 585`_-compliant **generics,** which
    fail to satisfy the same API as all other `PEP 585`_-compliant type hints.
    Why? Because `PEP 560`_-type erasure erases this API on `PEP
    585`_-compliant generics immediately after those generics are declared,
    preventing their subsequent detection as `PEP 585`_-compliant. Instead,
    `PEP 585`_-compliant generics are only detectable by calling either:

    * The high-level PEP-agnostic
      :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_generic`
      tester.
    * The low-level `PEP 585`_-specific :func:`is_hint_pep585_generic` tester.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a `PEP 585`_-compliant type hint.

    .. _PEP 560:
       https://www.python.org/dev/peps/pep-0585
    .. _PEP 585:
       https://www.python.org/dev/peps/pep-0585
    '''


is_hint_pep585_generic.__doc__ = '''
    ``True`` only if the passed object is a `PEP 585`_-compliant **generic**
    (i.e., class superficially subclassing at least one subscripted `PEP
    585`_-compliant pseudo-superclass).

    This tester memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a generic.

    .. _PEP 585:
       https://www.python.org/dev/peps/pep-0585
    '''

# ....................{ GETTERS                           }....................
def get_hint_pep585_generic_bases_unerased(hint: object) -> 'Tuple[object]':
    '''
    Tuple of all unerased `PEP 585`_-compliant **pseudo-superclasses** (i.e.,
    :mod:`typing` objects originally listed as superclasses prior to their
    implicit type erasure under `PEP 560`_) of the passed `PEP 585`-compliant
    **generic** (i.e., class subclassing at least one non-class `PEP
    585`-compliant object).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Tuple[object]
        Tuple of the one or more unerased pseudo-superclasses of this
        `PEP 585`_-compliant generic.

    Raises
    ----------
    BeartypeDecorHintPep585Exception
        If this hint is *not* a `PEP 585`_-compliant generic.

    See Also
    ----------
    :func:`beartype._util.hint.pep.utilhintget.get_hint_pep_generic_bases_unerased`
        Further details.

    .. _PEP 585:
       https://www.python.org/dev/peps/pep-0585
    '''

    # If this hint is *NOT* a PEP 585-compliant generic, raise an exception
    die_unless_hint_pep585_generic(hint)

    # Return the tuple of all unerased pseudo-superclasses of this generic.
    # While the "__orig_bases__" dunder instance variable is *NOT* guaranteed
    # to exist for PEP 484-compliant generic types, this variable is guaranteed
    # to exist for PEP 585-compliant generic types. Thanks for small favours.
    return hint.__orig_bases__


@callable_cached
def get_hint_pep585_generic_typevars(hint: object) -> 'Tuple[TypeVar]':
    '''
    Tuple of all **unique type variables** (i.e., subscripted :class:`TypeVar`
    instances of the passed `PEP 585`_-compliant generic listed by the caller
    at hint declaration time ignoring duplicates) if any *or* the empty tuple
    otherwise.

    This getter is memoized for efficiency.

    Motivation
    ----------
    The current implementation of `PEP 585`_ under at least Python 3.9 is
    fundamentally broken with respect to parametrized generics. While `PEP
    484`_-compliant generics properly propagate type variables from
    pseudo-superclasses to subclasses, `PEP 585`_ fails to do so. This function
    "fills in the gaps" by recovering these type variables from parametrized
    `PEP 585`_-compliant generics by iteratively constructing a new tuple from
    the type variables parametrizing all pseudo-superclasses of this generic.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Tuple[TypeVar]
        Either:

        * If this `PEP 585`_-compliant generic defines a ``__parameters__``
          dunder attribute, the value of that attribute.
        * Else, the empty tuple.

    Raises
    ----------
    BeartypeDecorHintPep585Exception
        If this hint is *not* a `PEP 585`_-compliant generic.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    .. _PEP 585:
       https://www.python.org/dev/peps/pep-0585
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typevars

    # Tuple of all pseudo-superclasses of this PEP 585-compliant generic.
    hint_bases = get_hint_pep585_generic_bases_unerased(hint)

    # Set of all type variables parametrizing these pseudo-superclasses.
    hint_typevars = set()

    # For each such pseudo-superclass, add all type variables parametrizing
    # this pseudo-superclass to this set.
    for hint_base in hint_bases:
        # print(f'hint_base_typevars: {hint_base} [{get_hint_pep_typevars(hint_base)}]')
        hint_typevars.update(get_hint_pep_typevars(hint_base))

    # Return this set coerced into a tuple.
    return tuple(hint_typevars)
