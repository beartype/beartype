#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) union type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant :attr:`typing.Optional` and :attr:`typing.Union` type
hints and :pep:`604`-compliant ``|``-delimited union type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._doorcls import (
    TypeHint,
    _TypeHintSubscripted,
)
from beartype.door._doortest import die_unless_typehint
from beartype.typing import (
    Any,
    Iterable,
)
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ SUBCLASSES                         }....................
class UnionTypeHint(_TypeHintSubscripted):
    '''
    **Union type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`-compliant :attr:`typing.Optional` or
    :attr:`typing.Union` type hint *or* :pep:`604`-compliant ``|``-delimited
    union type hint).
    '''

    # ..................{ TESTERS                            }..................
    @callable_cached
    def is_subhint(self, other: TypeHint) -> bool:

        # If the passed object is *NOT* a type hint wrapper, raise an exception.
        die_unless_typehint(other)
        # Else, the passed object is a type hint wrapper.

        #FIXME: Generalize. The test for "other._hint is Any" is generally
        #applicable to *ALL* type hints and should thus reside in the "TypeHint"
        #superclass. Do so as follows, please:
        #* Define TypeHint.is_subhint() to resemble:
        #      @callable_cached
        #      def is_subhint(self, other: TypeHint) -> bool:
        #
        #          # If the passed object is *NOT* a type hint wrapper, raise an exception.
        #          die_unless_typehint(other)
        #
        #          # If that hint is the "typing.Any" catch-all, return true.
        #          if other._hint is Any:
        #              return True
        #          # Else, that hint is *NOT* the "typing.Any" catch-all.
        #
        #          # Defer to the subclass-specific implementation of this test.
        #          return self._is_subhint(other)
        #* Define TypeHint._is_subhint() to resemble:
        #      def _is_subhint(self, other: TypeHint) -> bool:
        #          raise NotImplementedError(  # pragma: no cover
        #              'Abstract method TypeHint._is_subhint() undefined.')
        #* Rename all subclass is_subhint() methods to _is_subhint().
        #* Remove from those methods:
        #  * All "die_unless_typehint(other)" calls.
        #  * All @callable_cached decorations.
        #* Reduce all "other._hint is Any" tests to just "False" in those
        #  methods.

        # Return true only if *EVERY* child type hint of this union is a subhint
        # of at least one other child type hint of the passed other union.
        #
        # Note that this test has O(n**2) time complexity. Although non-ideal,
        # this is also unavoidable. Thankfully, since most real-world unions are
        # subscripted by only a small number of child type hints, this is also
        # mostly ignorable in practice.
        return all(
            # For each child type hint subscripting this union...
            (
                # If that other type hint is itself a union, true only if...
                any(
                    # For at least one other child type hint subscripting that
                    # other union, this child type hint is a subhint of that
                    # other child type hint.
                    this_branch.is_subhint(that_branch)
                    for that_branch in other._branches
                ) if isinstance(other, UnionTypeHint) else
                # Else, that other type hint is *NOT* a union. In this case,
                # true only if this child type hint is a subhint of that other
                # type hint.
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


    #FIXME: Unit test us up, please.
    # Override the default equality comparison with a union-specific comparison.
    # Union equality compares child type hints collectively (i.e., with respect
    # to *ALL* children subscripting those unions as a unified whole) rather
    # than individually (i.e., with respect to only each child subscripting
    # those unions as a distinct member). The default equality comparison
    # only compares child type hints individually. Although doing so suffices
    # for most type hints, unions are effectively sets of child type hints.
    # Individuality is irrelevant; only the collective matters. Welcome to the
    # Union Borg. We do hope you enjoy your stay, Locutius of QA.
    #
    # Note that we intentionally avoid typing this method as returning
    # "Union[bool, NotImplementedType]". Why? Because mypy in particular has
    # epileptic fits about "NotImplementedType". This is *NOT* worth the agony!
    @callable_cached
    def __eq__(self, other: object) -> bool:

        #FIXME: Note that this could probably be marginally optimized by
        #duplicating the iteration performed by the is_subhint() tester here,
        #refactored to perform the desired dual comparison. However, efficiency
        #is *NOT* a prominent concern for the DOOR API. Since performing this
        #optimization would violate DRY while *NOT* improving the Big-Oh
        #computational complexity of this operation, we avoid doing so.

        # Return true only if either...
        return (
            # If that object is *NOT* an instance of the same class, it is both
            # the case that...
            #
            # Note that this conditional implements the trivial boolean
            # syllogism that we all know: "If A <= B and B <= A, then A == B".
            (  # type: ignore[return-value]
                # This union is a subhint of that object.
                self.is_subhint(other) and
                # That object is a subhint of this union.
                other.is_subhint(self)
            )
            if isinstance(other, TypeHint) else
            # Else, that object is *NOT* an instance of the same class. In this
            # case, defer to either:
            # * If the class of that object defines a similar __eq__() method
            #   supporting the "TypeHint" API, that method.
            # * Else, Python's builtin C-based fallback equality comparator that
            #   merely compares whether two objects are identical (i.e., share
            #   the same object ID).
            NotImplemented
        )

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _branches(self) -> Iterable[TypeHint]:
        return self._args_wrapped_tuple

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_le_branch(self, branch: TypeHint) -> bool:
        raise NotImplementedError('UnionTypeHint._is_le_branch() unsupported.')  # pragma: no cover
