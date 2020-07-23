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
    'attrs_untypevared',
    'is_supported',
    'is_typevared',
    'superattrs',
    'superattrs_untypevared',
))
'''
**PEP-compliant type hint metadata** (i.e., named tuple whose variables detail
a PEP-compliant type hint with metadata applicable to testing scenarios).

Attributes
----------
attrs_untypevared : tuple
    Tuple of all **untypevared typing attributes** (i.e., public attributes of
    the :mod:`typing` module uniquely identifying this PEP-compliant type hint
    whose type is defined by that module, stripped of all type variable
    parametrization).
is_supported : bool
    ``True`` only if this PEP-compliant type hint is currently supported by the
    :func:`beartype.beartype` decorator.
is_typevared : bool
    ``True`` only if this PEP-compliant type hint is parametrized by one or
    more **type variables** (i.e., :class:`TypeVar` instances).
superattrs : tuple
    Tuple of all **untypevared typing super attributes** (i.e., public
    attributes of the :mod:`typing` module originally listed as superclasses of
    the class of this PEP-compliant type hint).
superattrs_untypevared : tuple
    Tuple of all **untypevared typing super attributes** (i.e., public
    attributes of the :mod:`typing` module originally listed as superclasses of
    the class of this PEP-compliant type hint, stripped of all type
    variable parametrization).
'''


PEP_HINT_TO_META = {
    # Singleton objects.
    typing.Any: PepHintMeta(
        attrs_untypevared=(typing.Any,),
        is_supported=True,
        is_typevared=False,
        superattrs=(),
        superattrs_untypevared=(),
    ),
    typing.NoReturn: PepHintMeta(
        attrs_untypevared=(typing.NoReturn,),
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_untypevared=(),
    ),

    # Builtin containers (dictionaries).
    typing.Dict[str, int]: PepHintMeta(
        attrs_untypevared=(typing.Dict,),
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_untypevared=(),
    ),
    typing.Dict[S, T]: PepHintMeta(
        attrs_untypevared=(typing.Dict,),
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_untypevared=(),
    ),

    # Builtin containers (lists).
    typing.List[float]: PepHintMeta(
        attrs_untypevared=(typing.List,),
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_untypevared=(),
    ),
    typing.List[T]: PepHintMeta(
        attrs_untypevared=(typing.List,),
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_untypevared=(),
    ),

    # Builtin containers (tuples).
    typing.Tuple[float, str, int]: PepHintMeta(
        attrs_untypevared=(typing.Tuple,),
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_untypevared=(),
    ),
    typing.Tuple[T, ...]: PepHintMeta(
        attrs_untypevared=(typing.Tuple,),
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_untypevared=(),
    ),

    # Callables.
    typing.Callable[[], str]: PepHintMeta(
        attrs_untypevared=(typing.Callable,),
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_untypevared=(),
    ),
    typing.Generator[int, float, str]: PepHintMeta(
        attrs_untypevared=(typing.Generator,),
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_untypevared=(),
    ),

    # Classes.
    typing.Type[dict]: PepHintMeta(
        attrs_untypevared=(typing.Type,),
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_untypevared=(),
    ),
    typing.Type[T]: PepHintMeta(
        attrs_untypevared=(typing.Type,),
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_untypevared=(),
    ),

    # Type aliases.
    TypeAlias: PepHintMeta(
        attrs_untypevared=(typing.Iterable,),
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_untypevared=(),
    ),

    # Type variables.
    T: PepHintMeta(
        attrs_untypevared=(typing.TypeVar,),
        is_supported=False,
        is_typevared=False,
        superattrs=(),
        superattrs_untypevared=(),
    ),

    # Unions.
    typing.Union[str, typing.Sequence[int]]: PepHintMeta(
        attrs_untypevared=(typing.Union,),
        is_supported=True,
        is_typevared=False,
        superattrs=(),
        superattrs_untypevared=(),
    ),
    typing.Union[str, typing.Iterable[typing.Tuple[S, T]]]: PepHintMeta(
        attrs_untypevared=(typing.Union,),
        is_supported=False,
        is_typevared=True,
        superattrs=(),
        superattrs_untypevared=(),
    ),

    # User-defined.
    CustomSingleTypevared: PepHintMeta(
        attrs_untypevared=(typing.Generic,),
        is_supported=False,
        is_typevared=True,
        superattrs=(typing.Generic[S, T],),
        superattrs_untypevared=(typing.Generic,),
    ),
    CustomSingleUntypevared: PepHintMeta(
        attrs_untypevared=(typing.Dict,),
        is_supported=False,
        is_typevared=False,
        superattrs=(typing.Dict[str, typing.List[str]],),
        superattrs_untypevared=(typing.Dict,),
    ),
    CustomMultipleTypevaredShallow: PepHintMeta(
        attrs_untypevared=(typing.Iterable, typing.Container,),
        is_supported=False,
        is_typevared=True,
        superattrs=(typing.Iterable[T], typing.Container[T],),
        superattrs_untypevared=(typing.Iterable, typing.Container,),
    ),
    CustomMultipleTypevaredDeep: PepHintMeta(
        attrs_untypevared=(typing.Iterable, typing.Container,),
        is_supported=False,
        is_typevared=True,
        superattrs=(
            typing.Iterable[typing.Tuple[S, T]],
            typing.Container[typing.Tuple[S, T]],
        ),
        superattrs_untypevared=(typing.Iterable, typing.Container,),
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
