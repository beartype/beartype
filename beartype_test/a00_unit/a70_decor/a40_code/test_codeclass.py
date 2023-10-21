#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator noop** unit tests.

This submodule unit tests edge cases of the :func:`beartype.beartype` decorator
efficiently reducing to a noop.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_class() -> None:
    '''
    Test decoration of user-defined classes by the :func:`beartype.beartype`
    decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Intentionally redecorate a class twice by the @beartype decorator,
    # exercising an edge case in class decoration.
    @beartype
    @beartype
    class FromHisInnocuousHand(object):
        '''
        Arbitrary class defining one or more arbitrary annotated methods.
        '''

        def his_bloodless_food(self, lured_by_the_gentle_meaning: str) -> int:
            '''
            Arbitrary annotated method.
            '''

            return len(lured_by_the_gentle_meaning)

    # Arbitrary instance of this class.
    of_his_looks = FromHisInnocuousHand()

    # ....................{ PASS                           }....................
    # Assert that this method returns the expected length of the passed string.
    assert of_his_looks.his_bloodless_food(
        'Lured by the gentle meaning of his looks,') == 41

    # Assert that the __sizeof__() dunder method internally monkey-patched by
    # the @beartype decorator returns the expected size.
    of_his_looks_size_new = of_his_looks.__sizeof__()
    of_his_looks_size_old = of_his_looks.__sizeof__.__wrapped__(of_his_looks)
    assert isinstance(of_his_looks_size_new, int)
    assert of_his_looks_size_new >= 0
    assert of_his_looks_size_new == of_his_looks_size_old

    # ....................{ FAIL                           }....................
    # Assert that this method raises the expected exception when passed a
    # invalid parameter.
    with raises(BeartypeCallHintParamViolation):
        of_his_looks.his_bloodless_food(
            ('And the wild antelope,', "that starts whene'er"))


def test_decor_subclass() -> None:
    '''
    Test decoration of user-defined subclasses of user-defined superclasses by
    the :func:`beartype.beartype` decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Intentionally redecorate a class twice by the @beartype decorator,
    # exercising an edge case in class decoration.
    @beartype
    @beartype
    class WhereStoodJerusalem(object):
        '''
        Arbitrary superclass.
        '''

        def __init__(self, the_fallen_towers: str) -> None:
            '''
            Arbitrary constructor accepting an arbitrary annotated parameter.
            '''

            self._the_fallen_towers = the_fallen_towers


        def of_babylon(self, the_eternal_pyramids: str) -> int:
            '''
            Arbitrary annotated method.
            '''

            return len(self._the_fallen_towers + the_eternal_pyramids)


    @beartype
    @beartype
    class MemphisAndThebes(WhereStoodJerusalem):
        '''
        Arbitrary subclass of the superclass defined above, intentionally:

        * Overriding *all* methods defined by that superclass.
        * Defining a new subclass-specific method.
        '''

        def __init__(self, the_fallen_towers: str) -> None:
            self._the_fallen_towers_len = len(the_fallen_towers)


        def of_babylon(self, the_eternal_pyramids: str) -> int:
            return (
                self._the_fallen_towers_len * len(the_eternal_pyramids))


        def and_whatsoever_of_strange(
            self, sculptured_on_alabaster_obelisk: str) -> float:
            '''
            Arbitrary subclass-specific annotated method.
            '''

            return (
                self._the_fallen_towers_len /
                len(sculptured_on_alabaster_obelisk)
            )


    # Arbitrary instance of this subclass.
    or_jasper_tomb = MemphisAndThebes('Or jasper tomb, or mutilated sphynx,')

    # ....................{ PASS                           }....................
    # Assert that these methods passed arbitrary parameters return the expected
    # values from those parameters.
    assert or_jasper_tomb.of_babylon(
        'Of more than man, where marble daemons watch') == 1584
    assert or_jasper_tomb.and_whatsoever_of_strange(
        "The Zodiac's brazen mystery, and dead men") == 0.8780487804878049

    # ....................{ FAIL                           }....................
    # Assert that these methods all raise the expected exception when passed
    # invalid parameters.
    with raises(BeartypeCallHintParamViolation):
        MemphisAndThebes(b'Dark Aethiopia in her desert hills')
    with raises(BeartypeCallHintParamViolation):
        or_jasper_tomb.of_babylon((
            'Conceals.', 'Among the ruined temples there,'))
    with raises(BeartypeCallHintParamViolation):
        or_jasper_tomb.and_whatsoever_of_strange(len(
            'Stupendous columns, and wild images'))
