#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) subscripted type
hint classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing
support for :pep:`484`- and :pep:`585`-compliant subscripted type hints *not*
already matched by a more fine-grained :class:`beartype.door.TypeHint`
subclass).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorabc import TypeHint
from beartype.roar import BeartypeDoorPepArgsLenException
from beartype._data.hint.sign.datahintsignmap import (
    HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE)
from beartype._data.hint.sign.datahintsignset import (
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_ZERO_OR_MORE)

# ....................{ SUBCLASSES                         }....................
class SubscriptedTypeHint(TypeHint):
    '''
    **Subscripted type hint wrapper** (i.e., high-level object encapsulating
    a low-level :pep:`484`- and :pep:`585`-compliant type hint satisfying
    various conditions).

    Notably, this wrapper wraps hints that both:

    * Are subscripted (indexed) by a predetermined number of one or more
      low-level child type hints.
    * Originate from an **isinstanceable class** such that *all* objects
      satisfying this hint are instances of that class.
    '''

    # ..................{ PRIVATE ~ factories                }..................
    def _make_args(self) -> tuple:

        # Tuple of the zero or more low-level child type hints subscripting
        # (indexing) the low-level parent type hint wrapped by this wrapper.
        args = super()._make_args()

        # If this hint is *NOT* subscripted by the expected number of child
        # hints, raise an exception.
        self._die_unless_args_len_range(args)
        # Else, this hint is subscripted by the expected number of child hints.

        # Return these child hints.
        return args

    # ..................{ PRIVATE ~ raisers                  }..................
    def _die_unless_args_len_range(self, args: tuple) -> None:
        '''
        Raise an exception unless this hint is subscripted by the expected
        number of child hints.

        Subclasses encapsulating hints subscripted by a variable number of child
        hints are encouraged to override this property to reduce to a noop.
        Since most hints are subscripted by a fixed number of child hints, this
        property defaults to returning :data:`True` for almost *all* subclasses.

        Parameters
        ----------
        args : tuple
            Tuple of the zero or more child hints subscripting this hint to be
            validated.

        Raises
        ------
        BeartypeDoorPepArgsLenException
            If this hint is *not* subscripted by the expected number of child
            hints.
        '''

        # If the sign uniquely identifying this hint is in the set of all signs
        # uniquely identifying hints subscripted by one or more child hints,
        # this hint is already necessarily subscripted by the expected number of
        # child hints. In this case, silently reduce to a noop.
        if self._hint_sign in (
            HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_ZERO_OR_MORE):
            return
        # Else, the sign uniquely identifying this hint is *NOT* in the set of
        # all signs uniquely identifying hints subscripted by one or more child
        # hints.

        # Argument length range (i.e., "range" object covering the minimum and
        # maximum number of child type hints that may subscript this low-level
        # parent type hint factory) if this factory has been associated with
        # such a range *OR* "None" otherwise (i.e., if this factory has *NOT*
        # been associated with such a range).
        args_len_range = HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE.get(
            self._hint_sign)  # type: ignore[arg-type]

        # If this factory has *NOT* been associated with such a range, raise an
        # exception. Note that this edge case should *NEVER occur. ----gulp----
        if args_len_range is None:  # pragma: no cover
            raise BeartypeDoorPepArgsLenException(  # pragma: no cover
                f'Type hint {repr(self._hint)} argument length range unknown.')
        # Else, this factory has been associated with such a range.

        # Total number of child hints subscripting this hint.
        args_len = len(args)

        #FIXME: Consider actually testing this. This *IS* technically testable
        #and should thus *NOT* be marked as "pragma: no cover".
        # If this hint was subscripted by an unexpected number of child hints...
        #
        # Note that this edge case commonly occurs with PEP 585-compliant type
        # hints (e.g., "list[str]"), which fail to validate their number of
        # child type hints: e.g.,
        #     >>> list[str, int]
        #     list[str, int]  # <-- wat
        if args_len not in args_len_range:  # pragma: no cover
            #FIXME: This seems sensible, but currently provokes test failures.
            #Let's investigate further at a later time, please. *sigh*
            # # If this hint was subscripted by *NO* parameters, comply with PEP
            # # 484 standards by silently pretending this hint was subscripted by
            # # the "typing.Any" fallback for all missing parameters.
            # if len(self._args) == 0:
            #     return (Any,)*self._args_len_expected

            # Exception message to be raised.
            exception_message = (
                f'PEP 585 type hint {repr(self._hint)} '
                f'not subscripted (indexed) by '
            )

            # Minimum and maximum number of arguments accepted by this factory.
            #
            # Note that the "stop" instance variable defined by "range" objects
            # is exclusive rather than inclusive. Subtracting 1 from that
            # yields the inclusive maximum of this range.
            ARGS_LEN_MIN = args_len_range.start
            ARGS_LEN_MAX = args_len_range.stop - 1

            # If this factory accepts a constant (rather than variable) number
            # of child hints, raise a human-readable exception denoting this.
            if ARGS_LEN_MIN == ARGS_LEN_MAX:
                # Human-readable noun describing the grammatically correct
                # plurality of the number of expected child type hints. English!
                exception_noun = (
                    'child type hint'
                    if ARGS_LEN_MAX == 1 else
                    'child type hints'
                )

                # Append this number to this exception message.
                exception_message += (
                    f'{ARGS_LEN_MAX} {exception_noun} (i.e., '
                    f'subscripted by {args_len} != '
                    f'{ARGS_LEN_MAX} child type hints).'
                )
            # Else, this factory accepts a variable number of child hints. Raise
            # a human-readable exception denoting this.
            else:
                # Append this number to this exception message.
                exception_message += (
                    f'[{ARGS_LEN_MIN}, {ARGS_LEN_MAX}] arguments (i.e., '
                    f'subscripted by {args_len} child type hints).'
                )

            # Raise this exception.
            raise BeartypeDoorPepArgsLenException(exception_message)
        # Else, this hint was subscripted by the expected number of child hints.

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_equal(self, other: TypeHint) -> bool:

        # ..................{ NOOP                           }..................
        # If *ALL* of the child hints subscripting both of these hints are
        # ignorable, return true only if both of these hints originate from the
        # same low-level type.
        if self._is_args_ignorable and other._is_args_ignorable:
            return self._origin_type == other._origin_type
        # Else, one or more of the child type hints subscripting either of these
        # hints are unignorable.
        #
        # If either...
        elif (
            # These hints are identified by differing signs *OR*...
            self._hint_sign is not other._hint_sign or
            # These hints are subscripted by differing numbers of child hints...
            len(self._args_wrapped_tuple) != len(other._args_wrapped_tuple)
        ):
            # Then these hints are unequal.
            return False
        # Else, these hints share the same sign and number of child hints.

        # ..................{ RETURN                         }..................
        # For each pair of child hints subscripting the same index of both of
        # these parent hints...
        for this_child, that_child in zip(
            self._args_wrapped_tuple, other._args_wrapped_tuple):
            # If this child hint is unequal to that child hint, this parent hint
            # is unequal to that parent hint. In this case, return false.
            if this_child != that_child:
                return False
            # Else, this child hint is equal to that child hint, implying this
            # parent hint *COULD* be equal to that parent hint. Continue to the
            # next child hint to decide.

        # Return true as a safe fallback.
        return True

    # ..................{ PRIVATE ~ getters                  }..................
    def _get_hash(self) -> int:

        # Low-level hashable object encapsulated by this high-level wrapper to
        # be hashed below as the hash for this wrapper, defined as either...
        wrapper_hashable = (
            # If at least one of the child hints subscripting this hint is
            # unignorable, the hashable 2-tuple combining (in arbitrary order):
            # * The type originating this hint (e.g., "list" for "list[int]").
            # * All nested "TypeHint" objects wrapping these child hints.
            #
            # This hash has the minor disadvantage of increased time complexity
            # but the major advantage of preserving consistency between equality
            # and hashes. Specifically, doing so ensures that semantically
            # equivalent subscripted PEP 484- and 585-compliant type hints
            # (e.g., "list[int]" and "typing.List[int]"), which compare equal,
            # also share the same hash.
            hash((self._origin_type, self._args_wrapped_tuple))
            if not self._is_args_ignorable else
            # Else, *ALL* child hints subscripting this hint are ignorable. In
            # this case, the type originating this hint. Doing so ensures that
            # unsubscripted type hint factories and the corresponding type
            # hints subscripted by ignorable child hints (e.g., "list" and
            # "list[object]"), which compare equal, also share the same hash.
            self._origin_type
        )

        # Hash this wrapper by this hashable.
        return hash(wrapper_hashable)
