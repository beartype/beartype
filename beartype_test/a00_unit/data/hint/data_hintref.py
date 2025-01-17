#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide  **forward reference data submodule.**

This submodule exercises **forward reference type hints** (i.e., strings whose
values are the names of classes and tuples of classes, one or more of which
typically have yet to be defined) support implemented in the
:func:`beartype.beartype` decorator. This support can *only* be fully exercised
from within an independent data submodule rather than the body of a unit test.
Why? Because:

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
from beartype.typing import (
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,  # <-- intentionally imported due to being embedded in strings below
    TypeVar,
    Union,
)
from beartype._data.hint.datahinttyping import T

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
    'beartype_test.a00_unit.data.hint.data_hintref.TheDarkestEveningOfTheYear')
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
    and_pinnacles_of_ice: 'List[TheDarkestForwardRefOfTheYear]') -> (
    TheDarkestForwardRefOfTheYear):
    '''
    :func:`beartype.beartype`-decorated function annotated by a composite type
    hint defined as a standard type hint subscripted by a relative forward
    reference referring to a type that has yet to be declared.
    '''

    return and_pinnacles_of_ice[0]


TheDarkestSubclassOfTheYear = 'Type[TheDarkestEveningOfTheYear]'
@beartype
def the_dry_leaf(rustles_in_the_brake: TheDarkestSubclassOfTheYear) -> (
    TheDarkestSubclassOfTheYear):
    '''
    :func:`beartype.beartype`-decorated function annotated by a composite type
    hint defined as a ``beartype.typing.Type[...]`` hint subscripted by a
    relative forward reference referring to a type that has yet to be declared,
    exercising an edge case with respect to proxying of :func:`issubclass`
    type-checks in forward reference proxies.

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
    Decorated function annotated by a PEP-noncompliant tuple containing both
    standard types and a fully-qualified forward reference referring to a type
    that has yet to be declared.
    '''

    return and_downy_flake

# ....................{ CLASSES                            }....................
class TheDarkestEveningOfTheYear(str):
    '''
    Arbitrary class previously referred to by forward references above.
    '''

    pass


class WithSluggishSurge(Generic[T]):
    '''
    Arbitrary generic declaring a method annotated by a forward reference
    referring to an instance of this same generic.
    '''

    @beartype
    def or_where_the_secret_caves(self) -> 'WithSluggishSurge[T]':
        '''
        Arbitrary method annotated by a forward reference referring to an
        instance of this same generic.
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

    def in_a_silver_vision_floats(self) -> Tuple[
        LikeATornCloud, LikeATornCloud]:
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
#FIXME: Technically, @beartype *MAYBE* could actually resolve nested forward
#references by dynamically inspecting the call stack (depending on whether
#Python injects parent callables into the call stacks of closures, which it
#probably does, but there's no way of knowing until we try, and that's a lot of
#work to go to for potentially no gain whatsoever if Python doesn't behave like
#we think it does). That gets real cray-cray and non-portable real fast, so
#we're better off avoiding that unless we absolutely must -- and we mustn't,
#because PEP 484 + 563 + Python 3.10 means that unqualified forward references
#*MUST* now refer to globally scoped classes. So... why even bother, you know?

# Note that we do *NOT* bother declaring nested callables annotated with forward
# references to nested classes. Why? Unlike static analysis tooling, runtime
# decorators have *NO* internal access into nested lexical scopes and thus
# *CANNOT* by definition resolve forward references to nested classes.
#
# For example, the following callable is callable without exception but the
# closures returned by that callable are *NOT*, because @beartype fails to
# resolve the nested forward references annotating those closures:
#     from collections.abc import Callable
#     from typing import Tuple
#
#     # Undecorated callable nesting...
#     def between_the_woods_and_frozen_lake() -> Tuple[Callable, Callable, type]:
#         # ..................{ CLOSURES                          }..................
#         # Decorated closure annotated by an  unnested unqualified forward
#         # reference referring to a type that has yet to be declared.
#         @beartype
#         def to_stop_without(a_farmhouse_near: 'WhoseWoodsTheseAreIThinkIKnow') -> (
#             'WhoseWoodsTheseAreIThinkIKnow'):
#             return a_farmhouse_near
#
#         # Decorated closure annotated by a nested unqualified forward
#         # reference referring to a type that has yet to be declared.
#         TheDarkestNestedUnionOfTheYear = Union[
#             int, 'WhoseWoodsTheseAreIThinkIKnow', bool]
#         @beartype
#         def to_watch_his_woods(
#             fill_up_with_snow: TheDarkestNestedUnionOfTheYear) -> (
#             TheDarkestNestedUnionOfTheYear):
#             return fill_up_with_snow
#
#         # ..................{ CLASSES                           }..................
#         # User-defined class previously referred to by forward references above.
#         class WhoseWoodsTheseAreIThinkIKnow(str): pass
#
#         # ..................{ RETURNS                           }..................
#         # Return *ALL* of the above constructs, including closures and classes.
#         return (to_stop_without, to_watch_his_woods, WhoseWoodsTheseAreIThinkIKnow)
