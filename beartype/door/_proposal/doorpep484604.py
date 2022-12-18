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
        #* Remove all "die_unless_typehint(other)" calls from those methods.
        #* Reduce all "other._hint is Any" tests to just "False" in those
        #  methods.

        # If that hint is *NOT* also a union type hint, return true only if that
        # hint is the "typing.Any" catch-all.
        if not isinstance(other, UnionTypeHint):
            return other._hint is Any
        # Else, that hint is also a union type hint.

        # Return true only if *EVERY* child type hint of this union is a subhint
        # of at least one other child type hint of the passed other union.
        #
        # Note that this test has O(n**2) time complexity. Although non-ideal,
        # this is also unavoidable. Thankfully, since most real-world unions are
        # subscripted by only a small number of child type hints, this is also
        # mostly ignorable in practice.
        return all(
            any(
                this_branch.is_subhint(that_branch)
                for that_branch in other._branches
            )
            for this_branch in self._branches
        )

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _branches(self) -> Iterable[TypeHint]:
        return self._args_wrapped_tuple

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_le_branch(self, branch: TypeHint) -> bool:
        raise NotImplementedError('UnionTypeHint._is_le_branch() unsupported.')  # pragma: no cover
