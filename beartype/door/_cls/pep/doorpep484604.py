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
from beartype._util.cache.func.utilcacheproperty import property_cached
from collections.abc import Collection
from typing import Union

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


    #FIXME: Docstring us up, please. *sigh*
    #FIXME: Refactor _get_hash() to defer to this property instead. *sigh*
    #FIXME: Cache if this actually works. Note that doing so will require
    #tediously defining "__slots__". *UGH*. *sigh*
    @property
    # @property_cached
    def _branches_unique(self) -> Union[TypeHint, Collection[TypeHint]]:

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
                    this_branch != other_branch and
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

        # Return this hashable.
        return wrapper_hashable

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_equal(self, other: TypeHint) -> bool:

        # Avoid circular import dependencies.
        from beartype.door._cls.pep.pep484.doorpep484any import AnyTypeHint

        #FIXME: Comment us up, please. *sigh*
        if isinstance(other, AnyTypeHint):
            return other == self
        elif isinstance(other, UnionTypeHint):
            return self._branches_unique == other._branches_unique
        else:
            return (
                self.is_subhint(other) and
                other.is_subhint(self)
            )

        #FIXME: Obsolete comment. Turns out... we figured it out.
        #Unsurprisingly, it was super-brutal. But we did it, yo! \o/
        # Note that there are *MANY* different techniques for implementing
        # equality comparison between a union and an arbitrary hint. If the
        # problematic PEP 484-compliant "typing.Any" catch-all singleton did
        # *NOT* exist, then the optimal implementation would simply be the
        # default TypeHint._is_equal() implementation: e.g.,
        #     return (
        #         self.is_subhint(other) and
        #         other.is_subhint(self)
        #     )
        #
        # That default implementation has the advantage of correctly comparing
        # *SEMANTIC* equality between a union and an arbitrary hint. Although
        # useful, that implementation also suffers a fatal flaw. Due to the
        # existence of "Any", guaranteeing consistency between union equality
        # (i.e., UnionTypeHint.__eq__() dunder method) and union hashability
        # (i.e., TypeHint.__hash__() dunder method) is effectively infeasible
        # under that default implementation. Why? Consider the example unions:
        # "Any | int" and "str | int". Under that implementation, these unions
        # compare equal yet have unequal hashes -- thus violating consistency.
        #
        # The only sane alternative is thus to compare *SYNTACTIC* equality
        # between a union and an arbitrary hint. Under this less useful rubric,
        # a union and an arbitrary hint compare equal only if the two share the
        # same branches (i.e., are subscripted by the same unique child hints).
        # Although less useful, this alternative preserves consistency.
        #
        # Note that other convoluted alternatives exist. For example, one might
        # attempt to employ a hybrid strategy:
        # * If this union is *NOT* subscripted by "Any", defer to the default
        #   implementation.
        # * If this union is subscripted by "Any", attempt to compare only the
        #   proper subset of each union that does *NOT* contain "Any". In
        #   theory, that sounds great. In practice, what exactly does that
        #   suspicious phrase 'contain "Any"' mean? After all, a hint
        #   "Annotated[Any, beartype.vale.Is[obj: True]]" is *NOT* "Any" and
        #   does *NOT* compare equal to "Any". Yet, that hint is semantically
        #   equivalent to "Any". In short, detecting hints that semantically
        #   equivalent to "Any"

    #     # If this union is subscripted by the PEP 484-compliant "typing.Any"
    #     # catch-all singleton...
    #     if self._is_arg_any:
    #         # If that other passed hint is *NOT* itself a union...
    #         if isinstance(other, UnionTypeHint):
    #             return False
    #
    #         other.
    #
    #     # If *ALL* of the child hints subscripting both of these unions are
    #     # ignorable, these unions are semantically equal. Return true.
    #     if self._is_args_ignorable and other._is_args_ignorable:
    #         return True
    #     # Else, one or more of the child type hints subscripting either of these
    #     # unions are unignorable.
    #     #
    #     # If these parent hints are subscripted by a differing number of
    #     # *UNIQUE* child hints, these unions are trivially unequal. Return
    #     # false.
    #     elif len(self._branches) != len(other._branches):
    #         return False
    #     # Else, these parent hints are subscripted by the same number of child
    #     # hints and thus *COULD* be equal.
    #
    #     # If that other passed hint is itself a union...
    #     if isinstance(other, UnionTypeHint):
    #         # For each unique child hint subscripting this union...
    #         for this_child in self._branches:
    #             # For each other unique child hint subscripting that other
    #             # union...
    #             for that_child in other._branches:
    #                 # If this child hint is equal to that child hint, some
    #                 # subset of this union is equal to some subset of that
    #                 # union. In this case, halt iterating the other child hints
    #                 # subscripting that other union and continue to the next
    #                 # child hint of this union. is unequal to that union.
    #                 if this_child == that_child:
    #                     break
    #                 # Else, this child hint is unequal to that child hint,
    #                 # implying this union *COULD* be unequal to that union.
    #                 # Continue to the next other child hint subscripting that
    #                 # other union to decide.
    #             # If the inner "for" loop above did *NOT* break, then this child
    #             # hint is *NOT* a subhint of some other child subscripting that
    #             # other union, implying that this union *CANOT* be a subhint of
    #             # that other union as a whole. In this case, return false.
    #             else:
    #                 return False
    #
    #     # Return true as a safe fallback.
    #     return True


    def _is_subhint(self, other: TypeHint) -> bool:

        # If that other passed hint is itself a union...
        if isinstance(other, UnionTypeHint):
            # For each child hint subscripting this union...
            #
            # Note that this iteration exhibits O(n**2) time complexity. While
            # non-ideal, this is also unavoidable. Thankfully, since most
            # real-world unions are subscripted by only a small number of child
            # hints, this is also mostly ignorable in practice.
            for this_branch in self._branches:
                # For each other child hint subscripting that other union...
                for that_branch in other._branches:
                    # If this child hint is a subhint of that other child
                    # hint, this child hint is a subhint of that other union as
                    # a whole. In this case, halt iterating the other child
                    # hints subscripting that other union and continue to the
                    # next child hint of this union.
                    if this_branch.is_subhint(that_branch):
                        break
                    # Else, this child hint is *NOT* a subhint of that other
                    # child hint, implying this union might *NOT* be a suhbint
                    # of that other union. Continue to the next other child
                    # hint subscripting that other union to decide.
                # If the inner "for" loop above did *NOT* break, then this child
                # hint is *NOT* a subhint of some other child subscripting that
                # other union, implying that this union *CANOT* be a subhint of
                # that other union as a whole. In this case, return false.
                else:
                    return False
        # Else, that other hint is *NOT* a union. In this case...
        #
        # Note that this is a common edge case. Examples include:
        # * "TypeHint(Union[...]) <= TypeHint(Any)". Although "Any" is *NOT* a
        #   union, *ALL* unions are subhints of "Any".
        # * "TypeHint(Union[A, B]) <= TypeHint(Union[A])" where "A" is the
        #   superclass of "B". Since Python reduces "Union[A]" to just "A", this
        #   is exactly equivalent to the comparison "TypeHint(Union[A, B]) <=
        #   TypeHint(A)". Although "A" is *NOT* a union, this example clearly
        #   demonstrates that a union may be a subhint of a non-union that is
        #   *NOT* "Any" -- contrary to intuition. Examples include:
        #   * "TypeHint(Union[int, bool]) <= TypeHint(Union[int])".
        else:
            # For each child hint subscripting this union...
            for this_branch in self._branches:
                # If this child hint is *NOT* a subhint of that other hint,
                # this union *CANNOT* be a subhint of that other hint. In this
                # case, return false.
                if not this_branch.is_subhint(other):
                    return False
                # Else, this child hint is a subhint of that other hint,
                # implying this union *COULD* be a subhint of that other hint.
                # Continue to the next child hint to decide.

        # Return true as a fallback.
        return True


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
                    this_branch != other_branch and
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
