#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646`- or :pep:`692`-compliant **unpack type hint** (i.e.,
``typing.Unpack[...]`` type hint subscripted by either a :pep:`646`-compliant
type variable tuple *or* :pep:`692`-compliant :class:`typing.TypedDict`
subclass) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: [PEP 646] Actually implement *SUPERFICIAL* type-checking support for PEP
#646-compliant tuple type hint unpacking:
#    Tuple[int, *Tuple[str, ...], str] - a tuple type where the first element is
#    guaranteed to be of type int, the last element is guaranteed to be of type
#    str, and the elements in the middle are zero or more elements of type str..
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
#def is_pep646_hint_tuple_unpacked(obj: object) -> bool:
#    return (
#        obj.__class__ is types.GenericAlias and
#        #FIXME: Globalize this magic constant for efficiency. *shrug*
#        obj.__mro__ == (tuple, object) and
#        getattr(obj, '__unpacked__', None) is True
#        (
#            getattr(obj, '__args__', False) ==
#            getattr(obj, '__typing_unpacked_tuple_args__', True)
#        )
#    )
#
#That's super-inefficient *AND* fragile across Python versions, but... what you
#gonna do, huh? PEP 646 authors *REALLY* dropped the ball on this one, sadly.
#
#Of course, all of that only gets us to just detecting these accursed objects.
#We then need to actually *TYPE-CHECK* their contents, somehow. A few ideas:
#* A parent tuple hint can contain at most *ONE* unpacked child tuple hint. So,
#  we'll now need to record the number of unpacked child tuple hints that have
#  been previously handled and raise an exception if two or more are seen. Ugh!
#* If the child tuple hint being unpacked is variadic (i.e., it's last item is
#  "...") while the parent tuple hint containing that child tuple hint is
#  fixed-length, we're now in trouble. This is exactly the example shown above.
#  Supporting this requires possibly intense generalizations to our code
#  generation algorithm for tuple hints, which previously partitioned support
#  for fixed-length and variadic tuple hints into two separate logic paths. Now,
#  the fixed-length tuple hint code path will need to detect and handle unpacked
#  child variadic tuple hints. Kinda madness, honestly. We sigh. *sigh*

#FIXME: [PEP 692] *LOL*. "Tuple[*Ts] == Tuple[Unpack[Ts]] == Tuple[object]"
#after reduction, a fixed-length tuple hint. Clearly, however,
#"Tuple[Unpack[Ts]]" should instead be semantically equivalent to a variadic
#tuple hint: e.g.,
#    # This is what we want! Tuple[*Ts] == Tuple[Unpack[Ts]] ==
#    Tuple[Any, ...]
#
#See commentary in "data_pep646" for how to address this. *sigh*

#FIXME: [PEP 692] Actually implement deep type-checking support for PEP
#692-compliant unpack type hints of the form "**kwargs:
#typing.Unpack[UserTypedDict]". Doing so will *ALMOST CERTAINLY* necessitate a
#new logic pathway for dynamically generating type-checking code efficiently
#type-checking the passed variadic keyword argument dictionary "**kwargs"
#against that user-defined "UserTypedDict". Feasible, but non-trivial. *sigh*

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPep646Exception,
    BeartypeDecorHintPep692Exception,
)
from beartype.typing import Optional
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignTypedDict,
    HintSignTypeVarTuple,
)
from beartype._util.func.arg.utilfuncargiter import ArgKind
from beartype._util.hint.pep.utilpepget import get_hint_pep_args
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, including:
#* Unsubscripted "typing.Unpack" type hints, which should be unconditionally
#  *PROHIBITED.* They signify nothing. "typing.Unpack" should *ALWAYS* be
#  subscripted by at least something.
def reduce_hint_pep646692_unpack(
    hint: Hint,
    arg_kind: Optional[ArgKind],
    exception_prefix: str,
    **kwargs
) -> Hint:
    '''
    Reduce the passed :pep:`646`- or :pep:`692`-compliant **unpack type hint**
    (i.e., ``typing.Unpack[...]`` type hint subscripted by either a
    :pep:`646`-compliant type variable tuple *or* :pep:`589`-compliant
    :class:`typing.TypedDict` subclass) to a more readily digestible type hint.

    Specifically, if the passed hint is:

    * A :pep:`646`-compliant unpack type hint subscripted by a
      :pep:`646`-compliant type variable tuple, this reducer effectively ignores
      this hint by reduction to the ignorable :class:`object` superclass (e.g.,
      from ``typing.Unpack[Ts]`` to simply ``object``). Although non-ideal,
      generating code type-checking these hints is sufficiently non-trivial to
      warrant a (hopefully) temporary delay in doing so properly. Note that:

      * Python itself unconditionally expands every unpacking of a
        :pep:`646`-compliant type variable tuple to this form of a
        :pep:`646`-compliant unpack type hint (e.g., from ``*Ts`` to
        ``typing.Unpack[Ts]``).
      * As a consequence of the prior note, :pep:`646`-compliant unpack type
        hints are as common as unpackings of :pep:`646`-compliant type variable
        tuples -- which is to say, increasingly common.

    * A :pep:`692`-compliant unpack type hint subscripted by a
      :pep:`589`-compliant :class:`typing.TypedDict` subclass, this reducer
      effectively ignores this hint by reduction to the ignorable
      :class:`object` superclass (e.g., from ``**kwargs:
      typing.Unpack[UserTypedDict]`` to simply ``**kwargs``). Although
      non-ideal, generating code type-checking these hints is sufficiently
      non-trivial to warrant a (hopefully) temporary delay in doing so properly.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : object
        :pep:`646`- or :pep:`692`-compliant unpack type hint to be reduced.
    arg_kind : Optional[ArgKind]
        Either:

        * If this hint annotates a parameter of some callable, that parameter's
          **kind** (i.e., :class:`.ArgKind` enumeration member conveying the
          syntactic class of that parameter, constraining how the callable
          declaring that parameter requires that parameter to be passed).
        * Else, :data:`None`.
    exception_prefix : str
        Human-readable substring prefixing exception messages raised by this
        reducer.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`._reduce_hint_pep646_args_or_kwargs` reducer.

    Returns
    -------
    object
        Lower-level type hint currently supported by :mod:`beartype`.

    Raises
    ------
    BeartypeDecorHintPep646Exception
        If this hint does *not* annotate a variadic keyword parameter and is
        *not* subscripted by a single :pep:`646`-compliant type variable tuple.
    BeartypeDecorHintPep692Exception
        If this hint annotates a variadic keyword parameter but is *not*
        subscripted by a single :pep:`589`-compliant :class:`typing.TypedDict`
        subclass.
    '''

    # ....................{ LOCALS                         }....................
    # Tuple of the single child hint subscripting this parent unpack hint. Note
    # that the "typing.Unpack" type hint factory has already pre-validated this
    # factory to accept at most one child type hint:
    #     >>> from typing import Unpack
    #     >>> Unpack['shaking', 'my', 'head']
    #     TypeError: typing.Unpack accepts only single type. Got ('shaking',
    #     'my', 'head').
    hints_child = get_hint_pep_args(hint)

    # Child hint subscripting this parent unpack hint.
    hint_child = hints_child[0]

    # Sign uniquely identifying this child hint if any *OR* "None".
    hint_child_sign = get_hint_pep_sign_or_none(hint_child)

    # ....................{ PEP 692                        }....................
    # Validate the passed variadic positional or keyword parameter type hint.

    # If this hint directly annotates a variadic keyword parameter, this is a
    # PEP 692- rather than 646-compliant hint. In this case...
    if arg_kind is ArgKind.VARIADIC_KEYWORD:
        # If this child hint is *NOT* a PEP 589-compliant "typing.TypeDict"
        # subclass, raise an exception.
        if hint_child_sign is not HintSignTypedDict:
            raise BeartypeDecorHintPep692Exception(
                f'{exception_prefix}PEP 692 unpack type hint {repr(hint)} '
                f'child type hint {repr(hint_child)} not '
                f'PEP 589 "typing.TypeDict" subclass.'
            )
        # Else, this child hint is a PEP 589-compliant "typing.TypeDict"
        # subclass.

        # Silently reduce to a noop by returning the ignorable "object"
        # superclass. While non-ideal, worky is preferable to non-worky.
        return object
    # Else, this hint does *NOT* directly annotate a variadic keyword parameter,
    # implying this is a PEP 646-compliant hint.

    # ....................{ PEP 646                        }....................
    # If this child hint is *NOT* a PEP 646-compliant "typing.TypeVarTuple"
    # object, raise an exception.
    if hint_child_sign is not HintSignTypeVarTuple:
        raise BeartypeDecorHintPep646Exception(
            f'{exception_prefix}PEP 646 unpack type hint {repr(hint)} '
            f'child type hint {repr(hint_child)} not '
            f'PEP 646 type variable tuple '
            f'(i.e., "typing.TypeVarTuple" object).'
        )
    # Else, this child hint is a PEP 646-compliant "typing.TypeVarTuple" object.

    # Silently reduce to a noop by returning the ignorable "object" superclass.
    # While non-ideal, worky is preferable to non-worky.
    return object
