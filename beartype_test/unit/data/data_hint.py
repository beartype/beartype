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

# ....................{ CLASSES ~ generic                 }....................
#FIXME: Rename to "GenericUserDefinedSingle" for disambiguity.
class GenericUserDefined(typing.Generic[S, T]):
    '''
    User-defined generic :mod:`typing` subtype.
    '''

    pass


class GenericUserDefinedMultiple(
    collections.abc.Sized,
    typing.Iterable[typing.Tuple[S, T]],
    typing.Container[typing.Tuple[S, T]],
    typing.Generic[S, T],
):
    '''
    User-defined generic :mod:`typing` subtype subclassing a heterogeneous
    amalgam of non-:mod:`typing` and :mod:`typing` superclasses.
    '''

    pass

# ....................{ CLASSES ~ non-generic             }....................
#FIXME: Rename to "NongenericUserDefinedSingle" for disambiguity.
class TypingUserDefined(typing.Dict[str, typing.List[str]]):
    '''
    User-defined :mod:`typing` subtype.
    '''

    pass


#FIXME: Rename to "NongenericUserDefinedMultiple" for disambiguity.
class TypingUserDefinedMultiple(typing.Iterable[T], typing.Container[T],):
    '''
    User-defined :mod:`typing` subtype subclassing multiple :mod:`typing`
    types.
    '''

    pass

# ....................{ MAPPINGS                          }....................
PepHintMeta = namedtuple('PepHintMeta', (
    'attrs_untypevared', 'super_attrs',))
'''
**PEP-compliant type hint metadata** (i.e., named tuple whose variables detail
a PEP-compliant type hint with metadata applicable to testing scenarios).

Attributes
----------
attrs_untypevared : tuple
    Tuple of all **untypevared typing attributes** (i.e., public attributes of
    the :mod:`typing` module uniquely identifying this PEP-compliant type hint
    defined via the :mod:`typing` module but stripped of all type variable
    parametrization).
super_attrs : tuple
    Tuple of all **typing super attributes** (i.e., public attributes of
    the :mod:`typing` module originally listed as superclasses of the class of
    the passed object).
'''


PEP_HINT_TO_META = {
    typing.Any: PepHintMeta(
        attrs_untypevared=(typing.Any,),
        super_attrs=(),
    ),

    typing.Callable[[], str]: PepHintMeta(
        attrs_untypevared=(typing.Callable,),
        super_attrs=(),
    ),

    typing.Dict[str, str]: PepHintMeta(
        attrs_untypevared=(typing.Dict,),
        super_attrs=(),
    ),

    typing.List[float]: PepHintMeta(
        attrs_untypevared=(typing.List,),
        super_attrs=(),
    ),

    typing.Generator[int, float, str]: PepHintMeta(
        attrs_untypevared=(typing.Generator,),
        super_attrs=(),
    ),

    typing.NoReturn: PepHintMeta(
        attrs_untypevared=(typing.NoReturn,),
        super_attrs=(),
    ),

    typing.Tuple[str, int]: PepHintMeta(
        attrs_untypevared=(typing.Tuple,),
        super_attrs=(),
    ),

    typing.Type[dict]: PepHintMeta(
        attrs_untypevared=(typing.Type,),
        super_attrs=(),
    ),

    typing.Union[str, typing.Iterable[typing.Tuple[S, T]]]: PepHintMeta(
        attrs_untypevared=(typing.Union,),
        super_attrs=(),
    ),
    typing.Union[str, typing.Sequence[int]]: PepHintMeta(
        attrs_untypevared=(typing.Union,),
        super_attrs=(),
    ),

    GenericUserDefined: PepHintMeta(
        attrs_untypevared=(typing.Generic,),
        super_attrs=(typing.Generic[S, T],),
    ),
    GenericUserDefinedMultiple: PepHintMeta(
        attrs_untypevared=(typing.Iterable, typing.Container, typing.Generic,),
        super_attrs=(
            typing.Iterable[typing.Tuple[S, T]],
            typing.Container[typing.Tuple[S, T]],
            typing.Generic[S, T],
        ),
    ),

    T: PepHintMeta(
        attrs_untypevared=(typing.TypeVar,),
        super_attrs=(),
    ),

    TypeAlias: PepHintMeta(
        attrs_untypevared=(typing.Iterable,),
        super_attrs=(),
    ),

    TypingUserDefined: PepHintMeta(
        attrs_untypevared=(typing.Dict,),
        super_attrs=(typing.Dict[str, typing.List[str]],),
    ),
    TypingUserDefinedMultiple: PepHintMeta(
        attrs_untypevared=(typing.Iterable, typing.Container,),
        super_attrs=(typing.Iterable[T], typing.Container[T],),
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
