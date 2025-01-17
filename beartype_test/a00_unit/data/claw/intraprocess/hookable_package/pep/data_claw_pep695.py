#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype import hookable** :pep:`695` **submodule** (i.e., data
module containing *only* :pep:`695`-compliant type aliases and callables and
classes annotated by those aliases, mimicking real-world usage of the
:func:`beartype.claw.beartype_package` import hook on an external package
utilizing type aliases).

This submodule *only* exercises **forward referencing type aliases** (i.e.,
:pep:`695`-compliant ``type`` statements containing one or more unquoted
relative forward references). Due to deficiencies in CPython's low-level C-based
implementation of :pep:`695`-compliant type aliases, type-checking forward
reference type aliases requires abstract syntax tree (AST) transformations and
thus beartype import hooks.

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.12.0.** If this is *not* the case, importing this submodule raises an
:exc:`SyntaxError` exception.

See Also
--------
:mod:`beartype_test.a00_util.data.hint.pep.proposal._data_pep695`
    Standard workflow defining all other type aliases to be tested, whose
    type-checking does *not* require AST transformations.
'''

# ....................{ IMPORTS                            }....................
# Defer test-specific imports.
from beartype.roar import (
    BeartypeCallHintParamViolation,
    BeartypeClawDecorWarning,
    BeartypeDecorHintPep695Exception,
)
from beartype.typing import Union
from pytest import (
    raises,
    warns,
)

# ....................{ ALIASES                            }....................
# Global forward referenced type alias containing:
# * Two or more unquoted relative forward references to a user-defined class
#   that has yet to be defined.
# * Two or more quoted relative forward references to another user-defined class
#   that has yet to be defined
#
# Note that we intentionally:
# * Embed at least two unquoted relative forward references in this alias. Why?
#   Because the low-level reduce_hint_pep695_unsubscripted() reducer responsible for handling
#   PEP 695-compliant type aliases is expected to iteratively resolve *ALL*
#   unquoted relative forward references in this alias -- *NOT* simply the first
#   relative forward reference in this alias.
# * Embed the same unquoted relative forward reference multiple times in the
#   same alias. Although unlikely in real-world code, this edge case is
#   sufficiently horrible to warrant explicit testing.
type GlobalRefAlias = Union[KindledThrough, OfHerPureMind, OfHerPureMind]

# ....................{ CALLABLES                          }....................
def a_permeating_fire(
    wild_numbers_then: GlobalRefAlias | None) -> GlobalRefAlias:
    '''
    Arbitrary :func:`.beartype`-decorated callable annotated by a global forward
    referenced type alias containing one or more forward references.
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
# Assert that a @beartype-decorated function annotated by a global forward
# referenced type alias returns the expected object.
subdued_by_its_own_pathos = a_permeating_fire(were_bare_alone)
assert subdued_by_its_own_pathos.her_fair_hands == (
    'She raised, with voice stifled in tremulous sobs')

# Assert that @beartype raises the expected violation when calling a
# @beartype-decorated function erroneously violating a global forward referenced
# type alias.
with raises(BeartypeCallHintParamViolation):
    a_permeating_fire('Were bare alone, sweeping from some strange harp')

# ....................{ CALLABLES                          }....................
def _sweeping_from_some_strange_harp() -> None:
    '''
    Arbitrary callable exercising various edge cases in
    :pep:`695`-compliant ``type`` statements defined at local rather than global
    scope.
    '''

    #FIXME: *BIG YIKES.* CPython's low-level C-based implementation of PEP
    #695-compliant type aliases currently fails to properly resolve unquoted
    #relative forward references defined in a local rather than global scope. I
    #tried literally everything to get this to work via AST transformations --
    #but whatever arcane type alias machinery it is that they've implemented
    #simply does *NOT* behave as expected at local scope. That said, we've
    #verified this *SHOULD* work via this simple snippet:
    #    >>> type bar = wut
    #    >>> globals()['wut'] = str
    #    >>> print(bar.__value__)
    #    str
    #
    #That behaves as expected -- until you actually then define the expected
    #class at local scope:
    #    def foo():
    #        type bar = wut
    #        globals()['wut'] = str
    #        print(bar.__value__)
    #        class wut(object): pass  # <-- this causes madness; WTF!?!?!?
    #    foo()
    #
    #The above print() statement now raises non-human readable exceptions
    #resembling:
    #    NameError: cannot access free variable 'wut' where it is not associated
    #    with a value in enclosing scope
    #
    #Clearly, this is madness. At the point at which the print() statement is
    #run, the "wut" class has yet to be redefined as a class. This constitutes a
    #profound CPython bug. Please submit us up the F-F-F-bomb.

    # ....................{ ALIASES                        }....................
    # Local forward referenced type alias containing an unquoted relative
    # forward reference to a user-defined class that has yet to be defined.
    type LocalRefAlias = StrangeSymphony

    # ....................{ CALLABLES                      }....................
    def in_their_branching_veins(
        the_eloquent_blood: LocalRefAlias | None) -> LocalRefAlias:
        '''
        Arbitrary :func:`.beartype`-decorated nested callable annotated by a
        local forward referenced type alias containing one or more forward
        references.
        '''

        return StrangeSymphony(the_eloquent_blood.told_an_ineffable_tale)

    # ....................{ CLASSES                        }....................
    class StrangeSymphony(object):
        '''
        Arbitrary class referred to by the above type alias.
        '''

        told_an_ineffable_tale: str = 'Her beamy bending eyes, her parted lips'


    # Instance of the above class.
    her_beamy_bending_eyes = StrangeSymphony()

    # # ....................{ PASS                           }....................
    # # Assert that a @beartype-decorated function annotated by a global forward
    # # referenced type alias returns the expected object.
    # her_parted_lips = in_their_branching_veins(her_beamy_bending_eyes)
    # assert her_parted_lips.told_an_ineffable_tale == (
    #     'Her beamy bending eyes, her parted lips')
    #
    # # Assert that @beartype raises the expected violation when calling a
    # # @beartype-decorated function erroneously violating a local forward
    # # referenced type alias.
    # with raises(BeartypeCallHintParamViolation):
    #     in_their_branching_veins(
    #         'Outstretched, and pale, and quivering eagerly.')

# ....................{ FAIL                               }....................
# Assert that @beartype raises the expected exception when attempting to define
# a local forward referenced type alias containing an unquoted relative forward
# reference to a user-defined class that has yet to be defined. Sadly, CPython's
# current implementation of PEP 695 is fundamentally broken -- especially in
# local scopes. See above.
with raises(BeartypeDecorHintPep695Exception):
    _sweeping_from_some_strange_harp()
