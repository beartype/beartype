#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 593`_**-compliant type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 593:
    https://www.python.org/dev/peps/pep-0593
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
# If the active Python interpreter targets at least Python >= 3.9 and thus
# supports PEP 593, define these functions appropriately.
if IS_PYTHON_AT_LEAST_3_9:
    # Defer version-dependent imports.
    from typing import Annotated

    #FIXME: Note this returns false for the unsubscripted "Annotated" class. Do
    #we particularly care about this edge case? Probably not. *shrug*
    def is_hint_pep593(hint: object) -> bool:

        # Return true only if the machine-readable representation of this
        # object implies this object to be a PEP 593-compliant type hint hint.
        #
        # Note that this approach has been intentionally designed to apply to
        # arbitrary and hence possibly PEP-noncompliant type hints. Notably,
        # this approach avoids the following equally applicable but
        # considerably less efficient heuristic:
        #    return (
        #        is_hint_pep(hint) and get_hint_pep_sign(hint) is Annotated)
        return repr(hint).startswith('typing.Annotated[')


    def is_hint_pep593_ignorable_or_none(
        hint: object, hint_sign: object) -> 'Optional[bool]':

        # Avoid circular import dependencies.
        from beartype._util.hint.utilhinttest import is_hint_ignorable
        # print(f'!!!!!!!Received 593 hint: {repr(hint)} [{repr(hint_sign)}]')

        # Return either...
        return (
            # If this hint is annotated, true only if the PEP-compliant child
            # type hint annotated by this hint hint is ignorable (e.g., the
            # "Any" in "Annotated[Any, 50, False]").
            is_hint_ignorable(hint.__origin__)
            if hint_sign is Annotated else
            # Else, "None".
            None
        )
# Else, the active Python interpreter targets at most Python < 3.9 and thus
# fails to support PEP 593. In this case, fallback to defining these functions
# to unconditionally return False.
else:
    def is_hint_pep593(hint: object) -> bool:
        return False


    def is_hint_pep593_ignorable_or_none(
        hint: object, hint_sign: object) -> 'Optional[bool]':
        return None

# ....................{ TESTERS ~ doc                     }....................
# Docstring for these functions regardless of the implementation details above.
is_hint_pep593.__doc__ = '''
    ``True`` only if the passed object is a `PEP 593`_-compliant **user-defined
    type metahint** (i.e., subscription of the :attr:`typing.Annotated`
    singleton).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a `PEP 593`_-compliant user-defined
        type metahint.

    .. _PEP 593:
       https://www.python.org/dev/peps/pep-0593
    '''


is_hint_pep593_ignorable_or_none.__doc__ = '''
    ``True`` only if the passed object is a `PEP 593`_-compliant **ignorable
    type hint,** ``False`` only if this object is a `PEP 593`_-compliant
    unignorable type hint, and ``None`` if this object is *not* `PEP
    593`_-compliant.

    Specifically, this tester function returns ``True`` only if this object is
    the :data:`Annotated` singleton whose first subscripted argument is an
    ignorable type hints (e.g., ``typing.Annotated[typing.Any, bool]``).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as this tester is only safely callable
    by the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    hint_sign : object
        **Sign** (i.e., arbitrary object uniquely identifying this hint).

    Returns
    ----------
    Optional[bool]
        Either:

        * If this object is `PEP 593`_-compliant:

          * If this object is a ignorable, ``True``.
          * Else, ``False``.

        * If this object is *not* `PEP 593`_-compliant, ``None``.

    .. _PEP 593:
       https://www.python.org/dev/peps/pep-0593
    '''
