#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype annotations and type hints data submodule.**

This submodule defines various types (including both `PEP 484`_-compliant and
-noncompliant types) exercising *all* edge cases on behalf of test submodules.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
import collections, typing
from beartype import cave
from collections import namedtuple

# ....................{ TYPE VARIABLES                    }....................
S = typing.TypeVar('S')
'''
User-defined generic :mod:`typing` type variable.
'''


T = typing.TypeVar('T')
'''
User-defined generic :mod:`typing` type variable.
'''

# ....................{ TYPE ALIASES                      }....................
TypeAlias = typing.Iterable[typing.Tuple[T, T]]
'''
User-defined :mod:`typing` type alias.
'''

# ....................{ CLASSES ~ single                  }....................
class CustomSingleTypevared(typing.Generic[S, T]):
    '''
    User-defined class subclassing a single parametrized :mod:`typing` type.
    '''

    pass


class CustomSingleUntypevared(typing.Dict[str, typing.List[str]]):
    '''
    User-defined class subclassing a single unparametrized :mod:`typing` type.
    '''

    pass

# ....................{ CLASSES ~ multiple                }....................
class CustomMultipleTypevaredShallow(typing.Iterable[T], typing.Container[T]):
    '''
    User-defined class subclassing multiple directly parametrized :mod:`typing`
    types.
    '''

    pass


class CustomMultipleTypevaredDeep(
    collections.abc.Sized,
    typing.Iterable[typing.Tuple[S, T]],
    typing.Container[typing.Tuple[S, T]],
):
    '''
    User-defined generic :mod:`typing` subtype subclassing a heterogeneous
    amalgam of non-:mod:`typing` and :mod:`typing` superclasses.
    User-defined class subclassing multiple indirectly parametrized
    :mod:`typing` types as well as a non-:mod:`typing` abstract base class
    '''

    pass

# ....................{ MAPPINGS                          }....................
PepHintMeta = namedtuple('PepHintMeta', (
    'is_supported',
    'is_typevared',
    'superattrs',
    'superattrs_argless_to_args',
    'attrs_argless_to_args',
))
'''
**PEP-compliant type hint metadata** (i.e., named tuple whose variables detail
a PEP-compliant type hint with metadata applicable to testing scenarios).

Attributes
----------
is_supported : bool
    ``True`` only if this PEP-compliant type hint is currently supported by the
    :func:`beartype.beartype` decorator.
is_typevared : bool
    ``True`` only if this PEP-compliant type hint is parametrized by one or
    more **type variables** (i.e., :class:`TypeVar` instances).
superattrs : tuple
    Tuple of all **typing super attributes** (i.e., public attributes of the
    :mod:`typing` module originally listed as superclasses of the class of this
    PEP-compliant type hint).
superattrs_argless_to_args : tuple
    Dictionary mapping each **argumentless typing super attribute** (i.e.,
    public attribute of the :mod:`typing` module originally listed as a
    superclass of the class of this PEP-compliant type hint *sans* arguments)
    to that attribute (i.e., *with* arguments).
attrs_argless_to_args : tuple
    Dictionary mapping each **argumentless typing attribute** (i.e.,
    public attribute of the :mod:`typing` module uniquely identifying this
    PEP-compliant type hint *sans* arguments) to that attribute (i.e., *with*
    arguments).
'''


PEP_HINT_TO_META = {
    # Singleton objects.
    typing.Any: PepHintMeta(
        is_supported=True,
        is_typevared=False,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Any: ()},
    ),
    typing.NoReturn: PepHintMeta(
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.NoReturn: ()},
    ),

    # Builtin containers (dictionaries).
    typing.Dict[str, int]: PepHintMeta(
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Dict: (str, int)},
    ),
    typing.Dict[S, T]: PepHintMeta(
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Dict: (S, T,)},
    ),

    # Builtin containers (lists).
    typing.List[float]: PepHintMeta(
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.List: (float,)},
    ),
    typing.List[T]: PepHintMeta(
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.List: (T,)},
    ),

    # Builtin containers (tuples).
    typing.Tuple[float, str, int]: PepHintMeta(
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Tuple: (float, str, int)},
    ),
    typing.Tuple[T, ...]: PepHintMeta(
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Tuple: (T, ...)},
    ),

    # Callables.
    typing.Callable[[], str]: PepHintMeta(
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Callable: (str,)},
    ),
    typing.Generator[int, float, str]: PepHintMeta(
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Generator: (int, float, str)},
    ),

    # Classes.
    typing.Type[dict]: PepHintMeta(
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Type: (dict,)},
    ),
    typing.Type[T]: PepHintMeta(
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Type: (T,)},
    ),

    # Type aliases.
    TypeAlias: PepHintMeta(
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Iterable: (typing.Tuple[T, T],)},
    ),

    # Type variables.
    T: PepHintMeta(
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.TypeVar: ()},
    ),

    # Unions.
    typing.Union[str, typing.Sequence[int]]: PepHintMeta(
        is_supported=True,
        is_typevared=False,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={typing.Union: (str, typing.Sequence[int])},
    ),
    typing.Union[str, typing.Iterable[typing.Tuple[S, T]]]: PepHintMeta(
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_argless_to_args={},
        attrs_argless_to_args={
            typing.Union: (str, typing.Iterable[typing.Tuple[S, T]])},
    ),

    # User-defined.
    CustomSingleTypevared: PepHintMeta(
        is_supported=False,
        is_typevared=True,
        superattrs=(typing.Generic[S, T],),
        superattrs_argless_to_args={typing.Generic: (S, T,)},
        attrs_argless_to_args     ={typing.Generic: (S, T,)},
    ),
    CustomSingleUntypevared: PepHintMeta(
        is_supported=False,
        is_typevared=False,
        superattrs=(typing.Dict[str, typing.List[str]],),
        superattrs_argless_to_args={
            typing.Dict: (str, typing.List[str],)},
        attrs_argless_to_args={
            typing.Dict: (str, typing.List[str],)},
    ),
    CustomMultipleTypevaredShallow: PepHintMeta(
        is_supported=False,
        is_typevared=True,
        superattrs=(typing.Iterable[T], typing.Container[T],),
        superattrs_argless_to_args={
            typing.Iterable:  (T,),
            typing.Container: (T,),
        },
        attrs_argless_to_args={
            typing.Iterable:  (T,),
            typing.Container: (T,),
        },
    ),
    CustomMultipleTypevaredDeep: PepHintMeta(
        is_supported=False,
        is_typevared=True,
        superattrs=(
            typing.Iterable[typing.Tuple[S, T]],
            typing.Container[typing.Tuple[S, T]],
        ),
        superattrs_argless_to_args={
            typing.Iterable:  (typing.Tuple[S, T],),
            typing.Container: (typing.Tuple[S, T],),
        },
        attrs_argless_to_args={
            typing.Iterable:  (typing.Tuple[S, T],),
            typing.Container: (typing.Tuple[S, T],),
        },
    ),
}
'''
Dictionary mapping various PEP-compliant type hints to :class:`PepHintMeta`
instances detailing those hints with metadata applicable to testing scenarios.
'''

# ....................{ ITERABLES                         }....................
PEP_HINTS = PEP_HINT_TO_META.keys()
'''
Iterable of various PEP-compliant type hints exercising well-known edge cases.
'''


NONPEP_HINTS = (
    list,
    str,
    cave.AnyType,
    cave.NoneType,
    cave.NoneTypeOr[cave.AnyType],
)
'''
Tuple of various PEP-noncompliant type hints exercising well-known edge cases.
'''
