#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`484`-compliant **stringified forward reference type hint**
(i.e., strings whose values are the names of classes and tuples of classes, one
or more of which typically have yet to be defined) data submodule.

This submodule exercises stringified forward reference support implemented in
the :func:`beartype.beartype` decorator. This support can *only* be fully
exercised from within an independent data submodule rather than the body of a
unit test. Why? Because:

* That decorator is only safely importable from within the body of a unit test.
* Forward reference type hints can only refer to objects defined at module
  scope rather than from within the body of a unit test.
* Forward reference type hints referring to objects previously defined at
  module scope fail to exercise the deferred nature of forward references.
* Ergo, callables that are decorated by that decorator, annotated by one or
  more forward reference type hints, and both declared and called from within
  the body of a unit test fail to exercise this deferred nature.
* Ergo, only callables that are decorated by that decorator, annotated by one or
  more forward reference type hints, and both declared and called at module
  scope before their referents exercise this deferred nature.
'''

# ....................{ IMPORTS                            }....................
from beartype import beartype
from beartype._data.typing.datatyping import T
from typing import (
    Generic,
    Optional,
    TypeVar,
    Union,
)
from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    Sequence,
)

# ....................{ LOCALS                             }....................
LikeATornCloud = TypeVar('LikeATornCloud', bound='BeforeTheHurricane')
'''
Type variable whose bound is expressed as a PEP-compliant relative forward
reference to a self-referential type that has yet to be defined.
'''

# ....................{ FUNCTIONS ~ pep : discrete         }....................
# Arbitrary functions annotated by PEP-compliant forward references defined as
# both unqualified (relative) and fully-qualified (absolute) Python identifiers,
# possibly nested in one or more parent type hints.

TheDarkestForwardRefOfTheYear = (
    'beartype_test.a00_unit.data.pep.pep484.data_pep484ref.TheDarkestEveningOfTheYear')
@beartype
def the_woods_are_lovely(dark_and_deep: TheDarkestForwardRefOfTheYear) -> (
    TheDarkestForwardRefOfTheYear):
    '''
    :func:`beartype.beartype`-decorated function annotated by a fully-qualified
    forward reference referring to a type that has yet to be declared.
    '''

    return dark_and_deep


@beartype
def stopping_by_woods_on(a_snowy_evening: 'TheDarkestEveningOfTheYear') -> (
    'TheDarkestEveningOfTheYear'):
    '''
    :func:`beartype.beartype`-decorated function annotated by a relative forward
    reference referring to a type that has yet to be declared.
    '''

    return a_snowy_evening


TheDarkestUnionOfTheYear = Union[complex, 'TheDarkestEveningOfTheYear', bytes]
@beartype
def but_i_have_promises(to_keep: TheDarkestUnionOfTheYear) -> (
    TheDarkestUnionOfTheYear):
    '''
    :func:`beartype.beartype`-decorated function annotated by a union of
    arbitrary types *and* a relative forward reference referring to a type that
    has yet to be declared.
    '''

    return to_keep


NearTheShore = Optional[Sequence['TheDarkestEveningOfTheYear']]
@beartype
def a_little_shallop(floating: NearTheShore = ()) -> NearTheShore:
    '''
    :func:`beartype.beartype`-decorated function accepting an optional parameter
    annotated by a union of arbitrary types *and* a relative forward reference
    referring to a type that has yet to be declared.
    '''

    return floating

# ....................{ FUNCTIONS ~ pep : composite        }....................
# Arbitrary functions annotated by PEP-compliant forward references defined as
# non-trivial Python expressions (i.e., strings that are *NOT* reducible to
# trivial Python identifiers) containing unqualified (relative) and
# fully-qualified (absolute) Python identifiers, either nested in one or more
# parent type hints *OR* themselves serving as parent type hints nesting one or
# more child type hints.
#
# Whereas discrete forward references are trivially supportable with simple
# dynamic module attribute lookups at call time, composite forward references
# can only be supported with non-trivial runtime parsing of Python expressions.

@beartype
def its_fields_of_snow(
    and_pinnacles_of_ice: 'list[TheDarkestForwardRefOfTheYear]') -> (
    TheDarkestForwardRefOfTheYear):
    '''
    :func:`beartype.beartype`-decorated function annotated by a
    :pep:`484`-compliant stringified hint referring to a :pep:`585`-compliant
    container hint subscripted by a relative forward reference referring to a
    type that has yet to be declared.
    '''

    return and_pinnacles_of_ice[0]


TheDarkestSubclassOfTheYear = 'type[TheDarkestEveningOfTheYear]'
@beartype
def the_dry_leaf(rustles_in_the_brake: TheDarkestSubclassOfTheYear) -> (
    TheDarkestSubclassOfTheYear):
    '''
    :func:`beartype.beartype`-decorated function annotated by a
    :pep:`484`-compliant stringified hint referring to a :pep:`585`-compliant
    subclass hint subscripted by a relative forward reference referring to a
    type that has yet to be declared, exercising an edge case with respect to
    proxying of :func:`issubclass` type-checks in forward reference proxies.

    See Also
    --------
    https://github.com/beartype/beartype/issues/289
        Issue exposing this edge case.
    '''

    return rustles_in_the_brake

# ....................{ FUNCTIONS ~ non-pep : discrete     }....................
# Arbitrary functions annotated by PEP-noncompliant forward references defined
# as both unqualified (relative) and fully-qualified (absolute) Python
# identifiers, possibly nested in one or more parent type hints.

TheDarkestTupleOfTheYear = (complex, TheDarkestForwardRefOfTheYear, bool)
@beartype
def of_easy_wind(and_downy_flake: TheDarkestTupleOfTheYear) -> (
    TheDarkestTupleOfTheYear):
    '''
    :func:`beartype.beartype`-decorated function annotated by a PEP-noncompliant
    tuple containing both standard types and a fully-qualified forward reference
    referring to a type that has yet to be declared.
    '''

    return and_downy_flake

# ....................{ CLASSES                            }....................
# Order of definition is mostly significant for the types defined below.

class TheDarkestEveningOfTheYear(str):
    '''
    Undecorated class previously referred to by forward references above.
    '''

    pass


@beartype
class AllHisBulkAnAgony(Sequence['WithSluggishSurge[T]']):
    '''
    :func:`beartype.beartype`-decorated :pep:`585`-compliant generic subclassing
    a :mod:`collection.abc` abstract base classes (ABC) subscripted by a
    :pep:`484`-compliant stringified forward reference to a :pep:`484`-compliant
    generic that has yet to be defined parametrized by the same type variable.
    '''

    # ................{ INITIALIZERS                           }................
    def __init__(self, sequence: tuple['WithSluggishSurge[T]']) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(sequence, tuple), f'{repr(sequence)} not tuple.'
        self._sequence = sequence

    # ................{ ABCs                                   }................
    # Define all protocols mandated by ABCs subclassed by this generic.

    def __call__(self) -> int:
        return len(self)

    def __contains__(self, obj: object) -> bool:
        return obj in self._sequence

    def __enter__(self) -> 'AllHisBulkAnAgony[T]':
        return self

    def __exit__(self, *args, **kwargs) -> bool:
        return False

    def __getitem__(self, index: int) -> 'WithSluggishSurge[T]':
        return self._sequence[index]

    def __iter__(self) -> Iterator['WithSluggishSurge[T]']:
        return iter(self._sequence)

    def __len__(self) -> bool:
        return len(self._sequence)

    def __reversed__(self) -> Iterable['WithSluggishSurge[T]']:
        return reversed(self._sequence)


class WithSluggishSurge(Generic[T]):
    '''
    Undecorated :pep:`484`-compliant generic declaring a method annotated by a
    forward reference referring to a parametrization of this same generic.
    '''

    @beartype
    def or_where_the_secret_caves(self) -> 'WithSluggishSurge[T]':
        '''
        :func:`beartype.beartype`-decorated method annotated by a forward
        reference referring to an instance of this same generic.
        '''

        return self

# ....................{ CLASSES ~ self-referential         }....................
# @beartype-decorated classes defining methods annotated by one or more
# self-referential type hints (i.e., hints referring to the same class via a
# PEP-compliant relative forward reference).

@beartype
class BeforeTheHurricane(object):
    '''
    :func:`beartype.beartype`-decorated class defining a method annotated by
    a **self-referential relative forward reference** (i.e., referring to
    this class currently being defined).
    '''

    def in_a_silver_vision_floats(self) -> (
        tuple[LikeATornCloud, LikeATornCloud]):
        '''
        Method annotated by a 2-tuple of type variables whose bounds are
        expressed as PEP-compliant relative forward references to this class
        currently being defined.

        This method exercises this edge case:
            https://github.com/beartype/beartype/issues/367
        '''

        # Return a 2-tuple intentionally violating this type variable.
        return ('As one that', 'in a silver vision floats')

# Test decorating a user-defined class with the @beartype decorator where:
# 1. That class defines a method annotated by a self-referential relative
#    forward reference (i.e., referring to that class currently being defined).
# 2. That method is then called.
# 3. That logic is then repeated *THREE TIMES,* thus redefining that class and
#    re-calling that method three times. Doing so simulates a hot reload (i.e.,
#    external reload of the hypothetical user-defined module defining that class
#    and that function).
#
# For reasons that are *NOT* particularly interesting (and would consume seven
# volumes of fine print), it has to be 3 iterations. 2 is too few.
#
# See also this user-reported issue underlying this test case:
#     https://github.com/beartype/beartype/issues/365
for _ in range(3):
    @beartype
    class OnTheBareMast(object):
        '''
        :func:`beartype.beartype`-decorated class defining a method annotated by
        a **self-referential relative forward reference** (i.e., referring to
        this class currently being defined).
        '''

        def __init__(self, and_took_his_lonely_seat: int) -> None:
            '''
            Initialize this object with the passed arbitrary parameter.
            '''

            self.and_took_his_lonely_seat = and_took_his_lonely_seat


        @classmethod
        def over_the_tranquil_sea(
            cls, and_took_his_lonely_seat: int) -> 'OnTheBareMast':
            '''
            Method annotated by a self-referential relative forward reference.
            '''

            return OnTheBareMast(and_took_his_lonely_seat + 0xBABECAFE)


    # Instantiate this class by invoking this factory class method.
    And_felt_the_boat_speed = OnTheBareMast.over_the_tranquil_sea(0xFEEDBABE)

# ....................{ FUNCTIONS ~ pep : composite : moar }....................
# Arbitrary functions annotated by PEP-compliant forward references defined as
# non-trivial Python expressions (i.e., strings that are *NOT* reducible to
# trivial Python identifiers) containing unqualified (relative) and
# fully-qualified (absolute) Python identifiers, requiring the previously
# defined classes to have already been declared.

@beartype
def winding_among_the_springs(
    of_fire_and_poison: 'Inaccessible') -> 'Inaccessible':
    '''
    Decorated function annotated by a relative forward reference referring to a
    **type alias** (i.e., global attribute whose value is a composite type hint
    defined as a standard type hint subscripted by an arbitrary type).
    '''

    return of_fire_and_poison


Inaccessible = WithSluggishSurge[int]
'''
Arbitrary **type alias** (i.e., global attribute whose value is a composite type
hint defined as a standard type hint subscripted by an arbitrary type).
'''

# ....................{ CLOSURES                           }....................
def between_the_woods_and_frozen_lake() -> tuple[Callable, Callable, type]:
    '''
    Undecorated callable internally defining and returning multiple
    :func:`beartype.beartype`-decorated closures annotated by
    :pep:`484`-compliant stringified forward references referring to types that
    have yet to be declared.
    '''

    # ..................{ CALLABLES                          }..................
    @beartype
    def to_stop_without(a_farmhouse_near: 'WhoseWoodsTheseAreIThinkIKnow') -> (
        'WhoseWoodsTheseAreIThinkIKnow'):
        '''
        :func:`beartype.beartype`-decorated decorated closure annotated by an
        unnested unqualified forward reference referring to a type that has yet
        to be declared.
        '''

        return a_farmhouse_near

    TheDarkestNestedUnionOfTheYear = Union[
        int, 'WhoseWoodsTheseAreIThinkIKnow', bool]

    @beartype
    def to_watch_his_woods(
        fill_up_with_snow: TheDarkestNestedUnionOfTheYear) -> (
        TheDarkestNestedUnionOfTheYear):
        '''
        :func:`beartype.beartype`-decorated decorated closure annotated by a
        nested unqualified forward reference referring to a type that has yet to
        be declared.
        '''

        return fill_up_with_snow

    # ..................{ CLASSES                            }..................
    # User-defined class previously referred to by forward references above.
    class WhoseWoodsTheseAreIThinkIKnow(str): pass

    # ..................{ RETURNS                            }..................
    # Return *ALL* of the above constructs, including closures and classes.
    return (to_stop_without, to_watch_his_woods, WhoseWoodsTheseAreIThinkIKnow)
