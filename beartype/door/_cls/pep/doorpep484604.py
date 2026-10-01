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
from beartype.door._cls.doorabc import (
    CollectionTypeHints,
    TypeHint,
)
from beartype._data.typing.datatypingport import Hint
from beartype._util.cache.func.utilcacheproperty import (
    get_property_var_name,
    property_cached,
)
from typing import Union

# ....................{ SUBCLASSES                         }....................
class UnionTypeHint(TypeHint):
    '''
    **Union type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`-compliant :attr:`typing.Optional` or
    :attr:`typing.Union` type hint *or* :pep:`604`-compliant ``|``-delimited
    union type hint).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        # Instance variables implicitly defined by each decoration of a property
        # method by the @property_cached decorator below, whose names are
        # dynamically precomputed by this getter. It doesn't have to make sense.
        get_property_var_name('_branches_unique'),
    )

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _branches(self) -> CollectionTypeHints:

        # Immutable iterable of all branches (i.e., high-level type hint
        # wrappers encapsulating all low-level child hints subscripting
        # (indexing) the low-level parent hint encapsulated by this high-level
        # parent type hint wrapper. Look. Just go with it. We do. Every day.
        return self._args_wrapped_frozenset


    @property  # type: ignore
    @property_cached
    def _branches_unique(self) -> Union[TypeHint, CollectionTypeHints]:
        '''
        Hashable and thus immutable collection of all **subhint-unique
        branches** (i.e., high-level type hint wrappers encapsulating all
        low-level **subhint-unique child hints** (i.e., child hints that are
        *not* subhints of any other child hint) subscripting this union) of this
        type hint wrapper.

        This property returns a non-collection in the common edge case in which
        this union contains only one subhint-unique branch, as doing so both
        simplifies and optimizes downstream methods accessing this property.
        Critically, this implies that:

        * If this union is subscripted by the :pep:`484`-compliant
          :obj:`typing.Any` singleton, this property trivially returns
          :obj:`typing.Any` regardless of what other child hints subscript this
          union.

        Returns
        -------
        Union[TypeHint, Collection[TypeHint]]
            Either:

            * If this union is subscripted by only a single subhint-unique child
              hint, that child hint. Doing so ensures that unions subscripted by
              two or more child hints only one of which is subhint-unique (e.g.,
              ``bool | int``) preserves equality-hash consistency with that
              subhint-unique child hint itself (e.g., ``int``) by ensuring that
              that union and child hint both compare equal to *and* shares the
              same hash with one another.
            * If this union is subscripted by two or more subhint-unique child
              hints, the frozenset of those child hints.
        '''

        # ..................{ IMPORTS                        }..................
        # Avoid circular import dependencies.
        from beartype.door._cls.pep.pep484.doorpep484any import AnyTypeHint

        # ..................{ LOCALS                         }..................
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

        # 0-based index of the child hint subscripting this union currently
        # being visited by the outer "while" loop below.
        branch_this_index = 0

        # 0-based index of the child hint subscripting this union currently
        # being visited by the inner "while" loop below.
        branch_that_index = 0

        # Efficiently indexable tuple of all trivially unique child hints (i.e.,
        # child hints that are *NOT* trivial duplicates of one another)
        # subscripting this union.
        branches = tuple(self._args_wrapped_frozenset)

        # Total number of trivially unique child hints subscripting this union.
        branches_len = len(branches)

        # ..................{ SEARCH                         }..................
        # While one or more child hints subscripting this union have yet to be
        # visited by this outer "while" loop...
        #
        # Note that this iteration exhibits O(n**2) time complexity. Although
        # non-ideal, this is also unavoidable. Thankfully, since most real-world
        # unions are subscripted by only a small number of child hints, this is
        # also mostly ignorable in practice.
        while branch_this_index < branches_len:
            # Child hint currently being visited by this outer "while" loop.
            branch_this = branches[branch_this_index]

            # If this child hint is the PEP 484-compliant "typing.Any"
            # catch-all singleton...
            #
            # This logic reduces *ANY* union subscripted by "Any" to the 1-list
            # containing *ONLY* "Any". Semantically, *ALL* unions subscripted by
            # "Any" are effectively subscripted by only one subhint-unique child
            # hint: "Any" itself. However, it is the case that both:
            # * "Any" is a subhint of *ANY* type hint.
            # * *ANY* type hint is a subhint of "Any".
            #
            # Altogether, these observations imply that the logic below would
            # naively "break" on *EVERY* child hint, preventing *ANY* child hint
            # from being appended to the "branches_unique" list, which would
            # thus remain empty. This logic avoids that erroneous edge case.
            #
            # Note that we need *NOT* also explicitly test whether
            # "isinstance(branch_that, AnyTypeHint)", as "branch_this" will
            # eventually be "branch_that" and thus trigger this conditional,
            # thus correctly obliterating all previously accumulated results.
            if isinstance(branch_this, AnyTypeHint):
                # Reduces this list to the 1-list containing *ONLY* "Any",
                # thus correctly obliterating all previously accumulated
                # subhint-unique child hints.
                branches_unique = [branch_this]

                # Immediately halt this outer "while" loop.
                break

            # 0-based index of the child hint subscripting this union currently
            # being visited by the inner "while" loop below.
            branch_that_index = 0

            # While one or more child hints subscripting this union have yet to
            # be visited by this inner "while" loop...
            while branch_that_index < branches_len:
                # If...
                if (
                    # The outer child hint being visited is *NOT* the same as
                    # the inner child hint being visited *AND*...
                    #
                    # Note that this is *NOT* simply a microoptimization. Every
                    # type hint is necessarily a subhint of itself. Thus,
                    # permitting this outer child hint to be compared as a
                    # subhint against itself would trigger the "break" statement
                    # for *ALL* child hints, preventing *ANY* child hints from
                    # being appended to the "branches_unique" list.
                    branch_this_index != branch_that_index and
                    # This outer child hint is a subhint of this inner child
                    # hint...
                    branch_this.is_subhint(branches[branch_that_index])
                ):
                    # Then this outer child hint is *NOT* subhint-unique. In
                    # this case, avoid appending this outer child hint to this
                    # list and instead silently continue to the next child hint.
                    break
                # Else, either:
                # * The outer child hint being visited is the same as the inner
                #   child hint being visited *OR*...
                # * This outer child hint is *NOT* a subhint of this inner child
                #   hint.
                #
                # In either case, this iteration has yielded insufficient data
                # to decide this outer child hint is subhint-unique. In this
                # case, proceed to the next inner child hint.

                # Increment the 0-based index of the child hint subscripting
                # this union currently being visited by this inner "while" loop.
                branch_that_index += 1
            # Else, the nested "for" loop above did *NOT* trigger the "break"
            # statement for this outer child hint, which must thus be
            # subhint-unique. Append this outer child hint to this list.
            else:
                branches_unique.append(branch_this)  # type: ignore[arg-type]

            # Increment the 0-based index of the child hint subscripting this
            # union currently being visited by this outer "while" loop.
            branch_this_index += 1

        # Assert that this union is subscripted by at least one subhint-unique
        # child hint (as a crude sanity check). By definition, *ALL* unions
        # *MUST* satisfy this basic constraint.
        assert len(branches_unique) >= 1, (
            f'PEP 484 or 604 union type hint wrapper '
            f'{repr(self)} subscripted by no subhint-unique child type hints.'
        )

        # ..................{ RETURN                         }..................
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

        # If that other hint is the PEP 484-compliant "typing.Any" catch-all,
        # intentionally avoid performing the boolean syllogism below. Instead,
        # reduce to returning the equality of these two hints with the order
        # reversed. See our superclass method commentary for further details.
        if isinstance(other, AnyTypeHint):
            return other == self
        # Else, that other hint is *NOT* "typing.Any".
        #
        # If that other hint is also a union, again avoid performing the boolean
        # syllogism below. Instead, reduce to returning true if and only if
        # these two unions are subscripted by the same subhint-unique branches
        # (i.e., child hints). If the problematic "typing.Any" catch-all did
        # *NOT* exist, the optimal implementation would simply be the default
        # TypeHint._is_equal() implementation performed below as a fallback:
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
        # under that default implementation. Why? Because, under that default
        # implementation,  the example unions "Any | int" and "str | int" would
        # compare equal while having unequal hashes, thus violating
        # equality-hash consistency.
        #
        # The only sane alternative is to compare subhint-unique child hints,
        # which is also unsurprisingly what the _get_hash() method defined below
        # underlying the sibling __hash__() dunder method does.
        elif isinstance(other, UnionTypeHint):
            return self._branches_unique == other._branches_unique
        # Else, that other hint is neither "Any" *NOR* a union.
        #
        # If this union is subscripted by "Any", intentionally avoid performing
        # the boolean syllogism below. Instead, reduce to returning the equality
        # of "Any" with that other hint (i.e., false unless that other hint is
        # also "Any"). See our superclass method commentary for further details.
        elif isinstance(self._branches_unique, AnyTypeHint):
            # print('Here!')
            return self._branches_unique == other
        # Else, this union is *NOT* subscripted by "Any". In this case, perform
        # the boolean syllogism performed by our superclass method.
        else:
            # print('There!')
            # print(f'_branches_unique: {self._branches_unique}')
            return (
                self.is_subhint(other) and
                other.is_subhint(self)
            )


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
                # other union, implying that this union *CANNOT* be a subhint of
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

        # Hash this union by the hashable collection of all subhint-unique
        # branches (i.e., child hints) subscripting this union.
        return hash(self._branches_unique)
