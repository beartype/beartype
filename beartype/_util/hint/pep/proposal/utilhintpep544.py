#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 544`_**-compliant type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 544:
    https://www.python.org/dev/peps/pep-0544
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPep544Exception
from beartype._util.hint.data.pep.proposal.utilhintdatapep544 import (
    HINT_PEP544_IO_GENERIC_TO_PROTOCOL)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from beartype._util.cls.utilclstest import is_type_builtin
from beartype._util.utilobject import is_object_subclass
from typing import Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
# If the active Python interpreter targets at least Python >= 3.8 and thus
# supports PEP 544, define these functions appropriately.
if IS_PYTHON_AT_LEAST_3_8:
    # Defer version-dependent imports.
    from typing import Protocol

    def is_hint_pep544_ignorable_or_none(
        hint: object, hint_sign: object) -> Optional[bool]:

        # Return either:
        # * If this hint is the "typing.Protocol" superclass directly
        #   parametrized by one or more type variables (e.g.,
        #   "typing.Protocol[S, T]"), true. For unknown and presumably
        #   uninteresting reasons, *ALL* possible objects satisfy this
        #   superclass. Ergo, this superclass and *ALL* parametrizations of
        #   this superclass are synonymous with the "object" root superclass.
        # * Else, "None".
        return repr(hint).startswith('typing.Protocol[') or None


    def is_hint_pep544_io_generic(hint: object) -> bool:

        # Attempt to...
        try:
            # Return true only if this hint is a PEP 484-compliant IO generic
            # base class.
            return hint in HINT_PEP544_IO_GENERIC_TO_PROTOCOL
        # If this hint is unhashable, this hint is by definition *NOT* a PEP
        # 484-compliant IO generic base class. In this case, return false.
        except TypeError:
            return False


    def is_hint_pep544_protocol(hint: object) -> bool:

        # Return true only if this hint is...
        return (
            # A PEP 544-compliant protocol *AND*...
            is_object_subclass(hint, Protocol) and  # type: ignore[arg-type]
            # *NOT* a builtin type. For unknown reasons, some but *NOT* all
            # builtin types erroneously present themselves to be PEP
            # 544-compliant protocols under Python >= 3.8: e.g.,
            #     >>> from typing import Protocol
            #     >>> isinstance(str, Protocol)
            #     False        # <--- this makes sense
            #     >>> isinstance(int, Protocol)
            #     True         # <--- this makes no sense whatsoever
            #
            # Since builtin types are obviously *NOT* PEP 544-compliant
            # protocols, explicitly exclude all such types. Why, Guido? Why?
            not (isinstance(hint, type) and is_type_builtin(hint))
        )


# Else, the active Python interpreter targets at most Python < 3.8 and thus
# fails to support PEP 544. In this case, fallback to declaring this function
# to unconditionally return False.
else:
    def is_hint_pep544_ignorable_or_none(
        hint: object, hint_sign: object) -> Optional[bool]:
        return None


    def is_hint_pep544_io_generic(hint: object) -> bool:
        return False


    def is_hint_pep544_protocol(hint: object) -> bool:
        return False

# ....................{ TESTERS ~ doc                     }....................
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


is_hint_pep544_io_generic.__doc__ = '''
    ``True`` only if the passed object is a functionally useless `PEP
    484`_-compliant :mod:`typing` **IO generic base class** (i.e., either
    :class:`typing.IO` itself *or* a subclass of :class:`typing.IO` defined by
    the :mod:`typing` module effectively unusable at runtime due to botched
    implementation details) that is losslessly replaceable with a useful `PEP
    544`_-compliant :mod:`beartype` **IO protocol** (i.e., either
    :class:`beartype._util.hint.data.pep.proposal.utilhintdatapep544._Pep544IO`
    itself *or* a subclass of that class defined by this submodule
    intentionally designed to be usable at runtime).

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
        ``True`` only if this object is a `PEP 484`_-compliant IO generic base
        class.

    See Also
    ----------
    :class:`beartype._util.hint.data.pep.proposal.utilhintdatapep544._Pep544IO`
        Further commentary.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    .. _PEP 544:
       https://www.python.org/dev/peps/pep-0544
    '''


is_hint_pep544_protocol.__doc__ = '''
    ``True`` only if the passed object is a `PEP 544`_-compliant **protocol**
    (i.e., subclass of the :class:`typing.Protocol` superclass).

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
        ``True`` only if this object is a `PEP 544`_-compliant protocol.

    .. _PEP 544:
       https://www.python.org/dev/peps/pep-0544
    '''

# ....................{ GETTTERS                          }....................
def get_hint_pep544_io_protocol_from_generic(hint: type) -> type:
    '''
    `PEP 544`_-compliant :mod:`beartype` **IO protocol** (i.e., either
    :class:`beartype._util.hint.data.pep.proposal.utilhintdatapep544._Pep544IO`
    itself *or* a subclass of that class defined by this submodule
    intentionally designed to be usable at runtime) corresponding to the passed
    `PEP 484`_-compliant :mod:`typing` **IO generic base class** (i.e., either
    :class:`typing.IO` itself *or* a subclass of :class:`typing.IO` defined by
    the :mod:`typing` module effectively unusable at runtime due to botched
    implementation details).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : type
        `PEP 484`_-compliant :mod:`typing` IO generic base class to be replaced
        by the corresponding `PEP 544`_-compliant :mod:`beartype` IO protocol.

    Returns
    ----------
    Protocol
        `PEP 544`_-compliant :mod:`beartype` IO protocol corresponding to this
        `PEP 484`_-compliant :mod:`typing` IO generic base class.

    Raises
    ----------
    BeartypeDecorHintPep544Exception
        If this object is *not* a `PEP 484`_-compliant IO generic base class.

    See Also
    ----------
    :class:`beartype._util.hint.data.pep.proposal.utilhintdatapep544._Pep544IO`
        Further commentary.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    .. _PEP 544:
       https://www.python.org/dev/peps/pep-0544
    '''

    # If this object is *NOT* a PEP 484-compliant "typing" IO generic,
    # raise an exception.
    if not is_hint_pep544_io_generic(hint):
        raise BeartypeDecorHintPep544Exception(
            f'PEP type hint {repr(hint)} not '
            f'PEP 484-compliant "typing" IO generic base class '
            f'(i.e., "typing.IO", "typing.BinaryIO", "typing.TextIO").')
    # Else, this object is *NOT* a PEP 484-compliant "typing" IO generic.

    # Return the corresponding PEP 544-compliant IO protocol.
    return HINT_PEP544_IO_GENERIC_TO_PROTOCOL[hint]
