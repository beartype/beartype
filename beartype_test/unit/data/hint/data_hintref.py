#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype forward reference data submodule.**

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

# ....................{ IMPORTS                           }....................
from beartype import beartype
from typing import Union

# ....................{ CALLABLES                         }....................
# Decorated callable annotated by a PEP-noncompliant fully-qualified forward
# reference referring to a type that has yet to be declared.
TheDarkestForwardRefOfTheYear = (
    'beartype_test.unit.data.hint.data_hintref.TheDarkestEveningOfTheYear')
@beartype
def the_woods_are_lovely(dark_and_deep: TheDarkestForwardRefOfTheYear) -> (
    TheDarkestForwardRefOfTheYear):
    return dark_and_deep


# Decorated callable annotated by a PEP-noncompliant tuple containing both
# standard types and a fully-qualified forward reference referring to a type
# that has yet to be declared.
TheDarkestTupleOfTheYear = (complex, TheDarkestForwardRefOfTheYear, bool)
@beartype
def of_easy_wind(and_downy_flake: TheDarkestTupleOfTheYear) -> (
    TheDarkestTupleOfTheYear):
    return and_downy_flake


# Decorated callable annotated by a PEP-compliant unnested unqualified forward
# reference referring to a type that has yet to be declared.
@beartype
def stopping_by_woods_on(a_snowy_evening: 'TheDarkestEveningOfTheYear') -> (
    'TheDarkestEveningOfTheYear'):
    return a_snowy_evening


# Decorated callable annotated by a PEP-compliant nested unqualified forward
# reference referring to a type that has yet to be declared.
TheDarkestUnionOfTheYear = Union[complex, 'TheDarkestEveningOfTheYear', bytes]
@beartype
def but_i_have_promises(to_keep: TheDarkestUnionOfTheYear) -> (
    TheDarkestUnionOfTheYear):
    return to_keep

# ....................{ CLASSES                           }....................
# User-defined class previously referred to by forward references above.
class TheDarkestEveningOfTheYear(str): pass
