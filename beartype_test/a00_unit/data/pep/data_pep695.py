#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695` **data submodule.**

This submodule exercises :pep:`695` support for statement-level type aliases
implemented in the :func:`beartype.beartype` decorator by declaring unit tests
exercising these aliases. For safety, these tests are intentionally isolated
from the main test suite.

Caveats
----------
**This submodule requires the active Python interpreter to target at least
Python 3.12.0.** If this is *not* the case, importing this submodule raises an
:exc:`SyntaxError` exception.
'''

# ....................{ TESTS                              }....................
def unit_test_decor_pep695() -> None:
    '''
    Low-level callable implementing the higher-level ``test_decor_pep695()``
    unit test in the main test suite.

    Caveats
    -------
    This test *only* exercises **non-trivial type aliases** (i.e.,
    :pep:`695`-compliant ``type`` statements testable *only* by a non-trivial
    workflow). Notably, this includes type aliases containing one or more
    unquoted relative forward references.

    This test intentionally omits most type aliases, which are trivial by
    definition and thus testable by a standard workflow in the
    :mod:`beartype_test.a00_util.data.hint.pep.proposal._data_pep695` submodule.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # ....................{ ALIASES                        }....................
    # Non-trivial type alias containing:
    # * Two or more unquoted relative forward references to a user-defined class
    #   that has yet to be defined.
    # * Two or more quoted relative forward references to another user-defined
    #   class that has yet to be defined
    #
    # Note that we intentionally:
    # * Embed at least two unquoted relative forward references in this alias.
    #   Why? Because the low-level reduce_hint_pep695() reducer responsible for
    #   handling PEP 695-compliant type aliases is expected to iteratively
    #   resolve *ALL* unquoted relative forward references in this alias --
    #   *NOT* simply the first relative forward reference in this alias.
    # * Embed the same unquoted relative forward reference multiple times in the
    #   same alias. Although unlikely in real-world code, this edge case is
    #   sufficiently horrible to warrant explicit testing.
    # * Avoid even defining the "AllHerFrame" class. Why? Simply to exercise
    #   that we can, mostly. *shrug*
    type RefAlias = (
        KindledThrough | OfHerPureMind | 'AllHerFrame' | OfHerPureMind)

    # ....................{ CALLABLES                      }....................
    @beartype
    def a_permeating_fire(wild_numbers_then: RefAlias | None) -> RefAlias:
        '''
        Arbitrary :func:`.beartype`-decorated callable annotated by a
        non-trivial type alias containing one or more forward references.
        '''

        return KindledThrough(wild_numbers_then.she_raised)

    # ....................{ CLASSES                        }....................
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

    # ....................{ PASS                           }....................
    # Assert that a @beartype-decorated function annotated by a non-trivial PEP
    # 695-compliant type alias returns the expected object.
    subdued_by_its_own_pathos = a_permeating_fire(were_bare_alone)
    assert subdued_by_its_own_pathos.her_fair_hands == (
        'She raised, with voice stifled in tremulous sobs')

    # Assert that @beartype raises the expected violation when calling a
    # @beartype-decorated function erroneously violating a PEP
    # 695-compliant type alias.
    with raises(BeartypeCallHintParamViolation):
        a_permeating_fire('Were bare alone, sweeping from some strange harp')
