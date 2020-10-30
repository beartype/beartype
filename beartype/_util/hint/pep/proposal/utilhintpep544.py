#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 544`_**-compliant type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 544:
    https://www.python.org/dev/peps/pep-0544
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS ~ ignorable               }....................
# If the active Python interpreter targets at least Python >= 3.8 and thus
# supports PEP 544, define these functions appropriately.
if IS_PYTHON_AT_LEAST_3_8:
    # Defer version-dependent imports.
    from typing import Protocol

    def is_hint_pep544_ignorable_or_none(
        hint: object, hint_sign: object) -> 'Optional[bool]':

        # Return either:
        # * If this hint is the "typing.Protocol" superclass directly
        #   parametrized by one or more type variables (e.g.,
        #   "typing.Protocol[S, T]"), True. Testing whether this sign is that
        #   superclass suffices to test this condition, as the
        #   get_hint_pep_sign() function returns that superclass as a sign
        #   *ONLY* when that superclass is directly parametrized by one or more
        #   type variables. In *ALL* other cases involving that superclass,
        #   that function *ALWAYS* returns the standard "typing.Generic"
        #   superclass for instead -- as generics and protocols are otherwise
        #   indistinguishable with respect to runtime type-checking.
        # * Else, "None".
        return hint_sign is Protocol or None
# Else, the active Python interpreter targets at most Python < 3.8 and thus
# fails to support PEP 544. In this case, fallback to declaring this function
# to unconditionally return False.
else:
    def is_hint_pep544_ignorable_or_none(
        hint: object, hint_sign: object) -> 'Optional[bool]':
        return None


is_hint_pep544_ignorable_or_none.__doc__ = '''
    ``True`` only if the passed object is a `PEP 544`_-compliant **ignorable
    type hint,** ``False`` only if this object is a `PEP 544`_-compliant
    unignorable type hint, and ``None`` if this object is *not* `PEP
    544`_-compliant.

    Specifically, this tester function returns ``True`` only if this object is
    a deeply ignorable `PEP 544`_-compliant type hint, including:

    * A parametrization of the :class:`typing.Protocol` abstract base class
      (ABC) by one or more type variables. As the name implies, this ABC is
      generic and thus fails to impose any meaningful constraints. Since a type
      variable in and of itself also fails to impose any meaningful
      constraints, these parametrizations are safely ignorable in all possible
      contexts: e.g.,

      .. code-block:: python

         from typing import Protocol, TypeVar
         T = TypeVar('T')
         def noop(param_hint_ignorable: Protocol[T]) -> T: pass

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

        * If this object is `PEP 544`_-compliant:

          * If this object is a ignorable, ``True``.
          * Else, ``False``.

        * If this object is *not* `PEP 544`_-compliant, ``None``.

    .. _PEP 544:
       https://www.python.org/dev/peps/pep-0544
    '''
