#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **generic type hint
testers** (i.e., low-level callables generically validating and detecting both
:pep:`484`- and :pep:`585`-compliant generic classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.cls.datacls import TYPES_PEP484544_GENERIC
from beartype._data.hint.datahintpep import Hint
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep484.pep484generic import (
    is_hint_pep484_generic_subscripted,
    is_hint_pep484_generic_unsubscripted,
)
from beartype._util.hint.pep.proposal.pep585 import (
    is_hint_pep585_generic_subscripted,
    is_hint_pep585_generic_unsubscripted,
    is_hint_pep585_builtin_subscripted,
)
from beartype._util.module.utilmodtest import (
    is_object_module_thirdparty_blacklisted)

# Intentionally import PEP 484-compliant "typing" type hint factories rather
# than possibly PEP 585-compliant "beartype.typing" type hint factories.
from typing import Generic

# ....................{ TESTERS                            }....................
def is_hint_pep484585_generic_subscripted_ignorable(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed :pep:`484`- or :pep:`585`-compliant
    **subscripted generic** (i.e., unsubscripted generic type originally
    parametrized by one or more :pep:`484`-compliant type variables subscripted
    by a corresponding number of arbitrary child type hints) is ignorable.

    This tester ignores *all* parametrizations of the :class:`typing.Generic`
    abstract base class (ABC) by one or more type variables. As the name
    implies, this ABC is generic and thus fails to impose any meaningful
    constraints. Since a type variable in and of itself also fails to impose any
    meaningful constraints, these parametrizations are safely ignorable in all
    possible contexts: e.g.,

    .. code-block:: python

       from typing import Generic, TypeVar
       T = TypeVar('T')
       def noop(param_hint_ignorable: Generic[T]) -> T: pass

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only safely callable by
    the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Caveats
    -------
    **Unsubscripted generics are unconditionally unignorable.** This tester thus
    considers *only* subscripted generics.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this :pep:`484`-compliant type hint is ignorable.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_origin_or_none
    # print(f'Testing generic hint {repr(hint)} deep ignorability...')

    # If this generic is the "typing.Generic" superclass directly parametrized
    # by one or more type variables (e.g., "typing.Generic[T]"), return true.
    #
    # Note that we intentionally avoid calling the
    # get_hint_pep_origin_type_isinstanceable_or_none() function here, which has
    # been intentionally designed to exclude PEP-compliant type hints
    # originating from "typing" type origins for stability reasons.
    if get_hint_pep_origin_or_none(hint) is Generic:
        # print(f'Testing generic hint {repr(hint)} deep ignorability... True')
        return True
    # Else, this generic is *NOT* the "typing.Generic" superclass directly
    # parametrized by one or more type variables and thus *NOT* an ignorable
    # non-protocol.
    #
    # Note that this condition being false is *NOT* sufficient to declare this
    # hint to be unignorable. Notably, the origin type originating both
    # ignorable and unignorable protocols is "Protocol" rather than "Generic".
    # Ergo, this generic could still be an ignorable protocol.
    # print(f'Testing generic hint {repr(hint)} deep ignorability... False')

    #FIXME: Probably insufficient. *shrug*
    return False


def is_hint_pep484585_generic_user(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed :pep:`484`- or :pep:`585`-compliant generic
    is **user-defined** (i.e., defined by a third-party downstream codebase
    rather than CPython's first-party upstream standard library).

    Specifically, this tester returns :data:`True` only if this generic is
    neither:

    * A :pep:`484`- or :pep:`544`-compliant superclass defined by the
      :mod:`typing` module (e.g., :class:`typing.Generic`) *nor*...
    * A :pep:`585`-compliant superclass (e.g., ``list[T]``).

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to
    an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this is a user-defined generic.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_origin_type_or_none)

    # Return true only if...
    return (
        # This object is a generic that is neither...
        is_hint_pep484585_generic(hint) and not (
            # A subscripted PEP 585-compliant superclass (e.g., "list[T]")
            # *NOR*...
            is_hint_pep585_builtin_subscripted(hint) or
            # A subscripted or unsubscripted PEP 484- or 544-compliant
            # superclass defined by the standard "typing" module, including:
            # * "typing.Generic".
            # * "typing.Generic[S]".
            # * "typing.Protocol".
            # * "typing.Protocol[S]".
            get_hint_pep_origin_type_or_none(
                hint=hint,
                # Preserve "typing.Generic" and "typing.Protocol" as themselves,
                # as doing so dramatically simplifies this test. *shrug*
                is_self_fallback=True,
            ) in TYPES_PEP484544_GENERIC
        )
    )

# ....................{ TESTERS ~ kind                     }....................
@callable_cached
def is_hint_pep484585_generic(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **generic** (i.e., either a type originally subclassing
    at least one subscripted :pep:`484`- or :pep:`585`-compliant
    pseudo-superclass *or* an object subscripted by one or more child type hints
    originating from such a type).

    This tester returns :data:`True` only if this object is either:

    * A :pep:`484`-compliant generic as tested by the lower-level
      :func:`.is_hint_pep484_generic` function.
    * A :pep:`585`-compliant generic as tested by the lower-level
      :func:`.is_hint_pep585_generic` function.

    This tester is memoized for efficiency.

    Caveats
    -------
    **Generics are not necessarily classes,** despite originally being declared
    as classes. Although *most* generics are classes, subscripting a generic
    class usually produces a generic non-class that *must* nonetheless be
    transparently treated as a generic class: e.g.,

    .. code-block:: pycon

       >>> from typing import Generic, TypeVar
       >>> S = TypeVar('S')
       >>> T = TypeVar('T')
       >>> class MuhGeneric(Generic[S, T]): pass
       >>> non_class_generic = MuhGeneric[S, T]
       >>> isinstance(non_class_generic, type)
       False

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a generic.

    See Also
    --------
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_typevars`
        Commentary on the relation between generics and parametrized hints.
    '''

    # Return true only if...
    return (
        # This hint is either a...
        (
            # PEP 484-compliant generic *OR*...
            #
            # Note these tests trivially reduce to fast O(1) operations and are
            # thus tested first.
            is_hint_pep484_generic_unsubscripted(hint) or
            is_hint_pep484_generic_subscripted(hint) or
            # PEP 585-compliant generic.
            #
            # Note this test is O(n) for n the number of pseudo-superclasses
            # originally subclassed by this generic and is thus tested last.
            is_hint_pep585_generic_unsubscripted(hint) or
            is_hint_pep585_generic_subscripted(hint)
        # *AND*...
        ) and
        # This generic is *NOT* beartype-blacklisted.
        not _is_hint_pep484585_generic_blacklisted(hint)
    )


def is_hint_pep484585_generic_subscripted(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **subscripted generic** (i.e., object subscripted by
    one or more child type hints originating from a type originally subclassing
    at least one subscripted :pep:`484`- or :pep:`585`-compliant
    pseudo-superclass).

    This tester returns :data:`True` only if this object is either:

    * A :pep:`484`-compliant subscripted generic as tested by the lower-level
      :func:`.is_hint_pep484_generic_subscripted` function.
    * A :pep:`585`-compliant subscripted generic as tested by the lower-level
      :func:`.is_hint_pep585_generic_subscripted` function.

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a subscripted generic.
    '''

    # Return true only if...
    return (
        # This hint is either a...
        (
            # PEP 484-compliant subscripted generic *OR*...
            #
            # Note this test trivially reduces to a fast O(1) operation and is
            # thus tested first.
            is_hint_pep484_generic_subscripted(hint) or
            # PEP 585-compliant subscripted generic.
            #
            # Note this test is O(n) for n the number of pseudo-superclasses
            # originally subclassed by this generic and is thus tested last.
            is_hint_pep585_generic_subscripted(hint)
        # *AND*...
        ) and
        # This generic is *NOT* beartype-blacklisted.
        not _is_hint_pep484585_generic_blacklisted(hint)
    )


def is_hint_pep484585_generic_unsubscripted(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **unsubscripted generic** (i.e., type originally
    subclassing at least one subscripted :pep:`484`- or :pep:`585`-compliant
    pseudo-superclass).

    This tester returns :data:`True` only if this object is either:

    * A :pep:`484`-compliant unsubscripted generic as tested by the lower-level
      :func:`.is_hint_pep484_generic_unsubscripted` function.
    * A :pep:`585`-compliant unsubscripted generic as tested by the lower-level
      :func:`.is_hint_pep585_generic_unsubscripted` function.

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a unsubscripted generic.
    '''

    # Return true only if...
    return (
        # This hint is either a...
        (
            # PEP 484-compliant unsubscripted generic *OR*...
            #
            # Note this test trivially reduces to a fast O(1) operation and is
            # thus tested first.
            is_hint_pep484_generic_unsubscripted(hint) or
            # PEP 585-compliant unsubscripted generic.
            #
            # Note this test is O(n) for n the number of pseudo-superclasses
            # originally subclassed by this generic and is thus tested last.
            is_hint_pep585_generic_unsubscripted(hint)
        # *AND*...
        ) and
        # This generic is *NOT* beartype-blacklisted.
        not _is_hint_pep484585_generic_blacklisted(hint)
    )

# ....................{ PRIVATE ~ testers                  }....................
#FIXME: Call above, please.
@callable_cached
def _is_hint_pep484585_generic_blacklisted(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed :pep:`484`- or :pep:`585`-compliant generic
    is **beartype-blacklisted** (i.e., defined in a third-party package or
    module known to be hostile to runtime type-checking).

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : Hint
        Generic to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this generic is beartype-blacklisted.

    See Also
    --------
    :func:`.is_object_module_thirdparty_blacklisted`
        Further details on beartype-blacklisting.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_type)

    # Either:
    # * If this generic is already unsubscripted, this generic as is.
    # * Else, this generic is subscripted. In this case, the unsubscripted
    #   generic underlying this subscripted generic.
    hint_type = get_hint_pep484585_generic_type(hint)

    # For each possibly erased superclass of this generic, arbitrarily iterated
    # according to the method resolution order (MRO) for this generic...
    for hint_base in hint_type.__mro__:
        # If this superclass is beartype-blacklisted (i.e., defined in a
        # third-party package or module known to be hostile to runtime
        # type-checking), return true immediately.
        if is_object_module_thirdparty_blacklisted(hint_base):
            return True
        # Else, this superclass is *NOT* beartype-blacklisted. In this case,
        # continue to the next such superclass of this generic.
    # Else, all superclasses of this generic are *NOT* beartype-blacklisted.

    # Return false as a sane fallback.
    return False
