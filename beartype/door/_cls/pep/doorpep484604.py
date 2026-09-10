#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) union type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant :attr:`typing.Optional` and :attr:`typing.Union` type
hints and :pep:`604`-compliant ``|``-delimited union type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorabc import TypeHint
from collections.abc import Collection

# ....................{ SUBCLASSES                         }....................
class UnionTypeHint(TypeHint):
    '''
    **Union type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`-compliant :attr:`typing.Optional` or
    :attr:`typing.Union` type hint *or* :pep:`604`-compliant ``|``-delimited
    union type hint).
    '''

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _branches(self) -> Collection[TypeHint]:

        # Immutable iterable of all branches (i.e., high-level type hint
        # wrappers encapsulating all low-level child hints subscripting
        # (indexing) the low-level parent hint encapsulated by this high-level
        # parent type hint wrapper. Look. Just go with it. We do. Every day.
        return self._args_wrapped_frozenset

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_subhint(self, other: TypeHint) -> bool:

        #FIXME: [SPEED] *INEFFICIENT.* The all() and any() builtins have been
        #profiled to be almost twice as slow as equivalent manual iteration!
        # Return true only if *EVERY* child hint of this union is a subhint of
        # at least one other child hint of the passed other union.
        #
        # Note that this iteration exhibits O(n**2) time complexity. Although
        # non-ideal, this is also unavoidable. Thankfully, since most real-world
        # unions are subscripted by only a small number of child hints, this is
        # also mostly ignorable in practice.
        #
        # Specifically, return true only if...
        return all(
            # For each child hint subscripting this union...
            (
                #FIXME: [SPEED] We inefficiently recheck whether the passed hint
                #is itself a union *EVERY* single iteration, which is sheer
                #special nonsense. Refactor the "if isinstance(other,
                #UnionTypeHint)" test out to the outermost body of this method.
                # If that other passed hint is itself a union, then for at least
                # one other child hint subscripting that other passed union...
                any(
                    # This child hint is a subhint of that other child hint.
                    this_branch.is_subhint(that_branch)
                    for that_branch in other._branches
                ) if isinstance(other, UnionTypeHint) else
                # Else, that other hint is *NOT* a union. In this case, true
                # only if this child hint is a subhint of that other hint.
                #
                # Note that this is a common edge case. Examples include:
                # * "TypeHint(Union[...]) <= TypeHint(Any)". Although "Any" is
                #   *NOT* a union, *ALL* unions are subhints of "Any".
                # * "TypeHint(Union[A, B]) <= TypeHint(Union[A])" where "A" is
                #   the superclass of "B". Since Python reduces "Union[A]" to
                #   just "A", this is exactly equivalent to the comparison
                #   "TypeHint(Union[A, B]) <= TypeHint(A)". Although "A" is
                #   *NOT* a union, this example clearly demonstrates that a
                #   union may be a subhint of a non-union that is *NOT* "Any" --
                #   contrary to intuition. Examples include:
                #   * "TypeHint(Union[int, bool]) <= TypeHint(Union[int])".
                this_branch.is_subhint(other)
            )
            for this_branch in self._branches
        )


    def _is_subhint_branch(self, branch: TypeHint) -> bool:  # pragma: no cover
        raise NotImplementedError(
            'UnionTypeHint._is_subhint_branch() unsupported.')

    # ..................{ PRIVATE ~ getters                  }..................
    def _get_hash(self) -> int:

        # List of all subhint-unique child hints subscripting this union, where
        # the ad-hoc term "subhint-unique" (which we totally just made up) is
        # defined here as "is *NOT* a subhint of any other child hint
        # subscripting this union." For example:
        # * Given the union "numbers.Number | float | int", this set is simply
        #   "{numbers.Number,}". Why? Because the builtin "float" and "int"
        #   types are both subhints of the standard "numbers.Number" type and
        #   thus redundant rather than unique.
        #
        # This hash has the minor disadvantage of increased time complexity but
        # the major advantage of preserving consistency between equality and
        # hashes. Specifically, doing so ensures that semantically equivalent
        # unions (e.g., "numbers.Number | float" and "numbers.Number | int"),
        # which compare equal, also share the same hash.
        branches_unique = []

        # For each child hint subscripting this union...
        #
        # Note that this iteration exhibits O(n**2) time complexity. Although
        # non-ideal, this is also unavoidable. Thankfully, since most real-world
        # unions are subscripted by only a small number of child hints, this is
        # also mostly ignorable in practice.
        for this_branch in self._args_wrapped_frozenset:
            # For each other child hint subscripting this union...
            for other_branch in self._args_wrapped_frozenset:
                # If...
                if (
                    # The outer child hint being visited is *NOT* the same as
                    # the inner child hint being visited...
                    #
                    # Note that this is *NOT* simply a microoptimization. Every
                    # type hint is necessarily a subhint of itself. Thus,
                    # permitting this outer child hint to be compared as a
                    # subhint against itself would trigger the "break" statement
                    # for *ALL* child hints, preventing *ANY* child hints from
                    # being appended to the "branches_unique" list.
                    this_branch is not other_branch and
                    # This outer child hint is a subhint of this inner child
                    # hint...
                    this_branch.is_subhint(other_branch)
                ):
                    # Then this outer child hint is *NOT* subhint-unique. In
                    # this case, avoid appending this outer child hint to this
                    # list and instead silently continue to the next child hint.
                    break
            # Else, the nested "for" loop above did *NOT* trigger the "break"
            # statement for this outer child hint, which must thus be
            # subhint-unique. Append this outer child hint to this list.
            else:
                branches_unique.append(this_branch)

        # Low-level hashable object encapsulated by this high-level wrapper to
        # be hashed below as the hash for this wrapper, defined as either...
        wrapper_hashable = (
            # If this union is subscripted by only a single subhint-unique child
            # hint, that hint. Doing so ensures that unions subscripted by two
            # or more child hints (only one of which is subhint-unique) and that
            # subhint-unique child hint itself (e.g., "bool | int" and "int"),
            # which compare equal, also share the same hash.
            branches_unique[0]
            if len(branches_unique) == 1 else
            # Else, this union is subscripted by two or more subhint-unique
            # child hints. In this case, the hashable frozenset coerced from
            # this unhashable list.
            #
            # Note that a frozenset rather than tuple is intentionally selected.
            # Whereas the latter erroneously treats the order of child hints
            # subscripting a union to be significant, the former correctly
            # ignores that order. Union membership is order-invariant. Sets, yo!
            frozenset(branches_unique)
        )

        # Hash this wrapper by this hashable.
        return hash(wrapper_hashable)
