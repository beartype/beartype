#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646`-compliant **tuple type
hint utilities** (i.e., low-level callables generically applicable to
:pep:`484`- and :pep:`585`-compliant purely fixed- and variadic-length tuple
type hints *and* :pep:`646`-compliant mixed fixed-variadic tuple type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import (
    HintGenericSubscriptedType,
    HintPep646TypeVarTupleType,
)
from beartype._data.hint.datahintpep import (
    Hint,
    # TypeIs,
)
from beartype._data.hint.pep.sign.datapepsigns import (
    # HintSignPep646UnpackedTuple,
    HintSignUnpack,
)

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_hint_pep646_unpacked_tuple(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed hint is a :pep:`646`-compliant **unpacked
    child tuple hint** (e.g., the child hint ``*tuple[str, ...]`` subscripting
    the parent tuple hint ``tuple[int, *tuple[str, ...], float]``).

    If this tester returns :data:`True`, then this unpacked child tuple hint is
    guaranteed to define the standard ``__args__`` dunder attribute to be
    either:

    * A 2-tuple ``({hint_child}, ...)``, in which case this child tuple hint
      unpacks to a variable-length tuple hint over ``{hint_child}`` types.
    * An n-tuple ``({hint_child_1}, ..., {hint_child_N})`` where ``...`` in this
      case is merely a placeholder connoting one or more child hints, in which
      case this child tuple hint unpacks to a fixed-length tuple hint over these
      exact ``{hint_child_I}`` types.

    This getter is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to
    an efficient one-liner.

    Motivation
    ----------
    Interestingly, even detecting accursed unpacked child tuple hints at runtime
    is highly non-trivial. They do *not* have a sane unambiguous type,
    significantly complicating detection. For some utterly inane reason, their
    type is simply the ambiguous type :class:`types.GenericAlias` (i.e.,
    :class:`.HintGenericSubscriptedType`). That... wasn't what we were expecting
    *at all*. For example, under Python 3.13:

    .. code-block:: python

       # Note that Python *REQUIRES* unpacked tuple type hints to be embedded in
       # some larger syntactic construct. So, just throw it into a list. This is
       # insane, because we're only going to rip it right back out of that list.
       # Blame the CPython interpreter. *shrug*
       >>> yam = [*tuple[int, str]]

       # Arbitrary unpacked tuple type hint.
       >>> yim = yam[0]
       >>> repr(yim)
       *tuple[int, str]  # <-- gud
       >>> type(yim)
       <class 'types.GenericAlias'>  # <-- *TOTALLY NOT GUD. WTF, PYTHON!?*

       # Now look at this special madness. The type of this object isn't even in
       # its method-resolution order (MRO)!?!? I've actually never seen that
       # before. The type of any object is *ALWAYS* the first item in its
       # method-resolution order (MRO), isn't it? I... guess not. *facepalm*
       >>> yim.__mro__
       (<class 'tuple'>, <class 'object'>)

       # So, "*tuple[int, str]" is literally both a tuple *AND* a "GenericAlias"
       # at the same time. That makes no sense, but here we are. What are the
       # contents of this unholy abomination?
       >>> dir(yim)
       ['__add__', '__args__', '__bases__', '__class__', '__class_getitem__',
       '__contains__', '__copy__', '__deepcopy__', '__delattr__', '__dir__',
       '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__',
       '__getitem__', '__getnewargs__', '__getstate__', '__gt__', '__hash__',
       '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__',
       '__mro_entries__', '__mul__', '__ne__', '__new__', '__origin__',
       '__parameters__', '__reduce__', '__reduce_ex__', '__repr__', '__rmul__',
       '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
       '__typing_unpacked_tuple_args__', '__unpacked__', 'count', 'index']

       # Lotsa weird stuff there, honestly. Let's poke around a bit.
       >>> yim.__args__
       (<class 'int'>, <class 'str'>)  # <-- gud
       >>> yim.__typing_unpacked_tuple_args__
       (<class 'int'>, <class 'str'>)  # <-- gud, albeit weird
       >>> yim.__unpacked__
       True  # <-- *WTF!?!? what the heck is this nonsense?*
       >>> yim.__origin__
       tuple  # <-- so you lie about everything, huh?

    Basically, the above means that the only means of reliably detecting an
    unpacked tuple hint at runtime is by heuristically introspecting for both
    the existence *and* values of various dunder attributes exhibited above.
    Introspecting merely the existence of these attributes is insufficient; only
    the combination of both existence and values suffices to effectively
    guarantee disambiguity. Likewise, introspecting merely one or even two of
    these attributes is insufficient; only the combination of three or more of
    these attributes suffices to effectively guarantee disambiguity.

    Note there *are* no means of actually guaranteeing disambiguity. Malicious
    third-party objects could attempt to masquerade as unpacked child tuple
    hints by defining similar dunder attributes. We can only reduce the
    likelihood of false positives by increasing the number of dunder attributes
    introspected by this tester. Don't blame us. We didn't start the fire.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this hint is an unpacked child tuple hint.
    '''

    # Return true only if...
    return (
        # This hint's type is that of all unpacked child tuple hints (as well as
        # many other unrelated first- and third-party hints, sadly) *AND*...
        hint.__class__ is HintGenericSubscriptedType and
        (
            # The tuple of all child hints subscripting this parent hint is also
            # the tuple of all child hints subscripting this unpacked child
            # tuple hint. Since only unpacked child tuple hints *SHOULD* define
            # the PEP 646-compliant and frankly outrageously verbose
            # "__typing_unpacked_tuple_args__" dunder attribute, this
            # equivalence *SHOULD* suffice to disambiguate this hint as an
            # unpacked child tuple hint.
            getattr(hint, '__args__', False) ==
            getattr(hint, '__typing_unpacked_tuple_args__', True)
        )
        #FIXME: Probably unnecessary for the moment. Let's avoid violating
        #fragile privacy encapsulation any more than we must, please. *sigh*
        # # This hint's method-resolution order (MRO) is that of all unpacked
        # # child tuple hints *AND*...
        # getattr(hint, '__mro__', None) == _PEP646_HINT_TUPLE_UNPACKED_MRO and  # pyright: ignore
        # # This hint defines a dunder attribute uniquely defined *ONLY* by
        # # unpacked child tuple hints with a value guaranteed to be set by all
        # # unpacked child tuple hints.
        # getattr(hint, '__unpacked__', None) is True
    )


#FIXME: Unit test us up, please.
def is_hint_pep646_unpacked_type_variable_tuple(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed hint is a :pep:`646`-compliant **unpacked
    type variable tuple** (e.g., the child hint ``*Ts`` subscripting the parent
    tuple hint ``tuple[str, *Ts, bool]``).

    This getter enables callers to disambiguate between otherwise ambiguous
    unpacked type hints sharing the same ambiguous sign of
    :data:`.HintSignUnpack`. This includes:

    * :pep:`646`-compliant **unpacked type variable tuples.**
    * :pep:`692`-compliant **unpacked typed dictionaries** (e.g.,
      ``typing.Unpack[SomeTypedDict]`` where ``SomeTypedDict`` is a subclass of
      :class:`typing.TypedDict`).

    This getter is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to
    an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this hint is an unpacked type variable tuple.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args
    from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # If this is a PEP 646- or 692-compliant "typing.Unpack[...]" hint, this
    # *COULD* be a PEP 646-compliant unpacked type variable tuple. Why? Because
    # CPython unpacks type variable tuples of the form "*Ts" into semantically
    # equivalent hints of the form "typing.Unpack[Ts]". Why? No idea. Who cares!
    if hint_sign is HintSignUnpack:
        # Tuple of the zero or more child hints subscripting this hint.
        hint_childs = get_hint_pep_args(hint)

        # Return true only if...
        return (
            # This hint is subscripted by exactly one child hint *AND*...
            len(hint_childs) == 1 and
            # This child hint is a PEP 646-compliant type variable tuple.
            isinstance(hint_childs[0], HintPep646TypeVarTupleType)
        )
    # Else, this is *NOT* PEP 646- or 692-compliant "typing.Unpack[...]" hint.
    # This hint *CANNOT* be a PEP 646-compliant unpacked type variable tuple.

    # Return false as a fallback.
    return False
