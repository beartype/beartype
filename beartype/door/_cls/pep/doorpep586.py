#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) literal type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`586`-compliant :attr:`typing.Literal` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorabc import (
    TypeHint,
    TupleTypeHints,
)
from beartype._data.typing.datatypingport import Hint
from beartype._util.cache.func.utilcacheproperty import (
    get_property_var_name,
    property_cached,
)
from beartype._util.hint.pep.proposal.pep586 import make_hint_pep586_literal
from beartype._util.hint.pep.proposal.pep484.pep484604union import (
    make_hint_pep484604_union)

# ....................{ SUBCLASSES                         }....................
class LiteralTypeHint(TypeHint):
    '''
    **Literal type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`586`-compliant :attr:`typing.Literal` type hint).
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
        get_property_var_name('_args_frozenset'),
        get_property_var_name('_union_arg_types_wrapped'),
    )

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _is_args_ignorable(self) -> bool:

        # Return true to present PEP 586-compliant literal hints as subscripted
        # from the low-level perspective of physically existing child hints.
        # Doing so prevents logic elsewhere (e.g., the
        # UnsubscriptedTypeHint._is_subhint_branch() method) from erroneously
        # treating PEP 586-compliant literal hints as unsubscripted.
        return False


    @property
    def _args_wrapped_tuple(self) -> TupleTypeHints:

        # Return the empty tuple to present PEP 586-compliant literal hints as
        # unsubscripted from the high-level perspective of semantically
        # comparable child hints. The arguments subscripting a literal hint are
        # (typically, anyway) *NOT* PEP-compliant type hints and thus *CANNOT*
        # be safely wrapped by "TypeHint" instances. These arguments are merely
        # arbitrary values.
        #
        # Note that this property getter is intentionally *NOT* memoized with
        # @property_cached, as Python already efficiently guarantees the empty
        # tuple to be a singleton.
        return ()

    # ..................{ PRIVATE ~ properties : custom      }..................
    # Custom private properties required *ONLY* be methods defined below.

    #FIXME: Unit test us up, please. *sigh*
    @property  # type: ignore
    @property_cached
    def _args_frozenset(self) -> frozenset:
        '''
        Frozen set of all child hints subscripting this :pep:`586`-compliant
        literal hint.
        '''

        # Mirage coordinator of a wingless apathy, one-liner! *wat*
        return frozenset(self._args)


    #FIXME: Unit test us up, please. *sigh*
    @property  # type: ignore
    @property_cached
    def _union_arg_types_wrapped(self) -> Hint:
        '''
        :pep:`484`- or :pep:`604`-compliant union over the types of all child
        hints subscripting this :pep:`586`-compliant literal hint (e.g.,
        ``int | str`` for ``typing.Literal[0xCAFEBABE, 'so cafe so babe']``).
        '''

        # Tuple of the types of all child hints subscripting this hint.
        union_childs = tuple(
            type(literal_child) for literal_child in self._args)

        # PEP 484- or 604-compliant union subscripted by these types.
        union_child_types = make_hint_pep484604_union(union_childs)
        # print(f'union_child_types: {union_child_types}')

        # Return this union wrapped by "TypeHint".
        return TypeHint(union_child_types)  # pyright: ignore

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_subhint(self, other: TypeHint) -> bool:

        # Return true only if either...
        return (
            # If the passed hint is also a literal, return true only if the
            # frozen set of all child hints subscripting this literal is a
            # subset of the frozen set of all child hints subscripting the
            # passed literal;
            self._args_frozenset <= other._args_frozenset
            if isinstance(other, LiteralTypeHint) else
            # False
            # Else, the passed hint is *NOT* also a literal. In this case,
            # return true only if either...
            (
                # The type of each child hint subscripting this literal is a
                # subhint (e.g., subclass) of the passed hint *OR*...
                #
                # This test makes little sense until one considers category and
                # group theory. Consider the algebraic number field of integers.
                # There exist countably infinite integers. The set of all
                # integers thus exists, albeit only in the abstract sense. Next,
                # consider a PEP 586-compliant literal hint subscripted by two
                # or more integers (e.g., "Literal[1, 2]"). Semantically, that
                # hint describes the proper subset of integers "{1, 2}".
                # Likewise, the builtin type "int" describes the countably
                # infinite set of all integers. Ergo, *ANY* PEP 586-compliant
                # literal hint subscripted by two or more integers could be
                # considered a subhint of "int". Why? Because one *COULD* (in
                # the abstract, anyway) programmatically construct a total and
                # complete PEP 586-compliant literal hint subscripted by *ALL*
                # possible integers; that hint would then be semantically
                # equivalent to and thus a subhint of "int". Given that, any
                # smaller literal hint *MUST* also then be a subhint of "int".
                # The same logic generalizes to:
                # * *ANY* PEP 586-compliant literal hint subscripted by one
                #   integer, which could be said to describe the proper subset
                #   of integers containing *ONLY* that integer.
                # * *ANY* PEP 586-compliant literal hint subscripted by *ANY*
                #   other types of literals, by the same exact argument.
                #
                # Note that unlike most type hints, each child hint subscripting
                # this literal is typically *NOT* a valid type hint in and of
                # itself (e.g., "Literal[True]" is a valid type hint, but "True"
                # is not). This test thus *CANNOT* be reduced to this simpler
                # and seemingly more sensible variant:
                #      return all(
                #          hint_child.is_subhint(other)
                #          for hint_child in self._args_wrapped_tuple
                #      )
                self._union_arg_types_wrapped <= other or
                # self._union_arg_types_wrapped <= other
                # Else, the type of each child hint subscripting this literal is
                # *NOT* a subhint (e.g., subclass) of the passed hint. However,
                # this literal *COULD* still be a subhint of that hint according
                # to standard typing semantics (e.g., due to itself being a
                # child hint subscripting the passed hint). Decide whether this
                # is the case by trivially deferring to our superclass: e.g.,
                #     # This test handles this surprisingly common edge case.
                #     >>> TypeHint(Literal[True]) <=
                #     ... TypeHint(Union[Literal[True], Literal[False]])
                #     True
                super()._is_subhint(other)
            )
        )

    # ..................{ PRIVATE ~ getters                  }..................
    def _get_hash(self) -> int:

        # Low-level hashable object to be hashed below as the hash for this
        # wrapper, defaulting to the literal hint encapsulated by this wrapper.
        wrapper_hashable = self._hint

        # If this PEP 586-compliant literal hint is subscripted by two or more
        # child hints, return the hash of a new PEP 484- or 604-compliant union
        # over one new PEP 586-compliant literal hint subscripted by each such
        # child hint individually (rather than simply returning the hash of this
        # hint as is). Why? To preserve consistency between this hint and that
        # union, which compare equal and *MUST* thus share the same hash: e.g.,
        #     >>> from beartype.door import TypeHint
        #     >>> from typing import Literal
        #     >>> foo = TypeHint(Literal[1, 2])
        #     >>> bar = TypeHint(Literal[1] | Literal[2])
        #     >>> foo == bar
        #     True  # <-- woah
        #     >>> hash(foo) == hash(bar)
        #     True  # <-- this edge case requires this edge case logic *sigh*
        #
        # Specifically...
        if len(self._args) >= 2:
            # Tuple comprised of one new PEP 586-compliant literal hint
            # subscripted by each child hint subscripting this hint. For
            # example, if this hint is "Literal[1, 2]", this tuple is
            # "(Literal[1], Literal[2])".
            #
            # Note that this _get_hint() getter is effectively memoized by our
            # superclass. Ergo, neither this nor the following union need be
            # explicitly memoized by us. We give thanks for small favours! \o/
            union_childs = tuple(
                make_hint_pep586_literal((literal_child,))
                for literal_child in self._args
            )

            # PEP 484- or 604-compliant union subscripted by these new PEP
            # 586-compliant literal hints. For example, if this hint is
            # "Literal[1, 2]", this union is "Literal[1] | Literal[2])".
            wrapper_hashable = make_hint_pep484604_union(union_childs)
        # Else, this PEP 586-compliant literal hint is subscripted by either one
        # or no child hints. In either case, preserve this default hashable.

        # Hash this hashable object, yo! *sigh*
        return hash(wrapper_hashable)
