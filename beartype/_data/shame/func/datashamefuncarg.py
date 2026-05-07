#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Shameful callable parameter blacklist globals** (i.e., immutable data
structures defining the initial user-configurable contents of blacklists
preventing problematic parameters of problematic functions and methods known to
be hostile to runtime type-checking in general and :mod:`beartype` specifically
from being inappropriately type-checked by :mod:`beartype`).

This private submodule principally describes functions and methods that are
universally applicable **dunder methods** (i.e., PEP-compliant callables whose
names are both prefixed and suffixed by ``"__"`` substrings, which Python itself
reserves for use in standardizing Python-wide dynamic magic).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.typing.datatyping import FrozenSetStrs

# ....................{ DICTS                              }....................
BLACKLIST_FUNC_NAMES_HINT_SELF: FrozenSetStrs = frozenset((
    # ....................{ DUNDERS ~ recursion guard      }....................
    # These PEP-compliant dunder methods are well-known to erroneously induce
    # infinitely recursive type-checking when *ANY* parameter or return is
    # annotated by a type hint that either is or is transitively subscripted by
    # the currently decorated type declaring these dunder methods and are thus
    # runtime-hostile with respect to these parameters.

    # The __getitem__() dunder method erroneously induces infinitely recursive
    # type-checking when *ANY* parameter or return of that method is annotated
    # by a type hint that either is or is transitively subscripted by the
    # currently decorated type declaring that dunder method when that type
    # satisfies the "collections.abc.Sequence" protocol: e.g.,
    #     from beartype import beartype
    #     from typing import SupportsIndex
    #
    #     @beartype
    #     class SquickyList[T](list[T]):
    #         def __getitem__(
    #             self: "SquickyList[T]",  # <------ totally problematic
    #             key: SupportsIndex | slice,  # <-- totally fine
    #         ) -> T:  # <-------------------------- totally fine again
    #             return self[key]
    #
    # The PEP 484-compliant stringified relative forward reference type hint
    # "SquickyList[T]" annotating the "self" parameter of the
    # SquickyList.__getitem__() dunder method erroneously induces infinitely
    # recursive type-checking under @beartype's default O(1) constant-time
    # type-checking strategy. Why? Because type-checking a "SquickyList"
    # instance in O(1) constant-time requires:
    # * Type-checking one item of that instance accessed via a pseudo-random
    #   index, which...
    # * Python implements by implicitly calling the SquickyList.__getitem__()
    #   dunder method, which...
    # * @beartype type-checks by validating that the value of the passed "self"
    #   parameter is a "SquickyList" instance, which...
    # * Triggers infinite recursion, exploding the fragile shell of this world.
    '__getitem__',

    #FIXME: Incrementally add each of the following *AFTER* exhaustively testing
    #that "__getitem__" behaves as expected, please:
    #'__iter__',
    #'__next__',
    #'__subclasscheck__',
))
'''
Frozen set of the unqualified basenames of all **beartype-blacklisted
callable names** well-known to be hostile to runtime type-checking in
general and :mod:`beartype` specifically with respect to *any* parameter or
return of these callables annotated by a type hint that either is or is
transitively subscripted by the currently decorated type declaring these
callables.

As a crude (albeit highly efficient and superficially effective) recursion guard
against infinitely recursive type-checking, :mod:`beartype` silently ignores all
uses of the currently decorated type transitively subscripting *any* parameter
or return of these callables.
'''
