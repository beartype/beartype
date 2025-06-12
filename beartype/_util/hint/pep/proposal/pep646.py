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
from beartype._cave._cavefast import HintGenericSubscriptedType
from beartype._data.hint.datahintpep import Hint

# ....................{ TESTERS                            }....................
#FIXME: Incorporate the following text into the docstring below.
#
#Interestingly, even detecting accursed objects like "*Tuple[str, ...]" at
#runtime is highly non-trivial. They do *NOT* have a sane unambiguous type,
#significantly complicating detection. For some utterly inane reason, their type
#is simply the ambiguous "types.GenericAlias" type. That... wasn't what we were
#expecting *AT ALL*. For example, under Python 3.13:
#    # Note that Python *REQUIRES* unpacked tuple type hints to be embedded in
#    # some larger syntactic construct. So, just throw it into a list. This is
#    # insane, because we're only going to rip it right back out of that list.
#    # Blame the CPython interpreter. *shrug*
#    >>> yam = [*tuple[int, str]]
#
#    # Arbitrary unpacked tuple type hint.
#    >>> yim = yam[0]
#    >>> repr(yim)
#    *tuple[int, str]  # <-- gud
#    >>> type(yim)
#    <class 'types.GenericAlias'>  # <-- *TOTALLY NOT GUD. WTF, PYTHON!?*
#
#    # Now look at this special madness. The type of this object isn't even in
#    # its method-resolution order (MRO)!?!? I've actually never seen that
#    # before. The type of any object is *ALWAYS* the first item in its
#    # method-resolution order (MRO), isn't it? I... guess not. *facepalm*
#    >>> yim.__mro__
#    (<class 'tuple'>, <class 'object'>)
#
#    # So, "*tuple[int, str]" is literally both a tuple *AND* a "GenericAlias"
#    # at the same time. That makes no sense, but here we are. What are the
#    # contents of this unholy abomination?
#    >>> dir(yim)
#    ['__add__', '__args__', '__bases__', '__class__', '__class_getitem__',
#    '__contains__', '__copy__', '__deepcopy__', '__delattr__', '__dir__',
#    '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__',
#    '__getitem__', '__getnewargs__', '__getstate__', '__gt__', '__hash__',
#    '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__',
#    '__mro_entries__', '__mul__', '__ne__', '__new__', '__origin__',
#    '__parameters__', '__reduce__', '__reduce_ex__', '__repr__', '__rmul__',
#    '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
#    '__typing_unpacked_tuple_args__', '__unpacked__', 'count', 'index']
#
#    # Lotsa weird stuff there, honestly. Let's poke around a bit.
#    >>> yim.__args__
#    (<class 'int'>, <class 'str'>)  # <-- gud
#    >>> yim.__typing_unpacked_tuple_args__
#    (<class 'int'>, <class 'str'>)  # <-- gud, albeit weird
#    >>> yim.__unpacked__
#    True  # <-- *WTF!?!? what the heck is this nonsense?*
#    >>> yim.__origin__
#    tuple  # <-- so you lie about everything, huh?
#
#Basically, the above means that the only means of reliably detecting an
#unpacked tuple type hint at runtime is as follows:

#FIXME: Unit test us up, please.
def is_pep646_hint_tuple_unpacked(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed hint is a :pep:`646`-compliant **unpacked
    child tuple hint** (e.g., the child hint ``*tuple[str, ...]`` subscripting
    the parent tuple hint ``tuple[int, *tuple[str, ...], float]``).

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this hint is an unpacked child tuple hint.
    '''

    #FIXME: Comment us up, please.
    # Return true only if...
    return (
        hint.__class__ is HintGenericSubscriptedType and
        hint.__mro__ == _PEP646_HINT_TUPLE_UNPACKED_MRO and  # pyright: ignore
        getattr(hint, '__unpacked__', None) is True
        #FIXME: Probably unnecessary for the moment. Let's avoid violating
        #fragile privacy encapsulation any more than we must, please. *sigh*
        # (
        #     getattr(hint, '__args__', False) ==
        #     getattr(hint, '__typing_unpacked_tuple_args__', True)
        # )
    )

# ....................{ PRIVATE ~ globals                  }....................
_PEP646_HINT_TUPLE_UNPACKED_MRO = (tuple, object)
'''
Method-resolution order (MRO) of *all* :pep:`646`-compliant **unpacked tuple
child type hints** (e.g., the child hint ``*tuple[int, ...]`` subscripting the
parent tuple type hint ``tuple[str, *tuple[int, ...], float]``).
'''
