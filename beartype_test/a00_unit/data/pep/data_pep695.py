#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695` **data submodule.**

This submodule exercises :pep:`695` support for statement-level type aliases
implemented in the :func:`beartype.beartype` decorator by declaring unit tests
exercising these aliases. For safety, these tests are intentionally isolated
from the main test suite. Notably, this low-level submodule implements the
higher-level ``test_decor_pep695()`` unit test in the main test suite.

This submodule *only* exercises **non-trivial type aliases** (i.e.,
:pep:`695`-compliant ``type`` statements testable *only* with a non-trivial
workflow). This includes type aliases containing one or more unquoted relative
forward references but excludes most other type aliases, which are trivial by
definition and thus testable with a standard workflow in the
:mod:`beartype_test.a00_util.data.hint.pep.proposal._data_pep695` submodule.

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.12.0.** If this is *not* the case, importing this submodule raises an
:exc:`SyntaxError` exception.
'''

# ....................{ IMPORTS                            }....................
# Defer test-specific imports.
from beartype import beartype
from beartype.roar import (
    BeartypeCallHintParamViolation,
    BeartypeDecorHintPep695Exception,
)
from beartype.typing import Union
from pytest import raises

# ....................{ ALIASES                            }....................
# Non-trivial global type alias containing:
# * Two or more unquoted relative forward references to a user-defined class
#   that has yet to be defined.
# * Two or more quoted relative forward references to another user-defined class
#   that has yet to be defined
#
# Note that we intentionally:
# * Embed at least two unquoted relative forward references in this alias. Why?
#   Because the low-level reduce_hint_pep695() reducer responsible for handling
#   PEP 695-compliant type aliases is expected to iteratively resolve *ALL*
#   unquoted relative forward references in this alias -- *NOT* simply the first
#   relative forward reference in this alias.
# * Embed the same unquoted relative forward reference multiple times in the
#   same alias. Although unlikely in real-world code, this edge case is
#   sufficiently horrible to warrant explicit testing.
# * Avoid even defining the "AllHerFrame" class. Why? Simply to exercise that we
#   can, mostly. *shrug*
type GlobalRefAlias = Union[
    KindledThrough, OfHerPureMind, 'AllHerFrame', OfHerPureMind]

# ....................{ CALLABLES                          }....................
@beartype
def a_permeating_fire(
    wild_numbers_then: GlobalRefAlias | None) -> GlobalRefAlias:
    '''
    Arbitrary :func:`.beartype`-decorated callable annotated by a non-trivial
    global type alias containing one or more forward references.
    '''

    return KindledThrough(wild_numbers_then.she_raised)

# ....................{ CLASSES                            }....................
class OfHerPureMind(object):
    '''
    Arbitrary class referred to by the above type alias.
    '''

    she_raised: str = 'She raised, with voice stifled in tremulous sobs'


class KindledThrough(object):
    '''
    Arbitrary class referred to by the above type alias.
    '''

    def __init__(self, her_fair_hands: str) -> None:
        self.her_fair_hands = her_fair_hands


# Instance of the former above class.
were_bare_alone = OfHerPureMind()

# ....................{ PASS                               }....................
# Assert that a @beartype-decorated function annotated by a non-trivial PEP
# 695-compliant type alias returns the expected object.
subdued_by_its_own_pathos = a_permeating_fire(were_bare_alone)
assert subdued_by_its_own_pathos.her_fair_hands == (
    'She raised, with voice stifled in tremulous sobs')

# Assert that @beartype raises the expected violation when calling a
# @beartype-decorated function erroneously violating a PEP 695-compliant type
# alias.
with raises(BeartypeCallHintParamViolation):
    a_permeating_fire('Were bare alone, sweeping from some strange harp')

# ....................{ CALLABLES                          }....................
def _sweeping_from_some_strange_harp() -> None:
    '''
    Arbitrary callable exercising various edge cases in
    :pep:`695`-compliant ``type`` statements defined at local rather than global
    scope.
    '''

    # ....................{ ALIASES                        }....................
    # Non-trivial local type alias containing an unquoted relative forward
    # reference to a user-defined class that has yet to be defined.
    type LocalRefAlias = StrangeSymphony

    # ....................{ CALLABLES                      }....................
    # Assert that @beartype raises the expected exception when decorating a
    # nested function annotated by a non-trivial local type alias containing one
    # or more forward references.
    with raises(BeartypeDecorHintPep695Exception):
        @beartype
        def in_their_branching_veins(
            the_eloquent_blood: LocalRefAlias | None) -> LocalRefAlias:
            '''
            Arbitrary :func:`.beartype`-decorated nested callable annotated by a
            non-trivial local type alias containing one or more forward
            references.
            '''

            return StrangeSymphony(the_eloquent_blood.told_an_ineffable_tale)

# Call the callable defined above.
_sweeping_from_some_strange_harp()
