#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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
    TypeVar,
    Union,
)

# ....................{ PRIVATE ~ hints                    }....................
_T = TypeVar('_T')
'''
Arbitrary type variable reference in type hints defined below.
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
    Decorated function annotated by a fully-qualified forward reference
    referring to a type that has yet to be declared.
    '''

    return dark_and_deep


@beartype
def stopping_by_woods_on(a_snowy_evening: 'TheDarkestEveningOfTheYear') -> (
    'TheDarkestEveningOfTheYear'):
    '''
    Decorated function annotated by a relative forward reference referring to a
    type that has yet to be declared.
    '''

    return a_snowy_evening


TheDarkestUnionOfTheYear = Union[complex, 'TheDarkestEveningOfTheYear', bytes]
@beartype
def but_i_have_promises(to_keep: TheDarkestUnionOfTheYear) -> (
    TheDarkestUnionOfTheYear):
    '''
    Decorated function annotated by a nested relative forward reference
    referring to a type that has yet to be declared.
    '''

    return to_keep

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
    Decorated function annotated by a composite type hint defined as a standard
    type hint subscripted by a relative forward reference referring to a type
    that has yet to be declared.
    '''

    return and_pinnacles_of_ice[0]

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


class WithSluggishSurge(Generic[_T]):
    '''
    Arbitrary generic declaring a method annotated by a forward reference
    referring to an instance of this same generic.
    '''

    @beartype
    def or_where_the_secret_caves(self) -> 'WithSluggishSurge[_T]':
        '''
        Arbitrary method annotated by a forward reference referring to an
        instance of this same generic.
        '''

        return self

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
