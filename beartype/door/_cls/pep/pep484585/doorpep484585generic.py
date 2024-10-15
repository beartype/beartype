#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) generic type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`- and :pep:`585`-compliant classes subclassing subclassable type
hints, including the ``typing.Generic[...]`` and ``typing.Protocol[...]`` type
hint superclasses).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsuper import TypeHint
from beartype.door._cls.pep.pep484.doorpep484class import ClassTypeHint
from beartype.door._cls.pep.pep484585.doorpep484585subscripted import (
    SubscriptedTypeHint as SubscriptedTypeHint)
from beartype.typing import TYPE_CHECKING

# ....................{ SUBCLASSES                         }....................
class GenericTypeHint(TypeHint):
    '''
    **Generic type hint wrapper** (i.e., high-level object encapsulating a
    low-level subclass of the :pep:`484`-compliant :class:`typing.Generic`
    superclass, :pep:`544`-compliant :class:`typing.Protocol` superclass, or any
    :pep:`585`-compliant subscripted type hint (e.g., ``class
    GenericListOfStrs(list[str]): ...``).
    '''

    # ..................{ STATIC                             }..................
    # Squelch false negatives from static type checkers.
    if TYPE_CHECKING:
        _hint: type

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_subhint_branch(self, branch: TypeHint) -> bool:
        # print(f'Entering GenericTypeHint._is_subhint_branch({self}, {branch})...')

        #FIXME: This is *EXTREMELY* similar to the superclass
        #TypeHint._is_subhint_branch() implementation. Consider generalizing.

        # If the unsubscripted type originating this generic is *NOT* a subclass
        # of the unsubscripted type originating that generic, then this generic
        # is *NOT* a subhint of that generic. In this case, return false.
        if not issubclass(self._origin, branch._origin):
            # print(f'{self._origin} not subclass of {branch._origin})!')
            return False
        # Else, this generic is a subclass of that generic. Note, however, that
        # this does *NOT* imply this generic to be a subhint of that generic.
        # The issubclass() builtin ignores parametrizations and thus returns
        # false positives for parametrized generics: e.g.,
        #     >>> from typing import Generic, TypeVar
        #     >>> T = TypeVar('T')
        #     >>> class MuhGeneric(Generic[T]): pass
        #     >>> issubclass(MuhGeneric, MuhGeneric[int])
        #     True
        #
        # Clearly, the unsubscripted generic "MuhGeneric" is a superhint
        # (rather than a subhint) of the subscripted generic
        # "MuhGeneric[int]". Further introspection is needed to decide how
        # exactly these two generics interrelate.
        #
        # If that branch is unsubscripted, assume that branch to have been
        # subscripted by "Any". Since *ANY* child hint subscripting this hint is
        # necessarily a subhint of "Any", this hint is a subhint of that branch.
        # Return true immediately.
        elif branch._is_args_ignorable:
            # print(f'is_subhint_branch({self}, {branch} [unsubscripted])')
            return True
        # Else, that branch is subscripted.

        #FIXME: If this actually works:
        #* Revise comment accordingly.
        #* Globalize this 2-tuple as a new private global.
        #* Since this is the only line that differs between this and the
        #  superclass _is_subhint_branch(), generalize this out, please.
        # If that branch is also a type hint wrapper of the same concrete
        # subclass as this type hint wrapper *AND*...
        elif not isinstance(branch, _IS_SUBHINT_TYPES_COMMENSURABLE):
            # print(f'{branch.__class__} not in {_IS_SUBHINT_TYPES_COMMENSURABLE})!')
            return False

        #FIXME: Do something intelligent here. In particular, we probably
        #*MUST* expand unsubscripted generics like "MuhGeneric" to their
        #full transitive subscriptions like "MuhGeneric[T]". Of course,
        #"MuhGeneric" has *NO* "__args__" and only an empty "__parameters__";
        #both are useless. Ergo, we have *NO* recourse but to iteratively
        #reconstruct the full transitive subscriptions for unsubscripted
        #generics by iterating with the
        #iter_hint_pep484585_generic_bases_unerased_tree() iterator. The idea
        #here is that we want to iteratively inspect first the "__args__" and
        #then the "__parameters__" of all superclasses of both "self" and
        #"branch" until obtaining two n-tuples (where "n" is the number of
        #type variables with which the root "Generic[...]" superclass was
        #originally subscripted):
        #* "self_args", the n-tuple of all types or type variables
        #   subscripting this generic.
        #* "branch_args", the n-tuple of all types or type variables
        #   subscripting the "branch" generic.
        #
        #Once we have those two n-tuples, we can then decide the is_subhint()
        #relation by simply iteratively subjecting each pair of items from
        #both "self_args" and "branch_args" to is_subhint(). Notably, we
        #return True if and only if is_subhint() returns True for *ALL* pairs
        #of items of these two n-tuples.
        #FIXME: Actually, it might be sufficient to just do something
        #resembling:
        #    if self._is_args_ignorable:
        #        args_wrapped_tuple = ...
        #
        #Actually, maybe we should just override _make_args() like so:
        #    def _make_args(self) -> tuple:
        #        return (
        #            get_hint_pep_args(self._hint) or
        #            get_hint_pep_typevars(self._hint)
        #        )
        #
        #Come to think of it: shouldn't that *ALREADY* be the superclass
        #implementation? Seems genuinely useful, honestly.

        # Return true only if all child type hints of this parent type hint are
        # subhints of the corresponding child type hints of that branch.
        # print(f'Comparing {self._args_wrapped_tuple} against {branch._args_wrapped_tuple}...')
        return all(
            self_child <= branch_child
            for self_child, branch_child in zip(
                self._args_wrapped_tuple, branch._args_wrapped_tuple)
        )

# ....................{ PRIVATE ~ constants                }....................
_IS_SUBHINT_TYPES_COMMENSURABLE = (
    # Generics are commensurable with other generics, clearly.
    GenericTypeHint,

    # Generics are also commensurable with subscripted type hints: e.g.,
    #     >>> from collections.abc import Sequence
    #     >>> class MuhSequence[T](Sequence[T]): pass
    #     >>> is_subhint(MuhSequence[T], Sequence[int])
    #     True
    SubscriptedTypeHint,

    # Generics are also commensurable with unsubscripted classes: e.g.,
    #     >>> from collections.abc import Sequence
    #     >>> class MuhSequence[T](Sequence[T]): pass
    #     >>> is_subhint(MuhSequence[T], Sequence)
    #     True
    ClassTypeHint,
)
'''
Tuple of all **commensurable generic types** (i.e., concrete :class:`.TypeHint`
subclasses such that the :meth:`GenericTypeHint._is_subhint_branch` method
returns :data:`False` if the passed ``branch`` parameter is *not* an instance of
a type in this tuple).

When passed a ``branch`` parameter that is *not* an instance of a type in this
tuple, the :meth:`GenericTypeHint._is_subhint_branch` method returns
:data:`False` due to that parameter being **incommensurable** (i.e.,
incomparable) with a :pep:`484`-compliant :class:`typing.Generic`.
'''
